with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_web_app = """import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config
from models import ProductModel, UserModel, InventoryMovementModel
from database import get_active_db_type, execute_query

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = getattr(Config, "SECRET_KEY", "la_ruta_del_este_secret_key_2026")

@app.route("/")
def index():
    products = ProductModel.get_all()
    low_stock = ProductModel.get_low_stock_products()
    db_engine = get_active_db_type()
    return render_template(
        "index.html", 
        products=products, 
        total_products=len(products), 
        low_stock_count=len(low_stock),
        db_engine=db_engine
    )

@app.route("/whatsapp")
def whatsapp_portal():
    return render_template("whatsapp.html")

@app.route("/api/version")
def api_version():
    try:
        import json
        v_file = os.path.join(os.path.dirname(__file__), "version.json")
        if os.path.exists(v_file):
            with open(v_file, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
    except Exception:
        pass
    return jsonify({
        "version": getattr(Config, "APP_VERSION", "1.0.0"),
        "fecha": "2026-07-28",
        "changelog": ["Versión base del servidor local."],
        "download_url": "",
        "obligatoria": False
    })

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    products = ProductModel.get_all(query)
    return jsonify(products)

@app.route("/api/stock-alerts")
def api_stock_alerts():
    low_stock = ProductModel.get_low_stock_products()
    return jsonify(low_stock)

# --- ALMACÉN & AUTHENTICATION ROUTES ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        user = UserModel.authenticate(username, password)
        if user:
            role = str(user.get("rol", "")).strip()
            if role in ["Almacen", "Admin", "Programador", "Propietario", "Supervisor", "Manager"]:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["user_name"] = user["nombre_completo"]
                session["role"] = role
                return redirect(url_for("almacen_portal"))
            else:
                return render_template("login.html", error="Este usuario no tiene permisos de acceso al Portal de Almacén.")
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("whatsapp_portal"))

@app.route("/almacen")
def almacen_portal():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("almacen.html")

@app.route("/api/almacen/movimiento", methods=["POST"])
def api_almacen_movimiento():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "No autorizado. Inicie sesión primero."}), 401
    
    try:
        data = request.get_json() or {}
        producto_id = int(data.get("producto_id"))
        tipo = data.get("tipo_movimiento", "Entrada")
        cantidad = int(data.get("cantidad", 0))
        motivo = data.get("motivo", "").strip() or f"Movimiento móvil ({tipo}) desde Almacén"
        user_id = session["user_id"]

        if cantidad <= 0 and tipo != "Ajuste":
            return jsonify({"success": False, "error": "La cantidad debe ser mayor a 0."}), 400

        if tipo == "Ajuste":
            execute_query("UPDATE productos SET stock_actual = ? WHERE id = ?", (cantidad, producto_id), commit=True)
            execute_query(
                "INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad, motivo, usuario_id) VALUES (?, ?, ?, ?, ?)",
                (producto_id, "Ajuste Manual", cantidad, motivo, user_id),
                commit=True
            )
        elif tipo in ["Entrada", "Entrada Suplidor"]:
            InventoryMovementModel.registrar_movimiento(producto_id, "Entrada Suplidor", cantidad, motivo, user_id)
        else:
            InventoryMovementModel.registrar_movimiento(producto_id, "Salida / Ajuste", cantidad, motivo, user_id)

        return jsonify({"success": True, "message": "Movimiento registrado correctamente."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def run_web_server(port=Config.FLASK_PORT, debug=False):
    print(f"Iniciando Servidor Web Flask para Pedidos WhatsApp & Almacén Móvil en: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    run_web_server(debug=True)
"""

with open('web_app.py', 'w', encoding='utf-8') as f:
    f.write(new_web_app)
print("web_app.py updated with authentication and mobile warehouse routes!")
