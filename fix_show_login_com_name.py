with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """        # 1. Left Panel (Branding / Minimalist Hero - 50% Width)
        left_hero = ctk.CTkFrame(main_login_box, fg_color="#1E293B", corner_radius=0)"""

replacement = """        # Fetch company info dynamically for branding
        comp_info = CompanyModel.get()
        com_name = comp_info.get("nombre_comercial", "Minimarket La Ruta del Este")

        # 1. Left Panel (Branding / Minimalist Hero - 50% Width)
        left_hero = ctk.CTkFrame(main_login_box, fg_color="#1E293B", corner_radius=0)"""

if target in code:
    code = code.replace(target, replacement)

code = code.replace('text="MINIMARKET LA RUTA DEL ESTE, S.R.L."', 'text=f"{com_name.upper()}, S.R.L."')

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed com_name in show_login!")
