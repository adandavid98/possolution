with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_welcome_start = """        # Always start on Welcome Dashboard upon login
        self.load_welcome_tab()"""

new_welcome_start = """        # Always start on Welcome Dashboard upon login
        self.load_welcome_tab()
        self.after(2000, self._trigger_background_update_check)"""

if old_welcome_start in content and "_trigger_background_update_check" not in content:
    content = content.replace(old_welcome_start, new_welcome_start)
    print("Trigger for background update check added to show_main_dashboard!")

update_methods = """
    # ==========================================
    # AUTO-UPDATE CHECKER & NOTIFICATION MODAL
    # ==========================================
    def _trigger_background_update_check(self):
        \"\"\"Triggers non-blocking background check for app updates.\"\"\"
        try:
            from utils.updater import UpdateChecker
            UpdateChecker.check_updates_async(self.open_update_notification_modal, self)
        except Exception as e:
            print("Update check error:", e)

    def open_update_notification_modal(self, update_data):
        \"\"\"Displays a modern dark-themed modal notification for new app updates.\"\"\"
        remote_ver = update_data.get("version", "1.1.0")
        source_name = update_data.get("source", "Servidor Remoto")
        changelog = update_data.get("changelog", [])
        download_url = update_data.get("download_url", "")

        win_update = ctk.CTkToplevel(self)
        win_update.title(f"🔔 Actualización de Software Disponible v{remote_ver}")
        
        win_w, win_h = 560, 480
        self.update_idletasks()
        rx = self.winfo_rootx() + (max(self.winfo_width(), 900) - win_w) // 2
        ry = self.winfo_rooty() + (max(self.winfo_height(), 600) - win_h) // 2 - 20
        win_update.geometry(f"{win_w}x{win_h}+{max(10, rx)}+{max(10, ry)}")
        win_update.configure(fg_color="#0F172A")

        win_update.transient(self)
        win_update.grab_set()

        # Header Card
        hdr_card = ctk.CTkFrame(win_update, fg_color="#1E293B", corner_radius=12, border_width=1, border_color="#38BDF8")
        hdr_card.pack(fill="x", padx=16, pady=(16, 10))

        ctk.CTkLabel(
            hdr_card, text="🔔 ¡NUEVA ACTUALIZACIÓN DE SOFTWARE DISPONIBLE!",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#38BDF8"
        ).pack(pady=(12, 4))

        # Version Pill Badge
        badge_frame = ctk.CTkFrame(hdr_card, fg_color="transparent")
        badge_frame.pack(pady=(0, 12))

        local_ver = getattr(Config, 'APP_VERSION', '1.0.0')
        ctk.CTkLabel(
            badge_frame, text=f" Versión Instalada: v{local_ver} ",
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#334155", text_color="#94A3B8", corner_radius=6
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            badge_frame, text=" ➜ ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8"
        ).pack(side="left")

        ctk.CTkLabel(
            badge_frame, text=f" Nueva Versión: v{remote_ver} ({source_name}) ",
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#10B981", text_color="white", corner_radius=6
        ).pack(side="left", padx=4)

        # Changelog Section
        ctk.CTkLabel(
            win_update, text="📋 Novedades y Mejoras Incluidas:",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#F8FAFC"
        ).pack(anchor="w", padx=20, pady=(4, 4))

        change_box = ctk.CTkScrollableFrame(win_update, height=180, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
        change_box.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        for item in changelog:
            p_item = ctk.CTkLabel(
                change_box, text=f"• {item}",
                font=ctk.CTkFont(size=11), text_color="#CBD5E1", justify="left", anchor="w", wraplength=480
            )
            p_item.pack(fill="x", padx=8, pady=3)

        # Download Status & Progress Frame
        status_lbl = ctk.CTkLabel(win_update, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8")
        status_lbl.pack(pady=(0, 4))

        pbar = ctk.CTkProgressBar(win_update, mode="indeterminate", height=10, progress_color="#10B981")
        
        def start_download_process():
            btn_update.configure(state="disabled", text="⏳ Descargando Actualización...")
            btn_later.configure(state="disabled")
            status_lbl.configure(text="Descargando paquete de actualización en segundo plano...")
            pbar.pack(fill="x", padx=20, pady=(0, 10))
            pbar.start()

            def _bg_download():
                try:
                    import tempfile
                    import urllib.request
                    temp_dir = tempfile.gettempdir()
                    dest_zip = os.path.join(temp_dir, f"POS_Update_v{remote_ver}.zip")
                    
                    if download_url and download_url.startswith("http"):
                        urllib.request.urlretrieve(download_url, dest_zip)
                    else:
                        local_zip = os.path.join(os.getcwd(), "dist", "Instalador_POS_LaRuta_Este_v1.0.zip")
                        import shutil
                        shutil.copy(local_zip, dest_zip)

                    def _on_finish():
                        try:
                            pbar.stop()
                            win_update.destroy()
                        except Exception:
                            pass
                        from utils.updater import UpdateChecker
                        UpdateChecker.launch_updater_and_exit(dest_zip)

                    self.after(500, _on_finish)
                except Exception as e:
                    def _on_err(err_msg=str(e)):
                        try:
                            pbar.stop()
                            pbar.pack_forget()
                        except Exception:
                            pass
                        status_lbl.configure(text=f"❌ Error en descarga: {err_msg}", text_color="#EF4444")
                        btn_update.configure(state="normal", text="⚡ REINTENTAR ACTUALIZACIÓN")
                        btn_later.configure(state="normal")
                    self.after(0, _on_err)

            t = threading.Thread(target=_bg_download, daemon=True)
            t.start()

        # Action Buttons Row
        btn_box = ctk.CTkFrame(win_update, fg_color="transparent")
        btn_box.pack(fill="x", padx=16, pady=(0, 16))

        btn_later = ctk.CTkButton(
            btn_box, text="Recordar Más Tarde", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#334155", hover_color="#475569", height=42, corner_radius=8,
            command=win_update.destroy
        )
        btn_later.pack(side="left", padx=4, expand=True, fill="x")

        btn_update = ctk.CTkButton(
            btn_box, text="⚡ ACTUALIZAR SOFTWARE AHORA", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981", hover_color="#059669", height=42, corner_radius=8,
            command=start_download_process
        )
        btn_update.pack(side="right", padx=4, expand=True, fill="x")
"""

if "_trigger_background_update_check" not in content:
    content += update_methods
    with open('app_gui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("app_gui.py updated with update notification modal and trigger!")
else:
    print("update notification modal already present in app_gui.py")
