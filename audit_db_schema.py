"""Full DB schema and data audit for system review."""
import sys
sys.path.insert(0, '.')
from database import execute_query

def check_table(table_name):
    print(f"\n=== {table_name.upper()} ===")
    sql = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? ORDER BY ORDINAL_POSITION"
    rows = execute_query(sql, (table_name,), fetch_all=True)
    if rows:
        for r in rows:
            print(f"  {r['COLUMN_NAME']} : {r['DATA_TYPE']}")
    else:
        print("  [TABLE NOT FOUND]")

def check_sample(table_name, limit=3):
    sql = f"SELECT TOP {limit} * FROM {table_name} ORDER BY id DESC"
    try:
        rows = execute_query(sql, fetch_all=True)
        print(f"\n  Sample {table_name} ({len(rows) if rows else 0} rows):")
        for r in rows:
            print(" ", dict(r))
    except Exception as e:
        print(f"  ERROR reading {table_name}: {e}")

def check_counts():
    tables = ['ventas', 'detalle_ventas', 'cajas', 'productos', 'clientes', 'usuarios', 
              'departamentos', 'subdepartamentos', 'movimientos_inventario', 'permisos_usuario',
              'configuracion_empresa']
    print("\n=== TABLE COUNTS ===")
    for t in tables:
        try:
            r = execute_query(f"SELECT COUNT(*) as cnt FROM {t}", fetch_one=True)
            print(f"  {t}: {r['cnt'] if r else 'ERROR'} rows")
        except Exception as e:
            print(f"  {t}: ERROR - {e}")

print("=" * 60)
print("   ANTI-POS DB SCHEMA + DATA AUDIT")
print("=" * 60)

# Schema checks
for t in ['ventas', 'detalle_ventas', 'cajas', 'usuarios', 'permisos_usuario']:
    check_table(t)

# Count checks
check_counts()

# Sample data
check_sample('ventas', 3)
check_sample('cajas', 3)
check_sample('permisos_usuario', 5)

# Report data verification
print("\n=== REPORT METRICS ===")
from models import ReportModel
metrics = ReportModel.get_dashboard_metrics()
print("  Dashboard metrics:", metrics)

journal = ReportModel.get_electronic_journal()
print(f"  Electronic journal rows: {len(journal)}")

dept_sales = ReportModel.get_department_subdepartment_sales()
print(f"  Dept/SubDept sales rows: {len(dept_sales)}")

multi = ReportModel.get_multi_total_store_report()
print(f"  Multi-total by tipo_pago: {len(multi)} rows")
for r in multi:
    print("   ", dict(r))

inv_val = ReportModel.get_inventory_valuation_report()
print(f"  Inventory valuation rows: {len(inv_val)}")

bounds = ReportModel.get_date_range_bounds()
print(f"  Date range: {bounds}")

# Caja checks
print("\n=== CAJA / POS CHECKS ===")
from models import CajaModel
active = CajaModel.get_active()
print(f"  Active caja: {dict(active) if active else 'NONE - caja must be opened first'}")
all_cajas = CajaModel.get_all()
print(f"  Total cajas: {len(all_cajas) if all_cajas else 0}")

print("\n=== AUDIT COMPLETE ===")
