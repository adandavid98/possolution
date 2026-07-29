"""Script to update Almacen default role permissions in models.py and sync active Almacen users in DB."""
import sys
sys.path.insert(0, '.')
import re
from models import UserModel, DEFAULT_ROLE_PERMISSIONS
from database import execute_query

print("=== UPDATING ALMACEN ROLE PERMISSIONS ===")

# 1. Update models.py
with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_almacen_block = '''    "Almacen": {
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
    },'''

code = re.sub(r'    "Almacen": \{.*?\},\n', new_almacen_block + '\n', code, flags=re.DOTALL)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("[1] models.py updated with new Almacen default permissions!")

# 2. Re-import models to verify
import importlib
import models
importlib.reload(models)

print("[2] Verified DEFAULT_ROLE_PERMISSIONS['Almacen']:", models.DEFAULT_ROLE_PERMISSIONS["Almacen"])

# 3. Sync existing users in DB with role Almacen
almacen_users = execute_query("SELECT id, username, nombre_completo FROM usuarios WHERE LOWER(rol) LIKE '%almacen%' OR LOWER(rol) LIKE '%almacén%'", fetch_all=True) or []
for u in almacen_users:
    u_id = u["id"]
    print(f"[3] Updating DB permissions for Almacen user #{u_id} ({u['nombre_completo']})...")
    models.UserModel.save_permissions(u_id, models.DEFAULT_ROLE_PERMISSIONS["Almacen"])
    updated_perms = models.UserModel.get_permissions(u_id)
    print(f"    Updated permissions for user #{u_id}: {updated_perms}")

print("=== ALMACEN PERMISSIONS UPDATE COMPLETE ===")
