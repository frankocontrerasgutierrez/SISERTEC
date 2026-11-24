from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.roles import ADMINISTRADOR, RECEPCIONISTA, TECNICO, TODOS, rol_requerido, tiene_rol

from . import servicios
from .forms import (AsignarTecnicoForm, DiagnosticoPresupuestoForm, ObservacionForm, OrdenForm,
                    ReparacionForm, RespuestaPresupuestoForm)
from .models import Diagnostico, OrdenTrabajo, Presupuesto

Estado = OrdenTrabajo.Estado


def _verificar_tecnico_asignado(request, orden):
    """Un técnico solo puede trabajar sus propias órdenes (control de acceso a nivel de objeto)."""
    if tiene_rol(request.user, ADMINISTRADOR):
        return
    if orden.tecnico_id != request.user.id:
        raise PermissionDenied("Esta orden está asignada a otro técnico.")


@rol_requerido(*TODOS)
def lista_ordenes(request):
    ordenes = OrdenTrabajo.objects.select_related("equipo__cliente", "tecnico")
    estado = request.GET.get("estado", "")
    if estado in Estado.values:
        ordenes = ordenes.filter(estado=estado)
    if request.GET.get("mias") and tiene_rol(request.user, TECNICO):
        ordenes = ordenes.filter(tecnico=request.user)
    return render(request, "ordenes/lista.html",
                  {"ordenes": ordenes, "estados": Estado.choices, "estado": estado})


@rol_requerido(RECEPCIONISTA, ADMINISTRADOR)
def crear_orden(request):
    form = OrdenForm(request.POST or None, initial={"equipo": request.GET.get("equipo")})
    if request.method == "POST" and form.is_valid():
        orden = servicios.registrar_ingreso(form.save(commit=False), request.user)
        messages.success(request, f"Orden {orden} creada. Código de consulta del cliente: {orden.codigo_consulta}")
        return redirect("detalle_orden", pk=orden.pk)
    return render(request, "form.html", {"form": form, "titulo": "Nueva orden de trabajo"})


@rol_requerido(*TODOS)
def detalle_orden(request, pk):
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related("equipo__cliente", "tecnico", "recepcionista"), pk=pk
    )
    contexto = {
        "orden": orden,
        "historial": orden.historial.select_related("usuario"),
        "notificaciones": orden.notificaciones.all()[:5],
        "form_asignar": AsignarTecnicoForm(),
        "form_diag": DiagnosticoPresupuestoForm(),
        "form_respuesta": RespuestaPresupuestoForm(),
        "form_reparacion": ReparacionForm(),
        "form_obs": ObservacionForm(),
        "es_mi_orden": orden.tecnico_id == request.user.id or tiene_rol(request.user, ADMINISTRADOR),
    }
    return render(request, "ordenes/detalle.html", contexto)


def _cambio(request, orden, nuevo, observacion=""):
    try:
        servicios.cambiar_estado(orden, nuevo, request.user, observacion)
        messages.success(request, f"Estado actualizado a: {orden.get_estado_display()}")
    except servicios.TransicionInvalida as e:
        messages.error(request, str(e))


@require_POST
@rol_requerido(ADMINISTRADOR)
def asignar_tecnico(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    form = AsignarTecnicoForm(request.POST)
    if form.is_valid() and orden.puede_cambiar_a(Estado.ASIGNADA):
        with transaction.atomic():
            orden.tecnico = form.cleaned_data["tecnico"]
            orden.save(update_fields=["tecnico"])
            _cambio(request, orden, Estado.ASIGNADA, f"Asignada a {orden.tecnico.get_full_name() or orden.tecnico}")
    else:
        messages.error(request, "No se pudo asignar el técnico.")
    return redirect("detalle_orden", pk=pk)


@require_POST
@rol_requerido(TECNICO, ADMINISTRADOR)
def iniciar_diagnostico(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    _verificar_tecnico_asignado(request, orden)
    _cambio(request, orden, Estado.EN_DIAGNOSTICO)
    return redirect("detalle_orden", pk=pk)


@require_POST
@rol_requerido(TECNICO, ADMINISTRADOR)
def registrar_diagnostico(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    _verificar_tecnico_asignado(request, orden)
    form = DiagnosticoPresupuestoForm(request.POST)
    if not form.is_valid() or orden.estado != Estado.EN_DIAGNOSTICO:
        messages.error(request, "Revise los datos del diagnóstico y presupuesto.")
        return redirect("detalle_orden", pk=pk)
    d = form.cleaned_data
    with transaction.atomic():
        Diagnostico.objects.create(orden=orden, tecnico=request.user, descripcion=d["diagnostico"])
        Presupuesto.objects.create(orden=orden, detalle=d["detalle"], monto=d["monto"])
        _cambio(request, orden, Estado.ESPERANDO_APROBACION, f"Presupuesto ${d['monto']:,.0f}")
    return redirect("detalle_orden", pk=pk)


@require_POST
@rol_requerido(RECEPCIONISTA, ADMINISTRADOR)
def responder_presupuesto(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    form = RespuestaPresupuestoForm(request.POST)
    if not form.is_valid() or orden.estado != Estado.ESPERANDO_APROBACION:
        messages.error(request, "No se pudo registrar la respuesta.")
        return redirect("detalle_orden", pk=pk)
    respuesta = form.cleaned_data["respuesta"]
    with transaction.atomic():
        presupuesto = orden.presupuesto
        presupuesto.respuesta = respuesta
        presupuesto.fecha_respuesta = timezone.now()
        presupuesto.save()
        nuevo = Estado.EN_REPARACION if respuesta == "APROBADO" else Estado.DEVUELTA_SIN_REPARAR
        _cambio(request, orden, nuevo, f"Presupuesto {presupuesto.get_respuesta_display().lower()}")
    return redirect("detalle_orden", pk=pk)


@require_POST
@rol_requerido(TECNICO, ADMINISTRADOR)
def pendiente_repuesto(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    _verificar_tecnico_asignado(request, orden)
    form = ObservacionForm(request.POST)
    obs = form.cleaned_data["observacion"] if form.is_valid() else ""
    destino = Estado.EN_REPARACION if orden.estado == Estado.PENDIENTE_REPUESTO else Estado.PENDIENTE_REPUESTO
    _cambio(request, orden, destino, obs)
    return redirect("detalle_orden", pk=pk)


@require_POST
@rol_requerido(TECNICO, ADMINISTRADOR)
def registrar_reparacion(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    _verificar_tecnico_asignado(request, orden)
    form = ReparacionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Revise los datos de la reparación.")
        return redirect("detalle_orden", pk=pk)
    d = form.cleaned_data
    usados = [(d["repuesto"].pk, d["cantidad"])] if d.get("repuesto") else []
    try:
        reparacion = servicios.registrar_reparacion(orden, request.user, d["descripcion"], usados)
        messages.success(request, "Reparación registrada, stock descontado y orden lista para entrega.")
        for r in reparacion.alertas_stock:
            messages.warning(request, f"Alerta de stock mínimo: {r.nombre} quedó con {r.stock} unidades.")
    except (servicios.StockInsuficiente, servicios.TransicionInvalida) as e:
        messages.error(request, str(e))
    return redirect("detalle_orden", pk=pk)


@require_POST
@rol_requerido(RECEPCIONISTA, ADMINISTRADOR)
def registrar_entrega(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    _cambio(request, orden, Estado.ENTREGADA, "Equipo retirado por el cliente")
    return redirect("detalle_orden", pk=pk)
