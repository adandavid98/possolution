with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_confirm_checkout = """        def confirm_final_checkout():
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
                messagebox.showerror("Error en Venta", f"Ocurrió un error al guardar la venta: {e}")"""

new_confirm_checkout = """        def confirm_final_checkout():
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

            self.after(60, _execute_sale)"""

if old_confirm_checkout in content:
    content = content.replace(old_confirm_checkout, new_confirm_checkout)
    print("confirm_final_checkout updated with transaction loading bar & live timer!")
else:
    print("WARNING: old_confirm_checkout not found in app_gui.py")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
