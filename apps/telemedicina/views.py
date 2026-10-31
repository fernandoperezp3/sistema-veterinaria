from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.telemedicina.models import ConsultaVirtual
from apps.telemedicina.forms import ConsultaVirtualForm
from apps.agenda.models import Cita


@login_required
def telemedicina_lista(request):
    hoy = timezone.localdate()
    # Teleconsultas programadas (vistas prioritariamente por fecha de la cita)
    consultas = ConsultaVirtual.objects.select_related('cita__mascota__cliente').order_by('estado_conexion', 'cita__fecha')
    
    # Citas tipo consulta que aún no tienen teleconsulta asociada (posibles futuras teleconsultas)
    citas_sin_telemedicina = Cita.objects.filter(tipo='CONSULTA', consulta_virtual__isnull=True, fecha__gte=hoy).order_by('fecha', 'hora')
    
    from apps.core.red import enlace_sala_publico, enlace_whatsapp, ruta_sala
    consultas = list(consultas)
    for c in consultas:
        if ruta_sala(c.enlace_reunion):
            c.link_vet = enlace_sala_publico(request, c.enlace_reunion, 'vet')
            c.link_cliente = enlace_sala_publico(request, c.enlace_reunion, 'cliente')
            cliente = c.cita.mascota.cliente
            mensaje = (
                f"Hola {cliente.nombres}, este es el enlace para la videoconsulta de {c.cita.mascota.nombre} "
                f"el {c.cita.fecha:%d/%m/%Y} a las {c.cita.hora:%H:%M}: {c.link_cliente} "
                f"(si aparece un aviso de seguridad, elija Avanzado y luego Continuar)."
            )
            c.link_whatsapp = enlace_whatsapp(cliente.telefono, mensaje)

    return render(request, 'telemedicina/lista.html', {
        'consultas': consultas,
        'citas_pendientes': citas_sin_telemedicina,
        'hoy': hoy,
    })


@login_required
def telemedicina_crear(request):
    form = ConsultaVirtualForm(request.POST or None)
    if form.is_valid():
        consulta = form.save(commit=False)
        # Integración con Microservicio de Telemedicina WebRTC (Puerto 8083)
        if not consulta.enlace_reunion:
            from apps.core.services_client import MicroservicesClient
            resp_sala = MicroservicesClient.crear_sala_telemedicina(
                cita_id=consulta.cita.id,
                veterinario=str(getattr(consulta.cita, 'veterinario', 'Dr. Veterinario')),
                paciente=consulta.cita.mascota.nombre,
                propietario=f"{consulta.cita.mascota.cliente.nombres} {consulta.cita.mascota.cliente.apellidos}"
            )
            if resp_sala and resp_sala.get('success'):
                consulta.enlace_reunion = resp_sala['sala']['url_acceso']
                consulta.codigo_acceso = resp_sala['sala']['sala_id']
        consulta.save()
        messages.success(request, 'Teleconsulta programada (Sala WebRTC generada por Microservicio).')
        from apps.core.red import enlace_sala_publico, ruta_sala
        if ruta_sala(consulta.enlace_reunion):
            from apps.agenda.views import _mensaje_whatsapp
            from apps.core.services_client import MicroservicesClient
            cita = consulta.cita
            notif = MicroservicesClient.notificar_cita(
                cita_id=cita.id,
                cliente_nombre=cita.mascota.cliente.nombre_completo,
                telefono=cita.mascota.cliente.telefono,
                mascota_nombre=cita.mascota.nombre,
                fecha=cita.fecha,
                hora=cita.hora,
                motivo=getattr(cita, 'motivo', 'Consulta General'),
                enlace_videollamada=enlace_sala_publico(request, consulta.enlace_reunion, 'cliente'),
            )
            _mensaje_whatsapp(request, notif)
        return redirect('telemedicina_lista')
        
    cita_id = request.GET.get('cita')
    if cita_id:
        form.initial['cita'] = cita_id
        
    return render(request, 'telemedicina/form.html', {'form': form, 'titulo': 'Programar Teleconsulta'})


@login_required
def telemedicina_editar(request, pk):
    consulta = get_object_or_404(ConsultaVirtual, pk=pk)
    form = ConsultaVirtualForm(request.POST or None, instance=consulta)
    if form.is_valid():
        form.save()
        messages.success(request, 'Datos de la teleconsulta actualizados.')
        return redirect('telemedicina_lista')
        
    return render(request, 'telemedicina/form.html', {'form': form, 'titulo': 'Editar Teleconsulta', 'consulta': consulta})


@login_required
def telemedicina_estado(request, pk, estado):
    consulta = get_object_or_404(ConsultaVirtual, pk=pk)
    if estado in dict(ConsultaVirtual.ESTADOS).keys():
        consulta.estado_conexion = estado
        consulta.save()
        messages.success(request, f'Estado de teleconsulta actualizado a {consulta.get_estado_conexion_display()}')
    return redirect('telemedicina_lista')
