with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update _build_backoffice_tab_ui subtab calls with try...except
old_subtab_calls = """        # Load Sub-tabs
        self._load_bo_item_maintenance(self._tab_item_maint)
        self._load_bo_customers(self._tab_customers)
        self._load_bo_operators(self._tab_operators)
        self._load_bo_store_config(self._tab_store_cfg)"""

new_subtab_calls = """        # Load Sub-tabs with fault isolation
        try:
            self._load_bo_item_maintenance(self._tab_item_maint)
        except Exception as e:
            print("Error loading item maintenance subtab:", e)

        try:
            self._load_bo_customers(self._tab_customers)
        except Exception as e:
            print("Error loading customers subtab:", e)

        try:
            self._load_bo_operators(self._tab_operators)
        except Exception as e:
            print("Error loading operators subtab:", e)

        try:
            self._load_bo_store_config(self._tab_store_cfg)
        except Exception as e:
            print("Error loading store config subtab:", e)"""

if old_subtab_calls in content:
    content = content.replace(old_subtab_calls, new_subtab_calls)

# 2. Fix stock_minimo and stock_actual safe null handling in _render_bo_products_table
old_stock_calc = """            stock_val = p['stock_actual']
            stock_min = p.get('stock_minimo', 5)
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444" """

new_stock_calc = """            stock_val = p.get('stock_actual') if p.get('stock_actual') is not None else 0
            stock_min = p.get('stock_minimo') if p.get('stock_minimo') is not None else 5
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444" """

# Let's search for exact stock block in app_gui.py
old_stock_block = """            stock_val = p['stock_actual']
            stock_min = p.get('stock_minimo', 5)
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D" """

new_stock_block = """            stock_val = p.get('stock_actual') if p.get('stock_actual') is not None else 0
            stock_min = p.get('stock_minimo') if p.get('stock_minimo') is not None else 5
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D" """

if "stock_val = p['stock_actual']" in content:
    content = content.replace("stock_val = p['stock_actual']", "stock_val = p.get('stock_actual') if p.get('stock_actual') is not None else 0")
if "stock_min = p.get('stock_minimo', 5)" in content:
    content = content.replace("stock_min = p.get('stock_minimo', 5)", "stock_min = p.get('stock_minimo') if p.get('stock_minimo') is not None else 5")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app_gui.py subtab fix complete.")
