"""Patch models.py and app_gui.py to restore full granular permissions for ALL modules and sub-tabs."""
import re

print("=== RESTORING FULL GRANULAR RBAC PERMISSIONS ===")

# 1. Update models.py
with open('models.py', 'r', encoding='utf-8') as f:
    m_code = f.read()

# Update ALL_MODULES to full list
old_all_modules = """ALL_MODULES = [
    ("pos", "Punto de Venta (Caja)"),
    ("inventory", "Control de Inventario & Stock"),
    ("caja", "Apertura / Cierre de Cajas"),
    ("reports", "Reportes de Ventas & Exportación"),
    ("backoffice", "Back Office & Ajustes Avanzados")
]"""

new_all_modules = """ALL_MODULES = [
    ("pos", "🛒 Punto de Venta (Caja & Cobros)"),
    ("productos", "🏷️ Mantenimiento de Artículos & Catálogo"),
    ("inventory", "📦 Control de Inventario, Stock & Mermas"),
    ("clientes", "👥 Gestión de Clientes & Proveedores"),
    ("caja", "💵 Apertura / Cierre & Arqueo de Cajas"),
    ("reports", "📊 Reportes de Ventas & Exportación PDF/Excel"),
    ("usuarios", "🔐 Gestión de Operadores & Permisos RBAC"),
    ("tienda", "🏬 Configuración General de la Tienda"),
    ("backup", "💾 Respaldo y Restauración de Base de Datos")
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
        for k in keys_to_check:
            if k in perms:
                return bool(perms[k])

        return True"""

m_code = m_code.replace(old_has_perm, new_has_perm)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(m_code)

print("[1] models.py updated with full granular permission list and aliases!")

# 2. Update app_gui.py Back Office sub-tabs permission filtering
with open('app_gui.py', 'r', encoding='utf-8') as f:
    g_code = f.read()

old_bo_subtabs = """        self._tab_item_maint = self._bo_tabview.add("🏷️ Mantenimiento Artículos")
        self._tab_customers  = self._bo_tabview.add("👥 Clientes & Proveedores")
        self._tab_operators  = self._bo_tabview.add("🔒 Operadores & Permisos (RBAC)")
        self._tab_store_cfg  = self._bo_tabview.add("🏬 Datos de la Tienda")
        self._tab_backup_cfg = self._bo_tabview.add("💾 Respaldo y Restauración SQL")

        # Load Sub-tabs with fault isolation
        try:
            self._load_bo_item_maintenance(self._tab_item_maint)
        except Exception as e:
            print("Error loading item maintenance subtab:", e)

        try:
            self._load_bo_customers(self._tab_customers)
        except Exception as e:
            print("Error loading customers subtab:", e)

        try:
            self._load_bo_operators(self._tab_operators)
        except Exception as e:
            print("Error loading operators subtab:", e)

        try:
            self._load_bo_store_config(self._tab_store_cfg)
        except Exception as e:
            print("Error loading store config subtab:", e)

        try:
            self._load_bo_backup_restore(self._tab_backup_cfg)
        except Exception as e:
            print("Error loading backup restore subtab:", e)"""

new_bo_subtabs = """        if UserModel.has_permission(self.current_user, "productos"):
            self._tab_item_maint = self._bo_tabview.add("🏷️ Mantenimiento Artículos")
            try:
                self._load_bo_item_maintenance(self._tab_item_maint)
            except Exception as e:
                print("Error loading item maintenance subtab:", e)

        if UserModel.has_permission(self.current_user, "clientes"):
            self._tab_customers = self._bo_tabview.add("👥 Clientes & Proveedores")
            try:
                self._load_bo_customers(self._tab_customers)
            except Exception as e:
                print("Error loading customers subtab:", e)

        if UserModel.has_permission(self.current_user, "usuarios"):
            self._tab_operators = self._bo_tabview.add("🔒 Operadores & Permisos (RBAC)")
            try:
                self._load_bo_operators(self._tab_operators)
            except Exception as e:
                print("Error loading operators subtab:", e)

        if UserModel.has_permission(self.current_user, "tienda"):
            self._tab_store_cfg = self._bo_tabview.add("🏬 Datos de la Tienda")
            try:
                self._load_bo_store_config(self._tab_store_cfg)
            except Exception as e:
                print("Error loading store config subtab:", e)

        if UserModel.has_permission(self.current_user, "backup"):
            self._tab_backup_cfg = self._bo_tabview.add("💾 Respaldo y Restauración SQL")
            try:
                self._load_bo_backup_restore(self._tab_backup_cfg)
            except Exception as e:
                print("Error loading backup restore subtab:", e)"""

g_code = g_code.replace(old_bo_subtabs, new_bo_subtabs)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(g_code)

print("[2] app_gui.py updated with granular sub-tab permission checks!")
print("=== FULL GRANULAR PERMISSIONS RESTORED SUCCESSFULLY ===")
