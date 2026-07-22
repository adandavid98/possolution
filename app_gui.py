import os
import sys
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk

from PIL import Image, ImageTk
from models import UserModel, ProductModel, CajaModel, VentaModel, InventoryMovementModel, ReportModel
from utils.pdf_generator import generate_ticket_pdf, generate_inventory_report_pdf
from utils.excel_exporter import export_inventory_to_excel, export_sales_to_excel

def get_asset_path(relative_path):
    """Gets absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# CustomTkinter Theme Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class POSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Minimarket La Ruta del Este - POS & Inventarios (SQL Server)")
        self.geometry("1280x768")
        self.minsize(1024, 700)
        
        self.current_user = None
        self.active_caja = None
        self.cart = [] # List of dicts for POS cart
        self.logo_ctk = None # Retain image reference
        
        # Container frame
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Global Function Key Shortcuts [F1-F12]
        self.bind_all("<F1>", lambda e: self.focus_pos_search())
        self.bind_all("<F2>", lambda e: self.open_qty_keypad())
        self.bind_all("<F3>", lambda e: self.remove_selected_cart_item())
        self.bind_all("<F4>", lambda e: self.clear_cart_confirm())
        self.bind_all("<F5>", lambda e: self.load_caja_tab())
        self.bind_all("<F6>", lambda e: self.open_quick_stock_lookup())
        self.bind_all("<F8>", lambda e: self.open_discount_keypad())
        self.bind_all("<F10>", lambda e: self.open_touch_payment_modal())
        self.bind_all("<F12>", lambda e: self.reprint_last_ticket())
        
        self.show_login()

    # ==========================================
    # LOGIN SCREEN (Clean Minimalist Corporate UI)
    # ==========================================
    def show_login(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        self.configure(fg_color="#0F172A")
        self.container.configure(fg_color="#0F172A")
            
        # Fullscreen main frame
        main_login_box = ctk.CTkFrame(self.container, fg_color="#0F172A", corner_radius=0)
        main_login_box.pack(fill="both", expand=True)

        # 1. Left Panel (Branding / Minimalist Hero - 50% Width)
        left_hero = ctk.CTkFrame(main_login_box, fg_color="#1E293B", corner_radius=0)
        left_hero.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)

        # Hero Content Container (Centered)
        hero_content = ctk.CTkFrame(left_hero, fg_color="transparent")
        hero_content.place(relx=0.5, rely=0.5, anchor="center")

        # Top Badge Label
        lbl_top_badge = ctk.CTkLabel(
            hero_content, 
            text="MINIMARKET LA RUTA DEL ESTE, S.R.L.", 
            font=ctk.CTkFont(family="Poppins", size=13, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_top_badge.pack(pady=(0, 20))

        # Minimalist Logo Emblem
        logo_path = get_asset_path(os.path.join("assets", "logo.jpg"))
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                self.logo_ctk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(200, 200))
                
                lbl_img = ctk.CTkLabel(hero_content, image=self.logo_ctk, text="")
                lbl_img.image = self.logo_ctk
                lbl_img.pack(pady=(0, 20))
            except Exception as e:
                print("Error loading logo image:", e)

        # Main Title & Subtitle
        lbl_main_title = ctk.CTkLabel(
            hero_content, 
            text="Minimarket La Ruta del Este", 
            font=ctk.CTkFont(family="Poppins", size=22, weight="bold"),
            text_color="#F8FAFC",
            justify="center"
        )
        lbl_main_title.pack(pady=(0, 6))

        lbl_sub_hero = ctk.CTkLabel(
            hero_content, 
            text="Sistema Integral de Punto de Venta & Control de Inventario", 
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#94A3B8",
            justify="center"
        )
        lbl_sub_hero.pack(pady=(0, 0))

        # 2. Vertical Separator
        divider = ctk.CTkFrame(main_login_box, fg_color="#334155", width=1, corner_radius=0)
        divider.place(relx=0.5, rely=0.0, relwidth=0.001, relheight=1.0)

        # 3. Right Panel (Minimalist Login Card - 50% Width)
        right_panel = ctk.CTkFrame(main_login_box, fg_color="#0F172A", corner_radius=0)
        right_panel.place(relx=0.501, rely=0.0, relwidth=0.499, relheight=1.0)

        card = ctk.CTkFrame(right_panel, corner_radius=12, fg_color="#1E293B", border_width=1, border_color="#334155", width=390)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Card Title
        lbl_card_title = ctk.CTkLabel(
            card, 
            text="Iniciar Sesión", 
            font=ctk.CTkFont(family="Poppins", size=20, weight="bold"),
            text_color="#F8FAFC"
        )
        lbl_card_title.pack(pady=(30, 4))

        lbl_card_desc = ctk.CTkLabel(
            card, 
            text="Ingrese sus credenciales para acceder al sistema", 
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8"
        )
        lbl_card_desc.pack(pady=(0, 20))

        # Username Input
        lbl_u = ctk.CTkLabel(card, text="Usuario", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1")
        lbl_u.pack(anchor="w", padx=35, pady=(5, 3))

        self.ent_username = ctk.CTkEntry(
            card, placeholder_text="Nombre de usuario", 
            width=320, height=42, fg_color="#0F172A", border_color="#475569", corner_radius=6
        )
        self.ent_username.pack(padx=35, pady=(0, 12))
        self.ent_username.insert(0, "cajero1")

        # Password Input
        lbl_p = ctk.CTkLabel(card, text="Contraseña", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1")
        lbl_p.pack(anchor="w", padx=35, pady=(5, 3))

        self.ent_password = ctk.CTkEntry(
            card, placeholder_text="Contraseña de acceso", show="*", 
            width=320, height=42, fg_color="#0F172A", border_color="#475569", corner_radius=6
        )
        self.ent_password.pack(padx=35, pady=(0, 20))
        self.ent_password.insert(0, "caja123")
        self.ent_password.bind("<Return>", lambda e: self.handle_login())

        # Login Button
        btn_login = ctk.CTkButton(
            card, 
            text="Entrar al Sistema", 
            font=ctk.CTkFont(family="Inter", weight="bold", size=13),
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            width=320, 
            height=44,
            corner_radius=6,
            command=self.handle_login
        )
        btn_login.pack(padx=35, pady=(5, 20))

        # Demo Users Quick Fill
        lbl_quick = ctk.CTkLabel(card, text="Acceso Rápido de Prueba", font=ctk.CTkFont(size=11), text_color="#64748B")
        lbl_quick.pack(pady=(5, 8))

        quick_box = ctk.CTkFrame(card, fg_color="transparent")
        quick_box.pack(pady=(0, 25))

        btn_q1 = ctk.CTkButton(
            quick_box, text="Cajero", width=98, height=30, 
            fg_color="#334155", hover_color="#475569", corner_radius=6,
            command=lambda: self.fill_login("cajero1", "caja123")
        )
        btn_q1.pack(side="left", padx=3)

        btn_q2 = ctk.CTkButton(
            quick_box, text="Admin", width=98, height=30, 
            fg_color="#334155", hover_color="#475569", corner_radius=6,
            command=lambda: self.fill_login("admin", "admin123")
        )
        btn_q2.pack(side="left", padx=3)

        btn_q3 = ctk.CTkButton(
            quick_box, text="Almacén", width=98, height=30, 
            fg_color="#334155", hover_color="#475569", corner_radius=6,
            command=lambda: self.fill_login("almacen1", "almacen123")
        )
        btn_q3.pack(side="left", padx=3)

    def fill_login(self, u, p):
        self.ent_username.delete(0, "end")
        self.ent_username.insert(0, u)
        self.ent_password.delete(0, "end")
        self.ent_password.insert(0, p)
        self.handle_login()

    def handle_login(self):
        u = self.ent_username.get().strip()
        p = self.ent_password.get().strip()
        
        user = UserModel.authenticate(u, p)
        if user:
            self.current_user = user
            self.active_caja = CajaModel.get_active_caja(user["id"])
            self.show_main_dashboard()
        else:
            messagebox.showerror("Error de Autenticación", "Usuario o contraseña incorrectos.")

    # ==========================================
    # MAIN DASHBOARD
    # ==========================================
    def show_main_dashboard(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        # Top Bar (Clean Minimalist Navy Slate)
        top_bar = ctk.CTkFrame(self.container, height=52, fg_color="#1E293B", corner_radius=0)
        top_bar.pack(side="top", fill="x")

        lbl_brand = ctk.CTkLabel(
            top_bar, 
            text="  LA RUTA DEL ESTE  |  PUNTO DE VENTA", 
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
            text_color="#F8FAFC"
        )
        lbl_brand.pack(side="left", padx=15)

        # Active Caja status badge
        caja_txt = "Caja: CERRADA"
        caja_bg = "#EF4444"
        if self.active_caja:
            caja_txt = f"Caja #{self.active_caja['id']} ABIERTA (Fondo: RD${float(self.active_caja['monto_inicial']):.2f})"
            caja_bg = "#10B981"

        self.lbl_caja_badge = ctk.CTkLabel(
            top_bar, text=f"  {caja_txt}  ", 
            font=ctk.CTkFont(size=11, weight="bold"), 
            fg_color=caja_bg, text_color="white", corner_radius=6
        )
        self.lbl_caja_badge.pack(side="left", padx=20)

        # User Info & Logout
        btn_logout = ctk.CTkButton(
            top_bar, text="Cerrar Sesión", width=110, height=32, 
            fg_color="#334155", hover_color="#475569", command=self.show_login
        )
        btn_logout.pack(side="right", padx=15)

        lbl_user = ctk.CTkLabel(
            top_bar, 
            text=f"Usuario: {self.current_user['nombre_completo']} ({self.current_user['rol']})", 
            font=ctk.CTkFont(size=12), text_color="#94A3B8"
        )
        lbl_user.pack(side="right", padx=10)

        # Main Body Frame (Sidebar + Content View)
        main_body = ctk.CTkFrame(self.container, fg_color="transparent")
        main_body.pack(side="bottom", fill="both", expand=True)

        # Sidebar Navigation
        sidebar = ctk.CTkFrame(main_body, width=200, fg_color="#0F172A", corner_radius=0)
        sidebar.pack(side="left", fill="y")

        self.content_area = ctk.CTkFrame(main_body, fg_color="#0F172A", corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Nav Buttons
        btn_pos = ctk.CTkButton(
            sidebar, text="  🛒 Caja / POS", font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=42, anchor="w", corner_radius=6,
            command=self.load_pos_tab
        )
        btn_pos.pack(fill="x", padx=10, pady=(20, 5))

        btn_inv = ctk.CTkButton(
            sidebar, text="  📦 Inventario & Alertas", font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
            command=self.load_inventory_tab
        )
        btn_inv.pack(fill="x", padx=10, pady=5)

        btn_caja = ctk.CTkButton(
            sidebar, text="  💵 Apertura/Cierre Caja", font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
            command=self.load_caja_tab
        )
        btn_caja.pack(fill="x", padx=10, pady=5)

        btn_rep = ctk.CTkButton(
            sidebar, text="  📊 Reportes & Ventas", font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
            command=self.load_reports_tab
        )
        btn_rep.pack(fill="x", padx=10, pady=5)

        # Default Tab
        self.load_pos_tab()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ==========================================
    # TAB 1: POS / CAJA
    # ==========================================
    def load_pos_tab(self):
        self.clear_content()

        # Main container for POS
        pos_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        pos_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # --- TOP TOUCH FUNCTION BAR [F1-F12] ---
        func_bar = ctk.CTkFrame(pos_frame, fg_color="#1E293B", corner_radius=8, border_width=1, border_color="#334155")
        func_bar.pack(fill="x", pady=(0, 10))

        funcs = [
            ("[F1] Buscar", "#2563EB", self.focus_pos_search),
            ("[F2] Cantidad", "#334155", self.open_qty_keypad),
            ("[F3] Eliminar", "#DC2626", self.remove_selected_cart_item),
            ("[F4] Cancelar", "#475569", self.clear_cart_confirm),
            ("[F5] Caja", "#D97706", self.load_caja_tab),
            ("[F6] Consulta", "#0284C7", self.open_quick_stock_lookup),
            ("[F8] Descuento", "#8B5CF6", self.open_discount_keypad),
            ("[F10] COBRAR ➔", "#10B981", self.open_touch_payment_modal),
            ("[F12] Ticket", "#475569", self.reprint_last_ticket),
        ]

        for text, col, cmd in funcs:
            btn = ctk.CTkButton(
                func_bar, text=text, font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=col, hover_color="#1E293B", height=38, corner_radius=6,
                command=cmd
            )
            btn.pack(side="left", padx=3, pady=5, expand=True, fill="x")

        # Split left (Catalog/Search) and right (Cart/Checkout)
        body_split = ctk.CTkFrame(pos_frame, fg_color="transparent")
        body_split.pack(fill="both", expand=True)

        left_side = ctk.CTkFrame(body_split, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right_side = ctk.CTkFrame(body_split, width=420, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        self.right_side.pack(side="right", fill="both", padx=(10, 0))

        # --- LEFT SIDE: Search & Product Selection ---
        search_box = ctk.CTkFrame(left_side, fg_color="transparent")
        search_box.pack(fill="x", padx=12, pady=12)

        self.ent_pos_search = ctk.CTkEntry(
            search_box, placeholder_text="🔍 Escanear Código de Barras o Buscar Producto [F1]...",
            height=44, font=ctk.CTkFont(size=13), fg_color="#0F172A", border_color="#475569", corner_radius=6
        )
        self.ent_pos_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ent_pos_search.bind("<KeyRelease>", lambda e: self.search_pos_products())
        self.ent_pos_search.bind("<Return>", lambda e: self.quick_add_pos_barcode())

        # Products Scrollable Grid/List
        self.products_scroll = ctk.CTkScrollableFrame(left_side, fg_color="transparent")
        self.products_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.search_pos_products()

        # --- RIGHT SIDE: Default Cart View ---
        self.show_pos_cart_view()

        self.render_cart()

    def search_pos_products(self):
        term = self.ent_pos_search.get().strip() if hasattr(self, 'ent_pos_search') else ""
        products = ProductModel.get_all(term)

        for w in self.products_scroll.winfo_children():
            w.destroy()

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll, text="No se encontraron productos.", text_color="#A0A0B0")
            lbl.pack(pady=20)
            return

        for p in products:
            card = ctk.CTkFrame(self.products_scroll, fg_color="#1F2937", height=50)
            card.pack(fill="x", pady=3)

            name_lbl = ctk.CTkLabel(card, text=f"{p['nombre']}\n[{p['codigo_barras']}]", anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
            name_lbl.pack(side="left", padx=10)

            stock_color = "#10B981" if p['stock_actual'] > p['stock_minimo'] else "#EF4444"
            stock_lbl = ctk.CTkLabel(card, text=f"Stock: {p['stock_actual']}", text_color=stock_color, font=ctk.CTkFont(size=11))
            stock_lbl.pack(side="left", padx=15)

            price_lbl = ctk.CTkLabel(card, text=f"RD${float(p['precio_venta']):.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#38BDF8")
            price_lbl.pack(side="right", padx=10)

            btn_add = ctk.CTkButton(
                card, text="+ Agregar", width=75, height=28, 
                fg_color="#8B5CF6", hover_color="#7C3AED",
                command=lambda prod=p: self.add_to_cart(prod)
            )
            btn_add.pack(side="right", padx=5)

    def quick_add_pos_barcode(self):
        code = self.ent_pos_search.get().strip()
        if not code:
            return
        prod = ProductModel.get_by_barcode(code)
        if prod:
            self.add_to_cart(prod)
            self.ent_pos_search.delete(0, "end")

    def add_to_cart(self, product):
        # Check if already in cart
        for item in self.cart:
            if item["id"] == product["id"]:
                if item["cantidad"] + 1 > product["stock_actual"]:
                    messagebox.showwarning("Stock Máximo", f"No hay suficiente stock de {product['nombre']}.")
                    return
                item["cantidad"] += 1
                self.render_cart()
                return

        if product["stock_actual"] < 1:
            messagebox.showwarning("Agotado", f"El producto {product['nombre']} está AGOTADO.")
            return

        item = product.copy()
        item["precio_venta"] = float(product["precio_venta"])
        item["precio_costo"] = float(product["precio_costo"])
        item["cantidad"] = 1
        self.cart.append(item)
        self.render_cart()

    def update_cart_qty(self, item_id, delta):
        for item in self.cart:
            if item["id"] == item_id:
                new_qty = item["cantidad"] + delta
                if new_qty <= 0:
                    self.cart.remove(item)
                else:
                    if new_qty > item["stock_actual"]:
                        messagebox.showwarning("Stock Insuficiente", "Supera el stock actual.")
                        return
                    item["cantidad"] = new_qty
                break
        self.render_cart()

    def render_cart(self):
        for w in self.cart_scroll.winfo_children():
            w.destroy()

        subtotal = 0.0
        for item in self.cart:
            line_sub = float(item["precio_venta"]) * item["cantidad"]
            subtotal += line_sub

            row = ctk.CTkFrame(self.cart_scroll, fg_color="#1A1A26", height=40)
            row.pack(fill="x", pady=2)

            lbl_name = ctk.CTkLabel(row, text=item["nombre"][:18], font=ctk.CTkFont(size=11), anchor="w")
            lbl_name.pack(side="left", padx=5)

            btn_minus = ctk.CTkButton(row, text="-", width=22, height=22, fg_color="#4B5563", command=lambda i=item["id"]: self.update_cart_qty(i, -1))
            btn_minus.pack(side="left", padx=2)

            lbl_qty = ctk.CTkLabel(row, text=str(item["cantidad"]), font=ctk.CTkFont(size=11, weight="bold"), width=20)
            lbl_qty.pack(side="left")

            btn_plus = ctk.CTkButton(row, text="+", width=22, height=22, fg_color="#4B5563", command=lambda i=item["id"]: self.update_cart_qty(i, 1))
            btn_plus.pack(side="left", padx=2)

            lbl_total_item = ctk.CTkLabel(row, text=f"RD${line_sub:.2f}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#10B981")
            lbl_total_item.pack(side="right", padx=5)

        itbis = subtotal * 0.18
        total = subtotal + itbis

        if hasattr(self, 'lbl_subtotal') and self.lbl_subtotal.winfo_exists():
            self.lbl_subtotal.configure(text=f"Subtotal: RD$ {subtotal:.2f}")
        if hasattr(self, 'lbl_itbis') and self.lbl_itbis.winfo_exists():
            self.lbl_itbis.configure(text=f"ITBIS (18%): RD$ {itbis:.2f}")
        if hasattr(self, 'lbl_total') and self.lbl_total.winfo_exists():
            self.lbl_total.configure(text=f"TOTAL: RD$ {total:.2f}")

        self.calculate_devuelta()

    def show_toast_notification(self, message, duration_ms=5000):
        """Displays a prominent auto-dismissing non-blocking toast notification banner for 5 seconds."""
        toast = ctk.CTkFrame(self, fg_color="#10B981", corner_radius=10, border_width=2, border_color="#059669", height=50)
        toast.place(relx=0.5, rely=0.88, anchor="center")

        lbl = ctk.CTkLabel(
            toast, text=message, 
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), 
            text_color="#FFFFFF"
        )
        lbl.pack(padx=28, pady=12)

        self.after(duration_ms, lambda: toast.destroy() if toast.winfo_exists() else None)

    # ==========================================
    # TOUCH SCREEN POS & FUNCTION SHORTCUTS [F1-F12]
    # ==========================================
    def focus_pos_search(self):
        """F1 Shortcut: Focus POS Search Input."""
        if hasattr(self, 'ent_pos_search'):
            self.ent_pos_search.focus_set()
            self.ent_pos_search.select_range(0, "end")

    def open_qty_keypad(self):
        """F2 Shortcut: On-Screen Touch Keypad to update Cart Item Quantity."""
        if not self.cart:
            messagebox.showinfo("Carrito Vacío", "Agregue productos al carrito.")
            return

        # Modal Keypad for Quantity
        top = ctk.CTkToplevel(self)
        top.title("🔢 Cantidad Táctil [F2]")
        top.geometry("380x440")
        top.grab_set()
        top.configure(fg_color="#0F172A")
        top.bind("<Escape>", lambda e: top.destroy())

        lbl_t = ctk.CTkLabel(top, text="INGRESE CANTIDAD", font=ctk.CTkFont(family="Poppins", size=16, weight="bold"), text_color="#F8FAFC")
        lbl_t.pack(pady=15)

        ent_val = ctk.CTkEntry(top, width=280, height=45, font=ctk.CTkFont(size=22, weight="bold"), justify="center", fg_color="#1E293B", border_color="#475569")
        ent_val.pack(pady=(0, 15))
        ent_val.insert(0, str(self.cart[-1]["cantidad"]))
        ent_val.focus_set()
        ent_val.bind("<Return>", lambda e: apply_qty())

        # Keypad Buttons Grid (1-9, C, 0, OK)
        pad_frame = ctk.CTkFrame(top, fg_color="transparent")
        pad_frame.pack(padx=20, pady=10)

        def press(key):
            if key == "C":
                ent_val.delete(0, "end")
            elif key == "⌫":
                curr = ent_val.get()
                ent_val.delete(0, "end")
                ent_val.insert(0, curr[:-1])
            else:
                ent_val.insert("end", key)

        keys = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            ["C", "0", "⌫"]
        ]

        for r, row in enumerate(keys):
            for c, k in enumerate(row):
                btn_col = "#DC2626" if k in ["C", "⌫"] else "#334155"
                b = ctk.CTkButton(
                    pad_frame, text=k, width=80, height=50, 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    fg_color=btn_col, hover_color="#475569", corner_radius=8,
                    command=lambda key=k: press(key)
                )
                b.grid(row=r, column=c, padx=5, pady=5)

        def apply_qty():
            try:
                val = int(ent_val.get().strip())
                if val > 0:
                    last_item_id = self.cart[-1]["id"]
                    for item in self.cart:
                        if item["id"] == last_item_id:
                            if val > item["stock_actual"]:
                                messagebox.showwarning("Stock Insuficiente", "Supera el stock actual.")
                                return
                            item["cantidad"] = val
                            break
                    self.render_cart()
                    top.destroy()
            except ValueError:
                pass

        btn_ok = ctk.CTkButton(
            top, text="✔ APLICAR CANTIDAD", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=45, width=280, corner_radius=8,
            command=apply_qty
        )
        btn_ok.pack(pady=15)

    def remove_selected_cart_item(self):
        """F3 Shortcut: Remove last/selected item from cart."""
        if self.cart:
            self.cart.pop()
            self.render_cart()

    def clear_cart_confirm(self):
        """F4 Shortcut: Clear full cart."""
        if self.cart:
            if messagebox.askyesno("Vaciar Carrito", "¿Desea limpiar todos los productos del carrito?"):
                self.cart = []
                self.render_cart()

    def open_quick_stock_lookup(self):
        """F6 Shortcut: Quick stock & price lookup popup."""
        top = ctk.CTkToplevel(self)
        top.title("🔍 Consulta Rápida de Stock y Precios [F6]")
        top.geometry("540x460")
        top.grab_set()
        top.configure(fg_color="#0F172A")
        top.bind("<Escape>", lambda e: top.destroy())

        lbl_t = ctk.CTkLabel(top, text="CONSULTA RÁPIDA DE PRODUCTOS", font=ctk.CTkFont(family="Poppins", size=15, weight="bold"), text_color="#38BDF8")
        lbl_t.pack(pady=12)

        ent_s = ctk.CTkEntry(top, placeholder_text="Escriba código o nombre...", width=470, height=40, fg_color="#1E293B", border_color="#475569")
        ent_s.pack(pady=(0, 10))
        ent_s.focus_set()

        res_scroll = ctk.CTkScrollableFrame(top, width=480, height=310, fg_color="#1E293B")
        res_scroll.pack(padx=15, pady=5)

        def add_and_close(p):
            self.add_to_cart(p)
            top.destroy()

        def search_lookup(e=None):
            for w in res_scroll.winfo_children():
                w.destroy()
            prods = ProductModel.get_all(ent_s.get().strip())
            for p in prods:
                row = ctk.CTkFrame(res_scroll, fg_color="#0F172A", height=38)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=f"{p['nombre']} [{p['codigo_barras']}]", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left", padx=8)
                stk_col = "#10B981" if p['stock_actual'] > p['stock_minimo'] else "#EF4444"
                ctk.CTkLabel(row, text=f"Stock: {p['stock_actual']}", text_color=stk_col, font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=f"RD${float(p['precio_venta']):.2f}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(side="right", padx=6)
                ctk.CTkButton(
                    row, text="+ Agregar", font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color="#2563EB", hover_color="#1D4ED8", width=75, height=26, corner_radius=4,
                    command=lambda prod=p: add_and_close(prod)
                ).pack(side="right", padx=4)

        ent_s.bind("<KeyRelease>", search_lookup)
        search_lookup()

    def open_discount_keypad(self):
        """F8 Shortcut: Apply Discount Modal."""
        if not self.cart:
            messagebox.showinfo("Carrito Vacío", "Agregue productos al carrito.")
            return

        top = ctk.CTkToplevel(self)
        top.title("🏷️ Descuento Especial [F8]")
        top.geometry("380x280")
        top.grab_set()
        top.configure(fg_color="#0F172A")
        top.bind("<Escape>", lambda e: top.destroy())

        lbl_t = ctk.CTkLabel(top, text="APLICAR DESCUENTO EN CARRITO", font=ctk.CTkFont(family="Poppins", size=15, weight="bold"), text_color="#8B5CF6")
        lbl_t.pack(pady=15)

        ent_disc = ctk.CTkEntry(top, placeholder_text="Monto Descuento en RD$", width=280, height=42, font=ctk.CTkFont(size=16), justify="center", fg_color="#1E293B", border_color="#475569")
        ent_disc.pack(pady=(0, 15))
        ent_disc.focus_set()

        def apply_disc():
            try:
                d = float(ent_disc.get().strip() or 0)
                if d > 0 and self.cart:
                    tot_val = sum(float(i["precio_venta"]) * i["cantidad"] for i in self.cart)
                    if tot_val > 0:
                        for item in self.cart:
                            item_val = float(item["precio_venta"]) * item["cantidad"]
                            item_disc = (item_val / tot_val) * d
                            item["precio_venta"] = max(0.0, float(item["precio_venta"]) - (item_disc / item["cantidad"]))
                    self.render_cart()
                    top.destroy()
            except ValueError:
                pass

        ent_disc.bind("<Return>", lambda e: apply_disc())

        btn_apply = ctk.CTkButton(
            top, text="✔ APLICAR DESCUENTO", 
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED", height=44, width=280, corner_radius=8,
            command=apply_disc
        )
        btn_apply.pack(pady=10)

    def reprint_last_ticket(self):
        """F12 Shortcut: Reprint Last Ticket PDF."""
        output_dir = os.path.join(os.getcwd(), "tickets")
        if os.path.exists(output_dir):
            files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".pdf")]
            if files:
                latest_file = max(files, key=os.path.getmtime)
                os.startfile(latest_file)
                return
        messagebox.showinfo("Reimprimir Ticket", "No se encontraron tickets impresos recientes.")

    # ==========================================
    # INTUITIVE IN-PLACE TOUCH PAYMENT VIEW [F10]
    # ==========================================
    def open_touch_payment_modal(self):
        """F10 / Checkout Trigger: Switches right panel to in-place payment view."""
        if not self.cart:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito.")
            return

        if not self.active_caja:
            messagebox.showerror("Caja Cerrada", "Debe abrir una caja antes de procesar ventas.")
            self.load_caja_tab()
            return

        self.show_pos_checkout_view()

    def show_pos_cart_view(self):
        """Restores the normal Cart view in the right panel."""
        for w in self.right_side.winfo_children():
            w.destroy()

        lbl_cart_header = ctk.CTkLabel(
            self.right_side, text="CARRITO DE VENTA", 
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"), text_color="#F8FAFC"
        )
        lbl_cart_header.pack(pady=(12, 5))

        # Cart Table Scroll
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

        # Big Touch Checkout Button
        btn_touch_pay = ctk.CTkButton(
            self.right_side, text="💳 COBRAR Y FACTURAR  [F10]", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=50, corner_radius=8,
            command=self.open_touch_payment_modal
        )
        btn_touch_pay.pack(fill="x", padx=12, pady=(6, 12))

        self.render_cart()

    # ==========================================
    # OPTION 1: INSTANT OVERLAYED TOUCH PAYMENT MODAL [F10]
    # ==========================================
    def open_touch_payment_modal(self):
        """F10 / Checkout Trigger: Instant Overlay Modal Dialog (Option 1)."""
        if not self.cart:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito.")
            return

        if not self.active_caja:
            messagebox.showerror("Caja Cerrada", "Debe abrir una caja antes de procesar ventas.")
            self.load_caja_tab()
            return

        subtotal = sum(float(i["precio_venta"]) * i["cantidad"] for i in self.cart)
        total_pagar = subtotal * 1.18

        pay_win = ctk.CTkToplevel(self)
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
        lbl_monto_total.pack(pady=(0, 10))

        # Payment Method Pill Selector
        method_box = ctk.CTkFrame(pay_win, fg_color="transparent")
        method_box.pack(fill="x", padx=15, pady=(0, 10))

        selected_method = tk.StringVar(value="Efectivo")

        def set_method(m):
            selected_method.set(m)
            for m_name, b_widget in method_btns.items():
                if m_name == m:
                    b_widget.configure(fg_color="#2563EB", hover_color="#1D4ED8")
                else:
                    b_widget.configure(fg_color="#334155", hover_color="#475569")

        method_btns = {}
        methods = [
            ("Efectivo", "💵 Efectivo"),
            ("Tarjeta", "💳 Tarjeta (POS)"),
            ("Transferencia/WhatsApp", "📱 Transferencia"),
            ("Credito", "🤝 Crédito (Fiado)")
        ]

        for m_id, m_label in methods:
            bg_c = "#2563EB" if m_id == "Efectivo" else "#334155"
            btn_m = ctk.CTkButton(
                method_box, text=m_label, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=bg_c, height=40, corner_radius=8,
                command=lambda id_m=m_id: set_method(id_m)
            )
            btn_m.pack(side="left", padx=3, expand=True, fill="x")
            method_btns[m_id] = btn_m

        # Cash Received & Change Layout
        pay_body = ctk.CTkFrame(pay_win, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        pay_body.pack(fill="both", expand=True, padx=15, pady=5)

        # Left side: RD$ Quick Bills | Right side: Keypad & Change
        cash_left = ctk.CTkFrame(pay_body, fg_color="transparent")
        cash_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        cash_right = ctk.CTkFrame(pay_body, fg_color="transparent", width=260)
        cash_right.pack(side="right", fill="both", padx=10, pady=10)

        ctk.CTkLabel(cash_left, text="BILLETES DOMINICANOS (RD$)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(pady=(0, 6))

        ent_recibido_modal = ctk.CTkEntry(cash_right, width=240, height=42, font=ctk.CTkFont(size=20, weight="bold"), justify="center", fg_color="#0F172A", border_color="#475569")
        ent_recibido_modal.pack(pady=(0, 6))
        ent_recibido_modal.insert(0, f"{total_pagar:.2f}")

        lbl_devuelta_modal = ctk.CTkLabel(cash_right, text="Devuelta: RD$ 0.00", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F59E0B")
        lbl_devuelta_modal.pack(pady=(0, 8))

        def update_modal_change():
            try:
                rec = float(ent_recibido_modal.get().strip() or 0)
                dev = max(0.0, rec - total_pagar)
                lbl_devuelta_modal.configure(text=f"Devuelta: RD$ {dev:,.2f}")
            except ValueError:
                lbl_devuelta_modal.configure(text="Devuelta: RD$ 0.00")

        ent_recibido_modal.bind("<KeyRelease>", lambda e: update_modal_change())

        # Dominican Republic Pesos (RD$) Quick Cash Bill Buttons
        bills_frame = ctk.CTkFrame(cash_left, fg_color="transparent")
        bills_frame.pack(fill="both", expand=True)

        def add_cash_bill(amount):
            if amount == "EXACTO":
                val = total_pagar
            elif amount == "CLEAR":
                val = 0.0
            else:
                try:
                    curr = float(ent_recibido_modal.get().strip() or 0)
                    val = curr + amount
                except ValueError:
                    val = float(amount)
            ent_recibido_modal.delete(0, "end")
            ent_recibido_modal.insert(0, f"{val:.2f}")
            update_modal_change()

        bills = [
            (50, "RD$ 50"),
            (100, "RD$ 100"),
            (200, "RD$ 200"),
            (500, "RD$ 500"),
            (1000, "RD$ 1,000"),
            (2000, "RD$ 2,000"),
            ("EXACTO", "Exacto"),
            ("CLEAR", "Borrar (C)")
        ]

        for i, (b_val, b_txt) in enumerate(bills):
            r, c = divmod(i, 2)
            b_col = "#10B981" if b_val == "EXACTO" else ("#DC2626" if b_val == "CLEAR" else "#0F172A")
            b = ctk.CTkButton(
                bills_frame, text=b_txt, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=b_col, hover_color="#334155", height=42, corner_radius=6,
                command=lambda val=b_val: add_cash_bill(val)
            )
            b.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
        bills_frame.grid_columnconfigure(0, weight=1)
        bills_frame.grid_columnconfigure(1, weight=1)

        # Touch Keypad (0-9, .)
        pad_modal = ctk.CTkFrame(cash_right, fg_color="transparent")
        pad_modal.pack(fill="both", expand=True)

        def modal_pad_press(k):
            if k == "C":
                ent_recibido_modal.delete(0, "end")
            elif k == "⌫":
                c_val = ent_recibido_modal.get()
                ent_recibido_modal.delete(0, "end")
                ent_recibido_modal.insert(0, c_val[:-1])
            else:
                ent_recibido_modal.insert("end", k)
            update_modal_change()

        m_keys = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            ["C", "0", "."]
        ]

        for r, row in enumerate(m_keys):
            for c, k in enumerate(row):
                b = ctk.CTkButton(
                    pad_modal, text=k, font=ctk.CTkFont(size=14, weight="bold"),
                    fg_color="#0F172A", hover_color="#475569", width=68, height=38, corner_radius=6,
                    command=lambda key=k: modal_pad_press(key)
                )
                b.grid(row=r, column=c, padx=2, pady=2)

        update_modal_change()

        def confirm_final_checkout():
            tipo_pago = selected_method.get()
            caja_id = self.active_caja["id"]
            user_id = self.current_user["id"]

            try:
                sale_res = VentaModel.procesar_venta(caja_id, user_id, "Cliente General", tipo_pago, self.cart)
                
                # Generate Ticket PDF
                output_dir = os.path.join(os.getcwd(), "tickets")
                os.makedirs(output_dir, exist_ok=True)
                ticket_file = os.path.join(output_dir, f"Ticket_{sale_res['codigo_factura']}.pdf")
                generate_ticket_pdf(sale_res, ticket_file)

                codigo_fact = sale_res["codigo_factura"]
                self.cart = []
                self.search_pos_products()
                self.show_pos_cart_view()
                pay_win.destroy()
                self.show_toast_notification(f"✔ ¡VENTA #{codigo_fact} PROCESADA CON ÉXITO!", 5000)

            except Exception as e:
                messagebox.showerror("Error en Venta", f"Ocurrió un error al guardar la venta: {e}")

        btn_confirm_pay = ctk.CTkButton(
            pay_win, text="✔ CONFIRMAR VENTA E IMPRIMIR COMPROBANTE  [ENTER]", 
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=50, corner_radius=8,
            command=confirm_final_checkout
        )
        btn_confirm_pay.pack(fill="x", padx=15, pady=(5, 15))
        pay_win.bind("<Return>", lambda e: confirm_final_checkout())
        pay_win.bind("<Escape>", lambda e: pay_win.destroy())

    def calculate_devuelta(self):
        if hasattr(self, 'ent_recibido'):
            try:
                subtotal = sum(float(i["precio_venta"]) * i["cantidad"] for i in self.cart)
                total = subtotal * 1.18
                recibido = float(self.ent_recibido.get().strip() or 0)
                devuelta = max(0.0, recibido - total)
                if hasattr(self, 'lbl_devuelta'):
                    self.lbl_devuelta.configure(text=f"Devuelta: RD$ {devuelta:.2f}")
            except Exception:
                pass

    def process_pos_checkout(self):
        self.open_touch_payment_modal()

    # ==========================================
    # TAB 2: INVENTARIO & ALERTAS
    # ==========================================
    def load_inventory_tab(self):
        self.clear_content()

        inv_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        inv_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header Action Controls
        ctrl_bar = ctk.CTkFrame(inv_frame, fg_color="#16161F", height=50)
        ctrl_bar.pack(fill="x", pady=(0, 10))

        self.ent_inv_search = ctk.CTkEntry(ctrl_bar, placeholder_text="Buscar en inventario...", width=250)
        self.ent_inv_search.pack(side="left", padx=10, pady=10)
        self.ent_inv_search.bind("<KeyRelease>", lambda e: self.render_inventory_table())

        btn_new_prod = ctk.CTkButton(ctrl_bar, text="+ Nuevo Producto", fg_color="#10B981", hover_color="#059669", command=self.modal_product_form)
        btn_new_prod.pack(side="left", padx=5)

        btn_mov = ctk.CTkButton(ctrl_bar, text="📦 Entrada / Merma", fg_color="#F59E0B", hover_color="#D97706", command=self.modal_movement_form)
        btn_mov.pack(side="left", padx=5)

        btn_exp_excel = ctk.CTkButton(ctrl_bar, text="📊 Exportar Excel", fg_color="#3B82F6", hover_color="#2563EB", command=self.export_inv_excel)
        btn_exp_excel.pack(side="right", padx=10)

        btn_exp_pdf = ctk.CTkButton(ctrl_bar, text="📄 Exportar PDF", fg_color="#EC4899", hover_color="#DB2777", command=self.export_inv_pdf)
        btn_exp_pdf.pack(side="right", padx=5)

        # Inventory Table Frame
        self.table_scroll = ctk.CTkScrollableFrame(inv_frame, fg_color="#16161F")
        self.table_scroll.pack(fill="both", expand=True)

        self.render_inventory_table()

    def render_inventory_table(self):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        term = self.ent_inv_search.get().strip() if hasattr(self, 'ent_inv_search') else ""
        products = ProductModel.get_all(term)

        # Headers
        headers = ["Cód. Barras", "Nombre Producto", "Categoría", "P. Costo", "P. Venta", "Stock", "Stock Mín.", "Estado", "Acciones"]
        cols_w = [110, 180, 120, 80, 80, 60, 70, 100, 120]

        head_row = ctk.CTkFrame(self.table_scroll, fg_color="#1F2937", height=35)
        head_row.pack(fill="x", pady=2)

        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(head_row, text=h, font=ctk.CTkFont(size=11, weight="bold"), width=cols_w[idx])
            lbl.pack(side="left", padx=2)

        for p in products:
            row = ctk.CTkFrame(self.table_scroll, fg_color="#111118", height=38)
            row.pack(fill="x", pady=2)

            stock = p['stock_actual']
            min_s = p['stock_minimo']
            status_txt = "NORMAL"
            status_bg = "#10B981"

            if stock <= 0:
                status_txt = "AGOTADO"
                status_bg = "#EF4444"
            elif stock <= min_s:
                status_txt = "STOCK BAJO"
                status_bg = "#F59E0B"

            values = [
                p['codigo_barras'], p['nombre'], p.get('categoria_nombre', 'N/A'),
                f"RD${p['precio_costo']:.2f}", f"RD${p['precio_venta']:.2f}",
                str(stock), str(min_s)
            ]

            for idx, val in enumerate(values):
                lbl = ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=11), width=cols_w[idx])
                lbl.pack(side="left", padx=2)

            # Badge
            badge = ctk.CTkLabel(row, text=f" {status_txt} ", font=ctk.CTkFont(size=10, weight="bold"), fg_color=status_bg, text_color="white", corner_radius=4, width=cols_w[7])
            badge.pack(side="left", padx=2)

            # Edit Button
            btn_edit = ctk.CTkButton(row, text="✏", width=30, height=24, fg_color="#374151", command=lambda prod=p: self.modal_product_form(prod))
            btn_edit.pack(side="left", padx=2)

            btn_del = ctk.CTkButton(row, text="🗑", width=30, height=24, fg_color="#EF4444", command=lambda prod=p: self.delete_prod(prod))
            btn_del.pack(side="left", padx=2)

    def delete_prod(self, prod):
        if messagebox.askyesno("Eliminar Producto", f"¿Seguro que deseas eliminar '{prod['nombre']}'?"):
            ProductModel.delete_product(prod["id"])
            self.render_inventory_table()

    def modal_product_form(self, prod=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Producto" if prod else "Nuevo Producto")
        dialog.geometry("450x520")
        dialog.grab_set()

        lbl_t = ctk.CTkLabel(dialog, text="FORMULARIO DE PRODUCTO", font=ctk.CTkFont(size=16, weight="bold"), text_color="#EC4899")
        lbl_t.pack(pady=15)

        ent_code = ctk.CTkEntry(dialog, placeholder_text="Código de Barras", width=320)
        ent_code.pack(pady=6)
        if prod: ent_code.insert(0, prod["codigo_barras"])

        ent_name = ctk.CTkEntry(dialog, placeholder_text="Nombre del Producto", width=320)
        ent_name.pack(pady=6)
        if prod: ent_name.insert(0, prod["nombre"])

        categories = ProductModel.get_categories()
        cat_names = [c["nombre"] for c in categories]
        cat_map = {c["nombre"]: c["id"] for c in categories}

        cmb_cat = ctk.CTkComboBox(dialog, values=cat_names, width=320)
        cmb_cat.pack(pady=6)

        ent_cost = ctk.CTkEntry(dialog, placeholder_text="Precio Costo (RD$)", width=320)
        ent_cost.pack(pady=6)
        if prod: ent_cost.insert(0, str(prod["precio_costo"]))

        ent_price = ctk.CTkEntry(dialog, placeholder_text="Precio Venta (RD$)", width=320)
        ent_price.pack(pady=6)
        if prod: ent_price.insert(0, str(prod["precio_venta"]))

        ent_stock = ctk.CTkEntry(dialog, placeholder_text="Stock Actual", width=320)
        ent_stock.pack(pady=6)
        if prod: ent_stock.insert(0, str(prod["stock_actual"]))

        ent_min = ctk.CTkEntry(dialog, placeholder_text="Stock Mínimo Alerta", width=320)
        ent_min.pack(pady=6)
        if prod: ent_min.insert(0, str(prod["stock_minimo"]))

        def save():
            try:
                data = {
                    "codigo_barras": ent_code.get().strip(),
                    "nombre": ent_name.get().strip(),
                    "categoria_id": cat_map.get(cmb_cat.get(), 1),
                    "precio_costo": float(ent_cost.get().strip()),
                    "precio_venta": float(ent_price.get().strip()),
                    "stock_actual": int(ent_stock.get().strip()),
                    "stock_minimo": int(ent_min.get().strip()),
                }
                if prod:
                    data["id"] = prod["id"]
                ProductModel.save_product(data)
                dialog.destroy()
                self.render_inventory_table()
            except Exception as e:
                messagebox.showerror("Error", f"Verifique los datos ingresados: {e}")

        btn_save = ctk.CTkButton(dialog, text="Guardar Producto", fg_color="#10B981", hover_color="#059669", width=320, height=40, command=save)
        btn_save.pack(pady=20)

    def modal_movement_form(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Registro de Movimiento de Inventario")
        dialog.geometry("420x420")
        dialog.grab_set()

        lbl_t = ctk.CTkLabel(dialog, text="ENTRADA / AJUSTE / MERMA", font=ctk.CTkFont(size=15, weight="bold"), text_color="#F59E0B")
        lbl_t.pack(pady=15)

        products = ProductModel.get_all()
        prod_map = {f"{p['nombre']} [{p['codigo_barras']}]": p["id"] for p in products}
        
        cmb_prod = ctk.CTkComboBox(dialog, values=list(prod_map.keys()), width=320)
        cmb_prod.pack(pady=8)

        cmb_tipo = ctk.CTkComboBox(dialog, values=["Entrada Suplidor", "Salida/Ajuste", "Mermas/Vencido"], width=320)
        cmb_tipo.pack(pady=8)

        ent_qty = ctk.CTkEntry(dialog, placeholder_text="Cantidad (Unidades)", width=320)
        ent_qty.pack(pady=8)

        ent_motivo = ctk.CTkEntry(dialog, placeholder_text="Motivo / Factura Suplidor", width=320)
        ent_motivo.pack(pady=8)

        def save_mov():
            try:
                p_id = prod_map[cmb_prod.get()]
                tipo = cmb_tipo.get()
                cant = int(ent_qty.get().strip())
                motivo = ent_motivo.get().strip() or "Ajuste manual"
                
                InventoryMovementModel.registrar_movimiento(p_id, tipo, cant, motivo, self.current_user["id"])
                dialog.destroy()
                self.render_inventory_table()
                messagebox.showinfo("Éxito", "Movimiento de inventario registrado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")

        btn_save = ctk.CTkButton(dialog, text="Registrar Movimiento", fg_color="#F59E0B", width=320, height=40, command=save_mov)
        btn_save.pack(pady=20)

    def export_inv_excel(self):
        products = ProductModel.get_all()
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            export_inventory_to_excel(products, file_path)
            messagebox.showinfo("Exportación Exitosa", f"Inventario exportado a Excel:\n{file_path}")

    def export_inv_pdf(self):
        products = ProductModel.get_all()
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            generate_inventory_report_pdf(products, file_path)
            messagebox.showinfo("Exportación Exitosa", f"Reporte de Inventario guardado en PDF:\n{file_path}")

    # ==========================================
    # TAB 3: CAJA (APERTURA Y CIERRE)
    # ==========================================
    def load_caja_tab(self):
        self.clear_content()

        caja_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        caja_frame.pack(fill="both", expand=True, padx=20, pady=20)

        card_caja = ctk.CTkFrame(caja_frame, fg_color="#16161F", corner_radius=12, width=600)
        card_caja.pack(pady=30, padx=20)

        lbl_t = ctk.CTkLabel(card_caja, text="GESTIÓN DE CAJA Y TURNOS", font=ctk.CTkFont(size=18, weight="bold"), text_color="#8B5CF6")
        lbl_t.pack(pady=(20, 10))

        if self.active_caja:
            status_txt = f"ESTADO: CAJA ABIERTA (ID #{self.active_caja['id']})"
            lbl_st = ctk.CTkLabel(card_caja, text=status_txt, font=ctk.CTkFont(size=14, weight="bold"), text_color="#10B981")
            lbl_st.pack(pady=5)

            lbl_f = ctk.CTkLabel(card_caja, text=f"Monto Inicial: RD$ {self.active_caja['monto_inicial']:.2f}\nApertura: {self.active_caja['fecha_apertura']}", font=ctk.CTkFont(size=12))
            lbl_f.pack(pady=10)

            ent_real = ctk.CTkEntry(card_caja, placeholder_text="Monto Final Real en Efectivo (RD$)", width=300, height=40)
            ent_real.pack(pady=15)

            def do_close():
                try:
                    val = float(ent_real.get().strip())
                    res = CajaModel.cerrar_caja(self.active_caja["id"], val)
                    self.active_caja = None
                    self.lbl_caja_badge.configure(text="  Caja: CERRADA  ", fg_color="#EF4444")
                    messagebox.showinfo("Cierre de Caja", f"Caja cerrada exitosamente.\n\nMonto Teórico: RD$ {res['monto_teorico']:.2f}\nMonto Real: RD$ {res['monto_real']:.2f}\nDiferencia: RD$ {res['diferencia']:.2f}")
                    self.load_caja_tab()
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un monto válido.")

            btn_close = ctk.CTkButton(card_caja, text="🔒 CERRAR CAJA Y EFECTUAR CUADRE", fg_color="#EF4444", hover_color="#DC2626", width=300, height=45, command=do_close)
            btn_close.pack(pady=(10, 25))

        else:
            lbl_st = ctk.CTkLabel(card_caja, text="ESTADO: CAJA CERRADA", font=ctk.CTkFont(size=14, weight="bold"), text_color="#EF4444")
            lbl_st.pack(pady=5)

            ent_init = ctk.CTkEntry(card_caja, placeholder_text="Monto Inicial en Caja (RD$)", width=300, height=40)
            ent_init.pack(pady=15)
            ent_init.insert(0, "1500.00")

            def do_open():
                try:
                    val = float(ent_init.get().strip())
                    self.active_caja = CajaModel.abrir_caja(self.current_user["id"], val)
                    self.lbl_caja_badge.configure(text=f"  Caja #{self.active_caja['id']} ABIERTA  ", fg_color="#10B981")
                    messagebox.showinfo("Apertura Exitosa", f"Caja aperturada con RD$ {val:.2f}")
                    self.load_caja_tab()
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un monto inicial válido.")

            btn_open = ctk.CTkButton(card_caja, text="🔓 ABRIR NUEVA CAJA", fg_color="#10B981", hover_color="#059669", width=300, height=45, command=do_open)
            btn_open.pack(pady=(10, 25))

    # ==========================================
    # TAB 4: REPORTES & VENTAS
    # ==========================================
    def load_reports_tab(self):
        self.clear_content()

        rep_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        rep_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Metrics summary cards
        summary = ReportModel.get_sales_summary()

        cards_box = ctk.CTkFrame(rep_frame, fg_color="transparent")
        cards_box.pack(fill="x", pady=(0, 15))

        card1 = ctk.CTkFrame(cards_box, fg_color="#16161F", corner_radius=10, height=80)
        card1.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(card1, text="VENTAS HOY", font=ctk.CTkFont(size=11), text_color="#A0A0B0").pack(pady=(10,0))
        ctk.CTkLabel(card1, text=str(summary["total_ventas_cant"]), font=ctk.CTkFont(size=20, weight="bold"), text_color="#EC4899").pack(pady=(0,10))

        card2 = ctk.CTkFrame(cards_box, fg_color="#16161F", corner_radius=10, height=80)
        card2.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(card2, text="INGRESOS HOY", font=ctk.CTkFont(size=11), text_color="#A0A0B0").pack(pady=(10,0))
        ctk.CTkLabel(card2, text=f"RD$ {summary['total_ingresos']:.2f}", font=ctk.CTkFont(size=20, weight="bold"), text_color="#10B981").pack(pady=(0,10))

        # Action Buttons
        btn_box = ctk.CTkFrame(rep_frame, fg_color="transparent")
        btn_box.pack(fill="x", pady=10)

        btn_exp_sales_excel = ctk.CTkButton(btn_box, text="📊 Exportar Ventas a Excel", fg_color="#3B82F6", command=self.export_sales_excel)
        btn_exp_sales_excel.pack(side="left", padx=5)

        # Sales History Table
        lbl_hist = ctk.CTkLabel(rep_frame, text="HISTORIAL RECIENTE DE FACTURAS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#8B5CF6")
        lbl_hist.pack(anchor="w", pady=(15, 5))

        sales_scroll = ctk.CTkScrollableFrame(rep_frame, fg_color="#16161F")
        sales_scroll.pack(fill="both", expand=True)

        sales = ReportModel.get_sales_history()
        headers = ["Factura #", "Fecha", "Cliente", "Tipo Pago", "Subtotal", "ITBIS", "Total (RD$)"]
        cols_w = [140, 160, 140, 120, 90, 80, 100]

        head_row = ctk.CTkFrame(sales_scroll, fg_color="#1F2937", height=35)
        head_row.pack(fill="x", pady=2)

        for idx, h in enumerate(headers):
            ctk.CTkLabel(head_row, text=h, font=ctk.CTkFont(size=11, weight="bold"), width=cols_w[idx]).pack(side="left", padx=2)

        for s in sales:
            row = ctk.CTkFrame(sales_scroll, fg_color="#111118", height=32)
            row.pack(fill="x", pady=2)

            vals = [
                s['codigo_factura'], str(s['fecha'])[:19], s['cliente_nombre'],
                s['tipo_pago'], f"RD${s['subtotal']:.2f}", f"RD${s['itbis_impuesto']:.2f}", f"RD${s['total']:.2f}"
            ]
            for idx, val in enumerate(vals):
                ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=11), width=cols_w[idx]).pack(side="left", padx=2)

    def export_sales_excel(self):
        sales = ReportModel.get_sales_history(500)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            export_sales_to_excel(sales, file_path)
            messagebox.showinfo("Exportación Exitosa", f"Ventas exportadas a Excel:\n{file_path}")

if __name__ == "__main__":
    app = POSApp()
    app.mainloop()
