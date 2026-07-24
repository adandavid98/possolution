from database import execute_query

def verify_and_seed_data():
    """Verifies and seeds Departments, Sub-departments, Users, Categories, and +35 Products."""
    try:
        # Check users count
        users = execute_query("SELECT COUNT(*) AS total FROM usuarios", fetch_one=True)
        departments = execute_query("SELECT COUNT(*) AS total FROM departamentos", fetch_one=True)
        products = execute_query("SELECT COUNT(*) AS total FROM productos", fetch_one=True)

        print(f"Estado BD:")
        print(f" - Usuarios: {users['total']}")
        print(f" - Departamentos: {departments['total']}")
        print(f" - Productos: {products['total']}")

        # Clear existing seeded products if products count is small (to refresh schema & new 35+ products)
        if products['total'] < 30:
            print("Actualizando esquema y re-poblando departamentos, sub-departamentos y catálogo de supermercado (+35 ítems)...")
            
            # Reset tables
            execute_query("DELETE FROM productos;", commit=True)
            execute_query("DELETE FROM subdepartamentos;", commit=True)
            execute_query("DELETE FROM departamentos;", commit=True)
            execute_query("DELETE FROM categorias;", commit=True)

            # 1. Departments
            execute_query("""
                INSERT INTO departamentos (nombre, descripcion) VALUES
                ('Comestibles (Grocery)', 'Víveres, granos, enlatados y condimentos'),
                ('Bebidas y Licores', 'Refrescos, jugos, aguas y bebidas alcohólicas'),
                ('Lácteos y Frescos', 'Leche, quesos, embutidos y carnes'),
                ('Limpieza e Higiene', 'Detergentes, jabones y cuidado personal'),
                ('Snacks y Dulces', 'Galletas, chocolates, frituras y confitería');
            """, commit=True)

            # Also seed legacy categorias for compatibility
            execute_query("""
                INSERT INTO categorias (nombre, descripcion) VALUES
                ('Comestibles (Grocery)', 'Víveres, granos, enlatados'),
                ('Bebidas y Licores', 'Refrescos, jugos, bebidas'),
                ('Lácteos y Frescos', 'Leche, quesos, embutidos'),
                ('Limpieza e Higiene', 'Detergentes, jabones'),
                ('Snacks y Dulces', 'Galletas, chocolates');
            """, commit=True)

            # 2. Sub-departments
            execute_query("""
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
            """, commit=True)

            # 3. Users (if empty or using old schema)
            execute_query("DELETE FROM usuarios WHERE username IN ('admin', 'cajero1', 'almacen1');", commit=True)
            if users['total'] == 0 or True:
                try:
                    execute_query("""
                        INSERT INTO usuarios (username, password_hash, nombre_completo, rol) VALUES
                        ('100001', '100001', 'Adan Ozoria (Programador/Admin)', 'Programador'),
                        ('100002', '100002', 'Don Henderson (Propietario)', 'Propietario'),
                        ('200001', '200001', 'Cajero Principal (Cajero)', 'Cajero'),
                        ('300001', '300001', 'Encargado de Almacen (Almacen)', 'Almacen');
                    """, commit=True)
                except Exception as ex:
                    print("Usuarios ya existentes o notificado:", ex)

            # 4. Initial Customers & Company Data
            try:
                execute_query("""
                    IF NOT EXISTS (SELECT * FROM clientes WHERE codigo = 'CLI-0001')
                    INSERT INTO clientes (codigo, nombre_razon_social, rnc_cedula, tipo_cliente, porcentaje_descuento) VALUES
                    ('CLI-0001', 'Cliente General / Ocasional', '000-0000000-0', 'General', 0.0),
                    ('CLI-0002', 'Comercial El Almacén S.R.L.', '131-45678-9', 'Wholesale/Mayorista', 10.0),
                    ('CLI-0003', 'Distribuidora Corripio (Vendedor)', '101-01992-3', 'Vendedor/Suplidor', 0.0);
                """, commit=True)
            except Exception:
                pass

            try:
                execute_query("""
                    IF NOT EXISTS (SELECT * FROM configuracion_empresa WHERE id = 1)
                    INSERT INTO configuracion_empresa (id, rnc, nombre_comercial, telefono, direccion, mensaje_factura) VALUES
                    (1, '101-00000-1', 'Minimarket La Ruta del Este', '(809) 555-0199', 'Av. Principal #45, La Altagracia', '¡Gracias por su compra! Vuelva pronto.');
                """, commit=True)
            except Exception:
                pass

            # 4. Supermarket Items (+35 Items)
            execute_query("""
                INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo) VALUES
                ('750100000001', 'Arroz Selecto 5 lbs', 1, 180.00, 225.00, 45, 10),
                ('750100000002', 'Habichuelas Rojas 1 lb', 1, 45.00, 60.00, 30, 8),
                ('750100000011', 'Habichuelas Negras 1 lb', 1, 48.00, 65.00, 25, 8),
                ('750100000012', 'Avena Entera 400g', 1, 60.00, 80.00, 35, 10),

                ('750100000003', 'Aceite Vegetal 16 oz', 2, 85.00, 110.00, 20, 5),
                ('750100000013', 'Aceite de Oliva 250ml', 2, 190.00, 245.00, 12, 4),
                ('750100000014', 'Sazonador Completo 200g', 2, 35.00, 50.00, 40, 10),
                ('750100000015', 'Sopita de Pollo (Caja 12 ud)', 2, 70.00, 95.00, 50, 15),

                ('750100000016', 'Salsa de Tomate 220g', 3, 28.00, 40.00, 60, 15),
                ('750100000017', 'Atún en Agua 170g', 3, 65.00, 85.00, 35, 10),
                ('750100000018', 'Maíz Dulce Lata 400g', 3, 50.00, 70.00, 28, 8),

                ('750100000019', 'Espaguetis 400g', 4, 32.00, 45.00, 80, 20),
                ('750100000020', 'Harina de Maíz 1 lb', 4, 30.00, 42.00, 30, 8),
                ('750100000021', 'Harina de Trigo 1 lb', 4, 35.00, 50.00, 25, 8),

                ('750100000004', 'Refresco Coca Cola 2L', 5, 90.00, 120.00, 15, 6),
                ('750100000022', 'Refresco Country Club 2L', 5, 75.00, 100.00, 22, 8),
                ('750100000023', 'Malta India 7 oz (Pack 6)', 5, 180.00, 230.00, 14, 5),

                ('750100000005', 'Agua Purificada 600ml', 6, 15.00, 25.00, 100, 20),
                ('750100000024', 'Jugo de Naranja 1 Litro', 6, 85.00, 115.00, 18, 6),
                ('750100000025', 'Agua Botellón 5 Galones', 6, 60.00, 90.00, 40, 10),

                ('750100000026', 'Cerveza Presidente 650ml', 7, 130.00, 165.00, 36, 12),
                ('750100000027', 'Ron Añejo 750ml', 7, 450.00, 560.00, 10, 4),

                ('750100000006', 'Leche Entera 1 Litro', 8, 65.00, 85.00, 4, 10),
                ('750100000028', 'Leche Evaporada 315g', 8, 52.00, 70.00, 45, 12),
                ('750100000029', 'Yogur de Fresa 200g', 8, 40.00, 55.00, 16, 6),

                ('750100000007', 'Queso Cheddar 1 lb', 9, 210.00, 275.00, 8, 5),
                ('750100000030', 'Mantequilla con Sal 200g', 9, 95.00, 125.00, 15, 5),

                ('750100000031', 'Salami Súper Especial 1 lb', 10, 140.00, 185.00, 20, 6),
                ('750100000032', 'Jamón de Pavo 1 lb', 10, 220.00, 290.00, 12, 4),
                ('750100000033', 'Salchichas de Pollo Pack', 10, 80.00, 110.00, 18, 5),

                ('750100000008', 'Detergente Polvo 500g', 11, 55.00, 75.00, 2, 8),
                ('750100000034', 'Cloro Blanqueador 1L', 11, 40.00, 60.00, 30, 10),
                ('750100000035', 'Lavaplatos Líquido 500ml', 11, 75.00, 100.00, 22, 6),

                ('750100000009', 'Papel Higiénico 4 Pack', 12, 80.00, 110.00, 25, 5),
                ('750100000036', 'Jabón de Baño 110g', 12, 35.00, 50.00, 50, 12),
                ('750100000037', 'Pasta Dental 100ml', 12, 70.00, 95.00, 28, 8),

                ('750100000010', 'Galletas Soda Pack', 13, 40.00, 60.00, 50, 12),
                ('750100000038', 'Platanitos Fritos 100g', 13, 25.00, 35.00, 40, 10),
                ('750100000039', 'Papitas Lay''s 80g', 13, 45.00, 65.00, 30, 8),

                ('750100000040', 'Chocolate en Barra 100g', 14, 50.00, 70.00, 25, 6);
            """, commit=True)

            print("¡Datos iniciales de Departamentos, Sub-departamentos y +35 ítems insertados exitosamente!")

    except Exception as e:
        print("Error al verificar/poblar la base de datos:", e)

if __name__ == "__main__":
    verify_and_seed_data()
