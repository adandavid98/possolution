"""Patch script to update ProductModel in models.py with full field persistence support."""
import re

with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Define updated ProductModel code block
old_product_model = """class ProductModel:
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
        sql = "SELECT TOP (?) p.*, s.nombre as subdepartamento_nombre FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id WHERE 1=1"
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
        sql = "SELECT * FROM productos WHERE id = ?"
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
    def create(codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento=None):
        clear_models_cache()
        sql = \"\"\"
            INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\"
        return execute_query(sql, (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento), commit=True)

    @staticmethod
    def save_product(data):
        clear_models_cache()
        prod_id = data.get("id")
        cb = data.get("codigo_barras")
        nom = data.get("nombre")
        sub_id = data.get("subdepartamento_id")
        pc = data.get("precio_costo", 0)
        pv = data.get("precio_venta", 0)
        sa = data.get("stock_actual", 0)
        sm = data.get("stock_minimo", 5)
        fv = data.get("fecha_vencimiento")
        if prod_id:
            sql = "UPDATE productos SET codigo_barras = ?, nombre = ?, subdepartamento_id = ?, precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?, fecha_vencimiento = ? WHERE id = ?"
            return execute_query(sql, (cb, nom, sub_id, pc, pv, sa, sm, fv, prod_id), commit=True)
        else:
            sql = "INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            return execute_query(sql, (cb, nom, sub_id, pc, pv, sa, sm, fv), commit=True)

    @staticmethod
    def update(prod_id, codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento=None):
        return ProductModel.save_product({"id": prod_id, "codigo_barras": codigo_barras, "nombre": nombre, "subdepartamento_id": subdepartamento_id, "precio_costo": precio_costo, "precio_venta": precio_venta, "stock_actual": stock_actual, "stock_minimo": stock_minimo, "fecha_vencimiento": fecha_vencimiento})

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
        return execute_query(sql, (delta_stock, prod_id), commit=True)"""

new_product_model = """class ProductModel:
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
        sql = "SELECT TOP (?) p.*, s.nombre as subdepartamento_nombre FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id WHERE 1=1"
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
        sql = "SELECT * FROM productos WHERE id = ?"
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
            sql = \"\"\"
                UPDATE productos 
                SET codigo_barras = ?, nombre = ?, subdepartamento_id = ?, 
                    precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?, 
                    fecha_vencimiento = ?, es_descontable = ?, precio_manual = ?, 
                    unidad_medida = ?, estado = ?
                WHERE id = ?
            \"\"\"
            return execute_query(sql, (cb, nom, sub_id, pc, pv, sa, sm, fv, es_desc, prec_man, unid, est, prod_id), commit=True)
        else:
            sql = \"\"\"
                INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, fecha_vencimiento, es_descontable, precio_manual, unidad_medida, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\"
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
        return execute_query(sql, (delta_stock, prod_id), commit=True)"""

if old_product_model in code:
    code = code.replace(old_product_model, new_product_model)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("models.py successfully patched with updated ProductModel!")
else:
    print("WARNING: Could not find exact old_product_model string in models.py, searching with regex...")
