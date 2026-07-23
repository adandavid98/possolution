import os
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header line
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.line(36, 756, 576, 756)

        self.drawString(36, 762, "MINIMARKET LA RUTA DEL ESTE - SISTEMA DE AUDITORÍA & REPORTES POS")
        self.drawRightString(576, 762, datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))

        # Footer line
        self.line(36, 36, 576, 36)
        self.setFont("Helvetica", 8)
        self.drawString(36, 24, "Documento de Auditoría Confidencial - Generado por Sistema POS La Ruta del Este")
        self.drawRightString(576, 24, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def generate_pdf_report(report_type, data, period_title, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=8
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    tb_style = ParagraphStyle(
        'TB',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )

    story = []

    # Title & Corporate Header
    story.append(Paragraph("MINIMARKET LA RUTA DEL ESTE", title_style))
    story.append(Paragraph(f"REPORTE: {report_type.upper()}", subtitle_style))
    story.append(Paragraph(f"<b>Período:</b> {period_title} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Generado:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
    story.append(Spacer(1, 8))

    if report_type == "General Consolidado":
        summary = data
        card_data = [
            [
                Paragraph("<b>Transacciones</b><br/><font size=14 color='#2563EB'><b>" + str(summary.get("total_transacciones", 0)) + "</b></font>", tb_style),
                Paragraph("<b>Ingresos Brutos</b><br/><font size=14 color='#10B981'><b>RD$ " + f"{summary.get('total_ingresos', 0):,.2f}" + "</b></font>", tb_style),
                Paragraph("<b>ITBIS Recaudado</b><br/><font size=14 color='#F59E0B'><b>RD$ " + f"{summary.get('total_itbis', 0):,.2f}" + "</b></font>", tb_style),
                Paragraph("<b>Ganancia Est.</b><br/><font size=14 color='#8B5CF6'><b>RD$ " + f"{summary.get('ganancia_estimada', 0):,.2f}" + "</b></font>", tb_style),
            ]
        ]
        card_table = Table(card_data, colWidths=[135, 135, 135, 135])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(card_table)
        story.append(Spacer(1, 15))

    elif report_type == "Por Departamentos y Sub-departamentos":
        rows = [["Departamento", "Sub-Departamento", "Vendidos", "Subtotal RD$", "ITBIS RD$", "Total RD$", "Ganancia Est."]]
        table_rows = [ [Paragraph(h, th_style) for h in rows[0]] ]

        total_neto_gen = 0.0
        for r in data:
            total_neto_gen += float(r.get('total_neto') or 0)
            table_rows.append([
                Paragraph(str(r.get('departamento', '')), tb_style),
                Paragraph(str(r.get('subdepartamento', '')), tb_style),
                Paragraph(str(r.get('unidades_vendidas', 0)), tb_style),
                Paragraph(f"RD$ {float(r.get('total_bruto') or 0):,.2f}", tb_style),
                Paragraph(f"RD$ {float(r.get('itbis_estimado') or 0):,.2f}", tb_style),
                Paragraph(f"RD$ {float(r.get('total_neto') or 0):,.2f}", tb_style),
                Paragraph(f"RD$ {float(r.get('ganancia_estimada') or 0):,.2f}", tb_style),
            ])

        t = Table(table_rows, colWidths=[100, 110, 50, 75, 65, 70, 70])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t)

    elif report_type == "Store Multi-Total (Métodos y Cajeros)":
        by_pay = data.get("by_payment", [])
        by_usr = data.get("by_user", [])

        story.append(Paragraph("<b>TOTALES POR MÉTODO DE PAGO</b>", subtitle_style))
        p_rows = [[Paragraph("Método de Pago", th_style), Paragraph("Operaciones", th_style), Paragraph("Subtotal RD$", th_style), Paragraph("ITBIS RD$", th_style), Paragraph("Monto Total RD$", th_style)]]
        for r in by_pay:
            p_rows.append([
                Paragraph(str(r.get("tipo_pago", "Efectivo")), tb_style),
                Paragraph(str(r.get("total_operaciones", 0)), tb_style),
                Paragraph(f"RD$ {float(r.get('subtotal') or 0):,.2f}", tb_style),
                Paragraph(f"RD$ {float(r.get('itbis') or 0):,.2f}", tb_style),
                Paragraph(f"RD$ {float(r.get('total_monto') or 0):,.2f}", tb_style),
            ])
        tp = Table(p_rows, colWidths=[130, 80, 110, 100, 120])
        tp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(tp)
        story.append(Spacer(1, 15))

        story.append(Paragraph("<b>VENTAS POR CAJERO / USUARIO</b>", subtitle_style))
        u_rows = [[Paragraph("Cajero / Usuario", th_style), Paragraph("Facturas Emitidas", th_style), Paragraph("Total Generado RD$", th_style)]]
        for r in by_usr:
            u_rows.append([
                Paragraph(str(r.get("cajero", "Cajero")), tb_style),
                Paragraph(str(r.get("total_ventas", 0)), tb_style),
                Paragraph(f"RD$ {float(r.get('total_monto') or 0):,.2f}", tb_style),
            ])
        tu = Table(u_rows, colWidths=[200, 140, 200])
        tu.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(tu)

    elif report_type == "Valoración de Inventario":
        sum_val = data.get("summary", {})
        det_val = data.get("details", [])

        c_data = [
            [
                Paragraph("<b>Total Ítems</b><br/><font size=12 color='#2563EB'><b>" + str(sum_val.get("total_productos", 0)) + "</b></font>", tb_style),
                Paragraph("<b>Valor Costo Total</b><br/><font size=12 color='#475569'><b>RD$ " + f"{float(sum_val.get('valor_costo_total') or 0):,.2f}" + "</b></font>", tb_style),
                Paragraph("<b>Valor Venta Total</b><br/><font size=12 color='#10B981'><b>RD$ " + f"{float(sum_val.get('valor_venta_total') or 0):,.2f}" + "</b></font>", tb_style),
                Paragraph("<b>Ganancia Potencial</b><br/><font size=12 color='#8B5CF6'><b>RD$ " + f"{float(sum_val.get('ganancia_potencial') or 0):,.2f}" + "</b></font>", tb_style),
            ]
        ]
        ct = Table(c_data, colWidths=[135, 135, 135, 135])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(ct)
        story.append(Spacer(1, 12))

        i_rows = [[Paragraph("Código", th_style), Paragraph("Producto", th_style), Paragraph("Subdepto", th_style), Paragraph("Stock", th_style), Paragraph("P. Costo", th_style), Paragraph("P. Venta", th_style), Paragraph("Valor Venta RD$", th_style)]]
        for p in det_val[:100]:
            i_rows.append([
                Paragraph(str(p.get("codigo_barras", "")), tb_style),
                Paragraph(str(p.get("nombre", "")), tb_style),
                Paragraph(str(p.get("subdepartamento", "")), tb_style),
                Paragraph(str(p.get("stock_actual", 0)), tb_style),
                Paragraph(f"RD${float(p.get('precio_costo') or 0):,.2f}", tb_style),
                Paragraph(f"RD${float(p.get('precio_venta') or 0):,.2f}", tb_style),
                Paragraph(f"RD${float(p.get('valor_venta') or 0):,.2f}", tb_style),
            ])
        ti = Table(i_rows, colWidths=[80, 140, 90, 45, 60, 60, 65])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(ti)

    elif report_type in ["Diario Electrónico (Electronic Journal)", "Historial de Facturas"]:
        ventas = data
        story.append(Paragraph(f"<b>TOTAL TRANSACCIONES EN EL DIARIO: {len(ventas)}</b>", subtitle_style))

        for v in ventas[:50]: # Limit for PDF clean rendering
            header_text = f"<b>Factura:</b> {v['codigo_factura']} &nbsp;|&nbsp; <b>Fecha:</b> {str(v['fecha'])[:19]} &nbsp;|&nbsp; <b>Cajero:</b> {v.get('cajero_nombre','N/A')} &nbsp;|&nbsp; <b>Pago:</b> {v['tipo_pago']} &nbsp;|&nbsp; <b>Total: RD$ {v['total']:,.2f}</b>"
            story.append(Paragraph(header_text, tb_style))
            
            items = v.get("items", [])
            if items:
                it_rows = [[Paragraph("Cód.", th_style), Paragraph("Artículo", th_style), Paragraph("Subdepto", th_style), Paragraph("Cant.", th_style), Paragraph("Precio U.", th_style), Paragraph("Subtotal RD$", th_style)]]
                for it in items:
                    it_rows.append([
                        Paragraph(str(it.get("codigo_barras", "")), tb_style),
                        Paragraph(str(it.get("producto_nombre", "")), tb_style),
                        Paragraph(str(it.get("subdepartamento_nombre", "")), tb_style),
                        Paragraph(str(it.get("cantidad", 1)), tb_style),
                        Paragraph(f"RD${float(it.get('precio_unitario') or 0):,.2f}", tb_style),
                        Paragraph(f"RD${float(it.get('subtotal') or 0):,.2f}", tb_style),
                    ])
                tit = Table(it_rows, colWidths=[70, 160, 110, 45, 75, 80])
                tit.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F1F5F9')]),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('PADDING', (0,0), (-1,-1), 3),
                ]))
                story.append(tit)
            story.append(Spacer(1, 8))

    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path

def print_pdf_file(pdf_path):
    """Sends PDF directly to Windows Default Printer using os.startfile."""
    if os.path.exists(pdf_path):
        try:
            os.startfile(pdf_path, "print")
            return True
        except Exception as e:
            print(f"Error calling print: {e}")
            os.startfile(pdf_path)
            return True
    return False
