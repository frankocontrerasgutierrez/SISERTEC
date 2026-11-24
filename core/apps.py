from django.apps import AppConfig
from django.db.models.signals import post_migrate


def crear_grupos(sender, **kwargs):
    """
    Crea los 3 roles internos después de cada `migrate`.
    El Administrador recibe permisos sobre usuarios, clientes, inventario y órdenes
    para poder gestionarlos también desde el sitio /admin/.
    """
    from django.contrib.auth.models import Group, Permission

    from .roles import ADMINISTRADOR, RECEPCIONISTA, TECNICO

    for nombre in (RECEPCIONISTA, TECNICO):
        Group.objects.get_or_create(name=nombre)
    admin, _ = Group.objects.get_or_create(name=ADMINISTRADOR)
    permisos = Permission.objects.filter(
        content_type__app_label__in=["auth", "clientes", "inventario", "ordenes"]
    )
    admin.permissions.set(permisos)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Núcleo SISERTEC"

    def ready(self):
        post_migrate.connect(crear_grupos, sender=self)
