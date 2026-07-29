with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_caja_model = """class CajaModel:
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
        return execute_query(sql, fetch_all=True)"""

start_m = "class CajaModel:"
end_m = "class VentaModel:"

if start_m in code and end_m in code:
    pre = code.split(start_m)[0]
    post = code.split(end_m)[1]
    new_code = pre + new_caja_model + "\n\n" + end_m + post
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("CajaModel methods and aliases updated successfully in models.py!")
else:
    print("Markers not found in models.py")
