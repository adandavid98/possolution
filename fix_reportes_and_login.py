with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove pre-warming call in show_main_dashboard so login is instant with 0 lag
old_dashboard_end = """        # Always start on Welcome Dashboard upon login
        self.load_welcome_tab()

        # Background pre-warming of all permitted modules for instant 0ms switching
        self.after(50, self._prewarm_permitted_modules)"""

new_dashboard_end = """        # Always start on Welcome Dashboard upon login
        self.load_welcome_tab()"""

if old_dashboard_end in content:
    content = content.replace(old_dashboard_end, new_dashboard_end)

# 2. Convert load_reports_tab to use show_tab("reports") and _build_reports_tab_ui
old_reports_head = """    def load_reports_tab(self):
        self.clear_content()

        # --- State ---
        self._report_period = "Hoy"
        self._report_type = "General Consolidado"
        self._report_start_date = ""
        self._report_end_date = ""

        outer = ctk.CTkFrame(self.content_area, fg_color="transparent")"""

new_reports_head = """    def load_reports_tab(self):
        self.show_tab("reports")

    def _build_reports_tab_ui(self, parent):
        # --- State ---
        self._report_period = "Hoy"
        self._report_type = "General Consolidado"
        self._report_start_date = ""
        self._report_end_date = ""

        outer = ctk.CTkFrame(parent, fg_color="transparent")"""

if old_reports_head in content:
    content = content.replace(old_reports_head, new_reports_head)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Reportes & login fix complete.")
