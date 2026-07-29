import os
import sys
import hashlib
import datetime
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
    ("pos", "🛒 Punto de Venta (Caja & Cobros)"),
    ("productos", "🏷️ Mantenimiento de Artículos & Catálogo"),
    ("inventory", "📦 Control de Inventario, Stock & Mermas"),
    ("clientes", "👥 Gestión de Clientes & Proveedores"),
    ("caja", "💵 Apertura / Cierre & Arqueo de Cajas"),
    ("reports", "📊 Reportes de Ventas & Exportación PDF/Excel"),
    ("usuarios", "🔐 Gestión de Operadores & Permisos RBAC"),
    ("tienda", "🏬 Configuración General de la Tienda"),
    ("backup", "💾 Respaldo y Restauración de Base de Datos")
]

DEFAULT_ROLE_PERMISSIONS = {
    "Cajero": {
        "pos": True,
        "caja": True,
        "productos": False,
        "inventory": False,
        "clientes": False,
        "reports": False,
        "usuarios": False,
        "tienda": False,
        "backup": False,
        "backoffice": False
    },
    "Almacen": {
        "pos": False,
        "caja": False,
        "productos": True,
        "inventory": True,
        "clientes": True,
        "reports": True,
        "usuarios": False,
        "tienda": False,
        "backup": False,
        "backoffice": True
    },
    "Vendedor": {
        "pos": True,
        "caja": False,
        "productos": False,
        "inventory": False,
        "clientes": True,
        "reports": False,
        "usuarios": False,
        "tienda": False,
        "backup": False,
        "backoffice": False
    },
    "Manager": {
        "pos": True,
        "caja": True,
        "productos": True,
        "inventory": True,
        "clientes": True,
        "reports": True,
        "usuarios": False,
        "tienda": False,
        "backup": False,
        "backoffice": True
    },
    "Supervisor": {
        "pos": True,
        "caja": True,
        "productos": True,
        "inventory": True,
        "clientes": True,
        "reports": True,
        "usuarios": False,
        "tienda": False,
        "backup": False,
        "backoffice": True
    },
    "Admin": {
        "pos": True, "productos": True, "inventory": True, "clientes": True,
        "caja": True, "reports": True, "usuarios": True, "tienda": True, "backup": True, "backoffice": True
    },
    "Programador": {
        "pos": True, "productos": True, "inventory": True, "clientes": True,
        "caja": True, "reports": True, "usuarios": True, "tienda": True, "backup": True, "backoffice": True
    },
    "Propietario": {
        "pos": True, "productos": True, "inventory": True, "clientes": True,
        "caja": True, "reports": True, "usuarios": True, "tienda": True, "backup": True, "backoffice": True
    }
}

class UserModel:
    @staticmethod
    def authenticate(username, password):
        pwd_hash = _hash_password(password)
        sql = "SELECT * FROM usuarios WHERE username = ? AND (password_hash = ? OR password_hash = ?) AND (activo = 1 OR activo IS NULL)"
        return execute_query(sql, (username, pwd_hash, password), fetch_one=True)

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
        res = execute_query(sql, (username, pwd_hash, nombre_completo, rol), commit=True)
        try:
            u_row = execute_query("SELECT TOP 1 id FROM usuarios WHERE username = ? ORDER BY id DESC", (username,), fetch_one=True)
            if u_row:
                u_id = u_row["id"]
                r_str = str(rol).strip()
                def_perms = DEFAULT_ROLE_PERMISSIONS.get(r_str)
                if not def_perms:
                    r_l = r_str.lower()
                    if "almacen" in r_l or "almacén" in r_l:
                        def_perms = DEFAULT_ROLE_PERMISSIONS["Almacen"]
                    elif "cajero" in r_l:
                        def_perms = DEFAULT_ROLE_PERMISSIONS["Cajero"]
                    elif "vendedor" in r_l:
                        def_perms = DEFAULT_ROLE_PERMISSIONS["Vendedor"]
                    elif "manager" in r_l or "supervisor" in r_l:
                        def_perms = DEFAULT_ROLE_PERMISSIONS["Manager"]
                    else:
                        def_perms = DEFAULT_ROLE_PERMISSIONS["Cajero"]
                UserModel.save_permissions(u_id, def_perms)
        except Exception as e:
            print("Auto-seeding default permissions note:", e)
        return res

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
        if isinstance(user_id, dict):
            user_id = user_id.get("id")
        if not user_id:
            return {}
        sql = "SELECT modulo_clave, permitido FROM permisos_usuario WHERE usuario_id = ?"
        rows = execute_query(sql, (user_id,), fetch_all=True) or []
        res = {}
        for r in rows:
            res[r["modulo_clave"]] = bool(r["permitido"])
        return res

    @staticmethod
    def save_permissions(user_id, permissions_dict):
        if isinstance(user_id, dict):
            user_id = user_id.get("id")
        del_sql = "DELETE FROM permisos_usuario WHERE usuario_id = ?"
        execute_query(del_sql, (user_id,), commit=True)
        for mod, perm in permissions_dict.items():
            ins_sql = "INSERT INTO permisos_usuario (usuario_id, modulo_clave, permitido) VALUES (?, ?, ?)"
            execute_query(ins_sql, (user_id, mod, 1 if perm else 0), commit=True)

    @staticmethod
    def has_permission(user_or_id, modulo_clave, user_role=None):
        if isinstance(user_or_id, dict):
            user_id = user_or_id.get("id")
            if not user_role:
                user_role = user_or_id.get("rol")
        else:
            user_id = user_or_id

        if user_role in ["Admin", "Programador", "Propietario"]:
            return True

        perms = UserModel.get_permissions(user_id)

        key_aliases = {
            "pos": ["pos"],
            "productos": ["productos", "inventory"],
            "inventory": ["inventory", "inventario", "productos"],
            "inventario": ["inventory", "inventario", "productos"],
            "clientes": ["clientes", "backoffice"],
            "caja": ["caja", "cajas"],
            "cajas": ["caja", "cajas"],
            "reports": ["reports", "reportes"],
            "reportes": ["reports", "reportes"],
            "usuarios": ["usuarios", "backoffice"],
            "tienda": ["tienda", "backoffice"],
            "backup": ["backup", "backoffice"],
            "backoffice": ["backoffice", "productos", "clientes", "usuarios", "tienda", "backup"]
        }

        keys_to_check = key_aliases.get(modulo_clave, [modulo_clave])

        if perms:
            for k in keys_to_check:
                if k in perms:
                    return bool(perms[k])

        default_map = DEFAULT_ROLE_PERMISSIONS.get(user_role)
        if not default_map:
            r_str = str(user_role).lower()
            if "almacen" in r_str or "almacén" in r_str:
                default_map = DEFAULT_ROLE_PERMISSIONS["Almacen"]
            elif "cajero" in r_str:
                default_map = DEFAULT_ROLE_PERMISSIONS["Cajero"]
            elif "vendedor" in r_str:
                default_map = DEFAULT_ROLE_PERMISSIONS["Vendedor"]
            elif "manager" in r_str or "supervisor" in r_str:
                default_map = DEFAULT_ROLE_PERMISSIONS["Manager"]
            else:
                default_map = DEFAULT_ROLE_PERMISSIONS["Cajero"]

        for k in keys_to_check:
            if k in default_map:
                return bool(default_map[k])

        return False

class CustomerModel:
    @staticmethod
    def get_all(query="", search_term=""):
        q = query or search_term
        if q:
            sql = "SELECT * FROM clientes WHERE codigo LIKE ? OR nombre_razon_social LIKE ? OR rnc_cedula LIKE ? ORDER BY id ASC"
            term = f"%{q}%"
            return execute_query(sql, (term, term, term), fetch_all=True)
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
    def get_by_department(dept_id=None):
        return DepartmentModel.get_all()

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
    def get_by_department(dept_id=None):
        return SubDepartmentModel.get_all(dept_id)

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
            sql = "SELECT p.*, s.nombre as subdepartamento_nombre, d.nombre as departamento_nombre FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id LEFT JOIN departamentos d ON s.departamento_id = d.id WHERE p.codigo_barras LIKE ? OR p.nombre LIKE ? ORDER BY p.id ASC"
            q = f"%{query}%"
            return execute_query(sql, (q, q), fetch_all=True)
        sql = "SELECT p.*, s.nombre as subdepartamento_nombre, d.nombre as departamento_nombre FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id LEFT JOIN departamentos d ON s.departamento_id = d.id ORDER BY p.id ASC"
        res = execute_query(sql, fetch_all=True)
        if not query:
            _PROD_CACHE = res
        return res

    @staticmethod
    def search_live(term="", limit=100, active_only=True, subdep_id=None):
        sql = "SELECT TOP (?) p.*, s.nombre as subdepartamento_nombre, d.nombre as departamento_nombre, d.id as departamento_id FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id LEFT JOIN departamentos d ON s.departamento_id = d.id WHERE 1=1"
        params = [limit]
        if term:
            sql += " AND (p.codigo_barras LIKE ? OR p.nombre LIKE ?)"
            q = f"%{term}%"
            params.extend([q, q])
        if subdep_id:
            sql += " AND p.subdepartamento_id = ?"
            params.append(subdep_id)
        sql += " ORDER BY p.nombre ASC"
        return execute_query(sql, tuple(params), fetch_all=True) or []

    @staticmethod
    def get_by_id(prod_id):
        sql = "SELECT p.*, s.nombre as subdepartamento_nombre, d.nombre as departamento_nombre, d.id as departamento_id FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id LEFT JOIN departamentos d ON s.departamento_id = d.id WHERE p.id = ?"
        return execute_query(sql, (prod_id,), fetch_one=True)

    @staticmethod
    def get_by_barcode(codigo_barras):
        sql = "SELECT * FROM productos WHERE codigo_barras = ?"
        return execute_query(sql, (codigo_barras,), fetch_one=True)

    @staticmethod
    def get_by_codigo(codigo_barras):
        return ProductModel.get_by_barcode(codigo_barras)

    @staticmethod
    def get_by_subdepartment(subdep_id):
        sql = "SELECT * FROM productos WHERE subdepartamento_id = ? ORDER BY nombre ASC"
        return execute_query(sql, (subdep_id,), fetch_all=True)

    @staticmethod
    def get_categories():
        sql = "SELECT * FROM categorias ORDER BY nombre ASC"
        return execute_query(sql, fetch_all=True) or []

    @staticmethod
    def get_low_stock_products():
        sql = "SELECT * FROM productos WHERE stock_actual <= stock_minimo ORDER BY stock_actual ASC"
        return execute_query(sql, fetch_all=True)

    @staticmethod
    def save_product(data):
        clear_models_cache()
        prod_id = data.get("id")
        cb = data.get("codigo_barras")
        nom = data.get("nombre")
        sub_id = data.get("subdepartamento_id")
        pc = float(data.get("precio_costo", 0))
        pv = float(data.get("precio_venta", 0))
        sa = int(data.get("stock_actual", 0))
        sm = int(data.get("stock_minimo", 5))
        fv = data.get("fecha_vencimiento")
        es_desc = 1 if data.get("es_descontable", True) else 0
        prec_man = 1 if data.get("precio_manual", False) else 0
        unid = data.get("unidad_medida", "UD")
        est = data.get("estado", "Activo")

        if prod_id:
            sql = """
                UPDATE productos 
                SET codigo_barras = ?, nombre = ?, subdepartamento_id = ?, 
                    precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?, 
                    fecha_vencimiento = ?, es_descontable = ?, precio_manual = ?, 
                    unidad_medida = ?, estado = ?
                WHERE id = ?
            """
            return execute_query(sql, (cb, nom, sub_id, pc, pv, sa, sm, fv, es_desc, prec_man, unid, est, prod_id), commit=True)
        else:
            sql = """
                INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento, es_descontable, precio_manual, unidad_medida, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            return execute_query(sql, (cb, nom, sub_id, pc, pv, sa, sm, fv, es_desc, prec_man, unid, est), commit=True)

    @staticmethod
    def create(codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento=None, es_descontable=1, precio_manual=0, unidad_medida="UD", estado="Activo"):
        return ProductModel.save_product({
            "codigo_barras": codigo_barras,
            "nombre": nombre,
            "subdepartamento_id": subdepartamento_id,
            "precio_costo": precio_costo,
            "precio_venta": precio_venta,
            "stock_actual": stock_actual,
            "stock_minimo": stock_minimo,
            "fecha_vencimiento": fecha_vencimiento,
            "es_descontable": es_descontable,
            "precio_manual": precio_manual,
            "unidad_medida": unidad_medida,
            "estado": estado
        })

    @staticmethod
    def update(prod_id, codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento=None, es_descontable=1, precio_manual=0, unidad_medida="UD", estado="Activo"):
        return ProductModel.save_product({
            "id": prod_id,
            "codigo_barras": codigo_barras,
            "nombre": nombre,
            "subdepartamento_id": subdepartamento_id,
            "precio_costo": precio_costo,
            "precio_venta": precio_venta,
            "stock_actual": stock_actual,
            "stock_minimo": stock_minimo,
            "fecha_vencimiento": fecha_vencimiento,
            "es_descontable": es_descontable,
            "precio_manual": precio_manual,
            "unidad_medida": unidad_medida,
            "estado": estado
        })

    @staticmethod
    def delete(prod_id):
        clear_models_cache()
        sql = "DELETE FROM productos WHERE id = ?"
        return execute_query(sql, (prod_id,), commit=True)

    @staticmethod
    def delete_product(prod_id):
        return ProductModel.delete(prod_id)

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
    def get_active_caja(user_id=None):
        return CajaModel.get_active(user_id)

    @staticmethod
    def abrir(user_id, monto_inicial):
        sql = "INSERT INTO cajas (usuario_id, monto_inicial, fecha_apertura, estado) VALUES (?, ?, GETDATE(), 'Abierta')"
        return execute_query(sql, (user_id, monto_inicial), commit=True)

    @staticmethod
    def abrir_caja(user_id, monto_inicial):
        CajaModel.abrir(user_id, monto_inicial)
        return CajaModel.get_active(user_id)

    @staticmethod
    def cerrar(caja_id, monto_final_real):
        sql = "UPDATE cajas SET monto_final_real = ?, fecha_cierre = GETDATE(), estado = 'Cerrada' WHERE id = ?"
        return execute_query(sql, (monto_final_real, caja_id), commit=True)

    @staticmethod
    def cerrar_caja(caja_id, monto_final_real):
        return CajaModel.cerrar(caja_id, monto_final_real)

    @staticmethod
    def get_all():
        sql = "SELECT * FROM cajas ORDER BY id DESC"
        return execute_query(sql, fetch_all=True)

class VentaModel:
    @staticmethod
    def create(codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total, items):
        clear_models_cache()
        now_dt = datetime.datetime.now()
        sql_v = """
            INSERT INTO ventas (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis_impuesto, total, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(sql_v, (codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total, now_dt), commit=True)
        
        sql_last = "SELECT TOP 1 id FROM ventas WHERE codigo_factura = ?"
        v_row = execute_query(sql_last, (codigo_factura,), fetch_one=True)
        if not v_row:
            return None
        venta_id = v_row["id"]

        norm_items = []
        for item in items:
            p_id = item.get("id") or item.get("producto_id")
            qty = int(item.get("qty") or item.get("cantidad", 1))
            p_unit = float(item.get("price") or item.get("precio_venta") or item.get("precio_unitario", 0))
            p_cost = float(item.get("precio_costo", 0))
            desc = float(item.get("descuento", 0))
            item_name = item.get("nombre") or item.get("producto_nombre", "Producto")
            item_sub = (qty * p_unit) - desc

            sql_d = """
                INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, precio_costo, descuento, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            execute_query(sql_d, (venta_id, p_id, qty, p_unit, p_cost, desc, item_sub), commit=True)
            ProductModel.update_stock(p_id, -qty)

            norm_items.append({
                "producto_id": p_id,
                "id": p_id,
                "nombre": item_name,
                "producto_nombre": item_name,
                "cantidad": qty,
                "qty": qty,
                "precio_unitario": p_unit,
                "precio_venta": p_unit,
                "price": p_unit,
                "precio_costo": p_cost,
                "descuento": desc,
                "subtotal": item_sub
            })

        return {
            "id": venta_id,
            "codigo_factura": codigo_factura,
            "caja_id": caja_id,
            "usuario_id": usuario_id,
            "cliente_nombre": cliente_nombre,
            "tipo_pago": tipo_pago,
            "subtotal": float(subtotal),
            "itbis": float(itbis),
            "itbis_impuesto": float(itbis),
            "total": float(total),
            "fecha": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "items": norm_items
        }

    @staticmethod
    def procesar_venta(*args, **kwargs):
        """Flexible adapter handling both dictionary and positional call styles."""
        if len(args) == 1 and isinstance(args[0], dict):
            sale_data = args[0]
            caja_id = sale_data.get("caja_id")
            usuario_id = sale_data.get("usuario_id")
            cliente_nombre = sale_data.get("cliente_nombre", "Cliente General")
            tipo_pago = sale_data.get("tipo_pago", "Efectivo")
            items = sale_data.get("items", [])
            codigo_factura = sale_data.get("codigo_factura")
            subtotal = sale_data.get("subtotal")
            itbis = sale_data.get("itbis") or sale_data.get("itbis_impuesto")
            total = sale_data.get("total")
        elif len(args) == 5:
            caja_id, usuario_id, cliente_nombre, tipo_pago, items = args
            codigo_factura = None
            subtotal = None
            itbis = None
            total = None
        elif len(args) >= 8:
            codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total = args[:8]
            items = args[8] if len(args) > 8 else []
        else:
            sale_data = kwargs
            caja_id = sale_data.get("caja_id")
            usuario_id = sale_data.get("usuario_id")
            cliente_nombre = sale_data.get("cliente_nombre", "Cliente General")
            tipo_pago = sale_data.get("tipo_pago", "Efectivo")
            items = sale_data.get("items", [])
            codigo_factura = sale_data.get("codigo_factura")
            subtotal = sale_data.get("subtotal")
            itbis = sale_data.get("itbis") or sale_data.get("itbis_impuesto")
            total = sale_data.get("total")

        if not codigo_factura:
            codigo_factura = f"FAC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        if subtotal is None or total is None:
            calc_subtotal = 0.0
            calc_itbis = 0.0
            for item in items:
                q = float(item.get("qty") or item.get("cantidad", 1))
                p = float(item.get("price") or item.get("precio_venta") or item.get("precio_unitario", 0))
                d = float(item.get("descuento", 0))
                calc_subtotal += (q * p) - d
                calc_itbis += float(item.get("itbis", (q * p - d) * 0.18))

            subtotal = calc_subtotal
            if itbis is None:
                itbis = calc_itbis
            total = subtotal + itbis

        return VentaModel.create(codigo_factura, caja_id, usuario_id, cliente_nombre, tipo_pago, subtotal, itbis, total, items)

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
        
        if tipo_mov in ["Entrada Suplidor", "Entrada"]:
            ProductModel.update_stock(prod_id, cantidad)
        elif tipo_mov in ["Salida/Ajuste", "Mermas/Vencido", "Salida"]:
            ProductModel.update_stock(prod_id, -abs(cantidad))
        return res

    @staticmethod
    def registrar_movimiento(prod_id, tipo_mov, cantidad, motivo="", user_id=None):
        return InventoryMovementModel.log(prod_id, tipo_mov, cantidad, motivo, user_id)

    @staticmethod
    def get_all(prod_id=None):
        if prod_id:
            sql = "SELECT m.*, p.nombre as producto_nombre FROM movimientos_inventario m JOIN productos p ON m.producto_id = p.id WHERE m.producto_id = ? ORDER BY m.id DESC"
            return execute_query(sql, (prod_id,), fetch_all=True)
        sql = "SELECT m.*, p.nombre as producto_nombre FROM movimientos_inventario m JOIN productos p ON m.producto_id = p.id ORDER BY m.id DESC"
        return execute_query(sql, fetch_all=True)

class ReportModel:
    @staticmethod
    def _parse_dates(start_date, end_date):
        params = []
        where_clause = ""
        s_str = None
        e_str = None

        if start_date:
            s_s = str(start_date).strip()
            if len(s_s) == 10:
                s_str = f"{s_s} 00:00:00"
            else:
                s_str = s_s

        if end_date:
            e_s = str(end_date).strip()
            if len(e_s) == 10:
                e_str = f"{e_s} 23:59:59"
            else:
                e_str = e_s

        if s_str and e_str:
            where_clause = " WHERE v.fecha >= ? AND v.fecha <= ?"
            params = [s_str, e_str]
        elif s_str:
            where_clause = " WHERE v.fecha >= ?"
            params = [s_str]
        elif e_str:
            where_clause = " WHERE v.fecha <= ?"
            params = [e_str]

        return where_clause, params

    @staticmethod
    def get_sales_summary(start_date=None, end_date=None):
        where, params = ReportModel._parse_dates(start_date, end_date)
        sql = f"SELECT COUNT(*) as total_ventas, SUM(total) as monto_total, SUM(subtotal) as subtotal, SUM(itbis_impuesto) as total_itbis FROM ventas v{where}"
        res = execute_query(sql, tuple(params), fetch_one=True)
        return res or {"total_ventas": 0, "monto_total": 0, "subtotal": 0, "total_itbis": 0}

    @staticmethod
    def get_dashboard_metrics(start_date=None, end_date=None):
        v_res = ReportModel.get_sales_summary(start_date, end_date)
        p_res = execute_query("SELECT COUNT(*) as total_prods FROM productos", fetch_one=True)
        c_res = execute_query("SELECT COUNT(*) as total_clientes FROM clientes", fetch_one=True)
        return {
            "total_ventas": v_res.get("total_ventas", 0) if v_res else 0,
            "monto_total": float(v_res.get("monto_total", 0) or 0) if v_res else 0,
            "total_productos": p_res.get("total_prods", 0) if p_res else 0,
            "total_clientes": c_res.get("total_clientes", 0) if c_res else 0
        }

    @staticmethod
    def get_executive_summary(start_date=None, end_date=None):
        where, params = ReportModel._parse_dates(start_date, end_date)
        sql_summary = f"""
            SELECT 
                COUNT(*) as total_tx,
                ISNULL(SUM(v.subtotal), 0) as total_sub,
                ISNULL(SUM(v.itbis_impuesto), 0) as total_itb,
                ISNULL(SUM(v.total), 0) as total_ing
            FROM ventas v
            {where}
        """
        row_s = execute_query(sql_summary, tuple(params), fetch_one=True) or {}

        sql_cost = f"""
            SELECT ISNULL(SUM(dv.cantidad * dv.precio_costo), 0) as total_cost
            FROM detalle_ventas dv
            JOIN ventas v ON dv.venta_id = v.id
            {where}
        """
        row_c = execute_query(sql_cost, tuple(params), fetch_one=True) or {}

        tx = row_s.get("total_tx", 0)
        sub = float(row_s.get("total_sub") or 0)
        itb = float(row_s.get("total_itb") or 0)
        ing = float(row_s.get("total_ing") or 0)
        cost = float(row_c.get("total_cost") or 0)

        ganancia = sub - cost
        ticket_avg = (ing / tx) if tx > 0 else 0.0

        p_res = execute_query("SELECT COUNT(*) as total_prods FROM productos", fetch_one=True)
        c_res = execute_query("SELECT COUNT(*) as total_clientes FROM clientes", fetch_one=True)

        return {
            "total_transacciones": tx,
            "total_ventas": tx,
            "total_ingresos": ing,
            "monto_total": ing,
            "total_subtotal": sub,
            "total_itbis": itb,
            "costo_total_estimado": cost,
            "ganancia_estimada": ganancia,
            "ticket_promedio": ticket_avg,
            "total_productos": p_res.get("total_prods", 0) if p_res else 0,
            "total_clientes": c_res.get("total_clientes", 0) if c_res else 0
        }

    @staticmethod
    def get_electronic_journal(start_date=None, end_date=None):
        where, params = ReportModel._parse_dates(start_date, end_date)
        sql = f"""
            SELECT v.*, u.nombre_completo as usuario_nombre 
            FROM ventas v 
            LEFT JOIN usuarios u ON v.usuario_id = u.id 
            {where}
            ORDER BY v.id DESC
        """
        return execute_query(sql, tuple(params), fetch_all=True) or []

    @staticmethod
    def get_multi_total_store_report(start_date=None, end_date=None):
        where, params = ReportModel._parse_dates(start_date, end_date)
        sql_pay = f"""
            SELECT 
                ISNULL(v.tipo_pago, 'Efectivo') as tipo_pago,
                COUNT(*) as total_operaciones,
                ISNULL(SUM(v.subtotal), 0) as subtotal,
                ISNULL(SUM(v.itbis_impuesto), 0) as itbis,
                ISNULL(SUM(v.total), 0) as total_monto
            FROM ventas v
            {where}
            GROUP BY v.tipo_pago
        """
        by_payment = execute_query(sql_pay, tuple(params), fetch_all=True) or []

        sql_usr = f"""
            SELECT 
                ISNULL(u.nombre_completo, 'Cajero General') as cajero,
                COUNT(*) as total_ventas,
                ISNULL(SUM(v.total), 0) as total_monto
            FROM ventas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            {where}
            GROUP BY u.nombre_completo
        """
        by_user = execute_query(sql_usr, tuple(params), fetch_all=True) or []

        return {
            "by_payment": by_payment,
            "by_user": by_user
        }

    @staticmethod
    def get_department_subdepartment_sales(start_date=None, end_date=None):
        where, params = ReportModel._parse_dates(start_date, end_date)
        sql = f"""
            SELECT 
                ISNULL(d.nombre, 'Sin Departamento') as departamento,
                ISNULL(s.nombre, 'General') as subdepartamento,
                SUM(dv.cantidad) as unidades_vendidas,
                SUM(dv.subtotal) as total_bruto,
                SUM(dv.subtotal * 0.18) as itbis_estimado,
                SUM(dv.subtotal * 1.18) as total_neto,
                SUM(dv.subtotal - (dv.cantidad * dv.precio_costo)) as ganancia_estimada
            FROM detalle_ventas dv
            JOIN ventas v ON dv.venta_id = v.id
            JOIN productos p ON dv.producto_id = p.id
            LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id
            LEFT JOIN departamentos d ON s.departamento_id = d.id
            {where}
            GROUP BY d.nombre, s.nombre
            ORDER BY total_bruto DESC
        """
        return execute_query(sql, tuple(params), fetch_all=True) or []

    @staticmethod
    def get_inventory_valuation_report():
        sql_prods = """
            SELECT 
                p.id,
                p.codigo_barras,
                p.nombre,
                ISNULL(s.nombre, 'Sin Categoria') as subdepartamento_nombre,
                p.stock_actual,
                p.stock_minimo,
                p.precio_costo,
                p.precio_venta,
                (p.stock_actual * p.precio_costo) as valor_costo,
                (p.stock_actual * p.precio_venta) as valor_venta
            FROM productos p
            LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id
            ORDER BY p.nombre ASC
        """
        details = execute_query(sql_prods, fetch_all=True) or []

        tot_prods = len(details)
        costo_tot = sum(float(r.get("valor_costo") or 0) for r in details)
        venta_tot = sum(float(r.get("valor_venta") or 0) for r in details)
        ganancia_pot = venta_tot - costo_tot
        cant_agotados = sum(1 for r in details if (r.get("stock_actual") or 0) <= 0)
        cant_stock_bajo = sum(1 for r in details if 0 < (r.get("stock_actual") or 0) <= (r.get("stock_minimo") or 5))

        summary = {
            "total_productos": tot_prods,
            "valor_costo_total": costo_tot,
            "valor_venta_total": venta_tot,
            "ganancia_potencial": ganancia_pot,
            "cant_agotados": cant_agotados,
            "cant_stock_bajo": cant_stock_bajo
        }

        return {
            "summary": summary,
            "details": details
        }

    @staticmethod
    def get_date_range_bounds():
        sql = "SELECT MIN(fecha) as min_date, MAX(fecha) as max_date FROM ventas"
        res = execute_query(sql, fetch_one=True)
        if not res or not res.get("min_date"):
            now_str = datetime.datetime.now().strftime("%Y-%m-%d")
            return {"min_date": now_str, "max_date": now_str}
        min_d = str(res["min_date"])[:10]
        max_d = str(res["max_date"])[:10]
        return {"min_date": min_d, "max_date": max_d}
