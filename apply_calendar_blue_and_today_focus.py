with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update selected date color in CTkCalendarPopup to Blue (#2563EB)
old_grid_colors = """                if is_selected:
                    fg = "#84CC16" # Lime Green
                    h_color = "#65A30D"
                    t_color = "#0F172A" """

new_grid_colors = """                if is_selected:
                    fg = "#2563EB" # Blue matching button
                    h_color = "#1D4ED8"
                    t_color = "#F8FAFC" """

if "fg = \"#84CC16\"" in content:
    content = content.replace("fg = \"#84CC16\"", "fg = \"#2563EB\"")
    content = content.replace("h_color = \"#65A30D\"", "h_color = \"#1D4ED8\"")
    content = content.replace("t_color = \"#0F172A\"", "t_color = \"#F8FAFC\"")
    print("Calendar grid selected color updated to Blue.")

# 2. Update _open_report_calendar_popup logic to focus today if today is within active mode range
old_popup_open = """    def _open_report_calendar_popup(self):
        def _on_date_picked(picked_date):
            self._report_ref_date = picked_date
            self._update_report_date_dropdown_options()
            self._render_report_content()

        btn = getattr(self, '_btn_report_calendar', None)
        popup = CTkCalendarPopup(
            self,
            initial_date=getattr(self, '_report_ref_date', datetime.date.today()),
            on_select_callback=_on_date_picked,
            btn_widget=btn
        )"""

new_popup_open = """    def _open_report_calendar_popup(self):
        def _on_date_picked(picked_date):
            self._report_ref_date = picked_date
            self._update_report_date_dropdown_options()
            self._render_report_content()

        btn = getattr(self, '_btn_report_calendar', None)
        today = datetime.date.today()
        ref = getattr(self, '_report_ref_date', today)

        # Check if today falls within current active mode date range
        s_str, e_str = self._get_report_date_bounds()
        try:
            s_date = datetime.datetime.strptime(s_str, "%Y-%m-%d").date()
            e_date = datetime.datetime.strptime(e_str, "%Y-%m-%d").date()
            if s_date <= today <= e_date:
                initial_d = today
            else:
                initial_d = ref
        except Exception:
            initial_d = ref

        popup = CTkCalendarPopup(
            self,
            initial_date=initial_d,
            on_select_callback=_on_date_picked,
            btn_widget=btn
        )"""

if old_popup_open in content:
    content = content.replace(old_popup_open, new_popup_open)
    print("_open_report_calendar_popup today focus updated.")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("apply_calendar_blue_and_today_focus complete.")
