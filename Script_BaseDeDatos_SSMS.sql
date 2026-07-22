-- ===================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS Y TABLAS EN SQL SERVER (SSMS)
-- Proyecto Integrador I: Minimarket La Ruta del Este, S.R.L.
-- ===================================================================

USE master;
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'POS_LaRuta_DB')
BEGIN
    CREATE DATABASE POS_LaRuta_DB;
END
GO

USE POS_LaRuta_DB;
GO

-- 1. TABLA USUARIOS
IF OBJECT_ID('usuarios', 'U') IS NOT NULL DROP TABLE usuarios;
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    rol VARCHAR(20) CHECK (rol IN ('Admin', 'Cajero', 'Almacen')) NOT NULL,
    activo BIT DEFAULT 1
);

-- 2. TABLA CATEGORIAS
IF OBJECT_ID('categorias', 'U') IS NOT NULL DROP TABLE categorias;
CREATE TABLE categorias (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255)
);

-- 3. TABLA PRODUCTOS
IF OBJECT_ID('productos', 'U') IS NOT NULL DROP TABLE productos;
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

-- 4. TABLA CAJAS (Apertura y Cierre)
IF OBJECT_ID('cajas', 'U') IS NOT NULL DROP TABLE cajas;
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

-- 5. TABLA VENTAS
IF OBJECT_ID('ventas', 'U') IS NOT NULL DROP TABLE ventas;
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

-- 6. TABLA DETALLE_VENTAS
IF OBJECT_ID('detalle_ventas', 'U') IS NOT NULL DROP TABLE detalle_ventas;
CREATE TABLE detalle_ventas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    venta_id INT FOREIGN KEY REFERENCES ventas(id),
    producto_id INT FOREIGN KEY REFERENCES productos(id),
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- 7. TABLA MOVIMIENTOS_INVENTARIO
IF OBJECT_ID('movimientos_inventario', 'U') IS NOT NULL DROP TABLE movimientos_inventario;
CREATE TABLE movimientos_inventario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    producto_id INT FOREIGN KEY REFERENCES productos(id),
    tipo_movimiento VARCHAR(30) CHECK (tipo_movimiento IN ('Entrada Suplidor', 'Salida/Ajuste', 'Mermas/Vencido')) NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(255),
    usuario_id INT FOREIGN KEY REFERENCES usuarios(id),
    fecha DATETIME DEFAULT GETDATE()
);

-- ===================================================================
-- DATOS SEMILLA (CATEGORÍAS, USUARIOS Y PRODUCTOS SINTÉTICOS INITIALES)
-- ===================================================================

INSERT INTO usuarios (username, password_hash, nombre_completo, rol) VALUES
('admin', 'admin123', 'Administrador General', 'Admin'),
('cajero1', 'caja123', 'Adan Ozoria (Cajero)', 'Cajero'),
('almacen1', 'almacen123', 'Henderson Branagan (Almacen)', 'Almacen');

INSERT INTO categorias (nombre, descripcion) VALUES
('Bebidas', 'Refrescos, jugos, aguas y energizantes'),
('Lácteos y Huevos', 'Leche, quesos, yogures y huevos'),
('Abarrotes', 'Arroz, habichuelas, aceite, enlatados'),
('Higiene y Limpieza', 'Jabones, detergentes, papel higiénico'),
('Snacks y Dulces', 'Galletas, papitas, chocolates');

INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_costo, precio_venta, stock_actual, stock_minimo) VALUES
('750100000001', 'Arroz Selecto 5 lbs', 3, 180.00, 225.00, 45, 10),
('750100000002', 'Habichuelas Rojas 1 lb', 3, 45.00, 60.00, 30, 8),
('750100000003', 'Aceite Vegetal 16 oz', 3, 85.00, 110.00, 20, 5),
('750100000004', 'Refresco Coca Cola 2L', 1, 90.00, 120.00, 15, 6),
('750100000005', 'Agua Purificada 600ml', 1, 15.00, 25.00, 100, 20),
('750100000006', 'Leche Entera 1 Litro', 2, 65.00, 85.00, 4, 10), -- Alerta Stock Mínimo
('750100000007', 'Queso Cheddar 1 lb', 2, 210.00, 275.00, 8, 5),
('750100000008', 'Detergente Polvo 500g', 4, 55.00, 75.00, 2, 8), -- Alerta Stock Mínimo
('750100000009', 'Papel Higiénico 4 Pack', 4, 80.00, 110.00, 25, 5),
('750100000010', 'Galletas Soda Pack', 5, 40.00, 60.00, 50, 12);

PRINT 'Base de datos POS_LaRuta_DB y tablas creadas exitosamente.';
GO
