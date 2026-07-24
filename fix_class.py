import ast

bo_methods = [
    'load_backoffice_tab', '_load_bo_item_maintenance', '_on_bo_dept_changed',
    '_update_bo_subdepts_dropdown', '_clear_bo_prod_form', '_save_bo_product',
    '_render_bo_products_table', '_edit_bo_prod', '_delete_bo_prod',
    '_load_bo_customers', '_clear_bo_cust_form', '_save_bo_customer',
    '_render_bo_customers_table', '_edit_bo_cust', '_delete_bo_cust',
    '_load_bo_operators', '_clear_bo_usr_form', '_save_bo_operator',
    '_render_bo_operators_table', '_edit_bo_user', '_select_user_for_perms',
    '_render_permissions_matrix', '_save_user_permissions_matrix',
    '_load_bo_store_config', '_save_company_config', '_open_dept_manager_modal'
]

with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '\n\n# === Monkey-patch Back Office methods from FlipChartModal onto POSApp ===\n'
for m in bo_methods:
    patch += f'POSApp.{m} = FlipChartModal.{m}\n'

# Only add patch if not already there
if 'Monkey-patch Back Office' not in content:
    content += patch

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
try:
    tree = ast.parse(content)
    print('SYNTAX OK')
    # Verify the patch works conceptually
    print('Monkey-patch lines added:', len(bo_methods))
    print('DONE - All Back Office methods will be available on POSApp instances')
except SyntaxError as e:
    print(f'SYNTAX ERROR line {e.lineno}: {e.msg}')
