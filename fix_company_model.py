import os

with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_company_model = """class CompanyModel:
    @staticmethod
    def get():
        try:
            sql = "SELECT * FROM configuracion_empresa WHERE id = 1"
            res = execute_query(sql, fetch_one=True)
            if res and res.get("nombre_comercial"):
                return res
            
            # Seed row 1 if table is empty or missing row
            default_data = {
                "id": 1, "rnc": "101-00000-1",
                "nombre_comercial": "Minimarket La Ruta del Este",
                "telefono": "(809) 555-0199",
                "direccion": "Av. Principal #45, La Altagracia",
                "mensaje_factura": "¡Gracias por su compra! Vuelva pronto."
            }
            try:
                seed_sql = \"\"\"
                    INSERT INTO configuracion_empresa (id, rnc, nombre_comercial, telefono, direccion, mensaje_factura)
                    VALUES (1, ?, ?, ?, ?, ?)
                \"\"\"
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
                sql = \"\"\"
                    UPDATE configuracion_empresa 
                    SET rnc = ?, nombre_comercial = ?, telefono = ?, direccion = ?, mensaje_factura = ?
                    WHERE id = 1
                \"\"\"
                return execute_query(sql, (rnc, nombre_comercial, telefono, direccion, mensaje_factura), commit=True)
            else:
                sql = \"\"\"
                    INSERT INTO configuracion_empresa (id, rnc, nombre_comercial, telefono, direccion, mensaje_factura)
                    VALUES (1, ?, ?, ?, ?, ?)
                \"\"\"
                return execute_query(sql, (rnc, nombre_comercial, telefono, direccion, mensaje_factura), commit=True)
        except Exception as e:
            print("Error in CompanyModel.update():", e)
            return False"""

# Replace CompanyModel in models.py
start_marker = "class CompanyModel:"
end_marker = "_DEPT_CACHE = None"

if start_marker in code and end_marker in code:
    pre = code.split(start_marker)[0]
    post = code.split(end_marker)[1]
    new_code = pre + new_company_model + "\n\n" + end_marker + post
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("models.py updated with robust CompanyModel get/update!")
else:
    print("Markers not found in models.py")
