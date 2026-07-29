import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw_er_diagram():
    # Setup figure
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Color Palette
    primary_color = '#0F4C81' # Deep Royal Blue
    secondary_color = '#1E293B' # Slate Dark
    bg_card = '#F8FAFC'
    border_color = '#0F4C81'
    line_color = '#2563EB' # Bright Blue
    text_white = '#FFFFFF'
    text_dark = '#0F172A'
    pk_color = '#D97706' # Amber/Gold for PK/FK

    # Title
    ax.text(50, 96, "MODELO ENTIDAD-RELACIÓN (DIAGRAMA DE FLUJO Y ESTRUCTURA DE DATOS)", 
            fontsize=13, fontweight='bold', ha='center', va='center', color=primary_color)
    ax.text(50, 93.5, "Sistema de Gestión de Inventario y Ventas — Minimarket La Ruta del Este, S.R.L.", 
            fontsize=10, fontstyle='italic', ha='center', va='center', color='#475569')

    # Helper function to draw Entity Box
    def draw_entity(x, y, w, h, title, fields):
        # Header Box
        hdr_rect = patches.FancyBboxPatch((x, y + h - 4.5), w, 4.5, boxstyle="square,pad=0",
                                          ec=border_color, fc=primary_color, lw=1.5)
        ax.add_patch(hdr_rect)
        ax.text(x + w/2, y + h - 2.25, title, fontsize=10, fontweight='bold', 
                ha='center', va='center', color=text_white)

        # Body Box
        body_rect = patches.FancyBboxPatch((x, y), w, h - 4.5, boxstyle="square,pad=0",
                                           ec=border_color, fc=bg_card, lw=1.5)
        ax.add_patch(body_rect)

        # Fields Text
        fy = y + h - 6.5
        for field in fields:
            is_pk = "PK" in field or "FK" in field or "UK" in field
            f_color = pk_color if is_pk else text_dark
            f_weight = 'bold' if is_pk else 'normal'
            ax.text(x + 1.5, fy, field, fontsize=7.5, fontweight=f_weight, color=f_color, va='center')
            fy -= 2.2

    # Draw Entities
    # 1. PRODUCTOS
    draw_entity(5, 50, 26, 38, "PRODUCTOS", [
        "🔑 id : INT [PK]",
        "⭐ codigo_barras : VARCHAR [UK]",
        "🏷️ nombre : VARCHAR",
        "💲 precio_compra : DECIMAL",
        "💲 precio_venta : DECIMAL",
        "📦 stock_actual : INT",
        "⚠️ stock_minimo : INT",
        "📏 unidad_medida : VARCHAR",
        "🔄 estado : VARCHAR",
        "🔗 departamento_id : INT [FK]",
        "🔗 subdepartamento_id : INT [FK]"
    ])

    # 2. DETALLE_VENTAS (Center Bottom)
    draw_entity(37, 10, 26, 24, "DETALLE_VENTAS", [
        "🔑 id : INT [PK]",
        "🔗 venta_id : INT [FK]",
        "🔗 producto_id : INT [FK]",
        "🔢 cantidad : INT",
        "💲 precio_unitario : DECIMAL",
        "💰 subtotal : DECIMAL"
    ])

    # 3. VENTAS (Right Middle)
    draw_entity(69, 48, 26, 34, "VENTAS", [
        "🔑 id : INT [PK (OUTPUT INSERTED.id)]",
        "⭐ codigo_factura : VARCHAR [UK]",
        "📅 fecha_venta : DATETIME",
        "🔗 caja_id : INT [FK]",
        "🔗 usuario_id : INT [FK]",
        "👤 cliente_nombre : VARCHAR",
        "💳 tipo_pago : VARCHAR",
        "💰 subtotal : DECIMAL",
        "📊 itbis : DECIMAL (18%)",
        "💵 total : DECIMAL"
    ])

    # 4. MOVIMIENTOS_INVENTARIO (Left Bottom)
    draw_entity(5, 10, 26, 26, "MOVIMIENTOS_INVENTARIO", [
        "🔑 id : INT [PK]",
        "🔗 producto_id : INT [FK]",
        "🔄 tipo_movimiento : VARCHAR",
        "🔢 cantidad : INT",
        "📝 motivo : VARCHAR",
        "📅 fecha_movimiento : DATETIME",
        "👤 usuario_id : INT [FK]"
    ])

    # 5. CAJAS (Right Top)
    draw_entity(69, 10, 26, 22, "CAJAS", [
        "🔑 id : INT [PK]",
        "🖥️ nombre_caja : VARCHAR",
        "🔄 estado : VARCHAR",
        "💵 fondo_inicial : DECIMAL"
    ])

    # Connectors & Cardinality Arrows
    def draw_connection(x1, y1, x2, y2, card1, card2, label):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=line_color, lw=2, ls='-'))
        # Cardinality text
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(x1 + (x2-x1)*0.2, y1 + (y2-y1)*0.2, card1, fontsize=8.5, fontweight='bold', color=line_color, backgroundcolor='#FFFFFF')
        ax.text(x1 + (x2-x1)*0.8, y1 + (y2-y1)*0.8, card2, fontsize=8.5, fontweight='bold', color=line_color, backgroundcolor='#FFFFFF')
        ax.text(mid_x, mid_y + 1.5, label, fontsize=7.5, fontstyle='italic', ha='center', color='#334155', backgroundcolor='#FFFFFF')

    # PRODUCTOS -> DETALLE_VENTAS
    draw_connection(18, 50, 37, 26, "(1)", "(N)", "es vendido en")

    # VENTAS -> DETALLE_VENTAS
    draw_connection(69, 58, 63, 26, "(1)", "(N)", "contiene")

    # PRODUCTOS -> MOVIMIENTOS_INVENTARIO
    draw_connection(18, 50, 18, 36, "(1)", "(N)", "registra movimientos")

    # CAJAS -> VENTAS
    draw_connection(82, 32, 82, 48, "(1)", "(N)", "procesa cobros")

    # Save figure
    img_path = "diagrama_er_flujo.png"
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"E-R Diagram Flowchart image generated successfully: {img_path}")

    # Copy to Artifacts folder as well
    artifact_dir = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2"
    if os.path.exists(artifact_dir):
        import shutil
        art_img = os.path.join(artifact_dir, img_path)
        shutil.copy(img_path, art_img)
        print(f"Copied image to artifacts: {art_img}")

if __name__ == "__main__":
    draw_er_diagram()
