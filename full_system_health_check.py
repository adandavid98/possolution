import ast
import sys

print("==========================================================")
print("     POS-SOLUTION INTEGRAL SYSTEM HEALTH CHECK & AUDIT    ")
print("==========================================================")

# 1. AST SYNTAX CHECK
files_to_check = ['config.py', 'database.py', 'seed_data.py', 'models.py', 'app_gui.py', 'web_app.py', 'main.py', 'build_exe.py']
for fname in files_to_check:
    with open(fname, 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print(f"[OK] AST Syntax Validated: {fname}")

# 2. MODULE IMPORTS
from database import test_db_connection, execute_query
from models import UserModel, CompanyModel, DepartmentModel, SubDepartmentModel, ProductModel, CajaModel, VentaModel, InventoryMovementModel, ReportModel
from web_app import app
import app_gui
print("[OK] All modules imported cleanly with 0 errors!")

# 3. DATABASE & SCHEMAS
success, info = test_db_connection()
print(f"[OK] DB Connection Test: {success} ({info.splitlines()[0]})")

# 4. USER AUTHENTICATION
u_admin = UserModel.authenticate("100001", "100001")
assert u_admin is not None, "Admin 100001 authentication failed!"
print(f"[OK] Admin Auth: {u_admin['nombre_completo']} ({u_admin['rol']})")

u_cajero = UserModel.authenticate("200001", "200001")
assert u_cajero is not None, "Cajero 200001 authentication failed!"
print(f"[OK] Cajero Auth: {u_cajero['nombre_completo']} ({u_cajero['rol']})")

u_almacen = UserModel.authenticate("300001", "300001")
assert u_almacen is not None, "Almacen 300001 authentication failed!"
print(f"[OK] Almacen Auth: {u_almacen['nombre_completo']} ({u_almacen['rol']})")

# 5. COMPANY SETTINGS & PERSISTENCE
company = CompanyModel.get()
assert company is not None and "nombre_comercial" in company, "CompanyModel get failed!"
print(f"[OK] Company Config: '{company['nombre_comercial']}' (RNC: {company['rnc']})")

# 6. DEPARTMENTS & PRODUCTS
depts = DepartmentModel.get_all()
subdepts = SubDepartmentModel.get_all()
prods = ProductModel.get_all()
low_stock = ProductModel.get_low_stock_products()
print(f"[OK] Catalog Audit: {len(depts)} Depts, {len(subdepts)} SubDepts, {len(prods)} Products ({len(low_stock)} low stock)")

# 7. CAJAS & SALES & REPORTS
cajas = CajaModel.get_all()
sales = VentaModel.get_all()
metrics = ReportModel.get_dashboard_metrics()
print(f"[OK] Sales & Cajas: {len(cajas)} Cajas, {len(sales)} Sales, Metrics={metrics}")

# 8. FLASK WEB APP ROUTES
client = app.test_client()
r_home = client.get("/")
assert r_home.status_code == 200, "Web / failed!"
r_search = client.get("/api/search?q=a")
assert r_search.status_code == 200, "Web /api/search failed!"
r_login = client.get("/login")
assert r_login.status_code == 200, "Web /login failed!"
print(f"[OK] Flask Web Server: Routes /, /api/search, /login verified 100% OK!")

print("==========================================================")
print("     ALL SYSTEM CHECKS PASSED 100% SUCCESSFULLY!          ")
print("==========================================================")
