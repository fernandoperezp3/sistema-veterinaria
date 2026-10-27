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
