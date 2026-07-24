import os
import sys
import socket
import datetime
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk

from PIL import Image, ImageTk
from models import UserModel, ProductModel, DepartmentModel, SubDepartmentModel, CustomerModel, CompanyModel, CajaModel, VentaModel, InventoryMovementModel, ReportModel, ALL_MODULES
from utils.pdf_generator import generate_ticket_pdf, generate_inventory_report_pdf
from utils.excel_exporter import export_inventory_to_excel, export_sales_to_excel
from report_pdf import generate_pdf_report, print_pdf_file

import calendar

class CTkCalendarPopup(ctk.CTkFrame):
    """Modern Dark-Themed Dropdown Calendar Picker Component (100% Native Dropdown Below Target Field)"""
    def __init__(self, parent, initial_date=None, on_select_callback=None, btn_widget=None):
        root_win = parent.winfo_toplevel()
        width, height = 310, 330
        super().__init__(root_win, width=width, height=height, fg_color="#0F172A", border_width=1, border_color="#334155", corner_radius=8)
        
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.selected_date = initial_date or datetime.date.today()
        self.curr_year = self.selected_date.year
        self.curr_month = self.selected_date.month
        self.showing_month_selector = False

        if btn_widget and btn_widget.winfo_exists():
            root_win.update_idletasks()
            rw = root_win.winfo_width()
            bx = btn_widget.winfo_rootx() - root_win.winfo_rootx()
            
            # If target field is near right edge (e.g. 'Hasta'), align right edges so it stays inside window
            if bx + width > rw - 20:
                self.place(in_=btn_widget, relx=1.0, rely=1.0, x=-width, y=2)
            else:
                self.place(in_=btn_widget, relx=0.0, rely=1.0, x=0, y=2)
        else:
            self.place(relx=0.5, rely=0.5, anchor="center")

        self.lift()

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=6)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self._build_header()
        self._build_weekdays()
        self._build_grid()

        self._btn_widget_str = str(btn_widget) if btn_widget and btn_widget.winfo_exists() else ""
        self._click_listener_active = False
        self.after(100, self._setup_click_listener)

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
            self.destroy()
        except Exception:
            pass

    def _build_header(self):
        if hasattr(self, 'hdr_frame') and self.hdr_frame.winfo_exists():
            self.hdr_frame.destroy()

        self.hdr_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.hdr_frame.pack(fill="x", padx=10, pady=(8, 4))

        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Clickable Month & Year Header Label to toggle Month/Year selector!
        self.lbl_month_year = ctk.CTkButton(
            self.hdr_frame,
            text=f"{months_es[self.curr_month]} {self.curr_year} ▾",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent", hover_color="#1E293B", text_color="#38BDF8",
            command=self._toggle_month_year_selector
        )
        self.lbl_month_year.pack(side="left", padx=2)

        btn_next = ctk.CTkButton(self.hdr_frame, text="▶", width=26, height=26, fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=10), command=lambda: self._change_month(1))
        btn_next.pack(side="right", padx=2)

        btn_prev = ctk.CTkButton(self.hdr_frame, text="◀", width=26, height=26, fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=10), command=lambda: self._change_month(-1))
        btn_prev.pack(side="right", padx=2)

    def _toggle_month_year_selector(self):
        self.showing_month_selector = not self.showing_month_selector
        if self.showing_month_selector:
            self._build_month_year_grid()
        else:
            self._build_grid()

    def _build_weekdays(self):
        if hasattr(self, 'wf_frame') and self.wf_frame.winfo_exists():
            self.wf_frame.destroy()

        self.wf_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.wf_frame.pack(fill="x", padx=8, pady=(2, 4))

        days_headers = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
        for d in days_headers:
            ctk.CTkLabel(self.wf_frame, text=d, font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8", width=38).pack(side="left", padx=1)

    def _build_grid(self):
        if hasattr(self, 'grid_frame') and self.grid_frame.winfo_exists():
            self.grid_frame.destroy()

        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        cal = calendar.Calendar(firstweekday=6)
        month_days = list(cal.itermonthdates(self.curr_year, self.curr_month))
        while len(month_days) < 42:
            month_days.append(month_days[-1] + datetime.timedelta(days=1))

        rows = [month_days[i:i+7] for i in range(0, 42, 7)]
        today = datetime.date.today()

        for r_idx, row in enumerate(rows):
            rf = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
            rf.pack(fill="x", pady=1)

            for d_idx, d_date in enumerate(row):
                is_curr_month = (d_date.month == self.curr_month)
                is_selected = (d_date == self.selected_date)
                is_today = (d_date == today)

                if is_selected:
                    fg = "#2563EB" # Blue matching button
                    h_color = "#1D4ED8"
                    t_color = "#F8FAFC"
                elif is_curr_month:
                    fg = "#1E293B"
                    h_color = "#334155"
                    t_color = "#F8FAFC"
                else:
                    fg = "#0F172A"
                    h_color = "#1E293B"
                    t_color = "#475569"

                btn = ctk.CTkButton(
                    rf, text=str(d_date.day), width=38, height=30,
                    fg_color=fg, hover_color=h_color, text_color=t_color,
                    font=ctk.CTkFont(size=11, weight="bold" if (is_selected or is_today) else "normal"),
                    corner_radius=15 if is_selected else 6,
                    command=lambda target_date=d_date: self._select_day(target_date)
                )
                btn.pack(side="left", padx=1)

    def _build_month_year_grid(self):
        if hasattr(self, 'grid_frame') and self.grid_frame.winfo_exists():
            self.grid_frame.destroy()

        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Year Controls Header
        yr_hdr = ctk.CTkFrame(self.grid_frame, fg_color="#1E293B", corner_radius=6)
        yr_hdr.pack(fill="x", pady=(4, 8))

        ctk.CTkButton(yr_hdr, text="◀", width=28, height=26, fg_color="transparent", hover_color="#334155", command=lambda: self._change_year(-1)).pack(side="left", padx=2)
        ctk.CTkLabel(yr_hdr, text=f"Año {self.curr_year}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC").pack(side="left", expand=True)
        ctk.CTkButton(yr_hdr, text="▶", width=28, height=26, fg_color="transparent", hover_color="#334155", command=lambda: self._change_year(1)).pack(side="right", padx=2)

        # 12 Month Grid (4 rows x 3 cols)
        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        m_grid = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        m_grid.pack(fill="both", expand=True)

        for idx in range(1, 13):
            r = (idx - 1) // 3
            c = (idx - 1) % 3
            m_name = months_es[idx]
            is_sel_m = (idx == self.curr_month)

            btn = ctk.CTkButton(
                m_grid, text=m_name, width=88, height=36,
                fg_color="#2563EB" if is_sel_m else "#1E293B",
                hover_color="#1D4ED8" if is_sel_m else "#334155",
                text_color="#F8FAFC",
                font=ctk.CTkFont(size=11, weight="bold" if is_sel_m else "normal"),
                command=lambda m_num=idx: self._select_month(m_num)
            )
            btn.grid(row=r, column=c, padx=3, pady=3)

    def _change_year(self, delta):
        self.curr_year += delta
        self._build_month_year_grid()

    def _select_month(self, m_num):
        self.curr_month = m_num
        self.showing_month_selector = False
        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_month_year.configure(text=f"{months_es[self.curr_month]} {self.curr_year} ▾")
        self._build_grid()

    def _change_month(self, delta):
        m = self.curr_month + delta
        y = self.curr_year
        if m > 12:
            m = 1; y += 1
        elif m < 1:
            m = 12; y -= 1
        self.curr_month = m
        self.curr_year = y

        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_month_year.configure(text=f"{months_es[self.curr_month]} {self.curr_year} ▾")
        if self.showing_month_selector:
            self._build_month_year_grid()
        else:
            self._build_grid()

    def _select_day(self, target_date):
        self.selected_date = target_date
        if self.on_select_callback:
            self.on_select_callback(target_date)
        self.destroy()

def get_asset_path(relative_path):
    """Gets absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

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
        self.bind_all("<F5>", lambda e: self.load_caja_tab(force_rebuild=True))
        self.bind_all("<F6>", lambda e: self.open_quick_stock_lookup())
        self.bind_all("<F8>", lambda e: self.open_discount_keypad())
        self.bind_all("<F10>", lambda e: self.open_touch_payment_modal())
        self.bind_all("<F12>", lambda e: self.reprint_last_ticket())
        
        self.show_login()

    # ==========================================
    # LOGIN SCREEN (Clean Minimalist Corporate UI)
    # ==========================================
    def show_login(self):
        self.current_user = None
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
        lbl_card_title.pack(pady=(30, 20))

        # Username Input
        lbl_u = ctk.CTkLabel(card, text="Usuario", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1")
        lbl_u.pack(anchor="w", padx=35, pady=(5, 3))

        self.ent_username = ctk.CTkEntry(
            card,
            width=320, height=42, fg_color="#0F172A", border_color="#475569", corner_radius=6
        )
        self.ent_username.pack(padx=35, pady=(0, 12))
        self.ent_username.bind("<Return>", lambda e: self.ent_password.focus())

        # Password Input
        lbl_p = ctk.CTkLabel(card, text="Clave", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1")
        lbl_p.pack(anchor="w", padx=35, pady=(5, 3))

        self.ent_password = ctk.CTkEntry(
            card, show="*", 
            width=320, height=42, fg_color="#0F172A", border_color="#475569", corner_radius=6
        )
        self.ent_password.pack(padx=35, pady=(0, 20))
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
        btn_login.pack(padx=35, pady=(5, 30))

        # Auto-focus username field
        self.after(100, lambda: self.ent_username.focus())

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
        self.lbl_caja_badge.pack(side="left", padx=15)

        # Wi-Fi Mobile Portal Badge
        local_ip = get_local_ip()
        mobile_url = f"http://{local_ip}:5000"
        lbl_mobile = ctk.CTkLabel(
            top_bar, text=f"  📱 Consulta Móvil Wi-Fi: {mobile_url}  ", 
            font=ctk.CTkFont(size=11, weight="bold"), 
            fg_color="#1E3A8A", text_color="#93C5FD", corner_radius=6
        )
        lbl_mobile.pack(side="left", padx=10)

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
        sidebar = ctk.CTkFrame(main_body, width=230, fg_color="#0F172A", corner_radius=0)
        sidebar.pack(side="left", fill="y")

        self.content_area = ctk.CTkFrame(main_body, fg_color="#0F172A", corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Nav Buttons filtered by RBAC permissions
        self.nav_buttons = {}

        btn_home = ctk.CTkButton(
            sidebar, text="  🏠 Menú Principal", font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=42, anchor="w", corner_radius=6,
            command=self.load_welcome_tab
        )
        btn_home.pack(fill="x", padx=10, pady=(20, 5))
        self.nav_buttons["welcome"] = btn_home

        if UserModel.has_permission(self.current_user, "pos"):
            btn_pos = ctk.CTkButton(
                sidebar, text="  🛒 Caja / POS", font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
                command=self.load_pos_tab
            )
            btn_pos.pack(fill="x", padx=10, pady=5)
            self.nav_buttons["pos"] = btn_pos

        if UserModel.has_permission(self.current_user, "inventory"):
            btn_inv = ctk.CTkButton(
                sidebar, text="  📦 Inventario & Alertas", font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
                command=self.load_inventory_tab
            )
            btn_inv.pack(fill="x", padx=10, pady=5)
            self.nav_buttons["inventory"] = btn_inv

        if UserModel.has_permission(self.current_user, "caja"):
            btn_caja = ctk.CTkButton(
                sidebar, text="  💵 Apertura/Cierre Caja", font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
                command=self.load_caja_tab
            )
            btn_caja.pack(fill="x", padx=10, pady=5)
            self.nav_buttons["caja"] = btn_caja

        if UserModel.has_permission(self.current_user, "reports"):
            btn_rep = ctk.CTkButton(
                sidebar, text="  📊 Reportes & Ventas", font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
                command=self.load_reports_tab
            )
            btn_rep.pack(fill="x", padx=10, pady=5)
            self.nav_buttons["reports"] = btn_rep

        if UserModel.has_permission(self.current_user, "backoffice"):
            btn_bo = ctk.CTkButton(
                sidebar, text="  💼 Back Office", font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#1E293B", hover_color="#334155", height=42, anchor="w", corner_radius=6,
                command=self.load_backoffice_tab
            )
            btn_bo.pack(fill="x", padx=10, pady=5)
            self.nav_buttons["backoffice"] = btn_bo

        # Always start on Welcome Dashboard upon login
        self.load_welcome_tab()

    def show_tab(self, tab_key):
        self._highlight_nav_btn(tab_key)

        if not hasattr(self, '_tab_views') or self._tab_views is None:
            self._tab_views = {}

        self._active_tab_key = tab_key

        # If tab view already built once in session, bring to front INSTANTLY (0 ms)
        if tab_key in self._tab_views and self._tab_views[tab_key].winfo_exists():
            self._tab_views[tab_key].tkraise()
            self.after(60, lambda tk=tab_key: self._focus_tab_search_field(tk))
            return

        # Otherwise: First time opening this module! Create container & show Indeterminate Loading Bar
        view_frame = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
        view_frame.grid(row=0, column=0, sticky="nsew")
        self._tab_views[tab_key] = view_frame
        view_frame.tkraise()

        if tab_key == "welcome":
            self._build_welcome_tab_ui(view_frame)
            self.after(60, lambda: self._focus_tab_search_field("welcome"))
        else:
            self._build_tab_with_loading_bar(tab_key, view_frame)

    def _build_tab_with_loading_bar(self, tab_key, view_frame):
        module_titles = {
            "pos": "Caja / POS",
            "inventory": "Inventario & Alertas",
            "caja": "Apertura / Cierre de Caja",
            "reports": "Reportes & Ventas",
            "backoffice": "Back Office"
        }
        title_name = module_titles.get(tab_key, "Módulo")

        # Overlay attached directly to self.content_area covering 100% of module space!
        overlay = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()

        center_card = ctk.CTkFrame(overlay, fg_color="#1E293B", corner_radius=14, border_width=2, border_color="#334155")
        center_card.place(relx=0.5, rely=0.5, anchor="center")

        lbl_title = ctk.CTkLabel(
            center_card, text=f"⏳ Cargando Módulo de {title_name}...",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC"
        )
        lbl_title.pack(padx=45, pady=(26, 12))

        # Indeterminate Progress Bar
        pbar = ctk.CTkProgressBar(center_card, mode="indeterminate", width=360, height=14, progress_color="#2563EB", fg_color="#0F172A")
        pbar.pack(padx=45, pady=8)
        pbar.start()

        # Real-time Elapsed Time Counter
        t0 = time.time()
        lbl_timer = ctk.CTkLabel(
            center_card, text="⏱️ Tiempo de carga: 0.0s",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#38BDF8"
        )
        lbl_timer.pack(padx=45, pady=(6, 8))

        sub_lbl = ctk.CTkLabel(
            center_card, text="Construyendo interfaz y cargando datos esenciales...",
            font=ctk.CTkFont(size=11), text_color="#64748B"
        )
        sub_lbl.pack(padx=45, pady=(0, 26))

        # Force UI update so overlay and progress bar render BEFORE build begins!
        self.update_idletasks()

        timer_active = [True]

        def _update_timer():
            if timer_active[0] and overlay.winfo_exists():
                elapsed = time.time() - t0
                lbl_timer.configure(text=f"⏱️ Tiempo de carga: {elapsed:.1f}s")
                self.after(50, _update_timer)

        _update_timer()

        def _deferred_build():
            try:
                if tab_key == "pos":
                    self._build_pos_tab_ui(view_frame)
                elif tab_key == "inventory":
                    self._build_inventory_tab_ui(view_frame)
                elif tab_key == "caja":
                    self._build_caja_tab_ui(view_frame)
                elif tab_key == "reports":
                    self._build_reports_tab_ui(view_frame)
                elif tab_key == "backoffice":
                    self._build_backoffice_tab_ui(view_frame)
                
                self.update_idletasks()
            finally:
                # Minimum 450ms display duration so user clearly sees the progress bar & timer counting up!
                elapsed_ms = int((time.time() - t0) * 1000)
                remaining_ms = max(50, 450 - elapsed_ms)

                def _finish():
                    timer_active[0] = False
                    try:
                        pbar.stop()
                        overlay.destroy()
                    except Exception:
                        pass
                    self.after(60, lambda: self._focus_tab_search_field(tab_key))

                self.after(remaining_ms, _finish)

        self.after(60, _deferred_build)

    def _focus_tab_search_field(self, tab_key):
        try:
            if tab_key == "pos" and hasattr(self, 'ent_pos_search') and self.ent_pos_search.winfo_exists():
                self.ent_pos_search.focus_set()
                self.ent_pos_search.focus()
            elif tab_key == "inventory" and hasattr(self, 'ent_inv_search') and self.ent_inv_search.winfo_exists():
                self.ent_inv_search.focus_set()
                self.ent_inv_search.focus()
            elif tab_key == "backoffice" and hasattr(self, '_ent_bo_search_prod') and self._ent_bo_search_prod.winfo_exists():
                self._ent_bo_search_prod.focus_set()
                self._ent_bo_search_prod.focus()
        except Exception:
            pass

    def _highlight_nav_btn(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color="#2563EB", hover_color="#1D4ED8")
            else:
                btn.configure(fg_color="#1E293B", hover_color="#334155")

    def load_welcome_tab(self):
        self.show_tab("welcome")

    def _build_welcome_tab_ui(self, parent):

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

        def _on_canvas_resize(event):
            canvas.itemconfig(wrapper_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_resize)

        def _on_wrapper_resize(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        wrapper.bind("<Configure>", _on_wrapper_resize)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        inner = ctk.CTkFrame(wrapper, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Hero banner
        user_name = self.current_user.get("nombre_completo", "Operador") if self.current_user else "Operador"
        user_role = self.current_user.get("rol", "") if self.current_user else ""
        caja_status = "Caja ABIERTA  🟢" if getattr(self, "active_caja", None) else "Caja CERRADA  🔴"

        hero = ctk.CTkFrame(inner, fg_color="#1E293B", corner_radius=12,
                            border_width=1, border_color="#334155")
        hero.pack(fill="x", pady=(0, 18))
        hero_pad = ctk.CTkFrame(hero, fg_color="transparent")
        hero_pad.pack(fill="x", padx=24, pady=18)

        ctk.CTkLabel(hero_pad,
            text=f"Bienvenido, {user_name}!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F8FAFC", anchor="w").pack(anchor="w")
        ctk.CTkLabel(hero_pad,
            text=f"Rol: {user_role}   |   {caja_status}   |   Seleccione el modulo:",
            font=ctk.CTkFont(size=12), text_color="#94A3B8", anchor="w").pack(anchor="w", pady=(6, 0))

        ctk.CTkLabel(inner, text="MODULOS DISPONIBLES",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8", anchor="w").pack(anchor="w", pady=(4, 10))

        modules_data = [
            ("pos",        "PUNTO DE VENTA / CAJA",
             "Facturacion, cobros en efectivo, tarjeta\ny transferencia. Descuentos y tickets.",
             "#2563EB", "#1D4ED8", "Ir al Punto de Venta", self.load_pos_tab),
            ("inventory",  "INVENTARIO Y ALERTAS",
             "Gestion de productos, existencias, precios\ny alertas de stock minimo.",
             "#0D9488", "#0F766E", "Ir a Inventario", self.load_inventory_tab),
            ("caja",       "APERTURA Y CIERRE DE CAJA",
             "Control diario de efectivo, apertura,\narqueo y cuadre de turno.",
             "#D97706", "#B45309", "Gestionar Caja", self.load_caja_tab),
            ("reports",    "REPORTES Y VENTAS",
             "Consolidados, historial de facturas,\nganancias y exportaciones.",
             "#9333EA", "#7E22CE", "Ver Reportes", self.load_reports_tab),
            ("backoffice", "MODULO BACK OFFICE",
             "Articulos, clientes/proveedores,\noperadores y permisos RBAC.",
             "#4F46E5", "#4338CA", "Entrar al Back Office", self.load_backoffice_tab),
        ]

        visible = [(k, t, d, bb, bh, bt, cmd) for k, t, d, bb, bh, bt, cmd in modules_data
                   if UserModel.has_permission(self.current_user, k)]

        for i in range(0, len(visible), 2):
            row_frame = ctk.CTkFrame(inner, fg_color="transparent")
            row_frame.pack(fill="x", pady=6)
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=1)

            for col_idx, item in enumerate(visible[i:i+2]):
                k, title, desc, btn_bg, btn_hv, btn_txt, cmd = item
                card = ctk.CTkFrame(row_frame, fg_color="#1E293B", corner_radius=10,
                                    border_width=1, border_color="#334155")
                card.grid(row=0, column=col_idx,
                          padx=(0, 8) if col_idx == 0 else (0, 0), sticky="nsew")

                pad = ctk.CTkFrame(card, fg_color="transparent")
                pad.pack(fill="x", padx=16, pady=16)

                ctk.CTkLabel(pad, text=title,
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color="#F8FAFC", anchor="w").pack(fill="x", pady=(0, 6))
                ctk.CTkLabel(pad, text=desc,
                             font=ctk.CTkFont(size=11), text_color="#94A3B8",
                             anchor="w", justify="left", wraplength=300).pack(fill="x", pady=(0, 12))
                ctk.CTkButton(pad, text=btn_txt,
                              font=ctk.CTkFont(size=12, weight="bold"),
                              fg_color=btn_bg, hover_color=btn_hv,
                              height=36, corner_radius=6,
                              command=cmd).pack(anchor="w")

    def clear_content(self):
        self._tab_views = {}
        self._active_tab_key = None
        for widget in list(self.content_area.winfo_children()):
            try:
                widget.destroy()
            except Exception:
                pass


    # ==========================================
    # TAB 1: POS / CAJA
    # ==========================================
    def load_pos_tab(self):
        self.show_tab("pos")

    def _build_pos_tab_ui(self, parent):
        # Main container for POS
        pos_frame = ctk.CTkFrame(parent, fg_color="transparent")
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
        self._pos_search_timer = None
        def _debounced_pos_search(e):
            if e.keysym in ("Return", "Tab", "Up", "Down", "Escape"):
                return
            if getattr(self, '_pos_search_timer', None):
                self.after_cancel(self._pos_search_timer)
            self._pos_search_timer = self.after(250, self.search_pos_products)

        self.ent_pos_search.bind("<KeyRelease>", _debounced_pos_search)
        self.ent_pos_search.bind("<Return>", lambda e: self.quick_add_pos_barcode())

        # --- SUB-DEPARTMENTS QUICK FILTER BAR & FLIP CHART BUTTON ---
        subdep_bar = ctk.CTkFrame(left_side, fg_color="transparent")
        subdep_bar.pack(fill="x", padx=12, pady=(0, 10))

        self.active_subdep_filter = None
        self._subdep_buttons = {}

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
                fg_color="#2563EB" if self.active_subdep_filter == sd_id else "#334155",
                hover_color="#1D4ED8", height=32, width=0, corner_radius=6,
                command=lambda s_id=sd_id: self.set_subdep_filter(s_id)
            )
            btn_sd.pack(side="left", padx=2, expand=True, fill="x")
            self._subdep_buttons[sd_id] = btn_sd

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
        if hasattr(self, '_subdep_buttons'):
            for s_id, btn in self._subdep_buttons.items():
                btn.configure(fg_color="#2563EB" if s_id == subdep_id else "#334155")
        self.search_pos_products(force_reload=True)

    def open_flip_chart_modal(self):
        FlipChartModal(self)

    def search_pos_products(self, force_reload=False):
        term = self.ent_pos_search.get().strip() if hasattr(self, 'ent_pos_search') else ""
        subdep_filter = getattr(self, 'active_subdep_filter', None)

        products = ProductModel.search_live(term, limit=100 if term else 20, active_only=True, subdep_id=subdep_filter)

        for w in self.products_scroll.winfo_children():
            w.destroy()

        if not products:
            lbl = ctk.CTkLabel(self.products_scroll,
                text="No se encontraron productos en este sub-departamento." if subdep_filter else ("No se encontraron productos." if term else "No hay artículos registrados."),
                text_color="#A0A0B0", font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(pady=25)
            return

        for p in products:
            card = ctk.CTkFrame(
                self.products_scroll,
                fg_color="#0F172A",
                corner_radius=10,
                border_width=1,
                border_color="#334155"
            )
            card.pack(fill="x", pady=4, padx=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            left_info = ctk.CTkFrame(inner, fg_color="transparent")
            left_info.pack(side="left", fill="x", expand=True)

            subdep_tag = p.get('subdepartamento_nombre') or 'General'
            ctk.CTkLabel(left_info, text=p['nombre'], anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC").pack(anchor="w")
            ctk.CTkLabel(left_info, text=f"📂 {subdep_tag}   •   Cód: {p['codigo_barras']}",
                anchor="w", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w", pady=(2, 0))

            right_actions = ctk.CTkFrame(inner, fg_color="transparent")
            right_actions.pack(side="right")

            stock_val = p.get('stock_actual') if p.get('stock_actual') is not None else 0
            stock_min = p.get('stock_minimo', 5) or 5
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D"

            stock_badge = ctk.CTkFrame(right_actions, fg_color=stock_bg, corner_radius=6)
            stock_badge.pack(side="left", padx=(0, 12))
            ctk.CTkLabel(stock_badge, text=f"Stock: {stock_val}",
                font=ctk.CTkFont(size=11, weight="bold"), text_color=stock_color).pack(padx=8, pady=3)

            ctk.CTkLabel(right_actions, text=f"RD$ {float(p['precio_venta']):.2f}",
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#38BDF8").pack(side="left", padx=(0, 12))

            ctk.CTkButton(right_actions, text="+ Agregar", width=85, height=34,
                corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#2563EB", hover_color="#1D4ED8",
                command=lambda prod=p: self.add_to_cart(prod)).pack(side="left")

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

        if product.get("precio_manual", 0):
            dialog = ctk.CTkInputDialog(text=f"El artículo '{product['nombre']}' está configurado para precio manual.\nIngrese el precio de venta (RD$):", title="Precio Manual")
            val = dialog.get_input()
            if val:
                try:
                    parsed_p = float(val.strip())
                    if parsed_p > 0:
                        orig_price = parsed_p
                except ValueError:
                    pass

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
                    if not target_item.get("es_descontable", 1):
                        messagebox.showwarning("Descuento No Permitido", f"El artículo '{target_item['nombre']}' está marcado como NO DESCONTABLE.")
                        return

                    orig_unit = float(target_item.get("precio_original", target_item["precio_venta"]))
                    if disc_type == "porcentaje":
                        disc_unit = orig_unit * (val / 100.0)
                    else:
                        disc_unit = val

                    target_item["descuento_monto"] = min(orig_unit, disc_unit)
                    target_item["precio_venta"] = max(0.0, orig_unit - target_item["descuento_monto"])

                elif disc_mode == "cart":
                    tot_val = sum(float(i.get("precio_original", i["precio_venta"])) * i["cantidad"] for i in self.cart if i.get("es_descontable", 1))
                    if tot_val > 0:
                        for item in self.cart:
                            if not item.get("es_descontable", 1):
                                continue
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
            self.load_caja_tab(force_rebuild=True)
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

        # Cart Table Scroll (flexible expand=True so bottom buttons are NEVER compressed)
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
        btn_touch_pay.pack(fill="x", padx=12, pady=(4, 10))

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
            self.load_caja_tab(force_rebuild=True)
            return

        subtotal = sum(float(i["precio_venta"]) * i["cantidad"] for i in self.cart)
        total_pagar = subtotal * 1.18

        pay_win = ctk.CTkToplevel(self)
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
        lbl_monto_total.pack(pady=(0, 6))

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

        def _validate_decimal_input(P):
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
            cart_copy = list(self.cart)

            # Close payment window immediately
            try:
                pay_win.destroy()
            except Exception:
                pass

            # Full-screen OPAQUE loading overlay on content_area with timer
            overlay = ctk.CTkFrame(self.content_area, fg_color="#0F172A", corner_radius=0)
            overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            overlay.lift()

            center_card = ctk.CTkFrame(overlay, fg_color="#1E293B", corner_radius=14, border_width=2, border_color="#334155")
            center_card.place(relx=0.5, rely=0.5, anchor="center")

            lbl_title = ctk.CTkLabel(
                center_card, text="⏳ Procesando Transacción de Venta...",
                font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC"
            )
            lbl_title.pack(padx=45, pady=(26, 12))

            # Indeterminate Sliding Progress Bar
            pbar = ctk.CTkProgressBar(center_card, mode="indeterminate", width=360, height=14, progress_color="#10B981", fg_color="#0F172A")
            pbar.pack(padx=45, pady=8)
            pbar.start()

            # Real-time Elapsed Time Counter
            t0 = time.time()
            lbl_timer = ctk.CTkLabel(
                center_card, text="⏱️ Tiempo de procesamiento: 0.0s",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#38BDF8"
            )
            lbl_timer.pack(padx=45, pady=(6, 8))

            sub_lbl = ctk.CTkLabel(
                center_card, text="Guardando venta en base de datos y emitiendo comprobante...",
                font=ctk.CTkFont(size=11), text_color="#64748B"
            )
            sub_lbl.pack(padx=45, pady=(0, 26))

            self.update_idletasks()
            timer_active = [True]

            def _update_timer():
                if timer_active[0] and overlay.winfo_exists():
                    elapsed = time.time() - t0
                    lbl_timer.configure(text=f"⏱️ Tiempo de procesamiento: {elapsed:.1f}s")
                    self.after(50, _update_timer)

            _update_timer()

            def _execute_sale():
                try:
                    sale_res = VentaModel.procesar_venta(caja_id, user_id, "Cliente General", tipo_pago, cart_copy)
                    
                    # Generate Ticket PDF
                    output_dir = os.path.join(os.getcwd(), "tickets")
                    os.makedirs(output_dir, exist_ok=True)
                    ticket_file = os.path.join(output_dir, f"Ticket_{sale_res['codigo_factura']}.pdf")
                    generate_ticket_pdf(sale_res, ticket_file)

                    codigo_fact = sale_res["codigo_factura"]
                    self.cart = []
                    self.search_pos_products(force_reload=True)
                    self.show_pos_cart_view()
                    self.update_idletasks()

                    self.show_toast_notification(f"✔ ¡VENTA #{codigo_fact} PROCESADA CON ÉXITO!", 5000)
                except Exception as e:
                    messagebox.showerror("Error en Venta", f"Ocurrió un error al guardar la venta: {e}")
                finally:
                    # Guarantee 450ms minimum display so user clearly sees the progress bar & timer
                    elapsed_ms = int((time.time() - t0) * 1000)
                    remaining_ms = max(50, 450 - elapsed_ms)

                    def _finish():
                        timer_active[0] = False
                        try:
                            pbar.stop()
                            overlay.destroy()
                        except Exception:
                            pass
                        self.after(60, lambda: self._focus_tab_search_field("pos"))

                    self.after(remaining_ms, _finish)

            self.after(60, _execute_sale)

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
        self.show_tab("inventory")

    def _build_inventory_tab_ui(self, parent):
        inv_frame = ctk.CTkFrame(parent, fg_color="transparent")
        inv_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header Action Controls
        ctrl_bar = ctk.CTkFrame(inv_frame, fg_color="#16161F", height=50)
        ctrl_bar.pack(fill="x", pady=(0, 10))

        self.ent_inv_search = ctk.CTkEntry(ctrl_bar, placeholder_text="Buscar en inventario...", width=250)
        self.ent_inv_search.pack(side="left", padx=10, pady=10)
        self._inv_search_timer = None
        def _debounced_inv_search(e):
            if getattr(self, '_inv_search_timer', None):
                self.after_cancel(self._inv_search_timer)
            self._inv_search_timer = self.after(250, self.render_inventory_table)
        self.ent_inv_search.bind("<KeyRelease>", _debounced_inv_search)

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

    def render_inventory_table(self, force_reload=False):
        term = self.ent_inv_search.get().strip() if hasattr(self, 'ent_inv_search') else ""
        products = ProductModel.search_live(term, limit=100 if term else 20)

        for w in self.table_scroll.winfo_children():
            w.destroy()

        headers = ["Cód. Barras", "Nombre Producto", "Departamento", "Sub-Depto", "P. Costo", "P. Venta", "Stock", "Estado", "Acciones"]
        cols_w = [110, 170, 130, 130, 80, 80, 50, 90, 80]

        head_row = ctk.CTkFrame(self.table_scroll, fg_color="#1F2937", height=35)
        head_row.pack(fill="x", pady=2)
        for idx, h in enumerate(headers):
            ctk.CTkLabel(head_row, text=h, font=ctk.CTkFont(size=11, weight="bold"), width=cols_w[idx]).pack(side="left", padx=2)

        if not products:
            lbl = ctk.CTkLabel(self.table_scroll, text="No se encontraron productos.", text_color="#A0A0B0", font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(pady=25)
            return

        for p in products:
            stock = p.get('stock_actual', 0) if p.get('stock_actual') is not None else 0
            min_s = p.get('stock_minimo', 5) or 5
            status_txt, status_bg = "NORMAL", "#10B981"
            if stock <= 0: status_txt, status_bg = "AGOTADO", "#EF4444"
            elif stock <= min_s: status_txt, status_bg = "STOCK BAJO", "#F59E0B"

            dep_tag = p.get('departamento_nombre') or p.get('categoria_nombre') or 'General'
            subdep_tag = p.get('subdepartamento_nombre') or 'General'

            row = ctk.CTkFrame(self.table_scroll, fg_color="#111118", height=38)
            row.pack(fill="x", pady=2)

            for idx, val in enumerate([p['codigo_barras'], p['nombre'], dep_tag, subdep_tag,
                                        f"RD${float(p['precio_costo']):.2f}", f"RD${float(p['precio_venta']):.2f}", str(stock)]):
                ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=11), width=cols_w[idx]).pack(side="left", padx=2)

            ctk.CTkLabel(row, text=f" {status_txt} ", font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=status_bg, text_color="white", corner_radius=4, width=cols_w[7]).pack(side="left", padx=2)
            ctk.CTkButton(row, text="✏", width=30, height=24, fg_color="#374151",
                command=lambda prod=p: self.modal_product_form(prod)).pack(side="left", padx=2)
            ctk.CTkButton(row, text="🗑", width=30, height=24, fg_color="#EF4444",
                command=lambda prod=p: self.delete_prod(prod)).pack(side="left", padx=2)

    def delete_prod(self, prod):
        if messagebox.askyesno("Eliminar Producto", f"¿Seguro que deseas eliminar '{prod['nombre']}'?"):
            ProductModel.delete_product(prod["id"])
            self.render_inventory_table(force_reload=True)

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
    def load_caja_tab(self, force_rebuild=False):
        if force_rebuild and hasattr(self, '_tab_views') and "caja" in self._tab_views:
            if self._tab_views["caja"].winfo_exists():
                self._tab_views["caja"].destroy()
            del self._tab_views["caja"]
        self.show_tab("caja")

    def _build_caja_tab_ui(self, parent):
        caja_frame = ctk.CTkFrame(parent, fg_color="transparent")
        caja_frame.pack(fill="both", expand=True, padx=20, pady=20)

        card_caja = ctk.CTkFrame(caja_frame, fg_color="#16161F", corner_radius=12, width=600)
        card_caja.pack(pady=30, padx=20)

        lbl_t = ctk.CTkLabel(card_caja, text="GESTIÓN DE CAJA Y TURNOS", font=ctk.CTkFont(size=18, weight="bold"), text_color="#38BDF8")
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
                    self.load_caja_tab(force_rebuild=True)
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
                    self.load_caja_tab(force_rebuild=True)
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un monto inicial válido.")

            btn_open = ctk.CTkButton(card_caja, text="🔓 ABRIR NUEVA CAJA", fg_color="#10B981", hover_color="#059669", width=300, height=45, command=do_open)
            btn_open.pack(pady=(10, 25))

    # ==========================================
    # TAB 4: REPORTES & VENTAS
    # ==========================================
    def load_reports_tab(self):
        self.show_tab("reports")

    def _build_reports_tab_ui(self, parent):
        # --- State ---
        self._report_granularity = "Día"
        self._report_ref_date = datetime.date.today()
        self._report_period = "Día"
        self._report_type = "General Consolidado"
        self._report_start_date = ""
        self._report_end_date = ""

        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=16, pady=10)

        # ── HEADER TITLE
        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(hdr, text="📊 MÓDULO DE REPORTES & ANALÍTICA",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#8B5CF6").pack(side="left")

        # ── PERIOD FILTER BAR WITH DROPDOWNS & NAV BUTTONS
        period_bar = ctk.CTkFrame(outer, fg_color="#1E293B", corner_radius=8, height=48)
        period_bar.pack(fill="x", pady=(0, 8))
        period_bar.pack_propagate(False)

        ctk.CTkLabel(period_bar, text=" 📅 Modo:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(10, 4))

        self._cmb_report_granularity = ctk.CTkComboBox(
            period_bar,
            values=["Día", "Semana", "Mes", "Año", "Personalizado"],
            width=115, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_granularity_changed
        )
        self._cmb_report_granularity.set("Día")
        self._cmb_report_granularity.pack(side="left", padx=4)

        # Prev Button
        self._btn_report_prev = ctk.CTkButton(
            period_bar, text="◀ Anterior", width=85, height=32,
            fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._nav_report_period(-1)
        )
        self._btn_report_prev.pack(side="left", padx=(6, 2))

        # Date Filter Dropdown with Integrated Calendar Button
        ctk.CTkLabel(period_bar, text="Fecha:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(6, 2))

        date_box_frame = ctk.CTkFrame(period_bar, fg_color="transparent")
        date_box_frame.pack(side="left", padx=2)

        self._cmb_report_date_list = ctk.CTkComboBox(
            date_box_frame, values=["Seleccionar..."], width=175, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_report_date_combo_selected
        )
        self._cmb_report_date_list.pack(side="left")
        self._cmb_report_date_list.bind("<Double-Button-1>", lambda e: self._open_report_calendar_popup(btn_widget=self._cmb_report_date_list))

        # Integrated Calendar Icon Button
        self._btn_report_calendar = ctk.CTkButton(
            date_box_frame, text="📅", width=34, height=32,
            fg_color="#2563EB", hover_color="#1D4ED8", text_color="#F8FAFC",
            font=ctk.CTkFont(size=13),
            command=lambda: self._open_report_calendar_popup(btn_widget=self._cmb_report_date_list)
        )
        self._btn_report_calendar.pack(side="left", padx=(2, 0))

        # Next Button
        self._btn_report_next = ctk.CTkButton(
            period_bar, text="Siguiente ▶", width=85, height=32,
            fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._nav_report_period(1)
        )
        self._btn_report_next.pack(side="left", padx=(4, 6))

        # Live Range Indicator Label
        self._lbl_report_period_range = ctk.CTkLabel(
            period_bar, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8"
        )
        self._lbl_report_period_range.pack(side="left", padx=6)

        # Custom date range (hidden by default)
        self._custom_date_frame = ctk.CTkFrame(period_bar, fg_color="transparent")
        
        lbl_s = ctk.CTkLabel(self._custom_date_frame, text="Desde 📅:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8")
        lbl_s.pack(side="left", padx=(6, 2))
        self._ent_start = ctk.CTkEntry(self._custom_date_frame, placeholder_text="DD-MM-YYYY (2 clics 📅)", width=130, height=32)
        self._ent_start.pack(side="left", padx=2)
        self._ent_start.bind("<Double-Button-1>", lambda e: self._open_calendar_for_entry(self._ent_start))

        lbl_e = ctk.CTkLabel(self._custom_date_frame, text="Hasta 📅:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8")
        lbl_e.pack(side="left", padx=(6, 2))
        self._ent_end = ctk.CTkEntry(self._custom_date_frame, placeholder_text="DD-MM-YYYY (2 clics 📅)", width=130, height=32)
        self._ent_end.pack(side="left", padx=2)
        self._ent_end.bind("<Double-Button-1>", lambda e: self._open_calendar_for_entry(self._ent_end))

        btn_apply = ctk.CTkButton(
            self._custom_date_frame, text="Aplicar", width=65, height=32,
            fg_color="#10B981", hover_color="#059669",
            command=self._apply_custom_date
        )
        btn_apply.pack(side="left", padx=4)

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


    def _get_report_date_bounds(self):
        mode = getattr(self, '_report_granularity', 'Día')
        ref = getattr(self, '_report_ref_date', datetime.date.today())

        if mode == "Día":
            s = ref
            e = ref
        elif mode == "Semana":
            s = ref - datetime.timedelta(days=ref.weekday())
            e = s + datetime.timedelta(days=6)
        elif mode == "Mes":
            s = ref.replace(day=1)
            _, last_day = calendar.monthrange(ref.year, ref.month)
            e = ref.replace(day=last_day)
        elif mode == "Año":
            s = datetime.date(ref.year, 1, 1)
            e = datetime.date(ref.year, 12, 31)
        elif mode == "Personalizado":
            s, e = None, None
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                if not s:
                    try: s = datetime.datetime.strptime(self._report_start_date, fmt).date()
                    except Exception: pass
                if not e:
                    try: e = datetime.datetime.strptime(self._report_end_date, fmt).date()
                    except Exception: pass
            if not s: s = datetime.date.today()
            if not e: e = datetime.date.today()
        else:
            s = ref
            e = ref

        return s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")

    def _on_report_granularity_changed(self, mode):
        self._report_granularity = mode
        if mode == "Personalizado":
            if hasattr(self, '_cmb_report_date_list') and self._cmb_report_date_list.master.winfo_exists():
                self._cmb_report_date_list.master.pack_forget()
            if hasattr(self, '_btn_report_prev') and self._btn_report_prev.winfo_exists():
                self._btn_report_prev.pack_forget()
            if hasattr(self, '_btn_report_next') and self._btn_report_next.winfo_exists():
                self._btn_report_next.pack_forget()
            self._custom_date_frame.pack(side="left", padx=4)
        else:
            self._custom_date_frame.pack_forget()
            if hasattr(self, '_btn_report_prev') and self._btn_report_prev.winfo_exists():
                self._btn_report_prev.pack(side="left", padx=(6, 2))
            if hasattr(self, '_cmb_report_date_list') and self._cmb_report_date_list.master.winfo_exists():
                self._cmb_report_date_list.master.pack(side="left", padx=2)
            if hasattr(self, '_btn_report_next') and self._btn_report_next.winfo_exists():
                self._btn_report_next.pack(side="left", padx=(4, 6))
            self._update_report_date_dropdown_options()
            self._render_report_content()

    def _nav_report_period(self, delta):
        mode = getattr(self, '_report_granularity', 'Día')
        ref = getattr(self, '_report_ref_date', datetime.date.today())

        if mode == "Día":
            ref = ref + datetime.timedelta(days=delta)
        elif mode == "Semana":
            ref = ref + datetime.timedelta(weeks=delta)
        elif mode == "Mes":
            m = ref.month + delta
            y = ref.year
            while m > 12: m -= 12; y += 1
            while m < 1: m += 12; y -= 1
            d = min(ref.day, calendar.monthrange(y, m)[1])
            ref = datetime.date(y, m, d)
        elif mode == "Año":
            y = ref.year + delta
            d = min(ref.day, calendar.monthrange(y, ref.month)[1])
            ref = datetime.date(y, ref.month, d)

        self._report_ref_date = ref
        self._update_report_date_dropdown_options()
        self._render_report_content()

    def _update_report_date_dropdown_options(self):
        mode = getattr(self, '_report_granularity', 'Día')
        ref = getattr(self, '_report_ref_date', datetime.date.today())
        today = datetime.date.today()

        opts = []
        sel_idx = 0

        if mode == "Día":
            for i in range(15, -16, -1):
                d = ref + datetime.timedelta(days=i)
                tag = " (Hoy)" if d == today else (" (Ayer)" if d == today - datetime.timedelta(days=1) else "")
                lbl = d.strftime("%d-%m-%Y") + tag
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Semana":
            curr_start = ref - datetime.timedelta(days=ref.weekday())
            for i in range(5, -6, -1):
                ws = curr_start + datetime.timedelta(weeks=i)
                we = ws + datetime.timedelta(days=6)
                lbl = ws.strftime("%d-%m-%Y") + " al " + we.strftime("%d-%m-%Y")
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Mes":
            months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            for i in range(6, -7, -1):
                m = ref.month + i
                y = ref.year
                while m > 12: m -= 12; y += 1
                while m < 1: m += 12; y -= 1
                lbl = months_es[m] + " " + str(y)
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        elif mode == "Año":
            for i in range(3, -4, -1):
                lbl = str(ref.year + i)
                opts.append(lbl)
                if i == 0:
                    sel_idx = len(opts) - 1

        if hasattr(self, '_cmb_report_date_list'):
            self._cmb_report_date_list.configure(values=opts)
            if opts and sel_idx < len(opts):
                self._cmb_report_date_list.set(opts[sel_idx])

        # Update Range Label with DD-MM-YYYY format
        s_raw, e_raw = self._get_report_date_bounds()
        try:
            s_dt = datetime.datetime.strptime(s_raw, "%Y-%m-%d")
            e_dt = datetime.datetime.strptime(e_raw, "%Y-%m-%d")
            s_formatted = s_dt.strftime("%d-%m-%Y")
            e_formatted = e_dt.strftime("%d-%m-%Y")
        except Exception:
            s_formatted, e_formatted = s_raw, e_raw

        if s_formatted == e_formatted:
            range_txt = f"📍 {s_formatted}"
        else:
            range_txt = f"📍 {s_formatted} al {e_formatted}"
        if hasattr(self, '_lbl_report_period_range'):
            self._lbl_report_period_range.configure(text=range_txt)

    def _open_calendar_for_entry(self, entry_widget):
        if hasattr(self, '_active_calendar_popup') and self._active_calendar_popup:
            try:
                if self._active_calendar_popup.winfo_exists():
                    self._active_calendar_popup.destroy()
            except Exception:
                pass
            self._active_calendar_popup = None

        def _on_date_picked(picked_date):
            d_str = picked_date.strftime("%d-%m-%Y")
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d_str)
            self._apply_custom_date()

        try:
            curr_val = entry_widget.get().strip()
            init_d = None
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    init_d = datetime.datetime.strptime(curr_val, fmt).date()
                    break
                except ValueError:
                    pass
            if not init_d:
                init_d = datetime.date.today()
        except Exception:
            init_d = datetime.date.today()

        self._active_calendar_popup = CTkCalendarPopup(
            self,
            initial_date=init_d,
            on_select_callback=_on_date_picked,
            btn_widget=entry_widget
        )

    def _open_report_calendar_popup(self, btn_widget=None):
        def _on_date_picked(picked_date):
            self._report_ref_date = picked_date
            self._update_report_date_dropdown_options()
            self._render_report_content()

        target_w = btn_widget or getattr(self, '_btn_report_calendar', None) or getattr(self, '_cmb_report_date_list', None)
        today = datetime.date.today()
        ref = getattr(self, '_report_ref_date', today)

        # Check if today falls within current active mode date range
        s_str, e_str = self._get_report_date_bounds()
        try:
            s_date = datetime.datetime.strptime(s_str, "%Y-%m-%d").date()
            e_date = datetime.datetime.strptime(e_str, "%Y-%m-%d").date()
            if s_date <= today <= e_date:
                initial_d = today
            else:
                initial_d = ref
        except Exception:
            initial_d = ref

        if hasattr(self, '_active_calendar_popup') and self._active_calendar_popup:
            try:
                if self._active_calendar_popup.winfo_exists():
                    self._active_calendar_popup.destroy()
            except Exception:
                pass
            self._active_calendar_popup = None

        self._active_calendar_popup = CTkCalendarPopup(
            self,
            initial_date=initial_d,
            on_select_callback=_on_date_picked,
            btn_widget=target_w
        )

    def _on_report_date_combo_selected(self, val):
        mode = getattr(self, '_report_granularity', 'Día')
        today = datetime.date.today()

        try:
            if mode == "Día":
                raw_d = val.split(" ")[0].strip()
                self._report_ref_date = datetime.datetime.strptime(raw_d, "%d-%m-%Y").date()
            elif mode == "Semana":
                parts = val.split(" al ")
                if len(parts) == 2:
                    raw_end = parts[1].strip()
                    self._report_ref_date = datetime.datetime.strptime(raw_end, "%d-%m-%Y").date()
            elif mode == "Mes":
                months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                m_str, y_str = val.split(" ")
                m_idx = months_es.index(m_str.strip())
                self._report_ref_date = datetime.date(int(y_str), m_idx, 1)
            elif mode == "Año":
                self._report_ref_date = datetime.date(int(val.strip()), 1, 1)
        except Exception as e:
            print("Error parsing report date combo:", e)

        self._update_report_date_dropdown_options()
        self._render_report_content()

    def _apply_custom_date(self):
        raw_start = self._ent_start.get().strip()
        raw_end = self._ent_end.get().strip()

        def to_iso(d_str):
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(d_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    pass
            return datetime.date.today().strftime("%Y-%m-%d")

        self._report_start_date = to_iso(raw_start) if raw_start else datetime.date.today().strftime("%Y-%m-%d")
        self._report_end_date = to_iso(raw_end) if raw_end else datetime.date.today().strftime("%Y-%m-%d")
        self._render_report_content()

    def _select_report_type(self, val):
        self._report_type = val
        self._render_report_content()

    def _get_period_label(self):
        s_str, e_str = self._get_report_date_bounds()
        if s_str == e_str:
            return s_str
        return f"Del {s_str} al {e_str}" 

    def _render_report_content(self):
        # Clear existing content
        for w in self._report_content_frame.winfo_children():
            w.destroy()

        s_str, e_str = self._get_report_date_bounds()
        start_dt = f"{s_str} 00:00:00"
        end_dt = f"{e_str} 23:59:59" 

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
        s_raw, e_raw = self._get_report_date_bounds()
        start_dt = f"{s_raw} 00:00:00"
        end_dt = f"{e_raw} 23:59:59"
        rtype = self._report_type
        period_lbl = self._lbl_report_period_range.cget("text") if hasattr(self, '_lbl_report_period_range') else f"{s_raw} al {e_raw}"
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
        s_raw, e_raw = self._get_report_date_bounds()
        start_dt = f"{s_raw} 00:00:00"
        end_dt = f"{e_raw} 23:59:59"
        rtype = self._report_type
        period_lbl = self._lbl_report_period_range.cget("text") if hasattr(self, '_lbl_report_period_range') else f"{s_raw} al {e_raw}"
        data = self._get_report_data_for_pdf(rtype, start_dt, end_dt)

        gran = getattr(self, '_report_granularity', 'reporte')
        default_name = f"reporte_{gran}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
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



    # ==========================================
    # TAB 5: BACK OFFICE
    # ==========================================
    def load_backoffice_tab(self):
        self.show_tab("backoffice")

    def _build_backoffice_tab_ui(self, parent):
        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        # Header Bar
        hdr = ctk.CTkFrame(outer, fg_color="#1E293B", corner_radius=8, height=48)
        hdr.pack(fill="x", pady=(0, 10))
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text="  💼 BACK OFFICE — ADMINISTRACIÓN INTEGRAL DE TIENDA & OPERADORES",
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            text_color="#F8FAFC"
        ).pack(side="left", padx=12, pady=10)

        # Tabview for Sub-modules
        def _on_bo_tab_change():
            try:
                sel = self._bo_tabview.get()
                if "Artículos" in sel and hasattr(self, '_ent_bo_search_prod') and self._ent_bo_search_prod.winfo_exists():
                    self.after(60, lambda: (self._ent_bo_search_prod.focus_set(), self._ent_bo_search_prod.focus()))
                elif "Clientes" in sel and hasattr(self, '_ent_bo_search_cust') and self._ent_bo_search_cust.winfo_exists():
                    self.after(60, lambda: (self._ent_bo_search_cust.focus_set(), self._ent_bo_search_cust.focus()))
            except Exception:
                pass

        self._bo_tabview = ctk.CTkTabview(outer, fg_color="#0F172A", segmented_button_fg_color="#1E293B",
                                          segmented_button_selected_color="#2563EB", segmented_button_selected_hover_color="#1D4ED8",
                                          command=_on_bo_tab_change)
        self._bo_tabview.pack(fill="both", expand=True)

        self._tab_item_maint = self._bo_tabview.add("🏷️ Mantenimiento Artículos")
        self._tab_customers  = self._bo_tabview.add("👥 Clientes & Proveedores")
        self._tab_operators  = self._bo_tabview.add("🔒 Operadores & Permisos (RBAC)")
        self._tab_store_cfg  = self._bo_tabview.add("🏬 Datos de la Tienda")

        # Load Sub-tabs with fault isolation
        try:
            self._load_bo_item_maintenance(self._tab_item_maint)
        except Exception as e:
            print("Error loading item maintenance subtab:", e)

        try:
            self._load_bo_customers(self._tab_customers)
        except Exception as e:
            print("Error loading customers subtab:", e)

        try:
            self._load_bo_operators(self._tab_operators)
        except Exception as e:
            print("Error loading operators subtab:", e)

        try:
            self._load_bo_store_config(self._tab_store_cfg)
        except Exception as e:
            print("Error loading store config subtab:", e)

    # ── 1. ITEM MAINTENANCE SUB-TAB ──────────────────────────────────────────
    def _load_bo_item_maintenance(self, parent):
        split = ctk.CTkFrame(parent, fg_color="transparent")
        split.pack(fill="both", expand=True)

        # Left: Form (Width ~380)
        form_card = ctk.CTkFrame(split, fg_color="#1E293B", corner_radius=8, width=380)
        form_card.pack(side="left", fill="y", padx=(0, 8), pady=4)
        form_card.pack_propagate(False)

        ctk.CTkLabel(form_card, text="📝 Formulario de Artículo", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=12, pady=(10, 6))

        self._bo_editing_prod_id = None

        # Form fields
        fields_frame = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=8, pady=2)

        ctk.CTkLabel(fields_frame, text="Código de Barras", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_bo_barcode = ctk.CTkEntry(fields_frame, placeholder_text="Ej: 750100000099", height=32)
        self._ent_bo_barcode.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Nombre del Artículo", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_bo_nombre = ctk.CTkEntry(fields_frame, placeholder_text="Ej: Aceite de Oliva 500ml", height=32)
        self._ent_bo_nombre.pack(fill="x", pady=(0, 6))

        # Department & Subdepartment Dropdowns
        ctk.CTkLabel(fields_frame, text="Departamento", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        depts = DepartmentModel.get_all()
        dept_names = [d["nombre"] for d in depts] if depts else ["General"]
        self._cmb_bo_dept = ctk.CTkComboBox(fields_frame, values=dept_names, height=30, command=self._on_bo_dept_changed)
        self._cmb_bo_dept.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Sub-departamento", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._cmb_bo_subdept = ctk.CTkComboBox(fields_frame, values=["General"], height=30)
        self._cmb_bo_subdept.pack(fill="x", pady=(0, 6))

        self._update_bo_subdepts_dropdown()

        # Costs and Prices
        row_prices = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row_prices.pack(fill="x", pady=2)

        c1 = ctk.CTkFrame(row_prices, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkLabel(c1, text="Precio Costo (RD$)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_costo = ctk.CTkEntry(c1, placeholder_text="0.00", height=32)
        self._ent_bo_costo.pack(fill="x")

        c2 = ctk.CTkFrame(row_prices, fg_color="transparent")
        c2.pack(side="left", fill="x", expand=True, padx=(4, 0))
        ctk.CTkLabel(c2, text="Precio Venta (RD$)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_venta = ctk.CTkEntry(c2, placeholder_text="0.00", height=32)
        self._ent_bo_venta.pack(fill="x")

        # Stocks
        row_stock = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row_stock.pack(fill="x", pady=4)

        s1 = ctk.CTkFrame(row_stock, fg_color="transparent")
        s1.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkLabel(s1, text="Stock Actual (UD)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_stock = ctk.CTkEntry(s1, placeholder_text="0", height=32)
        self._ent_bo_stock.pack(fill="x")

        s2 = ctk.CTkFrame(row_stock, fg_color="transparent")
        s2.pack(side="left", fill="x", expand=True, padx=(4, 0))
        ctk.CTkLabel(s2, text="Stock Mínimo", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_bo_min_stock = ctk.CTkEntry(s2, placeholder_text="5", height=32)
        self._ent_bo_min_stock.pack(fill="x")

        # Dedicated full-width Unit of Measure row
        ctk.CTkLabel(fields_frame, text="Unidad de Medida", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._cmb_bo_unidad = ctk.CTkComboBox(
            fields_frame,
            values=["UD - Unidad", "LB - Libra", "KG - Kilogramo", "PQT - Paquete", "CJ - Caja", "GL - Galón", "LT - Litro", "SAC - Saco"],
            height=32
        )
        self._cmb_bo_unidad.set("UD - Unidad")
        self._cmb_bo_unidad.pack(fill="x", pady=(0, 6))

        # Checkbox Flags
        self._chk_bo_descontable = ctk.CTkCheckBox(fields_frame, text="Permite Descuentos en POS", font=ctk.CTkFont(size=11))
        self._chk_bo_descontable.select()
        self._chk_bo_descontable.pack(anchor="w", pady=(8, 4))

        self._chk_bo_precio_manual = ctk.CTkCheckBox(fields_frame, text="Precio Manual al Cobrar", font=ctk.CTkFont(size=11))
        self._chk_bo_precio_manual.pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Estado del Artículo", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._cmb_bo_estado = ctk.CTkComboBox(fields_frame, values=["Activo", "Inactivo", "Descontinuado"], height=30)
        self._cmb_bo_estado.set("Activo")
        self._cmb_bo_estado.pack(fill="x", pady=(0, 10))

        # Save & Clear Buttons
        btn_box = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_box.pack(fill="x", padx=8, pady=8)

        self._btn_save_bo_prod = ctk.CTkButton(
            btn_box, text="💾 Guardar Artículo", fg_color="#2563EB", hover_color="#1D4ED8",
            font=ctk.CTkFont(size=11, weight="bold"), command=self._save_bo_product
        )
        self._btn_save_bo_prod.pack(side="left", fill="x", expand=True, padx=(0, 2))

        ctk.CTkButton(
            btn_box, text="🧹 Limpiar", fg_color="#334155", hover_color="#475569", width=75,
            font=ctk.CTkFont(size=11), command=self._clear_bo_prod_form
        ).pack(side="right", padx=(2, 0))

        # Right: Product Table & Department Manager
        right_card = ctk.CTkFrame(split, fg_color="#16161F", corner_radius=8, border_width=1, border_color="#1E293B")
        right_card.pack(side="right", fill="both", expand=True)

        top_ctrl = ctk.CTkFrame(right_card, fg_color="transparent", height=38)
        top_ctrl.pack(fill="x", padx=8, pady=6)

        self._ent_bo_search_prod = ctk.CTkEntry(top_ctrl, placeholder_text="🔍 Buscar por nombre o código de barras...", width=320, height=32)
        self._ent_bo_search_prod.pack(side="left", padx=4)

        self._bo_search_timer = None
        def _debounced_bo_search(e):
            if getattr(self, '_bo_search_timer', None):
                self.after_cancel(self._bo_search_timer)
            self._bo_search_timer = self.after(250, self._render_bo_products_table)

        self._ent_bo_search_prod.bind("<KeyRelease>", _debounced_bo_search)

        ctk.CTkButton(
            top_ctrl, text="➕ Deptos / Sub-deptos", fg_color="#0F766E", hover_color="#0D6B63",
            font=ctk.CTkFont(size=11, weight="bold"), height=32,
            command=self._open_dept_manager_modal
        ).pack(side="right", padx=4)

        # Products Scrollable Table
        self._bo_prods_table_frame = ctk.CTkScrollableFrame(right_card, fg_color="transparent")
        self._bo_prods_table_frame.pack(fill="both", expand=True, padx=6, pady=4)

        self._render_bo_products_table(force_reload=True)

    def _on_bo_dept_changed(self, choice):
        self._update_bo_subdepts_dropdown()

    def _update_bo_subdepts_dropdown(self):
        dept_name = self._cmb_bo_dept.get()
        depts = DepartmentModel.get_all()
        dept_id = None
        for d in depts:
            if d["nombre"] == dept_name:
                dept_id = d["id"]
                break
        if dept_id:
            subdepts = SubDepartmentModel.get_by_department(dept_id)
            names = [sd["nombre"] for sd in subdepts] if subdepts else ["General"]
        else:
            names = ["General"]
        self._cmb_bo_subdept.configure(values=names)
        self._cmb_bo_subdept.set(names[0])

    def _clear_bo_prod_form(self):
        self._bo_editing_prod_id = None
        self._ent_bo_barcode.delete(0, "end")
        self._ent_bo_nombre.delete(0, "end")
        self._ent_bo_costo.delete(0, "end")
        self._ent_bo_venta.delete(0, "end")
        self._ent_bo_stock.delete(0, "end")
        self._ent_bo_min_stock.delete(0, "end")
        self._cmb_bo_unidad.set("UD - Unidad")
        self._chk_bo_descontable.select()
        self._chk_bo_precio_manual.deselect()
        if hasattr(self, '_cmb_bo_estado'):
            self._cmb_bo_estado.set("Activo")
        if hasattr(self, '_btn_save_bo_prod'):
            self._btn_save_bo_prod.configure(text="💾 Guardar Artículo", fg_color="#2563EB", hover_color="#1D4ED8")

    def _save_bo_product(self):
        barcode = self._ent_bo_barcode.get().strip()
        nombre = self._ent_bo_nombre.get().strip()

        if not barcode or not nombre:
            messagebox.showerror("Error", "El código de barras y el nombre del artículo son obligatorios.")
            return

        try:
            costo = float(self._ent_bo_costo.get().strip() or 0)
            venta = float(self._ent_bo_venta.get().strip() or 0)
            stock = int(self._ent_bo_stock.get().strip() or 0)
            min_stock = int(self._ent_bo_min_stock.get().strip() or 5)
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos para costos, precios y stocks.")
            return

        subdept_name = self._cmb_bo_subdept.get()
        subdepts = SubDepartmentModel.get_all()
        subdept_id = None
        for sd in subdepts:
            if sd["nombre"] == subdept_name:
                subdept_id = sd["id"]
                break

        data = {
            "id": self._bo_editing_prod_id,
            "codigo_barras": barcode,
            "nombre": nombre,
            "subdepartamento_id": subdept_id,
            "precio_costo": costo,
            "precio_venta": venta,
            "stock_actual": stock,
            "stock_minimo": min_stock,
            "es_descontable": bool(self._chk_bo_descontable.get()),
            "precio_manual": bool(self._chk_bo_precio_manual.get()),
            "unidad_medida": self._cmb_bo_unidad.get().split(" - ")[0] if hasattr(self, "_cmb_bo_unidad") else "UD",
            "estado": self._cmb_bo_estado.get() if hasattr(self, '_cmb_bo_estado') else "Activo"
        }

        try:
            ProductModel.save_product(data)
            action_txt = "actualizado" if self._bo_editing_prod_id else "guardado"
            messagebox.showinfo("Éxito", f"¡Artículo '{nombre}' {action_txt} exitosamente!")
            self._clear_bo_prod_form()
            self._render_bo_products_table(force_reload=True)
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))

    def _render_bo_products_table(self, force_reload=False):
        search = self._ent_bo_search_prod.get().strip() if hasattr(self, '_ent_bo_search_prod') else ""
        prods = ProductModel.search_live(search, limit=100 if search else 20)

        # Destroy existing cards and rebuild
        for widget in self._bo_prods_table_frame.winfo_children():
            widget.destroy()

        if not prods:
            ctk.CTkLabel(self._bo_prods_table_frame, text="No hay artículos registrados.", text_color="#94A3B8", font=ctk.CTkFont(size=12)).pack(pady=30)
            return

        for p in prods:
            card = ctk.CTkFrame(
                self._bo_prods_table_frame,
                fg_color="#0F172A",
                corner_radius=8,
                border_width=1,
                border_color="#334155"
            )
            card._search_text = f"{p['nombre']} {p['codigo_barras']} {p.get('departamento_nombre', '')} {p.get('subdepartamento_nombre', '')}".lower()
            card.pack(fill="x", pady=4, padx=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            # Left side: Product Info & Badges
            left_box = ctk.CTkFrame(inner, fg_color="transparent")
            left_box.pack(side="left", fill="both", expand=True)

            subdep_txt = p.get("subdepartamento_nombre") or "General"
            dept_txt = p.get("departamento_nombre") or "General"
            unid_txt = p.get("unidad_medida") or "UD"
            estado_txt = p.get("estado") or "Activo"

            if estado_txt == "Inactivo":
                st_fg, st_bg = "#F59E0B", "#451A03"
            elif estado_txt == "Descontinuado":
                st_fg, st_bg = "#EF4444", "#450A0A"
            else:
                st_fg, st_bg = "#10B981", "#064E3B"

            header_frame = ctk.CTkFrame(left_box, fg_color="transparent")
            header_frame.pack(fill="x", anchor="w")

            st_pill = ctk.CTkFrame(header_frame, fg_color=st_bg, corner_radius=4)
            st_pill.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(st_pill, text=f" ● {estado_txt} ", font=ctk.CTkFont(size=10, weight="bold"), text_color=st_fg).pack(padx=4, pady=1)

            ctk.CTkLabel(
                header_frame,
                text=f"{p['nombre']}   (Cód: {p['codigo_barras']})",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#F8FAFC",
                anchor="w"
            ).pack(side="left")

            desc_badge = " [Desc. OK]" if p.get("es_descontable", 1) else " [Sin Desc.]"
            man_badge = " [P.Manual]" if p.get("precio_manual", 0) else ""

            ctk.CTkLabel(
                left_box,
                text=f"📂 {dept_txt} ➔ {subdep_txt}   •   Unid: {unid_txt}{desc_badge}{man_badge}",
                font=ctk.CTkFont(size=11),
                text_color="#94A3B8",
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))

            # Right side: Prices & Action Buttons (Stacked rows to prevent cut-off)
            right_box = ctk.CTkFrame(inner, fg_color="transparent")
            right_box.pack(side="right", padx=(10, 0))

            info_row = ctk.CTkFrame(right_box, fg_color="transparent")
            info_row.pack(anchor="e", pady=(0, 4))

            cost_txt = f"Costo: RD${float(p['precio_costo']):.2f}"
            price_txt = f"Venta: RD${float(p['precio_venta']):.2f}"
            ctk.CTkLabel(
                info_row,
                text=f"{cost_txt}  |  {price_txt}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#38BDF8"
            ).pack(side="left", padx=(0, 8))

            stock_val = p.get('stock_actual') if p.get('stock_actual') is not None else 0
            stock_min = p.get('stock_minimo') if p.get('stock_minimo') is not None else 5
            stock_color = "#10B981" if stock_val > stock_min else "#EF4444"
            stock_bg = "#064E3B" if stock_val > stock_min else "#7F1D1D"

            stk_frame = ctk.CTkFrame(info_row, fg_color=stock_bg, corner_radius=6)
            stk_frame.pack(side="left")
            ctk.CTkLabel(
                stk_frame,
                text=f"Stock: {stock_val}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=stock_color
            ).pack(padx=6, pady=2)

            act_row = ctk.CTkFrame(right_box, fg_color="transparent")
            act_row.pack(anchor="e")

            ctk.CTkButton(
                act_row,
                text="✏️ Editar",
                width=80,
                height=28,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                command=lambda prod=p: self._edit_bo_prod(prod)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                act_row,
                text="🗑️ Eliminar",
                width=85,
                height=28,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda pid=p["id"]: self._delete_bo_prod(pid)
            ).pack(side="left", padx=3)


    def _edit_bo_prod(self, p):
        self._bo_editing_prod_id = p["id"]
        self._ent_bo_barcode.delete(0, "end")
        self._ent_bo_barcode.insert(0, p["codigo_barras"])
        self._ent_bo_nombre.delete(0, "end")
        self._ent_bo_nombre.insert(0, p["nombre"])
        self._ent_bo_costo.delete(0, "end")
        self._ent_bo_costo.insert(0, str(p["precio_costo"]))
        self._ent_bo_venta.delete(0, "end")
        self._ent_bo_venta.insert(0, str(p["precio_venta"]))
        self._ent_bo_stock.delete(0, "end")
        self._ent_bo_stock.insert(0, str(p["stock_actual"]))
        self._ent_bo_min_stock.delete(0, "end")
        u_code = p.get("unidad_medida") or "UD"
        for u_val in ["UD - Unidad", "LB - Libra", "KG - Kilogramo", "PQT - Paquete", "CJ - Caja", "GL - Galón", "LT - Litro", "SAC - Saco"]:
            if u_val.startswith(u_code):
                self._cmb_bo_unidad.set(u_val)
                break
        else:
            self._cmb_bo_unidad.set("UD - Unidad")

        if p.get("es_descontable", 1):
            self._chk_bo_descontable.select()
        else:
            self._chk_bo_descontable.deselect()

        if p.get("precio_manual", 0):
            self._chk_bo_precio_manual.select()
        else:
            self._chk_bo_precio_manual.deselect()

        if p.get("departamento_nombre"):
            self._cmb_bo_dept.set(p["departamento_nombre"])
            self._update_bo_subdepts_dropdown()

        if p.get("subdepartamento_nombre"):
            self._cmb_bo_subdept.set(p["subdepartamento_nombre"])

        if hasattr(self, '_cmb_bo_estado'):
            self._cmb_bo_estado.set(p.get("estado") or "Activo")

        if hasattr(self, '_btn_save_bo_prod'):
            self._btn_save_bo_prod.configure(text=f"✏️ Actualizar Artículo #{p['id']}", fg_color="#10B981", hover_color="#059669")

    def _delete_bo_prod(self, prod_id):
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de eliminar este artículo del sistema?"):
            ProductModel.delete_product(prod_id)
            self._render_bo_products_table(force_reload=True)

    # ── 2. CUSTOMERS & VENDORS SUB-TAB ───────────────────────────────────────
    def _load_bo_customers(self, parent):
        split = ctk.CTkFrame(parent, fg_color="transparent")
        split.pack(fill="both", expand=True)

        form_card = ctk.CTkFrame(split, fg_color="#1E293B", corner_radius=8, width=370)
        form_card.pack(side="left", fill="y", padx=(0, 8), pady=4)
        form_card.pack_propagate(False)

        ctk.CTkLabel(form_card, text="👥 Registro de Cliente / Proveedor", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=12, pady=(10, 6))

        self._bo_editing_cust_id = None
        fields_frame = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=8, pady=2)

        ctk.CTkLabel(fields_frame, text="Código Cliente/Suplidor", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_cli_codigo = ctk.CTkEntry(fields_frame, placeholder_text="Ej: CLI-0004", height=32)
        self._ent_cli_codigo.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Nombre / Razón Social", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_cli_nombre = ctk.CTkEntry(fields_frame, placeholder_text="Ej: Comercial El Sol S.R.L.", height=32)
        self._ent_cli_nombre.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="RNC / Cédula", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_cli_rnc = ctk.CTkEntry(fields_frame, placeholder_text="131-00000-0", height=32)
        self._ent_cli_rnc.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Tipo de Entidad", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._cmb_cli_tipo = ctk.CTkComboBox(fields_frame, values=["General", "Wholesale/Mayorista", "Vendedor/Suplidor"], height=32)
        self._cmb_cli_tipo.set("General")
        self._cmb_cli_tipo.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Teléfono", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_cli_tel = ctk.CTkEntry(fields_frame, placeholder_text="(809) 000-0000", height=32)
        self._ent_cli_tel.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Email", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_cli_email = ctk.CTkEntry(fields_frame, placeholder_text="contacto@cliente.com", height=32)
        self._ent_cli_email.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Dirección", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_cli_dir = ctk.CTkEntry(fields_frame, placeholder_text="Calle Principal #10", height=32)
        self._ent_cli_dir.pack(fill="x", pady=(0, 6))

        row_desc = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row_desc.pack(fill="x", pady=2)

        d1 = ctk.CTkFrame(row_desc, fg_color="transparent")
        d1.pack(side="left", fill="x", expand=True, padx=(0, 2))
        ctk.CTkLabel(d1, text="% Descuento Mayorista", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_cli_desc = ctk.CTkEntry(d1, placeholder_text="0.0", height=32)
        self._ent_cli_desc.insert(0, "0.0")
        self._ent_cli_desc.pack(fill="x")

        d2 = ctk.CTkFrame(row_desc, fg_color="transparent")
        d2.pack(side="left", fill="x", expand=True, padx=(2, 0))
        ctk.CTkLabel(d2, text="Límite Crédito (RD$)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w")
        self._ent_cli_limite = ctk.CTkEntry(d2, placeholder_text="0.00", height=32)
        self._ent_cli_limite.insert(0, "0.00")
        self._ent_cli_limite.pack(fill="x")

        btn_box = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_box.pack(fill="x", padx=8, pady=8)

        ctk.CTkButton(
            btn_box, text="💾 Guardar Cliente", fg_color="#2563EB", hover_color="#1D4ED8",
            font=ctk.CTkFont(size=11, weight="bold"), command=self._save_bo_customer
        ).pack(side="left", fill="x", expand=True, padx=(0, 2))

        ctk.CTkButton(
            btn_box, text="🧹 Limpiar", fg_color="#334155", hover_color="#475569", width=75,
            font=ctk.CTkFont(size=11), command=self._clear_bo_cust_form
        ).pack(side="right", padx=(2, 0))

        # Right: Table
        right_card = ctk.CTkFrame(split, fg_color="#16161F", corner_radius=8, border_width=1, border_color="#1E293B")
        right_card.pack(side="right", fill="both", expand=True)

        top_ctrl = ctk.CTkFrame(right_card, fg_color="transparent", height=38)
        top_ctrl.pack(fill="x", padx=8, pady=6)

        self._ent_bo_search_cust = ctk.CTkEntry(top_ctrl, placeholder_text="🔍 Buscar cliente por nombre, RNC o código...", width=360, height=32)
        self._ent_bo_search_cust.pack(side="left", padx=4)
        self._ent_bo_search_cust.bind("<KeyRelease>", lambda e: self._render_bo_customers_table())

        self._bo_cust_table_frame = ctk.CTkScrollableFrame(right_card, fg_color="transparent")
        self._bo_cust_table_frame.pack(fill="both", expand=True, padx=6, pady=4)

        self._render_bo_customers_table()

    def _clear_bo_cust_form(self):
        self._bo_editing_cust_id = None
        self._ent_cli_codigo.delete(0, "end")
        self._ent_cli_nombre.delete(0, "end")
        self._ent_cli_rnc.delete(0, "end")
        self._ent_cli_tel.delete(0, "end")
        self._ent_cli_email.delete(0, "end")
        self._ent_cli_dir.delete(0, "end")
        self._ent_cli_desc.delete(0, "end")
        self._ent_cli_desc.insert(0, "0.0")
        self._ent_cli_limite.delete(0, "end")
        self._ent_cli_limite.insert(0, "0.00")
        self._cmb_cli_tipo.set("General")

    def _save_bo_customer(self):
        cod = self._ent_cli_codigo.get().strip()
        nom = self._ent_cli_nombre.get().strip()
        if not cod or not nom:
            messagebox.showerror("Error", "El código y el nombre del cliente son obligatorios.")
            return

        rnc = self._ent_cli_rnc.get().strip()
        tipo = self._cmb_cli_tipo.get()
        tel = self._ent_cli_tel.get().strip()
        email = self._ent_cli_email.get().strip()
        direccion = self._ent_cli_dir.get().strip()

        try:
            desc = float(self._ent_cli_desc.get().strip() or 0)
            limite = float(self._ent_cli_limite.get().strip() or 0)
        except ValueError:
            desc, limite = 0.0, 0.0

        try:
            if self._bo_editing_cust_id:
                CustomerModel.update(self._bo_editing_cust_id, nom, rnc, tipo, tel, email, direccion, desc, limite)
            else:
                CustomerModel.create(cod, nom, rnc, tipo, tel, email, direccion, desc, limite)
            messagebox.showinfo("Éxito", f"¡Cliente '{nom}' guardado exitosamente!")
            self._clear_bo_cust_form()
            self._render_bo_customers_table()
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))

    def _render_bo_customers_table(self):
        for widget in self._bo_cust_table_frame.winfo_children():
            widget.destroy()

        search = self._ent_bo_search_cust.get().strip()
        custs = CustomerModel.get_all(search_term=search)

        headers = ["Código", "Nombre / Razón Social", "RNC / Cédula", "Tipo Entidad", "Teléfono", "% Desc.", "Acciones"]
        cols_w  = [100,      210,                     130,            130,           110,        60,        90]

        head_row = ctk.CTkFrame(self._bo_cust_table_frame, fg_color="#1F2937", height=26)
        head_row.pack(fill="x", pady=(0, 2))
        head_row.pack_propagate(False)

        for h, w in zip(headers, cols_w):
            ctk.CTkLabel(head_row, text=h, font=ctk.CTkFont(size=10, weight="bold"), text_color="#93C5FD", width=w).pack(side="left", padx=2)

        if not custs:
            ctk.CTkLabel(self._bo_cust_table_frame, text="No hay clientes o suplidores registrados.", text_color="#475569", font=ctk.CTkFont(size=11)).pack(pady=20)
            return

        for i, c in enumerate(custs):
            bg = "#111827" if i % 2 == 0 else "#0F172A"
            row = ctk.CTkFrame(self._bo_cust_table_frame, fg_color=bg, corner_radius=3, height=28)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            vals = [
                c.get("codigo", ""), c.get("nombre_razon_social", "")[:28],
                c.get("rnc_cedula", ""), c.get("tipo_cliente", ""),
                c.get("telefono", ""), f"{float(c.get('porcentaje_descuento', 0)):.1f}%"
            ]

            for val, w in zip(vals, cols_w[:-1]):
                ctk.CTkLabel(row, text=str(val), font=ctk.CTkFont(size=10), text_color="#CBD5E1", width=w).pack(side="left", padx=2)

            act_box = ctk.CTkFrame(row, fg_color="transparent", width=cols_w[-1])
            act_box.pack(side="left", padx=2)

            ctk.CTkButton(
                act_box, text="✏️", width=36, height=22, fg_color="#3B82F6", hover_color="#2563EB",
                command=lambda cust=c: self._edit_bo_cust(cust)
            ).pack(side="left", padx=1)

            ctk.CTkButton(
                act_box, text="❌", width=36, height=22, fg_color="#EF4444", hover_color="#DC2626",
                command=lambda cid=c["id"]: self._delete_bo_cust(cid)
            ).pack(side="left", padx=1)

    def _edit_bo_cust(self, c):
        self._bo_editing_cust_id = c["id"]
        self._ent_cli_codigo.delete(0, "end")
        self._ent_cli_codigo.insert(0, c.get("codigo", ""))
        self._ent_cli_nombre.delete(0, "end")
        self._ent_cli_nombre.insert(0, c.get("nombre_razon_social", ""))
        self._ent_cli_rnc.delete(0, "end")
        self._ent_cli_rnc.insert(0, c.get("rnc_cedula", ""))
        self._cmb_cli_tipo.set(c.get("tipo_cliente", "General"))
        self._ent_cli_tel.delete(0, "end")
        self._ent_cli_tel.insert(0, c.get("telefono", ""))
        self._ent_cli_email.delete(0, "end")
        self._ent_cli_email.insert(0, c.get("email", ""))
        self._ent_cli_dir.delete(0, "end")
        self._ent_cli_dir.insert(0, c.get("direccion", ""))
        self._ent_cli_desc.delete(0, "end")
        self._ent_cli_desc.insert(0, str(c.get("porcentaje_descuento", 0)))
        self._ent_cli_limite.delete(0, "end")
        self._ent_cli_limite.insert(0, str(c.get("limite_credito", 0)))

    def _delete_bo_cust(self, cust_id):
        if messagebox.askyesno("Confirmar Eliminación", "¿Desea eliminar este cliente/suplidor?"):
            CustomerModel.delete(cust_id)
            self._render_bo_customers_table()

    # ── 3. OPERATORS & PERMISSIONS SUB-TAB (RBAC) ────────────────────────────
    def _load_bo_operators(self, parent):
        split = ctk.CTkFrame(parent, fg_color="transparent")
        split.pack(fill="both", expand=True)

        # Left: Operator Creation Form (Width 360)
        form_card = ctk.CTkFrame(split, fg_color="#1E293B", corner_radius=8, width=360)
        form_card.pack(side="left", fill="y", padx=(0, 8), pady=4)
        form_card.pack_propagate(False)

        ctk.CTkLabel(form_card, text="🔒 Registro de Operador (PIN Opcional)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=12, pady=(10, 6))

        self._bo_editing_user_id = None
        fields_frame = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=8, pady=2)

        ctk.CTkLabel(fields_frame, text="Usuario / ID (1 a 6 dígitos numéricos)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_usr_username = ctk.CTkEntry(fields_frame, placeholder_text="Ej: 200002 o 1", height=32)
        self._ent_usr_username.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Contraseña / PIN (Opcional, 1 a 6 dígitos)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_usr_password = ctk.CTkEntry(fields_frame, placeholder_text="Opcional (Dejar en blanco si no usa PIN)", show="*", height=32)
        self._ent_usr_password.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Nombre Completo del Empleado", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._ent_usr_nombre = ctk.CTkEntry(fields_frame, placeholder_text="Ej: María Rodríguez", height=32)
        self._ent_usr_nombre.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(fields_frame, text="Rol del Operador", font=ctk.CTkFont(size=10, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(4, 1))
        self._cmb_usr_rol = ctk.CTkComboBox(
            fields_frame, 
            values=["Programador", "Propietario", "Manager", "Supervisor", "Almacen", "Cajero"], 
            height=32
        )
        self._cmb_usr_rol.set("Cajero")
        self._cmb_usr_rol.pack(fill="x", pady=(0, 8))

        self._chk_usr_activo = ctk.CTkCheckBox(fields_frame, text="Usuario Activo", font=ctk.CTkFont(size=11))
        self._chk_usr_activo.select()
        self._chk_usr_activo.pack(anchor="w", pady=(0, 10))

        btn_box = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_box.pack(fill="x", padx=8, pady=8)

        ctk.CTkButton(
            btn_box, text="💾 Guardar Operador", fg_color="#2563EB", hover_color="#1D4ED8",
            font=ctk.CTkFont(size=11, weight="bold"), command=self._save_bo_operator
        ).pack(side="left", fill="x", expand=True, padx=(0, 2))

        ctk.CTkButton(
            btn_box, text="🧹 Limpiar", fg_color="#334155", hover_color="#475569", width=75,
            font=ctk.CTkFont(size=11), command=self._clear_bo_usr_form
        ).pack(side="right", padx=(2, 0))

        # Right: User Table & Permissions Matrix Panel
        right_split = ctk.CTkFrame(split, fg_color="transparent")
        right_split.pack(side="right", fill="both", expand=True)

        # Users Table Card (Top)
        u_card = ctk.CTkFrame(right_split, fg_color="#16161F", corner_radius=8, border_width=1, border_color="#1E293B", height=240)
        u_card.pack(fill="x", pady=(0, 6))
        u_card.pack_propagate(False)

        ctk.CTkLabel(u_card, text="  📋 Operadores Registrados (Seleccione para Configurar Permisos)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8B5CF6").pack(anchor="w", padx=10, pady=6)

        self._bo_users_table_frame = ctk.CTkScrollableFrame(u_card, fg_color="transparent")
        self._bo_users_table_frame.pack(fill="both", expand=True, padx=6, pady=2)

        # Permissions Matrix Card (Bottom)
        self._bo_perm_card = ctk.CTkFrame(right_split, fg_color="#16161F", corner_radius=8, border_width=1, border_color="#1E293B")
        self._bo_perm_card.pack(fill="both", expand=True)

        self._selected_perm_user = None
        self._perm_checkboxes = {}

        self._render_bo_operators_table()

    def _clear_bo_usr_form(self):
        self._bo_editing_user_id = None
        self._ent_usr_username.delete(0, "end")
        self._ent_usr_password.delete(0, "end")
        self._ent_usr_nombre.delete(0, "end")
        self._cmb_usr_rol.set("Cajero")
        self._chk_usr_activo.select()

    def _save_bo_operator(self):
        u = self._ent_usr_username.get().strip()
        p = self._ent_usr_password.get().strip()
        nom = self._ent_usr_nombre.get().strip()
        rol = self._cmb_usr_rol.get()
        activo = 1 if self._chk_usr_activo.get() else 0

        if not u or not nom:
            messagebox.showerror("Error", "El código de usuario y el nombre completo son obligatorios.")
            return

        try:
            if self._bo_editing_user_id:
                UserModel.update(self._bo_editing_user_id, p, nom, rol, activo)
            else:
                UserModel.create(u, p, nom, rol)
            messagebox.showinfo("Éxito", f"¡Operador '{nom}' guardado exitosamente!")
            self._clear_bo_usr_form()
            self._render_bo_operators_table()
        except Exception as e:
            messagebox.showerror("Error al Guardar Operador", str(e))

    def _render_bo_operators_table(self):
        for widget in self._bo_users_table_frame.winfo_children():
            widget.destroy()

        users = UserModel.get_all()
        headers = ["ID", "Usuario (PIN)", "Nombre Completo", "Rol", "Estado", "Acciones"]
        cols_w  = [45,   110,             180,               100,   70,       140]

        head_row = ctk.CTkFrame(self._bo_users_table_frame, fg_color="#1F2937", height=24)
        head_row.pack(fill="x", pady=(0, 2))
        head_row.pack_propagate(False)

        for h, w in zip(headers, cols_w):
            ctk.CTkLabel(head_row, text=h, font=ctk.CTkFont(size=10, weight="bold"), text_color="#93C5FD", width=w).pack(side="left", padx=2)

        for i, u in enumerate(users):
            bg = "#1E293B" if self._selected_perm_user and self._selected_perm_user["id"] == u["id"] else ("#111827" if i % 2 == 0 else "#0F172A")
            row = ctk.CTkFrame(self._bo_users_table_frame, fg_color=bg, corner_radius=3, height=26)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            vals = [str(u["id"]), u["username"], u["nombre_completo"][:22], u["rol"], "Activo" if u["activo"] else "Inactivo"]
            for val, w in zip(vals, cols_w[:-1]):
                lbl = ctk.CTkLabel(row, text=str(val), font=ctk.CTkFont(size=10), text_color="#CBD5E1", width=w)
                lbl.pack(side="left", padx=2)
                lbl.bind("<Button-1>", lambda e, user=u: self._select_user_for_perms(user))

            row.bind("<Button-1>", lambda e, user=u: self._select_user_for_perms(user))

            btn_box = ctk.CTkFrame(row, fg_color="transparent", width=cols_w[-1])
            btn_box.pack(side="left", padx=2)
            ctk.CTkButton(
                btn_box, text="✏️ Editar", width=62, height=22, fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda user=u: self._edit_bo_user(user)
            ).pack(side="left", padx=1)
            ctk.CTkButton(
                btn_box, text="🗑️ Eliminar", width=70, height=22, fg_color="#DC2626", hover_color="#B91C1C", font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda uid=u["id"]: self._delete_bo_user(uid)
            ).pack(side="left", padx=1)

        if not self._selected_perm_user and users:
            self._select_user_for_perms(users[0])

    def _edit_bo_user(self, u):
        self._bo_editing_user_id = u["id"]
        self._ent_usr_username.delete(0, "end")
        self._ent_usr_username.insert(0, u["username"])
        self._ent_usr_password.delete(0, "end")
        self._ent_usr_nombre.delete(0, "end")
        self._ent_usr_nombre.insert(0, u["nombre_completo"])
        self._cmb_usr_rol.set(u["rol"])
        if u["activo"]:
            self._chk_usr_activo.select()
        else:
            self._chk_usr_activo.deselect()

    def _delete_bo_user(self, user_id):
        if self.current_user and self.current_user["id"] == user_id:
            messagebox.showerror("Error", "No puede eliminar la cuenta con la que ha iniciado sesión actualmente.")
            return
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de eliminar este operador del sistema?"):
            try:
                UserModel.delete(user_id)
                messagebox.showinfo("Éxito", "Operador eliminado correctamente.")
                self._render_bo_operators_table()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el operador: {e}")

    def _select_user_for_perms(self, user):
        self._selected_perm_user = user
        self._render_bo_operators_table()
        self._render_permissions_matrix()

    def _render_permissions_matrix(self):
        for widget in self._bo_perm_card.winfo_children():
            widget.destroy()

        if not self._selected_perm_user:
            ctk.CTkLabel(self._bo_perm_card, text="Seleccione un operador para configurar sus permisos.", text_color="#475569").pack(pady=30)
            return

        u = self._selected_perm_user
        hdr = ctk.CTkFrame(self._bo_perm_card, fg_color="#1E293B", corner_radius=0, height=34)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text=f"  ⚙️ MATRIZ DE PERMISOS DINÁMICOS — OPERADOR: {u['nombre_completo']} ({u['username']}) | ROL: {u['rol']}",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8"
        ).pack(side="left", pady=6)

        user_perms = UserModel.get_permissions(u["id"])
        matrix_scroll = ctk.CTkScrollableFrame(self._bo_perm_card, fg_color="transparent")
        matrix_scroll.pack(fill="both", expand=True, padx=10, pady=6)

        self._perm_checkboxes = {}
        for mod_key, mod_title in ALL_MODULES:
            row = ctk.CTkFrame(matrix_scroll, fg_color="#0F172A", corner_radius=4, height=32)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # Check if permitted by custom setting or by role default
            is_checked = user_perms.get(mod_key, UserModel.has_permission(u, mod_key))

            chk = ctk.CTkCheckBox(row, text=mod_title, font=ctk.CTkFont(size=11, weight="bold"))
            if is_checked:
                chk.select()
            else:
                chk.deselect()
            chk.pack(side="left", padx=12, pady=6)
            self._perm_checkboxes[mod_key] = chk

        btn_bar = ctk.CTkFrame(self._bo_perm_card, fg_color="transparent", height=40)
        btn_bar.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(
            btn_bar, text="💾 Guardar Permisos del Operador", fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(size=12, weight="bold"), height=32,
            command=self._save_user_permissions_matrix
        ).pack(side="right")

    def _save_user_permissions_matrix(self):
        if not self._selected_perm_user:
            return
        perm_map = {mod_key: bool(chk.get()) for mod_key, chk in self._perm_checkboxes.items()}
        UserModel.save_permissions(self._selected_perm_user["id"], perm_map)
        messagebox.showinfo("Permisos Guardados", f"¡Matriz de permisos de '{self._selected_perm_user['nombre_completo']}' actualizada exitosamente!")

    # ── 4. STORE CONFIG SUB-TAB ──────────────────────────────────────────────
    def _load_bo_store_config(self, parent):
        box = ctk.CTkFrame(parent, fg_color="#1E293B", corner_radius=8, width=540)
        box.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(box, text="🏬 CONFIGURACIÓN GENERAL DE LA EMPRESA / TIENDA", font=ctk.CTkFont(size=13, weight="bold"), text_color="#38BDF8").pack(anchor="w", padx=20, pady=(15, 10))

        cfg = CompanyModel.get()

        f_frame = ctk.CTkFrame(box, fg_color="transparent")
        f_frame.pack(fill="both", expand=True, padx=20, pady=5)

        ctk.CTkLabel(f_frame, text="RNC / Cédula de la Empresa", font=ctk.CTkFont(size=11, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
        self._ent_cfg_rnc = ctk.CTkEntry(f_frame, width=450, height=34)
        self._ent_cfg_rnc.insert(0, cfg.get("rnc", ""))
        self._ent_cfg_rnc.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(f_frame, text="Nombre Comercial", font=ctk.CTkFont(size=11, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
        self._ent_cfg_nombre = ctk.CTkEntry(f_frame, width=450, height=34)
        self._ent_cfg_nombre.insert(0, cfg.get("nombre_comercial", ""))
        self._ent_cfg_nombre.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(f_frame, text="Teléfono Principal", font=ctk.CTkFont(size=11, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
        self._ent_cfg_tel = ctk.CTkEntry(f_frame, width=450, height=34)
        self._ent_cfg_tel.insert(0, cfg.get("telefono", ""))
        self._ent_cfg_tel.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(f_frame, text="Dirección Física", font=ctk.CTkFont(size=11, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
        self._ent_cfg_dir = ctk.CTkEntry(f_frame, width=450, height=34)
        self._ent_cfg_dir.insert(0, cfg.get("direccion", ""))
        self._ent_cfg_dir.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(f_frame, text="Mensaje Pie de Factura", font=ctk.CTkFont(size=11, weight="bold"), text_color="#CBD5E1").pack(anchor="w", pady=(6, 2))
        self._ent_cfg_msg = ctk.CTkEntry(f_frame, width=450, height=34)
        self._ent_cfg_msg.insert(0, cfg.get("mensaje_factura", ""))
        self._ent_cfg_msg.pack(anchor="w", pady=(0, 12))

        ctk.CTkButton(
            box, text="💾 Guardar Datos de la Tienda", fg_color="#2563EB", hover_color="#1D4ED8",
            font=ctk.CTkFont(size=12, weight="bold"), height=38, width=220,
            command=self._save_company_config
        ).pack(anchor="w", padx=20, pady=(0, 20))

    def _save_company_config(self):
        rnc = self._ent_cfg_rnc.get().strip()
        nom = self._ent_cfg_nombre.get().strip()
        tel = self._ent_cfg_tel.get().strip()
        direccion = self._ent_cfg_dir.get().strip()
        msg = self._ent_cfg_msg.get().strip()

        try:
            CompanyModel.update(rnc, nom, tel, direccion, msg)
            messagebox.showinfo("Éxito", "¡Configuración de la empresa guardada exitosamente!")
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))

    def _open_dept_manager_modal(self):
        DeptSubdeptManagerModal(self)


# ==============================================================================
# MODAL PARA GESTIÓN DE DEPARTAMENTOS Y SUB-DEPARTAMENTOS
# ==============================================================================
class DeptSubdeptManagerModal(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gestionar Departamentos & Sub-departamentos")
        self.geometry("620x520")
        self.resizable(False, False)
        self.grab_set()

        hdr = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0, height=42)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="  ➕ GESTIÓN DE DEPARTAMENTOS Y SUB-DEPARTAMENTOS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8").pack(side="left", pady=8)

        tabview = ctk.CTkTabview(self, fg_color="#0F172A")
        tabview.pack(fill="both", expand=True, padx=10, pady=6)

        tab_d  = tabview.add("Departamentos")
        tab_sd = tabview.add("Sub-departamentos")

        # Depts tab
        d_box = ctk.CTkFrame(tab_d, fg_color="transparent")
        d_box.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(d_box, text="Nombre del Nuevo Departamento:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.ent_dept_name = ctk.CTkEntry(d_box, placeholder_text="Ej: Carnicería / Embutidos", height=34)
        self.ent_dept_name.pack(fill="x", pady=(2, 8))

        ctk.CTkButton(d_box, text="➕ Agregar Departamento", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(size=11, weight="bold"), command=self._add_dept).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(d_box, text="Departamentos Existentes:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#93C5FD").pack(anchor="w", pady=(4, 2))
        self.dept_scroll = ctk.CTkScrollableFrame(d_box, fg_color="#16161F", height=200)
        self.dept_scroll.pack(fill="both", expand=True)
        self._render_depts()

        # Sub-depts tab
        sd_box = ctk.CTkFrame(tab_sd, fg_color="transparent")
        sd_box.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(sd_box, text="Departamento Padre:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        depts = DepartmentModel.get_all()
        dept_names = [d["nombre"] for d in depts] if depts else ["General"]
        self.cmb_sd_dept = ctk.CTkComboBox(sd_box, values=dept_names, height=34)
        self.cmb_sd_dept.pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(sd_box, text="Nombre del Sub-departamento:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.ent_subdept_name = ctk.CTkEntry(sd_box, placeholder_text="Ej: Quesos Importados", height=34)
        self.ent_subdept_name.pack(fill="x", pady=(2, 8))

        ctk.CTkButton(sd_box, text="➕ Agregar Sub-departamento", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(size=11, weight="bold"), command=self._add_subdept).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(sd_box, text="Sub-departamentos Existentes:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#93C5FD").pack(anchor="w", pady=(4, 2))
        self.subdept_scroll = ctk.CTkScrollableFrame(sd_box, fg_color="#16161F", height=180)
        self.subdept_scroll.pack(fill="both", expand=True)
        self._render_subdepts()

    def _add_dept(self):
        nom = self.ent_dept_name.get().strip()
        if not nom:
            return
        try:
            DepartmentModel.create(nom)
            self.ent_dept_name.delete(0, "end")
            self._render_depts()
            self.parent._update_bo_subdepts_dropdown()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _render_depts(self):
        for w in self.dept_scroll.winfo_children():
            w.destroy()
        depts = DepartmentModel.get_all()
        for d in depts:
            r = ctk.CTkFrame(self.dept_scroll, fg_color="#0F172A", height=28)
            r.pack(fill="x", pady=1)
            r.pack_propagate(False)
            ctk.CTkLabel(r, text=f"ID: {d['id']} | {d['nombre']}", font=ctk.CTkFont(size=11)).pack(side="left", padx=8)

    def _add_subdept(self):
        dept_name = self.cmb_sd_dept.get()
        sd_name = self.ent_subdept_name.get().strip()
        if not sd_name:
            return
        depts = DepartmentModel.get_all()
        dept_id = None
        for d in depts:
            if d["nombre"] == dept_name:
                dept_id = d["id"]
                break
        if dept_id:
            try:
                SubDepartmentModel.create(dept_id, sd_name)
                self.ent_subdept_name.delete(0, "end")
                self._render_subdepts()
                self.parent._update_bo_subdepts_dropdown()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _render_subdepts(self):
        for w in self.subdept_scroll.winfo_children():
            w.destroy()
        subdepts = SubDepartmentModel.get_all()
        for sd in subdepts:
            r = ctk.CTkFrame(self.subdept_scroll, fg_color="#0F172A", height=28)
            r.pack(fill="x", pady=1)
            r.pack_propagate(False)
            ctk.CTkLabel(r, text=f"ID: {sd['id']} | {sd['nombre']} (Depto: {sd.get('departamento_nombre', '')})", font=ctk.CTkFont(size=11)).pack(side="left", padx=8)


if __name__ == "__main__":
    app = POSApp()
    app.mainloop()


# === Monkey-patch Back Office methods from FlipChartModal onto POSApp ===
POSApp.load_backoffice_tab = FlipChartModal.load_backoffice_tab
POSApp._load_bo_item_maintenance = FlipChartModal._load_bo_item_maintenance
POSApp._on_bo_dept_changed = FlipChartModal._on_bo_dept_changed
POSApp._update_bo_subdepts_dropdown = FlipChartModal._update_bo_subdepts_dropdown
POSApp._clear_bo_prod_form = FlipChartModal._clear_bo_prod_form
POSApp._save_bo_product = FlipChartModal._save_bo_product
POSApp._render_bo_products_table = FlipChartModal._render_bo_products_table
POSApp._edit_bo_prod = FlipChartModal._edit_bo_prod
POSApp._delete_bo_prod = FlipChartModal._delete_bo_prod
POSApp._load_bo_customers = FlipChartModal._load_bo_customers
POSApp._clear_bo_cust_form = FlipChartModal._clear_bo_cust_form
POSApp._save_bo_customer = FlipChartModal._save_bo_customer
POSApp._render_bo_customers_table = FlipChartModal._render_bo_customers_table
POSApp._edit_bo_cust = FlipChartModal._edit_bo_cust
POSApp._delete_bo_cust = FlipChartModal._delete_bo_cust
POSApp._load_bo_operators = FlipChartModal._load_bo_operators
POSApp._clear_bo_usr_form = FlipChartModal._clear_bo_usr_form
POSApp._save_bo_operator = FlipChartModal._save_bo_operator
POSApp._render_bo_operators_table = FlipChartModal._render_bo_operators_table
POSApp._edit_bo_user = FlipChartModal._edit_bo_user
POSApp._delete_bo_user = FlipChartModal._delete_bo_user
POSApp._select_user_for_perms = FlipChartModal._select_user_for_perms
POSApp._render_permissions_matrix = FlipChartModal._render_permissions_matrix
POSApp._save_user_permissions_matrix = FlipChartModal._save_user_permissions_matrix
POSApp._load_bo_store_config = FlipChartModal._load_bo_store_config
POSApp._save_company_config = FlipChartModal._save_company_config
POSApp._open_dept_manager_modal = FlipChartModal._open_dept_manager_modal

POSApp._build_backoffice_tab_ui = FlipChartModal._build_backoffice_tab_ui
