"""Patch app_gui.py to add Logout session reset and clean Progress Bar loading overlay for modules."""

print("=== APPLYING PROGRESS BAR & LOGOUT SESSION RESET FIXES ===")

with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update show_login to reset _tab_views and _prebuilding_status on logout
old_show_login_head = """    def show_login(self):
        self.current_user = None
        for widget in self.container.winfo_children():
            widget.destroy()"""

new_show_login_head = """    def show_login(self):
        self.current_user = None
        self._tab_views = {}
        self._prebuilding_status = {}
        for widget in self.container.winfo_children():
            widget.destroy()"""

code = code.replace(old_show_login_head, new_show_login_head)

# 2. Update _start_idle_tab_prebuilding & show_tab logic in app_gui.py
old_prebuild_and_show = """    def _start_idle_tab_prebuilding(self):
        \"\"\"Silently pre-renders permitted tabs in background idle time for 0.0s instant switching.\"\"\"
        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}

        tabs_to_prebuild = ["pos", "inventory", "caja", "reports", "backoffice"]
        tabs_to_prebuild = [t for t in tabs_to_prebuild if UserModel.has_permission(self.current_user, t)]

        def _prebuild_next(index=0):
            if index >= len(tabs_to_prebuild):
                return
            
            tab_key = tabs_to_prebuild[index]
            if self.current_user and tab_key not in self._tab_views:
                try:
                    view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
                    view_frame.grid(row=0, column=0, sticky="nsew")
                    self._tab_views[tab_key] = view_frame

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

                    if hasattr(self, '_active_tab_key') and self._active_tab_key in self._tab_views:
                        self._tab_views[self._active_tab_key].tkraise()
                except Exception as e:
                    print(f"Idle pre-building note for tab '{tab_key}':", e)

            self.after(120, lambda: _prebuild_next(index + 1))

        self.after(250, lambda: _prebuild_next(0))

    def show_tab(self, tab_key):
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
            self._build_tab_with_loading_bar(tab_key, view_frame)"""

new_prebuild_and_show = """    def _start_idle_tab_prebuilding(self):
        \"\"\"Silently pre-renders permitted tabs in background idle time for 0.0s instant switching.\"\"\"
        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}
        if not hasattr(self, '_prebuilding_status') or self._prebuilding_status is None:
            self._prebuilding_status = {}

        tabs_to_prebuild = ["pos", "inventory", "caja", "reports", "backoffice"]
        tabs_to_prebuild = [t for t in tabs_to_prebuild if UserModel.has_permission(self.current_user, t)]

        def _prebuild_next(index=0):
            if index >= len(tabs_to_prebuild) or not self.current_user:
                return
            
            tab_key = tabs_to_prebuild[index]
            if tab_key not in self._tab_views:
                try:
                    self._prebuilding_status[tab_key] = "building"
                    view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
                    view_frame.grid(row=0, column=0, sticky="nsew")
                    self._tab_views[tab_key] = view_frame

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

                    self._prebuilding_status[tab_key] = "done"

                    if hasattr(self, '_active_tab_key') and self._active_tab_key in self._tab_views:
                        self._tab_views[self._active_tab_key].tkraise()
                except Exception as e:
                    print(f"Idle pre-building note for tab '{tab_key}':", e)

            self.after(120, lambda: _prebuild_next(index + 1))

        self.after(250, lambda: _prebuild_next(0))

    def show_tab(self, tab_key):
        self._highlight_nav_btn(tab_key)

        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}
        if not hasattr(self, '_prebuilding_status') or self._prebuilding_status is None:
            self._prebuilding_status = {}

        self._active_tab_key = tab_key

        # If tab is ALREADY fully pre-built in background, bring to front INSTANTLY (0 ms)
        if self._prebuilding_status.get(tab_key) == "done" and tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].tkraise()
            self.after(60, lambda tk=tab_key: self._focus_tab_search_field(tk))
            return

        # Otherwise: Module is either being created or opened for first time! Show Progress Bar Loading Overlay
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            view_frame = self._tab_views[tab_key]
        else:
            view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
            view_frame.grid(row=0, column=0, sticky="nsew")
            self._tab_views[tab_key] = view_frame

        view_frame.tkraise()

        if tab_key == "welcome":
            self._build_welcome_tab_ui(view_frame)
            self._prebuilding_status["welcome"] = "done"
            self.after(60, lambda: self._focus_tab_search_field("welcome"))
        else:
            self._build_tab_with_loading_bar(tab_key, view_frame)"""

code = code.replace(old_prebuild_and_show, new_prebuild_and_show)

# 3. Update _build_tab_with_loading_bar to set _prebuilding_status[tab_key] = "done"
old_finish_line = """                    self.after(60, lambda: self._focus_tab_search_field(tab_key))"""
new_finish_line = """                    self._prebuilding_status[tab_key] = "done"
                    self.after(60, lambda: self._focus_tab_search_field(tab_key))"""

code = code.replace(old_finish_line, new_finish_line)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py successfully patched with progress bar loading overlay and logout reset!")
