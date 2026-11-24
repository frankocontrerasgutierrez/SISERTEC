from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from core.roles import ADMINISTRADOR, TODOS, rol_requerido

from .forms import RepuestoForm
from .models import Repuesto


@rol_requerido(*TODOS)
def lista_repuestos(request):
    repuestos = Repuesto.objects.all()
    bajo_stock = repuestos.filter(stock__lte=F("stock_minimo"))
    return render(request, "inventario/lista.html", {"repuestos": repuestos, "bajo_stock": bajo_stock})


@rol_requerido(ADMINISTRADOR)
def crear_repuesto(request):
    form = RepuestoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Repuesto agregado al inventario.")
        return redirect("lista_repuestos")
    return render(request, "form.html", {"form": form, "titulo": "Nuevo repuesto"})


@rol_requerido(ADMINISTRADOR)
def editar_repuesto(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    form = RepuestoForm(request.POST or None, instance=repuesto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Repuesto actualizado.")
        return redirect("lista_repuestos")
    return render(request, "form.html", {"form": form, "titulo": f"Editar {repuesto}"})
