import datetime, calendar

script_content = '''
import datetime, calendar

def _init_report_period_bar(self, outer):
    # State initialization
    self._report_granularity = "Día"
    self._report_ref_date = datetime.date.today()
    self._report_start_date = ""
    self._report_end_date = ""
'''

# Let's inspect app_gui.py and write python replacement
with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace period filter bar creation in _build_reports_tab_ui
old_period_bar = """        # ── PERIOD FILTER BAR
        period_bar = ctk.CTkFrame(outer, fg_color="#1E293B", corner_radius=8, height=46)
        period_bar.pack(fill="x", pady=(0, 8))
        period_bar.pack_propagate(False)

        ctk.CTkLabel(period_bar, text=" 📅 Período:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(10, 4))

        self._period_btns = {}
        period_options = ["Hoy", "Esta Semana", "Este Mes", "Este Año", "Personalizado"]
        for p in period_options:
            btn = ctk.CTkButton(
                period_bar, text=p, width=100, height=30,
                fg_color="#3B82F6" if p == "Hoy" else "#334155",
                hover_color="#2563EB",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda opt=p: self._select_report_period(opt)
            )
            btn.pack(side="left", padx=4, pady=6)
            self._period_btns[p] = btn

        # Custom date range (hidden by default)
        self._custom_date_frame = ctk.CTkFrame(period_bar, fg_color="transparent")
        ctk.CTkLabel(self._custom_date_frame, text="Desde:",
            font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(8, 2))
        self._ent_start = ctk.CTkEntry(self._custom_date_frame, placeholder_text="YYYY-MM-DD", width=110)
        self._ent_start.pack(side="left", padx=2)
        ctk.CTkLabel(self._custom_date_frame, text="Hasta:",
            font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(8, 2))
        self._ent_end = ctk.CTkEntry(self._custom_date_frame, placeholder_text="YYYY-MM-DD", width=110)
        self._ent_end.pack(side="left", padx=2)
        btn_apply = ctk.CTkButton(
            self._custom_date_frame, text="Aplicar", width=70, height=28,
            fg_color="#10B981", hover_color="#059669",
            command=self._apply_custom_date
        )
        btn_apply.pack(side="left", padx=6)"""

new_period_bar = """        # ── PERIOD FILTER BAR WITH DROPDOWNS & NAV BUTTONS
        period_bar = ctk.CTkFrame(outer, fg_color="#1E293B", corner_radius=8, height=48)
        period_bar.pack(fill="x", pady=(0, 8))
        period_bar.pack_propagate(False)

        ctk.CTkLabel(period_bar, text=" 📅 Modo:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(10, 4))

        self._cmb_report_granularity = ctk.CTkComboBox(
            period_bar,
            values=["Día", "Semana", "Mes", "Año", "Personalizado"],
            width=115, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_granularity_changed
        )
        self._cmb_report_granularity.set("Día")
        self._cmb_report_granularity.pack(side="left", padx=4)

        # Prev Button
        self._btn_report_prev = ctk.CTkButton(
            period_bar, text="◀ Anterior", width=85, height=32,
            fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._nav_report_period(-1)
        )
        self._btn_report_prev.pack(side="left", padx=(6, 2))

        # Date Filter Dropdown
        ctk.CTkLabel(period_bar, text="Fecha:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(6, 2))
        self._cmb_report_date_list = ctk.CTkComboBox(
            period_bar, values=["Seleccionar..."], width=190, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_date_combo_selected
        )
        self._cmb_report_date_list.pack(side="left", padx=2)

        # Next Button
        self._btn_report_next = ctk.CTkButton(
            period_bar, text="Siguiente ▶", width=85, height=32,
            fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._nav_report_period(1)
        )
        self._btn_report_next.pack(side="left", padx=(2, 6))

        # Live Range Indicator Label
        self._lbl_report_period_range = ctk.CTkLabel(
            period_bar, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8"
        )
        self._lbl_report_period_range.pack(side="left", padx=8)

        # Custom date range (hidden by default)
        self._custom_date_frame = ctk.CTkFrame(period_bar, fg_color="transparent")
        ctk.CTkLabel(self._custom_date_frame, text="Desde:",
            font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(8, 2))
        self._ent_start = ctk.CTkEntry(self._custom_date_frame, placeholder_text="YYYY-MM-DD", width=100, height=32)
        self._ent_start.pack(side="left", padx=2)
        ctk.CTkLabel(self._custom_date_frame, text="Hasta:",
            font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(8, 2))
        self._ent_end = ctk.CTkEntry(self._custom_date_frame, placeholder_text="YYYY-MM-DD", width=100, height=32)
        self._ent_end.pack(side="left", padx=2)
        btn_apply = ctk.CTkButton(
            self._custom_date_frame, text="Aplicar", width=65, height=32,
            fg_color="#10B981", hover_color="#059669",
            command=self._apply_custom_date
        )
        btn_apply.pack(side="left", padx=4)"""

if old_period_bar in content:
    content = content.replace(old_period_bar, new_period_bar)
    print("Period bar UI replaced.")
else:
    print("WARNING: old_period_bar not found!")

# Replace state initialization in _build_reports_tab_ui
old_state = """        # --- State ---
        self._report_period = "Hoy"
        self._report_type = "General Consolidado"
        self._report_start_date = ""
        self._report_end_date = """

new_state = """        # --- State ---
        self._report_granularity = "Día"
        self._report_ref_date = datetime.date.today()
        self._report_period = "Día"
        self._report_type = "General Consolidado"
        self._report_start_date = ""
        self._report_end_date = """

if old_state in content:
    content = content.replace(old_state, new_state)

# Replace old handlers with new Period Navigation & Dropdown handlers
old_handlers = """    def _select_report_period(self, period):
        self._report_period = period
        for p, btn in self._period_btns.items():
            btn.configure(fg_color="#3B82F6" if p == period else "#334155")
        if period == "Personalizado":
            self._custom_date_frame.pack(side="left", padx=4)
        else:
            self._custom_date_frame.pack_forget()
            self._render_report_content()

    def _apply_custom_date(self):
        self._report_start_date = self._ent_start.get().strip()
        self._report_end_date = self._ent_end.get().strip()
        self._render_report_content()

    def _select_report_type(self, val):
        self._report_type = val
        self._render_report_content()

    def _get_period_label(self):
        p = self._report_period
        if p == "Personalizado":
            return f"Del {self._report_start_date} al {self._report_end_date}"
        return p"""

new_handlers = """    def _get_report_date_bounds(self):
        mode = getattr(self, '_report_granularity', 'Día')
        ref = getattr(self, '_report_ref_date', datetime.date.today())

        if mode == "Día":
            s = ref
            e = ref
        elif mode == "Semana":
            s = ref - datetime.timedelta(days=ref.weekday())
            e = s + datetime.timedelta(days=6)
        elif mode == "Mes":
            s = ref.replace(day=1)
            _, last_day = calendar.monthrange(ref.year, ref.month)
            e = ref.replace(day=last_day)
        elif mode == "Año":
            s = datetime.date(ref.year, 1, 1)
            e = datetime.date(ref.year, 12, 31)
        elif mode == "Personalizado":
            try:
                s = datetime.datetime.strptime(self._report_start_date, "%Y-%m-%d").date()
                e = datetime.datetime.strptime(self._report_end_date, "%Y-%m-%d").date()
            except Exception:
                s = datetime.date.today()
                e = datetime.date.today()
        else:
            s = ref
            e = ref

        return s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")

    def _on_report_granularity_changed(self, mode):
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
            self._render_report_content()

    def _nav_report_period(self, delta):
        mode = getattr(self, '_report_granularity', 'Día')
        ref = getattr(self, '_report_ref_date', datetime.date.today())

        if mode == "Día":
            ref = ref + datetime.timedelta(days=delta)
        elif mode == "Semana":
            ref = ref + datetime.timedelta(weeks=delta)
        elif mode == "Mes":
            m = ref.month + delta
            y = ref.year
            while m > 12: m -= 12; y += 1
            while m < 1: m += 12; y -= 1
            d = min(ref.day, calendar.monthrange(y, m)[1])
            ref = datetime.date(y, m, d)
        elif mode == "Año":
            y = ref.year + delta
            d = min(ref.day, calendar.monthrange(y, ref.month)[1])
            ref = datetime.date(y, ref.month, d)

        self._report_ref_date = ref
        self._update_report_date_dropdown_options()
        self._render_report_content()

    def _update_report_date_dropdown_options(self):
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
            self._lbl_report_period_range.configure(text=range_txt)

    def _on_report_date_combo_selected(self, val):
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
        self._render_report_content()

    def _apply_custom_date(self):
        self._report_start_date = self._ent_start.get().strip()
        self._report_end_date = self._ent_end.get().strip()
        self._render_report_content()

    def _select_report_type(self, val):
        self._report_type = val
        self._render_report_content()

    def _get_period_label(self):
        s_str, e_str = self._get_report_date_bounds()
        if s_str == e_str:
            return s_str
        return f"Del {s_str} al {e_str}" """

if old_handlers in content:
    content = content.replace(old_handlers, new_handlers)
    print("Handlers replaced.")
else:
    print("WARNING: old_handlers not found!")

# Update ReportModel.get_date_range_bounds call in _render_report_content
old_bounds_call = """        start_dt, end_dt = ReportModel.get_date_range_bounds(
            self._report_period,
            self._report_start_date,
            self._report_end_date
        )"""

new_bounds_call = """        s_str, e_str = self._get_report_date_bounds()
        start_dt = f"{s_str} 00:00:00"
        end_dt = f"{e_str} 23:59:59" """

if old_bounds_call in content:
    content = content.replace(old_bounds_call, new_bounds_call)
    print("Bounds call replaced.")

# Also trigger initial _update_report_date_dropdown_options in _build_reports_tab_ui
old_build_end = """        self._render_report_content()"""
new_build_end = """        self._update_report_date_dropdown_options()
        self._render_report_content()"""

if "self._update_report_date_dropdown_options()" not in content and old_build_end in content:
    content = content.replace(old_build_end, new_build_end, 1)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("apply_report_period_bar complete.")
