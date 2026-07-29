with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_route = """@app.route("/api/version")
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
        "version": Config.APP_VERSION,
        "fecha": "2026-07-28",
        "changelog": ["Versión base del servidor local."],
        "download_url": "",
        "obligatoria": False
    })

@app.route("/api/search")"""

if "@app.route(\"/api/version\")" not in content:
    content = content.replace("@app.route(\"/api/search\")", new_route)
    if "import os" not in content:
        content = "import os\n" + content
    with open('web_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("web_app.py updated with /api/version route!")
else:
    print("/api/version already in web_app.py")
