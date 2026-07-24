with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CTkCalendarPopup positioning logic
old_popup_init = """        # Calculate smooth position constrained strictly INSIDE the application window
        rw = max(root_win.winfo_width(), 800)
        rh = max(root_win.winfo_height(), 600)

        if btn_widget and btn_widget.winfo_exists():
            bx = btn_widget.winfo_rootx() - root_win.winfo_rootx()
            by = btn_widget.winfo_rooty() - root_win.winfo_rooty() + btn_widget.winfo_height() + 2
        else:
            bx = (rw - width) // 2
            by = (rh - height) // 2

        # Clamp relative coordinates so popover NEVER leaves app window boundaries
        final_x = max(10, min(bx, rw - width - 12))
        final_y = max(10, min(by, rh - height - 12))

        self.place(x=final_x, y=final_y)
        self.lift()"""

new_popup_init = """        # Calculate smooth position constrained strictly INSIDE the application window
        root_win.update_idletasks()
        rw = max(root_win.winfo_width(), 800)
        rh = max(root_win.winfo_height(), 600)

        if btn_widget and btn_widget.winfo_exists():
            btn_x_rel = btn_widget.winfo_rootx() - root_win.winfo_rootx()
            btn_w = btn_widget.winfo_width()
            
            # If trigger widget is near the right edge (like 'Hasta' field), align right edges
            if btn_x_rel + width > rw - 40:
                bx = (btn_x_rel + btn_w) - width
            else:
                bx = btn_x_rel

            by = btn_widget.winfo_rooty() - root_win.winfo_rooty() + btn_widget.winfo_height() + 4
        else:
            bx = (rw - width) // 2
            by = (rh - height) // 2

        # Strict clamping so popover NEVER leaves app window boundaries
        final_x = max(15, min(bx, rw - width - 25))
        final_y = max(15, min(by, rh - height - 25))

        self.place(x=final_x, y=final_y)
        self.lift()"""

if old_popup_init in content:
    content = content.replace(old_popup_init, new_popup_init)
    print("CTkCalendarPopup positioning and right-alignment clamping updated!")

# 2. Add singleton destruction in _open_calendar_for_entry and _open_report_calendar_popup
old_open_entry = """    def _open_calendar_for_entry(self, entry_widget):
        def _on_date_picked(picked_date):
            d_str = picked_date.strftime("%d-%m-%Y")
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d_str)
            self._apply_custom_date()

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
        )"""

new_open_entry = """    def _open_calendar_for_entry(self, entry_widget):
        if hasattr(self, '_active_calendar_popup') and self._active_calendar_popup:
            try:
                if self._active_calendar_popup.winfo_exists():
                    self._active_calendar_popup.destroy()
            except Exception:
                pass
            self._active_calendar_popup = None

        def _on_date_picked(picked_date):
            d_str = picked_date.strftime("%d-%m-%Y")
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d_str)
            self._apply_custom_date()

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

        self._active_calendar_popup = CTkCalendarPopup(
            self,
            initial_date=init_d,
            on_select_callback=_on_date_picked,
            btn_widget=entry_widget
        )"""

if old_open_entry in content:
    content = content.replace(old_open_entry, new_open_entry)
    print("_open_calendar_for_entry updated with singleton popup protection!")

old_open_report_cal = """        popup = CTkCalendarPopup(
            self,
            initial_date=initial_d,
            on_select_callback=_on_date_picked,
            btn_widget=target_w
        )"""

new_open_report_cal = """        if hasattr(self, '_active_calendar_popup') and self._active_calendar_popup:
            try:
                if self._active_calendar_popup.winfo_exists():
                    self._active_calendar_popup.destroy()
            except Exception:
                pass
            self._active_calendar_popup = None

        self._active_calendar_popup = CTkCalendarPopup(
            self,
            initial_date=initial_d,
            on_select_callback=_on_date_picked,
            btn_widget=target_w
        )"""

if old_open_report_cal in content:
    content = content.replace(old_open_report_cal, new_open_report_cal)
    print("_open_report_calendar_popup updated with singleton popup protection!")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
