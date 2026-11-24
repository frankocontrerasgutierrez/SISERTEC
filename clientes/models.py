from django.db import models

from core.validadores import normalizar_rut, validar_rut, validar_telefono


class Cliente(models.Model):
    """Persona que lleva uno o más equipos a reparar."""

    rut = models.CharField("RUT", max_length=12, unique=True, validators=[validar_rut])
    nombre = models.CharField("Nombre completo", max_length=120)
    email = models.EmailField("Correo electrónico")
    telefono = models.CharField("Teléfono", max_length=15, validators=[validar_telefono])
    direccion = models.CharField("Dirección", max_length=200, blank=True)
    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def save(self, *args, **kwargs):
        # El RUT se guarda siempre en el mismo formato para que la restricción UNIQUE funcione.
        self.rut = normalizar_rut(self.rut)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class Equipo(models.Model):
    """Equipo de un cliente. Un cliente tiene uno o más equipos (relación 1..N)."""

    TIPOS = [
        ("COMPUTADOR", "Computador"),
        ("NOTEBOOK", "Notebook"),
        ("IMPRESORA", "Impresora"),
        ("CELULAR", "Celular"),
    ]

    # PROTECT: no se puede borrar un cliente que tenga equipos (integridad referencial).
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="equipos")
    tipo = models.CharField(max_length=12, choices=TIPOS)
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    numero_serie = models.CharField("Número de serie", max_length=60, blank=True)
    descripcion = models.TextField("Descripción / accesorios", blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_registro"]
        verbose_name = "equipo"
        verbose_name_plural = "equipos"

    def __str__(self):
        return f"{self.get_tipo_display()} {self.marca} {self.modelo}"
