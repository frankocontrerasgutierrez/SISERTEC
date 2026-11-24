"""
Lógica de negocio de las órdenes de trabajo (capa de negocio).

Se separa de las vistas para que las reglas (transiciones de estado, historial,
notificación y descuento de inventario) estén en un solo lugar y se puedan probar.
"""
import logging

from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from inventario.models import Repuesto

from .models import DetalleRepuesto, HistorialEstado, Notificacion, OrdenTrabajo, Reparacion

logger = logging.getLogger("sisertec")


class TransicionInvalida(Exception):
    pass


class StockInsuficiente(Exception):
    pass


def notificar_cliente(orden: OrdenTrabajo) -> Notificacion:
    """Envía un correo al cliente con el nuevo estado y deja registro del intento."""
    cliente = orden.cliente
    asunto = f"SISERTEC - {orden}: {orden.get_estado_display()}"
    mensaje = (
        f"Estimado/a {cliente.nombre}:\n\n"
        f"Su orden {orden} ({orden.equipo}) cambió al estado: {orden.get_estado_display()}.\n"
        f"Puede consultar el detalle con su número de orden {orden.pk} y código {orden.codigo_consulta}.\n\n"
        "Servicio técnico SISERTEC"
    )
    notificacion = Notificacion(orden=orden, destinatario=cliente.email, asunto=asunto, mensaje=mensaje)
    try:
        send_mail(asunto, mensaje, None, [cliente.email], fail_silently=False)
        notificacion.enviada = True
    except Exception as exc:  # Un fallo de correo no debe impedir el cambio de estado.
        notificacion.error = str(exc)[:255]
        logger.warning("No se pudo notificar la orden %s: %s", orden.pk, exc)
    notificacion.save()
    return notificacion


def cambiar_estado(orden: OrdenTrabajo, nuevo_estado: str, usuario, observacion: str = "") -> OrdenTrabajo:
    """Valida la transición, guarda el historial y notifica al cliente."""
    if not orden.puede_cambiar_a(nuevo_estado):
        raise TransicionInvalida(
            f"No se puede pasar de '{orden.get_estado_display()}' a "
            f"'{OrdenTrabajo.Estado(nuevo_estado).label}'."
        )
    with transaction.atomic():
        anterior = orden.estado
        orden.estado = nuevo_estado
        if nuevo_estado in (OrdenTrabajo.Estado.ENTREGADA, OrdenTrabajo.Estado.DEVUELTA_SIN_REPARAR):
            orden.fecha_entrega = timezone.now()
        orden.save()
        HistorialEstado.objects.create(
            orden=orden, estado_anterior=anterior, estado_nuevo=nuevo_estado,
            usuario=usuario, observacion=observacion[:255],
        )
    logger.info("Orden %s: %s -> %s por %s", orden.pk, anterior, nuevo_estado, usuario)
    transaction.on_commit(lambda: notificar_cliente(orden))
    return orden


def registrar_ingreso(orden: OrdenTrabajo, usuario) -> OrdenTrabajo:
    """Guarda una orden nueva en estado 'Ingresada' con su primer registro de historial."""
    with transaction.atomic():
        orden.recepcionista = usuario
        orden.estado = OrdenTrabajo.Estado.INGRESADA
        orden.save()
        HistorialEstado.objects.create(
            orden=orden, estado_nuevo=orden.estado, usuario=usuario, observacion="Ingreso del equipo"
        )
    transaction.on_commit(lambda: notificar_cliente(orden))
    return orden


def registrar_reparacion(orden: OrdenTrabajo, usuario, descripcion: str, repuestos_usados) -> Reparacion:
    """
    Registra la reparación, descuenta los repuestos del inventario y deja la orden
    'Lista para entrega'. Todo ocurre en una transacción: si un repuesto no tiene
    stock suficiente, no se guarda nada (no quedan inventarios inconsistentes).

    repuestos_usados: lista de tuplas (repuesto_id, cantidad).
    """
    if orden.estado != OrdenTrabajo.Estado.EN_REPARACION:
        raise TransicionInvalida("Solo se puede registrar la reparación de una orden 'En reparación'.")

    with transaction.atomic():
        reparacion = Reparacion.objects.create(orden=orden, tecnico=usuario, descripcion_trabajo=descripcion)
        alertas = []
        for repuesto_id, cantidad in repuestos_usados:
            # select_for_update bloquea la fila para evitar que dos técnicos usen el mismo stock a la vez.
            repuesto = Repuesto.objects.select_for_update().get(pk=repuesto_id)
            if repuesto.stock < cantidad:
                raise StockInsuficiente(
                    f"Stock insuficiente de {repuesto.nombre}: hay {repuesto.stock}, se piden {cantidad}."
                )
            repuesto.stock -= cantidad
            repuesto.save(update_fields=["stock"])
            DetalleRepuesto.objects.create(
                reparacion=reparacion, repuesto=repuesto, cantidad=cantidad,
                precio_unitario=repuesto.precio_unitario,
            )
            if repuesto.bajo_stock:
                alertas.append(repuesto)
        cambiar_estado(orden, OrdenTrabajo.Estado.LISTA_ENTREGA, usuario, "Reparación registrada")
    for repuesto in alertas:
        logger.warning("ALERTA stock mínimo: %s (stock %s)", repuesto, repuesto.stock)
    reparacion.alertas_stock = alertas
    return reparacion
