from database import get_connection, get_active_db_type
conn, _ = get_connection()
cursor = conn.cursor()
print("DB type:", get_active_db_type())

# Check if precio_costo column exists in detalle_ventas
cursor.execute("PRAGMA table_info(detalle_ventas)")
cols = [c[1] for c in cursor.fetchall()]
print("detalle_ventas columns:", cols)

if "precio_costo" not in cols:
    print("Adding precio_costo column to detalle_ventas...")
    cursor.execute("ALTER TABLE detalle_ventas ADD COLUMN precio_costo REAL DEFAULT 0")
    conn.commit()
    print("Column added successfully.")
else:
    print("precio_costo already exists.")

# Check descuento column
cursor.execute("PRAGMA table_info(detalle_ventas)")
cols = [c[1] for c in cursor.fetchall()]
if "descuento" not in cols:
    print("Adding descuento column to detalle_ventas...")
    cursor.execute("ALTER TABLE detalle_ventas ADD COLUMN descuento REAL DEFAULT 0")
    conn.commit()
    print("descuento column added.")

cursor.execute("PRAGMA table_info(detalle_ventas)")
print("Final detalle_ventas schema:", [(c[1], c[2]) for c in cursor.fetchall()])

cursor.close()
conn.close()
