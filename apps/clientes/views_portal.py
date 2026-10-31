from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.agenda.models import Cita
from apps.clientes.forms import MascotaForm, PerfilClienteForm
from apps.clientes.models import Cliente
from apps.clientes.portal import es_cliente, marcar_como_cliente


def _enlace_sala(cita, request):
    consulta = getattr(cita, 'consulta_virtual', None)
    if not consulta or not consulta.enlace_reunion or consulta.estado_conexion in ('FINALIZADA', 'CANCELADA'):
        return None
    enlace = consulta.enlace_reunion
    if '/sala/' in enlace and ':8083' in enlace:
        ruta = '/sala/' + enlace.split('/sala/', 1)[1]
        if request.is_secure():
            return ruta + '?rol=cliente'
        return f"http://{request.get_host().split(':')[0]}:8083{ruta}?rol=cliente"
    return enlace


def _ocultar_correo(correo):
    if not correo or '@' not in correo:
        return 'otra cuenta'
    usuario, dominio = correo.split('@', 1)
    return f"{usuario[:3]}***@{dominio}"


def _cliente_de(user):
    cliente = getattr(user, 'cliente_perfil', None)
    if cliente:
        return cliente
    if user.email:
        cliente = Cliente.objects.filter(email__iexact=user.email, usuario__isnull=True).first()
        if cliente:
            cliente.usuario = user
            cliente.save(update_fields=['usuario'])
            marcar_como_cliente(user)
            return cliente
    return None


@login_required
def portal_inicio(request):
    if not es_cliente(request.user):
        return redirect('dashboard')
    cliente = _cliente_de(request.user)
    if not cliente:
        return redirect('portal_perfil')

    hoy = timezone.localdate()
    citas = Cita.objects.filter(mascota__cliente=cliente, is_active=True).select_related(
        'mascota', 'veterinario'
    ).order_by('-fecha', '-hora')
    proximas = []
    anteriores = []
    for cita in citas:
        cita.enlace_sala = _enlace_sala(cita, request)
        if cita.fecha >= hoy and cita.estado not in ('COMPLETADA', 'CANCELADA'):
            proximas.append(cita)
        else:
            anteriores.append(cita)
    proximas.sort(key=lambda c: (c.fecha, c.hora))

    return render(request, 'portal/inicio.html', {
        'cliente': cliente,
        'mascotas': cliente.mascotas.filter(is_active=True),
        'proximas': proximas,
        'anteriores': anteriores[:10],
    })


@login_required
def portal_perfil(request):
    if not es_cliente(request.user):
        return redirect('dashboard')
    cliente = _cliente_de(request.user)
    inicial = {}
    if not cliente:
        inicial = {
            'nombres': request.user.first_name,
            'apellidos': request.user.last_name,
        }
    if request.method == 'POST' and not cliente:
        existente = Cliente.objects.filter(dni=(request.POST.get('dni') or '').strip()).select_related('usuario').first()
        if existente and existente.usuario_id and existente.usuario_id != request.user.id:
            messages.error(
                request,
                f'Ese DPI ya está registrado con otra cuenta de Google ({_ocultar_correo(existente.usuario.email)}). '
                'Cierra sesión y entra con esa cuenta para ver tus mascotas y citas.'
            )
            form = PerfilClienteForm(request.POST)
            return render(request, 'portal/perfil.html', {'form': form, 'nuevo': True})
        if existente:
            cliente = existente
    form = PerfilClienteForm(request.POST or None, instance=cliente, initial=inicial)
    if form.is_valid():
        nuevo = form.save(commit=False)
        nuevo.usuario = request.user
        if not nuevo.email:
            nuevo.email = request.user.email
        nuevo.save()
        marcar_como_cliente(request.user)
        messages.success(request, 'Tus datos se guardaron correctamente.')
        return redirect('portal_inicio')
    return render(request, 'portal/perfil.html', {'form': form, 'nuevo': cliente is None})


@login_required
def portal_mascota_nueva(request):
    if not es_cliente(request.user):
        return redirect('dashboard')
    cliente = _cliente_de(request.user)
    if not cliente:
        return redirect('portal_perfil')
    form = MascotaForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        mascota = form.save(commit=False)
        mascota.cliente = cliente
        mascota.save()
        messages.success(request, f'{mascota.nombre} quedó registrada.')
        return redirect('portal_inicio')
    return render(request, 'portal/mascota_form.html', {'form': form})
