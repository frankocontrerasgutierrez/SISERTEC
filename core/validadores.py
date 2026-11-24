"""Validadores reutilizables de SISERTEC (validación de entradas, OWASP A03)."""
import re

from django.core.exceptions import ValidationError


def normalizar_rut(rut: str) -> str:
    """Convierte '12.345.678-k' en '12345678-K'."""
    limpio = re.sub(r"[^0-9kK]", "", rut or "").upper()
    if len(limpio) < 2:
        return limpio
    return f"{limpio[:-1]}-{limpio[-1]}"


def calcular_dv(cuerpo: str) -> str:
    """Calcula el dígito verificador del RUT con el algoritmo módulo 11."""
    suma, factor = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    return {11: "0", 10: "K"}.get(resto, str(resto))


def validar_rut(valor: str) -> None:
    rut = normalizar_rut(valor)
    if not re.fullmatch(r"\d{7,8}-[0-9K]", rut):
        raise ValidationError("Formato de RUT inválido. Ejemplo: 12.345.678-5")
    cuerpo, dv = rut.split("-")
    if calcular_dv(cuerpo) != dv:
        raise ValidationError("El dígito verificador del RUT no es correcto.")


def validar_telefono(valor: str) -> None:
    if not re.fullmatch(r"\+?\d{8,12}", (valor or "").replace(" ", "")):
        raise ValidationError("Ingrese un teléfono válido (8 a 12 dígitos, ej: +56912345678).")
