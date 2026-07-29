"""Patch app_gui.py to remove Idle Pre-building, restoring first-time progress bar loading and instant 0.0s cached switching."""

print("=== REMOVING IDLE PRE-BUILDING & RESTORING LAZY PROGRESS BAR CACHING ===")

with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove call to _start_idle_tab_prebuilding() from show_main_interface
code = code.replace("        self._start_idle_tab_prebuilding()\n", "")
code = code.replace("        self._start_idle_tab_prebuilding()", "")

# 2. Remove _start_idle_tab_prebuilding method definition if present
old_prebuild_method = """    def _start_idle_tab_prebuilding(self):
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

        self.after(250, lambda: _prebuild_next(0))"""

code = code.replace(old_prebuild_method, "")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py successfully updated: Idle Pre-building removed!")
