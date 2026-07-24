with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CTkCalendarPopup to add inside-app geometry clamping & Month/Year Picker View
new_calendar_class = '''class CTkCalendarPopup(ctk.CTkToplevel):
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
        self.showing_month_selector = False

        # Calculate position constrained strictly INSIDE the parent app window
        width, height = 320, 350
        parent_root = parent.winfo_toplevel()
        rx = parent_root.winfo_rootx()
        ry = parent_root.winfo_rooty()
        rw = max(parent_root.winfo_width(), 800)
        rh = max(parent_root.winfo_height(), 600)

        if btn_widget and btn_widget.winfo_exists():
            bx = btn_widget.winfo_rootx()
            by = btn_widget.winfo_rooty() + btn_widget.winfo_height() + 4
        else:
            bx = rx + (rw - width) // 2
            by = ry + (rh - height) // 2

        # Clamp coordinates so popover NEVER leaves app window bounds
        final_x = max(rx + 8, min(bx, rx + rw - width - 8))
        final_y = max(ry + 8, min(by, ry + rh - height - 8))
        self.geometry(f"{width}x{height}+{final_x}+{final_y}")

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
            pass

    def _build_header(self):
        if hasattr(self, 'hdr_frame') and self.hdr_frame.winfo_exists():
            self.hdr_frame.destroy()

        self.hdr_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.hdr_frame.pack(fill="x", padx=10, pady=(8, 4))

        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Clickable Month & Year Header Label to toggle Month/Year selector!
        self.lbl_month_year = ctk.CTkButton(
            self.hdr_frame,
            text=f"{months_es[self.curr_month]} {self.curr_year} ▾",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent", hover_color="#1E293B", text_color="#38BDF8",
            command=self._toggle_month_year_selector
        )
        self.lbl_month_year.pack(side="left", padx=2)

        btn_next = ctk.CTkButton(self.hdr_frame, text="▶", width=26, height=26, fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=10), command=lambda: self._change_month(1))
        btn_next.pack(side="right", padx=2)

        btn_prev = ctk.CTkButton(self.hdr_frame, text="◀", width=26, height=26, fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=10), command=lambda: self._change_month(-1))
        btn_prev.pack(side="right", padx=2)

    def _toggle_month_year_selector(self):
        self.showing_month_selector = not self.showing_month_selector
        if self.showing_month_selector:
            self._build_month_year_grid()
        else:
            self._build_grid()

    def _build_weekdays(self):
        if hasattr(self, 'wf_frame') and self.wf_frame.winfo_exists():
            self.wf_frame.destroy()

        self.wf_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.wf_frame.pack(fill="x", padx=8, pady=(2, 4))

        days_headers = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
        for d in days_headers:
            ctk.CTkLabel(self.wf_frame, text=d, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8", width=38).pack(side="left", padx=1)

    def _build_grid(self):
        if hasattr(self, 'grid_frame') and self.grid_frame.winfo_exists():
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
                    fg = "#2563EB" # Blue matching button
                    h_color = "#1D4ED8"
                    t_color = "#F8FAFC"
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

    def _build_month_year_grid(self):
        if hasattr(self, 'grid_frame') and self.grid_frame.winfo_exists():
            self.grid_frame.destroy()

        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Year Controls Header
        yr_hdr = ctk.CTkFrame(self.grid_frame, fg_color="#1E293B", corner_radius=6)
        yr_hdr.pack(fill="x", pady=(4, 8))

        ctk.CTkButton(yr_hdr, text="◀", width=28, height=26, fg_color="transparent", hover_color="#334155", command=lambda: self._change_year(-1)).pack(side="left", padx=2)
        ctk.CTkLabel(yr_hdr, text=f"Año {self.curr_year}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC").pack(side="left", expand=True)
        ctk.CTkButton(yr_hdr, text="▶", width=28, height=26, fg_color="transparent", hover_color="#334155", command=lambda: self._change_year(1)).pack(side="right", padx=2)

        # 12 Month Grid (4 rows x 3 cols)
        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        m_grid = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        m_grid.pack(fill="both", expand=True)

        for idx in range(1, 13):
            r = (idx - 1) // 3
            c = (idx - 1) % 3
            m_name = months_es[idx]
            is_sel_m = (idx == self.curr_month)

            btn = ctk.CTkButton(
                m_grid, text=m_name, width=88, height=36,
                fg_color="#2563EB" if is_sel_m else "#1E293B",
                hover_color="#1D4ED8" if is_sel_m else "#334155",
                text_color="#F8FAFC",
                font=ctk.CTkFont(size=11, weight="bold" if is_sel_m else "normal"),
                command=lambda m_num=idx: self._select_month(m_num)
            )
            btn.grid(row=r, column=c, padx=3, pady=3)

    def _change_year(self, delta):
        self.curr_year += delta
        self._build_month_year_grid()

    def _select_month(self, m_num):
        self.curr_month = m_num
        self.showing_month_selector = False
        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_month_year.configure(text=f"{months_es[self.curr_month]} {self.curr_year} ▾")
        self._build_grid()

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
        self.lbl_month_year.configure(text=f"{months_es[self.curr_month]} {self.curr_year} ▾")
        if self.showing_month_selector:
            self._build_month_year_grid()
        else:
            self._build_grid()

    def _select_day(self, target_date):
        self.selected_date = target_date
        if self.on_select_callback:
            self.on_select_callback(target_date)
        self.destroy()'''

# Extract old CTkCalendarPopup block
old_cal_class_start = "class CTkCalendarPopup(ctk.CTkToplevel):"
old_cal_class_end = "import os\nimport sys"

parts = content.split(old_cal_class_start)
header_code = parts[0]
after_class = parts[1].split(old_cal_class_end, 1)[1]

content = header_code + new_calendar_class + "\n\nimport os\nimport sys" + after_class

# 2. Update _on_report_granularity_changed to hide date combo / nav buttons when Personalizado is selected
old_gran_changed = """    def _on_report_granularity_changed(self, mode):
        self._report_granularity = mode
        if mode == "Personalizado":
            self._custom_date_frame.pack(side="left", padx=4)
            self._cmb_report_date_list.configure(state="disabled")
            self._btn_report_prev.configure(state="disabled")
            self._btn_report_next.configure(state="disabled")
        else:
            self._custom_date_frame.pack_forget()
            self._cmb_report_date_list.configure(state="normal")
            self._btn_report_prev.configure(state="normal")
            self._btn_report_next.configure(state="normal")
            self._update_report_date_dropdown_options()
            self._render_report_content()"""

new_gran_changed = """    def _on_report_granularity_changed(self, mode):
        self._report_granularity = mode
        if mode == "Personalizado":
            if hasattr(self, '_cmb_report_date_list') and self._cmb_report_date_list.master.winfo_exists():
                self._cmb_report_date_list.master.pack_forget()
            if hasattr(self, '_btn_report_prev') and self._btn_report_prev.winfo_exists():
                self._btn_report_prev.pack_forget()
            if hasattr(self, '_btn_report_next') and self._btn_report_next.winfo_exists():
                self._btn_report_next.pack_forget()
            self._custom_date_frame.pack(side="left", padx=4)
        else:
            self._custom_date_frame.pack_forget()
            if hasattr(self, '_btn_report_prev') and self._btn_report_prev.winfo_exists():
                self._btn_report_prev.pack(side="left", padx=(6, 2))
            if hasattr(self, '_cmb_report_date_list') and self._cmb_report_date_list.master.winfo_exists():
                self._cmb_report_date_list.master.pack(side="left", padx=2)
            if hasattr(self, '_btn_report_next') and self._btn_report_next.winfo_exists():
                self._btn_report_next.pack(side="left", padx=(4, 6))
            self._update_report_date_dropdown_options()
            self._render_report_content()"""

if old_gran_changed in content:
    content = content.replace(old_gran_changed, new_gran_changed)
    print("_on_report_granularity_changed updated.")

# 3. Update _apply_custom_date & _get_report_date_bounds to parse DD-MM-YYYY -> YYYY-MM-DD properly
old_apply_custom = """    def _apply_custom_date(self):
        self._report_start_date = self._ent_start.get().strip()
        self._report_end_date = self._ent_end.get().strip()
        self._render_report_content()"""

new_apply_custom = """    def _apply_custom_date(self):
        raw_start = self._ent_start.get().strip()
        raw_end = self._ent_end.get().strip()

        def to_iso(d_str):
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(d_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    pass
            return datetime.date.today().strftime("%Y-%m-%d")

        self._report_start_date = to_iso(raw_start) if raw_start else datetime.date.today().strftime("%Y-%m-%d")
        self._report_end_date = to_iso(raw_end) if raw_end else datetime.date.today().strftime("%Y-%m-%d")
        self._render_report_content()"""

if old_apply_custom in content:
    content = content.replace(old_apply_custom, new_apply_custom)
    print("_apply_custom_date updated with ISO parsing.")

# 4. Update _get_report_date_bounds return format (YYYY-MM-DD)
old_bounds = """        elif mode == "Personalizado":
            s, e = None, None
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                if not s:
                    try: s = datetime.datetime.strptime(self._report_start_date, fmt).date()
                    except Exception: pass
                if not e:
                    try: e = datetime.datetime.strptime(self._report_end_date, fmt).date()
                    except Exception: pass
            if not s: s = datetime.date.today()
            if not e: e = datetime.date.today()"""

new_bounds = """        elif mode == "Personalizado":
            s, e = None, None
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                if not s:
                    try: s = datetime.datetime.strptime(self._report_start_date, fmt).date()
                    except Exception: pass
                if not e:
                    try: e = datetime.datetime.strptime(self._report_end_date, fmt).date()
                    except Exception: pass
            if not s: s = datetime.date.today()
            if not e: e = datetime.date.today()"""

if old_bounds in content:
    content = content.replace(old_bounds, new_bounds)
    print("_get_report_date_bounds updated.")

# 5. Update _open_calendar_for_entry callback to auto-trigger _apply_custom_date
old_entry_cal = """    def _open_calendar_for_entry(self, entry_widget):
        def _on_date_picked(picked_date):
            d_str = picked_date.strftime("%d-%m-%Y")
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d_str)"""

new_entry_cal = """    def _open_calendar_for_entry(self, entry_widget):
        def _on_date_picked(picked_date):
            d_str = picked_date.strftime("%d-%m-%Y")
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d_str)
            self._apply_custom_date()"""

if old_entry_cal in content:
    content = content.replace(old_entry_cal, new_entry_cal)
    print("_open_calendar_for_entry callback updated.")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("apply_all_4_calendar_fixes complete.")
