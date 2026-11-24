from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from clientes import views as clientes
from core import views as core
from inventario import views as inventario
from ordenes import views as ordenes

urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticación (vistas propias de Django: CSRF, hash de contraseñas, rotación de sesión)
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("cambiar-clave/", auth_views.PasswordChangeView.as_view(success_url="/"), name="cambiar_clave"),
    # Panel y consulta pública del cliente
    path("", core.panel, name="panel"),
    path("consulta/", core.consulta_cliente, name="consulta_cliente"),
    # Clientes y equipos
    path("clientes/", clientes.lista_clientes, name="lista_clientes"),
    path("clientes/nuevo/", clientes.crear_cliente, name="crear_cliente"),
    path("clientes/<int:pk>/", clientes.detalle_cliente, name="detalle_cliente"),
    path("clientes/<int:pk>/editar/", clientes.editar_cliente, name="editar_cliente"),
    path("equipos/nuevo/", clientes.crear_equipo, name="crear_equipo"),
    # Inventario
    path("repuestos/", inventario.lista_repuestos, name="lista_repuestos"),
    path("repuestos/nuevo/", inventario.crear_repuesto, name="crear_repuesto"),
    path("repuestos/<int:pk>/editar/", inventario.editar_repuesto, name="editar_repuesto"),
    # Órdenes de trabajo y su flujo de estados
    path("ordenes/", ordenes.lista_ordenes, name="lista_ordenes"),
    path("ordenes/nueva/", ordenes.crear_orden, name="crear_orden"),
    path("ordenes/<int:pk>/", ordenes.detalle_orden, name="detalle_orden"),
    path("ordenes/<int:pk>/asignar/", ordenes.asignar_tecnico, name="asignar_tecnico"),
    path("ordenes/<int:pk>/iniciar-diagnostico/", ordenes.iniciar_diagnostico, name="iniciar_diagnostico"),
    path("ordenes/<int:pk>/diagnostico/", ordenes.registrar_diagnostico, name="registrar_diagnostico"),
    path("ordenes/<int:pk>/respuesta/", ordenes.responder_presupuesto, name="responder_presupuesto"),
    path("ordenes/<int:pk>/repuesto/", ordenes.pendiente_repuesto, name="pendiente_repuesto"),
    path("ordenes/<int:pk>/reparacion/", ordenes.registrar_reparacion, name="registrar_reparacion"),
    path("ordenes/<int:pk>/entrega/", ordenes.registrar_entrega, name="registrar_entrega"),
]

admin.site.site_header = "SISERTEC - Administración"
admin.site.site_title = "SISERTEC"
