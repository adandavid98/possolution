import os
from reportlab.lib.pagesizes import letter, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_ticket_pdf(sale_data, output_filepath):
    """Generates a PDF Receipt/Ticket for a sale."""
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=(250, 450),
        rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=1, # Center
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        alignment=1,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10
    )
    
    elements = []
    
    # Header
    elements.append(Paragraph("MINIMARKET LA RUTA DEL ESTE", title_style))
    elements.append(Paragraph("Santo Domingo Este, R.D. | Tel: (809) 555-0199", subtitle_style))
    elements.append(Paragraph("RNC: 1-30-98765-4", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=4, spaceAfter=4))
    
    # Details
    elements.append(Paragraph(f"<b>Factura:</b> {sale_data['codigo_factura']}", body_style))
    elements.append(Paragraph(f"<b>Fecha:</b> {sale_data['fecha']}", body_style))
    elements.append(Paragraph(f"<b>Cliente:</b> {sale_data['cliente_nombre']}", body_style))
    elements.append(Paragraph(f"<b>Pago:</b> {sale_data['tipo_pago']}", body_style))
    elements.append(Spacer(1, 6))
    
    # Table Items
    table_data = [["Cant", "Producto", "Precio", "Total"]]
    for item in sale_data['items']:
        table_data.append([
            str(item['cantidad']),
            item['nombre'][:15],
            f"RD${item['precio_venta']:.2f}",
            f"RD${(item['precio_venta'] * item['cantidad']):.2f}"
        ])
        
    t = Table(table_data, colWidths=[25, 100, 50, 55])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black),
    ]))
    elements.append(t)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=6, spaceAfter=6))
    
    # Totals
    elements.append(Paragraph(f"<b>Subtotal:</b> RD$ {sale_data['subtotal']:.2f}", body_style))
    elements.append(Paragraph(f"<b>ITBIS (18%):</b> RD$ {sale_data['itbis']:.2f}", body_style))
    elements.append(Paragraph(f"<b>TOTAL PAGADO:</b> RD$ {sale_data['total']:.2f}", ParagraphStyle('BoldTotal', parent=body_style, fontName='Helvetica-Bold', fontSize=10)))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("¡Gracias por su compra en La Ruta del Este!", subtitle_style))
    
    doc.build(elements)
    return output_filepath

def generate_inventory_report_pdf(products, output_filepath):
    """Generates an Inventory Status PDF report."""
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, alignment=1)
    elements.append(Paragraph("MINIMARKET LA RUTA DEL ESTE", title_style))
    elements.append(Paragraph("Reporte General de Inventarios y Alertas", ParagraphStyle('Sub', parent=styles['Normal'], alignment=1, fontSize=11)))
    elements.append(Spacer(1, 15))
    
    table_data = [["Código", "Producto", "Categoría", "P. Costo", "P. Venta", "Stock Actual", "Stock Mín.", "Estado"]]
    for p in products:
        stock = p['stock_actual']
        min_s = p['stock_minimo']
        estado = "OK"
        if stock <= 0:
            estado = "AGOTADO"
        elif stock <= min_s:
            estado = "ALERTA BAJO"
            
        table_data.append([
            p['codigo_barras'],
            p['nombre'],
            p.get('categoria_nombre', 'N/A') or 'N/A',
            f"RD${p['precio_costo']:.2f}",
            f"RD${p['precio_venta']:.2f}",
            str(stock),
            str(min_s),
            estado
        ])
        
    t = Table(table_data, colWidths=[80, 150, 100, 55, 55, 60, 55, 65])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16161F')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t)
    doc.build(elements)
    return output_filepath
