import re

with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update clear_content to reset tab views dictionary
old_clear = """    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()"""

new_clear = """    def clear_content(self):
        self._tab_views = {}
        self._active_tab_key = None
        for widget in list(self.content_area.winfo_children()):
            try:
                widget.destroy()
            except Exception:
                pass"""

if old_clear in content:
    content = content.replace(old_clear, new_clear)

# 2. Add show_tab implementation right before _highlight_nav_btn
show_tab_code = """    def show_tab(self, tab_key):
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
            self._build_backoffice_tab_ui(view_frame)

    def _highlight_nav_btn(self, active_key):"""

if 'def _highlight_nav_btn(self, active_key):' in content and 'def show_tab(self, tab_key):' not in content:
    content = content.replace('    def _highlight_nav_btn(self, active_key):', show_tab_code)

# 3. Refactor load_welcome_tab into load_welcome_tab and _build_welcome_tab_ui
old_welcome_head = """    def load_welcome_tab(self):
        self.clear_content()
        self._highlight_nav_btn("welcome")"""

new_welcome_head = """    def load_welcome_tab(self):
        self.show_tab("welcome")

    def _build_welcome_tab_ui(self, parent):"""

if old_welcome_head in content:
    content = content.replace(old_welcome_head, new_welcome_head)
    # Replace container = ctk.CTkFrame(self.content_area...
    content = content.replace(
        'container = ctk.CTkFrame(self.content_area, fg_color="#0F172A")',
        'container = ctk.CTkFrame(parent, fg_color="#0F172A")'
    )

# 4. Refactor load_pos_tab into load_pos_tab and _build_pos_tab_ui
old_pos_head = """    def load_pos_tab(self):
        self.clear_content()

        # Main container for POS
        pos_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")"""

new_pos_head = """    def load_pos_tab(self):
        self.show_tab("pos")

    def _build_pos_tab_ui(self, parent):
        # Main container for POS
        pos_frame = ctk.CTkFrame(parent, fg_color="transparent")"""

if old_pos_head in content:
    content = content.replace(old_pos_head, new_pos_head)

# 5. Refactor load_inventory_tab into load_inventory_tab and _build_inventory_tab_ui
old_inv_head = """    def load_inventory_tab(self):
        self.clear_content()

        inv_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")"""

new_inv_head = """    def load_inventory_tab(self):
        self.show_tab("inventory")

    def _build_inventory_tab_ui(self, parent):
        inv_frame = ctk.CTkFrame(parent, fg_color="transparent")"""

if old_inv_head in content:
    content = content.replace(old_inv_head, new_inv_head)

# 6. Refactor load_caja_tab into load_caja_tab and _build_caja_tab_ui
old_caja_head = """    def load_caja_tab(self):
        self.clear_content()

        caja_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")"""

new_caja_head = """    def load_caja_tab(self, force_rebuild=False):
        if force_rebuild and hasattr(self, '_tab_views') and "caja" in self._tab_views:
            if self._tab_views["caja"].winfo_exists():
                self._tab_views["caja"].destroy()
            del self._tab_views["caja"]
        self.show_tab("caja")

    def _build_caja_tab_ui(self, parent):
        caja_frame = ctk.CTkFrame(parent, fg_color="transparent")"""

if old_caja_head in content:
    content = content.replace(old_caja_head, new_caja_head)
    content = content.replace('self.load_caja_tab()', 'self.load_caja_tab(force_rebuild=True)')

# 7. Refactor load_reports_tab into load_reports_tab and _build_reports_tab_ui
old_rep_head = """    def load_reports_tab(self):
        self.clear_content()

        rep_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")"""

new_rep_head = """    def load_reports_tab(self):
        self.show_tab("reports")

    def _build_reports_tab_ui(self, parent):
        rep_frame = ctk.CTkFrame(parent, fg_color="transparent")"""

if old_rep_head in content:
    content = content.replace(old_rep_head, new_rep_head)

# 8. Refactor load_backoffice_tab into load_backoffice_tab and _build_backoffice_tab_ui
old_bo_head = """    def load_backoffice_tab(self):
        self.clear_content()
        self._highlight_nav_btn("backoffice")

        outer = ctk.CTkFrame(self.content_area, fg_color="transparent")"""

new_bo_head = """    def load_backoffice_tab(self):
        self.show_tab("backoffice")

    def _build_backoffice_tab_ui(self, parent):
        outer = ctk.CTkFrame(parent, fg_color="transparent")"""

if old_bo_head in content:
    content = content.replace(old_bo_head, new_bo_head)

# 9. Update monkey-patch list at bottom of app_gui.py
if 'POSApp._build_backoffice_tab_ui = FlipChartModal._build_backoffice_tab_ui' not in content:
    content += '\nPOSApp._build_backoffice_tab_ui = FlipChartModal._build_backoffice_tab_ui\n'

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactoring complete.")
