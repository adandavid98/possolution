from database import execute_query

def verify_and_seed_data():
    """Verifies that initial categories, users, and products exist in POS_LaRuta_DB."""
    try:
        # Check users count
        users = execute_query("SELECT COUNT(*) AS total FROM usuarios", fetch_one=True)
        categories = execute_query("SELECT COUNT(*) AS total FROM categorias", fetch_one=True)
        products = execute_query("SELECT COUNT(*) AS total FROM productos", fetch_one=True)

        print(f"Estado BD SQL Server (POS_LaRuta_DB):")
        print(f" - Usuarios: {users['total']}")
        print(f" - Categorías: {categories['total']}")
        print(f" - Productos: {products['total']}")

        if products['total'] == 0:
            print("Poblando categorías y productos iniciales...")
            # Categories
            execute_query("""
                INSERT INTO categorias (nombre, descripcion) VALUES
                ('Bebidas', 'Refrescos, jugos, aguas y energizantes'),
                ('Lácteos y Huevos', 'Leche, quesos, yogures y huevos'),
                ('Abarrotes', 'Arroz, habichuelas, aceite, enlatados'),
                ('Higiene y Limpieza', 'Jabones, detergentes, papel higiénico'),
                ('Snacks y Dulces', 'Galletas, papitas, chocolates');
            """, commit=True)

            # Users
            execute_query("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, rol) VALUES
                ('admin', 'admin123', 'Administrador General', 'Admin'),
                ('cajero1', 'caja123', 'Adan Ozoria (Cajero)', 'Cajero'),
                ('almacen1', 'almacen123', 'Henderson Branagan (Almacen)', 'Almacen');
            """, commit=True)

            # Products
            execute_query("""
                INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_costo, precio_venta, stock_actual, stock_minimo) VALUES
                ('750100000001', 'Arroz Selecto 5 lbs', 3, 180.00, 225.00, 45, 10),
                ('750100000002', 'Habichuelas Rojas 1 lb', 3, 45.00, 60.00, 30, 8),
                ('750100000003', 'Aceite Vegetal 16 oz', 3, 85.00, 110.00, 20, 5),
                ('750100000004', 'Refresco Coca Cola 2L', 1, 90.00, 120.00, 15, 6),
                ('750100000005', 'Agua Purificada 600ml', 1, 15.00, 25.00, 100, 20),
                ('750100000006', 'Leche Entera 1 Litro', 2, 65.00, 85.00, 4, 10),
                ('750100000007', 'Queso Cheddar 1 lb', 2, 210.00, 275.00, 8, 5),
                ('750100000008', 'Detergente Polvo 500g', 4, 55.00, 75.00, 2, 8),
                ('750100000009', 'Papel Higiénico 4 Pack', 4, 80.00, 110.00, 25, 5),
                ('750100000010', 'Galletas Soda Pack', 5, 40.00, 60.00, 50, 12);
            """, commit=True)
            print("Datos iniciales insertados correctamente en SQL Server.")

    except Exception as e:
        print("Error al verificar/poblar la base de datos:", e)

if __name__ == "__main__":
    verify_and_seed_data()
