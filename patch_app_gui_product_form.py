"""Patch app_gui.py to fix _edit_bo_prod and _save_bo_product in Back Office Article Maintenance."""
with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix 1: _edit_bo_prod stock_minimo insert and department resolution
old_edit_block = """        self._ent_bo_stock.delete(0, "end")
        self._ent_bo_stock.insert(0, str(p["stock_actual"]))
        self._ent_bo_min_stock.delete(0, "end")
        u_code = p.get("unidad_medida") or "UD\""""

new_edit_block = """        self._ent_bo_stock.delete(0, "end")
        self._ent_bo_stock.insert(0, str(p["stock_actual"]))
        self._ent_bo_min_stock.delete(0, "end")
        self._ent_bo_min_stock.insert(0, str(p.get("stock_minimo", 5)))
        u_code = p.get("unidad_medida") or "UD\""""

code = code.replace(old_edit_block, new_edit_block)

# Fix 2: _save_bo_product robust subdept_id resolution
old_save_subdept = """        subdept_name = self._cmb_bo_subdept.get()
        subdepts = SubDepartmentModel.get_all()
        subdept_id = None
        for sd in subdepts:
            if sd["nombre"] == subdept_name:
                subdept_id = sd["id"]
                break"""

new_save_subdept = """        dept_name = self._cmb_bo_dept.get() if hasattr(self, '_cmb_bo_dept') else ""
        subdept_name = self._cmb_bo_subdept.get() if hasattr(self, '_cmb_bo_subdept') else ""

        depts = DepartmentModel.get_all()
        dept_id = None
        for d in depts:
            if d["nombre"] == dept_name:
                dept_id = d["id"]
                break

        subdept_id = None
        if dept_id:
            subdepts = SubDepartmentModel.get_by_department(dept_id)
            for sd in subdepts:
                if sd["nombre"] == subdept_name:
                    subdept_id = sd["id"]
                    break

        if not subdept_id:
            all_sds = SubDepartmentModel.get_all()
            for sd in all_sds:
                if sd["nombre"] == subdept_name:
                    subdept_id = sd["id"]
                    break

        if not subdept_id and self._bo_editing_prod_id:
            curr_prod = ProductModel.get_by_id(self._bo_editing_prod_id)
            if curr_prod:
                subdept_id = curr_prod.get("subdepartamento_id")"""

code = code.replace(old_save_subdept, new_save_subdept)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py successfully patched with complete Article Maintenance fixes!")
