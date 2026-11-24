from django.contrib import admin

from .models import Cliente, Equipo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["rut", "nombre", "email", "telefono"]
    search_fields = ["rut", "nombre"]


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ["__str__", "cliente", "numero_serie"]
    list_filter = ["tipo"]
