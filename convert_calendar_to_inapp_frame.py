with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_calendar_class = """class CTkCalendarPopup(ctk.CTkToplevel):
    \"\"\"Modern Dark-Themed Floating Calendar Picker Component\"\"\"
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
            pass"""

new_calendar_class = """class CTkCalendarPopup(ctk.CTkFrame):
    \"\"\"Modern Dark-Themed In-App Floating Calendar Picker Component (100% inside system window)\"\"\"
    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
        root_win = parent.winfo_toplevel()
        super().__init__(root_win, fg_color="#0F172A", border_width=2, border_color="#38BDF8", corner_radius=12)
        
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.selected_date = initial_date or datetime.date.today()
        self.curr_year = self.selected_date.year
        self.curr_month = self.selected_date.month
        self.showing_month_selector = False

        # Calculate position constrained strictly INSIDE the application window
        width, height = 320, 350
        root_win.update_idletasks()
        rw = max(root_win.winfo_width(), 800)
        rh = max(root_win.winfo_height(), 600)

        if btn_widget and btn_widget.winfo_exists():
            bx = btn_widget.winfo_rootx() - root_win.winfo_rootx()
            by = btn_widget.winfo_rooty() - root_win.winfo_rooty() + btn_widget.winfo_height() + 4
        else:
            bx = (rw - width) // 2
            by = (rh - height) // 2

        # Clamp relative coordinates so popover NEVER leaves app window boundaries
        final_x = max(10, min(bx, rw - width - 15))
        final_y = max(10, min(by, rh - height - 15))

        self.place(x=final_x, y=final_y, width=width, height=height)
        self.lift()

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self._build_header()
        self._build_weekdays()
        self._build_grid()

        # Outside click listener to dismiss calendar cleanly
        self._click_bind_id = root_win.bind_all("<ButtonPress-1>", self._on_global_click, add="+")

    def destroy(self):
        try:
            if hasattr(self, '_click_bind_id'):
                self.parent.winfo_toplevel().unbind_all("<ButtonPress-1>")
        except Exception:
            pass
        super().destroy()

    def _on_global_click(self, event):
        try:
            widget_str = str(event.widget)
            if not widget_str.startswith(str(self)):
                self.after(10, self.destroy)
        except Exception:
            pass"""

if old_calendar_class in content:
    content = content.replace(old_calendar_class, new_calendar_class)
    print("CTkCalendarPopup converted to CTkFrame in-app overlay successfully!")
else:
    print("WARNING: old_calendar_class not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
