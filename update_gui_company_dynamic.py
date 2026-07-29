import os

with open('app_gui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update show_login to fetch company info dynamically
old_login_text = """        # 1. Header / Logo / Branding
        lbl_top_brand = ctk.CTkLabel(
            hero_content, 
            text="MINIMARKET LA RUTA DEL ESTE, S.R.L.", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_top_brand.pack(pady=(0, 15))"""

new_login_text = """        # 1. Header / Logo / Branding
        comp_info = CompanyModel.get()
        com_name = comp_info.get("nombre_comercial", "Minimarket La Ruta del Este")

        lbl_top_brand = ctk.CTkLabel(
            hero_content, 
            text=f"{com_name.upper()}, S.R.L.", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_top_brand.pack(pady=(0, 15))"""

if old_login_text in code:
    code = code.replace(old_login_text, new_login_text)

old_title_text = """        # Main Title & Subtitle
        lbl_main_title = ctk.CTkLabel(
            hero_content, 
            text="Minimarket La Ruta del Este","""

new_title_text = """        # Main Title & Subtitle
        lbl_main_title = ctk.CTkLabel(
            hero_content, 
            text=com_name,"""

if old_title_text in code:
    code = code.replace(old_title_text, new_title_text)

# 2. Update show_main_dashboard to fetch company info dynamically
old_dashboard_brand = """        lbl_brand = ctk.CTkLabel(
            top_bar, 
            text="  LA RUTA DEL ESTE  |  PUNTO DE VENTA", 
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
            text_color="#F8FAFC"
        )
        lbl_brand.pack(side="left", padx=15)"""

new_dashboard_brand = """        comp_info = CompanyModel.get()
        com_name_dash = comp_info.get("nombre_comercial", "LA RUTA DEL ESTE").upper()

        self.lbl_brand = ctk.CTkLabel(
            top_bar, 
            text=f"  {com_name_dash}  |  PUNTO DE VENTA", 
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
            text_color="#F8FAFC"
        )
        self.lbl_brand.pack(side="left", padx=15)"""

if old_dashboard_brand in code:
    code = code.replace(old_dashboard_brand, new_dashboard_brand)

# 3. Update _save_company_config to update self.lbl_brand if present
old_save_company = """    def _save_company_config(self):
        rnc = self._ent_cfg_rnc.get().strip()
        nom = self._ent_cfg_nombre.get().strip()
        tel = self._ent_cfg_tel.get().strip()
        direccion = self._ent_cfg_dir.get().strip()
        msg = self._ent_cfg_msg.get().strip()

        try:
            CompanyModel.update(rnc, nom, tel, direccion, msg)
            messagebox.showinfo("Éxito", "¡Configuración de la empresa guardada exitosamente!")
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))"""

new_save_company = """    def _save_company_config(self):
        rnc = self._ent_cfg_rnc.get().strip()
        nom = self._ent_cfg_nombre.get().strip()
        tel = self._ent_cfg_tel.get().strip()
        direccion = self._ent_cfg_dir.get().strip()
        msg = self._ent_cfg_msg.get().strip()

        if not nom:
            messagebox.showwarning("Atención", "El Nombre Comercial no puede estar vacío.")
            return

        try:
            res = CompanyModel.update(rnc, nom, tel, direccion, msg)
            if hasattr(self, 'lbl_brand') and self.lbl_brand:
                try:
                    self.lbl_brand.configure(text=f"  {nom.upper()}  |  PUNTO DE VENTA")
                except Exception:
                    pass
            messagebox.showinfo("Éxito", "¡Configuración de la empresa guardada exitosamente!")
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e))"""

if old_save_company in code:
    code = code.replace(old_save_company, new_save_company)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("app_gui.py updated with dynamic company name branding!")
