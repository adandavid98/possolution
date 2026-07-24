with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

calendar_class_code = '''import calendar

class CTkCalendarPopup(ctk.CTkToplevel):
    """Modern Dark-Themed Floating Calendar Picker Component"""
    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
        super().__init__(parent)
        self.title("Seleccionar Fecha")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0F172A")
        
        self.on_select_callback = on_select_callback
        self.selected_date = initial_date or datetime.date.today()
        self.curr_year = self.selected_date.year
        self.curr_month = self.selected_date.month

        # Calculate position near btn_widget or mouse
        width, height = 310, 340
        if btn_widget and btn_widget.winfo_exists():
            bx = btn_widget.winfo_rootx()
            by = btn_widget.winfo_rooty() + btn_widget.winfo_height() + 4
            self.geometry(f"{width}x{height}+{bx}+{by}")
        else:
            self.geometry(f"{width}x{height}")

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F172A", border_width=2, border_color="#334155", corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self._build_header()
        self._build_weekdays()
        self._build_grid()

        self.bind("<FocusOut>", lambda e: self.after(100, self._check_close))
        self.bind("<Escape>", lambda e: self.destroy())

    def _check_close(self):
        try:
            focus_widget = self.focus_get()
            if focus_widget is None or not str(focus_widget).startswith(str(self)):
                self.destroy()
        except Exception:
            pass

    def _build_header(self):
        hdr = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=(8, 4))

        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_month_year = ctk.CTkLabel(hdr, text=f"{months_es[self.curr_month]} {self.curr_year}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC")
        self.lbl_month_year.pack(side="left", padx=4)

        btn_next = ctk.CTkButton(hdr, text="▶", width=26, height=26, fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=10), command=lambda: self._change_month(1))
        btn_next.pack(side="right", padx=2)

        btn_prev = ctk.CTkButton(hdr, text="◀", width=26, height=26, fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=10), command=lambda: self._change_month(-1))
        btn_prev.pack(side="right", padx=2)

    def _build_weekdays(self):
        wf = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        wf.pack(fill="x", padx=8, pady=(2, 4))

        days_headers = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
        for d in days_headers:
            ctk.CTkLabel(wf, text=d, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8", width=38).pack(side="left", padx=1)

    def _build_grid(self):
        if hasattr(self, 'grid_frame'):
            self.grid_frame.destroy()

        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        cal = calendar.Calendar(firstweekday=6)
        month_days = list(cal.itermonthdates(self.curr_year, self.curr_month))
        while len(month_days) < 42:
            month_days.append(month_days[-1] + datetime.timedelta(days=1))

        rows = [month_days[i:i+7] for i in range(0, 42, 7)]
        today = datetime.date.today()

        for r_idx, row in enumerate(rows):
            rf = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
            rf.pack(fill="x", pady=1)

            for d_idx, d_date in enumerate(row):
                is_curr_month = (d_date.month == self.curr_month)
                is_selected = (d_date == self.selected_date)
                is_today = (d_date == today)

                if is_selected:
                    fg = "#84CC16" # Lime Green
                    h_color = "#65A30D"
                    t_color = "#0F172A"
                elif is_curr_month:
                    fg = "#1E293B"
                    h_color = "#334155"
                    t_color = "#F8FAFC"
                else:
                    fg = "#0F172A"
                    h_color = "#1E293B"
                    t_color = "#475569"

                btn = ctk.CTkButton(
                    rf, text=str(d_date.day), width=38, height=30,
                    fg_color=fg, hover_color=h_color, text_color=t_color,
                    font=ctk.CTkFont(size=11, weight="bold" if (is_selected or is_today) else "normal"),
                    corner_radius=15 if is_selected else 6,
                    command=lambda target_date=d_date: self._select_day(target_date)
                )
                btn.pack(side="left", padx=1)

    def _change_month(self, delta):
        m = self.curr_month + delta
        y = self.curr_year
        if m > 12:
            m = 1; y += 1
        elif m < 1:
            m = 12; y -= 1
        self.curr_month = m
        self.curr_year = y

        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_month_year.configure(text=f"{months_es[self.curr_month]} {self.curr_year}")
        self._build_grid()

    def _select_day(self, target_date):
        self.selected_date = target_date
        if self.on_select_callback:
            self.on_select_callback(target_date)
        self.destroy()
'''

# 1. Insert CTkCalendarPopup class definition at top of app_gui.py (before POSApp)
if "class CTkCalendarPopup" not in content:
    content = calendar_class_code + "\n\n" + content

# 2. Add Calendar Popup Button to Reports Period Bar
old_period_bar_buttons = """        # Date Filter Dropdown
        ctk.CTkLabel(period_bar, text="Fecha:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(6, 2))
        self._cmb_report_date_list = ctk.CTkComboBox(
            period_bar, values=["Seleccionar..."], width=190, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_date_combo_selected
        )
        self._cmb_report_date_list.pack(side="left", padx=2)"""

new_period_bar_buttons = """        # Date Filter Dropdown
        ctk.CTkLabel(period_bar, text="Fecha:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(6, 2))
        self._cmb_report_date_list = ctk.CTkComboBox(
            period_bar, values=["Seleccionar..."], width=170, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_date_combo_selected
        )
        self._cmb_report_date_list.pack(side="left", padx=2)

        # Calendar Popup Trigger Button
        self._btn_report_calendar = ctk.CTkButton(
            period_bar, text="📅 Calendario", width=110, height=32,
            fg_color="#84CC16", hover_color="#65A30D", text_color="#0F172A",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._open_report_calendar_popup
        )
        self._btn_report_calendar.pack(side="left", padx=(2, 4))"""

if old_period_bar_buttons in content:
    content = content.replace(old_period_bar_buttons, new_period_bar_buttons)

# 3. Add _open_report_calendar_popup handler to POSApp
popup_handler_code = '''    def _open_report_calendar_popup(self):
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
        )'''

if "def _open_report_calendar_popup" not in content:
    content = content.replace("    def _on_report_date_combo_selected(self, val):", popup_handler_code + "\n\n    def _on_report_date_combo_selected(self, val):")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Calendar popup integration complete.")
