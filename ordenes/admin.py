from django.contrib import admin

from .models import (DetalleRepuesto, Diagnostico, HistorialEstado, Notificacion, OrdenTrabajo, Presupuesto,
                     Reparacion)


class HistorialInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    can_delete = False
    readonly_fields = ["estado_anterior", "estado_nuevo", "usuario", "observacion", "fecha"]

    def has_add_permission(self, request, obj=None):
        return False  # el historial solo lo escribe el sistema


@admin.register(OrdenTrabajo)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ["__str__", "equipo", "estado", "tecnico", "fecha_ingreso"]
    list_filter = ["estado", "tecnico"]
    search_fields = ["equipo__cliente__nombre", "equipo__cliente__rut"]
    readonly_fields = ["estado", "codigo_consulta"]  # el estado solo cambia por el flujo validado
    inlines = [HistorialInline]


@admin.register(HistorialEstado)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ["orden", "estado_anterior", "estado_nuevo", "usuario", "fecha"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register([Diagnostico, Presupuesto, Reparacion, DetalleRepuesto, Notificacion])
