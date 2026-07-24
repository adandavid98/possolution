with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_btn = """        # Big Touch Checkout Button
        btn_touch_pay = ctk.CTkButton(
            self.right_side, text="💳 COBRAR Y FACTURAR  [F10]", 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=54, corner_radius=10,
            command=self.open_touch_payment_modal
        )
        btn_touch_pay.pack(fill="x", padx=12, pady=(8, 14))"""

new_btn = """        # Big Touch Checkout Button (Amplio y Destacado)
        btn_touch_pay = ctk.CTkButton(
            self.right_side, text="💳 COBRAR Y FACTURAR  (F10)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=62, corner_radius=12,
            command=self.open_touch_payment_modal
        )
        btn_touch_pay.pack(fill="x", padx=8, pady=(8, 16))"""

if old_btn in content:
    content = content.replace(old_btn, new_btn)
    print("btn_touch_pay updated to height=62, size=14, clear text (F10)!")
else:
    print("WARNING: old_btn not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
