import datetime
from database import execute_query, get_connection, get_active_db_type

ALL_MODULES = [
    ("pos", "🛒 Caja / POS Billing"),
    ("inventory", "📦 Inventario & Alertas"),
    ("caja", "💵 Apertura / Cierre de Caja"),
    ("reports", "📊 Reportes & Diario Electrónico"),
    ("backoffice", "💼 Módulo de Back Office"),
    ("item_maintenance", "🏷️ Mantenimiento de Artículos"),
    ("customers", "👥 Gestión de Clientes / Suplidores"),
    ("operators", "🔒 Gestión de Operadores & Permisos"),
    ("discount", "🏷️ Permitir Descuentos en POS"),
    ("price_override", "✏️ Permitir Precios Manuales en POS")
]

class UserModel:
    @staticmethod
    def authenticate(username, password=""):
        u_str = str(username).strip()
        p_str = str(password).strip() if password is not None else ""
        sql = "SELECT id, username, nombre_completo, rol, activo FROM usuarios WHERE username = ? AND (password_hash = ? OR (password_hash IS NULL AND ? = ''))"
        user = execute_query(sql, (u_str, p_str, p_str), fetch_one=True)
        if user and user.get("activo"):
            return user
        return None

    @staticmethod
    def get_all():
        sql = "SELECT id, username, nombre_completo, rol, activo FROM usuarios ORDER BY id ASC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def create(username, password, nombre_completo, rol):
        u_str = str(username).strip()
        p_str = str(password).strip() if password is not None else ""
        if not u_str.isdigit() or not (1 <= len(u_str) <= 6):
            raise ValueError("El usuario debe ser numérico de 1 a 6 dígitos (ej. 1, 12, 100001).")
        if p_str:
            if not p_str.isdigit() or not (1 <= len(p_str) <= 6):
                raise ValueError("La contraseña/PIN debe ser numérica de 1 a 6 dígitos (o dejarse en blanco).")
            
        sql = "INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo) VALUES (?, ?, ?, ?, 1)"
        return execute_query(sql, (u_str, p_str, nombre_completo, rol), commit=True)

    @staticmethod
    def update(user_id, password, nombre_completo, rol, activo=1):
        if password is not None:
            p_str = str(password).strip()
            if p_str:
                if not p_str.isdigit() or not (1 <= len(p_str) <= 6):
                    raise ValueError("La contraseña/PIN debe ser numérica de 1 a 6 dígitos.")
            sql = "UPDATE usuarios SET password_hash = ?, nombre_completo = ?, rol = ?, activo = ? WHERE id = ?"
            return execute_query(sql, (p_str, nombre_completo, rol, activo, user_id), commit=True)
        else:
            sql = "UPDATE usuarios SET nombre_completo = ?, rol = ?, activo = ? WHERE id = ?"
            return execute_query(sql, (nombre_completo, rol, activo, user_id), commit=True)

    @staticmethod
    def delete(user_id):
        execute_query("DELETE FROM permisos_usuario WHERE usuario_id = ?", (user_id,), commit=True)
        sql = "DELETE FROM usuarios WHERE id = ?"
        return execute_query(sql, (user_id,), commit=True)

    @staticmethod
    def get_permissions(user_id):
        sql = "SELECT modulo_clave, permitido FROM permisos_usuario WHERE usuario_id = ?"
        rows = execute_query(sql, (user_id,), fetch_all=True) or []
        perm_map = {row["modulo_clave"]: bool(row["permitido"]) for row in rows}
        return perm_map

    @staticmethod
    def save_permissions(user_id, perm_map):
        execute_query("DELETE FROM permisos_usuario WHERE usuario_id = ?", (user_id,), commit=True)
        for key, value in perm_map.items():
            sql = "INSERT INTO permisos_usuario (usuario_id, modulo_clave, permitido) VALUES (?, ?, ?)"
            execute_query(sql, (user_id, key, 1 if value else 0), commit=True)

    @staticmethod
    def has_permission(user, module_key):
        if not user:
            return False
        rol = str(user.get("rol", "")).strip()
        if rol in ["Programador", "Admin", "Propietario", "Manager"]:
            return True
            
        user_perms = UserModel.get_permissions(user["id"])
        if module_key in user_perms:
            return user_perms[module_key]

        # Default fallbacks by role
        if rol == "Supervisor":
            return module_key in ["pos", "inventory", "caja", "reports", "backoffice", "item_maintenance", "customers", "discount"]
        elif rol == "Almacen":
            return module_key in ["inventory", "backoffice", "item_maintenance"]
        elif rol == "Cajero":
            return module_key in ["pos", "caja", "discount"]
        return False

class CustomerModel:
    @staticmethod
    def get_all(search_term=""):
        if search_term:
            sql = "SELECT * FROM clientes WHERE nombre_razon_social LIKE ? OR rnc_cedula LIKE ? OR codigo LIKE ? ORDER BY id DESC"
            term = f"%{search_term}%"
            return execute_query(sql, (term, term, term), fetch_all=True)
        sql = "SELECT * FROM clientes ORDER BY id DESC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def create(codigo, nombre_razon_social, rnc_cedula, tipo_cliente, telefono, email, direccion, porcentaje_descuento=0.0, limite_credito=0.0):
        sql = """
            INSERT INTO clientes (codigo, nombre_razon_social, rnc_cedula, tipo_cliente, telefono, email, direccion, porcentaje_descuento, limite_credito)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(sql, (codigo, nombre_razon_social, rnc_cedula, tipo_cliente, telefono, email, direccion, porcentaje_descuento, limite_credito), commit=True)

    @staticmethod
    def update(customer_id, nombre_razon_social, rnc_cedula, tipo_cliente, telefono, email, direccion, porcentaje_descuento=0.0, limite_credito=0.0):
        sql = """
            UPDATE clientes 
            SET nombre_razon_social = ?, rnc_cedula = ?, tipo_cliente = ?, telefono = ?, email = ?, direccion = ?, porcentaje_descuento = ?, limite_credito = ?
            WHERE id = ?
        """
        return execute_query(sql, (nombre_razon_social, rnc_cedula, tipo_cliente, telefono, email, direccion, porcentaje_descuento, limite_credito, customer_id), commit=True)

    @staticmethod
    def delete(customer_id):
        sql = "DELETE FROM clientes WHERE id = ?"
        return execute_query(sql, (customer_id,), commit=True)

class CompanyModel:
    @staticmethod
    def get():
        try:
            sql = "SELECT * FROM configuracion_empresa WHERE id = 1"
            res = execute_query(sql, fetch_one=True)
            if res:
                return res
        except Exception:
            pass
        return {
            "id": 1, "rnc": "101-00000-1",
            "nombre_comercial": "Minimarket La Ruta del Este",
            "telefono": "(809) 555-0199",
            "direccion": "Av. Principal #45, La Altagracia",
            "mensaje_factura": "¡Gracias por su compra! Vuelva pronto."
        }

    @staticmethod
    def update(rnc, nombre_comercial, telefono, direccion, mensaje_factura):
        sql = """
            UPDATE configuracion_empresa 
            SET rnc = ?, nombre_comercial = ?, telefono = ?, direccion = ?, mensaje_factura = ?
            WHERE id = 1
        """
        return execute_query(sql, (rnc, nombre_comercial, telefono, direccion, mensaje_factura), commit=True)

_DEPT_CACHE = None
_SUBDEPT_CACHE = None
_PROD_CACHE = None

def clear_models_cache():
    global _DEPT_CACHE, _SUBDEPT_CACHE, _PROD_CACHE
    _DEPT_CACHE = None
    _SUBDEPT_CACHE = None
    _PROD_CACHE = None

class DepartmentModel:
    @staticmethod
    def get_all():
        global _DEPT_CACHE
        if _DEPT_CACHE is not None:
            return _DEPT_CACHE
        sql = "SELECT * FROM departamentos ORDER BY id ASC"
        res = execute_query(sql, fetch_all=True)
        _DEPT_CACHE = res
        return res

    @staticmethod
    def create(nombre, descripcion=""):
        clear_models_cache()
        sql = "INSERT INTO departamentos (nombre, descripcion) VALUES (?, ?)"
        return execute_query(sql, (nombre, descripcion), commit=True)

    @staticmethod
    def update(dept_id, nombre, descripcion=""):
        clear_models_cache()
        sql = "UPDATE departamentos SET nombre = ?, descripcion = ? WHERE id = ?"
        return execute_query(sql, (nombre, descripcion, dept_id), commit=True)

class SubDepartmentModel:
    @staticmethod
    def get_all():
        global _SUBDEPT_CACHE
        if _SUBDEPT_CACHE is not None:
            return _SUBDEPT_CACHE
        sql = """
            SELECT sd.*, d.nombre AS departamento_nombre 
            FROM subdepartamentos sd
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            ORDER BY sd.id ASC
        """
        res = execute_query(sql, fetch_all=True)
        _SUBDEPT_CACHE = res
        return res

    @staticmethod
    def get_by_department(department_id):
        subdeps = SubDepartmentModel.get_all()
        return [sd for sd in subdeps if sd.get('departamento_id') == department_id]

    @staticmethod
    def create(departamento_id, nombre, descripcion=""):
        clear_models_cache()
        sql = "INSERT INTO subdepartamentos (departamento_id, nombre, descripcion) VALUES (?, ?, ?)"
        return execute_query(sql, (departamento_id, nombre, descripcion), commit=True)

    @staticmethod
    def update(subdep_id, departamento_id, nombre, descripcion=""):
        clear_models_cache()
        sql = "UPDATE subdepartamentos SET departamento_id = ?, nombre = ?, descripcion = ? WHERE id = ?"
        return execute_query(sql, (departamento_id, nombre, descripcion, subdep_id), commit=True)

class ProductModel:
    @staticmethod
    def get_all(search_term="", subdep_id=None, dep_id=None, active_only=False):
        global _PROD_CACHE
        if not search_term and subdep_id is None and dep_id is None and not active_only:
            if _PROD_CACHE is not None:
                return _PROD_CACHE

        params = []
        conditions = []

        sql = """
            SELECT p.*, 
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre,
                   c.nombre AS categoria_nombre 
            FROM productos p 
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
        """

        if search_term:
            conditions.append("(p.nombre LIKE ? OR p.codigo_barras LIKE ?)")
            term = f"%{search_term}%"
            params.extend([term, term])

        if subdep_id:
            conditions.append("p.subdepartamento_id = ?")
            params.append(subdep_id)

        if dep_id:
            conditions.append("sd.departamento_id = ?")
            params.append(dep_id)

        if active_only:
            conditions.append("p.estado = 'Activo'")

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY p.nombre ASC"
        res = execute_query(sql, tuple(params), fetch_all=True)
        if not search_term and subdep_id is None and dep_id is None:
            _PROD_CACHE = res
        return res

    @staticmethod
    def get_recent(limit=20, active_only=False):
        """Returns the top initial essential products (limit 20)."""
        extra = "AND (p.estado IS NULL OR p.estado = '' OR p.estado = 'Activo')" if active_only else ""
        sql = f"""
            SELECT TOP {limit} p.*,
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre,
                   c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE 1=1 {extra}
            ORDER BY p.nombre ASC
        """
        return execute_query(sql, (), fetch_all=True) or []

    @staticmethod
    def search_live(term="", limit=100, active_only=False, subdep_id=None):
        """SQL-level live search — handles search terms and subdepartment filtering."""
        conditions = []
        params = []

        if term:
            t = f"%{term}%"
            conditions.append("(p.nombre LIKE ? OR p.codigo_barras LIKE ?)")
            params.extend([t, t])

        if active_only:
            conditions.append("(p.estado IS NULL OR p.estado = '' OR p.estado = 'Activo')")

        if subdep_id is not None:
            conditions.append("p.subdepartamento_id = ?")
            params.append(subdep_id)

        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        eff_limit = limit if (term or subdep_id is not None) else 20

        sql = f"""
            SELECT TOP {eff_limit} p.*,
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre,
                   c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            {where}
            ORDER BY p.nombre ASC
        """
        return execute_query(sql, tuple(params), fetch_all=True) or []

    @staticmethod
    def get_by_id(product_id):
        sql = "SELECT * FROM productos WHERE id = ?"
        return execute_query(sql, (product_id,), fetch_one=True)

    @staticmethod
    def get_by_subdepartment(subdep_id):
        all_prods = ProductModel.get_all()
        return [p for p in all_prods if p.get('subdepartamento_id') == subdep_id]

    @staticmethod
    def save_product(data):
        """Creates or updates a product."""
        clear_models_cache()
        subdep_id = data.get("subdepartamento_id", None)
        es_desc = 1 if data.get("es_descontable", True) else 0
        precio_man = 1 if data.get("precio_manual", False) else 0
        unidad = data.get("unidad_medida", "UD")
        estado = data.get("estado", "Activo")

        if "id" in data and data["id"]:
            sql = """
                UPDATE productos 
                SET codigo_barras = ?, nombre = ?, subdepartamento_id = ?, precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?, es_descontable = ?, precio_manual = ?, unidad_medida = ?, estado = ?
                WHERE id = ?
            """
            params = (
                data["codigo_barras"], data["nombre"], subdep_id,
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"], es_desc, precio_man, unidad, estado, data["id"]
            )
            execute_query(sql, params, commit=True)
            return data["id"]
        else:
            sql = """
                INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, es_descontable, precio_manual, unidad_medida, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                data["codigo_barras"], data["nombre"], subdep_id,
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"], es_desc, precio_man, unidad, estado
            )
            new_id = execute_query(sql, params, commit=True)
            if isinstance(new_id, int) and new_id > 0:
                return new_id
            res = execute_query("SELECT MAX(id) AS new_id FROM productos", fetch_one=True)
            return res["new_id"]

    @staticmethod
    def delete_product(product_id):
        clear_models_cache()
        sql = "DELETE FROM productos WHERE id = ?"
        execute_query(sql, (product_id,), commit=True)

    @staticmethod
    def get_categories():
        return execute_query("SELECT * FROM categorias ORDER BY nombre ASC", fetch_all=True)

    @staticmethod
    def get_low_stock_products():
        sql = """
            SELECT p.*, 
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre
            FROM productos p 
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            WHERE p.stock_actual <= p.stock_minimo
            ORDER BY p.stock_actual ASC
        """
        return execute_query(sql, fetch_all=True)

class CajaModel:
    @staticmethod
    def get_active_caja(user_id=None):
        if get_active_db_type() == "SQL Server":
            if user_id:
                sql = "SELECT TOP 1 * FROM cajas WHERE usuario_id = ? AND estado = 'Abierta' ORDER BY fecha_apertura DESC"
                return execute_query(sql, (user_id,), fetch_one=True)
            else:
                sql = "SELECT TOP 1 * FROM cajas WHERE estado = 'Abierta' ORDER BY fecha_apertura DESC"
                return execute_query(sql, fetch_one=True)
        else:
            if user_id:
                sql = "SELECT * FROM cajas WHERE usuario_id = ? AND estado = 'Abierta' ORDER BY fecha_apertura DESC LIMIT 1"
                return execute_query(sql, (user_id,), fetch_one=True)
            else:
                sql = "SELECT * FROM cajas WHERE estado = 'Abierta' ORDER BY fecha_apertura DESC LIMIT 1"
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
            "SELECT COALESCE(SUM(total), 0) AS total_ventas FROM ventas WHERE caja_id = ?", 
            (caja_id,), fetch_one=True
        )
        caja = execute_query("SELECT monto_inicial FROM cajas WHERE id = ?", (caja_id,), fetch_one=True)
        
        monto_teorico = float(caja["monto_inicial"]) + float(sales["total_ventas"])
        
        if get_active_db_type() == "SQL Server":
            sql = """
                UPDATE cajas 
                SET monto_final_teorico = ?, monto_final_real = ?, fecha_cierre = GETDATE(), estado = 'Cerrada'
                WHERE id = ?
            """
        else:
            sql = """
                UPDATE cajas 
                SET monto_final_teorico = ?, monto_final_real = ?, fecha_cierre = datetime('now', 'localtime'), estado = 'Cerrada'
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
        Executes a sale atomically across tables:
        ventas -> detalle_ventas -> productos (update stock) -> movimientos_inventario.
        """
        if not items:
            raise ValueError("El carrito de compras está vacío.")

        conn, db_type = get_connection()
        cursor = conn.cursor()
        
        try:
            # Subtotal, ITBIS (18%), Total
            subtotal = sum(item["precio_venta"] * item["cantidad"] for item in items)
            itbis = subtotal * 0.18
            total = subtotal + itbis
            
            codigo_factura = f"FAC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

            if db_type == "sqlite":
                sql_venta = """
                    INSERT INTO ventas (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis_impuesto, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(sql_venta, (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total))
                venta_id = cursor.lastrowid
            else:
                sql_venta = """
                    INSERT INTO ventas (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis_impuesto, total)
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(sql_venta, (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total))
                row_id = cursor.fetchone()
                venta_id = row_id[0] if row_id else None

            # 2. Insert details & update stock
            for item in items:
                prod_id = item["id"]
                cant = item["cantidad"]
                precio = item["precio_venta"]
                subtotal_item = precio * cant

                # Check current stock and get cost price
                cursor.execute("SELECT stock_actual, nombre, precio_costo FROM productos WHERE id = ?", (prod_id,))
                prod_db = cursor.fetchone()
                if isinstance(prod_db, dict) or hasattr(prod_db, 'keys'):
                    stock_val = prod_db["stock_actual"]
                    prod_name = prod_db["nombre"]
                    costo_unitario = float(prod_db.get("precio_costo") or 0)
                else:
                    stock_val = prod_db[0]
                    prod_name = prod_db[1]
                    costo_unitario = float(prod_db[2]) if len(prod_db) > 2 else 0.0

                if not prod_db or stock_val < cant:
                    raise ValueError(f"Stock insuficiente para {prod_name}. Disponible: {stock_val}")

                # Detail insert - include precio_costo and descuento
                descuento_item = float(item.get("descuento", 0) or 0)
                try:
                    cursor.execute("""
                        INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, precio_costo, descuento, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (venta_id, prod_id, cant, precio, costo_unitario, descuento_item, subtotal_item))
                except Exception:
                    # Fallback without new columns for older schemas
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
        conn, _ = get_connection()
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
        if get_active_db_type() == "SQL Server":
            sql = """
                SELECT TOP (?) m.*, p.nombre AS producto_nombre, u.username AS usuario_nombre
                FROM movimientos_inventario m
                LEFT JOIN productos p ON m.producto_id = p.id
                LEFT JOIN usuarios u ON m.usuario_id = u.id
                ORDER BY m.fecha DESC
            """
            return execute_query(sql, (limit,), fetch_all=True)
        else:
            sql = """
                SELECT m.*, p.nombre AS producto_nombre, u.username AS usuario_nombre
                FROM movimientos_inventario m
                LEFT JOIN productos p ON m.producto_id = p.id
                LEFT JOIN usuarios u ON m.usuario_id = u.id
                ORDER BY m.fecha DESC
                LIMIT ?
            """
            return execute_query(sql, (limit,), fetch_all=True)


class ReportModel:
    @staticmethod
    def get_date_range_bounds(period_type, start_date=None, end_date=None):
        today = datetime.date.today()
        p = str(period_type or '').strip()

        def to_iso_date(d_str):
            if not d_str: return today
            d_str = str(d_str).strip()
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(d_str, fmt).date()
                except ValueError:
                    pass
            return today

        if p in ["Día", "Hoy"]:
            s = e = today
        elif p in ["Semana", "Esta Semana"]:
            s = today - datetime.timedelta(days=today.weekday())
            e = today
        elif p in ["Mes", "Este Mes"]:
            s = today.replace(day=1)
            e = today
        elif p in ["Año", "Este Año"]:
            s = today.replace(month=1, day=1)
            e = today
        elif p == "Personalizado" and start_date and end_date:
            s = to_iso_date(start_date)
            e = to_iso_date(end_date)
        else:
            s = e = today

        return f"{s} 00:00:00", f"{e} 23:59:59" 

    @staticmethod
    def get_executive_summary(start_dt, end_dt):
        sql = """
            SELECT 
                COUNT(*) AS total_transacciones,
                COALESCE(SUM(v.subtotal), 0) AS total_subtotal,
                COALESCE(SUM(v.itbis_impuesto), 0) AS total_itbis,
                COALESCE(SUM(v.total), 0) AS total_ingresos,
                COALESCE(SUM(dv_margin.costo_total), 0) AS costo_total_estimado,
                (COALESCE(SUM(v.subtotal), 0) - COALESCE(SUM(dv_margin.costo_total), 0)) AS ganancia_estimada
            FROM ventas v
            LEFT JOIN (
                SELECT venta_id, SUM(COALESCE(precio_costo, 0) * cantidad) AS costo_total
                FROM detalle_ventas
                GROUP BY venta_id
            ) dv_margin ON v.id = dv_margin.venta_id
            WHERE v.fecha >= ? AND v.fecha <= ?
        """
        try:
            res = execute_query(sql, (start_dt, end_dt), fetch_one=True)
        except Exception:
            # Fallback without cost calculation if column issue
            sql_simple = """
                SELECT 
                    COUNT(*) AS total_transacciones,
                    COALESCE(SUM(subtotal), 0) AS total_subtotal,
                    COALESCE(SUM(itbis_impuesto), 0) AS total_itbis,
                    COALESCE(SUM(total), 0) AS total_ingresos,
                    0 AS costo_total_estimado,
                    COALESCE(SUM(subtotal), 0) AS ganancia_estimada
                FROM ventas
                WHERE fecha >= ? AND fecha <= ?
            """
            res = execute_query(sql_simple, (start_dt, end_dt), fetch_one=True)

        if not res or not res.get("total_transacciones"):
            return {
                "total_transacciones": 0,
                "total_subtotal": 0.0,
                "total_itbis": 0.0,
                "total_ingresos": 0.0,
                "costo_total_estimado": 0.0,
                "ganancia_estimada": 0.0,
                "ticket_promedio": 0.0
            }

        tot_cnt = int(res["total_transacciones"] or 0)
        tot_ing = float(res["total_ingresos"] or 0)
        res["ticket_promedio"] = tot_ing / tot_cnt if tot_cnt > 0 else 0.0
        # Ensure all keys are float-safe
        for k in ["total_subtotal", "total_itbis", "total_ingresos", "costo_total_estimado", "ganancia_estimada"]:
            res[k] = float(res.get(k) or 0)
        return res

    @staticmethod
    def get_department_subdepartment_sales(start_dt, end_dt):
        sql = """
            SELECT 
                COALESCE(d.nombre, 'Sin Departamento') AS departamento,
                COALESCE(sd.nombre, 'Sin Sub-Depto') AS subdepartamento,
                SUM(dv.cantidad) AS unidades_vendidas,
                SUM(dv.subtotal) AS total_bruto,
                SUM(dv.subtotal * 0.18) AS itbis_estimado,
                SUM(dv.subtotal * 1.18) AS total_neto,
                SUM(COALESCE(dv.precio_costo, 0) * dv.cantidad) AS costo_total,
                (SUM(dv.subtotal) - SUM(COALESCE(dv.precio_costo, 0) * dv.cantidad)) AS ganancia_estimada
            FROM detalle_ventas dv
            JOIN ventas v ON dv.venta_id = v.id
            JOIN productos p ON dv.producto_id = p.id
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            WHERE v.fecha >= ? AND v.fecha <= ?
            GROUP BY d.nombre, sd.nombre
            ORDER BY SUM(dv.subtotal) DESC
        """
        try:
            rows = execute_query(sql, (start_dt, end_dt), fetch_all=True)
        except Exception:
            rows = []
        return rows if rows else []

    @staticmethod
    def get_multi_total_store_report(start_dt, end_dt):
        sql_payment = """
            SELECT 
                COALESCE(tipo_pago, 'Efectivo') AS tipo_pago,
                COUNT(*) AS total_operaciones,
                SUM(subtotal) AS subtotal,
                SUM(itbis_impuesto) AS itbis,
                SUM(total) AS total_monto
            FROM ventas
            WHERE fecha >= ? AND fecha <= ?
            GROUP BY tipo_pago
            ORDER BY total_monto DESC
        """
        by_payment = execute_query(sql_payment, (start_dt, end_dt), fetch_all=True)

        sql_user = """
            SELECT 
                COALESCE(u.username, 'Cajero General') AS cajero,
                COUNT(v.id) AS total_ventas,
                SUM(v.total) AS total_monto
            FROM ventas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.fecha >= ? AND v.fecha <= ?
            GROUP BY u.username
            ORDER BY total_monto DESC
        """
        by_user = execute_query(sql_user, (start_dt, end_dt), fetch_all=True)

        return {
            "by_payment": by_payment,
            "by_user": by_user
        }

    @staticmethod
    def get_inventory_valuation_report():
        sql = """
            SELECT 
                COUNT(*) AS total_productos,
                SUM(stock_actual) AS total_unidades,
                SUM(stock_actual * precio_costo) AS valor_costo_total,
                SUM(stock_actual * precio_venta) AS valor_venta_total,
                SUM(stock_actual * (precio_venta - precio_costo)) AS ganancia_potencial,
                SUM(CASE WHEN stock_actual <= 0 THEN 1 ELSE 0 END) AS cant_agotados,
                SUM(CASE WHEN stock_actual > 0 AND stock_actual <= stock_minimo THEN 1 ELSE 0 END) AS cant_stock_bajo
            FROM productos
        """
        val_summary = execute_query(sql, fetch_one=True)

        sql_details = """
            SELECT 
                p.codigo_barras, p.nombre,
                COALESCE(d.nombre, 'General') AS departamento,
                COALESCE(sd.nombre, 'General') AS subdepartamento,
                p.precio_costo, p.precio_venta, p.stock_actual, p.stock_minimo,
                (p.stock_actual * p.precio_costo) AS valor_costo,
                (p.stock_actual * p.precio_venta) AS valor_venta
            FROM productos p
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            ORDER BY valor_venta DESC
        """
        details = execute_query(sql_details, fetch_all=True)

        return {
            "summary": val_summary,
            "details": details
        }

    @staticmethod
    def get_electronic_journal(start_dt, end_dt):
        sql_ventas = """
            SELECT v.*, u.username AS cajero_nombre
            FROM ventas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.fecha >= ? AND v.fecha <= ?
            ORDER BY v.fecha DESC
        """
        ventas = execute_query(sql_ventas, (start_dt, end_dt), fetch_all=True)

        for v in ventas:
            sql_items = """
                SELECT dv.*, p.nombre AS producto_nombre, p.codigo_barras,
                       COALESCE(sd.nombre, 'General') AS subdepartamento_nombre
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
                WHERE dv.venta_id = ?
            """
            v["items"] = execute_query(sql_items, (v["id"],), fetch_all=True)

        return ventas
