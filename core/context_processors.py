from .roles import ADMINISTRADOR, RECEPCIONISTA, TECNICO, tiene_rol


def roles(request):
    """Expone a las plantillas qué rol tiene el usuario, para mostrar solo sus opciones."""
    u = request.user
    return {
        "es_recepcionista": tiene_rol(u, RECEPCIONISTA),
        "es_tecnico": tiene_rol(u, TECNICO),
        "es_admin": tiene_rol(u, ADMINISTRADOR),
    }
