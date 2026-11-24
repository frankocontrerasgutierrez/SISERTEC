from django.core.validators import MinValueValidator
from django.db import models


class Repuesto(models.Model):
    """Repuesto del inventario. El stock se descuenta al registrar una reparación."""

    codigo = models.CharField("Código", max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField("Descripción", blank=True)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField("Stock mínimo", default=1)
    precio_unitario = models.DecimalField(
        "Precio unitario (CLP)", max_digits=10, decimal_places=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "repuesto"
        verbose_name_plural = "repuestos"
        constraints = [
            # Restricción también a nivel de base de datos: el stock nunca queda negativo.
            models.CheckConstraint(condition=models.Q(stock__gte=0), name="repuesto_stock_no_negativo"),
        ]

    @property
    def bajo_stock(self) -> bool:
        """Alerta: el repuesto llegó (o bajó) a su stock mínimo."""
        return self.stock <= self.stock_minimo

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
