with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace period_bar layout in _build_reports_tab_ui
old_period_bar = """        # Date Filter Dropdown
        ctk.CTkLabel(period_bar, text="Fecha:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(6, 2))
        self._cmb_report_date_list = ctk.CTkComboBox(
            period_bar, values=["Seleccionar..."], width=170, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_date_combo_selected
        )
        self._cmb_report_date_list.pack(side="left", padx=2)

        # Calendar Popup Trigger Button (BLUE)
        self._btn_report_calendar = ctk.CTkButton(
            period_bar, text="📅 Calendario", width=110, height=32,
            fg_color="#2563EB", hover_color="#1D4ED8", text_color="#F8FAFC",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._open_report_calendar_popup
        )
        self._btn_report_calendar.pack(side="left", padx=(2, 4))

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

new_period_bar = """        # Date Filter Dropdown with Integrated Calendar Button
        ctk.CTkLabel(period_bar, text="Fecha:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(6, 2))

        date_box_frame = ctk.CTkFrame(period_bar, fg_color="transparent")
        date_box_frame.pack(side="left", padx=2)

        self._cmb_report_date_list = ctk.CTkComboBox(
            date_box_frame, values=["Seleccionar..."], width=175, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_date_combo_selected
        )
        self._cmb_report_date_list.pack(side="left")
        self._cmb_report_date_list.bind("<Double-Button-1>", lambda e: self._open_report_calendar_popup(btn_widget=self._cmb_report_date_list))

        # Integrated Calendar Icon Button
        self._btn_report_calendar = ctk.CTkButton(
            date_box_frame, text="📅", width=34, height=32,
            fg_color="#2563EB", hover_color="#1D4ED8", text_color="#F8FAFC",
            font=ctk.CTkFont(size=13),
            command=lambda: self._open_report_calendar_popup(btn_widget=self._cmb_report_date_list)
        )
        self._btn_report_calendar.pack(side="left", padx=(2, 0))

        # Next Button
        self._btn_report_next = ctk.CTkButton(
            period_bar, text="Siguiente ▶", width=85, height=32,
            fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._nav_report_period(1)
        )
        self._btn_report_next.pack(side="left", padx=(4, 6))

        # Live Range Indicator Label
        self._lbl_report_period_range = ctk.CTkLabel(
            period_bar, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8"
        )
        self._lbl_report_period_range.pack(side="left", padx=6)

        # Custom date range (hidden by default)
        self._custom_date_frame = ctk.CTkFrame(period_bar, fg_color="transparent")
        
        lbl_s = ctk.CTkLabel(self._custom_date_frame, text="Desde 📅:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8")
        lbl_s.pack(side="left", padx=(6, 2))
        self._ent_start = ctk.CTkEntry(self._custom_date_frame, placeholder_text="DD-MM-YYYY (2 clics 📅)", width=130, height=32)
        self._ent_start.pack(side="left", padx=2)
        self._ent_start.bind("<Double-Button-1>", lambda e: self._open_calendar_for_entry(self._ent_start))

        lbl_e = ctk.CTkLabel(self._custom_date_frame, text="Hasta 📅:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8")
        lbl_e.pack(side="left", padx=(6, 2))
        self._ent_end = ctk.CTkEntry(self._custom_date_frame, placeholder_text="DD-MM-YYYY (2 clics 📅)", width=130, height=32)
        self._ent_end.pack(side="left", padx=2)
        self._ent_end.bind("<Double-Button-1>", lambda e: self._open_calendar_for_entry(self._ent_end))

        btn_apply = ctk.CTkButton(
            self._custom_date_frame, text="Aplicar", width=65, height=32,
            fg_color="#10B981", hover_color="#059669",
            command=self._apply_custom_date
        )
        btn_apply.pack(side="left", padx=4)"""

if old_period_bar in content:
    content = content.replace(old_period_bar, new_period_bar)
    print("Period bar layout updated with integrated calendar icon and double-click entries.")

# Update _open_calendar_for_entry & _get_report_date_bounds in app_gui.py
old_popup_methods = """    def _open_report_calendar_popup(self):
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

new_popup_methods = """    def _open_calendar_for_entry(self, entry_widget):
        def _on_date_picked(picked_date):
            d_str = picked_date.strftime("%d-%m-%Y")
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d_str)

        try:
            curr_val = entry_widget.get().strip()
            init_d = None
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    init_d = datetime.datetime.strptime(curr_val, fmt).date()
                    break
                except ValueError:
                    pass
            if not init_d:
                init_d = datetime.date.today()
        except Exception:
            init_d = datetime.date.today()

        CTkCalendarPopup(
            self,
            initial_date=init_d,
            on_select_callback=_on_date_picked,
            btn_widget=entry_widget
        )

    def _open_report_calendar_popup(self, btn_widget=None):
        def _on_date_picked(picked_date):
            self._report_ref_date = picked_date
            self._update_report_date_dropdown_options()
            self._render_report_content()

        target_w = btn_widget or getattr(self, '_btn_report_calendar', None) or getattr(self, '_cmb_report_date_list', None)
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
            btn_widget=target_w
        )"""

if old_popup_methods in content:
    content = content.replace(old_popup_methods, new_popup_methods)
    print("Popup methods updated with _open_calendar_for_entry.")

# Update _get_report_date_bounds to handle DD-MM-YYYY input strings in Personalizado
old_bounds = """        elif mode == "Personalizado":
            try:
                s = datetime.datetime.strptime(self._report_start_date, "%Y-%m-%d").date()
                e = datetime.datetime.strptime(self._report_end_date, "%Y-%m-%d").date()
            except Exception:
                s = datetime.date.today()
                e = datetime.date.today()"""

new_bounds = """        elif mode == "Personalizado":
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

if old_bounds in content:
    content = content.replace(old_bounds, new_bounds)
    print("_get_report_date_bounds updated with flexible date parsing.")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("integrate_calendar_in_date_fields complete.")
