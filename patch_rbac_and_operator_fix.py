"""Patch models.py and app_gui.py to resolve Operator saving error and Permission key mismatch."""
import re

print("=== APPLYING RBAC & OPERATOR SAVE FIXES ===")

# 1. Update models.py
with open('models.py', 'r', encoding='utf-8') as f:
    m_code = f.read()

# Update ALL_MODULES in models.py
old_all_modules = """ALL_MODULES = [
    ("pos", "Punto de Venta (Caja)"),
    ("productos", "Gestión de Productos"),
    ("inventario", "Control de Inventario & Stock"),
    ("clientes", "Gestión de Clientes"),
    ("usuarios", "Gestión de Usuarios & Roles"),
    ("cajas", "Apertura / Cierre de Cajas"),
    ("reportes", "Reportes de Ventas & Exportación"),
    ("backoffice", "Back Office & Ajustes Avanzados")
]"""

new_all_modules = """ALL_MODULES = [
    ("pos", "Punto de Venta (Caja)"),
    ("inventory", "Control de Inventario & Stock"),
    ("caja", "Apertura / Cierre de Cajas"),
    ("reports", "Reportes de Ventas & Exportación"),
    ("backoffice", "Back Office & Ajustes Avanzados")
]"""

m_code = m_code.replace(old_all_modules, new_all_modules)

# Update UserModel.has_permission in models.py
old_has_perm = """    @staticmethod
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
        if not perms:
            return True
        return perms.get(modulo_clave, True)"""

new_has_perm = """    @staticmethod
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
        if not perms:
            return True

        key_aliases = {
            "inventory": ["inventory", "inventario", "productos"],
            "inventario": ["inventory", "inventario", "productos"],
            "caja": ["caja", "cajas"],
            "cajas": ["caja", "cajas"],
            "reports": ["reports", "reportes"],
            "reportes": ["reports", "reportes"],
            "backoffice": ["backoffice", "usuarios"]
        }

        keys_to_check = key_aliases.get(modulo_clave, [modulo_clave])
        for k in keys_to_check:
            if k in perms:
                return bool(perms[k])

        return True"""

m_code = m_code.replace(old_has_perm, new_has_perm)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(m_code)

print("[1] models.py patched successfully!")

# 2. Update app_gui.py
with open('app_gui.py', 'r', encoding='utf-8') as f:
    g_code = f.read()

old_save_bo_op = """        try:
            if self._bo_editing_user_id:
                UserModel.update(self._bo_editing_user_id, p, nom, rol, activo)
            else:
                UserModel.create(u, p, nom, rol)"""

new_save_bo_op = """        try:
            if self._bo_editing_user_id:
                UserModel.update(user_id=self._bo_editing_user_id, nombre_completo=nom, rol=rol, password=p if p else None, activo=activo)
            else:
                UserModel.create(username=u, password=p, nombre_completo=nom, rol=rol)"""

g_code = g_code.replace(old_save_bo_op, new_save_bo_op)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(g_code)

print("[2] app_gui.py patched successfully!")
print("=== RBAC & OPERATOR SAVE FIXES COMPLETE ===")
