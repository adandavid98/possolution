with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_init = """    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
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
        self.lift()"""

new_init = """    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
        root_win = parent.winfo_toplevel()
        width, height = 320, 350
        super().__init__(root_win, width=width, height=height, fg_color="#0F172A", border_width=2, border_color="#38BDF8", corner_radius=12)
        
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.selected_date = initial_date or datetime.date.today()
        self.curr_year = self.selected_date.year
        self.curr_month = self.selected_date.month
        self.showing_month_selector = False

        # Calculate position constrained strictly INSIDE the application window
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

        self.place(x=final_x, y=final_y)
        self.lift()"""

if old_init in content:
    content = content.replace(old_init, new_init)
    print("CTkCalendarPopup place width/height ValueError bug fixed!")
else:
    print("WARNING: old_init not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
