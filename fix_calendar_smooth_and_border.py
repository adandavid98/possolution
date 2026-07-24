with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_cal_init = """    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
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
        self.lift()

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=4, pady=4)"""

new_cal_init = """    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
        root_win = parent.winfo_toplevel()
        width, height = 320, 340
        super().__init__(root_win, width=width, height=height, fg_color="#0F172A", border_width=1, border_color="#334155", corner_radius=10)
        
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.selected_date = initial_date or datetime.date.today()
        self.curr_year = self.selected_date.year
        self.curr_month = self.selected_date.month
        self.showing_month_selector = False

        # Calculate smooth position constrained strictly INSIDE the application window
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
        self.lift()

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=8)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)"""

if old_cal_init in content:
    content = content.replace(old_cal_init, new_cal_init)
    print("Calendar border restored to original dark #334155 and smooth placement applied!")
else:
    print("WARNING: old_cal_init not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
