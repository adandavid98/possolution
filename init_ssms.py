import pyodbc
from config import Config

def init_sqlserver_schema(conn):
    """Ensures all required tables exist in SQL Server POS_LaRuta_DB."""
    cursor = conn.cursor()
    statements = [
        """
        IF OBJECT_ID('usuarios', 'U') IS NULL
        CREATE TABLE usuarios (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            rol VARCHAR(20) CHECK (rol IN ('Admin', 'Cajero', 'Almacen')) NOT NULL,
            activo BIT DEFAULT 1
        );
        """,
        """
        IF OBJECT_ID('departamentos', 'U') IS NULL
        CREATE TABLE departamentos (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            descripcion VARCHAR(255)
        );
        """,
        """
        IF OBJECT_ID('subdepartamentos', 'U') IS NULL
        CREATE TABLE subdepartamentos (
            id INT IDENTITY(1,1) PRIMARY KEY,
            departamento_id INT FOREIGN KEY REFERENCES departamentos(id),
            nombre VARCHAR(50) UNIQUE NOT NULL,
            descripcion VARCHAR(255)
        );
        """,
        """
        IF OBJECT_ID('categorias', 'U') IS NULL
        CREATE TABLE categorias (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            descripcion VARCHAR(255)
        );
        """,
        """
        IF OBJECT_ID('productos', 'U') IS NULL
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
        """,
        """
        IF OBJECT_ID('cajas', 'U') IS NULL
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
        """,
        """
        IF OBJECT_ID('ventas', 'U') IS NULL
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
        """,
        """
        IF OBJECT_ID('detalle_ventas', 'U') IS NULL
        CREATE TABLE detalle_ventas (
            id INT IDENTITY(1,1) PRIMARY KEY,
            venta_id INT FOREIGN KEY REFERENCES ventas(id),
            producto_id INT FOREIGN KEY REFERENCES productos(id),
            cantidad INT NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            precio_costo DECIMAL(10,2) DEFAULT 0,
            descuento DECIMAL(10,2) DEFAULT 0,
            subtotal DECIMAL(10,2) NOT NULL
        );
        """,
        """
        IF OBJECT_ID('movimientos_inventario', 'U') IS NULL
        CREATE TABLE movimientos_inventario (
            id INT IDENTITY(1,1) PRIMARY KEY,
            producto_id INT FOREIGN KEY REFERENCES productos(id),
            tipo_movimiento VARCHAR(30) CHECK (tipo_movimiento IN ('Entrada Suplidor', 'Salida/Ajuste', 'Mermas/Vencido')) NOT NULL,
            cantidad INT NOT NULL,
            motivo VARCHAR(255),
            usuario_id INT FOREIGN KEY REFERENCES usuarios(id),
            fecha DATETIME DEFAULT GETDATE()
        );
        """
    ]
    for stmt in statements:
        cursor.execute(stmt)

    # Migrations for existing tables if needed
    cursor.execute("IF COL_LENGTH('detalle_ventas', 'precio_costo') IS NULL ALTER TABLE detalle_ventas ADD precio_costo DECIMAL(10,2) DEFAULT 0;")
    cursor.execute("IF COL_LENGTH('detalle_ventas', 'descuento') IS NULL ALTER TABLE detalle_ventas ADD descuento DECIMAL(10,2) DEFAULT 0;")
    cursor.execute("IF COL_LENGTH('productos', 'subdepartamento_id') IS NULL ALTER TABLE productos ADD subdepartamento_id INT NULL FOREIGN KEY REFERENCES subdepartamentos(id);")
    conn.commit()
    cursor.close()

if __name__ == "__main__":
    driver = "ODBC Driver 17 for SQL Server"
    server = Config.DB_SERVER
    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={Config.DB_NAME};Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes;"
    conn = pyodbc.connect(conn_str)
    init_sqlserver_schema(conn)
    conn.close()
    print("Schema initialized successfully!")
