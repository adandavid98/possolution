with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update content_area configuration in show_main_dashboard
old_content_area = """        self.content_area = ctk.CTkFrame(main_body, fg_color="#0F172A", corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)"""

new_content_area = """        self.content_area = ctk.CTkFrame(main_body, fg_color="#0F172A", corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)"""

if old_content_area in content:
    content = content.replace(old_content_area, new_content_area)

# 2. Update _prewarm_permitted_modules to use grid stack and restore welcome tab on finish
old_prewarm = """    def _prewarm_permitted_modules(self):
        if not hasattr(self, 'current_user') or not self.current_user:
            return

        tabs_to_warm = ["pos", "inventory", "caja", "reports", "backoffice"]
        
        def _warm_step(idx):
            if idx >= len(tabs_to_warm):
                return
            tab_key = tabs_to_warm[idx]
            if UserModel.has_permission(self.current_user, tab_key):
                if not hasattr(self, '_tab_views') or self._tab_views is None:
                    self._tab_views = {}
                if tab_key not in self._tab_views:
                    view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
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
                        print(f"Prewarm module {tab_key} notice:", e)
            self.after(20, lambda: _warm_step(idx + 1))

        self.after(20, lambda: _warm_step(0))"""

new_prewarm = """    def _prewarm_permitted_modules(self):
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
                        print(f"Prewarm module {tab_key} notice:", e)
            self.after(15, lambda: _warm_step(idx + 1))

        self.after(15, lambda: _warm_step(0))"""

if old_prewarm in content:
    content = content.replace(old_prewarm, new_prewarm)

# 3. Update show_tab to use tkraise() without re-rendering tables on every switch
old_show_tab = """    def show_tab(self, tab_key):
        self._highlight_nav_btn(tab_key)

        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}

        # Hide current active tab view
        if hasattr(self, '_active_tab_key') and self._active_tab_key and self._active_tab_key in self._tab_views:
            if self._active_tab_key != tab_key and self._tab_views[self._active_tab_key].winfo_exists():
                self._tab_views[self._active_tab_key].pack_forget()

        # If tab view already built, show it instantly! (0ms response)
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].pack(fill="both", expand=True)
            self._active_tab_key = tab_key

            # Lightweight data refresh when shown
            if tab_key == "inventory" and hasattr(self, '_render_inventory_table'):
                self._render_inventory_table()
            elif tab_key == "backoffice" and hasattr(self, '_render_bo_products_table'):
                self._render_bo_products_table()
            elif tab_key == "pos" and hasattr(self, 'ent_pos_search'):
                self.after(50, lambda: self.ent_pos_search.focus())
            return

        # Otherwise build tab view container for the first time
        view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
        view_frame.pack(fill="both", expand=True)
        self._tab_views[tab_key] = view_frame
        self._active_tab_key = tab_key

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
            self._build_backoffice_tab_ui(view_frame)"""

new_show_tab = """    def show_tab(self, tab_key):
        self._highlight_nav_btn(tab_key)

        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}

        self._active_tab_key = tab_key

        # If tab view already built, bring to front instantly with tkraise (0ms)
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].tkraise()
            if tab_key == "pos" and hasattr(self, 'ent_pos_search'):
                self.after(50, lambda: self.ent_pos_search.focus())
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
            self._build_backoffice_tab_ui(view_frame)"""

if old_show_tab in content:
    content = content.replace(old_show_tab, new_show_tab)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Grid stack refactoring complete.")
