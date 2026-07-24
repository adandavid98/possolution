with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# A. Update search_pos_products in POS tab to use active_only=True
old_pos_search = "prods = ProductModel.get_all(search_term=st, subdep_id=self.active_subdep_filter)"
new_pos_search = "prods = ProductModel.get_all(search_term=st, subdep_id=self.active_subdep_filter, active_only=True)"

if old_pos_search in content:
    content = content.replace(old_pos_search, new_pos_search)

# B. Update quick_add_pos_barcode to check active status
old_quick_add = """        prods = ProductModel.get_all(search_term=code)
        if prods:
            p = prods[0]
            self.add_to_cart(p)"""

new_quick_add = """        prods = ProductModel.get_all(search_term=code)
        if prods:
            p = prods[0]
            if p.get("estado") and p["estado"] != "Activo":
                self.show_toast_banner(f"⚠️ El producto '{p['nombre']}' está {p['estado'].upper()} y no se puede vender.")
                self.ent_pos_search.delete(0, "end")
                return
            self.add_to_cart(p)"""

if old_quick_add in content:
    content = content.replace(old_quick_add, new_quick_add)

# C. Add estado dropdown to _load_bo_item_maintenance form
old_form_chk = """        self._chk_bo_precio_manual = ctk.CTkCheckBox(fields_frame, text="Precio Manual al Cobrar", font=ctk.CTkFont(size=11))
        self._chk_bo_precio_manual.pack(anchor="w", pady=(0, 10))"""

new_form_chk = """        self._chk_bo_precio_manual = ctk.CTkCheckBox(fields_frame, text="Precio Manual al Cobrar", font=ctk.CTkFont(size=11))
        self._chk_bo_precio_manual.pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Estado del Artículo", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._cmb_bo_estado = ctk.CTkComboBox(fields_frame, values=["Activo", "Inactivo", "Descontinuado"], height=30)
        self._cmb_bo_estado.set("Activo")
        self._cmb_bo_estado.pack(fill="x", pady=(0, 10))"""

if old_form_chk in content and "_cmb_bo_estado" not in content:
    content = content.replace(old_form_chk, new_form_chk)

# D. Update _clear_bo_prod_form
old_clear_prod = """        self._chk_bo_descontable.select()
        self._chk_bo_precio_manual.deselect()"""

new_clear_prod = """        self._chk_bo_descontable.select()
        self._chk_bo_precio_manual.deselect()
        if hasattr(self, '_cmb_bo_estado'):
            self._cmb_bo_estado.set("Activo")"""

if old_clear_prod in content:
    content = content.replace(old_clear_prod, new_clear_prod)

# E. Update _save_bo_product data dictionary
old_save_data = """            "precio_manual": bool(self._chk_bo_precio_manual.get()),
            "unidad_medida": self._cmb_bo_unidad.get()
        }"""

new_save_data = """            "precio_manual": bool(self._chk_bo_precio_manual.get()),
            "unidad_medida": self._cmb_bo_unidad.get(),
            "estado": self._cmb_bo_estado.get() if hasattr(self, '_cmb_bo_estado') else "Activo"
        }"""

if old_save_data in content:
    content = content.replace(old_save_data, new_save_data)

# F. Update _edit_bo_prod to set _cmb_bo_estado
old_edit_prod = """        if p.get("subdepartamento_nombre"):
            self._cmb_bo_subdept.set(p["subdepartamento_nombre"])"""

new_edit_prod = """        if p.get("subdepartamento_nombre"):
            self._cmb_bo_subdept.set(p["subdepartamento_nombre"])

        if hasattr(self, '_cmb_bo_estado'):
            self._cmb_bo_estado.set(p.get("estado") or "Activo")"""

if old_edit_prod in content:
    content = content.replace(old_edit_prod, new_edit_prod)

# G. Replace _render_bo_products_table with redesigned product card UI (stacked prices & 100% visible buttons)
old_render_bo_table = """    def _render_bo_products_table(self):
        for widget in self._bo_prods_table_frame.winfo_children():
            widget.destroy()

        search = self._ent_bo_search_prod.get().strip() if hasattr(self, '_ent_bo_search_prod') else ""
        prods = ProductModel.get_all(search_term=search)

        if not prods:
            ctk.CTkLabel(self._bo_prods_table_frame, text="No hay artículos registrados.", text_color="#94A3B8", font=ctk.CTkFont(size=12)).pack(pady=30)
            return

        for p in prods:
            card = ctk.CTkFrame(
                self._bo_prods_table_frame,
                fg_color="#0F172A",
                corner_radius=8,
                border_width=1,
                border_color="#334155"
            )
            card.pack(fill="x", pady=4, padx=2)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            # Left side: Product Info
            left_side = ctk.CTkFrame(inner, fg_color="transparent")
            left_side.pack(side="left", fill="x", expand=True)

            subdep_txt = p.get("subdepartamento_nombre") or "General"
            dept_txt = p.get("departamento_nombre") or "General"
            unid_txt = p.get("unidad_medida") or "UD"

            # Row 1: Name & Barcode
            title_lbl = ctk.CTkLabel(
                left_side,
                text=f"{p['nombre']}   (Cód: {p['codigo_barras']})",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#F8FAFC",
                anchor="w"
            )
            title_lbl.pack(anchor="w")

            # Row 2: Department, Subdep, Unit & Flags
            desc_badge = " [Descuentos OK]" if p.get("es_descontable", 1) else " [Sin Desc.]"
            man_badge = " [P.Manual]" if p.get("precio_manual", 0) else ""

            meta_lbl = ctk.CTkLabel(
                left_side,
                text=f"📂 {dept_txt} ➔ {subdep_txt}   •   Unid: {unid_txt}{desc_badge}{man_badge}",
                font=ctk.CTkFont(size=11),
                text_color="#94A3B8",
                anchor="w"
            )
            meta_lbl.pack(anchor="w", pady=(2, 0))

            # Right side: Cost, Price, Stock & Action Buttons
            right_side = ctk.CTkFrame(inner, fg_color="transparent")
            right_side.pack(side="right")

            # Costo & Venta
            cost_txt = f"Costo: RD${float(p['precio_costo']):.2f}"
            price_txt = f"Venta: RD${float(p['precio_venta']):.2f}"
            prices_lbl = ctk.CTkLabel(
                right_side,
                text=f"{cost_txt}  |  {price_txt}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#38BDF8"
            )
            prices_lbl.pack(side="left", padx=(0, 10))

            # Stock Badge
            stock_val = p['stock_actual']
            stock_min = p.get('stock_minimo', 5)
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D"

            stock_frame = ctk.CTkFrame(right_side, fg_color=stock_bg, corner_radius=6)
            stock_frame.pack(side="left", padx=(0, 10))

            stock_lbl = ctk.CTkLabel(
                stock_frame,
                text=f"Stock: {stock_val}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=stock_color
            )
            stock_lbl.pack(padx=6, pady=2)

            # Edit Button
            btn_edit = ctk.CTkButton(
                right_side,
                text="✏️ Editar",
                width=75,
                height=30,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                command=lambda prod=p: self._edit_bo_prod(prod)
            )
            btn_edit.pack(side="left", padx=2)"""

new_render_bo_table = """    def _render_bo_products_table(self):
        for widget in self._bo_prods_table_frame.winfo_children():
            widget.destroy()

        search = self._ent_bo_search_prod.get().strip() if hasattr(self, '_ent_bo_search_prod') else ""
        prods = ProductModel.get_all(search_term=search)

        if not prods:
            ctk.CTkLabel(self._bo_prods_table_frame, text="No hay artículos registrados.", text_color="#94A3B8", font=ctk.CTkFont(size=12)).pack(pady=30)
            return

        for p in prods:
            card = ctk.CTkFrame(
                self._bo_prods_table_frame,
                fg_color="#0F172A",
                corner_radius=8,
                border_width=1,
                border_color="#334155"
            )
            card.pack(fill="x", pady=4, padx=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            # Left side: Product Info & Badges
            left_box = ctk.CTkFrame(inner, fg_color="transparent")
            left_box.pack(side="left", fill="both", expand=True)

            subdep_txt = p.get("subdepartamento_nombre") or "General"
            dept_txt = p.get("departamento_nombre") or "General"
            unid_txt = p.get("unidad_medida") or "UD"
            estado_txt = p.get("estado") or "Activo"

            if estado_txt == "Inactivo":
                st_fg, st_bg = "#F59E0B", "#451A03"
            elif estado_txt == "Descontinuado":
                st_fg, st_bg = "#EF4444", "#450A0A"
            else:
                st_fg, st_bg = "#10B981", "#064E3B"

            header_frame = ctk.CTkFrame(left_box, fg_color="transparent")
            header_frame.pack(fill="x", anchor="w")

            st_pill = ctk.CTkFrame(header_frame, fg_color=st_bg, corner_radius=4)
            st_pill.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(st_pill, text=f" ● {estado_txt} ", font=ctk.CTkFont(size=10, weight="bold"), text_color=st_fg).pack(padx=4, pady=1)

            ctk.CTkLabel(
                header_frame,
                text=f"{p['nombre']}   (Cód: {p['codigo_barras']})",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#F8FAFC",
                anchor="w"
            ).pack(side="left")

            desc_badge = " [Desc. OK]" if p.get("es_descontable", 1) else " [Sin Desc.]"
            man_badge = " [P.Manual]" if p.get("precio_manual", 0) else ""

            ctk.CTkLabel(
                left_box,
                text=f"📂 {dept_txt} ➔ {subdep_txt}   •   Unid: {unid_txt}{desc_badge}{man_badge}",
                font=ctk.CTkFont(size=11),
                text_color="#94A3B8",
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))

            # Right side: Prices & Action Buttons (Stacked rows to prevent cut-off)
            right_box = ctk.CTkFrame(inner, fg_color="transparent")
            right_box.pack(side="right", padx=(10, 0))

            info_row = ctk.CTkFrame(right_box, fg_color="transparent")
            info_row.pack(anchor="e", pady=(0, 4))

            cost_txt = f"Costo: RD${float(p['precio_costo']):.2f}"
            price_txt = f"Venta: RD${float(p['precio_venta']):.2f}"
            ctk.CTkLabel(
                info_row,
                text=f"{cost_txt}  |  {price_txt}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#38BDF8"
            ).pack(side="left", padx=(0, 8))

            stock_val = p['stock_actual']
            stock_min = p.get('stock_minimo', 5)
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D"

            stk_frame = ctk.CTkFrame(info_row, fg_color=stock_bg, corner_radius=6)
            stk_frame.pack(side="left")
            ctk.CTkLabel(
                stk_frame,
                text=f"Stock: {stock_val}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=stock_color
            ).pack(padx=6, pady=2)

            act_row = ctk.CTkFrame(right_box, fg_color="transparent")
            act_row.pack(anchor="e")

            ctk.CTkButton(
                act_row,
                text="✏️ Editar",
                width=80,
                height=28,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                command=lambda prod=p: self._edit_bo_prod(prod)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                act_row,
                text="🗑️ Eliminar",
                width=85,
                height=28,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda pid=p["id"]: self._delete_bo_prod(pid)
            ).pack(side="left", padx=3)"""

if old_render_bo_table in content:
    content = content.replace(old_render_bo_table, new_render_bo_table)

# H. Update _render_bo_operators_table to include Delete button & _delete_bo_user method
old_op_table_cols = """        headers = ["ID", "Usuario (PIN)", "Nombre Completo", "Rol", "Estado", "Acción"]
        cols_w  = [45,   110,             200,               110,   75,       70]"""

new_op_table_cols = """        headers = ["ID", "Usuario (PIN)", "Nombre Completo", "Rol", "Estado", "Acciones"]
        cols_w  = [45,   110,             180,               100,   70,       140]"""

if old_op_table_cols in content:
    content = content.replace(old_op_table_cols, new_op_table_cols)

old_op_edit_btn = """            btn_box = ctk.CTkFrame(row, fg_color="transparent", width=cols_w[-1])
            btn_box.pack(side="left", padx=2)
            ctk.CTkButton(
                btn_box, text="✏️ Editar", width=64, height=20, fg_color="#3B82F6", font=ctk.CTkFont(size=9),
                command=lambda user=u: self._edit_bo_user(user)
            ).pack(side="left")"""

new_op_edit_btn = """            btn_box = ctk.CTkFrame(row, fg_color="transparent", width=cols_w[-1])
            btn_box.pack(side="left", padx=2)
            ctk.CTkButton(
                btn_box, text="✏️ Editar", width=62, height=22, fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda user=u: self._edit_bo_user(user)
            ).pack(side="left", padx=1)
            ctk.CTkButton(
                btn_box, text="🗑️ Eliminar", width=70, height=22, fg_color="#DC2626", hover_color="#B91C1C", font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda uid=u["id"]: self._delete_bo_user(uid)
            ).pack(side="left", padx=1)"""

if old_op_edit_btn in content:
    content = content.replace(old_op_edit_btn, new_op_edit_btn)

# Add _delete_bo_user method after _edit_bo_user
old_edit_user = """    def _edit_bo_user(self, u):
        self._bo_editing_user_id = u["id"]
        self._ent_usr_username.delete(0, "end")
        self._ent_usr_username.insert(0, u["username"])
        self._ent_usr_password.delete(0, "end")
        self._ent_usr_nombre.delete(0, "end")
        self._ent_usr_nombre.insert(0, u["nombre_completo"])
        self._cmb_usr_rol.set(u["rol"])
        if u["activo"]:
            self._chk_usr_activo.select()
        else:
            self._chk_usr_activo.deselect()"""

new_edit_user = old_edit_user + """

    def _delete_bo_user(self, user_id):
        if self.current_user and self.current_user["id"] == user_id:
            messagebox.showerror("Error", "No puede eliminar la cuenta con la que ha iniciado sesión actualmente.")
            return
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de eliminar este operador del sistema?"):
            try:
                UserModel.delete(user_id)
                messagebox.showinfo("Éxito", "Operador eliminado correctamente.")
                self._render_bo_operators_table()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el operador: {e}")"""

if old_edit_user in content and "_delete_bo_user" not in content:
    content = content.replace(old_edit_user, new_edit_user)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app_gui.py updated successfully.")
