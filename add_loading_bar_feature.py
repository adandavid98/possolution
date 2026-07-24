with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import time if not present
if "import time" not in content:
    content = content.replace("import datetime", "import datetime\nimport time")
    print("Added import time")

# 2. Remove _prewarm_permitted_modules and update show_tab & _build_tab_with_loading_bar
old_show_tab_section = """    def _prewarm_permitted_modules(self):
        if not hasattr(self, 'current_user') or not self.current_user:
            return

        tabs_to_warm = ["pos", "inventory", "caja", "reports", "backoffice"]
        
        def _warm_step(idx):
            if idx >= len(tabs_to_warm):
                if hasattr(self, '_tab_views') and "welcome" in self._tab_views:
                    if self._tab_views["welcome"].winfo_exists():
                        self._tab_views["welcome"].tkraise()
                return
            tab_key = tabs_to_warm[idx]
            if UserModel.has_permission(self.current_user, tab_key):
                if not hasattr(self, '_tab_views') or self._tab_views is None:
                    self._tab_views = {}
                if tab_key not in self._tab_views:
                    view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
                    view_frame.grid(row=0, column=0, sticky="nsew")
                    self._tab_views[tab_key] = view_frame
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
                    except Exception as e:
                        print("Prewarm module notice:", e)
            self.after(15, lambda: _warm_step(idx + 1))

        self.after(15, lambda: _warm_step(0))

    def show_tab(self, tab_key):
        self._highlight_nav_btn(tab_key)

        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}

        self._active_tab_key = tab_key

        # If tab view already built, bring to front instantly with tkraise (0ms)
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].tkraise()
            self.after(60, lambda tk=tab_key: self._focus_tab_search_field(tk))
            return

        # Otherwise build tab view container for the first time
        view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
        view_frame.grid(row=0, column=0, sticky="nsew")
        self._tab_views[tab_key] = view_frame
        view_frame.tkraise()

        if tab_key == "welcome":
            self._build_welcome_tab_ui(view_frame)
        elif tab_key == "pos":
            self._build_pos_tab_ui(view_frame)
        elif tab_key == "inventory":
            self._build_inventory_tab_ui(view_frame)
        elif tab_key == "caja":
            self._build_caja_tab_ui(view_frame)
        elif tab_key == "reports":
            self._build_reports_tab_ui(view_frame)
        elif tab_key == "backoffice":
            self._build_backoffice_tab_ui(view_frame)

        self.after(60, lambda: self._focus_tab_search_field(tab_key))"""

new_show_tab_section = """    def show_tab(self, tab_key):
        self._highlight_nav_btn(tab_key)

        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}

        self._active_tab_key = tab_key

        # If tab view already built once in session, bring to front INSTANTLY (0 ms)
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].tkraise()
            self.after(60, lambda tk=tab_key: self._focus_tab_search_field(tk))
            return

        # Otherwise: First time opening this module! Create container & show Indeterminate Loading Bar
        view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
        view_frame.grid(row=0, column=0, sticky="nsew")
        self._tab_views[tab_key] = view_frame
        view_frame.tkraise()

        if tab_key == "welcome":
            self._build_welcome_tab_ui(view_frame)
            self.after(60, lambda: self._focus_tab_search_field("welcome"))
        else:
            self._build_tab_with_loading_bar(tab_key, view_frame)

    def _build_tab_with_loading_bar(self, tab_key, view_frame):
        module_titles = {
            "pos": "Caja / POS",
            "inventory": "Inventario & Alertas",
            "caja": "Apertura / Cierre de Caja",
            "reports": "Reportes & Ventas",
            "backoffice": "Back Office"
        }
        title_name = module_titles.get(tab_key, "Módulo")

        # Overlay Loading Container
        overlay = ctk.CTkFrame(view_frame, fg_color="#0F172A")
        overlay.place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(overlay, fg_color="#1E293B", corner_radius=12, border_width=1, border_color="#334155")
        card.pack(padx=30, pady=30)

        lbl_title = ctk.CTkLabel(
            card, text=f"⏳ Cargando Módulo de {title_name}...",
            font=ctk.CTkFont(size=15, weight="bold"), text_color="#F8FAFC"
        )
        lbl_title.pack(padx=30, pady=(20, 10))

        # Indeterminate Sliding Progress Bar
        pbar = ctk.CTkProgressBar(card, mode="indeterminate", width=320, height=12, progress_color="#2563EB")
        pbar.pack(padx=30, pady=8)
        pbar.start()

        # Real-time Elapsed Time Counter
        t0 = time.time()
        lbl_timer = ctk.CTkLabel(
            card, text="⏱️ Tiempo de carga: 0.0s",
            font=ctk.CTkFont(size=12), text_color="#94A3B8"
        )
        lbl_timer.pack(padx=30, pady=(4, 8))

        sub_lbl = ctk.CTkLabel(
            card, text="Preparando interfaz y datos esenciales...",
            font=ctk.CTkFont(size=10), text_color="#64748B"
        )
        sub_lbl.pack(padx=30, pady=(0, 20))

        timer_active = [True]

        def _update_timer():
            if timer_active[0] and card.winfo_exists():
                elapsed = time.time() - t0
                lbl_timer.configure(text=f"⏱️ Tiempo de carga: {elapsed:.1f}s")
                self.after(100, _update_timer)

        _update_timer()

        # Build actual module UI asynchronously after 30ms so UI paints progress bar first!
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
            finally:
                timer_active[0] = False
                try:
                    pbar.stop()
                    overlay.destroy()
                except Exception:
                    pass
                self.after(60, lambda: self._focus_tab_search_field(tab_key))

        self.after(30, _deferred_build)"""

if old_show_tab_section in content:
    content = content.replace(old_show_tab_section, new_show_tab_section)
    print("show_tab and _build_tab_with_loading_bar updated successfully!")
else:
    print("WARNING: old_show_tab_section not found exactly in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
