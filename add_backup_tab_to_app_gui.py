with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_tab_add = """        self._tab_item_maint = self._bo_tabview.add("🏷️ Mantenimiento Artículos")
        self._tab_customers  = self._bo_tabview.add("👥 Clientes & Proveedores")
        self._tab_operators  = self._bo_tabview.add("🔒 Operadores & Permisos (RBAC)")
        self._tab_store_cfg  = self._bo_tabview.add("🏬 Datos de la Tienda")"""

new_tab_add = """        self._tab_item_maint = self._bo_tabview.add("🏷️ Mantenimiento Artículos")
        self._tab_customers  = self._bo_tabview.add("👥 Clientes & Proveedores")
        self._tab_operators  = self._bo_tabview.add("🔒 Operadores & Permisos (RBAC)")
        self._tab_store_cfg  = self._bo_tabview.add("🏬 Datos de la Tienda")
        self._tab_backup_cfg = self._bo_tabview.add("💾 Respaldo y Restauración SQL")"""

old_tab_loads = """        try:
            self._load_bo_store_config(self._tab_store_cfg)
        except Exception as e:
            print("Error loading store config subtab:", e)"""

new_tab_loads = """        try:
            self._load_bo_store_config(self._tab_store_cfg)
        except Exception as e:
            print("Error loading store config subtab:", e)

        try:
            self._load_bo_backup_restore(self._tab_backup_cfg)
        except Exception as e:
            print("Error loading backup restore subtab:", e)"""

backup_ui_code = """
    # ── 5. BACKUP & RESTORE SUB-TAB ──────────────────────────────────────────
    def _load_bo_backup_restore(self, parent):
        outer = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        # Header Card
        hdr_card = ctk.CTkFrame(outer, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#38BDF8")
        hdr_card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            hdr_card, text="💾 RESPALDO Y RESTAURACIÓN MANUAL DE BASE DE DATOS (SQL SERVER)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#38BDF8"
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            hdr_card, text="Exporte e importe copias de seguridad nativas (.BAK) para proteger toda la información comercial y transaccional del minimarket.",
            font=ctk.CTkFont(size=11), text_color="#94A3B8"
        ).pack(anchor="w", padx=16, pady=(0, 14))

        # Main Layout (2 Columns: Export on Left, Import on Right)
        grid_frame = ctk.CTkFrame(outer, fg_color="transparent")
        grid_frame.pack(fill="x")
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        # --- LEFT CARD: EXPORT BACKUP ---
        card_export = ctk.CTkFrame(grid_frame, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        card_export.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)

        ctk.CTkLabel(
            card_export, text="📤 Exportar Respaldo de Base de Datos",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#10B981"
        ).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(
            card_export,
            text="Genera un archivo de respaldo completo (.BAK) en su equipo. Se recomienda guardar copias periódicas en una memoria USB o disco externo.",
            font=ctk.CTkFont(size=11), text_color="#CBD5E1", justify="left", wraplength=340
        ).pack(anchor="w", padx=16, pady=(0, 12))

        def _execute_export():
            from datetime import datetime
            from tkinter import filedialog, messagebox
            from database import backup_database_sqlserver

            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_file = f"Backup_POS_LaRuta_DB_{now_str}.bak"
            
            dest_file = filedialog.asksaveasfilename(
                title="Guardar Respaldo SQL Server",
                initialfile=default_file,
                defaultextension=".bak",
                filetypes=[("Respaldo SQL Server (*.bak)", "*.bak"), ("Todos los archivos", "*.*")]
            )
            
            if dest_file:
                success, msg = backup_database_sqlserver(dest_file)
                if success:
                    messagebox.showinfo("Respaldo Exitoso", f"El respaldo de la base de datos se generó correctamente en:\n\n{dest_file}")
                else:
                    messagebox.showerror("Error al Respaldar", f"No se pudo generar el respaldo:\n\n{msg}")

        ctk.CTkButton(
            card_export, text="📤 EXPORTAR RESPALDO AHORA (.BAK)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=42, corner_radius=8,
            command=_execute_export
        ).pack(fill="x", padx=16, pady=(0, 16))

        # --- RIGHT CARD: IMPORT / RESTORE BACKUP ---
        card_import = ctk.CTkFrame(grid_frame, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#EF4444")
        card_import.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=4)

        ctk.CTkLabel(
            card_import, text="📥 Importar / Restaurar Base de Datos",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#EF4444"
        ).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(
            card_import,
            text="⚠️ ADVERTENCIA: Al restaurar un respaldo (.BAK), la información actual de la base de datos será reemplazada por los datos del archivo seleccionado.",
            font=ctk.CTkFont(size=11), text_color="#FCA5A5", justify="left", wraplength=340
        ).pack(anchor="w", padx=16, pady=(0, 12))

        def _execute_import():
            from tkinter import filedialog, messagebox
            from database import restore_database_sqlserver, check_sql_server

            confirm = messagebox.askyesno(
                "Confirmar Restauración de Base de Datos",
                "⚠️ ¿Está seguro que desea restaurar la base de datos desde un archivo de respaldo?\n\n"
                "La información actual de ventas y productos será reemplazada."
            )
            if not confirm:
                return

            src_file = filedialog.askopenfilename(
                title="Seleccionar Archivo de Respaldo (.BAK)",
                filetypes=[("Respaldo SQL Server (*.bak)", "*.bak"), ("Todos los archivos", "*.*")]
            )

            if src_file:
                success, msg = restore_database_sqlserver(src_file)
                if success:
                    check_sql_server(force_recheck=True)
                    messagebox.showinfo("Restauración Completada", "La base de datos se restauró con éxito.\n\nEl sistema refrescará sus catálogos ahora.")
                    try:
                        self._load_products()
                    except Exception:
                        pass
                else:
                    messagebox.showerror("Error al Restaurar", f"No se pudo restaurar la base de datos:\n\n{msg}")

        ctk.CTkButton(
            card_import, text="📥 SELECCIONAR Y RESTAURAR RESPALDO",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#DC2626", hover_color="#B91C1C", height=42, corner_radius=8,
            command=_execute_import
        ).pack(fill="x", padx=16, pady=(0, 16))
"""

if old_tab_add in content:
    content = content.replace(old_tab_add, new_tab_add)
if old_tab_loads in content:
    content = content.replace(old_tab_loads, new_tab_loads)

if "_load_bo_backup_restore" not in content:
    content += backup_ui_code
    with open('app_gui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("app_gui.py updated with Backup & Restore sub-tab!")
else:
    print("Backup & Restore sub-tab already exists in app_gui.py")
