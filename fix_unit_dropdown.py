with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update row_stock and _cmb_bo_unidad layout in _load_bo_item_maintenance
old_stock_unit_block = """        # Stocks and Unit
        row_stock = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row_stock.pack(fill="x", pady=4)

        s1 = ctk.CTkFrame(row_stock, fg_color="transparent")
        s1.pack(side="left", fill="x", expand=True, padx=(0, 2))
        ctk.CTkLabel(s1, text="Stock Act.", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_stock = ctk.CTkEntry(s1, placeholder_text="0", height=32)
        self._ent_bo_stock.pack(fill="x")

        s2 = ctk.CTkFrame(row_stock, fg_color="transparent")
        s2.pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkLabel(s2, text="Stock Mín.", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_min_stock = ctk.CTkEntry(s2, placeholder_text="5", height=32)
        self._ent_bo_min_stock.pack(fill="x")

        s3 = ctk.CTkFrame(row_stock, fg_color="transparent")
        s3.pack(side="left", fill="x", expand=True, padx=(2, 0))
        ctk.CTkLabel(s3, text="Unidad", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._cmb_bo_unidad = ctk.CTkComboBox(s3, values=["UD", "LB", "KG", "PQT", "CJ", "GL", "LT", "SAC"], height=32, width=80)
        self._cmb_bo_unidad.set("UD")
        self._cmb_bo_unidad.pack(fill="x")"""

new_stock_unit_block = """        # Stocks
        row_stock = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row_stock.pack(fill="x", pady=4)

        s1 = ctk.CTkFrame(row_stock, fg_color="transparent")
        s1.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkLabel(s1, text="Stock Actual (UD)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_stock = ctk.CTkEntry(s1, placeholder_text="0", height=32)
        self._ent_bo_stock.pack(fill="x")

        s2 = ctk.CTkFrame(row_stock, fg_color="transparent")
        s2.pack(side="left", fill="x", expand=True, padx=(4, 0))
        ctk.CTkLabel(s2, text="Stock Mínimo", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_min_stock = ctk.CTkEntry(s2, placeholder_text="5", height=32)
        self._ent_bo_min_stock.pack(fill="x")

        # Dedicated full-width Unit of Measure row
        ctk.CTkLabel(fields_frame, text="Unidad de Medida", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._cmb_bo_unidad = ctk.CTkComboBox(
            fields_frame,
            values=["UD - Unidad", "LB - Libra", "KG - Kilogramo", "PQT - Paquete", "CJ - Caja", "GL - Galón", "LT - Litro", "SAC - Saco"],
            height=32
        )
        self._cmb_bo_unidad.set("UD - Unidad")
        self._cmb_bo_unidad.pack(fill="x", pady=(0, 6))"""

if old_stock_unit_block in content:
    content = content.replace(old_stock_unit_block, new_stock_unit_block)

# 2. Update _clear_bo_prod_form
old_clear_u = 'self._cmb_bo_unidad.set("UD")'
new_clear_u = 'self._cmb_bo_unidad.set("UD - Unidad")'
if old_clear_u in content:
    content = content.replace(old_clear_u, new_clear_u)

# 3. Update _save_bo_product to parse unit code
old_save_u = '"unidad_medida": self._cmb_bo_unidad.get()'
new_save_u = '"unidad_medida": self._cmb_bo_unidad.get().split(" - ")[0] if hasattr(self, "_cmb_bo_unidad") else "UD"'
if old_save_u in content:
    content = content.replace(old_save_u, new_save_u)

# 4. Update _edit_bo_prod to match unit code
old_edit_u = 'self._cmb_bo_unidad.set(p.get("unidad_medida") or "UD")'
new_edit_u = """        u_code = p.get("unidad_medida") or "UD"
        for u_val in ["UD - Unidad", "LB - Libra", "KG - Kilogramo", "PQT - Paquete", "CJ - Caja", "GL - Galón", "LT - Litro", "SAC - Saco"]:
            if u_val.startswith(u_code):
                self._cmb_bo_unidad.set(u_val)
                break
        else:
            self._cmb_bo_unidad.set("UD - Unidad")"""

if old_edit_u in content:
    content = content.replace(old_edit_u, new_edit_u)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Unit dropdown fix complete.")
