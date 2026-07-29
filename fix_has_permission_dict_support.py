with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_perm_block = """    @staticmethod
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
        return perms.get(modulo_clave, True)"""

new_perm_block = """    @staticmethod
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
        if not perms:
            return True
        return perms.get(modulo_clave, True)"""

if old_perm_block in code:
    code = code.replace(old_perm_block, new_perm_block)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("UserModel permissions methods updated in models.py!")
else:
    print("old_perm_block snippet not found in models.py")
