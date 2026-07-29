import os

# 1. Update app_gui.py
with open('app_gui.py', 'r', encoding='utf-8') as f:
    gui_code = f.read()

dynamic_func = """def get_dynamic_logo_path():
    \"\"\"Dynamically looks for logo.png, logo.jpg, logo.jpeg, logo.webp in external assets directory first, then fallback.\"\"\"
    possible_names = ["logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "logo.bmp"]
    
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    ext_assets = os.path.join(exe_dir, "assets")
    cwd_assets = os.path.join(os.getcwd(), "assets")
    
    for folder in [ext_assets, cwd_assets]:
        if os.path.exists(folder):
            for fname in possible_names:
                full_p = os.path.join(folder, fname)
                if os.path.exists(full_p):
                    return full_p

    if hasattr(sys, '_MEIPASS'):
        for fname in possible_names:
            full_p = os.path.join(sys._MEIPASS, "assets", fname)
            if os.path.exists(full_p):
                return full_p

    return get_asset_path(os.path.join("assets", "logo.jpg"))

"""

if "def get_dynamic_logo_path():" not in gui_code:
    gui_code = gui_code.replace("def get_asset_path(relative_path):", dynamic_func + "def get_asset_path(relative_path):")

gui_code = gui_code.replace('logo_path = get_asset_path(os.path.join("assets", "logo.jpg"))', 'logo_path = get_dynamic_logo_path()')

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(gui_code)

print("app_gui.py updated with get_dynamic_logo_path()!")

# 2. Update web_app.py
with open('web_app.py', 'r', encoding='utf-8') as f:
    web_code = f.read()

route_code = """import sys
from flask import send_from_directory

@app.route('/assets/<path:filename>')
def serve_custom_assets(filename):
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(exe_dir, "assets")
    if not os.path.exists(assets_dir):
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    return send_from_directory(assets_dir, filename)
"""

if "serve_custom_assets" not in web_code:
    web_code = web_code + "\n\n" + route_code
    with open('web_app.py', 'w', encoding='utf-8') as f:
        f.write(web_code)

print("web_app.py updated with dynamic /assets/<filename> route!")
