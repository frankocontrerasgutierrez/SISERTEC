from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.roles import ADMINISTRADOR, RECEPCIONISTA, TODOS, rol_requerido

from .forms import ClienteForm, EquipoForm
from .models import Cliente


@rol_requerido(*TODOS)
def lista_clientes(request):
    q = request.GET.get("q", "").strip()
    clientes = Cliente.objects.all()
    if q:
        # El ORM de Django parametriza la consulta: no hay riesgo de inyección SQL.
        clientes = clientes.filter(Q(nombre__icontains=q) | Q(rut__icontains=q))
    return render(request, "clientes/lista.html", {"clientes": clientes, "q": q})


@rol_requerido(RECEPCIONISTA, ADMINISTRADOR)
def crear_cliente(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cliente = form.save()
        messages.success(request, f"Cliente {cliente.nombre} registrado.")
        return redirect("detalle_cliente", pk=cliente.pk)
    return render(request, "form.html", {"form": form, "titulo": "Registrar cliente"})


@rol_requerido(RECEPCIONISTA, ADMINISTRADOR)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cliente actualizado.")
        return redirect("detalle_cliente", pk=pk)
    return render(request, "form.html", {"form": form, "titulo": f"Editar {cliente.nombre}"})


@rol_requerido(*TODOS)
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, "clientes/detalle.html", {"cliente": cliente})


@rol_requerido(RECEPCIONISTA, ADMINISTRADOR)
def crear_equipo(request):
    form = EquipoForm(request.POST or None, initial={"cliente": request.GET.get("cliente")})
    if request.method == "POST" and form.is_valid():
        equipo = form.save()
        messages.success(request, f"Equipo {equipo} registrado.")
        return redirect("detalle_cliente", pk=equipo.cliente_id)
    return render(request, "form.html", {"form": form, "titulo": "Registrar equipo"})
