from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from core.validadores import normalizar_rut, validar_rut

from .forms import ClienteForm
from .models import Cliente, Equipo


class ValidacionRutTest(TestCase):
    def test_rut_valido_con_y_sin_formato(self):
        validar_rut("12.345.678-5")
        validar_rut("11111111-1")
        self.assertEqual(normalizar_rut("12.345.678-k"), "12345678-K")

    def test_rut_con_digito_verificador_incorrecto(self):
        with self.assertRaises(ValidationError):
            validar_rut("12.345.678-9")


class ClienteFormTest(TestCase):
    datos = {"rut": "12.345.678-5", "nombre": "María González", "email": "maria@example.com",
             "telefono": "+56922222222"}

    def test_formulario_valido_normaliza_rut(self):
        form = ClienteForm(self.datos)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().rut, "12345678-5")

    def test_rut_duplicado_y_datos_invalidos(self):
        ClienteForm(self.datos).save()
        form = ClienteForm({**self.datos, "rut": "12345678-5", "email": "no-es-correo", "telefono": "abc"})
        self.assertFalse(form.is_valid())
        self.assertIn("rut", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("telefono", form.errors)


class IntegridadReferencialTest(TestCase):
    def test_no_se_borra_cliente_con_equipos(self):
        c = Cliente.objects.create(rut="11111111-1", nombre="Juan", email="j@example.com", telefono="+56911111111")
        Equipo.objects.create(cliente=c, tipo="CELULAR", marca="Samsung", modelo="A14")
        with self.assertRaises(ProtectedError):
            c.delete()
