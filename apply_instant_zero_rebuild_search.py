with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update POS search_pos_products to perform instant 0ms show/hide filtering on pre-built cards
old_pos_search = """    def search_pos_products(self):
        term = self.ent_pos_search.get().strip() if hasattr(self, 'ent_pos_search') else ""
        subdep_id = getattr(self, 'active_subdep_filter', None)
        products = ProductModel.get_all(search_term=term, subdep_id=subdep_id)

        for w in self.products_scroll.winfo_children():
            w.destroy()

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll, text="No se encontraron productos.", text_color="#A0A0B0")
            lbl.pack(pady=20)
            return

        for p in products:
            card = ctk.CTkFrame(
                self.products_scroll,
                fg_color="#0F172A",
                corner_radius=8,
                border_width=1,
                border_color="#334155"
            )"""

new_pos_search = """    def search_pos_products(self):
        term = self.ent_pos_search.get().strip().lower() if hasattr(self, 'ent_pos_search') else ""
        subdep_filter = getattr(self, 'active_subdep_filter', None)

        existing_cards = self.products_scroll.winfo_children()

        # If product cards are already rendered, perform INSTANT 0ms show/hide without destroying widgets!
        if existing_cards and hasattr(existing_cards[0], '_search_text'):
            visible_count = 0
            for card in existing_cards:
                if hasattr(card, '_search_text'):
                    matches_term = (not term or term in card._search_text)
                    matches_subdep = (subdep_filter is None or card._subdep_id == subdep_filter)
                    if matches_term and matches_subdep:
                        card.pack(fill="x", pady=4, padx=4)
                        visible_count += 1
                    else:
                        card.pack_forget()
            return

        # Build card widgets for the first time
        for w in self.products_scroll.winfo_children():
            w.destroy()

        products = ProductModel.get_all(active_only=True)

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll, text="No se encontraron productos.", text_color="#A0A0B0")
            lbl.pack(pady=20)
            return

        for p in products:
            card = ctk.CTkFrame(
                self.products_scroll,
                fg_color="#0F172A",
                corner_radius=8,
                border_width=1,
                border_color="#334155"
            )
            card._search_text = f"{p['nombre']} {p['codigo_barras']}".lower()
            card._subdep_id = p.get('subdepartamento_id')

            matches_term = (not term or term in card._search_text)
            matches_subdep = (subdep_filter is None or card._subdep_id == subdep_filter)
            if matches_term and matches_subdep:
                card.pack(fill="x", pady=4, padx=4)
            else:
                card.pack_forget()"""

if old_pos_search in content:
    content = content.replace(old_pos_search, new_pos_search)
    print("POS search updated with instant 0ms show/hide.")

# 2. Update Back Office _render_bo_products_table for instant 0ms show/hide
old_bo_search = """    def _render_bo_products_table(self):
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
            )"""

new_bo_search = """    def _render_bo_products_table(self, force_reload=False):
        search = self._ent_bo_search_prod.get().strip().lower() if hasattr(self, '_ent_bo_search_prod') else ""

        existing_cards = self._bo_prods_table_frame.winfo_children()

        # If product cards are already rendered and not force_reload, perform INSTANT 0ms show/hide without destroying widgets!
        if not force_reload and existing_cards and hasattr(existing_cards[0], '_search_text'):
            for card in existing_cards:
                if hasattr(card, '_search_text'):
                    if not search or search in card._search_text:
                        card.pack(fill="x", pady=4, padx=4)
                    else:
                        card.pack_forget()
            return

        # Build card widgets for the first time or when force_reload=True
        for widget in self._bo_prods_table_frame.winfo_children():
            widget.destroy()

        prods = ProductModel.get_all()

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
            card._search_text = f"{p['nombre']} {p['codigo_barras']} {p.get('departamento_nombre', '')} {p.get('subdepartamento_nombre', '')}".lower()

            if not search or search in card._search_text:
                card.pack(fill="x", pady=4, padx=4)
            else:
                card.pack_forget()"""

if old_bo_search in content:
    content = content.replace(old_bo_search, new_bo_search)
    print("Back Office search updated with instant 0ms show/hide.")

# 3. Update force reload when saving/deleting BO product
old_save_reload = "self._render_bo_products_table()"
new_save_reload = "self._render_bo_products_table(force_reload=True)"
if old_save_reload in content:
    content = content.replace(old_save_reload, new_save_reload)

# 4. Increase debounce timer to 250ms for smooth word typing before filter triggers
old_timer_120 = "self.after(120,"
new_timer_250 = "self.after(250,"
if old_timer_120 in content:
    content = content.replace(old_timer_120, new_timer_250)
    print("Debounce timers increased to 250ms.")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("apply_instant_zero_rebuild_search complete.")
