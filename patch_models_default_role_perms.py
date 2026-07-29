"""Patch models.py with complete DEFAULT_ROLE_PERMISSIONS including backoffice flag."""

with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

default_role_perms_code = '''DEFAULT_ROLE_PERMISSIONS = {
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
        "clientes": False,
        "reports": False,
        "usuarios": False,
        "tienda": False,
        "backup": False,
        "backoffice": False
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
'''

# Replace existing DEFAULT_ROLE_PERMISSIONS block if present
import re
code = re.sub(r'DEFAULT_ROLE_PERMISSIONS = \{.*?\n\}', default_role_perms_code.strip(), code, flags=re.DOTALL)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("models.py updated with complete DEFAULT_ROLE_PERMISSIONS including backoffice flag!")
