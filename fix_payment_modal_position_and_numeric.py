with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update btn_touch_pay in self.right_side
old_btn_touch = """        # Big Touch Checkout Button
        btn_touch_pay = ctk.CTkButton(
            self.right_side, text="💳 COBRAR Y FACTURAR  [F10]", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=50, corner_radius=8,
            command=self.open_touch_payment_modal
        )
        btn_touch_pay.pack(fill="x", padx=12, pady=(6, 12))"""

new_btn_touch = """        # Big Touch Checkout Button
        btn_touch_pay = ctk.CTkButton(
            self.right_side, text="💳 COBRAR Y FACTURAR  [F10]", 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=54, corner_radius=10,
            command=self.open_touch_payment_modal
        )
        btn_touch_pay.pack(fill="x", padx=12, pady=(8, 14))"""

if old_btn_touch in content:
    content = content.replace(old_btn_touch, new_btn_touch)
    print("btn_touch_pay updated!")

# 2. Update open_touch_payment_modal position and layout
old_modal_start = """        pay_win = ctk.CTkToplevel(self)
        pay_win.title("💳 COBRO TÁCTIL E IMPRESIÓN DE FACTURA [F10]")
        pay_win.geometry("640x620")
        pay_win.configure(fg_color="#0F172A")
        
        # Make modal overlay anchored directly on main window
        pay_win.transient(self)
        pay_win.grab_set()

        # Title & Total Display
        top_header = ctk.CTkFrame(pay_win, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        top_header.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(top_header, text="TOTAL A COBRAR (CON ITBIS 18%)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").pack(pady=(10, 2))
        lbl_monto_total = ctk.CTkLabel(top_header, text=f"RD$ {total_pagar:,.2f}", font=ctk.CTkFont(family="Poppins", size=32, weight="bold"), text_color="#10B981")
        lbl_monto_total.pack(pady=(0, 10))"""

new_modal_start = """        pay_win = ctk.CTkToplevel(self)
        pay_win.title("💳 COBRO TÁCTIL E IMPRESIÓN DE FACTURA [F10]")
        
        # Position higher up so confirm button is 100% visible on all screens
        self.update_idletasks()
        root_w = max(self.winfo_width(), 1024)
        root_h = max(self.winfo_height(), 700)
        root_x = self.winfo_rootx()
        root_y = self.winfo_rooty()
        win_w, win_h = 650, 600
        pos_x = max(10, root_x + (root_w - win_w) // 2)
        pos_y = max(10, root_y + (root_h - win_h) // 2 - 50)
        pay_win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        pay_win.configure(fg_color="#0F172A")
        
        pay_win.transient(self)
        pay_win.grab_set()

        # Title & Total Display
        top_header = ctk.CTkFrame(pay_win, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        top_header.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(top_header, text="TOTAL A COBRAR (CON ITBIS 18%)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(pady=(6, 1))
        lbl_monto_total = ctk.CTkLabel(top_header, text=f"RD$ {total_pagar:,.2f}", font=ctk.CTkFont(family="Poppins", size=28, weight="bold"), text_color="#10B981")
        lbl_monto_total.pack(pady=(0, 6))"""

if old_modal_start in content:
    content = content.replace(old_modal_start, new_modal_start)
    print("open_touch_payment_modal positioning updated!")

# 3. Add numeric decimal validation for ent_recibido_modal
old_entry_setup = """        ent_recibido_modal = ctk.CTkEntry(cash_right, width=240, height=42, font=ctk.CTkFont(size=20, weight="bold"), justify="center", fg_color="#0F172A", border_color="#475569")
        ent_recibido_modal.pack(pady=(0, 6))
        ent_recibido_modal.insert(0, f"{total_pagar:.2f}")"""

new_entry_setup = """        def _validate_decimal_input(P):
            if P == "" or P == ".":
                return True
            try:
                val = float(P)
                return val >= 0
            except ValueError:
                return False

        vcmd_num = (pay_win.register(_validate_decimal_input), '%P')

        ent_recibido_modal = ctk.CTkEntry(
            cash_right, width=240, height=42, font=ctk.CTkFont(size=20, weight="bold"),
            justify="center", fg_color="#0F172A", border_color="#475569",
            validate="key", validatecommand=vcmd_num
        )
        ent_recibido_modal.pack(pady=(0, 6))
        ent_recibido_modal.insert(0, f"{total_pagar:.2f}")"""

if old_entry_setup in content:
    content = content.replace(old_entry_setup, new_entry_setup)
    print("ent_recibido_modal numeric validation added!")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
