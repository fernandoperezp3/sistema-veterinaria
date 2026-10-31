from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from apps.agenda.models import Cita
from apps.agenda.forms import CitaForm



def _mensaje_whatsapp(request, respuesta):
    """Si el microservicio de notificaciones devolvió un enlace wa.me, lo muestra como botón."""
    enlace = ((respuesta or {}).get('detalle') or {}).get('enlace_whatsapp')
    if enlace:
        messages.info(request, enlace, extra_tags='whatsapp')
    elif respuesta:
        messages.warning(request, 'El cliente no tiene un teléfono válido; no se pudo preparar el WhatsApp.')

@login_required
def agenda_lista(request):
    fecha_filtro = request.GET.get('fecha', '')
    estado_filtro = request.GET.get('estado', '')
    q = request.GET.get('q', '')

    citas = Cita.objects.select_related('mascota__cliente', 'veterinario').filter(is_active=True).order_by('fecha', 'hora')

    if fecha_filtro:
        citas = citas.filter(fecha=fecha_filtro)
    if estado_filtro:
        citas = citas.filter(estado=estado_filtro)
    if q:
        citas = citas.filter(
            Q(mascota__nombre__icontains=q) | Q(mascota__cliente__nombres__icontains=q)
            | Q(mascota__cliente__apellidos__icontains=q)
        )

    hoy = timezone.localdate()
    citas_hoy = Cita.objects.filter(fecha=hoy, is_active=True).count()

    context = {
        'citas': citas,
        'estados': Cita.ESTADOS,
        'fecha_filtro': fecha_filtro,
        'estado_filtro': estado_filtro,
        'q': q,
        'hoy': hoy,
        'citas_hoy': citas_hoy,
    }
    return render(request, 'agenda/lista.html', context)


def _enlace_teleconsulta(request, cita):
    from apps.core.red import enlace_sala_publico, ruta_sala
    consulta = getattr(cita, 'consulta_virtual', None)
    if not consulta or consulta.estado_conexion in ('FINALIZADA', 'CANCELADA') or not ruta_sala(consulta.enlace_reunion):
        return None
    return enlace_sala_publico(request, consulta.enlace_reunion, 'cliente')


def _crear_teleconsulta(cita):
    from apps.core.services_client import MicroservicesClient
    from apps.telemedicina.models import ConsultaVirtual
    if hasattr(cita, 'consulta_virtual'):
        return cita.consulta_virtual
    veterinario = cita.veterinario.get_full_name() if cita.veterinario else 'Dr. Veterinario'
    resp = MicroservicesClient.crear_sala_telemedicina(
        cita_id=cita.id,
        veterinario=veterinario or 'Dr. Veterinario',
        paciente=cita.mascota.nombre,
        propietario=cita.mascota.cliente.nombre_completo,
    )
    if not (resp and resp.get('success')):
        return None
    return ConsultaVirtual.objects.create(
        cita=cita,
        plataforma='OTRO',
        enlace_reunion=resp['sala']['url_acceso'],
        codigo_acceso=resp['sala']['sala_id'],
        estado_conexion='PROGRAMADA',
    )


@login_required
def cita_crear(request):
    inicial = {}
    if request.GET.get('mascota'):
        inicial['mascota'] = request.GET.get('mascota')
    if request.GET.get('tipo'):
        inicial['tipo'] = request.GET.get('tipo')
    if request.GET.get('teleconsulta'):
        inicial['es_teleconsulta'] = True
    form = CitaForm(request.POST or None, initial=inicial)
    if form.is_valid():
        cita = form.save(commit=False)
        if form.cleaned_data.get('es_teleconsulta'):
            cita.tipo = 'CONSULTA'
        cita.save()
        if form.cleaned_data.get('es_teleconsulta'):
            sala = _crear_teleconsulta(cita)
            if sala:
                messages.info(request, f'Teleconsulta creada para {cita.mascota.nombre}. El cliente la verá en su portal.')
            else:
                messages.warning(request, 'La cita se guardó, pero el microservicio de telemedicina no respondió. Prográmala desde Telemedicina.')
        
        # Integración con Microservicio de Notificaciones (Puerto 8081)
        from apps.core.services_client import MicroservicesClient
        notif = MicroservicesClient.notificar_cita(
            cita_id=cita.id,
            cliente_nombre=f"{cita.mascota.cliente.nombres} {cita.mascota.cliente.apellidos}",
            telefono=cita.mascota.cliente.telefono,
            mascota_nombre=cita.mascota.nombre,
            fecha=cita.fecha,
            hora=cita.hora,
            motivo=getattr(cita, 'motivo', 'Consulta General'),
            enlace_videollamada=_enlace_teleconsulta(request, cita),
        )
        if notif:
            messages.success(request, f'Cita registrada para {cita.mascota.nombre} el {cita.fecha}. Recordatorio preparado por el Microservicio de Notificaciones.')
            _mensaje_whatsapp(request, notif)
        else:
            messages.success(request, f'Cita registrada para {cita.mascota.nombre} el {cita.fecha}.')
        return redirect('agenda_lista')
    return render(request, 'agenda/form.html', {'form': form, 'titulo': 'Nueva Cita', 'accion': 'Registrar'})


@login_required
def cita_editar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    form = CitaForm(request.POST or None, instance=cita)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cita actualizada correctamente.')
        return redirect('agenda_lista')
    return render(request, 'agenda/form.html', {'form': form, 'titulo': 'Editar Cita', 'accion': 'Guardar', 'cita': cita})


@login_required
def cita_estado(request, pk):
    if request.method == 'POST':
        cita = get_object_or_404(Cita, pk=pk)
        cita.is_active = not cita.is_active
        cita.save()
        estado_str = "activada" if cita.is_active else "desactivada"
        messages.success(request, f'Cita {estado_str}.')
    return redirect('agenda_lista')


@login_required
def cita_cambiar_estado(request, pk):
    if request.method == 'POST':
        cita = get_object_or_404(Cita, pk=pk)
        nuevo_estado = request.POST.get('estado')
        estados_validos = [e[0] for e in Cita.ESTADOS]
        if nuevo_estado in estados_validos:
            cita.estado = nuevo_estado
            cita.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'estado': cita.get_estado_display()})
            messages.success(request, f'Estado actualizado a: {cita.get_estado_display()}')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Estado inválido'}, status=400)
    return redirect('agenda_lista')


@login_required
def cita_notificar_microservicio(request, pk):
    """Reenvía la notificación de la cita invocando al Microservicio en el puerto 8081."""
    cita = get_object_or_404(Cita, pk=pk)
    from apps.core.services_client import MicroservicesClient
    
    resp = MicroservicesClient.notificar_cita(
        cita_id=cita.id,
        cliente_nombre=f"{cita.mascota.cliente.nombres} {cita.mascota.cliente.apellidos}",
        telefono=cita.mascota.cliente.telefono,
        mascota_nombre=cita.mascota.nombre,
        fecha=cita.fecha,
        hora=cita.hora,
        motivo=getattr(cita, 'motivo', 'Consulta General'),
        enlace_videollamada=_enlace_teleconsulta(request, cita),
    )
    if resp and resp.get('success'):
        messages.success(request, f'Recordatorio de la cita de {cita.mascota.nombre} preparado por el Microservicio de Notificaciones (8081).')
        _mensaje_whatsapp(request, resp)
    else:
        messages.warning(request, f'El Microservicio de Notificaciones está offline o no respondió. La cita sigue registrada.')
    return redirect('agenda_lista')

