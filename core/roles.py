"""
Control de acceso por roles (OWASP A01 - Broken Access Control).

Los roles se implementan con los Grupos de Django. Cada vista interna declara qué
roles pueden usarla; si el usuario no pertenece a uno de ellos se responde 403.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

RECEPCIONISTA = "Recepcionista"
TECNICO = "Tecnico"
ADMINISTRADOR = "Administrador"
TODOS = (RECEPCIONISTA, TECNICO, ADMINISTRADOR)


def tiene_rol(usuario, *roles) -> bool:
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    return usuario.groups.filter(name__in=roles).exists()


def rol_requerido(*roles):
    """Decorador: exige sesión iniciada y pertenecer a alguno de los roles indicados."""

    def decorador(vista):
        @login_required
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not tiene_rol(request.user, *roles):
                raise PermissionDenied("No tiene permisos para esta acción.")
            return vista(request, *args, **kwargs)

        return envoltura

    return decorador
