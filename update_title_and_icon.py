import os

# --- 1. UPDATE config.py ---
with open('config.py', 'r', encoding='utf-8') as f:
    cfg_content = f.read()

cfg_content = cfg_content.replace('APP_NAME = "Minimarket La Ruta del Este - POS & Inventarios"', 'APP_NAME = "POS-SOLUTION"')
with open('config.py', 'w', encoding='utf-8') as f:
    f.write(cfg_content)
print("config.py updated with APP_NAME = 'POS-SOLUTION'!")

# --- 2. UPDATE main.py ---
with open('main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

win_id_code = """def main():
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("pos.solution.app.v1")
    except Exception:
        pass
"""

if "SetCurrentProcessExplicitAppUserModelID" not in main_content:
    main_content = main_content.replace("def main():", win_id_code)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(main_content)
    print("main.py updated with Windows AppUserModelID!")

# --- 3. UPDATE app_gui.py ---
with open('app_gui.py', 'r', encoding='utf-8') as f:
    gui_content = f.read()

old_title = 'self.title("Minimarket La Ruta del Este - POS & Inventarios (SQL Server)")'
new_title = """app_v = getattr(Config, 'APP_VERSION', '1.0.0')
        self.title(f"POS-SOLUTION v{app_v}")
        ico_path = get_asset_path("app_icon.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass"""

if old_title in gui_content:
    gui_content = gui_content.replace(old_title, new_title)
    with open('app_gui.py', 'w', encoding='utf-8') as f:
        f.write(gui_content)
    print("app_gui.py updated with new window title 'POS-SOLUTION v1.0.0' and app_icon.ico!")

# --- 4. UPDATE build_exe.py ---
with open('build_exe.py', 'r', encoding='utf-8') as f:
    bld_content = f.read()

if '"--icon=assets/app_icon.ico"' not in bld_content:
    bld_content = bld_content.replace('"--windowed",', '"--windowed",\n        "--icon=assets/app_icon.ico",')
    with open('build_exe.py', 'w', encoding='utf-8') as f:
        f.write(bld_content)
    print("build_exe.py updated with --icon=assets/app_icon.ico!")
