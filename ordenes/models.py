import secrets

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from clientes.models import Equipo
from inventario.models import Repuesto


def generar_codigo_consulta():
    """Código aleatorio que el cliente usa para consultar su orden sin iniciar sesión."""
    return secrets.token_hex(4).upper()  # 8 caracteres, ej: 'A3F09C1B'


class OrdenTrabajo(models.Model):
    """Clase principal del sistema: el servicio técnico sobre un equipo."""

    class Estado(models.TextChoices):
        INGRESADA = "INGRESADA", "Ingresada"
        ASIGNADA = "ASIGNADA", "Asignada"
        EN_DIAGNOSTICO = "EN_DIAGNOSTICO", "En diagnóstico"
        ESPERANDO_APROBACION = "ESPERANDO_APROBACION", "Esperando aprobación"
        EN_REPARACION = "EN_REPARACION", "En reparación"
        PENDIENTE_REPUESTO = "PENDIENTE_REPUESTO", "Pendiente por repuesto"
        LISTA_ENTREGA = "LISTA_ENTREGA", "Lista para entrega"
        ENTREGADA = "ENTREGADA", "Entregada"
        DEVUELTA_SIN_REPARAR = "DEVUELTA_SIN_REPARAR", "Devuelta sin reparar"

    # Transiciones permitidas entre los 9 estados (máquina de estados).
    TRANSICIONES = {
        Estado.INGRESADA: [Estado.ASIGNADA],
        Estado.ASIGNADA: [Estado.EN_DIAGNOSTICO],
        Estado.EN_DIAGNOSTICO: [Estado.ESPERANDO_APROBACION],
        Estado.ESPERANDO_APROBACION: [Estado.EN_REPARACION, Estado.DEVUELTA_SIN_REPARAR],
        Estado.EN_REPARACION: [Estado.PENDIENTE_REPUESTO, Estado.LISTA_ENTREGA],
        Estado.PENDIENTE_REPUESTO: [Estado.EN_REPARACION],
        Estado.LISTA_ENTREGA: [Estado.ENTREGADA],
        Estado.ENTREGADA: [],
        Estado.DEVUELTA_SIN_REPARAR: [],
    }

    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name="ordenes")
    recepcionista = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="ordenes_recibidas"
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ordenes_asignadas",
    )
    falla_reportada = models.TextField("Falla reportada por el cliente")
    estado = models.CharField(max_length=25, choices=Estado.choices, default=Estado.INGRESADA)
    codigo_consulta = models.CharField(max_length=8, unique=True, default=generar_codigo_consulta, editable=False)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_ingreso"]
        verbose_name = "orden de trabajo"
        verbose_name_plural = "órdenes de trabajo"

    def __str__(self):
        return f"OT-{self.pk:05d}" if self.pk else "OT nueva"

    @property
    def cliente(self):
        return self.equipo.cliente

    def puede_cambiar_a(self, nuevo_estado) -> bool:
        return nuevo_estado in self.TRANSICIONES.get(self.estado, [])


class Diagnostico(models.Model):
    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name="diagnostico")
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField("Falla real detectada")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnóstico {self.orden}"


class Presupuesto(models.Model):
    class Respuesta(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name="presupuesto")
    detalle = models.TextField("Detalle del trabajo y repuestos")
    monto = models.DecimalField("Monto (CLP)", max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    respuesta = models.CharField(max_length=10, choices=Respuesta.choices, default=Respuesta.PENDIENTE)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Presupuesto {self.orden}: ${self.monto}"


class Reparacion(models.Model):
    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name="reparacion")
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    descripcion_trabajo = models.TextField("Trabajo realizado")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reparación {self.orden}"


class DetalleRepuesto(models.Model):
    """Repuesto usado en una reparación (tabla intermedia Reparación–Repuesto)."""

    reparacion = models.ForeignKey(Reparacion, on_delete=models.CASCADE, related_name="detalles")
    repuesto = models.ForeignKey(Repuesto, on_delete=models.PROTECT, related_name="usos")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.cantidad} x {self.repuesto.nombre}"


class HistorialEstado(models.Model):
    """Registro inmutable de cada cambio de estado de una orden (trazabilidad)."""

    # PROTECT: una orden con historial no se puede eliminar, así no se pierde la trazabilidad.
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.PROTECT, related_name="historial")
    estado_anterior = models.CharField(max_length=25, choices=OrdenTrabajo.Estado.choices, blank=True)
    estado_nuevo = models.CharField(max_length=25, choices=OrdenTrabajo.Estado.choices)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    observacion = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha", "pk"]
        verbose_name = "historial de estado"
        verbose_name_plural = "historial de estados"

    def __str__(self):
        return f"{self.orden}: {self.estado_anterior or '-'} → {self.estado_nuevo}"


class Notificacion(models.Model):
    """Correo enviado (o intentado) al cliente cuando cambia el estado de su orden."""

    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="notificaciones")
    destinatario = models.EmailField()
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    enviada = models.BooleanField(default=False)
    error = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"

    def __str__(self):
        return f"{self.asunto} → {self.destinatario}"
