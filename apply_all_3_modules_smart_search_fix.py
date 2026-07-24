with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update POS subdepartment buttons & search_pos_products
old_pos_buttons_and_search = """        self.active_subdep_filter = None

        quick_subdeps = [
            ("🌟 Todos", None),
            ("🌾 Granos", 1),
            ("🥤 Refrescos", 5),
            ("🥛 Lácteos", 8),
            ("🧹 Limpieza", 11),
        ]

        for label, sd_id in quick_subdeps:
            btn_sd = ctk.CTkButton(
                subdep_bar, text=label, font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#334155" if self.active_subdep_filter != sd_id else "#2563EB",
                hover_color="#475569", height=32, width=0, corner_radius=6,
                command=lambda s_id=sd_id: self.set_subdep_filter(s_id)
            )
            btn_sd.pack(side="left", padx=2, expand=True, fill="x")

        # Big Flip Chart Overlay Trigger
        btn_flip = ctk.CTkButton(
            subdep_bar, text="📋 Flip Chart", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED", height=32, width=110, corner_radius=6,
            command=self.open_flip_chart_modal
        )
        btn_flip.pack(side="right", padx=(4, 0))

        # Products Scrollable Grid/List
        self.products_scroll = ctk.CTkScrollableFrame(left_side, fg_color="transparent")
        self.products_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.search_pos_products()

        # --- RIGHT SIDE: Default Cart View ---
        self.show_pos_cart_view()

        self.render_cart()

    def set_subdep_filter(self, subdep_id):
        self.active_subdep_filter = subdep_id
        self.search_pos_products()

    def open_flip_chart_modal(self):
        FlipChartModal(self)

    def search_pos_products(self, force_reload=False):
        term = self.ent_pos_search.get().strip() if hasattr(self, 'ent_pos_search') else ""
        subdep_filter = getattr(self, 'active_subdep_filter', None)

        # Determine which products to display
        if len(term) >= 2:
            # SQL-level search: fast even with 100k+ products
            products = ProductModel.search_live(term, limit=100, active_only=True, subdep_id=subdep_filter)
        elif len(term) == 0 and not force_reload:
            # Use cached recent products if already loaded
            existing = self.products_scroll.winfo_children()
            if existing and hasattr(existing[0], '_pos_search_text'):
                for card in existing:
                    if hasattr(card, '_pos_search_text'):
                        matches = (subdep_filter is None or card._pos_subdep_id == subdep_filter)
                        card.pack(fill="x", pady=5, padx=4) if matches else card.pack_forget()
                return
            products = ProductModel.get_recent(limit=40, active_only=True)
        else:
            # 1-char typed: too short to search, keep current view
            return

        # Rebuild widget list with new results
        for w in self.products_scroll.winfo_children():
            w.destroy()

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll,
                text="No se encontraron productos." if term else "No hay artículos registrados.",
                text_color="#A0A0B0")
            lbl.pack(pady=20)
            return

        for p in products:
            card = ctk.CTkFrame(
                self.products_scroll,
                fg_color="#0F172A",
                corner_radius=10,
                border_width=1,
                border_color="#334155"
            )
            card._pos_search_text = f"{p['nombre']} {p['codigo_barras']} {p.get('subdepartamento_nombre', '')}".lower()
            card._pos_subdep_id = p.get('subdepartamento_id')
            card.pack(fill="x", pady=5, padx=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            left_info = ctk.CTkFrame(inner, fg_color="transparent")
            left_info.pack(side="left", fill="x", expand=True)

            subdep_tag = p.get('subdepartamento_nombre') or 'General'
            ctk.CTkLabel(left_info, text=p['nombre'], anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC").pack(anchor="w")
            ctk.CTkLabel(left_info, text=f"📂 {subdep_tag}   •   Cód: {p['codigo_barras']}",
                anchor="w", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w", pady=(2, 0))

            right_actions = ctk.CTkFrame(inner, fg_color="transparent")
            right_actions.pack(side="right")

            stock_val = p.get('stock_actual') if p.get('stock_actual') is not None else 0
            stock_min = p['stock_minimo']
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D"

            stock_badge = ctk.CTkFrame(right_actions, fg_color=stock_bg, corner_radius=6)
            stock_badge.pack(side="left", padx=(0, 12))
            ctk.CTkLabel(stock_badge, text=f"Stock: {stock_val}",
                font=ctk.CTkFont(size=11, weight="bold"), text_color=stock_color).pack(padx=8, pady=3)

            ctk.CTkLabel(right_actions, text=f"RD$ {float(p['precio_venta']):.2f}",
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#38BDF8").pack(side="left", padx=(0, 12))

            ctk.CTkButton(right_actions, text="+ Agregar", width=85, height=34,
                corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#2563EB", hover_color="#1D4ED8",
                command=lambda prod=p: self.add_to_cart(prod)).pack(side="left")"""

new_pos_buttons_and_search = """        self.active_subdep_filter = None
        self._subdep_buttons = {}

        quick_subdeps = [
            ("🌟 Todos", None),
            ("🌾 Granos", 1),
            ("🥤 Refrescos", 5),
            ("🥛 Lácteos", 8),
            ("🧹 Limpieza", 11),
        ]

        for label, sd_id in quick_subdeps:
            btn_sd = ctk.CTkButton(
                subdep_bar, text=label, font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#2563EB" if self.active_subdep_filter == sd_id else "#334155",
                hover_color="#1D4ED8", height=32, width=0, corner_radius=6,
                command=lambda s_id=sd_id: self.set_subdep_filter(s_id)
            )
            btn_sd.pack(side="left", padx=2, expand=True, fill="x")
            self._subdep_buttons[sd_id] = btn_sd

        # Big Flip Chart Overlay Trigger
        btn_flip = ctk.CTkButton(
            subdep_bar, text="📋 Flip Chart", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED", height=32, width=110, corner_radius=6,
            command=self.open_flip_chart_modal
        )
        btn_flip.pack(side="right", padx=(4, 0))

        # Products Scrollable Grid/List
        self.products_scroll = ctk.CTkScrollableFrame(left_side, fg_color="transparent")
        self.products_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.search_pos_products()

        # --- RIGHT SIDE: Default Cart View ---
        self.show_pos_cart_view()

        self.render_cart()

    def set_subdep_filter(self, subdep_id):
        self.active_subdep_filter = subdep_id
        if hasattr(self, '_subdep_buttons'):
            for s_id, btn in self._subdep_buttons.items():
                btn.configure(fg_color="#2563EB" if s_id == subdep_id else "#334155")
        self.search_pos_products(force_reload=True)

    def open_flip_chart_modal(self):
        FlipChartModal(self)

    def search_pos_products(self, force_reload=False):
        term = self.ent_pos_search.get().strip() if hasattr(self, 'ent_pos_search') else ""
        subdep_filter = getattr(self, 'active_subdep_filter', None)

        products = ProductModel.search_live(term, limit=100 if term else 20, active_only=True, subdep_id=subdep_filter)

        for w in self.products_scroll.winfo_children():
            w.destroy()

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll,
                text="No se encontraron productos en este sub-departamento." if subdep_filter else ("No se encontraron productos." if term else "No hay artículos registrados."),
                text_color="#A0A0B0", font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(pady=25)
            return

        for p in products:
            card = ctk.CTkFrame(
                self.products_scroll,
                fg_color="#0F172A",
                corner_radius=10,
                border_width=1,
                border_color="#334155"
            )
            card.pack(fill="x", pady=4, padx=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            left_info = ctk.CTkFrame(inner, fg_color="transparent")
            left_info.pack(side="left", fill="x", expand=True)

            subdep_tag = p.get('subdepartamento_nombre') or 'General'
            ctk.CTkLabel(left_info, text=p['nombre'], anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC").pack(anchor="w")
            ctk.CTkLabel(left_info, text=f"📂 {subdep_tag}   •   Cód: {p['codigo_barras']}",
                anchor="w", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w", pady=(2, 0))

            right_actions = ctk.CTkFrame(inner, fg_color="transparent")
            right_actions.pack(side="right")

            stock_val = p.get('stock_actual') if p.get('stock_actual') is not None else 0
            stock_min = p.get('stock_minimo', 5) or 5
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D"

            stock_badge = ctk.CTkFrame(right_actions, fg_color=stock_bg, corner_radius=6)
            stock_badge.pack(side="left", padx=(0, 12))
            ctk.CTkLabel(stock_badge, text=f"Stock: {stock_val}",
                font=ctk.CTkFont(size=11, weight="bold"), text_color=stock_color).pack(padx=8, pady=3)

            ctk.CTkLabel(right_actions, text=f"RD$ {float(p['precio_venta']):.2f}",
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#38BDF8").pack(side="left", padx=(0, 12))

            ctk.CTkButton(right_actions, text="+ Agregar", width=85, height=34,
                corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#2563EB", hover_color="#1D4ED8",
                command=lambda prod=p: self.add_to_cart(prod)).pack(side="left")"""

if old_pos_buttons_and_search in content:
    content = content.replace(old_pos_buttons_and_search, new_pos_buttons_and_search)
    print("POS buttons and search updated successfully!")
else:
    print("WARNING: old_pos_buttons_and_search block not found")

# 2. Update render_inventory_table
old_inventory_table = """    def render_inventory_table(self, force_reload=False):
        term = self.ent_inv_search.get().strip() if hasattr(self, 'ent_inv_search') else ""

        # Smart load: SQL search on ≥2 chars, get_recent on empty, skip on 1 char
        if len(term) >= 2:
            products = ProductModel.search_live(term, limit=100)
            force_reload = True  # always rebuild when doing SQL search
        elif len(term) == 0 and not force_reload:
            data_rows = [w for w in self.table_scroll.winfo_children() if hasattr(w, '_inv_search_text')]
            if data_rows:
                for row in data_rows:
                    row.pack(fill="x", pady=2)
                return
            products = ProductModel.get_recent(limit=40)
        elif len(term) == 1:
            return  # too short, skip
        else:
            products = ProductModel.get_recent(limit=40)
            force_reload = True

        # Rebuild rows
        for w in self.table_scroll.winfo_children():
            w.destroy()

        headers = ["Cód. Barras", "Nombre Producto", "Departamento", "Sub-Depto", "P. Costo", "P. Venta", "Stock", "Estado", "Acciones"]
        cols_w = [110, 170, 130, 130, 80, 80, 50, 90, 80]

        head_row = ctk.CTkFrame(self.table_scroll, fg_color="#1F2937", height=35)
        head_row.pack(fill="x", pady=2)
        for idx, h in enumerate(headers):
            ctk.CTkLabel(head_row, text=h, font=ctk.CTkFont(size=11, weight="bold"), width=cols_w[idx]).pack(side="left", padx=2)

        for p in products:
            stock = p['stock_actual']
            min_s = p['stock_minimo']
            status_txt, status_bg = "NORMAL", "#10B981"
            if stock <= 0: status_txt, status_bg = "AGOTADO", "#EF4444"
            elif stock <= min_s: status_txt, status_bg = "STOCK BAJO", "#F59E0B"

            dep_tag = p.get('departamento_nombre') or p.get('categoria_nombre') or 'General'
            subdep_tag = p.get('subdepartamento_nombre') or 'General'

            row = ctk.CTkFrame(self.table_scroll, fg_color="#111118", height=38)
            row._inv_search_text = f"{p['codigo_barras']} {p['nombre']} {dep_tag} {subdep_tag}".lower()
            row.pack(fill="x", pady=2)

            for idx, val in enumerate([p['codigo_barras'], p['nombre'], dep_tag, subdep_tag,
                                        f"RD${p['precio_costo']:.2f}", f"RD${p['precio_venta']:.2f}", str(stock)]):
                ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=11), width=cols_w[idx]).pack(side="left", padx=2)

            ctk.CTkLabel(row, text=f" {status_txt} ", font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=status_bg, text_color="white", corner_radius=4, width=cols_w[7]).pack(side="left", padx=2)
            ctk.CTkButton(row, text="✏", width=30, height=24, fg_color="#374151",
                command=lambda prod=p: self.modal_product_form(prod)).pack(side="left", padx=2)
            ctk.CTkButton(row, text="🗑", width=30, height=24, fg_color="#EF4444",
                command=lambda prod=p: self.delete_prod(prod)).pack(side="left", padx=2)"""

new_inventory_table = """    def render_inventory_table(self, force_reload=False):
        term = self.ent_inv_search.get().strip() if hasattr(self, 'ent_inv_search') else ""
        products = ProductModel.search_live(term, limit=100 if term else 20)

        for w in self.table_scroll.winfo_children():
            w.destroy()

        headers = ["Cód. Barras", "Nombre Producto", "Departamento", "Sub-Depto", "P. Costo", "P. Venta", "Stock", "Estado", "Acciones"]
        cols_w = [110, 170, 130, 130, 80, 80, 50, 90, 80]

        head_row = ctk.CTkFrame(self.table_scroll, fg_color="#1F2937", height=35)
        head_row.pack(fill="x", pady=2)
        for idx, h in enumerate(headers):
            ctk.CTkLabel(head_row, text=h, font=ctk.CTkFont(size=11, weight="bold"), width=cols_w[idx]).pack(side="left", padx=2)

        if not products:
            lbl = ctk.CTkLabel(self.table_scroll, text="No se encontraron productos.", text_color="#A0A0B0", font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(pady=25)
            return

        for p in products:
            stock = p.get('stock_actual', 0) if p.get('stock_actual') is not None else 0
            min_s = p.get('stock_minimo', 5) or 5
            status_txt, status_bg = "NORMAL", "#10B981"
            if stock <= 0: status_txt, status_bg = "AGOTADO", "#EF4444"
            elif stock <= min_s: status_txt, status_bg = "STOCK BAJO", "#F59E0B"

            dep_tag = p.get('departamento_nombre') or p.get('categoria_nombre') or 'General'
            subdep_tag = p.get('subdepartamento_nombre') or 'General'

            row = ctk.CTkFrame(self.table_scroll, fg_color="#111118", height=38)
            row.pack(fill="x", pady=2)

            for idx, val in enumerate([p['codigo_barras'], p['nombre'], dep_tag, subdep_tag,
                                        f"RD${float(p['precio_costo']):.2f}", f"RD${float(p['precio_venta']):.2f}", str(stock)]):
                ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=11), width=cols_w[idx]).pack(side="left", padx=2)

            ctk.CTkLabel(row, text=f" {status_txt} ", font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=status_bg, text_color="white", corner_radius=4, width=cols_w[7]).pack(side="left", padx=2)
            ctk.CTkButton(row, text="✏", width=30, height=24, fg_color="#374151",
                command=lambda prod=p: self.modal_product_form(prod)).pack(side="left", padx=2)
            ctk.CTkButton(row, text="🗑", width=30, height=24, fg_color="#EF4444",
                command=lambda prod=p: self.delete_prod(prod)).pack(side="left", padx=2)"""

if old_inventory_table in content:
    content = content.replace(old_inventory_table, new_inventory_table)
    print("render_inventory_table updated successfully!")
else:
    print("WARNING: old_inventory_table block not found")

# 3. Update _render_bo_products_table
old_bo_table = """    def _render_bo_products_table(self, force_reload=False):
        search = self._ent_bo_search_prod.get().strip() if hasattr(self, '_ent_bo_search_prod') else ""

        # Smart load: SQL search on ≥2 chars, get_recent on empty, skip on 1 char
        if len(search) >= 2:
            prods = ProductModel.search_live(search, limit=100)
            force_reload = True
        elif len(search) == 0 and not force_reload:
            existing = self._bo_prods_table_frame.winfo_children()
            if existing and hasattr(existing[0], '_search_text'):
                for card in existing:
                    if hasattr(card, '_search_text'):
                        card.pack(fill="x", pady=4, padx=4)
                return
            prods = ProductModel.get_recent(limit=40)
        elif len(search) == 1:
            return  # too short, skip
        else:
            prods = ProductModel.get_recent(limit=40)
            force_reload = True"""

new_bo_table = """    def _render_bo_products_table(self, force_reload=False):
        search = self._ent_bo_search_prod.get().strip() if hasattr(self, '_ent_bo_search_prod') else ""
        prods = ProductModel.search_live(search, limit=100 if search else 20)"""

if old_bo_table in content:
    content = content.replace(old_bo_table, new_bo_table)
    print("_render_bo_products_table updated successfully!")
else:
    print("WARNING: old_bo_table block not found")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
