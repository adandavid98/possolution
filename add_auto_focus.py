with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add helper _focus_tab_search_field to POSApp
focus_helper = """    def _focus_tab_search_field(self, tab_key):
        try:
            if tab_key == "pos" and hasattr(self, 'ent_pos_search') and self.ent_pos_search.winfo_exists():
                self.ent_pos_search.focus_set()
                self.ent_pos_search.focus()
            elif tab_key == "inventory" and hasattr(self, 'ent_inv_search') and self.ent_inv_search.winfo_exists():
                self.ent_inv_search.focus_set()
                self.ent_inv_search.focus()
            elif tab_key == "backoffice" and hasattr(self, '_ent_bo_search_prod') and self._ent_bo_search_prod.winfo_exists():
                self._ent_bo_search_prod.focus_set()
                self._ent_bo_search_prod.focus()
        except Exception:
            pass"""

# Insert focus_helper before _highlight_nav_btn
if "def _focus_tab_search_field" not in content:
    content = content.replace("    def _highlight_nav_btn(self, active_key):", focus_helper + "\n\n    def _highlight_nav_btn(self, active_key):")

# 2. Update show_tab to trigger _focus_tab_search_field both on tkraise and on initial build
old_show_tab_check = """        # If tab view already built, bring to front instantly with tkraise (0ms)
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].tkraise()
            if tab_key == "pos" and hasattr(self, 'ent_pos_search'):
                self.after(50, lambda: self.ent_pos_search.focus())
            return"""

new_show_tab_check = """        # If tab view already built, bring to front instantly with tkraise (0ms)
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].tkraise()
            self.after(60, lambda tk=tab_key: self._focus_tab_search_field(tk))
            return"""

if old_show_tab_check in content:
    content = content.replace(old_show_tab_check, new_show_tab_check)

# Also trigger focus after initial build at end of show_tab
old_show_tab_end = """        elif tab_key == "backoffice":
            self._build_backoffice_tab_ui(view_frame)"""

new_show_tab_end = """        elif tab_key == "backoffice":
            self._build_backoffice_tab_ui(view_frame)
        self.after(60, lambda tk=tab_key: self._focus_tab_search_field(tk))"""

if old_show_tab_end in content:
    content = content.replace(old_show_tab_end, new_show_tab_end)

# 3. Update Back Office tabview creation to focus search entry when switching sub-tabs
old_bo_tabview = """        self._bo_tabview = ctk.CTkTabview(outer, fg_color="#0F172A", segmented_button_fg_color="#1E293B",
                                          segmented_button_selected_color="#2563EB", segmented_button_selected_hover_color="#1D4ED8")"""

new_bo_tabview = """        def _on_bo_tab_change():
            try:
                sel = self._bo_tabview.get()
                if "Artículos" in sel and hasattr(self, '_ent_bo_search_prod') and self._ent_bo_search_prod.winfo_exists():
                    self.after(60, lambda: (self._ent_bo_search_prod.focus_set(), self._ent_bo_search_prod.focus()))
                elif "Clientes" in sel and hasattr(self, '_ent_bo_search_cust') and self._ent_bo_search_cust.winfo_exists():
                    self.after(60, lambda: (self._ent_bo_search_cust.focus_set(), self._ent_bo_search_cust.focus()))
            except Exception:
                pass

        self._bo_tabview = ctk.CTkTabview(outer, fg_color="#0F172A", segmented_button_fg_color="#1E293B",
                                          segmented_button_selected_color="#2563EB", segmented_button_selected_hover_color="#1D4ED8",
                                          command=_on_bo_tab_change)"""

if old_bo_tabview in content:
    content = content.replace(old_bo_tabview, new_bo_tabview)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("auto focus enhancement complete.")
