import datetime
from database import execute_query, get_connection

class UserModel:
    @staticmethod
    def authenticate(username, password):
        sql = "SELECT id, username, nombre_completo, rol, activo FROM usuarios WHERE username = ? AND password_hash = ?"
        user = execute_query(sql, (username, password), fetch_one=True)
        if user and user["activo"]:
            return user
        return None

class ProductModel:
    @staticmethod
    def get_all(search_term=""):
        if search_term:
            sql = """
                SELECT p.*, c.nombre AS categoria_nombre 
                FROM productos p 
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.nombre LIKE ? OR p.codigo_barras LIKE ?
                ORDER BY p.nombre ASC
            """
            term = f"%{search_term}%"
            return execute_query(sql, (term, term), fetch_all=True)
        else:
            sql = """
                SELECT p.*, c.nombre AS categoria_nombre 
                FROM productos p 
                LEFT JOIN categorias c ON p.categoria_id = c.id
                ORDER BY p.nombre ASC
            """
            return execute_query(sql, fetch_all=True)

    @staticmethod
    def get_by_barcode(barcode):
        sql = """
            SELECT p.*, c.nombre AS categoria_nombre 
            FROM productos p 
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.codigo_barras = ?
        """
        return execute_query(sql, (barcode,), fetch_one=True)

    @staticmethod
    def get_by_id(product_id):
        sql = "SELECT * FROM productos WHERE id = ?"
        return execute_query(sql, (product_id,), fetch_one=True)

    @staticmethod
    def save_product(data):
        """Creates or updates a product."""
        if "id" in data and data["id"]:
            sql = """
                UPDATE productos 
                SET codigo_barras = ?, nombre = ?, categoria_id = ?, precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?
                WHERE id = ?
            """
            params = (
                data["codigo_barras"], data["nombre"], data["categoria_id"],
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"], data["id"]
            )
            execute_query(sql, params, commit=True)
            return data["id"]
        else:
            sql = """
                INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_costo, precio_venta, stock_actual, stock_minimo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                data["codigo_barras"], data["nombre"], data["categoria_id"],
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"]
            )
            execute_query(sql, params, commit=True)
            res = execute_query("SELECT @@IDENTITY AS new_id", fetch_one=True)
            return res["new_id"]

    @staticmethod
    def delete_product(product_id):
        sql = "DELETE FROM productos WHERE id = ?"
        execute_query(sql, (product_id,), commit=True)

    @staticmethod
    def get_categories():
        return execute_query("SELECT * FROM categorias ORDER BY nombre ASC", fetch_all=True)

    @staticmethod
    def get_low_stock_products():
        sql = """
            SELECT p.*, c.nombre AS categoria_nombre 
            FROM productos p 
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.stock_actual <= p.stock_minimo
            ORDER BY p.stock_actual ASC
        """
        return execute_query(sql, fetch_all=True)

class CajaModel:
    @staticmethod
    def get_active_caja(user_id=None):
        if user_id:
            sql = "SELECT TOP 1 * FROM cajas WHERE usuario_id = ? AND estado = 'Abierta' ORDER BY fecha_apertura DESC"
            return execute_query(sql, (user_id,), fetch_one=True)
        else:
            sql = "SELECT TOP 1 * FROM cajas WHERE estado = 'Abierta' ORDER BY fecha_apertura DESC"
            return execute_query(sql, fetch_one=True)

    @staticmethod
    def abrir_caja(user_id, monto_inicial):
        sql = "INSERT INTO cajas (usuario_id, monto_inicial, estado) VALUES (?, ?, 'Abierta')"
        execute_query(sql, (user_id, monto_inicial), commit=True)
        return CajaModel.get_active_caja(user_id)

    @staticmethod
    def cerrar_caja(caja_id, monto_real):
        # Calculate theoretical total
        sales = execute_query(
            "SELECT ISNULL(SUM(total), 0) AS total_ventas FROM ventas WHERE caja_id = ?", 
            (caja_id,), fetch_one=True
        )
        caja = execute_query("SELECT monto_inicial FROM cajas WHERE id = ?", (caja_id,), fetch_one=True)
        
        monto_teorico = float(caja["monto_inicial"]) + float(sales["total_ventas"])
        
        sql = """
            UPDATE cajas 
            SET monto_final_teorico = ?, monto_final_real = ?, fecha_cierre = GETDATE(), estado = 'Cerrada'
            WHERE id = ?
        """
        execute_query(sql, (monto_teorico, monto_real, caja_id), commit=True)
        return {
            "monto_teorico": monto_teorico,
            "monto_real": monto_real,
            "diferencia": monto_real - monto_teorico
        }

class VentaModel:
    @staticmethod
    def procesar_venta(caja_id, usuario_id, cliente_nombre, tipo_pago, items):
        """
        Executes a sale atomically across SQL Server tables:
        ventas -> detalle_ventas -> productos (update stock) -> movimientos_inventario.
        """
        if not items:
            raise ValueError("El carrito de compras está vacío.")

        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Subtotal, ITBIS (18%), Total
            subtotal = sum(item["precio_venta"] * item["cantidad"] for item in items)
            itbis = subtotal * 0.18
            total = subtotal + itbis
            
            codigo_factura = f"FAC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

            # 1. Insert into ventas
            sql_venta = """
                INSERT INTO ventas (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis_impuesto, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(sql_venta, (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total))
            
            cursor.execute("SELECT SCOPE_IDENTITY() AS new_id")
            venta_id = cursor.fetchone()[0]

            # 2. Insert details & update stock
            for item in items:
                prod_id = item["id"]
                cant = item["cantidad"]
                precio = item["precio_venta"]
                subtotal_item = precio * cant

                # Check current stock
                cursor.execute("SELECT stock_actual, nombre FROM productos WHERE id = ?", (prod_id,))
                prod_db = cursor.fetchone()
                if not prod_db or prod_db[0] < cant:
                    raise ValueError(f"Stock insuficiente para {prod_db[1] if prod_db else 'Producto'}. Disponible: {prod_db[0] if prod_db else 0}")

                # Detail insert
                cursor.execute("""
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (venta_id, prod_id, cant, precio, subtotal_item))

                # Update stock
                cursor.execute("""
                    UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?
                """, (cant, prod_id))

                # Record movement
                cursor.execute("""
                    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad, motivo, usuario_id)
                    VALUES (?, 'Salida/Ajuste', ?, ?, ?)
                """, (prod_id, cant, f"Venta Factura #{codigo_factura}", usuario_id))

            conn.commit()
            return {
                "venta_id": venta_id,
                "codigo_factura": codigo_factura,
                "cliente_nombre": cliente_nombre,
                "tipo_pago": tipo_pago,
                "subtotal": subtotal,
                "itbis": itbis,
                "total": total,
                "items": items,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

class InventoryMovementModel:
    @staticmethod
    def registrar_movimiento(producto_id, tipo_movimiento, cantidad, motivo, usuario_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Insert Movement
            cursor.execute("""
                INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad, motivo, usuario_id)
                VALUES (?, ?, ?, ?, ?)
            """, (producto_id, tipo_movimiento, cantidad, motivo, usuario_id))

            # 2. Adjust Stock
            if tipo_movimiento == "Entrada Suplidor":
                cursor.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?", (cantidad, producto_id))
            else:
                cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?", (cantidad, producto_id))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_recent_movements(limit=20):
        sql = """
            SELECT TOP (?) m.*, p.nombre AS producto_nombre, u.username AS usuario_nombre
            FROM movimientos_inventario m
            LEFT JOIN productos p ON m.producto_id = p.id
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY m.fecha DESC
        """
        return execute_query(sql, (limit,), fetch_all=True)

class ReportModel:
    @staticmethod
    def get_sales_summary(date_str=None):
        if not date_str:
            date_str = datetime.date.today().strftime("%Y-%m-%d")
        
        sql = """
            SELECT 
                COUNT(*) AS total_ventas_cant,
                ISNULL(SUM(subtotal), 0) AS total_subtotal,
                ISNULL(SUM(itbis_impuesto), 0) AS total_itbis,
                ISNULL(SUM(total), 0) AS total_ingresos
            FROM ventas
            WHERE CONVERT(DATE, fecha) = ?
        """
        return execute_query(sql, (date_str,), fetch_one=True)

    @staticmethod
    def get_top_selling_products(limit=5):
        sql = """
            SELECT TOP (?) p.nombre, SUM(dv.cantidad) AS cantidad_vendida, SUM(dv.subtotal) AS total_generado
            FROM detalle_ventas dv
            JOIN productos p ON dv.producto_id = p.id
            GROUP BY p.nombre
            ORDER BY cantidad_vendida DESC
        """
        return execute_query(sql, (limit,), fetch_all=True)

    @staticmethod
    def get_sales_history(limit=50):
        sql = """
            SELECT TOP (?) v.*, u.username, c.estado AS caja_estado
            FROM ventas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            LEFT JOIN cajas c ON v.caja_id = c.id
            ORDER BY v.fecha DESC
        """
        return execute_query(sql, (limit,), fetch_all=True)
