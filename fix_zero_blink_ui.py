"""Patch app_gui.py to use native CTkScrollableFrame in Welcome Tab and remove all Python resize delay loops for ZERO blink UI."""

with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_welcome_canvas_code = """    def _build_welcome_tab_ui(self, parent):

        import tkinter as tk

        container = ctk.CTkFrame(parent, fg_color="#0F172A")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#0F172A", highlightthickness=0, bd=0)
        scrollbar = ctk.CTkScrollbar(container, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        wrapper = ctk.CTkFrame(canvas, fg_color="#0F172A")
        wrapper_id = canvas.create_window((0, 0), window=wrapper, anchor="nw")

        _canvas_resize_job = None
        def _on_canvas_resize(event):
            nonlocal _canvas_resize_job
            if getattr(self, '_is_minimized', False):
                return
            if _canvas_resize_job is not None:
                try:
                    canvas.after_cancel(_canvas_resize_job)
                except Exception:
                    pass
            w = event.width
            def _apply():
                if canvas.winfo_exists():
                    canvas.itemconfig(wrapper_id, width=w)
            _canvas_resize_job = canvas.after(15, _apply)
        canvas.bind("<Configure>", _on_canvas_resize)

        _wrapper_resize_job = None
        def _on_wrapper_resize(event):
            nonlocal _wrapper_resize_job
            if getattr(self, '_is_minimized', False):
                return
            if _wrapper_resize_job is not None:
                try:
                    canvas.after_cancel(_wrapper_resize_job)
                except Exception:
                    pass
            def _apply():
                if canvas.winfo_exists():
                    canvas.configure(scrollregion=canvas.bbox("all"))
            _wrapper_resize_job = canvas.after(15, _apply)
        wrapper.bind("<Configure>", _on_wrapper_resize)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        inner = ctk.CTkFrame(wrapper, fg_color="transparent")"""

new_welcome_scroll_code = """    def _build_welcome_tab_ui(self, parent):

        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="#0F172A", corner_radius=0)
        scroll_frame.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll_frame, fg_color="transparent")"""

code = code.replace(old_welcome_canvas_code, new_welcome_scroll_code)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py successfully updated to native CTkScrollableFrame for Zero-Blink UI!")
