import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import shutil

def draw_er_diagram_clean():
    fig, ax = plt.subplots(figsize=(15, 10.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Color Palette
    primary_color = '#0F4C81' # Deep Royal Blue Header
    secondary_color = '#1E293B' # Slate Dark
    bg_card = '#F8FAFC'
    border_color = '#0F4C81'
    line_color = '#2563EB' # Bright Blue
    text_white = '#FFFFFF'
    text_dark = '#0F172A'
    pk_color = '#B45309' # Amber/Gold for PK/FK

    # Title Banner
    ax.text(50, 96.5, "DIAGRAMA ENTIDAD-RELACIÓN Y FLUJO DE DATOS DEL SISTEMA", 
            fontsize=14, fontweight='bold', ha='center', va='center', color=primary_color)
    ax.text(50, 93.8, "Minimarket La Ruta del Este, S.R.L. — Modelo Relacional en 3FN", 
            fontsize=10.5, fontstyle='italic', ha='center', va='center', color='#475569')

    def draw_entity(x, y, w, h, title, fields):
        # Header Box
        hdr_rect = patches.FancyBboxPatch((x, y + h - 4.5), w, 4.5, boxstyle="square,pad=0",
                                          ec=border_color, fc=primary_color, lw=1.5)
        ax.add_patch(hdr_rect)
        ax.text(x + w/2, y + h - 2.25, title, fontsize=10.5, fontweight='bold', 
                ha='center', va='center', color=text_white)

        # Body Box
        body_rect = patches.FancyBboxPatch((x, y), w, h - 4.5, boxstyle="square,pad=0",
                                           ec=border_color, fc=bg_card, lw=1.5)
        ax.add_patch(body_rect)

        # Fields Text
        fy = y + h - 6.8
        for field in fields:
            is_pk = "[PK]" in field or "[FK]" in field or "[UK]" in field
            f_color = pk_color if is_pk else text_dark
            f_weight = 'bold' if is_pk else 'normal'
            ax.text(x + 1.5, fy, field, fontsize=8, fontweight=f_weight, color=f_color, va='center')
            fy -= 2.2

    # 1. PRODUCTOS
    draw_entity(4, 48, 27, 40, "PRODUCTOS", [
        "[PK] id : INT",
        "[UK] codigo_barras : VARCHAR(50)",
        "  nombre : VARCHAR(150)",
        "  precio_compra : DECIMAL(10,2)",
        "  precio_venta : DECIMAL(10,2)",
        "  stock_actual : INT",
        "  stock_minimo : INT",
        "  unidad_medida : VARCHAR(20)",
        "  estado : VARCHAR(20)",
        "[FK] departamento_id : INT",
        "[FK] subdepartamento_id : INT"
    ])

    # 2. DETALLE_VENTAS
    draw_entity(36.5, 8, 27, 26, "DETALLE_VENTAS", [
        "[PK] id : INT",
        "[FK] venta_id : INT",
        "[FK] producto_id : INT",
        "  cantidad : INT",
        "  precio_unitario : DECIMAL(10,2)",
        "  subtotal : DECIMAL(10,2)"
    ])

    # 3. VENTAS
    draw_entity(69, 46, 27, 38, "VENTAS", [
        "[PK] id : INT (OUTPUT INSERTED.id)",
        "[UK] codigo_factura : VARCHAR(50)",
        "  fecha_venta : DATETIME",
        "[FK] caja_id : INT",
        "[FK] usuario_id : INT",
        "  cliente_nombre : VARCHAR(100)",
        "  tipo_pago : VARCHAR(30)",
        "  subtotal : DECIMAL(10,2)",
        "  itbis : DECIMAL(10,2)",
        "  total : DECIMAL(10,2)"
    ])

    # 4. MOVIMIENTOS_INVENTARIO
    draw_entity(4, 8, 27, 28, "MOVIMIENTOS_INVENTARIO", [
        "[PK] id : INT",
        "[FK] producto_id : INT",
        "  tipo_movimiento : VARCHAR(20)",
        "  cantidad : INT",
        "  motivo : VARCHAR(200)",
        "  fecha_movimiento : DATETIME",
        "[FK] usuario_id : INT"
    ])

    # 5. CAJAS
    draw_entity(69, 8, 27, 24, "CAJAS", [
        "[PK] id : INT",
        "  nombre_caja : VARCHAR(50)",
        "  estado : VARCHAR(20)",
        "  fondo_inicial : DECIMAL(10,2)"
    ])

    # Connectors & Flow Logic
    def draw_flow_link(x1, y1, x2, y2, card1, card2, label):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=line_color, lw=2.2, ls='-'))
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(x1 + (x2-x1)*0.18, y1 + (y2-y1)*0.18, card1, fontsize=9, fontweight='bold', color=line_color, bbox=dict(boxstyle="round,pad=0.2", fc="#EFF6FF", ec=line_color, lw=1))
        ax.text(x1 + (x2-x1)*0.82, y1 + (y2-y1)*0.82, card2, fontsize=9, fontweight='bold', color=line_color, bbox=dict(boxstyle="round,pad=0.2", fc="#EFF6FF", ec=line_color, lw=1))
        ax.text(mid_x, mid_y + 1.8, label, fontsize=8, fontstyle='italic', ha='center', color='#1E293B', bbox=dict(boxstyle="square,pad=0.2", fc="#FFFFFF", ec="none"))

    # Connections
    draw_flow_link(17.5, 48, 36.5, 26, "1", "N", "es vendido en")
    draw_flow_link(69, 56, 63.5, 26, "1", "N", "contiene renglones")
    draw_flow_link(17.5, 48, 17.5, 36, "1", "N", "registra movimientos")
    draw_flow_link(82.5, 32, 82.5, 46, "1", "N", "procesa cobros")

    # Save PNG
    img_path = "diagrama_er_flujo.png"
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Clean E-R Diagram Flowchart image generated: {img_path}")

    # Copy to Artifacts folder
    artifact_dir = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2"
    if os.path.exists(artifact_dir):
        art_img = os.path.join(artifact_dir, img_path)
        shutil.copy(img_path, art_img)
        print(f"Copied clean image to artifacts: {art_img}")

if __name__ == "__main__":
    draw_er_diagram_clean()
