# SISERTEC — Sistema de gestión de servicio técnico

Prototipo funcional (Evaluación 3, Ingeniería de Software, INACAP) para la gestión del servicio técnico de
CICERTECH (Copiapó): clientes, equipos, órdenes de trabajo con 9 estados, diagnóstico, presupuesto, reparación,
repuestos e inventario, historial de estados, notificaciones por correo y consulta del cliente.

**Stack:** Python 3 · Django 5.2 · MySQL (mysqlclient) · Plantillas Django (HTML/CSS) · despliegue previsto Gunicorn + Nginx.

## Estructura

```
sisertec/      configuración (settings.py lee secretos desde .env), urls.py, wsgi.py
core/          roles (grupos), panel principal, consulta pública del cliente, comando cargar_demo
clientes/      Cliente y Equipo
inventario/    Repuesto (stock, stock mínimo)
ordenes/       OrdenTrabajo, Diagnostico, Presupuesto, Reparacion, DetalleRepuesto,
               HistorialEstado, Notificacion + servicios.py (reglas de negocio)
templates/     plantillas HTML        static/  CSS
database/      sisertec_mysql.sql (script de creación de la BD MySQL)
docs/          diagramas de arquitectura y entidad-relación
```

## Instalación y ejecución

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # editar: SECRET_KEY, DEBUG=True para desarrollo, datos de MySQL, DEMO_PASSWORD
```

### Base de datos MySQL

1. Crear la base y un usuario con privilegios limitados (ver encabezado de `database/sisertec_mysql.sql`):
   ```sql
   CREATE DATABASE sisertec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'sisertec_app'@'localhost' IDENTIFIED BY '<contraseña segura>';
   GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES, DROP ON sisertec.* TO 'sisertec_app'@'localhost';
   ```
2. En `.env`: `DB_ENGINE=mysql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
3. Crear las tablas (forma recomendada):
   ```powershell
   python manage.py migrate
   ```
   Alternativa: ejecutar `database/sisertec_mysql.sql` (generado desde las mismas migraciones).

> Si `DB_ENGINE` no se define, el proyecto usa SQLite (`db.sqlite3`) como respaldo de desarrollo/pruebas.

**Entorno usado en la evaluación:** MySQL Server 9.5.0 en una instancia local dedicada (127.0.0.1, puerto 3307,
`DB_PORT=3307`), con el usuario `sisertec_app`. En el equipo de desarrollo se inicia con
`%USERPROFILE%\mysql_sisertec\iniciar_mysql_sisertec.bat` (no forma parte del repositorio). En MySQL Workbench
existe la conexión "SISERTEC (MySQL 9.5 - puerto 3307)".

### Datos de demostración y servidor

```powershell
python manage.py cargar_demo --password "<clave de al menos 10 caracteres>"
python manage.py runserver
```

Usuarios de demostración: `recepcion` (Recepcionista), `tecnico` (Técnico), `jefe` (Administrador), todos con la
clave indicada. Para un superusuario: `python manage.py createsuperuser`.

- Personal: http://127.0.0.1:8000/login/
- Consulta del cliente (sin login): http://127.0.0.1:8000/consulta/ (N.º de orden + código de consulta)
- Administración de usuarios: http://127.0.0.1:8000/admin/

## Verificación

```powershell
python manage.py check
python manage.py test
```

Resultado al 19-11-2026: `check` sin problemas; 17 pruebas OK.

## Flujo de estados

Ingresada → Asignada → En diagnóstico → Esperando aprobación → En reparación ⇄ Pendiente por repuesto →
Lista para entrega → Entregada. Si el presupuesto se rechaza: Esperando aprobación → Devuelta sin reparar.
Cada cambio queda en `HistorialEstado` y genera un correo al cliente (consola en desarrollo, SMTP en producción).

## Despliegue previsto (no realizado aún)

VM Linux (IaaS) con Nginx (HTTPS, estáticos) → Gunicorn (`gunicorn sisertec.wsgi`) → Django → MySQL.
Con `DEBUG=False` se activan cookies Secure, redirección HTTPS y HSTS. Ejecutar `python manage.py collectstatic`.

## Seguridad

Secretos solo en `.env` (excluido por `.gitignore`), hash PBKDF2, CSRF, roles por grupo, control por objeto,
sesión de 30 min, ORM parametrizado, validación de RUT/correo/teléfono/montos/stock. Detalle en el informe.
