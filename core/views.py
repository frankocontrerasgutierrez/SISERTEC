from django.db.models import Count, F
from django.shortcuts import render

from clientes.models import Cliente
from inventario.models import Repuesto
from ordenes.forms import ConsultaClienteForm
from ordenes.models import OrdenTrabajo

from .roles import TECNICO, TODOS, rol_requerido, tiene_rol


@rol_requerido(*TODOS)
def panel(request):
    """Panel principal: resumen de órdenes por estado y alertas de stock (reporte básico)."""
    por_estado = dict(OrdenTrabajo.objects.values_list("estado").annotate(n=Count("id")))
    resumen = [(valor, etiqueta, por_estado.get(valor, 0)) for valor, etiqueta in OrdenTrabajo.Estado.choices]
    contexto = {
        "resumen": resumen,
        "total_ordenes": sum(por_estado.values()),
        "total_clientes": Cliente.objects.count(),
        "bajo_stock": Repuesto.objects.filter(stock__lte=F("stock_minimo")),
        "recientes": OrdenTrabajo.objects.select_related("equipo__cliente", "tecnico")[:8],
    }
    if tiene_rol(request.user, TECNICO) and not request.user.is_superuser:
        contexto["mis_ordenes"] = OrdenTrabajo.objects.filter(tecnico=request.user).exclude(
            estado__in=[OrdenTrabajo.Estado.ENTREGADA, OrdenTrabajo.Estado.DEVUELTA_SIN_REPARAR]
        )
    return render(request, "core/panel.html", contexto)


def consulta_cliente(request):
    """
    Actor Cliente: consulta el estado de su orden SIN iniciar sesión.
    Se exige número de orden + código aleatorio de 8 caracteres, para que nadie
    pueda ver órdenes ajenas solo adivinando números (OWASP A01).
    Se muestra el mismo mensaje si la orden no existe o el código es incorrecto.
    """
    form = ConsultaClienteForm(request.GET or None)
    orden = None
    no_encontrada = False
    if request.GET and form.is_valid():
        orden = OrdenTrabajo.objects.filter(
            pk=form.cleaned_data["numero"], codigo_consulta=form.cleaned_data["codigo"]
        ).select_related("equipo").first()
        no_encontrada = orden is None
    historial = orden.historial.all() if orden else []
    return render(request, "core/consulta.html",
                  {"form": form, "orden": orden, "historial": historial, "no_encontrada": no_encontrada})
