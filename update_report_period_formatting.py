with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CTkCalendarPopup to make button blue and add global outside click listener
old_popup_init = """    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
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
        self.bind("<Escape>", lambda e: self.destroy())"""

new_popup_init = """    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
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

        # Outside click & Escape bindings
        self.click_binding = self.bind_all("<ButtonPress-1>", self._on_global_click)
        self.bind("<Escape>", lambda e: self.destroy())

    def _on_global_click(self, event):
        try:
            widget_str = str(event.widget)
            if not widget_str.startswith(str(self)):
                self.unbind_all("<ButtonPress-1>")
                self.after(10, self.destroy)
        except Exception:
            pass"""

if old_popup_init in content:
    content = content.replace(old_popup_init, new_popup_init)
    print("CTkCalendarPopup outside click updated.")

# 2. Update Calendar Button styling in Reports period bar (make it BLUE)
old_cal_btn = """        # Calendar Popup Trigger Button
        self._btn_report_calendar = ctk.CTkButton(
            period_bar, text="📅 Calendario", width=110, height=32,
            fg_color="#84CC16", hover_color="#65A30D", text_color="#0F172A",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._open_report_calendar_popup
        )"""

new_cal_btn = """        # Calendar Popup Trigger Button (BLUE)
        self._btn_report_calendar = ctk.CTkButton(
            period_bar, text="📅 Calendario", width=110, height=32,
            fg_color="#2563EB", hover_color="#1D4ED8", text_color="#F8FAFC",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._open_report_calendar_popup
        )"""

if old_cal_btn in content:
    content = content.replace(old_cal_btn, new_cal_btn)
    print("Calendar button color changed to BLUE.")

# 3. Update date formats to DD-MM-YYYY in dropdowns & range indicators
old_dropdown_logic = """    def _update_report_date_dropdown_options(self):
        mode = getattr(self, '_report_granularity', 'Día')
        ref = getattr(self, '_report_ref_date', datetime.date.today())
        today = datetime.date.today()

        opts = []
        sel_idx = 0

        if mode == "Día":
            for i in range(15, -16, -1):
                d = ref + datetime.timedelta(days=i)
                tag = " (Hoy)" if d == today else (" (Ayer)" if d == today - datetime.timedelta(days=1) else "")
                lbl = d.strftime("%Y-%m-%d") + tag
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Semana":
            curr_start = ref - datetime.timedelta(days=ref.weekday())
            for i in range(5, -6, -1):
                ws = curr_start + datetime.timedelta(weeks=i)
                we = ws + datetime.timedelta(days=6)
                lbl = ws.strftime("%d/%m") + " al " + we.strftime("%d/%m/%Y")
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Mes":
            months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            for i in range(6, -7, -1):
                m = ref.month + i
                y = ref.year
                while m > 12: m -= 12; y += 1
                while m < 1: m += 12; y -= 1
                lbl = months_es[m] + " " + str(y)
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Año":
            for i in range(3, -4, -1):
                lbl = str(ref.year + i)
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        if hasattr(self, '_cmb_report_date_list'):
            self._cmb_report_date_list.configure(values=opts)
            if opts and sel_idx < len(opts):
                self._cmb_report_date_list.set(opts[sel_idx])

        # Update Range Label
        s_str, e_str = self._get_report_date_bounds()
        if s_str == e_str:
            range_txt = f"📍 {s_str}"
        else:
            range_txt = f"📍 {s_str} al {e_str}"
        if hasattr(self, '_lbl_report_period_range'):
            self._lbl_report_period_range.configure(text=range_txt)"""

new_dropdown_logic = """    def _update_report_date_dropdown_options(self):
        mode = getattr(self, '_report_granularity', 'Día')
        ref = getattr(self, '_report_ref_date', datetime.date.today())
        today = datetime.date.today()

        opts = []
        sel_idx = 0

        if mode == "Día":
            for i in range(15, -16, -1):
                d = ref + datetime.timedelta(days=i)
                tag = " (Hoy)" if d == today else (" (Ayer)" if d == today - datetime.timedelta(days=1) else "")
                lbl = d.strftime("%d-%m-%Y") + tag
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Semana":
            curr_start = ref - datetime.timedelta(days=ref.weekday())
            for i in range(5, -6, -1):
                ws = curr_start + datetime.timedelta(weeks=i)
                we = ws + datetime.timedelta(days=6)
                lbl = ws.strftime("%d-%m-%Y") + " al " + we.strftime("%d-%m-%Y")
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Mes":
            months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            for i in range(6, -7, -1):
                m = ref.month + i
                y = ref.year
                while m > 12: m -= 12; y += 1
                while m < 1: m += 12; y -= 1
                lbl = months_es[m] + " " + str(y)
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Año":
            for i in range(3, -4, -1):
                lbl = str(ref.year + i)
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        if hasattr(self, '_cmb_report_date_list'):
            self._cmb_report_date_list.configure(values=opts)
            if opts and sel_idx < len(opts):
                self._cmb_report_date_list.set(opts[sel_idx])

        # Update Range Label with DD-MM-YYYY format
        s_raw, e_raw = self._get_report_date_bounds()
        try:
            s_dt = datetime.datetime.strptime(s_raw, "%Y-%m-%d")
            e_dt = datetime.datetime.strptime(e_raw, "%Y-%m-%d")
            s_formatted = s_dt.strftime("%d-%m-%Y")
            e_formatted = e_dt.strftime("%d-%m-%Y")
        except Exception:
            s_formatted, e_formatted = s_raw, e_raw

        if s_formatted == e_formatted:
            range_txt = f"📍 {s_formatted}"
        else:
            range_txt = f"📍 {s_formatted} al {e_formatted}"
        if hasattr(self, '_lbl_report_period_range'):
            self._lbl_report_period_range.configure(text=range_txt)"""

if old_dropdown_logic in content:
    content = content.replace(old_dropdown_logic, new_dropdown_logic)
    print("Dropdown logic & DD-MM-YYYY format updated.")

# 4. Update _on_report_date_combo_selected parsing for DD-MM-YYYY
old_combo_selected = """    def _on_report_date_combo_selected(self, val):
        mode = getattr(self, '_report_granularity', 'Día')
        today = datetime.date.today()

        try:
            if mode == "Día":
                raw_d = val.split(" ")[0].strip()
                self._report_ref_date = datetime.datetime.strptime(raw_d, "%Y-%m-%d").date()
            elif mode == "Semana":
                # Parse date from string
                parts = val.split(" al ")
                if len(parts) == 2:
                    raw_end = parts[1].strip()
                    self._report_ref_date = datetime.datetime.strptime(raw_end, "%d/%m/%Y").date()
            elif mode == "Mes":
                months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                m_str, y_str = val.split(" ")
                m_idx = months_es.index(m_str.strip())
                self._report_ref_date = datetime.date(int(y_str), m_idx, 1)
            elif mode == "Año":
                self._report_ref_date = datetime.date(int(val.strip()), 1, 1)
        except Exception as e:
            print("Error parsing report date combo:", e)

        self._update_report_date_dropdown_options()
        self._render_report_content()"""

new_combo_selected = """    def _on_report_date_combo_selected(self, val):
        mode = getattr(self, '_report_granularity', 'Día')
        today = datetime.date.today()

        try:
            if mode == "Día":
                raw_d = val.split(" ")[0].strip()
                self._report_ref_date = datetime.datetime.strptime(raw_d, "%d-%m-%Y").date()
            elif mode == "Semana":
                parts = val.split(" al ")
                if len(parts) == 2:
                    raw_end = parts[1].strip()
                    self._report_ref_date = datetime.datetime.strptime(raw_end, "%d-%m-%Y").date()
            elif mode == "Mes":
                months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                m_str, y_str = val.split(" ")
                m_idx = months_es.index(m_str.strip())
                self._report_ref_date = datetime.date(int(y_str), m_idx, 1)
            elif mode == "Año":
                self._report_ref_date = datetime.date(int(val.strip()), 1, 1)
        except Exception as e:
            print("Error parsing report date combo:", e)

        self._update_report_date_dropdown_options()
        self._render_report_content()"""

if old_combo_selected in content:
    content = content.replace(old_combo_selected, new_combo_selected)
    print("Combo selection parsing updated.")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("update_report_period_formatting complete.")
