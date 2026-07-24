with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_calendar_class = """class CTkCalendarPopup(ctk.CTkFrame):
    \"\"\"Modern Dark-Themed In-App Floating Calendar Picker Component (Opens Straight Up & Perfectly Aligned)\"\"\"
    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
        root_win = parent.winfo_toplevel()
        width, height = 310, 330
        super().__init__(root_win, width=width, height=height, fg_color="#0F172A", border_width=1, border_color="#334155", corner_radius=8)
        
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.selected_date = initial_date or datetime.date.today()
        self.curr_year = self.selected_date.year
        self.curr_month = self.selected_date.month
        self.showing_month_selector = False

        # Calculate exact position right below the target input field or button
        rw = max(root_win.winfo_width(), 800)
        rh = max(root_win.winfo_height(), 600)

        if btn_widget and btn_widget.winfo_exists():
            btn_x = btn_widget.winfo_rootx() - root_win.winfo_rootx()
            btn_w = btn_widget.winfo_width()
            btn_y = btn_widget.winfo_rooty() - root_win.winfo_rooty() + btn_widget.winfo_height() + 2
            
            # Align under target widget. If near right window edge (e.g. 'Hasta'), align right edges
            if btn_x + width > rw - 15:
                bx = (btn_x + btn_w) - width
            else:
                bx = btn_x
            by = btn_y
        else:
            bx = (rw - width) // 2
            by = (rh - height) // 2

        # Clamp relative coordinates so popup stays 100% inside app window
        final_x = max(10, min(bx, rw - width - 15))
        final_y = max(10, min(by, rh - height - 15))

        # Direct, immediate placement - straight up, zero animation delay
        self.place(x=final_x, y=final_y)
        self.lift()

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=6)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self._build_header()
        self._build_weekdays()
        self._build_grid()

        self._btn_widget_str = str(btn_widget) if btn_widget and btn_widget.winfo_exists() else ""
        self._click_listener_active = False
        self.after(150, self._setup_click_listener)

    def _setup_click_listener(self):
        try:
            if self.winfo_exists():
                self._click_listener_active = True
                root_win = self.parent.winfo_toplevel()
                self._click_bind_id = root_win.bind_all("<ButtonPress-1>", self._on_global_click, add="+")
        except Exception:
            pass

    def destroy(self):
        try:
            if hasattr(self, '_click_bind_id'):
                self.parent.winfo_toplevel().unbind_all("<ButtonPress-1>")
        except Exception:
            pass
        super().destroy()

    def _on_global_click(self, event):
        if not getattr(self, '_click_listener_active', False):
            return
        try:
            if not self.winfo_exists():
                return
            widget_str = str(event.widget)
            if widget_str.startswith(str(self)):
                return
            if self._btn_widget_str and (widget_str == self._btn_widget_str or widget_str.startswith(self._btn_widget_str)):
                return
            self.destroy()
        except Exception:
            pass"""

new_calendar_class = """class CTkCalendarPopup(ctk.CTkFrame):
    \"\"\"Modern Dark-Themed Dropdown Calendar Picker Component (100% Native Dropdown Below Target Field)\"\"\"
    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
        root_win = parent.winfo_toplevel()
        width, height = 310, 330
        super().__init__(root_win, width=width, height=height, fg_color="#0F172A", border_width=1, border_color="#334155", corner_radius=8)
        
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.selected_date = initial_date or datetime.date.today()
        self.curr_year = self.selected_date.year
        self.curr_month = self.selected_date.month
        self.showing_month_selector = False

        if btn_widget and btn_widget.winfo_exists():
            root_win.update_idletasks()
            rw = root_win.winfo_width()
            bx = btn_widget.winfo_rootx() - root_win.winfo_rootx()
            
            # If target field is near right edge (e.g. 'Hasta'), align right edges so it stays inside window
            if bx + width > rw - 20:
                self.place(in_=btn_widget, relx=1.0, rely=1.0, x=-width, y=2)
            else:
                self.place(in_=btn_widget, relx=0.0, rely=1.0, x=0, y=2)
        else:
            self.place(relx=0.5, rely=0.5, anchor="center")

        self.lift()

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=6)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self._build_header()
        self._build_weekdays()
        self._build_grid()

        self._btn_widget_str = str(btn_widget) if btn_widget and btn_widget.winfo_exists() else ""
        self._click_listener_active = False
        self.after(100, self._setup_click_listener)

    def _setup_click_listener(self):
        try:
            if self.winfo_exists():
                self._click_listener_active = True
                root_win = self.parent.winfo_toplevel()
                self._click_bind_id = root_win.bind_all("<ButtonPress-1>", self._on_global_click, add="+")
        except Exception:
            pass

    def destroy(self):
        try:
            if hasattr(self, '_click_bind_id'):
                self.parent.winfo_toplevel().unbind_all("<ButtonPress-1>")
        except Exception:
            pass
        super().destroy()

    def _on_global_click(self, event):
        if not getattr(self, '_click_listener_active', False):
            return
        try:
            if not self.winfo_exists():
                return
            widget_str = str(event.widget)
            if widget_str.startswith(str(self)):
                return
            if self._btn_widget_str and (widget_str == self._btn_widget_str or widget_str.startswith(self._btn_widget_str)):
                return
            self.destroy()
        except Exception:
            pass"""

if old_calendar_class in content:
    content = content.replace(old_calendar_class, new_calendar_class)
    print("CTkCalendarPopup updated to native dropdown with place(in_=btn_widget)!")
else:
    print("WARNING: old_calendar_class not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
