with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_cal_code = """        # Outside click listener to dismiss calendar cleanly
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

new_cal_code = """        self._btn_widget_str = str(btn_widget) if btn_widget and btn_widget.winfo_exists() else ""
        self._click_listener_active = False
        self.after(250, self._setup_click_listener)

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
            self.after(10, self.destroy)
        except Exception:
            pass"""

if old_cal_code in content:
    content = content.replace(old_cal_code, new_cal_code)
    print("Calendar instant destroy bug fixed successfully!")
else:
    print("WARNING: old_cal_code not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
