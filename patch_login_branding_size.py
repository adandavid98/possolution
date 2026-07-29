"""Patch app_gui.py to enlarge the left branding panel on the Login screen (logo, title, subtitle, badge)."""

print("=== ENLARGING LOGIN SCREEN BRANDING PANEL ===")

with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_left_branding = """        # Top Badge Label
        lbl_top_badge = ctk.CTkLabel(
            hero_content, 
            text=f"{com_name.upper()}, S.R.L.", 
            font=ctk.CTkFont(family="Poppins", size=13, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_top_badge.pack(pady=(0, 20))

        # Minimalist Logo Emblem
        logo_path = get_dynamic_logo_path()
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
            text=com_name, 
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
        lbl_sub_hero.pack(pady=(0, 0))"""

new_left_branding = """        # Top Badge Label
        lbl_top_badge = ctk.CTkLabel(
            hero_content, 
            text=f"{com_name.upper()}, S.R.L.", 
            font=ctk.CTkFont(family="Poppins", size=17, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_top_badge.pack(pady=(0, 25))

        # Minimalist Logo Emblem
        logo_path = get_dynamic_logo_path()
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                self.logo_ctk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(320, 320))
                
                lbl_img = ctk.CTkLabel(hero_content, image=self.logo_ctk, text="")
                lbl_img.image = self.logo_ctk
                lbl_img.pack(pady=(0, 25))
            except Exception as e:
                print("Error loading logo image:", e)

        # Main Title & Subtitle
        lbl_main_title = ctk.CTkLabel(
            hero_content, 
            text=com_name, 
            font=ctk.CTkFont(family="Poppins", size=30, weight="bold"),
            text_color="#F8FAFC",
            justify="center"
        )
        lbl_main_title.pack(pady=(0, 10))

        lbl_sub_hero = ctk.CTkLabel(
            hero_content, 
            text="Sistema Integral de Punto de Venta & Control de Inventario", 
            font=ctk.CTkFont(family="Inter", size=15),
            text_color="#94A3B8",
            justify="center"
        )
        lbl_sub_hero.pack(pady=(0, 0))"""

code = code.replace(old_left_branding, new_left_branding)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py successfully patched with enlarged login branding panel!")
