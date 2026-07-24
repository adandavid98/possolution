from flask import Flask, render_template, request, jsonify
from config import Config
from models import ProductModel
from database import get_active_db_type

app = Flask(__name__)
app.config.from_object(Config)

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

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    products = ProductModel.get_all(query)
    return jsonify(products)

@app.route("/api/stock-alerts")
def api_stock_alerts():
    low_stock = ProductModel.get_low_stock_products()
    return jsonify(low_stock)

def run_web_server(port=Config.FLASK_PORT, debug=False):
    print(f"Iniciando Servidor Web Flask para Pedidos WhatsApp en: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    run_web_server(debug=True)
