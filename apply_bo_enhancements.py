import re

# 1. Update database.py to add estado column migration to productos
with open('database.py', 'r', encoding='utf-8') as f:
    db_content = f.read()

target_col = "cursor.execute(\"IF COL_LENGTH('productos', 'unidad_medida') IS NULL ALTER TABLE productos ADD unidad_medida VARCHAR(20) DEFAULT 'UD';\")"
replacement_col = target_col + "\n    cursor.execute(\"IF COL_LENGTH('productos', 'estado') IS NULL ALTER TABLE productos ADD estado VARCHAR(20) DEFAULT 'Activo';\")"

if target_col in db_content and "IF COL_LENGTH('productos', 'estado')" not in db_content:
    db_content = db_content.replace(target_col, replacement_col)
    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(db_content)
    print("database.py updated.")

# 2. Update models.py for UserModel.delete, ProductModel active filtering & estado parameter
with open('models.py', 'r', encoding='utf-8') as f:
    mod_content = f.read()

# Add UserModel.delete
old_user_update = """            sql = "UPDATE usuarios SET nombre_completo = ?, rol = ?, activo = ? WHERE id = ?"
            return execute_query(sql, (nombre_completo, rol, activo, user_id), commit=True)"""

new_user_update = old_user_update + """

    @staticmethod
    def delete(user_id):
        execute_query("DELETE FROM permisos_usuario WHERE usuario_id = ?", (user_id,), commit=True)
        sql = "DELETE FROM usuarios WHERE id = ?"
        return execute_query(sql, (user_id,), commit=True)"""

if old_user_update in mod_content and "def delete(user_id):" not in mod_content:
    mod_content = mod_content.replace(old_user_update, new_user_update)

# Update ProductModel.get_all for active_only
old_prod_get_all = """    @staticmethod
    def get_all(search_term="", subdep_id=None, dep_id=None):
        global _PROD_CACHE
        if not search_term and subdep_id is None and dep_id is None:
            if _PROD_CACHE is not None:
                return _PROD_CACHE"""

new_prod_get_all = """    @staticmethod
    def get_all(search_term="", subdep_id=None, dep_id=None, active_only=False):
        global _PROD_CACHE
        if not search_term and subdep_id is None and dep_id is None and not active_only:
            if _PROD_CACHE is not None:
                return _PROD_CACHE"""

if old_prod_get_all in mod_content:
    mod_content = mod_content.replace(old_prod_get_all, new_prod_get_all)

old_prod_cond = """        if dep_id:
            conditions.append("sd.departamento_id = ?")
            params.append(dep_id)"""

new_prod_cond = """        if dep_id:
            conditions.append("sd.departamento_id = ?")
            params.append(dep_id)

        if active_only:
            conditions.append("(p.estado IS NULL OR p.estado = 'Activo')")"""

if old_prod_cond in mod_content and "active_only:" not in mod_content:
    mod_content = mod_content.replace(old_prod_cond, new_prod_cond)

# Update ProductModel.save_product for estado
old_save_prod = """        subdep_id = data.get("subdepartamento_id", None)
        es_desc = 1 if data.get("es_descontable", True) else 0
        precio_man = 1 if data.get("precio_manual", False) else 0
        unidad = data.get("unidad_medida", "UD")

        if "id" in data and data["id"]:
            sql = \"\"\"
                UPDATE productos 
                SET codigo_barras = ?, nombre = ?, subdepartamento_id = ?, precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?, es_descontable = ?, precio_manual = ?, unidad_medida = ?
                WHERE id = ?
            \"\"\"
            params = (
                data["codigo_barras"], data["nombre"], subdep_id,
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"], es_desc, precio_man, unidad, data["id"]
            )
            execute_query(sql, params, commit=True)
            return data["id"]
        else:
            sql = \"\"\"
                INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, es_descontable, precio_manual, unidad_medida)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\"
            params = (
                data["codigo_barras"], data["nombre"], subdep_id,
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"], es_desc, precio_man, unidad
            )"""

new_save_prod = """        subdep_id = data.get("subdepartamento_id", None)
        es_desc = 1 if data.get("es_descontable", True) else 0
        precio_man = 1 if data.get("precio_manual", False) else 0
        unidad = data.get("unidad_medida", "UD")
        estado = data.get("estado", "Activo")

        if "id" in data and data["id"]:
            sql = \"\"\"
                UPDATE productos 
                SET codigo_barras = ?, nombre = ?, subdepartamento_id = ?, precio_costo = ?, precio_venta = ?, stock_actual = ?, stock_minimo = ?, es_descontable = ?, precio_manual = ?, unidad_medida = ?, estado = ?
                WHERE id = ?
            \"\"\"
            params = (
                data["codigo_barras"], data["nombre"], subdep_id,
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"], es_desc, precio_man, unidad, estado, data["id"]
            )
            execute_query(sql, params, commit=True)
            return data["id"]
        else:
            sql = \"\"\"
                INSERT INTO productos (codigo_barras, nombre, subdepartamento_id, precio_costo, precio_venta, stock_actual, stock_minimo, es_descontable, precio_manual, unidad_medida, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\"
            params = (
                data["codigo_barras"], data["nombre"], subdep_id,
                data["precio_costo"], data["precio_venta"], data["stock_actual"],
                data["stock_minimo"], es_desc, precio_man, unidad, estado
            )"""

if old_save_prod in mod_content:
    mod_content = mod_content.replace(old_save_prod, new_save_prod)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(mod_content)
print("models.py updated.")
