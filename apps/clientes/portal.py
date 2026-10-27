from django.contrib.auth.models import Group

GRUPO_CLIENTES = 'Clientes'


def es_cliente(user):
    if not user.is_authenticated or user.is_staff or user.is_superuser:
        return False
    if hasattr(user, 'cliente_perfil'):
        return True
    if user.groups.filter(name=GRUPO_CLIENTES).exists():
        return True
    return user.socialaccount_set.exists()


def marcar_como_cliente(user):
    grupo, _ = Group.objects.get_or_create(name=GRUPO_CLIENTES)
    user.groups.add(grupo)
