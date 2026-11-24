from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from clientes.models import Cliente, Equipo
from core.roles import ADMINISTRADOR, RECEPCIONISTA, TECNICO
from inventario.models import Repuesto

from . import servicios
from .models import HistorialEstado, OrdenTrabajo

Estado = OrdenTrabajo.Estado
CLAVE = "Prueba-Segura-2026"


def crear_usuario(username, rol):
    u = User.objects.create_user(username=username, password=CLAVE)
    u.groups.add(Group.objects.get(name=rol))
    return u


class BaseOrdenTest(TestCase):
    def setUp(self):
        self.recepcion = crear_usuario("recepcion", RECEPCIONISTA)
        self.tecnico = crear_usuario("tecnico", TECNICO)
        self.otro_tecnico = crear_usuario("tecnico2", TECNICO)
        self.jefe = crear_usuario("jefe", ADMINISTRADOR)
        cliente = Cliente.objects.create(rut="12345678-5", nombre="María González", email="maria@example.com",
                                         telefono="+56922222222")
        self.equipo = Equipo.objects.create(cliente=cliente, tipo="NOTEBOOK", marca="Lenovo", modelo="IdeaPad")
        self.repuesto = Repuesto.objects.create(codigo="HDMI", nombre="Puerto HDMI", stock=3, stock_minimo=2,
                                                precio_unitario=8000)

    def nueva_orden(self):
        orden = OrdenTrabajo(equipo=self.equipo, falla_reportada="No da imagen por HDMI")
        return servicios.registrar_ingreso(orden, self.recepcion)


class FlujoEstadosTest(BaseOrdenTest):
    def test_flujo_completo_hasta_entrega_descuenta_stock_y_guarda_historial(self):
        with self.captureOnCommitCallbacks(execute=True):
            orden = self.nueva_orden()
            orden.tecnico = self.tecnico
            servicios.cambiar_estado(orden, Estado.ASIGNADA, self.jefe)
            servicios.cambiar_estado(orden, Estado.EN_DIAGNOSTICO, self.tecnico)
            servicios.cambiar_estado(orden, Estado.ESPERANDO_APROBACION, self.tecnico)
            servicios.cambiar_estado(orden, Estado.EN_REPARACION, self.recepcion)
            servicios.cambiar_estado(orden, Estado.PENDIENTE_REPUESTO, self.tecnico)
            servicios.cambiar_estado(orden, Estado.EN_REPARACION, self.tecnico)
            rep = servicios.registrar_reparacion(orden, self.tecnico, "Cambio de puerto", [(self.repuesto.pk, 1)])
            servicios.cambiar_estado(orden, Estado.ENTREGADA, self.recepcion)

        orden.refresh_from_db()
        self.repuesto.refresh_from_db()
        self.assertEqual(orden.estado, Estado.ENTREGADA)
        self.assertIsNotNone(orden.fecha_entrega)
        self.assertEqual(self.repuesto.stock, 2)                 # 3 - 1
        self.assertEqual(rep.alertas_stock, [self.repuesto])     # llegó al stock mínimo (2)
        self.assertEqual(orden.historial.count(), 9)             # ingreso + 8 cambios
        self.assertEqual(len(mail.outbox), 9)                    # un correo por cada cambio
        self.assertTrue(orden.notificaciones.filter(enviada=True).exists())

    def test_transicion_invalida_es_rechazada(self):
        orden = self.nueva_orden()
        with self.assertRaises(servicios.TransicionInvalida):
            servicios.cambiar_estado(orden, Estado.ENTREGADA, self.recepcion)
        self.assertEqual(orden.historial.count(), 1)

    def test_presupuesto_rechazado_termina_en_devuelta_sin_reparar(self):
        orden = self.nueva_orden()
        for estado in (Estado.ASIGNADA, Estado.EN_DIAGNOSTICO, Estado.ESPERANDO_APROBACION,
                       Estado.DEVUELTA_SIN_REPARAR):
            servicios.cambiar_estado(orden, estado, self.jefe)
        self.assertEqual(orden.TRANSICIONES[orden.estado], [])

    def test_stock_insuficiente_no_guarda_nada(self):
        orden = self.nueva_orden()
        for estado in (Estado.ASIGNADA, Estado.EN_DIAGNOSTICO, Estado.ESPERANDO_APROBACION, Estado.EN_REPARACION):
            servicios.cambiar_estado(orden, estado, self.jefe)
        with self.assertRaises(servicios.StockInsuficiente):
            servicios.registrar_reparacion(orden, self.tecnico, "Cambio", [(self.repuesto.pk, 10)])
        self.repuesto.refresh_from_db()
        orden.refresh_from_db()
        self.assertEqual(self.repuesto.stock, 3)            # rollback: el stock no cambió
        self.assertEqual(orden.estado, Estado.EN_REPARACION)
        self.assertFalse(hasattr(orden, "reparacion") and orden.reparacion)


class SeguridadVistasTest(BaseOrdenTest):
    def test_vistas_internas_exigen_login(self):
        r = self.client.get(reverse("lista_ordenes"))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('lista_ordenes')}")

    def test_tecnico_no_puede_crear_ordenes(self):
        self.client.login(username="tecnico", password=CLAVE)
        r = self.client.post(reverse("crear_orden"), {"equipo": self.equipo.pk, "falla_reportada": "Algo falla"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(OrdenTrabajo.objects.count(), 0)

    def test_recepcionista_crea_orden_valida(self):
        self.client.login(username="recepcion", password=CLAVE)
        r = self.client.post(reverse("crear_orden"), {"equipo": self.equipo.pk, "falla_reportada": "No enciende"})
        orden = OrdenTrabajo.objects.get()
        self.assertRedirects(r, reverse("detalle_orden", args=[orden.pk]))
        self.assertEqual(orden.recepcionista, self.recepcion)
        self.assertEqual(HistorialEstado.objects.filter(orden=orden).count(), 1)

    def test_tecnico_no_puede_operar_orden_de_otro_tecnico(self):
        orden = self.nueva_orden()
        orden.tecnico = self.otro_tecnico
        servicios.cambiar_estado(orden, Estado.ASIGNADA, self.jefe)
        self.client.login(username="tecnico", password=CLAVE)
        r = self.client.post(reverse("iniciar_diagnostico", args=[orden.pk]))
        self.assertEqual(r.status_code, 403)

    def test_solo_admin_asigna_tecnico(self):
        orden = self.nueva_orden()
        self.client.login(username="recepcion", password=CLAVE)
        r = self.client.post(reverse("asignar_tecnico", args=[orden.pk]), {"tecnico": self.tecnico.pk})
        self.assertEqual(r.status_code, 403)
        self.client.login(username="jefe", password=CLAVE)
        self.client.post(reverse("asignar_tecnico", args=[orden.pk]), {"tecnico": self.tecnico.pk})
        orden.refresh_from_db()
        self.assertEqual((orden.estado, orden.tecnico), (Estado.ASIGNADA, self.tecnico))

    def test_post_sin_token_csrf_es_rechazado(self):
        c = Client(enforce_csrf_checks=True)
        c.login(username="recepcion", password=CLAVE)
        r = c.post(reverse("crear_orden"), {"equipo": self.equipo.pk, "falla_reportada": "No enciende"})
        self.assertEqual(r.status_code, 403)

    def test_contrasena_se_guarda_como_hash(self):
        self.assertTrue(self.recepcion.password.startswith("pbkdf2_sha256$"))
        self.assertNotIn(CLAVE, self.recepcion.password)


class ConsultaClienteTest(BaseOrdenTest):
    def test_consulta_requiere_codigo_correcto(self):
        orden = self.nueva_orden()
        url = reverse("consulta_cliente")
        ok = self.client.get(url, {"numero": orden.pk, "codigo": orden.codigo_consulta})
        self.assertContains(ok, "Ingresada")
        malo = self.client.get(url, {"numero": orden.pk, "codigo": "00000000"})
        self.assertContains(malo, "No se encontró")
        self.assertNotContains(malo, self.equipo.marca)
