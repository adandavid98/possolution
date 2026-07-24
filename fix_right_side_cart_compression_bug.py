with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_cart_view = """        # Cart Table Scroll
        self.cart_scroll = ctk.CTkScrollableFrame(self.right_side, height=280, fg_color="#0F172A")
        self.cart_scroll.pack(fill="x", padx=12, pady=5)

        # Cart Action Quick Buttons Row
        cart_actions = ctk.CTkFrame(self.right_side, fg_color="transparent")
        cart_actions.pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(
            cart_actions, text="🔢 Cantidad [F2]", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#334155", hover_color="#475569", height=32, corner_radius=6,
            command=self.open_qty_keypad
        ).pack(side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(
            cart_actions, text="🏷️ Descuento [F8]", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED", height=32, corner_radius=6,
            command=self.open_discount_keypad
        ).pack(side="left", padx=2, expand=True, fill="x")

        # Totals Panel
        totals_panel = ctk.CTkFrame(self.right_side, fg_color="#0F172A", corner_radius=8, border_width=1, border_color="#334155")
        totals_panel.pack(fill="x", padx=12, pady=8)

        self.lbl_subtotal = ctk.CTkLabel(totals_panel, text="Subtotal: RD$ 0.00", font=ctk.CTkFont(size=12), text_color="#94A3B8")
        self.lbl_subtotal.pack(anchor="w", padx=12, pady=(6, 1))

        self.lbl_itbis = ctk.CTkLabel(totals_panel, text="ITBIS (18%): RD$ 0.00", font=ctk.CTkFont(size=12), text_color="#94A3B8")
        self.lbl_itbis.pack(anchor="w", padx=12, pady=1)

        self.lbl_total = ctk.CTkLabel(
            totals_panel, text="TOTAL: RD$ 0.00", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#10B981"
        )
        self.lbl_total.pack(anchor="w", padx=12, pady=(1, 6))

        # Big Touch Checkout Button (Amplio y Destacado)
        btn_touch_pay = ctk.CTkButton(
            self.right_side, text="💳 COBRAR Y FACTURAR  (F10)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=62, corner_radius=12,
            command=self.open_touch_payment_modal
        )
        btn_touch_pay.pack(fill="x", padx=8, pady=(8, 16))"""

new_cart_view = """        # Cart Table Scroll (flexible expand=True so bottom buttons are NEVER compressed)
        self.cart_scroll = ctk.CTkScrollableFrame(self.right_side, fg_color="#0F172A")
        self.cart_scroll.pack(fill="both", expand=True, padx=12, pady=(4, 2))

        # Cart Action Quick Buttons Row
        cart_actions = ctk.CTkFrame(self.right_side, fg_color="transparent")
        cart_actions.pack(fill="x", padx=12, pady=2)

        ctk.CTkButton(
            cart_actions, text="🔢 Cantidad [F2]", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#334155", hover_color="#475569", height=32, corner_radius=6,
            command=self.open_qty_keypad
        ).pack(side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(
            cart_actions, text="🏷️ Descuento [F8]", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED", height=32, corner_radius=6,
            command=self.open_discount_keypad
        ).pack(side="left", padx=2, expand=True, fill="x")

        # Totals Panel
        totals_panel = ctk.CTkFrame(self.right_side, fg_color="#0F172A", corner_radius=8, border_width=1, border_color="#334155")
        totals_panel.pack(fill="x", padx=12, pady=4)

        self.lbl_subtotal = ctk.CTkLabel(totals_panel, text="Subtotal: RD$ 0.00", font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.lbl_subtotal.pack(anchor="w", padx=12, pady=(4, 1))

        self.lbl_itbis = ctk.CTkLabel(totals_panel, text="ITBIS (18%): RD$ 0.00", font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.lbl_itbis.pack(anchor="w", padx=12, pady=1)

        self.lbl_total = ctk.CTkLabel(
            totals_panel, text="TOTAL: RD$ 0.00", 
            font=ctk.CTkFont(size=17, weight="bold"), text_color="#10B981"
        )
        self.lbl_total.pack(anchor="w", padx=12, pady=(1, 4))

        # Big Touch Checkout Button (Protegido contra compresión)
        btn_touch_pay = ctk.CTkButton(
            self.right_side, text="💳 COBRAR Y FACTURAR [F10]", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=46, corner_radius=8,
            command=self.open_touch_payment_modal
        )
        btn_touch_pay.pack(fill="x", padx=12, pady=(4, 10))"""

if old_cart_view in content:
    content = content.replace(old_cart_view, new_cart_view)
    print("right_side layout updated with cart_scroll expand=True to prevent button compression!")
else:
    print("WARNING: old_cart_view not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
