import re, ast

with open("app_gui.py", "r", encoding="utf-8") as f:
    gui_code = f.read()

model_names = ['UserModel', 'CustomerModel', 'CompanyModel', 'DepartmentModel', 'SubDepartmentModel', 'ProductModel', 'CajaModel', 'VentaModel', 'InventoryMovementModel', 'ReportModel']

for m in model_names:
    pattern = rf"{m}\.([a-zA-Z0-9_]+)"
    matches = set(re.findall(pattern, gui_code))
    print(f"\n{m} methods called in app_gui.py:")
    for func in sorted(matches):
        print(f"  - {m}.{func}")
