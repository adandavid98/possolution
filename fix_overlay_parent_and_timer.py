with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_loading_method = """    def _build_tab_with_loading_bar(self, tab_key, view_frame):
        module_titles = {
            "pos": "Caja / POS",
            "inventory": "Inventario & Alertas",
            "caja": "Apertura / Cierre de Caja",
            "reports": "Reportes & Ventas",
            "backoffice": "Back Office"
        }
        title_name = module_titles.get(tab_key, "Módulo")

        # Full-screen OPAQUE loading overlay covering 100% of module container!
        overlay = ctk.CTkFrame(view_frame, fg_color="#0F172A", corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        center_box = ctk.CTkFrame(overlay, fg_color="transparent")
        center_box.place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(center_box, fg_color="#1E293B", corner_radius=12, border_width=1, border_color="#334155")
        card.pack(padx=30, pady=30)

        lbl_title = ctk.CTkLabel(
            card, text=f"⏳ Cargando Módulo de {title_name}...",
            font=ctk.CTkFont(size=15, weight="bold"), text_color="#F8FAFC"
        )
        lbl_title.pack(padx=40, pady=(24, 10))

        # Indeterminate Sliding Progress Bar
        pbar = ctk.CTkProgressBar(card, mode="indeterminate", width=340, height=12, progress_color="#2563EB")
        pbar.pack(padx=40, pady=8)
        pbar.start()

        # Real-time Elapsed Time Counter
        t0 = time.time()
        lbl_timer = ctk.CTkLabel(
            card, text="⏱️ Tiempo de carga: 0.0s",
            font=ctk.CTkFont(size=12), text_color="#94A3B8"
        )
        lbl_timer.pack(padx=40, pady=(4, 8))

        sub_lbl = ctk.CTkLabel(
            card, text="Construyendo interfaz y organizando artículos...",
            font=ctk.CTkFont(size=10), text_color="#64748B"
        )
        sub_lbl.pack(padx=40, pady=(0, 24))

        timer_active = [True]

        def _update_timer():
            if timer_active[0] and card.winfo_exists():
                elapsed = time.time() - t0
                lbl_timer.configure(text=f"⏱️ Tiempo de carga: {elapsed:.1f}s")
                self.after(50, _update_timer)

        _update_timer()

        # Ensure overlay is topmost inside view_frame before building
        overlay.lift()

        # Build module UI behind the opaque overlay, then reveal 100% formed UI
        def _deferred_build():
            try:
                if tab_key == "pos":
                    self._build_pos_tab_ui(view_frame)
                elif tab_key == "inventory":
                    self._build_inventory_tab_ui(view_frame)
                elif tab_key == "caja":
                    self._build_caja_tab_ui(view_frame)
                elif tab_key == "reports":
                    self._build_reports_tab_ui(view_frame)
                elif tab_key == "backoffice":
                    self._build_backoffice_tab_ui(view_frame)

                # Ensure overlay stays on top during creation
                if overlay.winfo_exists():
                    overlay.lift()
                view_frame.update_idletasks()
            finally:
                # Guarantee smooth 400ms minimum display so user clearly sees the progress bar & counter
                elapsed_ms = int((time.time() - t0) * 1000)
                remaining_ms = max(10, 400 - elapsed_ms)

                def _finish():
                    timer_active[0] = False
                    try:
                        pbar.stop()
                        overlay.destroy()
                    except Exception:
                        pass
                    self.after(60, lambda: self._focus_tab_search_field(tab_key))

                self.after(remaining_ms, _finish)

        self.after(40, _deferred_build)"""

new_loading_method = """    def _build_tab_with_loading_bar(self, tab_key, view_frame):
        module_titles = {
            "pos": "Caja / POS",
            "inventory": "Inventario & Alertas",
            "caja": "Apertura / Cierre de Caja",
            "reports": "Reportes & Ventas",
            "backoffice": "Back Office"
        }
        title_name = module_titles.get(tab_key, "Módulo")

        # Overlay attached directly to self.content_area covering 100% of module space!
        overlay = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()

        center_card = ctk.CTkFrame(overlay, fg_color="#1E293B", corner_radius=14, border_width=2, border_color="#334155")
        center_card.place(relx=0.5, rely=0.5, anchor="center")

        lbl_title = ctk.CTkLabel(
            center_card, text=f"⏳ Cargando Módulo de {title_name}...",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC"
        )
        lbl_title.pack(padx=45, pady=(26, 12))

        # Indeterminate Progress Bar
        pbar = ctk.CTkProgressBar(center_card, mode="indeterminate", width=360, height=14, progress_color="#2563EB", fg_color="#0F172A")
        pbar.pack(padx=45, pady=8)
        pbar.start()

        # Real-time Elapsed Time Counter
        t0 = time.time()
        lbl_timer = ctk.CTkLabel(
            center_card, text="⏱️ Tiempo de carga: 0.0s",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#38BDF8"
        )
        lbl_timer.pack(padx=45, pady=(6, 8))

        sub_lbl = ctk.CTkLabel(
            center_card, text="Construyendo interfaz y cargando datos esenciales...",
            font=ctk.CTkFont(size=11), text_color="#64748B"
        )
        sub_lbl.pack(padx=45, pady=(0, 26))

        # Force UI update so overlay and progress bar render BEFORE build begins!
        self.update_idletasks()

        timer_active = [True]

        def _update_timer():
            if timer_active[0] and overlay.winfo_exists():
                elapsed = time.time() - t0
                lbl_timer.configure(text=f"⏱️ Tiempo de carga: {elapsed:.1f}s")
                self.after(50, _update_timer)

        _update_timer()

        def _deferred_build():
            try:
                if tab_key == "pos":
                    self._build_pos_tab_ui(view_frame)
                elif tab_key == "inventory":
                    self._build_inventory_tab_ui(view_frame)
                elif tab_key == "caja":
                    self._build_caja_tab_ui(view_frame)
                elif tab_key == "reports":
                    self._build_reports_tab_ui(view_frame)
                elif tab_key == "backoffice":
                    self._build_backoffice_tab_ui(view_frame)
                
                self.update_idletasks()
            finally:
                # Minimum 450ms display duration so user clearly sees the progress bar & timer counting up!
                elapsed_ms = int((time.time() - t0) * 1000)
                remaining_ms = max(50, 450 - elapsed_ms)

                def _finish():
                    timer_active[0] = False
                    try:
                        pbar.stop()
                        overlay.destroy()
                    except Exception:
                        pass
                    self.after(60, lambda: self._focus_tab_search_field(tab_key))

                self.after(remaining_ms, _finish)

        self.after(60, _deferred_build)"""

if old_loading_method in content:
    content = content.replace(old_loading_method, new_loading_method)
    print("Overlay parent updated to content_area with forced idletasks update.")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
