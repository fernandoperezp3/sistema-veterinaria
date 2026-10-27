import datetime
import glob
import os
import shutil
import subprocess

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import connection
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.utils import timezone


@login_required
def dashboard(request):
    from apps.agenda.models import Cita
    from apps.clientes.models import Mascota
    from apps.facturacion.models import Factura
    from apps.inventario.models import Producto

    hoy = timezone.localdate()
    mes_inicio = hoy.replace(day=1)
    anio_inicio = hoy.replace(month=1, day=1)

    citas_hoy = Cita.objects.filter(fecha=hoy, is_active=True).count()
    total_mascotas = Mascota.objects.filter(is_active=True).count()
    mascotas_mes = Mascota.objects.filter(fecha_registro__date__gte=mes_inicio).count()

    facturas_mes = Factura.objects.filter(estado='PAGADA', fecha__date__gte=mes_inicio)
    ingresos_mes = facturas_mes.aggregate(total=Sum('total'))['total'] or 0
    cantidad_facturas_mes = facturas_mes.count()
    ticket_promedio = (ingresos_mes / cantidad_facturas_mes) if cantidad_facturas_mes else 0
    ingresos_anio = Factura.objects.filter(
        estado='PAGADA', fecha__date__gte=anio_inicio
    ).aggregate(total=Sum('total'))['total'] or 0

    productos_activos = Producto.objects.filter(is_active=True).count()
    stock_bajo = sum(1 for p in Producto.objects.filter(is_active=True) if p.necesita_reposicion)

    proximas_citas = Cita.objects.filter(
        fecha=hoy, is_active=True
    ).exclude(estado__in=['COMPLETADA', 'CANCELADA']).select_related(
        'mascota__cliente', 'veterinario'
    ).order_by('hora')[:5]

    clave_grafico = f"dashboard:grafico:{hoy.isoformat()}"
    grafico = cache.get(clave_grafico)
    if grafico is None:
        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        labels = []
        data_citas = []
        data_ingresos = []
        for i in range(6, -1, -1):
            dia = hoy - datetime.timedelta(days=i)
            labels.append(dias_semana[dia.weekday()])
            data_citas.append(Cita.objects.filter(fecha=dia, is_active=True).count())
            ing_dia = Factura.objects.filter(
                estado='PAGADA', fecha__date=dia
            ).aggregate(t=Sum('total'))['t'] or 0
            data_ingresos.append(float(ing_dia))
        grafico = (labels, data_citas, data_ingresos)
        cache.set(clave_grafico, grafico, 60)
    labels, data_citas, data_ingresos = grafico

    context = {
        'citas_hoy': citas_hoy,
        'total_mascotas': total_mascotas,
        'mascotas_mes': mascotas_mes,
        'ingresos_mes': ingresos_mes,
        'ingresos_anio': ingresos_anio,
        'ticket_promedio': round(ticket_promedio, 2),
        'productos_activos': productos_activos,
        'stock_bajo': stock_bajo,
        'proximas_citas': proximas_citas,
        'labels': labels,
        'data_citas': data_citas,
        'data_ingresos': data_ingresos,
    }
    return render(request, 'dashboard/index.html', context)


def _solo_admin(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado. Solo administradores pueden ver esta sección.')
        return redirect('dashboard')
    return None


def _es_mysql():
    return connection.vendor == 'mysql'


def _backups_dir():
    ruta = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(ruta, exist_ok=True)
    return ruta


def _mysql_args(binario):
    db = settings.DATABASES['default']
    args = [binario, '-h', str(db['HOST'] or 'localhost'), '-P', str(db['PORT'] or '3306'), '-u', str(db['USER'])]
    if db['PASSWORD']:
        args.append(f"-p{db['PASSWORD']}")
    args.append(str(db['NAME']))
    return args


@login_required
def mantenimiento_index(request):
    denegado = _solo_admin(request)
    if denegado:
        return denegado

    tablas_info = []
    total_registros = 0
    tablas = connection.introspection.table_names()
    with connection.cursor() as cursor:
        for nombre_tabla in tablas:
            if nombre_tabla.startswith(('auth_', 'django_', 'account_', 'socialaccount_', 'sqlite_')):
                continue
            cursor.execute(f"SELECT COUNT(*) FROM {connection.ops.quote_name(nombre_tabla)}")
            conteo = cursor.fetchone()[0]
            tablas_info.append({'nombre': nombre_tabla, 'cantidad': conteo})
            total_registros += conteo

    tamano_bd_mb = 0
    try:
        if _es_mysql():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT SUM(data_length + index_length) / 1024 / 1024 FROM information_schema.TABLES WHERE table_schema = %s",
                    [settings.DATABASES['default']['NAME']],
                )
                tamano_bd_mb = round(float(cursor.fetchone()[0] or 0), 2)
        else:
            ruta_bd = settings.DATABASES['default']['NAME']
            if os.path.exists(ruta_bd):
                tamano_bd_mb = round(os.path.getsize(ruta_bd) / 1024 / 1024, 2)
    except Exception:
        tamano_bd_mb = 0

    archivos_backup = len(glob.glob(os.path.join(_backups_dir(), '*.sql')))

    context = {
        'tablas_info': tablas_info,
        'total_registros': total_registros,
        'tamano_bd_mb': tamano_bd_mb,
        'archivos_backup': archivos_backup,
    }
    return render(request, 'core/mantenimiento.html', context)


@login_required
def mantenimiento_backup(request):
    denegado = _solo_admin(request)
    if denegado:
        return denegado

    if not _es_mysql():
        messages.error(request, 'El respaldo automático solo está disponible con MySQL.')
        return redirect('mantenimiento_index')

    if not shutil.which('mysqldump'):
        messages.error(request, 'No se encontró "mysqldump". Agregue la carpeta bin de MySQL al PATH del sistema.')
        return redirect('mantenimiento_index')

    fecha_str = timezone.localtime().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_vet_{fecha_str}.sql"
    filepath = os.path.join(_backups_dir(), filename)

    try:
        with open(filepath, 'wb') as salida:
            subprocess.run(_mysql_args('mysqldump'), stdout=salida, stderr=subprocess.PIPE, check=True)
        return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
    except subprocess.CalledProcessError as e:
        detalle = e.stderr.decode('utf-8', 'ignore').strip() if e.stderr else str(e)
        messages.error(request, f'Error al generar backup: {detalle}')
    except Exception as e:
        messages.error(request, f'Error al generar backup: {e}')
    return redirect('mantenimiento_index')


@login_required
def mantenimiento_restore(request):
    denegado = _solo_admin(request)
    if denegado:
        return denegado

    if request.method == 'POST' and request.FILES.get('backup_file'):
        archivo = request.FILES['backup_file']
        if not archivo.name.lower().endswith('.sql'):
            messages.error(request, 'El archivo debe ser formato .sql')
            return redirect('mantenimiento_index')

        if not _es_mysql():
            messages.error(request, 'La restauración automática solo está disponible con MySQL.')
            return redirect('mantenimiento_index')

        if not shutil.which('mysql'):
            messages.error(request, 'No se encontró el cliente "mysql". Agregue la carpeta bin de MySQL al PATH del sistema.')
            return redirect('mantenimiento_index')

        temp_path = os.path.join(_backups_dir(), 'temp_restore.sql')
        with open(temp_path, 'wb+') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)

        try:
            with open(temp_path, 'rb') as entrada:
                subprocess.run(_mysql_args('mysql'), stdin=entrada, stderr=subprocess.PIPE, check=True)
            messages.success(request, 'Base de datos restaurada correctamente.')
        except subprocess.CalledProcessError as e:
            detalle = e.stderr.decode('utf-8', 'ignore').strip() if e.stderr else str(e)
            messages.error(request, f'Error al restaurar: {detalle}')
        except Exception as e:
            messages.error(request, f'Error al restaurar: {e}')
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        messages.error(request, 'Seleccione un archivo .sql para restaurar.')

    return redirect('mantenimiento_index')


@login_required
def mantenimiento_reset(request):
    denegado = _solo_admin(request)
    if denegado:
        return denegado

    if request.method == 'POST' and request.POST.get('confirm_reset') == 'RESET_SISTEMA_VET':
        from apps.agenda.models import Cita
        from apps.clientes.models import Cliente, Mascota
        from apps.facturacion.models import Caja, DetalleFactura, Factura
        from apps.grooming.models import ServicioGrooming
        from apps.inventario.models import Movimiento
        from apps.medico.models import DetalleReceta, HistoriaClinica, Receta, Vacuna
        from apps.telemedicina.models import ConsultaVirtual
        from django.db import transaction

        modelos = [
            DetalleFactura, Factura, Caja, ServicioGrooming, ConsultaVirtual, Movimiento,
            DetalleReceta, Receta, Vacuna, HistoriaClinica, Cita, Mascota, Cliente,
        ]
        try:
            with transaction.atomic():
                for modelo in modelos:
                    modelo.objects.all().delete()
            messages.success(request, 'Sistema reseteado correctamente. Datos de negocio eliminados. (Usuarios conservados)')
        except Exception as e:
            messages.error(request, f'Error al resetear: {e}')
    else:
        messages.error(request, 'Confirmación incorrecta para resetear el sistema.')

    return redirect('mantenimiento_index')


@login_required
def microservicios_panel(request):
    from apps.core.services_client import MicroservicesClient
    estados = MicroservicesClient.ping_all()
    total_online = sum(1 for s in estados.values() if s.get('online'))

    context = {
        'estados': estados,
        'total_online': total_online,
        'total_servicios': len(estados),
        'titulo': 'Monitor de Microservicios',
        'notificaciones': (MicroservicesClient.historial('notificaciones', '/api/v1/notificaciones/historial') or {}).get('historial', [])[:15],
        'comprobantes': (MicroservicesClient.historial('facturacion', '/api/v1/facturacion/comprobantes') or {}).get('comprobantes', [])[:15],
    }
    return render(request, 'core/microservicios_panel.html', context)
