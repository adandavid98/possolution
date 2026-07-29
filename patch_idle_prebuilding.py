"""Patch app_gui.py to implement Strategy 2: Idle Pre-rendering of modules in background."""
import re

print("=== APPLYING IDLE PRE-RENDERING OPTIMIZATION ===")

with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add _start_idle_tab_prebuilding method to POSApp
idle_prebuild_code = '''
    def _start_idle_tab_prebuilding(self):
        """Silently pre-renders permitted tabs in background idle time for 0.0s instant switching."""
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
'''

if "_start_idle_tab_prebuilding" not in code:
    code = code.replace("    def show_tab(self, tab_key):", idle_prebuild_code + "\n    def show_tab(self, tab_key):")

# 2. Trigger _start_idle_tab_prebuilding after loading welcome tab
old_load_welcome = """        # Always start on Welcome Dashboard upon login
        self.load_welcome_tab()"""

new_load_welcome = """        # Always start on Welcome Dashboard upon login
        self.load_welcome_tab()
        self._start_idle_tab_prebuilding()"""

code = code.replace(old_load_welcome, new_load_welcome)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py successfully patched with Idle Pre-rendering optimization!")
