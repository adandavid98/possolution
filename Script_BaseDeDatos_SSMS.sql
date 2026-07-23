-- ===================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS Y TABLAS EN SQL SERVER (SSMS)
-- Proyecto Integrador I: Minimarket La Ruta del Este, S.R.L.
-- Estructura: Departamento -> Sub-departamento -> Artículos
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

-- 2. TABLA DEPARTAMENTOS
IF OBJECT_ID('departamentos', 'U') IS NOT NULL DROP TABLE departamentos;
CREATE TABLE departamentos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255)
);

-- 3. TABLA SUBDEPARTAMENTOS
IF OBJECT_ID('subdepartamentos', 'U') IS NOT NULL DROP TABLE subdepartamentos;
CREATE TABLE subdepartamentos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    departamento_id INT FOREIGN KEY REFERENCES departamentos(id),
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255)
);

-- 4. TABLA CATEGORIAS (Mantenida por compatibilidad)
IF OBJECT_ID('categorias', 'U') IS NOT NULL DROP TABLE categorias;
CREATE TABLE categorias (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255)
);

-- 5. TABLA PRODUCTOS
IF OBJECT_ID('productos', 'U') IS NOT NULL DROP TABLE productos;
CREATE TABLE productos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo_barras VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    categoria_id INT NULL FOREIGN KEY REFERENCES categorias(id),
    subdepartamento_id INT NULL FOREIGN KEY REFERENCES subdepartamentos(id),
    precio_costo DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    fecha_vencimiento DATE NULL
);

-- 6. TABLA CAJAS (Apertura y Cierre)
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

-- 7. TABLA VENTAS
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

-- 8. TABLA DETALLE_VENTAS
IF OBJECT_ID('detalle_ventas', 'U') IS NOT NULL DROP TABLE detalle_ventas;
CREATE TABLE detalle_ventas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    venta_id INT FOREIGN KEY REFERENCES ventas(id),
    producto_id INT FOREIGN KEY REFERENCES productos(id),
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- 9. TABLA MOVIMIENTOS_INVENTARIO
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
-- DATOS SEMILLA (DEPARTAMENTOS, SUBDEPARTAMENTOS Y ARTÍCULOS)
-- ===================================================================

INSERT INTO usuarios (username, password_hash, nombre_completo, rol) VALUES
('admin', 'admin123', 'Administrador General', 'Admin'),
('cajero1', 'caja123', 'Adan Ozoria (Cajero)', 'Cajero'),
('almacen1', 'almacen123', 'Henderson Branagan (Almacen)', 'Almacen');

INSERT INTO departamentos (nombre, descripcion) VALUES
('Comestibles (Grocery)', 'Víveres, granos, enlatados y condimentos'),
('Bebidas y Licores', 'Refrescos, jugos, aguas y bebidas alcohólicas'),
('Lácteos y Frescos', 'Leche, quesos, embutidos y carnes'),
('Limpieza e Higiene', 'Detergentes, jabones y cuidado personal'),
('Snacks y Dulces', 'Galletas, chocolates, frituras y confitería');

-- Sub-departamentos (Asignados a su Departamento)
INSERT INTO subdepartamentos (departamento_id, nombre, descripcion) VALUES
(1, 'Granos y Cereales', 'Arroz, habichuelas, avena y cereales'),
(1, 'Aceites y Condimentos', 'Aceites, sopitas, sal y vinagres'),
(1, 'Enlatados y Salsas', 'Salsa de tomate, maíz, atún y sardinas'),
(1, 'Pastas y Harinas', 'Espaguetis, harina de trigo y maíz'),

(2, 'Refrescos y Malta', 'Gaseosas y maltas embotelladas/latas'),
(2, 'Jugos y Agua Purificada', 'Jugos en caja, concentrados y botellas de agua'),
(2, 'Cervezas y Licores', 'Cervezas nacionales e importadas, rones'),

(3, 'Leche y Yogur', 'Leche en polvo, líquida y yogures'),
(3, 'Quesos y Mantequillas', 'Queso cheddar, blanco, danés y mantequilla'),
(3, 'Embutidos y Carnes', 'Salami, jamón, salchichas y carnes envasadas'),

(4, 'Detergentes y Lavaplatos', 'Detergente en polvo, cloro, lavaplatos'),
(4, 'Cuidado Personal y Papel', 'Papel higiénico, jabón de baño, pasta dental'),

(5, 'Galletas y Frituras', 'Galletas dulces, de soda, papitas y platanitos'),
(5, 'Chocolates y Dulces', 'Chocolates, mentas y golosinas');

-- Artículos Esenciales de Supermercado (+35 productos)
INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo) VALUES
-- Granos y Cereales
('750100000001', 'Arroz Selecto 5 lbs', 1, 180.00, 225.00, 45, 10),
('750100000002', 'Habichuelas Rojas 1 lb', 1, 45.00, 60.00, 30, 8),
('750100000011', 'Habichuelas Negras 1 lb', 1, 48.00, 65.00, 25, 8),
('750100000012', 'Avena Entera 400g', 1, 60.00, 80.00, 35, 10),

-- Aceites y Condimentos
('750100000003', 'Aceite Vegetal 16 oz', 2, 85.00, 110.00, 20, 5),
('750100000013', 'Aceite de Oliva 250ml', 2, 190.00, 245.00, 12, 4),
('750100000014', 'Sazonador Completo 200g', 2, 35.00, 50.00, 40, 10),
('750100000015', 'Sopita de Pollo (Caja 12 ud)', 2, 70.00, 95.00, 50, 15),

-- Enlatados y Salsas
('750100000016', 'Salsa de Tomate 220g', 3, 28.00, 40.00, 60, 15),
('750100000017', 'Atún en Agua 170g', 3, 65.00, 85.00, 35, 10),
('750100000018', 'Maíz Dulce Lata 400g', 3, 50.00, 70.00, 28, 8),

-- Pastas y Harinas
('750100000019', 'Espaguetis 400g', 4, 32.00, 45.00, 80, 20),
('750100000020', 'Harina de Maíz 1 lb', 4, 30.00, 42.00, 30, 8),
('750100000021', 'Harina de Trigo 1 lb', 4, 35.00, 50.00, 25, 8),

-- Refrescos y Malta
('750100000004', 'Refresco Coca Cola 2L', 5, 90.00, 120.00, 15, 6),
('750100000022', 'Refresco Country Club 2L', 5, 75.00, 100.00, 22, 8),
('750100000023', 'Malta India 7 oz (Pack 6)', 5, 180.00, 230.00, 14, 5),

-- Jugos y Agua
('750100000005', 'Agua Purificada 600ml', 6, 15.00, 25.00, 100, 20),
('750100000024', 'Jugo de Naranja 1 Litro', 6, 85.00, 115.00, 18, 6),
('750100000025', 'Agua Botellón 5 Galones', 6, 60.00, 90.00, 40, 10),

-- Cervezas y Licores
('750100000026', 'Cerveza Presidente 650ml', 7, 130.00, 165.00, 36, 12),
('750100000027', 'Ron Añejo 750ml', 7, 450.00, 560.00, 10, 4),

-- Leche y Yogur
('750100000006', 'Leche Entera 1 Litro', 8, 65.00, 85.00, 4, 10),
('750100000028', 'Leche Evaporada 315g', 8, 52.00, 70.00, 45, 12),
('750100000029', 'Yogur de Fresa 200g', 8, 40.00, 55.00, 16, 6),

-- Quesos y Mantequillas
('750100000007', 'Queso Cheddar 1 lb', 9, 210.00, 275.00, 8, 5),
('750100000030', 'Mantequilla con Sal 200g', 9, 95.00, 125.00, 15, 5),

-- Embutidos y Carnes
('750100000031', 'Salami Súper Especial 1 lb', 10, 140.00, 185.00, 20, 6),
('750100000032', 'Jamón de Pavo 1 lb', 10, 220.00, 290.00, 12, 4),
('750100000033', 'Salchichas de Pollo Pack', 10, 80.00, 110.00, 18, 5),

-- Detergentes y Lavaplatos
('750100000008', 'Detergente Polvo 500g', 11, 55.00, 75.00, 2, 8),
('750100000034', 'Cloro Blanqueador 1L', 11, 40.00, 60.00, 30, 10),
('750100000035', 'Lavaplatos Líquido 500ml', 11, 75.00, 100.00, 22, 6),

-- Cuidado Personal y Papel
('750100000009', 'Papel Higiénico 4 Pack', 12, 80.00, 110.00, 25, 5),
('750100000036', 'Jabón de Baño 110g', 12, 35.00, 50.00, 50, 12),
('750100000037', 'Pasta Dental 100ml', 12, 70.00, 95.00, 28, 8),

-- Galletas y Frituras
('750100000010', 'Galletas Soda Pack', 13, 40.00, 60.00, 50, 12),
('750100000038', 'Platanitos Fritos 100g', 13, 25.00, 35.00, 40, 10),
('750100000039', 'Papitas Lay''s 80g', 13, 45.00, 65.00, 30, 8),

-- Chocolates y Dulces
('750100000040', 'Chocolate en Barra 100g', 14, 50.00, 70.00, 25, 6);

PRINT 'Base de datos POS_LaRuta_DB y tablas con departamentos/subdepartamentos creadas exitosamente.';
GO
