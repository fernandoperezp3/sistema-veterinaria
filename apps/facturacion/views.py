from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.configuracion.models import Configuracion
from apps.facturacion.models import Factura, DetalleFactura, Caja
from apps.inventario.models import Producto, Movimiento


def get_numero_factura():
    ultimo = 0
    for numero in Factura.objects.values_list('numero', flat=True):
        try:
            ultimo = max(ultimo, int(str(numero).split('-')[-1]))
        except (ValueError, TypeError):
            continue
    siguiente = ultimo + 1
    while Factura.objects.filter(numero=f"F-{siguiente:06d}").exists():
        siguiente += 1
    return f"F-{siguiente:06d}"


def _actualizar_caja(monto):
    caja, _ = Caja.objects.get_or_create(fecha=timezone.localdate(), defaults={'monto_inicial': 0})
    if caja.cerrada:
        return False
    caja.total_ingresos = (caja.total_ingresos or 0) + monto
    caja.monto_final = (caja.monto_inicial or 0) + caja.total_ingresos - (caja.total_egresos or 0)
    caja.save()
    return True


def _leer_items(request):
    descripciones = request.POST.getlist('descripcion[]')
    cantidades = request.POST.getlist('cantidad[]')
    precios = request.POST.getlist('precio[]')
    producto_ids = request.POST.getlist('producto_id[]')

    items = []
    errores = []
    for i, desc in enumerate(descripciones):
        desc = (desc or '').strip()
        if not desc:
            continue
        try:
            cantidad = int(cantidades[i]) if i < len(cantidades) and cantidades[i] else 1
            precio = Decimal(precios[i]) if i < len(precios) and precios[i] else Decimal('0')
        except (ValueError, InvalidOperation):
            errores.append(f'Cantidad o precio inválido en "{desc}".')
            continue
        if cantidad <= 0:
            errores.append(f'La cantidad de "{desc}" debe ser mayor a cero.')
            continue
        if precio < 0:
            errores.append(f'El precio de "{desc}" no puede ser negativo.')
            continue

        producto = None
        prod_id = producto_ids[i] if i < len(producto_ids) else ''
        if prod_id:
            try:
                producto = Producto.objects.get(pk=int(prod_id), is_active=True)
            except (Producto.DoesNotExist, ValueError):
                producto = None
        items.append({'descripcion': desc, 'cantidad': cantidad, 'precio': precio, 'producto': producto})

    requerido = {}
    for item in items:
        if item['producto']:
            requerido[item['producto'].pk] = requerido.get(item['producto'].pk, 0) + item['cantidad']
    for prod_id, cantidad in requerido.items():
        producto = Producto.objects.get(pk=prod_id)
        if cantidad > producto.stock_actual:
            errores.append(f'Stock insuficiente de "{producto.nombre}". Disponible: {producto.stock_actual}, solicitado: {cantidad}.')

    return items, errores


@login_required
def factura_lista(request):
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    q = request.GET.get('q', '')

    facturas = Factura.objects.select_related('cliente').order_by('-fecha')

    if fecha_desde:
        facturas = facturas.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        facturas = facturas.filter(fecha__date__lte=fecha_hasta)
    if q:
        facturas = facturas.filter(
            Q(numero__icontains=q) | Q(cliente__nombres__icontains=q) | Q(cliente__apellidos__icontains=q)
        )

    total_ingresos = facturas.filter(estado='PAGADA').aggregate(t=Sum('total'))['t'] or 0

    return render(request, 'facturacion/lista.html', {
        'facturas': facturas,
        'total_ingresos': total_ingresos,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'q': q,
    })


@login_required
def factura_crear(request):
    clientes = Cliente.objects.filter(is_active=True).order_by('nombres')
    productos = Producto.objects.filter(is_active=True).order_by('nombre')
    config = Configuracion.get_config()
    contexto = {
        'clientes': clientes,
        'productos': productos,
        'productos_data': {
            str(p.pk): {'nombre': p.nombre, 'precio': float(p.precio_venta), 'stock': p.stock_actual}
            for p in productos
        },
        'factura_js': {
            'simbolo': config.simbolo_moneda,
            'tasa': float(config.tasa_impuesto),
        },
    }

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        metodo_pago = request.POST.get('metodo_pago', 'EFECTIVO')
        if metodo_pago not in dict(Factura.METODOS):
            metodo_pago = 'EFECTIVO'

        items, errores = _leer_items(request)
        if not items and not errores:
            errores.append('Debe agregar al menos un ítem a la factura.')
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'facturacion/nueva_factura.html', contexto)

        cliente = Cliente.objects.filter(pk=cliente_id).first() if cliente_id else None

        with transaction.atomic():
            factura = Factura.objects.create(
                cliente=cliente,
                numero=get_numero_factura(),
                subtotal=0,
                igv=0,
                total=0,
                metodo_pago=metodo_pago,
                cajero=request.user.get_full_name() or request.user.username,
            )

            subtotal = Decimal('0.00')
            for item in items:
                DetalleFactura.objects.create(
                    factura=factura,
                    producto=item['producto'],
                    descripcion=item['descripcion'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                )
                subtotal += Decimal(item['cantidad']) * item['precio']
                if item['producto']:
                    Movimiento.objects.create(
                        producto=item['producto'],
                        tipo='SALIDA',
                        cantidad=item['cantidad'],
                        motivo='Venta',
                        comprobante=factura.numero,
                    )

            impuesto = (subtotal * config.tasa_impuesto).quantize(Decimal('0.01'))
            factura.subtotal = subtotal
            factura.igv = impuesto
            factura.total = subtotal + impuesto
            factura.save()

            _actualizar_caja(factura.total)

        from apps.core.services_client import MicroservicesClient
        items_payload = [
            {
                'descripcion': d.descripcion,
                'cantidad': d.cantidad,
                'precio_unitario': float(d.precio_unitario),
                'subtotal': float(d.subtotal),
            }
            for d in factura.detalles.all()
        ]
        cpe = MicroservicesClient.emitir_comprobante_fiscal(
            factura_id=factura.id,
            numero=factura.numero,
            cliente_nombre=factura.cliente.nombre_completo if factura.cliente else "Cliente General",
            documento=factura.cliente.dni if factura.cliente else "00000000",
            total=factura.total,
            igv=factura.igv,
            subtotal=factura.subtotal,
            items=items_payload,
        )
        campos = []
        if cpe and cpe.get('comprobante'):
            comp = cpe['comprobante']
            factura.hash_cpe = comp.get('hash_cpe', '')
            factura.firma_digital = comp.get('firma_digital', '')
            factura.estado_fiscal = comp.get('estado_sunat_sat', '')
            factura.codigo_qr = comp.get('codigo_qr_texto', '')
            campos += ['hash_cpe', 'firma_digital', 'estado_fiscal', 'codigo_qr']

        pago = None
        if factura.metodo_pago == 'TARJETA':
            pago = MicroservicesClient.procesar_pago_tarjeta(
                numero_factura=factura.numero,
                monto=factura.total,
                titular=factura.cliente.nombre_completo if factura.cliente else "Cliente General",
            )
            if pago and pago.get('success'):
                factura.autorizacion_pago = pago.get('codigo_autorizacion', '')
                campos.append('autorizacion_pago')
        if campos:
            factura.save(update_fields=campos)

        if cpe:
            messages.success(request, f'Factura {factura.numero} generada y firmada electrónicamente por el microservicio fiscal (hash {factura.hash_cpe[:12]}…).')
        else:
            messages.success(request, f'Factura {factura.numero} generada por {config.simbolo_moneda} {factura.total}. El microservicio fiscal no respondió.')
        if pago and pago.get('success'):
            messages.info(request, f"Pago con tarjeta aprobado por la pasarela ({pago.get('pasarela')}). Autorización {factura.autorizacion_pago}.")
        elif factura.metodo_pago == 'TARJETA':
            messages.warning(request, 'La pasarela de pagos no respondió; registre la autorización del POS manualmente.')
        return redirect('factura_detalle', pk=factura.pk)

    return render(request, 'facturacion/nueva_factura.html', contexto)


@login_required
def factura_detalle(request, pk):
    factura = get_object_or_404(Factura.objects.select_related('cliente').prefetch_related('detalles__producto'), pk=pk)
    return render(request, 'facturacion/detalle_factura.html', {'factura': factura})


@login_required
def factura_anular(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if factura.estado == 'ANULADA':
        messages.info(request, f'La factura {factura.numero} ya está anulada.')
        return redirect('factura_detalle', pk=factura.pk)

    if request.method == 'POST':
        with transaction.atomic():
            factura.estado = 'ANULADA'
            factura.save()
            for detalle in factura.detalles.select_related('producto'):
                if detalle.producto:
                    Movimiento.objects.create(
                        producto=detalle.producto,
                        tipo='ENTRADA',
                        cantidad=detalle.cantidad,
                        motivo='Anulación de venta',
                        comprobante=factura.numero,
                    )
            if timezone.localtime(factura.fecha).date() == timezone.localdate():
                _actualizar_caja(-factura.total)
        messages.warning(request, f'Factura {factura.numero} anulada. Stock restituido.')
        return redirect('factura_lista')
    return render(request, 'clientes/confirmar_eliminar.html', {'objeto': factura, 'tipo': 'factura (anular)'})


@login_required
def caja_hoy(request):
    hoy = timezone.localdate()
    caja, _ = Caja.objects.get_or_create(fecha=hoy, defaults={'monto_inicial': 0})
    facturas_hoy = Factura.objects.filter(fecha__date=hoy, estado='PAGADA')
    total_hoy = facturas_hoy.aggregate(t=Sum('total'))['t'] or 0
    return render(request, 'facturacion/caja.html', {
        'caja': caja, 'facturas_hoy': facturas_hoy, 'total_hoy': total_hoy, 'hoy': hoy
    })


@login_required
def caja_cerrar(request):
    if request.method == 'POST':
        hoy = timezone.localdate()
        caja = get_object_or_404(Caja, fecha=hoy)
        if not caja.cerrada:
            caja.cerrada = True
            caja.fecha_cierre = timezone.now()
            caja.usuario_cierre = request.user.get_full_name() or request.user.username
            caja.save()
            messages.success(request, 'Caja cerrada correctamente.')
    return redirect('caja_hoy')


@login_required
def api_producto_precio(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return JsonResponse({
        'nombre': producto.nombre,
        'precio': float(producto.precio_venta),
        'stock': producto.stock_actual,
    })


@login_required
def factura_pdf(request, pk):
    import io
    from django.http import HttpResponse
    from reportlab.graphics.barcode.qr import QrCodeWidget
    from reportlab.graphics.shapes import Drawing
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    factura = get_object_or_404(Factura.objects.select_related('cliente').prefetch_related('detalles'), pk=pk)
    config = Configuracion.get_config()
    moneda = config.simbolo_moneda
    acento = colors.HexColor('#0bb8c8')
    gris = colors.HexColor('#64748b')

    def dinero(valor):
        return f"{moneda} {valor:,.2f}"

    normal = ParagraphStyle('n', fontName='Helvetica', fontSize=9.5, leading=13)
    pequeno = ParagraphStyle('p', parent=normal, fontSize=8, textColor=gris, leading=11)
    titulo = ParagraphStyle('t', parent=normal, fontName='Helvetica-Bold', fontSize=18, textColor=acento, leading=22)
    derecha = ParagraphStyle('d', parent=normal, alignment=2)
    derecha_b = ParagraphStyle('db', parent=derecha, fontName='Helvetica-Bold', fontSize=14, leading=18)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            title=f"Factura {factura.numero}", author=config.nombre_empresa or 'VetSystem')
    ancho = letter[0] - 3.6 * cm
    elementos = []

    empresa = [Paragraph((config.nombre_empresa or 'VetSystem').upper(), titulo)]
    for dato in (config.ruc and f"NIT: {config.ruc}", config.direccion, config.telefono and f"Tel: {config.telefono}"):
        if dato:
            empresa.append(Paragraph(str(dato), pequeno))
    cabecera_der = [
        Paragraph(f"<b>FACTURA {factura.numero}</b>", derecha_b),
        Paragraph(factura.fecha.astimezone(timezone.get_current_timezone()).strftime('%d/%m/%Y %H:%M'), ParagraphStyle('f', parent=derecha, textColor=gris)),
        Paragraph(f"Estado: <b>{factura.get_estado_display()}</b>", derecha),
    ]
    cab = Table([[empresa, cabecera_der]], colWidths=[ancho * 0.55, ancho * 0.45])
    cab.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#e2e8f0')),
                             ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    elementos += [cab, Spacer(1, 12)]

    cliente = factura.cliente
    datos_cliente = [Paragraph('<font color="#64748b" size="8">CLIENTE</font>', normal),
                     Paragraph(f"<b>{cliente.nombre_completo if cliente else 'Consumidor final'}</b>", normal)]
    if cliente:
        datos_cliente += [Paragraph(f"DPI: {cliente.dni}", pequeno), Paragraph(f"Tel: {cliente.telefono}", pequeno)]
    datos_pago = [Paragraph('<font color="#64748b" size="8">MÉTODO DE PAGO</font>', derecha),
                  Paragraph(f"<b>{factura.get_metodo_pago_display()}</b>", derecha),
                  Paragraph(f"Cajero: {factura.cajero or '—'}", ParagraphStyle('c', parent=pequeno, alignment=2))]
    info = Table([[datos_cliente, datos_pago]], colWidths=[ancho * 0.6, ancho * 0.4])
    info.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elementos += [info, Spacer(1, 14)]

    filas = [['Descripción', 'Cant.', 'Precio unit.', 'Subtotal']]
    for d in factura.detalles.all():
        filas.append([Paragraph(d.descripcion, normal), str(d.cantidad), dinero(d.precio_unitario), dinero(d.subtotal)])
    n = len(filas)
    filas += [['', '', 'Subtotal', dinero(factura.subtotal)],
              ['', '', config.nombre_impuesto or 'IVA', dinero(factura.igv)],
              ['', '', 'TOTAL', dinero(factura.total)]]
    tabla = Table(filas, colWidths=[ancho * 0.52, ancho * 0.1, ancho * 0.19, ancho * 0.19], repeatRows=1)
    tabla.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')), ('TEXTCOLOR', (0, 0), (-1, 0), gris),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'), ('ALIGN', (1, 0), (1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, n - 1), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (2, n), (-1, n), 0.8, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'), ('FONTSIZE', (2, -1), (-1, -1), 12),
        ('TEXTCOLOR', (3, -1), (3, -1), colors.HexColor('#059669')),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos += [tabla, Spacer(1, 18)]

    if factura.hash_cpe:
        tam = 3.2 * cm
        qr = QrCodeWidget(factura.codigo_qr or factura.hash_cpe)
        x1, y1, x2, y2 = qr.getBounds()
        dibujo = Drawing(tam, tam, transform=[tam / (x2 - x1), 0, 0, tam / (y2 - y1), 0, 0])
        dibujo.add(qr)
        lineas = [Paragraph('<b>Comprobante electrónico firmado</b>', normal),
                  Paragraph(f"Hash SHA-256: <font face='Courier'>{factura.hash_cpe}</font>", pequeno),
                  Paragraph(f"Firma digital: <font face='Courier'>{factura.firma_digital}</font>", pequeno),
                  Paragraph(f"Estado fiscal: <b>{factura.estado_fiscal or '—'}</b>", pequeno)]
        if factura.autorizacion_pago:
            lineas.append(Paragraph(f"Pago con tarjeta autorizado: <b>{factura.autorizacion_pago}</b>", pequeno))
        fiscal = Table([[dibujo, lineas]], colWidths=[tam + 0.6 * cm, ancho - tam - 0.6 * cm])
        fiscal.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cbd5e1')),
                                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                                    ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        elementos.append(fiscal)
    else:
        elementos.append(Paragraph('Comprobante sin certificación electrónica.', pequeno))

    elementos += [Spacer(1, 20), Paragraph('Gracias por su preferencia.', ParagraphStyle('g', parent=pequeno, alignment=1))]
    doc.build(elementos)

    respuesta = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    modo = 'attachment' if request.GET.get('descargar') else 'inline'
    respuesta['Content-Disposition'] = f'{modo}; filename="Factura_{factura.numero}.pdf"'
    return respuesta
