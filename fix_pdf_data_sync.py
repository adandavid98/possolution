with open('models.py', 'r', encoding='utf-8') as f:
    content_models = f.read()

# Update ReportModel.get_date_range_bounds in models.py
old_bounds_method = """    @staticmethod
    def get_date_range_bounds(period_type, start_date=None, end_date=None):

        today = datetime.date.today()
        if period_type == "Hoy":
            s_dt = f"{today} 00:00:00"
            e_dt = f"{today} 23:59:59"
        elif period_type == "Esta Semana":
            start_week = today - datetime.timedelta(days=today.weekday())
            s_dt = f"{start_week} 00:00:00"
            e_dt = f"{today} 23:59:59"
        elif period_type == "Este Mes":
            start_month = today.replace(day=1)
            s_dt = f"{start_month} 00:00:00"
            e_dt = f"{today} 23:59:59"
        elif period_type == "Este Año":
            start_year = today.replace(month=1, day=1)
            s_dt = f"{start_year} 00:00:00"
            e_dt = f"{today} 23:59:59"
        elif period_type == "Personalizado" and start_date and end_date:
            s_dt = f"{start_date} 00:00:00"
            e_dt = f"{end_date} 23:59:59"
        else:
            s_dt = f"{today} 00:00:00"
            e_dt = f"{today} 23:59:59"
        return s_dt, e_dt"""

new_bounds_method = """    @staticmethod
    def get_date_range_bounds(period_type, start_date=None, end_date=None):
        today = datetime.date.today()
        p = str(period_type or '').strip()

        def to_iso_date(d_str):
            if not d_str: return today
            d_str = str(d_str).strip()
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(d_str, fmt).date()
                except ValueError:
                    pass
            return today

        if p in ["Día", "Hoy"]:
            s = e = today
        elif p in ["Semana", "Esta Semana"]:
            s = today - datetime.timedelta(days=today.weekday())
            e = today
        elif p in ["Mes", "Este Mes"]:
            s = today.replace(day=1)
            e = today
        elif p in ["Año", "Este Año"]:
            s = today.replace(month=1, day=1)
            e = today
        elif p == "Personalizado" and start_date and end_date:
            s = to_iso_date(start_date)
            e = to_iso_date(end_date)
        else:
            s = e = today

        return f"{s} 00:00:00", f"{e} 23:59:59" """

if old_bounds_method in content_models:
    content_models = content_models.replace(old_bounds_method, new_bounds_method)
    print("models.py get_date_range_bounds updated!")

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content_models)


with open('app_gui.py', 'r', encoding='utf-8') as f:
    content_gui = f.read()

# Update _open_pdf_preview and _export_pdf_direct in app_gui.py
old_pdf_methods = """    def _open_pdf_preview(self):
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
                messagebox.showerror("Error PDF", f"No se pudo exportar:\n{e}")"""

new_pdf_methods = """    def _open_pdf_preview(self):
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
                messagebox.showerror("Error PDF", f"No se pudo exportar:\n{e}")"""

if old_pdf_methods in content_gui:
    content_gui = content_gui.replace(old_pdf_methods, new_pdf_methods)
    print("app_gui.py _open_pdf_preview and _export_pdf_direct updated!")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content_gui)

print("fix_pdf_data_sync script finished!")
