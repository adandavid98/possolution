with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_auth = """    @staticmethod
    def authenticate(username, password):
        pwd_hash = _hash_password(password)
        sql = "SELECT * FROM usuarios WHERE username = ? AND password_hash = ? AND (activo = 1 OR activo IS NULL)"
        return execute_query(sql, (username, pwd_hash), fetch_one=True)"""

new_auth = """    @staticmethod
    def authenticate(username, password):
        pwd_hash = _hash_password(password)
        sql = "SELECT * FROM usuarios WHERE username = ? AND (password_hash = ? OR password_hash = ?) AND (activo = 1 OR activo IS NULL)"
        return execute_query(sql, (username, pwd_hash, password), fetch_one=True)"""

if old_auth in code:
    code = code.replace(old_auth, new_auth)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("UserModel.authenticate updated to support both plaintext and hashed passwords!")
else:
    print("old_auth snippet not found in models.py")
