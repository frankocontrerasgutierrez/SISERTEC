from django.contrib import admin

from .models import Repuesto


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "stock", "stock_minimo", "bajo_stock", "precio_unitario"]
    search_fields = ["codigo", "nombre"]

    @admin.display(boolean=True, description="Bajo stock")
    def bajo_stock(self, obj):
        return obj.bajo_stock
