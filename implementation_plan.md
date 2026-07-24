# Plan de Implementación: Sistema POS & Control de Inventarios (SQL Server / SSMS)
**Caso Ficticio**: Minimarket La Ruta del Este, S.R.L. (Santo Domingo Este, R.D.)  
**Asignatura**: Proyecto Integrador I (INF-225-002) - UTESA  
**Tecnología**: Python 3 + CustomTkinter (GUI Moderna) + Microsoft SQL Server (SSMS via `pyodbc`)  
**Ubicación del Proyecto**: `C:\Users\Luis\Documents\Anti-POS_Project`

---

## 📌 1. Resumen del Proyecto y Contexto del Cliente

El **Minimarket La Ruta del Este, S.R.L.** es un comercio minorista de consumo diario (620 productos activos, ~85 ventas diarias, 12 empleados). Actialmente opera con registros manuales (libretas y Excel), lo cual provoca:
- **14% de descuadre** entre inventario físico y registros.
- **RD$18,700/mes** en pérdidas por productos vencidos, ventas no concretadas y compras urgentes.
- **Demoras y cancelaciones** en pedidos solicitados por WhatsApp (9 de 65 pedidos cancelados por no saber si hay stock).
- **Más de 2 horas diarias** desperdiciadas verificando mercancía físicamente.

### Objetivo de la Solución
Desarrollar un sistema de Punto de Venta (POS) y Gestión de Inventarios ágil, conectable a **SQL Server / SSMS**, enfocado en:
1. Actualización en **tiempo real** del inventario tras cada venta o entrada mediante procedimientos almacenados o transacciones en SQL Server.
2. **Alertas automáticas de stock mínimo** para evitar agotados sin aviso.
3. Módulo rápido de **Atención a Pedidos WhatsApp** (consulta de stock al instante).
4. **Reportes operativos** de ventas diarias, cierres de caja y mercancía más vendida.

---

## 🏗️ 2. Arquitectura del Sistema

- **Lenguaje**: Python 3.x
- **Interfaz Gráfica (GUI)**: `CustomTkinter` (Diseño moderno estilo Dark/Light Mode, responsivo y ultra rápido).
- **Base de Datos**: `Microsoft SQL Server` (Base de datos: `POS_LaRuta_DB`).
- **Conector DB**: `pyodbc` / `SQLAlchemy` utilizando el driver `ODBC Driver 17 for SQL Server` o `MSOLEDBSQL`.
- **Script de Estructura**: Archivo `.sql` ejecutable desde **SSMS (SQL Server Management Studio)**.

---

## 🗄️ 3. Modelo de Base de Datos (SQL Server T-SQL)

```sql
-- Crear Base de Datos en SSMS
CREATE DATABASE POS_LaRuta_DB;
GO

USE POS_LaRuta_DB;
GO

-- Tabla: Usuarios y Roles
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    rol VARCHAR(20) CHECK (rol IN ('Admin', 'Cajero', 'Almacen')) NOT NULL,
    activo BIT DEFAULT 1
);

-- Tabla: Categorías de Productos
CREATE TABLE categorias (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255)
);

-- Tabla: Catálogo de Productos
CREATE TABLE productos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo_barras VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    categoria_id INT FOREIGN KEY REFERENCES categorias(id),
    precio_costo DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    fecha_vencimiento DATE NULL
);

-- Tabla: Sesiones de Caja (Apertura y Cierre)
CREATE TABLE cajas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT FOREIGN KEY REFERENCES usuarios(id),
    monto_inicial DECIMAL(10,2) NOT NULL,
    monto_final_teorico DECIMAL(10,2) NULL,
    monto_final_real DECIMAL(10,2) NULL,
    fecha_apertura DATETIME DEFAULT GETDATE(),
    fecha_cierre DATETIME NULL,
    estado VARCHAR(20) CHECK (estado IN ('Abierta', 'Cerrada')) DEFAULT 'Abierta'
);

-- Tabla: Encabezado de Ventas
CREATE TABLE ventas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo_factura VARCHAR(50) UNIQUE NOT NULL,
    caja_id INT FOREIGN KEY REFERENCES cajas(id),
    usuario_id INT FOREIGN KEY REFERENCES usuarios(id),
    cliente_nombre VARCHAR(100) DEFAULT 'Cliente General',
    tipo_pago VARCHAR(30) CHECK (tipo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia/WhatsApp')) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    itbis_impuesto DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT GETDATE()
);

-- Tabla: Detalle de Ventas
CREATE TABLE detalle_ventas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    venta_id INT FOREIGN KEY REFERENCES ventas(id),
    producto_id INT FOREIGN KEY REFERENCES productos(id),
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- Tabla: Movimientos de Inventario (Entradas/Salidas/Ajustes)
CREATE TABLE movimientos_inventario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    producto_id INT FOREIGN KEY REFERENCES productos(id),
    tipo_movimiento VARCHAR(30) CHECK (tipo_movimiento IN ('Entrada Suplidor', 'Salida/Ajuste', 'Mermas/Vencido')) NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(255),
    usuario_id INT FOREIGN KEY REFERENCES usuarios(id),
    fecha DATETIME DEFAULT GETDATE()
);
GO
```

---

## 🎨 4. Módulos y Pantallas de la Aplicación

1. **Configuración de Conexión a SQL Server**
   - Modal o archivo `.env` / `config.json` para configurar Servidor (ej. `localhost` o `localhost\SQLEXPRESS`), Nombre de BD, Usuario y Contraseña (o Autenticación de Windows).

2. **Pantalla de Autenticación (Login)**
   - Validación de credenciales contra la tabla `usuarios` en SQL Server.

3. **Dashboard Principal (Navegación Moderna)**
   - Sidebar con pestañas: POS/Caja, Inventario, Entradas/Salidas, Pedidos WhatsApp, Reportes, Usuarios.

4. **Módulo Punto de Venta (POS / Caja)**
   - Búsqueda en tiempo real por scanner de código de barras o nombre.
   - Carrito de compras, cálculo de cambio (devuelta en RD$) e impresión de ticket.
   - **Descuento de stock en SQL Server mediante transacción segura**.

5. **Módulo de Inventario & Alertas**
   - Indicadores visuales de color (Stock bajo / Agotado / Normal).
   - Gestión CRUD de productos.

6. **Módulo de Reportes Operativos**
   - Consultas SQL eficientes para total de ventas, cierres de caja y productos más vendidos.

---

## 📋 5. Plan de Ejecución Fase a Fase

- [x] **Fase 1**: Análisis de Requisitos y Ajuste de Arquitectura a SQL Server (Completado).
- [ ] **Fase 2**: Generación del Script `.sql` completo para ejecutar en **SSMS**.
- [ ] **Fase 3**: Conexión de Python a SQL Server usando `pyodbc` con soporte para Autenticación de Windows o SQL Authentication.
- [ ] **Fase 4**: Desarrollo del Backend (Controlador DB, Auth, Ventas, Stock).
- [ ] **Fase 5**: Interfaz Gráfica con `CustomTkinter`.
- [ ] **Fase 6**: Pruebas de integración entre Python y SSMS.

---

## 🧪 Plan de Verificación y Pruebas

- **Prueba de Conexión SSMS**: Verificar que Python establezca comunicación exitosa con la instancia de SQL Server.
- **Prueba de Transacciones de Venta**: Comprobar que al registrar una venta en Python, los cambios se reflejen de forma consistente en las tablas `ventas`, `detalle_ventas` y `productos` en SQL Server.
- **Prueba de Alertas de Stock**: Ejecutar consultas en SSMS y verificar que la interfaz responda marcando los productos por debajo del stock mínimo.
