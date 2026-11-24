"""
Carga datos de demostración: 3 usuarios (uno por rol), clientes, equipos y repuestos.

Uso:  python manage.py cargar_demo --password "<clave_demo>"
La clave NO está escrita en el código: se entrega por parámetro o por la
variable DEMO_PASSWORD del archivo .env.
"""
import os

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError

from clientes.models import Cliente, Equipo
from core.roles import ADMINISTRADOR, RECEPCIONISTA, TECNICO
from inventario.models import Repuesto


class Command(BaseCommand):
    help = "Crea usuarios y datos de demostración para presentar el prototipo."

    def add_arguments(self, parser):
        parser.add_argument("--password", default=os.getenv("DEMO_PASSWORD", ""))

    def handle(self, *args, **opciones):
        clave = opciones["password"]
        if not clave:
            raise CommandError("Indique --password o defina DEMO_PASSWORD en .env")
        validate_password(clave)  # aplica las mismas reglas de contraseña del sistema

        usuarios = [
            ("recepcion", "Ana", "Rojas", RECEPCIONISTA, False),
            ("tecnico", "Pedro", "Soto", TECNICO, False),
            ("jefe", "Carla", "Muñoz", ADMINISTRADOR, True),
        ]
        for username, nombre, apellido, rol, staff in usuarios:
            u, creado = User.objects.get_or_create(username=username)
            u.first_name, u.last_name, u.is_staff = nombre, apellido, staff
            u.set_password(clave)  # se guarda como hash, nunca en texto plano
            u.save()
            u.groups.add(Group.objects.get(name=rol))
            self.stdout.write(f"Usuario {username} ({rol}) {'creado' if creado else 'actualizado'}")

        c1, _ = Cliente.objects.get_or_create(
            rut="11111111-1",
            defaults=dict(nombre="Juan Pérez Araya", email="juan.perez@example.com",
                          telefono="+56911111111", direccion="Copiapó"),
        )
        c2, _ = Cliente.objects.get_or_create(
            rut="12345678-5",
            defaults=dict(nombre="María González Tapia", email="maria.gonzalez@example.com",
                          telefono="+56922222222", direccion="Copiapó"),
        )
        Equipo.objects.get_or_create(cliente=c1, tipo="NOTEBOOK", marca="Lenovo", modelo="IdeaPad 3",
                                     defaults={"numero_serie": "LNV-001"})
        Equipo.objects.get_or_create(cliente=c2, tipo="IMPRESORA", marca="Epson", modelo="L3250",
                                     defaults={"numero_serie": "EPS-002"})

        repuestos = [
            ("PUE-HDMI", "Puerto HDMI notebook", 5, 2, 8000),
            ("SSD-480", "Disco SSD 480 GB", 3, 2, 32000),
            ("PAN-6.5", "Pantalla celular 6,5\"", 2, 2, 45000),
            ("RAM-8GB", "Memoria RAM 8 GB DDR4", 6, 2, 25000),
        ]
        for codigo, nombre, stock, minimo, precio in repuestos:
            Repuesto.objects.get_or_create(
                codigo=codigo,
                defaults=dict(nombre=nombre, stock=stock, stock_minimo=minimo, precio_unitario=precio),
            )
        self.stdout.write(self.style.SUCCESS("Datos de demostración cargados."))
