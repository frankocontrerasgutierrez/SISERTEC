-- =====================================================================
-- SISERTEC - Script de creación de la base de datos MySQL
-- Generado automáticamente desde las migraciones de Django (sqlmigrate)
-- Motor: MySQL 8.0+ / 9.x, InnoDB, utf8mb4
-- Forma recomendada de crear las tablas: python manage.py migrate
-- =====================================================================

CREATE DATABASE IF NOT EXISTS sisertec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sisertec;

-- Usuario de la aplicación con privilegios mínimos (cambie la contraseña):
-- CREATE USER 'sisertec_app'@'localhost' IDENTIFIED BY '<CAMBIAR_CONTRASEÑA>';
-- GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES, DROP ON sisertec.* TO 'sisertec_app'@'localhost';

-- ---- Migración contenttypes.0001_initial ----
--
-- Create model ContentType
--
CREATE TABLE `django_content_type` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(100) NOT NULL, `app_label` varchar(100) NOT NULL, `model` varchar(100) NOT NULL);
--
-- Alter unique_together for contenttype (1 constraint(s))
--
ALTER TABLE `django_content_type` ADD CONSTRAINT `django_content_type_app_label_model_76bd3d3b_uniq` UNIQUE (`app_label`, `model`);

-- ---- Migración auth.0001_initial ----
--
-- Create model Permission
--
CREATE TABLE `auth_permission` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(50) NOT NULL, `content_type_id` integer NOT NULL, `codename` varchar(100) NOT NULL);
--
-- Create model Group
--
CREATE TABLE `auth_group` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(80) NOT NULL UNIQUE);
CREATE TABLE `auth_group_permissions` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `group_id` integer NOT NULL, `permission_id` integer NOT NULL);
--
-- Create model User
--
CREATE TABLE `auth_user` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `password` varchar(128) NOT NULL, `last_login` datetime(6) NOT NULL, `is_superuser` bool NOT NULL, `username` varchar(30) NOT NULL UNIQUE, `first_name` varchar(30) NOT NULL, `last_name` varchar(30) NOT NULL, `email` varchar(75) NOT NULL, `is_staff` bool NOT NULL, `is_active` bool NOT NULL, `date_joined` datetime(6) NOT NULL);
CREATE TABLE `auth_user_groups` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` integer NOT NULL, `group_id` integer NOT NULL);
CREATE TABLE `auth_user_user_permissions` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` integer NOT NULL, `permission_id` integer NOT NULL);
ALTER TABLE `auth_permission` ADD CONSTRAINT `auth_permission_content_type_id_codename_01ab375a_uniq` UNIQUE (`content_type_id`, `codename`);
ALTER TABLE `auth_permission` ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` UNIQUE (`group_id`, `permission_id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);
ALTER TABLE `auth_user_groups` ADD CONSTRAINT `auth_user_groups_user_id_group_id_94350c0c_uniq` UNIQUE (`user_id`, `group_id`);
ALTER TABLE `auth_user_groups` ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `auth_user_groups` ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `auth_user_user_permissions` ADD CONSTRAINT `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` UNIQUE (`user_id`, `permission_id`);
ALTER TABLE `auth_user_user_permissions` ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `auth_user_user_permissions` ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);

-- ---- Migración admin.0001_initial ----
--
-- Create model LogEntry
--
CREATE TABLE `django_admin_log` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `action_time` datetime(6) NOT NULL, `object_id` longtext NULL, `object_repr` varchar(200) NOT NULL, `action_flag` smallint UNSIGNED NOT NULL CHECK (`action_flag` >= 0), `change_message` longtext NOT NULL, `content_type_id` integer NULL, `user_id` integer NOT NULL);
ALTER TABLE `django_admin_log` ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
ALTER TABLE `django_admin_log` ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

-- ---- Migración admin.0002_logentry_remove_auto_add ----
--
-- Alter field action_time on logentry
--
-- (no-op)

-- ---- Migración admin.0003_logentry_add_action_flag_choices ----
--
-- Alter field action_flag on logentry
--
-- (no-op)

-- ---- Migración contenttypes.0002_remove_content_type_name ----
--
-- Change Meta options on contenttype
--
-- (no-op)
--
-- Alter field name on contenttype
--
ALTER TABLE `django_content_type` MODIFY `name` varchar(100) NULL;
--
-- Raw Python operation
--
-- THIS OPERATION CANNOT BE WRITTEN AS SQL
--
-- Remove field name from contenttype
--
ALTER TABLE `django_content_type` DROP COLUMN `name`;

-- ---- Migración auth.0002_alter_permission_name_max_length ----
--
-- Alter field name on permission
--
ALTER TABLE `auth_permission` MODIFY `name` varchar(255) NOT NULL;

-- ---- Migración auth.0003_alter_user_email_max_length ----
--
-- Alter field email on user
--
ALTER TABLE `auth_user` MODIFY `email` varchar(254) NOT NULL;

-- ---- Migración auth.0004_alter_user_username_opts ----
--
-- Alter field username on user
--
-- (no-op)

-- ---- Migración auth.0005_alter_user_last_login_null ----
--
-- Alter field last_login on user
--
ALTER TABLE `auth_user` MODIFY `last_login` datetime(6) NULL;

-- ---- Migración auth.0006_require_contenttypes_0002 ----

-- ---- Migración auth.0007_alter_validators_add_error_messages ----
--
-- Alter field username on user
--
-- (no-op)

-- ---- Migración auth.0008_alter_user_username_max_length ----
--
-- Alter field username on user
--
ALTER TABLE `auth_user` MODIFY `username` varchar(150) NOT NULL;

-- ---- Migración auth.0009_alter_user_last_name_max_length ----
--
-- Alter field last_name on user
--
ALTER TABLE `auth_user` MODIFY `last_name` varchar(150) NOT NULL;

-- ---- Migración auth.0010_alter_group_name_max_length ----
--
-- Alter field name on group
--
ALTER TABLE `auth_group` MODIFY `name` varchar(150) NOT NULL;

-- ---- Migración auth.0011_update_proxy_permissions ----
--
-- Raw Python operation
--
-- THIS OPERATION CANNOT BE WRITTEN AS SQL

-- ---- Migración auth.0012_alter_user_first_name_max_length ----
--
-- Alter field first_name on user
--
ALTER TABLE `auth_user` MODIFY `first_name` varchar(150) NOT NULL;

-- ---- Migración clientes.0001_initial ----
--
-- Create model Cliente
--
CREATE TABLE `clientes_cliente` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `rut` varchar(12) NOT NULL UNIQUE, `nombre` varchar(120) NOT NULL, `email` varchar(254) NOT NULL, `telefono` varchar(15) NOT NULL, `direccion` varchar(200) NOT NULL, `fecha_registro` datetime(6) NOT NULL);
--
-- Create model Equipo
--
CREATE TABLE `clientes_equipo` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `tipo` varchar(12) NOT NULL, `marca` varchar(60) NOT NULL, `modelo` varchar(60) NOT NULL, `numero_serie` varchar(60) NOT NULL, `descripcion` longtext NOT NULL, `fecha_registro` datetime(6) NOT NULL, `cliente_id` bigint NOT NULL);
ALTER TABLE `clientes_equipo` ADD CONSTRAINT `clientes_equipo_cliente_id_b4b4392a_fk_clientes_cliente_id` FOREIGN KEY (`cliente_id`) REFERENCES `clientes_cliente` (`id`);

-- ---- Migración inventario.0001_initial ----
--
-- Create model Repuesto
--
CREATE TABLE `inventario_repuesto` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `codigo` varchar(30) NOT NULL UNIQUE, `nombre` varchar(100) NOT NULL, `descripcion` longtext NOT NULL, `stock` integer UNSIGNED NOT NULL CHECK (`stock` >= 0), `stock_minimo` integer UNSIGNED NOT NULL CHECK (`stock_minimo` >= 0), `precio_unitario` numeric(10, 0) NOT NULL, CONSTRAINT `repuesto_stock_no_negativo` CHECK (`stock` >= 0));

-- ---- Migración ordenes.0001_initial ----
--
-- Create model OrdenTrabajo
--
CREATE TABLE `ordenes_ordentrabajo` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `falla_reportada` longtext NOT NULL, `estado` varchar(25) NOT NULL, `codigo_consulta` varchar(8) NOT NULL UNIQUE, `fecha_ingreso` datetime(6) NOT NULL, `fecha_entrega` datetime(6) NULL, `equipo_id` bigint NOT NULL, `recepcionista_id` integer NULL, `tecnico_id` integer NULL);
--
-- Create model Notificacion
--
CREATE TABLE `ordenes_notificacion` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `destinatario` varchar(254) NOT NULL, `asunto` varchar(150) NOT NULL, `mensaje` longtext NOT NULL, `enviada` bool NOT NULL, `error` varchar(255) NOT NULL, `fecha` datetime(6) NOT NULL, `orden_id` bigint NOT NULL);
--
-- Create model HistorialEstado
--
CREATE TABLE `ordenes_historialestado` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `estado_anterior` varchar(25) NOT NULL, `estado_nuevo` varchar(25) NOT NULL, `observacion` varchar(255) NOT NULL, `fecha` datetime(6) NOT NULL, `usuario_id` integer NULL, `orden_id` bigint NOT NULL);
--
-- Create model Diagnostico
--
CREATE TABLE `ordenes_diagnostico` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `descripcion` longtext NOT NULL, `fecha` datetime(6) NOT NULL, `tecnico_id` integer NULL, `orden_id` bigint NOT NULL UNIQUE);
--
-- Create model Presupuesto
--
CREATE TABLE `ordenes_presupuesto` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `detalle` longtext NOT NULL, `monto` numeric(10, 0) NOT NULL, `respuesta` varchar(10) NOT NULL, `fecha` datetime(6) NOT NULL, `fecha_respuesta` datetime(6) NULL, `orden_id` bigint NOT NULL UNIQUE);
--
-- Create model Reparacion
--
CREATE TABLE `ordenes_reparacion` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `descripcion_trabajo` longtext NOT NULL, `fecha` datetime(6) NOT NULL, `orden_id` bigint NOT NULL UNIQUE, `tecnico_id` integer NULL);
--
-- Create model DetalleRepuesto
--
CREATE TABLE `ordenes_detallerepuesto` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `cantidad` integer UNSIGNED NOT NULL CHECK (`cantidad` >= 0), `precio_unitario` numeric(10, 0) NOT NULL, `repuesto_id` bigint NOT NULL, `reparacion_id` bigint NOT NULL);
ALTER TABLE `ordenes_ordentrabajo` ADD CONSTRAINT `ordenes_ordentrabajo_equipo_id_308a2199_fk_clientes_equipo_id` FOREIGN KEY (`equipo_id`) REFERENCES `clientes_equipo` (`id`);
ALTER TABLE `ordenes_ordentrabajo` ADD CONSTRAINT `ordenes_ordentrabajo_recepcionista_id_51c2cead_fk_auth_user_id` FOREIGN KEY (`recepcionista_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `ordenes_ordentrabajo` ADD CONSTRAINT `ordenes_ordentrabajo_tecnico_id_3edd6e5e_fk_auth_user_id` FOREIGN KEY (`tecnico_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `ordenes_notificacion` ADD CONSTRAINT `ordenes_notificacion_orden_id_6daf9eab_fk_ordenes_o` FOREIGN KEY (`orden_id`) REFERENCES `ordenes_ordentrabajo` (`id`);
ALTER TABLE `ordenes_historialestado` ADD CONSTRAINT `ordenes_historialestado_usuario_id_ccacc0f3_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `ordenes_historialestado` ADD CONSTRAINT `ordenes_historialest_orden_id_92391427_fk_ordenes_o` FOREIGN KEY (`orden_id`) REFERENCES `ordenes_ordentrabajo` (`id`);
ALTER TABLE `ordenes_diagnostico` ADD CONSTRAINT `ordenes_diagnostico_tecnico_id_de2b7240_fk_auth_user_id` FOREIGN KEY (`tecnico_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `ordenes_diagnostico` ADD CONSTRAINT `ordenes_diagnostico_orden_id_56bb252f_fk_ordenes_ordentrabajo_id` FOREIGN KEY (`orden_id`) REFERENCES `ordenes_ordentrabajo` (`id`);
ALTER TABLE `ordenes_presupuesto` ADD CONSTRAINT `ordenes_presupuesto_orden_id_1ac02a27_fk_ordenes_ordentrabajo_id` FOREIGN KEY (`orden_id`) REFERENCES `ordenes_ordentrabajo` (`id`);
ALTER TABLE `ordenes_reparacion` ADD CONSTRAINT `ordenes_reparacion_orden_id_e1e7a810_fk_ordenes_ordentrabajo_id` FOREIGN KEY (`orden_id`) REFERENCES `ordenes_ordentrabajo` (`id`);
ALTER TABLE `ordenes_reparacion` ADD CONSTRAINT `ordenes_reparacion_tecnico_id_8d1de935_fk_auth_user_id` FOREIGN KEY (`tecnico_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `ordenes_detallerepuesto` ADD CONSTRAINT `ordenes_detallerepue_repuesto_id_8a754b75_fk_inventari` FOREIGN KEY (`repuesto_id`) REFERENCES `inventario_repuesto` (`id`);
ALTER TABLE `ordenes_detallerepuesto` ADD CONSTRAINT `ordenes_detallerepue_reparacion_id_2bdac56a_fk_ordenes_r` FOREIGN KEY (`reparacion_id`) REFERENCES `ordenes_reparacion` (`id`);

-- ---- Migración sessions.0001_initial ----
--
-- Create model Session
--
CREATE TABLE `django_session` (`session_key` varchar(40) NOT NULL PRIMARY KEY, `session_data` longtext NOT NULL, `expire_date` datetime(6) NOT NULL);
CREATE INDEX `django_session_expire_date_a5c62663` ON `django_session` (`expire_date`);

-- Tabla de control de migraciones de Django
CREATE TABLE IF NOT EXISTS `django_migrations` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `app` varchar(255) NOT NULL, `name` varchar(255) NOT NULL, `applied` datetime(6) NOT NULL);

