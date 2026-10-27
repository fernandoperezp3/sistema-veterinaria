from django.shortcuts import redirect

from apps.clientes.portal import es_cliente

RUTAS_PERMITIDAS = ('/portal/', '/logout/', '/accounts/', '/static/', '/media/', '/sala/', '/ws/')


class PortalClienteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if es_cliente(request.user) and not request.path.startswith(RUTAS_PERMITIDAS):
            return redirect('portal_inicio')
        return self.get_response(request)
