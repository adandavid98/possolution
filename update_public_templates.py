# Update whatsapp.html
with open('templates/whatsapp.html', 'r', encoding='utf-8') as f:
    w_content = f.read()

w_old_hdr = """    <div class="header-box text-center text-white">
        <h4 class="fw-bold m-0">📱 CONSULTA PEDIDOS WHATSAPP</h4>
        <small>Minimarket La Ruta del Este | Tiempo Real SQL Server</small>
    </div>"""

w_new_hdr = """    <div class="header-box text-white">
        <div class="container d-flex justify-content-between align-items-center">
            <div>
                <h5 class="fw-bold m-0">📱 CONSULTA PEDIDOS WHATSAPP</h5>
                <small>Minimarket La Ruta del Este | Tiempo Real SQL Server</small>
            </div>
            <div>
                <a href="/login" class="btn btn-dark btn-sm rounded-pill px-3 border-secondary">🔒 Acceso Almacén</a>
            </div>
        </div>
    </div>"""

if w_old_hdr in w_content:
    w_content = w_content.replace(w_old_hdr, w_new_hdr)
    with open('templates/whatsapp.html', 'w', encoding='utf-8') as f:
        f.write(w_content)
    print("whatsapp.html updated with Acceso Almacén link!")

# Update index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    i_content = f.read()

i_old_ms = """            <div class="ms-auto">
                <a href="/whatsapp" class="btn btn-outline-primary rounded-pill px-4">📱 Consulta WhatsApp Móvil</a>
            </div>"""

i_new_ms = """            <div class="ms-auto d-flex gap-2">
                <a href="/whatsapp" class="btn btn-outline-primary rounded-pill px-3">📱 Consulta WhatsApp Móvil</a>
                <a href="/login" class="btn btn-outline-success rounded-pill px-3">🔒 Acceso Almacén</a>
            </div>"""

if i_old_ms in i_content:
    i_content = i_content.replace(i_old_ms, i_new_ms)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(i_content)
    print("index.html updated with Acceso Almacén link!")
