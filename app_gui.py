import os
import sys
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk

from PIL import Image, ImageTk
from models import UserModel, ProductModel, DepartmentModel, SubDepartmentModel, CajaModel, VentaModel, InventoryMovementModel, ReportModel
from utils.pdf_generator import generate_ticket_pdf, generate_inventory_report_pdf
from utils.excel_exporter import export_inventory_to_excel, export_sales_to_excel
from report_pdf import generate_pdf_report, print_pdf_file

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

        # ── SQL Server Connection Status Banner ──────────────────────────
        from database import check_db_status
        self._db_connected, self._db_detail = check_db_status()

        if self._db_connected:
            banner_bg   = "#065F46"
            banner_text = f"  ✅  SQL Server — Conexión exitosa  |  {self._db_detail[:85]}"
            banner_fg   = "#A7F3D0"
        else:
            banner_bg   = "#7F1D1D"
            banner_text = f"  🔴  SQL Server no disponible  |  {self._db_detail[:90]}"
            banner_fg   = "#FCA5A5"

        db_banner = ctk.CTkFrame(self.container, fg_color=banner_bg, height=30, corner_radius=0)
        db_banner.pack(side="top", fill="x")
        db_banner.pack_propagate(False)
        ctk.CTkLabel(
            db_banner, text=banner_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=banner_fg
        ).pack(side="left", padx=14, pady=6)
        if not self._db_connected:
            ctk.CTkButton(
                db_banner, text="🔄 Reintentar", width=120, height=22,
                fg_color="#991B1B", hover_color="#B91C1C",
                font=ctk.CTkFont(size=10, weight="bold"),
                command=self.show_login
            ).pack(side="right", padx=12, pady=4)

        # Auto-remove banner after 5 seconds
        self.after(5000, lambda: db_banner.destroy() if db_banner.winfo_exists() else None)
        # ─────────────────────────────────────────────────────────────────

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
        # Block login if SQL Server is offline
        if not getattr(self, '_db_connected', True):
            messagebox.showerror(
                "Sin Conexión a SQL Server",
                "No es posible iniciar sesión sin conexión a SQL Server.\n\n"
                f"Detalle: {getattr(self, '_db_detail', 'Error desconocido')}\n\n"
                "Verifique que el servidor SQL Server esté encendido y accesible,\n"
                "luego use el botón 'Reintentar' para reconectar."
            )
            return

        u = self.ent_username.get().strip()
        p = self.ent_password.get().strip()

        try:
            user = UserModel.authenticate(u, p)
        except RuntimeError as e:
            messagebox.showerror("Sin Conexión a SQL Server", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"Error al conectar con la base de datos:\n{e}")
            return

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
            ("[F10] Cobrar ➔", "#10B981", self.open_touch_payment_modal),
            ("[F12] Ticket", "#475569", self.reprint_last_ticket),
        ]

        for i in range(len(funcs)):
            func_bar.grid_columnconfigure(i, weight=1)

        for idx, (text, col, cmd) in enumerate(funcs):
            btn = ctk.CTkButton(
                func_bar, text=text, font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=col, hover_color="#1E293B", height=36, corner_radius=6,
                width=0,
                command=cmd
            )
            btn.grid(row=0, column=idx, padx=2, pady=4, sticky="ew")

        # Split left (Catalog/Search) and right (Cart/Checkout)
        body_split = ctk.CTkFrame(pos_frame, fg_color="transparent")
        body_split.pack(fill="both", expand=True)

        left_side = ctk.CTkFrame(body_split, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right_side = ctk.CTkFrame(body_split, width=480, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        self.right_side.pack(side="right", fill="both", padx=(10, 0))

        # --- LEFT SIDE: Search & Product Selection ---
        search_box = ctk.CTkFrame(left_side, fg_color="transparent")
        search_box.pack(fill="x", padx=12, pady=(12, 6))

        self.ent_pos_search = ctk.CTkEntry(
            search_box, placeholder_text="🔍 Escanear Código de Barras o Buscar Producto [F1]...",
            height=44, font=ctk.CTkFont(size=13), fg_color="#0F172A", border_color="#475569", corner_radius=6
        )
        self.ent_pos_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ent_pos_search.bind("<KeyRelease>", lambda e: self.search_pos_products())
        self.ent_pos_search.bind("<Return>", lambda e: self.quick_add_pos_barcode())

        # --- SUB-DEPARTMENTS QUICK FILTER BAR & FLIP CHART BUTTON ---
        subdep_bar = ctk.CTkFrame(left_side, fg_color="transparent")
        subdep_bar.pack(fill="x", padx=12, pady=(0, 10))

        self.active_subdep_filter = None

        quick_subdeps = [
            ("🌟 Todos", None),
            ("🌾 Granos", 1),
            ("🥤 Refrescos", 5),
            ("🥛 Lácteos", 8),
            ("🧹 Limpieza", 11),
        ]

        for label, sd_id in quick_subdeps:
            btn_sd = ctk.CTkButton(
                subdep_bar, text=label, font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#334155" if self.active_subdep_filter != sd_id else "#2563EB",
                hover_color="#475569", height=32, width=0, corner_radius=6,
                command=lambda s_id=sd_id: self.set_subdep_filter(s_id)
            )
            btn_sd.pack(side="left", padx=2, expand=True, fill="x")

        # Big Flip Chart Overlay Trigger
        btn_flip = ctk.CTkButton(
            subdep_bar, text="📋 Flip Chart", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED", height=32, width=110, corner_radius=6,
            command=self.open_flip_chart_modal
        )
        btn_flip.pack(side="right", padx=(4, 0))

        # Products Scrollable Grid/List
        self.products_scroll = ctk.CTkScrollableFrame(left_side, fg_color="transparent")
        self.products_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.search_pos_products()

        # --- RIGHT SIDE: Default Cart View ---
        self.show_pos_cart_view()

        self.render_cart()

    def set_subdep_filter(self, subdep_id):
        self.active_subdep_filter = subdep_id
        self.search_pos_products()

    def open_flip_chart_modal(self):
        FlipChartModal(self)

    def search_pos_products(self):
        term = self.ent_pos_search.get().strip() if hasattr(self, 'ent_pos_search') else ""
        subdep_id = getattr(self, 'active_subdep_filter', None)
        products = ProductModel.get_all(search_term=term, subdep_id=subdep_id)

        for w in self.products_scroll.winfo_children():
            w.destroy()

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll, text="No se encontraron productos.", text_color="#A0A0B0")
            lbl.pack(pady=20)
            return

        for p in products:
            card = ctk.CTkFrame(self.products_scroll, fg_color="#1F2937", height=50)
            card.pack(fill="x", pady=3)

            subdep_tag = p.get('subdepartamento_nombre') or 'General'
            name_lbl = ctk.CTkLabel(
                card, 
                text=f"{p['nombre']}  •  [{subdep_tag}]\nCód: {p['codigo_barras']}", 
                anchor="w", 
                font=ctk.CTkFont(size=12, weight="bold")
            )
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
                self.selected_cart_item_id = item["id"]
                self.render_cart()
                return

        if product["stock_actual"] < 1:
            messagebox.showwarning("Agotado", f"El producto {product['nombre']} está AGOTADO.")
            return

        item = product.copy()
        orig_price = float(product["precio_venta"])
        item["precio_original"] = orig_price
        item["precio_venta"] = orig_price
        item["descuento_monto"] = 0.0
        item["precio_costo"] = float(product["precio_costo"])
        item["cantidad"] = 1
        self.cart.append(item)
        self.selected_cart_item_id = item["id"]
        self.render_cart()

    def select_cart_item(self, item_id):
        self.selected_cart_item_id = item_id
        self.render_cart()

    def update_cart_qty(self, item_id, delta):
        for item in self.cart:
            if item["id"] == item_id:
                new_qty = item["cantidad"] + delta
                if new_qty <= 0:
                    self.cart.remove(item)
                    if self.selected_cart_item_id == item_id:
                        self.selected_cart_item_id = self.cart[-1]["id"] if self.cart else None
                else:
                    if new_qty > item["stock_actual"]:
                        messagebox.showwarning("Stock Insuficiente", "Supera el stock actual.")
                        return
                    item["cantidad"] = new_qty
                    self.selected_cart_item_id = item_id
                break
        self.render_cart()

    def render_cart(self):
        for w in self.cart_scroll.winfo_children():
            w.destroy()

        subtotal = 0.0
        for item in self.cart:
            is_selected = hasattr(self, 'selected_cart_item_id') and (self.selected_cart_item_id == item["id"])
            
            effective_price = float(item.get("precio_venta", item["precio_original"]))
            line_sub = effective_price * item["cantidad"]
            subtotal += line_sub

            bg_col = "#2563EB" if is_selected else "#1A1A26"
            border_col = "#60A5FA" if is_selected else "#334155"

            row = ctk.CTkFrame(
                self.cart_scroll, 
                fg_color=bg_col, 
                corner_radius=8, 
                border_width=2 if is_selected else 1, 
                border_color=border_col, 
                height=68
            )
            row.pack(fill="x", pady=4, padx=2)
            row.bind("<Button-1>", lambda e, i_id=item["id"]: self.select_cart_item(i_id))

            # --- ROW LINE 1: FULL PRODUCT NAME (LEFT) & LINE TOTAL (RIGHT) ---
            top_line = ctk.CTkFrame(row, fg_color="transparent")
            top_line.pack(fill="x", padx=10, pady=(6, 2))
            top_line.bind("<Button-1>", lambda e, i_id=item["id"]: self.select_cart_item(i_id))

            name_prefix = "👉 " if is_selected else ""
            lbl_name = ctk.CTkLabel(
                top_line, 
                text=f"{name_prefix}{item['nombre']}", 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color="#FFFFFF" if is_selected else "#F8FAFC",
                anchor="w"
            )
            lbl_name.pack(side="left", fill="x", expand=True)
            lbl_name.bind("<Button-1>", lambda e, i_id=item["id"]: self.select_cart_item(i_id))

            lbl_total_item = ctk.CTkLabel(
                top_line, text=f"RD$ {line_sub:.2f}", 
                font=ctk.CTkFont(size=14, weight="bold"), 
                text_color="#FDE047" if is_selected else "#38BDF8",
                anchor="e"
            )
            lbl_total_item.pack(side="right", padx=(8, 0))
            lbl_total_item.bind("<Button-1>", lambda e, i_id=item["id"]: self.select_cart_item(i_id))

            # --- ROW LINE 2: DISCOUNT / UNIT INFO (LEFT) & TOUCH QTY BUTTONS [-] N [+] (RIGHT) ---
            bottom_line = ctk.CTkFrame(row, fg_color="transparent")
            bottom_line.pack(fill="x", padx=10, pady=(0, 6))
            bottom_line.bind("<Button-1>", lambda e, i_id=item["id"]: self.select_cart_item(i_id))

            # Touch Quantity controls: [-] Qty [+] on the right
            qty_box = ctk.CTkFrame(bottom_line, fg_color="transparent")
            qty_box.pack(side="right")

            btn_minus = ctk.CTkButton(
                qty_box, text="-", width=34, height=28, 
                font=ctk.CTkFont(size=16, weight="bold"), 
                fg_color="#DC2626", hover_color="#B91C1C", corner_radius=6,
                command=lambda i=item["id"]: self.update_cart_qty(i, -1)
            )
            btn_minus.pack(side="left", padx=1)

            lbl_qty = ctk.CTkLabel(
                qty_box, text=str(item["cantidad"]), 
                font=ctk.CTkFont(size=14, weight="bold"), 
                text_color="#FFFFFF", width=28
            )
            lbl_qty.pack(side="left")

            btn_plus = ctk.CTkButton(
                qty_box, text="+", width=34, height=28, 
                font=ctk.CTkFont(size=16, weight="bold"), 
                fg_color="#10B981", hover_color="#059669", corner_radius=6,
                command=lambda i=item["id"]: self.update_cart_qty(i, 1)
            )
            btn_plus.pack(side="left", padx=1)

            # Left side of line 2: Unit Price or Discount Tag
            disc_val = item.get("descuento_monto", 0.0)
            orig_val = item.get("precio_original", effective_price)
            if disc_val > 0:
                info_text = f"Orig: RD${orig_val:.2f}  Desc: -RD${disc_val:.2f}/u"
                info_color = "#FDE047" if is_selected else "#F59E0B"
            else:
                info_text = f"Precio Unit: RD$ {effective_price:.2f}"
                info_color = "#E2E8F0" if is_selected else "#94A3B8"

            lbl_info = ctk.CTkLabel(
                bottom_line, text=info_text, 
                font=ctk.CTkFont(size=10, weight="bold"), 
                text_color=info_color, anchor="w"
            )
            lbl_info.pack(side="left", fill="x", expand=True, padx=(0, 6))
            lbl_info.bind("<Button-1>", lambda e, i_id=item["id"]: self.select_cart_item(i_id))

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
        """F2 Shortcut: On-Screen Touch Keypad to update Quantity for Selected Cart Item."""
        if not self.cart:
            messagebox.showinfo("Carrito Vacío", "Agregue productos al carrito.")
            return

        target_item = None
        if hasattr(self, 'selected_cart_item_id') and self.selected_cart_item_id:
            for item in self.cart:
                if item["id"] == self.selected_cart_item_id:
                    target_item = item
                    break
        if not target_item:
            target_item = self.cart[-1]
            self.selected_cart_item_id = target_item["id"]

        top = ctk.CTkToplevel(self)
        top.title(f"🔢 Cantidad Táctil - {target_item['nombre']}")
        top.geometry("400x480")
        top.grab_set()
        top.configure(fg_color="#0F172A")
        top.bind("<Escape>", lambda e: top.destroy())

        lbl_t = ctk.CTkLabel(
            top, text="INGRESE CANTIDAD", 
            font=ctk.CTkFont(family="Poppins", size=16, weight="bold"), 
            text_color="#F8FAFC"
        )
        lbl_t.pack(pady=(15, 2))

        lbl_sub = ctk.CTkLabel(
            top, text=f"Ítem: {target_item['nombre']}", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8"
        )
        lbl_sub.pack(pady=(0, 10))

        ent_val = ctk.CTkEntry(
            top, width=280, height=45, 
            font=ctk.CTkFont(size=22, weight="bold"), 
            justify="center", fg_color="#1E293B", border_color="#475569"
        )
        ent_val.pack(pady=(0, 15))
        ent_val.insert(0, str(target_item["cantidad"]))
        ent_val.focus_set()
        ent_val.bind("<Return>", lambda e: apply_qty())

        pad_frame = ctk.CTkFrame(top, fg_color="transparent")
        pad_frame.pack(padx=20, pady=5)

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
                    pad_frame, text=k, width=80, height=48, 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    fg_color=btn_col, hover_color="#475569", corner_radius=8,
                    command=lambda key=k: press(key)
                )
                b.grid(row=r, column=c, padx=5, pady=4)

        def apply_qty():
            try:
                val = int(ent_val.get().strip())
                if val > 0:
                    if val > target_item["stock_actual"]:
                        messagebox.showwarning("Stock Insuficiente", f"Supera el stock actual ({target_item['stock_actual']}).")
                        return
                    target_item["cantidad"] = val
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
        """F3 Shortcut: Remove selected item from cart (or last item)."""
        if not self.cart:
            return

        if hasattr(self, 'selected_cart_item_id') and self.selected_cart_item_id:
            self.cart = [i for i in self.cart if i["id"] != self.selected_cart_item_id]
            self.selected_cart_item_id = self.cart[-1]["id"] if self.cart else None
        else:
            self.cart.pop()
            self.selected_cart_item_id = self.cart[-1]["id"] if self.cart else None

        self.render_cart()

    def clear_cart_confirm(self):
        """F4 Shortcut: Clear full cart."""
        if self.cart:
            if messagebox.askyesno("Vaciar Carrito", "¿Desea limpiar todos los productos del carrito?"):
                self.cart = []
                self.selected_cart_item_id = None
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
        """F8 Shortcut: Apply Discount per Selected Item or Entire Transaction."""
        if not self.cart:
            messagebox.showinfo("Carrito Vacío", "Agregue productos al carrito.")
            return

        target_item = None
        if hasattr(self, 'selected_cart_item_id') and self.selected_cart_item_id:
            for item in self.cart:
                if item["id"] == self.selected_cart_item_id:
                    target_item = item
                    break

        top = ctk.CTkToplevel(self)
        top.title("🏷️ Descuento Especial [F8]")
        top.geometry("440x380")
        top.grab_set()
        top.configure(fg_color="#0F172A")
        top.bind("<Escape>", lambda e: top.destroy())

        lbl_t = ctk.CTkLabel(
            top, text="APLICAR DESCUENTO", 
            font=ctk.CTkFont(family="Poppins", size=16, weight="bold"), text_color="#8B5CF6"
        )
        lbl_t.pack(pady=(15, 5))

        target_label_text = f"Ítem: {target_item['nombre']}" if target_item else "Toda la venta"
        lbl_target_info = ctk.CTkLabel(
            top, text=f"Aplicando a: {target_label_text}", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8"
        )
        lbl_target_info.pack(pady=(0, 10))

        mode_var = ctk.StringVar(value="item" if target_item else "cart")
        mode_frame = ctk.CTkFrame(top, fg_color="transparent")
        mode_frame.pack(pady=(0, 10))

        rb_item = ctk.CTkRadioButton(
            mode_frame, text="Ítem Seleccionado", variable=mode_var, value="item",
            state="normal" if target_item else "disabled"
        )
        rb_item.pack(side="left", padx=10)

        rb_cart = ctk.CTkRadioButton(
            mode_frame, text="Toda la Venta (Global)", variable=mode_var, value="cart"
        )
        rb_cart.pack(side="left", padx=10)

        type_var = ctk.StringVar(value="monto")
        type_frame = ctk.CTkFrame(top, fg_color="transparent")
        type_frame.pack(pady=(0, 10))

        rb_monto = ctk.CTkRadioButton(type_frame, text="Monto Fijo (RD$)", variable=type_var, value="monto")
        rb_monto.pack(side="left", padx=10)

        rb_pct = ctk.CTkRadioButton(type_frame, text="Porcentaje (%)", variable=type_var, value="porcentaje")
        rb_pct.pack(side="left", padx=10)

        ent_disc = ctk.CTkEntry(
            top, placeholder_text="Ingrese valor...", 
            width=300, height=45, font=ctk.CTkFont(size=20, weight="bold"), 
            justify="center", fg_color="#1E293B", border_color="#475569"
        )
        ent_disc.pack(pady=(0, 15))
        ent_disc.focus_set()

        def apply_disc():
            try:
                val = float(ent_disc.get().strip() or 0)
                if val < 0:
                    return

                disc_mode = mode_var.get()
                disc_type = type_var.get()

                if disc_mode == "item" and target_item:
                    orig_unit = float(target_item.get("precio_original", target_item["precio_venta"]))
                    if disc_type == "porcentaje":
                        disc_unit = orig_unit * (val / 100.0)
                    else:
                        disc_unit = val

                    target_item["descuento_monto"] = min(orig_unit, disc_unit)
                    target_item["precio_venta"] = max(0.0, orig_unit - target_item["descuento_monto"])

                elif disc_mode == "cart":
                    tot_val = sum(float(i.get("precio_original", i["precio_venta"])) * i["cantidad"] for i in self.cart)
                    if tot_val > 0:
                        for item in self.cart:
                            orig_unit = float(item.get("precio_original", item["precio_venta"]))
                            if disc_type == "porcentaje":
                                disc_unit = orig_unit * (val / 100.0)
                            else:
                                item_val = orig_unit * item["cantidad"]
                                disc_unit = ((item_val / tot_val) * val) / item["cantidad"]
                            
                            item["descuento_monto"] = min(orig_unit, disc_unit)
                            item["precio_venta"] = max(0.0, orig_unit - item["descuento_monto"])

                self.render_cart()
                top.destroy()
            except ValueError:
                pass

        ent_disc.bind("<Return>", lambda e: apply_disc())

        btn_apply = ctk.CTkButton(
            top, text="✔ APLICAR DESCUENTO", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED", height=45, width=300, corner_radius=8,
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
        headers = ["Cód. Barras", "Nombre Producto", "Departamento", "Sub-Depto", "P. Costo", "P. Venta", "Stock", "Estado", "Acciones"]
        cols_w = [110, 170, 130, 130, 80, 80, 50, 90, 80]

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

            dep_tag = p.get('departamento_nombre') or p.get('categoria_nombre') or 'General'
            subdep_tag = p.get('subdepartamento_nombre') or 'General'

            values = [
                p['codigo_barras'], p['nombre'], dep_tag, subdep_tag,
                f"RD${p['precio_costo']:.2f}", f"RD${p['precio_venta']:.2f}",
                str(stock)
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
        dialog.geometry("480x640")
        dialog.grab_set()

        lbl_t = ctk.CTkLabel(dialog, text="FORMULARIO DE PRODUCTO", font=ctk.CTkFont(size=16, weight="bold"), text_color="#EC4899")
        lbl_t.pack(pady=(15, 8))

        ent_code = ctk.CTkEntry(dialog, placeholder_text="Código de Barras", width=340)
        ent_code.pack(pady=4)
        if prod: ent_code.insert(0, prod["codigo_barras"])

        ent_name = ctk.CTkEntry(dialog, placeholder_text="Nombre del Producto", width=340)
        ent_name.pack(pady=4)
        if prod: ent_name.insert(0, prod["nombre"])

        # Fetch Departments & Subdepartments
        departments = DepartmentModel.get_all()
        if not departments:
            departments = ProductModel.get_categories()

        dep_names = [d["nombre"] for d in departments]
        dep_map = {d["nombre"]: d["id"] for d in departments}

        all_subdeps = SubDepartmentModel.get_all()

        lbl_dep = ctk.CTkLabel(dialog, text="Departamento / Categoría:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8", anchor="w")
        lbl_dep.pack(anchor="w", padx=70, pady=(6, 0))

        cmb_dep = ctk.CTkComboBox(dialog, values=dep_names, width=340, command=lambda sel: update_subdeps(sel))
        cmb_dep.pack(pady=(2, 4))

        lbl_subdep = ctk.CTkLabel(dialog, text="Sub-Departamento:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8", anchor="w")
        lbl_subdep.pack(anchor="w", padx=70, pady=(4, 0))

        cmb_subdep = ctk.CTkComboBox(dialog, values=[], width=340)
        cmb_subdep.pack(pady=(2, 4))

        subdep_map = {}

        def update_subdeps(selected_dep_name):
            nonlocal subdep_map
            dep_id = dep_map.get(selected_dep_name)
            filtered = [sd for sd in all_subdeps if sd.get("departamento_id") == dep_id] if dep_id else all_subdeps
            if not filtered:
                filtered = all_subdeps
            
            subdep_names = [sd["nombre"] for sd in filtered]
            subdep_map = {sd["nombre"]: sd["id"] for sd in filtered}
            
            cmb_subdep.configure(values=subdep_names if subdep_names else ["General"])
            if subdep_names:
                cmb_subdep.set(subdep_names[0])
            else:
                cmb_subdep.set("General")

        initial_dep = dep_names[0] if dep_names else "General"
        if prod and prod.get("departamento_nombre") in dep_names:
            initial_dep = prod["departamento_nombre"]
        
        cmb_dep.set(initial_dep)
        update_subdeps(initial_dep)

        if prod and prod.get("subdepartamento_nombre") in subdep_map:
            cmb_subdep.set(prod["subdepartamento_nombre"])

        ent_cost = ctk.CTkEntry(dialog, placeholder_text="Precio Costo (RD$)", width=340)
        ent_cost.pack(pady=4)
        if prod: ent_cost.insert(0, str(prod["precio_costo"]))

        ent_price = ctk.CTkEntry(dialog, placeholder_text="Precio Venta (RD$)", width=340)
        ent_price.pack(pady=4)
        if prod: ent_price.insert(0, str(prod["precio_venta"]))

        ent_stock = ctk.CTkEntry(dialog, placeholder_text="Stock Actual", width=340)
        ent_stock.pack(pady=4)
        if prod: ent_stock.insert(0, str(prod["stock_actual"]))

        ent_min = ctk.CTkEntry(dialog, placeholder_text="Stock Mínimo Alerta", width=340)
        ent_min.pack(pady=4)
        if prod: ent_min.insert(0, str(prod["stock_minimo"]))

        def save():
            try:
                sel_dep = cmb_dep.get()
                sel_subdep = cmb_subdep.get()

                dep_id = dep_map.get(sel_dep, 1)
                subdep_id = subdep_map.get(sel_subdep)

                if not subdep_id and all_subdeps:
                    matching = [sd for sd in all_subdeps if sd.get("departamento_id") == dep_id]
                    if matching:
                        subdep_id = matching[0]["id"]
                    else:
                        subdep_id = 1

                data = {
                    "codigo_barras": ent_code.get().strip(),
                    "nombre": ent_name.get().strip(),
                    "categoria_id": dep_id,
                    "subdepartamento_id": subdep_id,
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

        btn_save = ctk.CTkButton(dialog, text="Guardar Producto", fg_color="#10B981", hover_color="#059669", width=340, height=42, command=save)
        btn_save.pack(pady=15)

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

        # --- State ---
        self._report_period = "Hoy"
        self._report_type = "General Consolidado"
        self._report_start_date = ""
        self._report_end_date = ""

        outer = ctk.CTkFrame(self.content_area, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=16, pady=10)

        # ── HEADER TITLE
        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(hdr, text="📊 MÓDULO DE REPORTES & ANALÍTICA",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#8B5CF6").pack(side="left")

        # ── PERIOD FILTER BAR
        period_bar = ctk.CTkFrame(outer, fg_color="#1E293B", corner_radius=8, height=46)
        period_bar.pack(fill="x", pady=(0, 8))
        period_bar.pack_propagate(False)

        ctk.CTkLabel(period_bar, text=" 📅 Período:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(10, 4))

        self._period_btns = {}
        period_options = ["Hoy", "Esta Semana", "Este Mes", "Este Año", "Personalizado"]
        for p in period_options:
            btn = ctk.CTkButton(
                period_bar, text=p, width=100, height=30,
                fg_color="#3B82F6" if p == "Hoy" else "#334155",
                hover_color="#2563EB",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda opt=p: self._select_report_period(opt)
            )
            btn.pack(side="left", padx=4, pady=6)
            self._period_btns[p] = btn

        # Custom date range (hidden by default)
        self._custom_date_frame = ctk.CTkFrame(period_bar, fg_color="transparent")
        ctk.CTkLabel(self._custom_date_frame, text="Desde:",
            font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(8, 2))
        self._ent_start = ctk.CTkEntry(self._custom_date_frame, placeholder_text="YYYY-MM-DD", width=110)
        self._ent_start.pack(side="left", padx=2)
        ctk.CTkLabel(self._custom_date_frame, text="Hasta:",
            font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(8, 2))
        self._ent_end = ctk.CTkEntry(self._custom_date_frame, placeholder_text="YYYY-MM-DD", width=110)
        self._ent_end.pack(side="left", padx=2)
        btn_apply = ctk.CTkButton(
            self._custom_date_frame, text="Aplicar", width=70, height=28,
            fg_color="#10B981", hover_color="#059669",
            command=self._apply_custom_date
        )
        btn_apply.pack(side="left", padx=6)

        # ── REPORT TYPE SELECTOR + ACTIONS
        ctrl_bar = ctk.CTkFrame(outer, fg_color="#1E293B", corner_radius=8, height=46)
        ctrl_bar.pack(fill="x", pady=(0, 8))
        ctrl_bar.pack_propagate(False)

        ctk.CTkLabel(ctrl_bar, text=" 📋 Tipo de Reporte:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(10, 4))

        report_types = [
            "General Consolidado",
            "Por Departamentos y Sub-departamentos",
            "Store Multi-Total (Métodos y Cajeros)",
            "Valoración de Inventario",
            "Diario Electrónico (Electronic Journal)"
        ]
        self._cmb_report_type = ctk.CTkComboBox(
            ctrl_bar, values=report_types, width=310, height=30,
            font=ctk.CTkFont(size=11),
            command=lambda v: self._select_report_type(v)
        )
        self._cmb_report_type.set("General Consolidado")
        self._cmb_report_type.pack(side="left", padx=6, pady=8)

        # Action Buttons
        ctk.CTkButton(
            ctrl_bar, text="🔄 Generar", width=90, height=30,
            fg_color="#7C3AED", hover_color="#6D28D9",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._render_report_content
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            ctrl_bar, text="👁️ Vista PDF", width=100, height=30,
            fg_color="#0F766E", hover_color="#0D6B63",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._open_pdf_preview
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            ctrl_bar, text="📄 Exportar PDF", width=110, height=30,
            fg_color="#DC2626", hover_color="#B91C1C",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._export_pdf_direct
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            ctrl_bar, text="📊 Exportar Excel", width=120, height=30,
            fg_color="#15803D", hover_color="#166534",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_sales_excel
        ).pack(side="left", padx=4)

        # ── MAIN SPLIT AREA: top = report content | bottom = historial reciente
        split_frame = ctk.CTkFrame(outer, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)

        # Top: Report content (scrollable)
        self._report_content_frame = ctk.CTkScrollableFrame(split_frame, fg_color="#0F172A", corner_radius=8, height=280)
        self._report_content_frame.pack(fill="both", expand=True, pady=(0, 6))

        # Bottom: Historial Reciente de Facturas (always visible)
        hist_outer = ctk.CTkFrame(split_frame, fg_color="#16161F", corner_radius=8,
            border_width=1, border_color="#1E293B", height=220)
        hist_outer.pack(fill="x", pady=(0, 4))
        hist_outer.pack_propagate(False)

        hist_hdr = ctk.CTkFrame(hist_outer, fg_color="#1E293B", corner_radius=0, height=30)
        hist_hdr.pack(fill="x")
        hist_hdr.pack_propagate(False)
        ctk.CTkLabel(hist_hdr, text="  🧾 HISTORIAL RECIENTE DE FACTURAS",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#8B5CF6").pack(side="left", pady=5)
        ctk.CTkLabel(hist_hdr, text="Últimas 20 transacciones del día",
            font=ctk.CTkFont(size=10), text_color="#475569").pack(side="left", padx=8, pady=5)

        # Table header
        headers = ["Factura #", "Fecha & Hora", "Cliente", "Tipo Pago", "Subtotal", "ITBIS", "Total (RD$)"]
        cols_w  = [145,          155,            120,       105,         90,          80,      95]

        hist_head = ctk.CTkFrame(hist_outer, fg_color="#1F2937", height=26)
        hist_head.pack(fill="x", padx=6, pady=(4, 0))
        hist_head.pack_propagate(False)
        for h, w in zip(headers, cols_w):
            ctk.CTkLabel(hist_head, text=h, font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#93C5FD", width=w).pack(side="left", padx=2)

        # Scrollable rows
        hist_scroll = ctk.CTkScrollableFrame(hist_outer, fg_color="transparent", height=152)
        hist_scroll.pack(fill="both", expand=True, padx=6, pady=2)

        today = datetime.date.today()
        s_dt = f"{today} 00:00:00"
        e_dt = f"{today} 23:59:59"
        recent_sales = ReportModel.get_electronic_journal(s_dt, e_dt)

        if not recent_sales:
            ctk.CTkLabel(hist_scroll, text="No hay facturas registradas hoy.",
                text_color="#475569", font=ctk.CTkFont(size=11)).pack(pady=12)
        else:
            for i, s in enumerate(recent_sales[:20]):
                bg = "#111827" if i % 2 == 0 else "#0F172A"
                row = ctk.CTkFrame(hist_scroll, fg_color=bg, corner_radius=3, height=24)
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)
                vals = [
                    s.get("codigo_factura", ""),
                    str(s.get("fecha", ""))[:19],
                    s.get("cliente_nombre", "General"),
                    s.get("tipo_pago", ""),
                    f"RD${float(s.get('subtotal', 0)):,.2f}",
                    f"RD${float(s.get('itbis_impuesto', 0)):,.2f}",
                    f"RD${float(s.get('total', 0)):,.2f}",
                ]
                for val, w in zip(vals, cols_w):
                    ctk.CTkLabel(row, text=str(val), font=ctk.CTkFont(size=10),
                        text_color="#CBD5E1", width=w).pack(side="left", padx=2)

        # Auto-render default report in top area
        self._render_report_content()


    def _select_report_period(self, period):
        self._report_period = period
        for p, btn in self._period_btns.items():
            btn.configure(fg_color="#3B82F6" if p == period else "#334155")
        if period == "Personalizado":
            self._custom_date_frame.pack(side="left", padx=4)
        else:
            self._custom_date_frame.pack_forget()
            self._render_report_content()

    def _apply_custom_date(self):
        self._report_start_date = self._ent_start.get().strip()
        self._report_end_date = self._ent_end.get().strip()
        self._render_report_content()

    def _select_report_type(self, val):
        self._report_type = val
        self._render_report_content()

    def _get_period_label(self):
        p = self._report_period
        if p == "Personalizado":
            return f"Del {self._report_start_date} al {self._report_end_date}"
        return p

    def _render_report_content(self):
        # Clear existing content
        for w in self._report_content_frame.winfo_children():
            w.destroy()

        start_dt, end_dt = ReportModel.get_date_range_bounds(
            self._report_period,
            self._report_start_date,
            self._report_end_date
        )

        period_lbl = self._get_period_label()
        rtype = self._report_type

        # Period + Type header inside content
        meta_row = ctk.CTkFrame(self._report_content_frame, fg_color="transparent")
        meta_row.pack(fill="x", pady=(10, 8), padx=12)
        ctk.CTkLabel(meta_row,
            text=f"Reporte: {rtype}  |  Período: {period_lbl}  |  Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=ctk.CTkFont(size=11), text_color="#64748B"
        ).pack(side="left")

        if rtype == "General Consolidado":
            self._render_general_report(start_dt, end_dt)
        elif rtype == "Por Departamentos y Sub-departamentos":
            self._render_depto_report(start_dt, end_dt)
        elif rtype == "Store Multi-Total (Métodos y Cajeros)":
            self._render_multitotal_report(start_dt, end_dt)
        elif rtype == "Valoración de Inventario":
            self._render_inventory_valuation()
        elif rtype == "Diario Electrónico (Electronic Journal)":
            self._render_electronic_journal(start_dt, end_dt)

    def _make_summary_card(self, parent, title, value, color, icon=""):
        card = ctk.CTkFrame(parent, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        card.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkLabel(card, text=f"{icon} {title}",
            font=ctk.CTkFont(size=10, weight="bold"), text_color="#94A3B8").pack(pady=(10, 2))
        ctk.CTkLabel(card, text=value,
            font=ctk.CTkFont(size=18, weight="bold"), text_color=color).pack(pady=(0, 10))

    def _make_table_header(self, parent, headers, widths):
        hrow = ctk.CTkFrame(parent, fg_color="#1E3A5F", corner_radius=6, height=32)
        hrow.pack(fill="x", padx=8, pady=(0, 2))
        hrow.pack_propagate(False)
        for h, w in zip(headers, widths):
            ctk.CTkLabel(hrow, text=h, font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#E2E8F0", width=w).pack(side="left", padx=3)

    def _make_table_row(self, parent, vals, widths, alt=False):
        bg = "#111827" if alt else "#0F172A"
        row = ctk.CTkFrame(parent, fg_color=bg, corner_radius=4, height=28)
        row.pack(fill="x", padx=8, pady=1)
        row.pack_propagate(False)
        for v, w in zip(vals, widths):
            ctk.CTkLabel(row, text=str(v), font=ctk.CTkFont(size=10),
                text_color="#CBD5E1", width=w).pack(side="left", padx=3)
        return row

    # --- RENDER: General Consolidado ---
    def _render_general_report(self, start_dt, end_dt):
        data = ReportModel.get_executive_summary(start_dt, end_dt)

        cards = ctk.CTkFrame(self._report_content_frame, fg_color="transparent")
        cards.pack(fill="x", padx=12, pady=8)

        self._make_summary_card(cards, "Transacciones",
            str(data.get("total_transacciones", 0)), "#EC4899", "🧾")
        self._make_summary_card(cards, "Ingresos Brutos RD$",
            f"RD$ {float(data.get('total_ingresos', 0)):,.2f}", "#10B981", "💰")
        self._make_summary_card(cards, "ITBIS Recaudado",
            f"RD$ {float(data.get('total_itbis', 0)):,.2f}", "#F59E0B", "📑")
        self._make_summary_card(cards, "Ganancia Est.",
            f"RD$ {float(data.get('ganancia_estimada', 0)):,.2f}", "#8B5CF6", "📈")

        cards2 = ctk.CTkFrame(self._report_content_frame, fg_color="transparent")
        cards2.pack(fill="x", padx=12, pady=4)
        self._make_summary_card(cards2, "Subtotal (sin ITBIS)",
            f"RD$ {float(data.get('total_subtotal', 0)):,.2f}", "#38BDF8", "🏷️")
        self._make_summary_card(cards2, "Costo Estimado",
            f"RD$ {float(data.get('costo_total_estimado', 0)):,.2f}", "#FB7185", "📦")
        self._make_summary_card(cards2, "Ticket Promedio",
            f"RD$ {float(data.get('ticket_promedio', 0)):,.2f}", "#A3E635", "🎫")

        # Also show recent sales history table
        ctk.CTkLabel(self._report_content_frame, text="  📄 HISTORIAL DE FACTURAS DEL PERÍODO",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8",
            anchor="w").pack(fill="x", padx=12, pady=(14, 4))

        hdrs = ["Factura #", "Fecha & Hora", "Cliente", "Tipo Pago", "Subtotal", "ITBIS", "Total RD$"]
        wdts = [145, 145, 120, 100, 90, 80, 95]
        self._make_table_header(self._report_content_frame, hdrs, wdts)

        sales = ReportModel.get_electronic_journal(start_dt, end_dt)
        for i, s in enumerate(sales[:100]):
            self._make_table_row(self._report_content_frame, [
                s.get("codigo_factura", ""), str(s.get("fecha", ""))[:19],
                s.get("cliente_nombre", "General"), s.get("tipo_pago", ""),
                f"RD${float(s.get('subtotal',0)):,.2f}",
                f"RD${float(s.get('itbis_impuesto',0)):,.2f}",
                f"RD${float(s.get('total',0)):,.2f}"
            ], wdts, alt=i%2==0)

    # --- RENDER: Departamentos y Sub-departamentos ---
    def _render_depto_report(self, start_dt, end_dt):
        rows = ReportModel.get_department_subdepartment_sales(start_dt, end_dt)

        ctk.CTkLabel(self._report_content_frame, text="  🏬 VENTAS POR DEPARTAMENTO Y SUB-DEPARTAMENTO",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8",
            anchor="w").pack(fill="x", padx=12, pady=(12, 4))

        hdrs = ["Departamento", "Sub-Departamento", "Unidades", "Subtotal RD$", "ITBIS Est.", "Total Neto", "Ganancia Est."]
        wdts = [130, 140, 70, 110, 95, 105, 105]
        self._make_table_header(self._report_content_frame, hdrs, wdts)

        if not rows:
            ctk.CTkLabel(self._report_content_frame,
                text="No hay datos de ventas por departamento en este período.",
                text_color="#64748B").pack(pady=20)
            return

        total_neto = 0
        for i, r in enumerate(rows):
            total_neto += float(r.get("total_neto") or 0)
            self._make_table_row(self._report_content_frame, [
                r.get("departamento", ""),
                r.get("subdepartamento", ""),
                r.get("unidades_vendidas", 0),
                f"RD${float(r.get('total_bruto') or 0):,.2f}",
                f"RD${float(r.get('itbis_estimado') or 0):,.2f}",
                f"RD${float(r.get('total_neto') or 0):,.2f}",
                f"RD${float(r.get('ganancia_estimada') or 0):,.2f}"
            ], wdts, alt=i%2==0)

        # Total footer
        foot = ctk.CTkFrame(self._report_content_frame, fg_color="#1E3A5F", corner_radius=4, height=30)
        foot.pack(fill="x", padx=8, pady=4)
        foot.pack_propagate(False)
        ctk.CTkLabel(foot, text=f"  TOTAL NETO PERÍODO:   RD$ {total_neto:,.2f}",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#10B981").pack(side="left", padx=6)

    # --- RENDER: Store Multi-Total ---
    def _render_multitotal_report(self, start_dt, end_dt):
        data = ReportModel.get_multi_total_store_report(start_dt, end_dt)
        by_pay = data.get("by_payment", [])
        by_usr = data.get("by_user", [])

        ctk.CTkLabel(self._report_content_frame, text="  💳 TOTALES POR MÉTODO DE PAGO",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8",
            anchor="w").pack(fill="x", padx=12, pady=(12, 4))

        hdrs_p = ["Método de Pago", "Operaciones", "Subtotal RD$", "ITBIS RD$", "Total Monto RD$"]
        wdts_p = [160, 100, 130, 110, 150]
        self._make_table_header(self._report_content_frame, hdrs_p, wdts_p)
        for i, r in enumerate(by_pay):
            self._make_table_row(self._report_content_frame, [
                r.get("tipo_pago", "Efectivo"),
                r.get("total_operaciones", 0),
                f"RD${float(r.get('subtotal') or 0):,.2f}",
                f"RD${float(r.get('itbis') or 0):,.2f}",
                f"RD${float(r.get('total_monto') or 0):,.2f}"
            ], wdts_p, alt=i%2==0)

        ctk.CTkLabel(self._report_content_frame, text="  👤 RENDIMIENTO POR CAJERO / USUARIO",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#A78BFA",
            anchor="w").pack(fill="x", padx=12, pady=(16, 4))

        hdrs_u = ["Cajero / Usuario", "Facturas Emitidas", "Total Generado RD$"]
        wdts_u = [220, 160, 220]
        self._make_table_header(self._report_content_frame, hdrs_u, wdts_u)
        for i, r in enumerate(by_usr):
            self._make_table_row(self._report_content_frame, [
                r.get("cajero", "General"),
                r.get("total_ventas", 0),
                f"RD${float(r.get('total_monto') or 0):,.2f}"
            ], wdts_u, alt=i%2==0)

    # --- RENDER: Valoración de Inventario ---
    def _render_inventory_valuation(self):
        data = ReportModel.get_inventory_valuation_report()
        summary = data.get("summary") or {}
        details = data.get("details") or []

        cards = ctk.CTkFrame(self._report_content_frame, fg_color="transparent")
        cards.pack(fill="x", padx=12, pady=8)
        self._make_summary_card(cards, "Total Productos",
            str(summary.get("total_productos", 0)), "#38BDF8", "📦")
        self._make_summary_card(cards, "Valor Costo RD$",
            f"RD$ {float(summary.get('valor_costo_total') or 0):,.2f}", "#94A3B8", "💵")
        self._make_summary_card(cards, "Valor Venta RD$",
            f"RD$ {float(summary.get('valor_venta_total') or 0):,.2f}", "#10B981", "💰")
        self._make_summary_card(cards, "Ganancia Potencial",
            f"RD$ {float(summary.get('ganancia_potencial') or 0):,.2f}", "#8B5CF6", "📈")

        cards2 = ctk.CTkFrame(self._report_content_frame, fg_color="transparent")
        cards2.pack(fill="x", padx=12, pady=4)
        self._make_summary_card(cards2, "Agotados",
            str(summary.get("cant_agotados", 0)), "#EF4444", "🚫")
        self._make_summary_card(cards2, "Stock Bajo",
            str(summary.get("cant_stock_bajo", 0)), "#F59E0B", "⚠️")

        ctk.CTkLabel(self._report_content_frame, text="  📦 DETALLE DE VALORACIÓN DE INVENTARIO",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8",
            anchor="w").pack(fill="x", padx=12, pady=(14, 4))

        hdrs = ["Código", "Producto", "Sub-Depto", "Stock", "P. Costo", "P. Venta", "Valor Venta RD$"]
        wdts = [90, 160, 110, 55, 85, 85, 110]
        self._make_table_header(self._report_content_frame, hdrs, wdts)
        for i, p in enumerate(details):
            stk = int(p.get("stock_actual") or 0)
            stk_min = int(p.get("stock_minimo") or 0)
            color_override = None
            if stk <= 0:
                color_override = "#EF4444"
            elif stk <= stk_min:
                color_override = "#F59E0B"
            row = self._make_table_row(self._report_content_frame, [
                p.get("codigo_barras", ""),
                p.get("nombre", ""),
                p.get("subdepartamento", ""),
                stk,
                f"RD${float(p.get('precio_costo') or 0):,.2f}",
                f"RD${float(p.get('precio_venta') or 0):,.2f}",
                f"RD${float(p.get('valor_venta') or 0):,.2f}"
            ], wdts, alt=i%2==0)

    # --- RENDER: Electronic Journal ---
    def _render_electronic_journal(self, start_dt, end_dt):
        ventas = ReportModel.get_electronic_journal(start_dt, end_dt)

        ctk.CTkLabel(self._report_content_frame,
            text=f"  📖 DIARIO ELECTRÓNICO (ELECTRONIC JOURNAL)  —  {len(ventas)} transacciones",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#34D399",
            anchor="w").pack(fill="x", padx=12, pady=(12, 6))

        if not ventas:
            ctk.CTkLabel(self._report_content_frame,
                text="No hay transacciones registradas en este período.",
                text_color="#64748B", font=ctk.CTkFont(size=12)).pack(pady=30)
            return

        for v in ventas:
            # Transaction header card
            vcard = ctk.CTkFrame(self._report_content_frame, fg_color="#1E293B",
                corner_radius=8, border_width=1, border_color="#334155")
            vcard.pack(fill="x", padx=8, pady=5)

            top_row = ctk.CTkFrame(vcard, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(8, 4))

            ctk.CTkLabel(top_row,
                text=f"🧾 {v.get('codigo_factura', '')}",
                font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8"
            ).pack(side="left", padx=(0, 16))
            ctk.CTkLabel(top_row,
                text=str(v.get("fecha", ""))[:19],
                font=ctk.CTkFont(size=11), text_color="#94A3B8"
            ).pack(side="left", padx=8)
            ctk.CTkLabel(top_row,
                text=f"👤 {v.get('cajero_nombre', 'General')}",
                font=ctk.CTkFont(size=11), text_color="#CBD5E1"
            ).pack(side="left", padx=8)
            ctk.CTkLabel(top_row,
                text=f"💳 {v.get('tipo_pago', 'Efectivo')}",
                font=ctk.CTkFont(size=11), text_color="#A3E635"
            ).pack(side="left", padx=8)
            ctk.CTkLabel(top_row,
                text=f"  TOTAL: RD$ {float(v.get('total', 0)):,.2f}",
                font=ctk.CTkFont(size=12, weight="bold"), text_color="#10B981"
            ).pack(side="right", padx=10)

            # Line Items sub-table
            items = v.get("items", [])
            if items:
                item_frame = ctk.CTkFrame(vcard, fg_color="#0F172A", corner_radius=4)
                item_frame.pack(fill="x", padx=10, pady=(2, 8))

                # Item header
                ihead = ctk.CTkFrame(item_frame, fg_color="#1E3A5F", height=24, corner_radius=4)
                ihead.pack(fill="x", padx=4, pady=(4, 2))
                ihead.pack_propagate(False)
                for col, w in zip(["Código", "Artículo", "Sub-Depto", "Cant.", "Precio Unit.", "Descuento", "Subtotal"],
                                  [80, 190, 120, 50, 90, 85, 90]):
                    ctk.CTkLabel(ihead, text=col, font=ctk.CTkFont(size=9, weight="bold"),
                        text_color="#93C5FD", width=w).pack(side="left", padx=2)

                for j, it in enumerate(items):
                    irow_bg = "#111827" if j%2==0 else "#0F172A"
                    irow = ctk.CTkFrame(item_frame, fg_color=irow_bg, height=24, corner_radius=3)
                    irow.pack(fill="x", padx=4, pady=1)
                    irow.pack_propagate(False)
                    disc = float(it.get("descuento") or 0)
                    disc_str = f"- RD${disc:,.2f}" if disc > 0 else "—"
                    for val, w in zip([
                        it.get("codigo_barras", ""),
                        it.get("producto_nombre", ""),
                        it.get("subdepartamento_nombre", ""),
                        it.get("cantidad", 1),
                        f"RD${float(it.get('precio_unitario') or 0):,.2f}",
                        disc_str,
                        f"RD${float(it.get('subtotal') or 0):,.2f}"
                    ], [80, 190, 120, 50, 90, 85, 90]):
                        ctk.CTkLabel(irow, text=str(val), font=ctk.CTkFont(size=9),
                            text_color="#CBD5E1", width=w).pack(side="left", padx=2)

    # --- PDF Preview Modal ---
    def _open_pdf_preview(self):
        start_dt, end_dt = ReportModel.get_date_range_bounds(
            self._report_period, self._report_start_date, self._report_end_date)
        rtype = self._report_type
        period_lbl = self._get_period_label()
        data = self._get_report_data_for_pdf(rtype, start_dt, end_dt)

        os.makedirs("reportes", exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join("reportes", f"reporte_{ts}.pdf")
        try:
            generate_pdf_report(rtype, data, period_lbl, pdf_path)
            ReportPreviewModal(self, pdf_path)
        except Exception as e:
            messagebox.showerror("Error PDF", f"No se pudo generar el PDF:\n{e}")

    def _export_pdf_direct(self):
        start_dt, end_dt = ReportModel.get_date_range_bounds(
            self._report_period, self._report_start_date, self._report_end_date)
        rtype = self._report_type
        period_lbl = self._get_period_label()
        data = self._get_report_data_for_pdf(rtype, start_dt, end_dt)

        default_name = f"reporte_{self._report_period}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            try:
                generate_pdf_report(rtype, data, period_lbl, file_path)
                messagebox.showinfo("PDF Exportado", f"Reporte guardado en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error PDF", f"No se pudo exportar:\n{e}")

    def _get_report_data_for_pdf(self, rtype, start_dt, end_dt):
        if rtype == "General Consolidado":
            return ReportModel.get_executive_summary(start_dt, end_dt)
        elif rtype == "Por Departamentos y Sub-departamentos":
            return ReportModel.get_department_subdepartment_sales(start_dt, end_dt)
        elif rtype == "Store Multi-Total (Métodos y Cajeros)":
            return ReportModel.get_multi_total_store_report(start_dt, end_dt)
        elif rtype == "Valoración de Inventario":
            return ReportModel.get_inventory_valuation_report()
        elif rtype == "Diario Electrónico (Electronic Journal)":
            return ReportModel.get_electronic_journal(start_dt, end_dt)
        return {}

    def export_sales_excel(self):
        start_dt, end_dt = ReportModel.get_date_range_bounds(
            self._report_period,
            getattr(self, '_report_start_date', ''),
            getattr(self, '_report_end_date', '')
        )
        ventas = ReportModel.get_electronic_journal(start_dt, end_dt)
        # Convert EJ data to simple list for excel exporter
        sales_flat = []
        for v in ventas:
            for it in v.get("items", []):
                sales_flat.append({
                    "codigo_factura": v.get("codigo_factura", ""),
                    "fecha": str(v.get("fecha", ""))[:19],
                    "cajero": v.get("cajero_nombre", "General"),
                    "tipo_pago": v.get("tipo_pago", ""),
                    "cliente_nombre": v.get("cliente_nombre", "General"),
                    "producto": it.get("producto_nombre", ""),
                    "cantidad": it.get("cantidad", 1),
                    "precio_unitario": it.get("precio_unitario", 0),
                    "subtotal": it.get("subtotal", 0),
                    "total_factura": v.get("total", 0),
                })
        if not sales_flat:
            sales_flat = ventas  # fallback
        default_name = f"reporte_{self._report_period}_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            try:
                export_sales_to_excel(sales_flat, file_path)
                messagebox.showinfo("Exportación Exitosa", f"Reporte exportado a Excel:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error Excel", f"No se pudo exportar:\n{e}")


class ReportPreviewModal(ctk.CTkToplevel):
    """Modal window for PDF preview and printing."""
    def __init__(self, parent, pdf_path):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.title("👁️ Vista Previa del Reporte PDF")
        self.geometry("860x640")
        self.configure(fg_color="#0F172A")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 860) // 2
        y = (self.winfo_screenheight() - 640) // 2
        self.geometry(f"860x640+{max(0,x)}+{max(0,y)}")
        self.grab_set()

        # Header
        hdr = ctk.CTkFrame(self, height=52, fg_color="#1E293B", corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="  👁️ VISTA PREVIA DEL REPORTE PDF",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#F8FAFC").pack(side="left", pady=10)
        ctk.CTkButton(hdr, text="🖨️ Imprimir", width=110, height=34,
            fg_color="#2563EB", hover_color="#1D4ED8",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._print_pdf).pack(side="right", padx=8, pady=8)
        ctk.CTkButton(hdr, text="💾 Guardar PDF", width=120, height=34,
            fg_color="#DC2626", hover_color="#B91C1C",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._save_pdf).pack(side="right", padx=4, pady=8)
        ctk.CTkButton(hdr, text="✕ Cerrar", width=80, height=34,
            fg_color="#475569", hover_color="#334155",
            command=self.destroy).pack(side="right", padx=4, pady=8)

        # PDF path label
        path_bar = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0, height=28)
        path_bar.pack(fill="x")
        path_bar.pack_propagate(False)
        ctk.CTkLabel(path_bar, text=f"  📂 {os.path.abspath(pdf_path)}",
            font=ctk.CTkFont(size=9), text_color="#64748B").pack(side="left", pady=4)

        # Content area
        self._content_area = ctk.CTkScrollableFrame(self, fg_color="#1E293B", corner_radius=0)
        self._content_area.pack(fill="both", expand=True, padx=4, pady=4)

        self._try_render_pages()

    def _try_render_pages(self):
        """Try to render PDF pages as images using pdf2image or pymupdf; fallback to text info."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(self.pdf_path)
            for page_num in range(min(len(doc), 10)):
                page = doc[page_num]
                mat = fitz.Matrix(1.6, 1.6)  # zoom 1.6x
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("ppm")
                from PIL import Image as PILImage
                import io
                img = PILImage.open(io.BytesIO(img_data))
                self._embed_page_image(img, page_num + 1, len(doc))
            doc.close()
        except ImportError:
            self._show_pdf_text_fallback()
        except Exception as e:
            self._show_pdf_text_fallback(str(e))

    def _embed_page_image(self, pil_img, page_num, total_pages):
        from PIL import ImageTk
        frame = ctk.CTkFrame(self._content_area, fg_color="white",
            corner_radius=4, border_width=1, border_color="#CBD5E1")
        frame.pack(pady=8, padx=12)
        ctk.CTkLabel(frame, text=f"Página {page_num} de {total_pages}",
            font=ctk.CTkFont(size=9), text_color="#64748B", fg_color="#F1F5F9").pack(fill="x")
        tk_img = ImageTk.PhotoImage(pil_img)
        lbl = tk.Label(frame, image=tk_img, bg="white")
        lbl.image = tk_img
        lbl.pack()

    def _show_pdf_text_fallback(self, err=""):
        ctk.CTkLabel(self._content_area,
            text="📄 El PDF fue generado exitosamente.",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#10B981").pack(pady=30)
        ctk.CTkLabel(self._content_area,
            text=f"Archivo: {os.path.abspath(self.pdf_path)}",
            font=ctk.CTkFont(size=11), text_color="#94A3B8").pack()
        ctk.CTkLabel(self._content_area,
            text="Para ver la vista previa completa instale pymupdf:\npip install pymupdf",
            font=ctk.CTkFont(size=10), text_color="#64748B").pack(pady=8)
        if err:
            ctk.CTkLabel(self._content_area, text=f"Detalle: {err}",
                font=ctk.CTkFont(size=9), text_color="#475569").pack()
        ctk.CTkButton(self._content_area, text="📂 Abrir PDF Externamente",
            fg_color="#2563EB", hover_color="#1D4ED8",
            command=lambda: os.startfile(self.pdf_path)).pack(pady=12)

    def _print_pdf(self):
        success = print_pdf_file(self.pdf_path)
        if success:
            messagebox.showinfo("Imprimir", "El reporte fue enviado a la impresora.")
        else:
            messagebox.showerror("Error", "No se pudo enviar a la impresora.")

    def _save_pdf(self):
        dest = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=os.path.basename(self.pdf_path)
        )
        if dest:
            import shutil
            shutil.copy2(self.pdf_path, dest)
            messagebox.showinfo("Guardado", f"PDF guardado en:\n{dest}")

class FlipChartModal(ctk.CTkToplevel):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

        self.title("📋 Flip Chart - Catálogo Visual por Sub-Departamentos")
        self.geometry("1000x680")
        self.configure(fg_color="#0F172A")
        
        # Center modal on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1000) // 2
        y = (self.winfo_screenheight() - 680) // 2
        self.geometry(f"1000x680+{max(0, x)}+{max(0, y)}")
        self.grab_set()

        self.selected_subdep_id = None

        # --- Top Header ---
        header = ctk.CTkFrame(self, height=60, fg_color="#1E293B", corner_radius=0)
        header.pack(side="top", fill="x")

        lbl_title = ctk.CTkLabel(
            header, text="  📋 FLIP CHART - CATÁLOGO VISUAL DE ARTÍCULOS", 
            font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
            text_color="#F8FAFC"
        )
        lbl_title.pack(side="left", padx=15, pady=12)

        lbl_subtitle = ctk.CTkLabel(
            header, text="Seleccione un sub-departamento para explorar artículos y agregarlos al carrito.",
            font=ctk.CTkFont(size=11), text_color="#94A3B8"
        )
        lbl_subtitle.pack(side="left", padx=10, pady=12)

        btn_close = ctk.CTkButton(
            header, text=" ✕ Cerrar ", width=80, height=32,
            fg_color="#DC2626", hover_color="#B91C1C",
            command=self.destroy
        )
        btn_close.pack(side="right", padx=15)

        # --- Notification Banner (Toast) ---
        self.banner_frame = ctk.CTkFrame(self, height=36, fg_color="#059669", corner_radius=0)
        self.banner_lbl = ctk.CTkLabel(
            self.banner_frame, text="", 
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"), 
            text_color="#FFFFFF"
        )
        self.banner_lbl.pack(pady=6)
        self._banner_timer = None

        # --- Main Body Split ---
        self.body_split = ctk.CTkFrame(self, fg_color="transparent")
        self.body_split.pack(side="bottom", fill="both", expand=True, padx=12, pady=12)

        # Left Panel: Sub-departments Sidebar
        self.left_panel = ctk.CTkFrame(self.body_split, width=280, fg_color="#1E293B", corner_radius=8, border_width=1, border_color="#334155")
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))

        lbl_dep_header = ctk.CTkLabel(
            self.left_panel, text=" SUB-DEPARTAMENTOS ", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8"
        )
        lbl_dep_header.pack(fill="x", padx=10, pady=(12, 6))

        self.subdeps_scroll = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.subdeps_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # Right Panel: Products Grid
        self.right_panel = ctk.CTkFrame(self.body_split, fg_color="#1E293B", corner_radius=8, border_width=1, border_color="#334155")
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.lbl_selected_title = ctk.CTkLabel(
            self.right_panel, text="Todos los Artículos Esenciales", 
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), text_color="#F8FAFC"
        )
        self.lbl_selected_title.pack(anchor="w", padx=15, pady=(12, 6))

        self.products_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.products_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Populate
        self.load_subdepartments_list()
        self.load_flip_products()

    def show_toast_banner(self, text):
        if self._banner_timer:
            self.after_cancel(self._banner_timer)
            self._banner_timer = None
        
        self.banner_lbl.configure(text=text)
        self.banner_frame.pack(side="top", fill="x", before=self.body_split)
        self._banner_timer = self.after(2500, self.hide_toast_banner)

    def hide_toast_banner(self):
        if hasattr(self, 'banner_frame'):
            self.banner_frame.pack_forget()
        self._banner_timer = None

    def load_subdepartments_list(self):
        for w in self.subdeps_scroll.winfo_children():
            w.destroy()

        departments = DepartmentModel.get_all()
        subdeps = SubDepartmentModel.get_all()

        # All Products Button
        btn_all = ctk.CTkButton(
            self.subdeps_scroll, text="🌟 Todos los Artículos",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2563EB" if self.selected_subdep_id is None else "#0F172A",
            hover_color="#1D4ED8", height=34, anchor="w", corner_radius=6,
            command=lambda: self.select_subdepartment(None, "Todos los Artículos Esenciales")
        )
        btn_all.pack(fill="x", pady=(0, 8))

        # Group subdeps by dept
        for dep in departments:
            lbl_dep = ctk.CTkLabel(
                self.subdeps_scroll, text=f"📂 {dep['nombre'].upper()}",
                font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8", anchor="w"
            )
            lbl_dep.pack(fill="x", padx=4, pady=(8, 3))

            dept_subdeps = [sd for sd in subdeps if sd['departamento_id'] == dep['id']]
            for sd in dept_subdeps:
                is_sel = self.selected_subdep_id == sd['id']
                btn_sd = ctk.CTkButton(
                    self.subdeps_scroll, 
                    text=f"   • {sd['nombre']}",
                    font=ctk.CTkFont(size=11),
                    fg_color="#8B5CF6" if is_sel else "#1F2937",
                    hover_color="#7C3AED", height=30, anchor="w", corner_radius=6,
                    command=lambda s_id=sd['id'], s_name=sd['nombre']: self.select_subdepartment(s_id, s_name)
                )
                btn_sd.pack(fill="x", pady=2)

    def select_subdepartment(self, subdep_id, name):
        self.selected_subdep_id = subdep_id
        self.lbl_selected_title.configure(text=f"Artículos en: {name}")
        self.load_subdepartments_list()
        self.load_flip_products()

    def load_flip_products(self):
        for w in self.products_scroll.winfo_children():
            w.destroy()

        if self.selected_subdep_id:
            products = ProductModel.get_by_subdepartment(self.selected_subdep_id)
        else:
            products = ProductModel.get_all()

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll, text="No hay artículos registrados en este sub-departamento.", text_color="#94A3B8")
            lbl.pack(pady=30)
            return

        # Grid view with 2 columns
        grid_frame = ctk.CTkFrame(self.products_scroll, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)

        for idx, p in enumerate(products):
            row_idx = idx // 2
            col_idx = idx % 2

            card = ctk.CTkFrame(grid_frame, fg_color="#0F172A", corner_radius=8, border_width=1, border_color="#334155")
            card.grid(row=row_idx, column=col_idx, padx=6, pady=6, sticky="ew")

            # Header inside card
            subdep_tag = p.get('subdepartamento_nombre') or 'General'
            tag_lbl = ctk.CTkLabel(card, text=f"🏷️ {subdep_tag} | Cód: {p['codigo_barras']}", font=ctk.CTkFont(size=9), text_color="#64748B", anchor="w")
            tag_lbl.pack(fill="x", padx=10, pady=(6, 2))

            name_lbl = ctk.CTkLabel(card, text=p['nombre'], font=ctk.CTkFont(size=12, weight="bold"), text_color="#F8FAFC", anchor="w")
            name_lbl.pack(fill="x", padx=10, pady=(0, 4))

            # Bottom price and add button
            bottom_box = ctk.CTkFrame(card, fg_color="transparent")
            bottom_box.pack(fill="x", padx=10, pady=(0, 8))

            price_lbl = ctk.CTkLabel(bottom_box, text=f"RD$ {float(p['precio_venta']):.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#38BDF8")
            price_lbl.pack(side="left")

            stock_color = "#10B981" if p['stock_actual'] > p['stock_minimo'] else "#EF4444"
            stock_lbl = ctk.CTkLabel(bottom_box, text=f" (Stock: {p['stock_actual']}) ", font=ctk.CTkFont(size=10), text_color=stock_color)
            stock_lbl.pack(side="left", padx=4)

            btn_add = ctk.CTkButton(
                bottom_box, text="+ Agregar", width=80, height=28,
                fg_color="#10B981", hover_color="#059669",
                font=ctk.CTkFont(size=11, weight="bold")
            )
            btn_add.configure(command=lambda prod=p, btn=btn_add: self.add_item_to_pos(prod, btn))
            btn_add.pack(side="right")

    def add_item_to_pos(self, product, button_widget=None):
        self.parent_app.add_to_cart(product)
        
        # Show Banner Notification
        self.show_toast_banner(f"🛒 ¡{product['nombre']} agregado al carrito!  |  RD$ {float(product['precio_venta']):.2f}")
        
        # Flash Button Feedback
        if button_widget:
            orig_text = button_widget.cget("text")
            orig_color = button_widget.cget("fg_color")
            button_widget.configure(text="✓ ¡Añadido!", fg_color="#059669")
            self.after(1000, lambda: button_widget.configure(text=orig_text, fg_color=orig_color))

if __name__ == "__main__":
    app = POSApp()
    app.mainloop()
