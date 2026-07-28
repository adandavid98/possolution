import os
import sqlite3
import pyodbc
from config import Config

DB_FILE = os.path.join(os.path.dirname(__file__), "POS_LaRuta_DB.db")

_INSTALLED_DRIVER = None
_CACHED_CONN_STR = None
_SCHEMA_INITIALIZED = False

def get_installed_driver():
    """Finds the first available SQL Server ODBC driver on the system (cached)."""
    global _INSTALLED_DRIVER
    if _INSTALLED_DRIVER:
        return _INSTALLED_DRIVER
    try:
        available_drivers = pyodbc.drivers()
        for driver in Config.PREFERRED_DRIVERS:
            if driver in available_drivers:
                _INSTALLED_DRIVER = driver
                return _INSTALLED_DRIVER
    except Exception:
        pass
    _INSTALLED_DRIVER = "SQL Server"
    return _INSTALLED_DRIVER

def check_sql_server(force_recheck=False):
    """Checks if Microsoft SQL Server POS_LaRuta_DB is available, auto-creating it if missing."""
    global _CACHED_CONN_STR, _SCHEMA_INITIALIZED
    if _CACHED_CONN_STR and not force_recheck:
        return True, _CACHED_CONN_STR

    try:
        driver = get_installed_driver()
        if Config.DB_USER and Config.DB_PASSWORD:
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={Config.DB_SERVER};"
                f"DATABASE={Config.DB_NAME};"
                f"UID={Config.DB_USER};"
                f"PWD={Config.DB_PASSWORD};"
                f"Encrypt=no;TrustServerCertificate=yes;"
            )
            master_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={Config.DB_SERVER};"
                f"DATABASE=master;"
                f"UID={Config.DB_USER};"
                f"PWD={Config.DB_PASSWORD};"
                f"Encrypt=no;TrustServerCertificate=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={Config.DB_SERVER};"
                f"DATABASE={Config.DB_NAME};"
                f"Trusted_Connection=yes;"
                f"Encrypt=no;TrustServerCertificate=yes;"
            )
            master_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={Config.DB_SERVER};"
                f"DATABASE=master;"
                f"Trusted_Connection=yes;"
                f"Encrypt=no;TrustServerCertificate=yes;"
            )
        
        # Try direct connection
        try:
            conn = pyodbc.connect(conn_str, timeout=3)
            if not _SCHEMA_INITIALIZED:
                init_sqlserver_schema(conn)
                _SCHEMA_INITIALIZED = True
            conn.close()
            _CACHED_CONN_STR = conn_str
            return True, conn_str
        except Exception:
            # If direct connection failed, try connecting to master to auto-create DB
            master_conn = pyodbc.connect(master_str, autocommit=True, timeout=3)
            m_cursor = master_conn.cursor()
            m_cursor.execute(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{Config.DB_NAME}') CREATE DATABASE {Config.DB_NAME};")
            m_cursor.close()
            master_conn.close()
            
            # Now test direct connection again
            conn = pyodbc.connect(conn_str, timeout=3)
            if not _SCHEMA_INITIALIZED:
                init_sqlserver_schema(conn)
                _SCHEMA_INITIALIZED = True
            conn.close()
            _CACHED_CONN_STR = conn_str
            return True, conn_str
    except Exception:
        _CACHED_CONN_STR = None
        return False, None

def init_sqlserver_schema(conn):
    """Ensures all required tables and columns exist in SQL Server POS_LaRuta_DB."""
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
        """,
        """
        IF OBJECT_ID('clientes', 'U') IS NULL
        CREATE TABLE clientes (
            id INT IDENTITY(1,1) PRIMARY KEY,
            codigo VARCHAR(30) UNIQUE NOT NULL,
            nombre_razon_social VARCHAR(150) NOT NULL,
            rnc_cedula VARCHAR(20) NULL,
            tipo_cliente VARCHAR(30) CHECK (tipo_cliente IN ('General', 'Wholesale/Mayorista', 'Vendedor/Suplidor')) DEFAULT 'General',
            telefono VARCHAR(30) NULL,
            email VARCHAR(100) NULL,
            direccion VARCHAR(255) NULL,
            porcentaje_descuento DECIMAL(5,2) DEFAULT 0,
            limite_credito DECIMAL(10,2) DEFAULT 0,
            activo BIT DEFAULT 1
        );
        """,
        """
        IF OBJECT_ID('permisos_usuario', 'U') IS NULL
        CREATE TABLE permisos_usuario (
            id INT IDENTITY(1,1) PRIMARY KEY,
            usuario_id INT FOREIGN KEY REFERENCES usuarios(id) ON DELETE CASCADE,
            modulo_clave VARCHAR(50) NOT NULL,
            permitido BIT DEFAULT 1
        );
        """,
        """
        IF OBJECT_ID('configuracion_empresa', 'U') IS NULL
        CREATE TABLE configuracion_empresa (
            id INT PRIMARY KEY DEFAULT 1,
            rnc VARCHAR(20) DEFAULT '101-00000-1',
            nombre_comercial VARCHAR(150) DEFAULT 'Minimarket La Ruta del Este',
            telefono VARCHAR(30) DEFAULT '(809) 555-0199',
            direccion VARCHAR(255) DEFAULT 'Av. Principal #45, La Altagracia',
            mensaje_factura VARCHAR(255) DEFAULT '¡Gracias por su compra! Vuelva pronto.'
        );
        """
    ]
    for stmt in statements:
        cursor.execute(stmt)

    cursor.execute("IF COL_LENGTH('detalle_ventas', 'precio_costo') IS NULL ALTER TABLE detalle_ventas ADD precio_costo DECIMAL(10,2) DEFAULT 0;")
    cursor.execute("IF COL_LENGTH('detalle_ventas', 'descuento') IS NULL ALTER TABLE detalle_ventas ADD descuento DECIMAL(10,2) DEFAULT 0;")
    cursor.execute("IF COL_LENGTH('productos', 'subdepartamento_id') IS NULL ALTER TABLE productos ADD subdepartamento_id INT NULL FOREIGN KEY REFERENCES subdepartamentos(id);")
    cursor.execute("IF COL_LENGTH('productos', 'es_descontable') IS NULL ALTER TABLE productos ADD es_descontable BIT DEFAULT 1;")
    cursor.execute("IF COL_LENGTH('productos', 'precio_manual') IS NULL ALTER TABLE productos ADD precio_manual BIT DEFAULT 0;")
    cursor.execute("IF COL_LENGTH('productos', 'unidad_medida') IS NULL ALTER TABLE productos ADD unidad_medida VARCHAR(20) DEFAULT 'UD';")
    cursor.execute("IF COL_LENGTH('productos', 'estado') IS NULL ALTER TABLE productos ADD estado VARCHAR(20) DEFAULT 'Activo';")

    # Migration for usuarios table: Drop old rol CHECK constraint, allow NULL password_hash, migrate legacy users
    try:
        cursor.execute("""
            DECLARE @chkName NVARCHAR(256);
            SELECT @chkName = name FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('usuarios');
            IF @chkName IS NOT NULL
            BEGIN
                EXEC('ALTER TABLE usuarios DROP CONSTRAINT ' + @chkName);
            END
        """)
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE usuarios ALTER COLUMN password_hash VARCHAR(255) NULL;")
    except Exception:
        pass

    try:
        cursor.execute("UPDATE usuarios SET username = '100001', password_hash = '100001', rol = 'Programador', nombre_completo = 'Adan Ozoria (Programador/Admin)' WHERE username = 'admin';")
        cursor.execute("UPDATE usuarios SET username = '200001', password_hash = '200001', rol = 'Cajero', nombre_completo = 'Cajero Principal (Cajero)' WHERE username = 'cajero1';")
        cursor.execute("UPDATE usuarios SET username = '300001', password_hash = '300001', rol = 'Almacen', nombre_completo = 'Encargado de Almacen (Almacen)' WHERE username = 'almacen1';")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM usuarios WHERE username = '100001')
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo) VALUES ('100001', '100001', 'Adan Ozoria (Programador/Admin)', 'Programador', 1);

            IF NOT EXISTS (SELECT * FROM usuarios WHERE username = '100002')
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo) VALUES ('100002', '100002', 'Don Henderson (Propietario)', 'Propietario', 1);

            IF NOT EXISTS (SELECT * FROM usuarios WHERE username = '200001')
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo) VALUES ('200001', '200001', 'Cajero Principal (Cajero)', 'Cajero', 1);

            IF NOT EXISTS (SELECT * FROM usuarios WHERE username = '300001')
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo) VALUES ('300001', '300001', 'Encargado de Almacen (Almacen)', 'Almacen', 1);
        """)
    except Exception as ex_u:
        print("Migración usuarios info:", ex_u)

    conn.commit()
    cursor.close()

def init_sqlite_schema(conn):
    """Ensures all tables and indexes exist in SQLite database."""
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre_completo TEXT NOT NULL,
        rol TEXT NOT NULL CHECK (rol IN ('Admin', 'Cajero', 'Almacen')),
        activo INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS departamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS subdepartamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departamento_id INTEGER REFERENCES departamentos(id),
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        categoria_id INTEGER REFERENCES categorias(id),
        subdepartamento_id INTEGER REFERENCES subdepartamentos(id),
        precio_costo REAL NOT NULL,
        precio_venta REAL NOT NULL,
        stock_actual INTEGER DEFAULT 0,
        stock_minimo INTEGER DEFAULT 5,
        fecha_vencimiento TEXT NULL
    );

    CREATE TABLE IF NOT EXISTS cajas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER REFERENCES usuarios(id),
        monto_inicial REAL NOT NULL,
        monto_final_teorico REAL NULL,
        monto_final_real REAL NULL,
        fecha_apertura TEXT DEFAULT (datetime('now', 'localtime')),
        fecha_cierre TEXT NULL,
        estado TEXT DEFAULT 'Abierta' CHECK (estado IN ('Abierta', 'Cerrada'))
    );

    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_factura TEXT UNIQUE NOT NULL,
        caja_id INTEGER REFERENCES cajas(id),
        usuario_id INTEGER REFERENCES usuarios(id),
        cliente_nombre TEXT DEFAULT 'Cliente General',
        tipo_pago TEXT NOT NULL CHECK (tipo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia/WhatsApp')),
        subtotal REAL NOT NULL,
        itbis_impuesto REAL NOT NULL,
        total REAL NOT NULL,
        fecha TEXT DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER REFERENCES ventas(id),
        producto_id INTEGER REFERENCES productos(id),
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        precio_costo REAL DEFAULT 0,
        descuento REAL DEFAULT 0,
        subtotal REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS movimientos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER REFERENCES productos(id),
        tipo_movimiento TEXT NOT NULL CHECK (tipo_movimiento IN ('Entrada Suplidor', 'Salida/Ajuste', 'Mermas/Vencido')),
        cantidad INTEGER NOT NULL,
        motivo TEXT,
        usuario_id INTEGER REFERENCES usuarios(id),
        fecha TEXT DEFAULT (datetime('now', 'localtime'))
    );
    """)

    # Auto-migrate: add subdepartamento_id to productos if missing
    cursor.execute("PRAGMA table_info(productos)")
    prod_cols = [col[1] for col in cursor.fetchall()]
    if "subdepartamento_id" not in prod_cols:
        cursor.execute("ALTER TABLE productos ADD COLUMN subdepartamento_id INTEGER REFERENCES subdepartamentos(id)")

    # Auto-migrate: add precio_costo and descuento to detalle_ventas if missing
    cursor.execute("PRAGMA table_info(detalle_ventas)")
    dv_cols = [col[1] for col in cursor.fetchall()]
    if "precio_costo" not in dv_cols:
        cursor.execute("ALTER TABLE detalle_ventas ADD COLUMN precio_costo REAL DEFAULT 0")
    if "descuento" not in dv_cols:
        cursor.execute("ALTER TABLE detalle_ventas ADD COLUMN descuento REAL DEFAULT 0")

    conn.commit()

def get_connection():
    """Establishes and returns a SQL Server connection. Raises RuntimeError if unavailable."""
    is_sql, conn_str = check_sql_server()
    if is_sql:
        conn = pyodbc.connect(conn_str)
        return conn, "sqlserver"
    else:
        raise RuntimeError(
            "No se pudo conectar a SQL Server.\n"
            "Verifique que el servicio SQL Server esté activo\n"
            f"y que el servidor '{Config.DB_SERVER}' sea accesible.\n"
            f"Base de datos requerida: '{Config.DB_NAME}'"
        )

def get_active_db_type():
    is_sql, _ = check_sql_server()
    return "SQL Server" if is_sql else "Desconectado"

def check_db_status():
    """Returns (connected: bool, detail_str: str) for the SQL Server connection."""
    is_sql, conn_str = check_sql_server()
    if is_sql:
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            ver = cursor.fetchone()[0]
            conn.close()
            short_ver = ver.split("\n")[0].strip() if ver else "SQL Server"
            return True, short_ver
        except Exception as e:
            return False, str(e)
    return False, f"Servidor '{Config.DB_SERVER}' / BD '{Config.DB_NAME}' no accesible"

def execute_query(sql, params=(), fetch_one=False, fetch_all=False, commit=False):
    """
    Executes a SQL statement against SQL Server via pyodbc.
    Returns list of dicts for SELECT, affected count for DML, or single dict for fetch_one.
    Raises RuntimeError if SQL Server is not available.
    """
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)

        result = None
        if fetch_one:
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, row))
        elif fetch_all:
            rows = cursor.fetchall()
            if rows:
                columns = [column[0] for column in cursor.description]
                result = [dict(zip(columns, r)) for r in rows]
            else:
                result = []
        elif commit:
            conn.commit()
            result = cursor.rowcount

        return result
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def test_db_connection():
    """Tests SQL Server connection and returns version string."""
    try:
        conn, _ = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION AS version")
        row = cursor.fetchone()
        version_str = f"SQL Server: {row[0]}"
        conn.close()
        return True, version_str
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, info = test_db_connection()
    if success:
        print("Conexión exitosa a SQL Server!")
        print("Detalle:", info)
    else:
        print("Error al conectar:", info)

def backup_database_sqlserver(destination_path):
    """Generates a native SQL Server database backup (.bak) to destination_path."""
    driver = get_installed_driver()
    if Config.DB_USER and Config.DB_PASSWORD:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"UID={Config.DB_USER};"
            f"PWD={Config.DB_PASSWORD};"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    else:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    
    conn = pyodbc.connect(master_str, autocommit=True)
    cursor = conn.cursor()
    try:
        clean_path = destination_path.replace("'", "''")
        db_name = Config.DB_NAME
        sql = f"BACKUP DATABASE [{db_name}] TO DISK = '{clean_path}' WITH FORMAT, INIT, NAME = 'POS_LaRuta_DB-Full Backup';"
        cursor.execute(sql)
        return True, "Respaldo generado con éxito."
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def restore_database_sqlserver(backup_path):
    """Restores SQL Server POS_LaRuta_DB from a .bak file."""
    driver = get_installed_driver()
    if Config.DB_USER and Config.DB_PASSWORD:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"UID={Config.DB_USER};"
            f"PWD={Config.DB_PASSWORD};"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    else:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )

    conn = pyodbc.connect(master_str, autocommit=True)
    cursor = conn.cursor()
    try:
        clean_path = backup_path.replace("'", "''")
        db_name = Config.DB_NAME
        
        # Set DB to single user to terminate active connections
        cursor.execute(f"IF EXISTS (SELECT * FROM sys.databases WHERE name = '{db_name}') ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;")
        
        # Restore database
        cursor.execute(f"RESTORE DATABASE [{db_name}] FROM DISK = '{clean_path}' WITH REPLACE;")
        
        # Set DB back to multi user
        cursor.execute(f"ALTER DATABASE [{db_name}] SET MULTI_USER;")
        
        return True, "Base de datos restaurada con éxito."
    except Exception as e:
        try:
            cursor.execute(f"ALTER DATABASE [{Config.DB_NAME}] SET MULTI_USER;")
        except Exception:
            pass
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
