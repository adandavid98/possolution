"""Patch app_gui.py to add debouncing and smooth layout pass optimization on window resize/maximize/restore."""
import re

print("=== APPLYING WINDOW RESIZE & REDRAW OPTIMIZATION ===")

with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add _is_minimized flag and window map/unmap handlers in POSApp.__init__
old_init_shortcut = """        # Global Function Key Shortcuts [F1-F12]
        self.bind_all("<F1>", lambda e: self.focus_pos_search())"""

new_init_shortcut = """        # Window State & Resize Throttling
        self._is_minimized = False
        self.bind("<Unmap>", lambda e: setattr(self, '_is_minimized', True) if e.widget == self else None)
        self.bind("<Map>", lambda e: setattr(self, '_is_minimized', False) if e.widget == self else None)

        # Global Function Key Shortcuts [F1-F12]
        self.bind_all("<F1>", lambda e: self.focus_pos_search())"""

if "_is_minimized" not in code:
    code = code.replace(old_init_shortcut, new_init_shortcut)

# 2. Debounce canvas and wrapper resize handlers in _build_welcome_tab_ui
old_canvas_binds = """        def _on_canvas_resize(event):
            canvas.itemconfig(wrapper_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_resize)

        def _on_wrapper_resize(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        wrapper.bind("<Configure>", _on_wrapper_resize)"""

new_canvas_binds = """        _canvas_resize_job = None
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
        wrapper.bind("<Configure>", _on_wrapper_resize)"""

code = code.replace(old_canvas_binds, new_canvas_binds)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py successfully patched with debounced resize handlers and window state tracking!")
