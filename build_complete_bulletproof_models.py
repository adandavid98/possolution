import sys
import ast

models_code = '''import os
import sys
import hashlib
from database import execute_query, get_active_db_type

_DEPT_CACHE = None
_SUBDEPT_CACHE = None
_PROD_CACHE = None

def clear_models_cache():
    global _DEPT_CACHE, _SUBDEPT_CACHE, _PROD_CACHE
    _DEPT_CACHE = None
    _SUBDEPT_CACHE = None
    _PROD_CACHE = None

def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

ALL_MODULES = [
    ("pos", "Punto de Venta (Caja)"),
    ("productos", "Gestión de Productos"),
    ("inventario", "Control de Inventario & Stock"),
    ("clientes", "Gestión de Clientes"),
    ("usuarios", "Gestión de Usuarios & Roles"),
    ("cajas", "Apertura / Cierre de Cajas"),
    ("reportes", "Reportes de Ventas & Exportación"),
    ("backoffice", "Back Office & Ajustes Avanzados")
]

class UserModel:
    @staticmethod
    def authenticate(username, password):
        pwd_hash = _hash_password(password)
        sql = "SELECT * FROM usuarios WHERE username = ? AND password_hash = ? AND (activo = 1 OR activo IS NULL)"
        return execute_query(sql, (username, pwd_hash), fetch_one=True)

    @staticmethod
    def get_all(query=""):
        if query:
            sql = "SELECT * FROM usuarios WHERE username LIKE ? OR nombre_completo LIKE ? ORDER BY id ASC"
            q = f"%{query}%"
            return execute_query(sql, (q, q), fetch_all=True)
        sql = "SELECT * FROM usuarios ORDER BY id ASC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def create(username, password, nombre_completo, rol="Cajero"):
        pwd_hash = _hash_password(password)
        sql = "INSERT INTO usuarios (username, password_hash, nombre_completo, rol, activo) VALUES (?, ?, ?, ?, 1)"
        return execute_query(sql, (username, pwd_hash, nombre_completo, rol), commit=True)

    @staticmethod
    def update(user_id, nombre_completo, rol, password=None, activo=1):
        if password:
            pwd_hash = _hash_password(password)
            sql = "UPDATE usuarios SET nombre_completo = ?, rol = ?, password_hash = ?, activo = ? WHERE id = ?"
            return execute_query(sql, (nombre_completo, rol, pwd_hash, activo, user_id), commit=True)
        else:
            sql = "UPDATE usuarios SET nombre_completo = ?, rol = ?, activo = ? WHERE id = ?"
            return execute_query(sql, (nombre_completo, rol, activo, user_id), commit=True)

    @staticmethod
    def delete(user_id):
        sql = "DELETE FROM usuarios WHERE id = ?"
        return execute_query(sql, (user_id,), commit=True)

    @staticmethod
    def get_permissions(user_id):
        sql = "SELECT modulo_clave, permitido FROM permisos_usuario WHERE usuario_id = ?"
        rows = execute_query(sql, (user_id,), fetch_all=True) or []
        res = {}
        for r in rows:
            res[r["modulo_clave"]] = bool(r["permitido"])
        return res

    @staticmethod
    def save_permissions(user_id, permissions_dict):
        del_sql = "DELETE FROM permisos_usuario WHERE usuario_id = ?"
        execute_query(del_sql, (user_id,), commit=True)
        for mod, perm in permissions_dict.items():
            ins_sql = "INSERT INTO permisos_usuario (usuario_id, modulo_clave, permitido) VALUES (?, ?, ?)"
            execute_query(ins_sql, (user_id, mod, 1 if perm else 0), commit=True)

    @staticmethod
    def has_permission(user_id, modulo_clave, user_role=None):
        if user_role == "Admin":
            return True
        perms = UserModel.get_permissions(user_id)
        if not perms:
            return True
        return perms.get(modulo_clave, True)

class CustomerModel:
    @staticmethod
    def get_all(query=""):
        if query:
            sql = "SELECT * FROM clientes WHERE codigo LIKE ? OR nombre_razon_social LIKE ? OR rnc_cedula LIKE ? ORDER BY id ASC"
            q = f"%{query}%"
            return execute_query(sql, (q, q, q), fetch_all=True)
        sql = "SELECT * FROM clientes ORDER BY id ASC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def create(codigo, nombre, rnc_cedula="", tipo="General", tel="", email="", direccion="", descuento=0, limite=0):
        sql = """
            INSERT INTO clientes (codigo, nombre_razon_social, rnc_cedula, tipo_cliente, telefono, email, direccion, porcentaje_descuento, limite_credito, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """
        return execute_query(sql, (codigo, nombre, rnc_cedula, tipo, tel, email, direccion, descuento, limite), commit=True)

    @staticmethod
    def update(customer_id, codigo, nombre, rnc_cedula="", tipo="General", tel="", email="", direccion="", descuento=0, limite=0):
        sql = """
            UPDATE clientes 
            SET codigo = ?, nombre_razon_social = ?, rnc_cedula = ?, tipo_cliente = ?, telefono = ?, email = ?, direccion = ?, porcentaje_descuento = ?, limite_credito = ?
            WHERE id = ?
        """
        return execute_query(sql, (codigo, nombre, rnc_cedula, tipo, tel, email, direccion, descuento, limite, customer_id), commit=True)

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
            if res and res.get("nombre_comercial"):
                return res
            
            default_data = {
                "id": 1, "rnc": "101-00000-1",
                "nombre_comercial": "Minimarket La Ruta del Este",
                "telefono": "(809) 555-0199",
                "direccion": "Av. Principal #45, La Altagracia",
                "mensaje_factura": "¡Gracias por su compra! Vuelva pronto."
            }
            try:
                seed_sql = """
                    INSERT INTO configuracion_empresa (id, rnc, nombre_comercial, telefono, direccion, mensaje_factura)
                    VALUES (1, ?, ?, ?, ?, ?)
                """
                execute_query(seed_sql, (default_data["rnc"], default_data["nombre_comercial"], default_data["telefono"], default_data["direccion"], default_data["mensaje_factura"]), commit=True)
            except Exception:
                pass
            return default_data
        except Exception as e:
            print("Error in CompanyModel.get():", e)
        return {
            "id": 1, "rnc": "101-00000-1",
            "nombre_comercial": "Minimarket La Ruta del Este",
            "telefono": "(809) 555-0199",
            "direccion": "Av. Principal #45, La Altagracia",
            "mensaje_factura": "¡Gracias por su compra! Vuelva pronto."
        }

    @staticmethod
    def update(rnc, nombre_comercial, telefono, direccion, mensaje_factura):
        try:
            check_sql = "SELECT id FROM configuracion_empresa WHERE id = 1"
            exists = execute_query(check_sql, fetch_one=True)
            if exists:
                sql = """
                    UPDATE configuracion_empresa 
                    SET rnc = ?, nombre_comercial = ?, telefono = ?, direccion = ?, mensaje_factura = ?
                    WHERE id = 1
                """
                return execute_query(sql, (rnc, nombre_comercial, telefono, direccion, mensaje_factura), commit=True)
            else:
                sql = """
                    INSERT INTO configuracion_empresa (id, rnc, nombre_comercial, telefono, direccion, mensaje_factura)
                    VALUES (1, ?, ?, ?, ?, ?)
                """
                return execute_query(sql, (rnc, nombre_comercial, telefono, direccion, mensaje_factura), commit=True)
        except Exception as e:
            print("Error in CompanyModel.update():", e)
            return False

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

    @staticmethod
    def delete(dept_id):
        clear_models_cache()
        sql = "DELETE FROM departamentos WHERE id = ?"
        return execute_query(sql, (dept_id,), commit=True)

class SubDepartmentModel:
    @staticmethod
    def get_all(dept_id=None):
        global _SUBDEPT_CACHE
        if _SUBDEPT_CACHE is not None and dept_id is None:
            return _SUBDEPT_CACHE
        if dept_id:
            sql = "SELECT * FROM subdepartamentos WHERE departamento_id = ? ORDER BY id ASC"
            return execute_query(sql, (dept_id,), fetch_all=True)
        sql = "SELECT * FROM subdepartamentos ORDER BY id ASC"
        res = execute_query(sql, fetch_all=True)
        if dept_id is None:
            _SUBDEPT_CACHE = res
        return res

    @staticmethod
    def create(dept_id, nombre, descripcion=""):
        clear_models_cache()
        sql = "INSERT INTO subdepartamentos (departamento_id, nombre, descripcion) VALUES (?, ?, ?)"
        return execute_query(sql, (dept_id, nombre, descripcion), commit=True)

    @staticmethod
    def update(subdept_id, dept_id, nombre, descripcion=""):
        clear_models_cache()
        sql = "UPDATE subdepartamentos SET departamento_id = ?, nombre = ?, descripcion = ? WHERE id = ?"
        return execute_query(sql, (dept_id, nombre, descripcion, subdept_id), commit=True)

    @staticmethod
    def delete(subdept_id):
        clear_models_cache()
        sql = "DELETE FROM subdepartamentos WHERE id = ?"
        return execute_query(sql, (subdept_id,), commit=True)

class ProductModel:
    @staticmethod
    def get_all(query=""):
        global _PROD_CACHE
        if not query and _PROD_CACHE is not None:
            return _PROD_CACHE
        if query:
            sql = "SELECT * FROM productos WHERE codigo_barras LIKE ? OR nombre LIKE ? ORDER BY id ASC"
            q = f"%{query}%"
            return execute_query(sql, (q, q), fetch_all=True)
        sql = "SELECT * FROM productos ORDER BY id ASC"
        res = execute_query(sql, fetch_all=True)
        if not query:
            _PROD_CACHE = res
        return res

    @staticmethod
    def get_by_id(prod_id):
        sql = "SELECT * FROM productos WHERE id = ?"
        return execute_query(sql, (prod_id,), fetch_one=True)

    @staticmethod
    def get_by_codigo(codigo_barras):
        sql = "SELECT * FROM productos WHERE codigo_barras = ?"
        return execute_query(sql, (codigo_barras,), fetch_one=True)

    @staticmethod
    def get_low_stock_products():
        sql = "SELECT * FROM productos WHERE stock_actual <= stock_minimo ORDER BY stock_actual ASC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def create(codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento=None):
        clear_models_cache()
        sql = """
            INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(sql, (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento), commit=True)

    @staticmethod
    def update(prod_id, codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento=None):
        clear_models_cache()
        sql = """
            UPDATE productos 
            SET codigo_barras = ?, nombre = ?, subdepartamento_id = ?, precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?, fecha_vencimiento = ?
            WHERE id = ?
        """
        return execute_query(sql, (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento, prod_id), commit=True)

    @staticmethod
    def delete(prod_id):
        clear_models_cache()
        sql = "DELETE FROM productos WHERE id = ?"
        return execute_query(sql, (prod_id,), commit=True)

    @staticmethod
    def update_stock(prod_id, delta_stock):
        clear_models_cache()
        sql = "UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?"
        return execute_query(sql, (delta_stock, prod_id), commit=True)

class CajaModel:
    @staticmethod
    def get_active(user_id=None):
        if user_id:
            sql = "SELECT TOP 1 * FROM cajas WHERE usuario_id = ? AND estado = 'Abierta' ORDER BY id DESC"
            return execute_query(sql, (user_id,), fetch_one=True)
        sql = "SELECT TOP 1 * FROM cajas WHERE estado = 'Abierta' ORDER BY id DESC"
        return execute_query(sql, fetch_one=True)

    @staticmethod
    def abrir(user_id, monto_inicial):
        sql = "INSERT INTO cajas (usuario_id, monto_inicial, fecha_apertura, estado) VALUES (?, ?, GETDATE(), 'Abierta')"
        return execute_query(sql, (user_id, monto_inicial), commit=True)

    @staticmethod
    def cerrar(caja_id, monto_final_real):
        sql = "UPDATE cajas SET monto_final_real = ?, fecha_cierre = GETDATE(), estado = 'Cerrada' WHERE id = ?"
        return execute_query(sql, (monto_final_real, caja_id), commit=True)

    @staticmethod
    def get_all():
        sql = "SELECT * FROM cajas ORDER BY id DESC"
        return execute_query(sql, fetch_all=True)

class VentaModel:
    @staticmethod
    def create(codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total, items):
        clear_models_cache()
        sql_v = """
            INSERT INTO ventas (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis_impuesto, total, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """
        res_v = execute_query(sql_v, (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total), commit=True)
        
        # Get latest sale ID
        sql_last = "SELECT TOP 1 id FROM ventas WHERE codigo_factura = ?"
        v_row = execute_query(sql_last, (codigo_factura,), fetch_one=True)
        if not v_row:
            return False
        venta_id = v_row["id"]

        for item in items:
            p_id = item["id"]
            qty = item["qty"]
            p_unit = item["price"]
            p_cost = item.get("precio_costo", 0)
            desc = item.get("descuento", 0)
            item_sub = qty * p_unit - desc

            sql_d = """
                INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, precio_costo, descuento, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            execute_query(sql_d, (venta_id, p_id, qty, p_unit, p_cost, desc, item_sub), commit=True)
            ProductModel.update_stock(p_id, -qty)

        return True

    @staticmethod
    def get_all(search_query=""):
        if search_query:
            sql = "SELECT * FROM ventas WHERE codigo_factura LIKE ? OR cliente_nombre LIKE ? ORDER BY id DESC"
            q = f"%{search_query}%"
            return execute_query(sql, (q, q), fetch_all=True)
        sql = "SELECT * FROM ventas ORDER BY id DESC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def get_by_id(venta_id):
        sql_v = "SELECT * FROM ventas WHERE id = ?"
        v = execute_query(sql_v, (venta_id,), fetch_one=True)
        if not v:
            return None
        sql_d = "SELECT d.*, p.nombre as producto_nombre, p.codigo_barras FROM detalle_ventas d JOIN productos p ON d.producto_id = p.id WHERE d.venta_id = ?"
        items = execute_query(sql_d, (venta_id,), fetch_all=True)
        v["items"] = items
        return v

class InventoryMovementModel:
    @staticmethod
    def log(prod_id, tipo_mov, cantidad, motivo="", user_id=None):
        clear_models_cache()
        sql = """
            INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad, motivo, usuario_id, fecha)
            VALUES (?, ?, ?, ?, ?, GETDATE())
        """
        res = execute_query(sql, (prod_id, tipo_mov, cantidad, motivo, user_id), commit=True)
        
        # Adjust stock according to movement type
        if tipo_mov == "Entrada Suplidor":
            ProductModel.update_stock(prod_id, cantidad)
        elif tipo_mov in ["Salida/Ajuste", "Mermas/Vencido"]:
            ProductModel.update_stock(prod_id, -abs(cantidad))
        return res

    @staticmethod
    def get_all(prod_id=None):
        if prod_id:
            sql = "SELECT m.*, p.nombre as producto_nombre FROM movimientos_inventario m JOIN productos p ON m.producto_id = p.id WHERE m.producto_id = ? ORDER BY m.id DESC"
            return execute_query(sql, (prod_id,), fetch_all=True)
        sql = "SELECT m.*, p.nombre as producto_nombre FROM movimientos_inventario m JOIN productos p ON m.producto_id = p.id ORDER BY m.id DESC"
        return execute_query(sql, fetch_all=True)

class ReportModel:
    @staticmethod
    def get_sales_summary():
        sql = "SELECT COUNT(*) as total_ventas, SUM(total) as monto_total FROM ventas"
        res = execute_query(sql, fetch_one=True)
        return res or {"total_ventas": 0, "monto_total": 0}

    @staticmethod
    def get_dashboard_metrics():
        v_res = ReportModel.get_sales_summary()
        p_res = execute_query("SELECT COUNT(*) as total_prods FROM productos", fetch_one=True)
        c_res = execute_query("SELECT COUNT(*) as total_clientes FROM clientes", fetch_one=True)
        return {
            "total_ventas": v_res.get("total_ventas", 0) if v_res else 0,
            "monto_total": float(v_res.get("monto_total", 0) or 0) if v_res else 0,
            "total_productos": p_res.get("total_prods", 0) if p_res else 0,
            "total_clientes": c_res.get("total_clientes", 0) if c_res else 0
        }
'''

ast.parse(models_code)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(models_code)

print("models.py written with complete, 100% verified AST syntax!")
