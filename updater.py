import os
import json
import threading
import urllib.request
import urllib.error
import subprocess
import sys
import zipfile
import shutil
from config import Config

def parse_version_tuple(v_str):
    try:
        clean = v_str.strip().lstrip("vV")
        return tuple(int(x) for x in clean.split(".") if x.isdigit())
    except Exception:
        return (0, 0, 0)

class UpdateChecker:
    """Non-blocking background update checker with dual source (GitHub + Local Server fallback)."""
    
    @staticmethod
    def fetch_version_info():
        """Attempts to fetch version manifest from GitHub first, then Local Server."""
        urls = [
            ("GitHub", getattr(Config, "UPDATE_CHECK_URL_GITHUB", "")),
            ("Servidor Local", getattr(Config, "UPDATE_CHECK_URL_LOCAL", ""))
        ]

        for source_name, url in urls:
            if not url:
                continue
            try:
                req = urllib.request.Request(
                    url, 
                    headers={"User-Agent": "POS-Update-Checker/1.0", "Accept": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        data["source"] = source_name
                        return True, data
            except Exception:
                continue

        return False, None

    @classmethod
    def check_updates_async(cls, callback_on_main_thread, root_widget):
        """Runs the update check in a background thread without blocking the GUI startup."""
        def _bg_task():
            success, data = cls.fetch_version_info()
            if success and data:
                remote_ver = data.get("version", "1.0.0")
                local_ver = getattr(Config, "APP_VERSION", "1.0.0")
                
                if parse_version_tuple(remote_ver) > parse_version_tuple(local_ver):
                    # Trigger UI modal on Tkinter main thread safely
                    root_widget.after(0, lambda: callback_on_main_thread(data))

        t = threading.Thread(target=_bg_task, daemon=True)
        t.start()

    @staticmethod
    def launch_updater_and_exit(downloaded_zip_path):
        """Launches updater.bat script to replace binary files and restart POS_LaRuta_Este.exe."""
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        bat_script = os.path.join(app_dir, "updater.bat")
        exe_name = "POS_LaRuta_Este.exe"

        bat_content = f"""@echo off
title Actualizando Sistema POS Minimarket La Ruta del Este...
echo ==================================================
echo   ACTUALIZANDO SISTEMA POS & INVENTARIOS
echo ==================================================
echo Esperando a que el sistema se cierre...
timeout /t 2 /nobreak > nul

taskkill /F /IM {exe_name} 2>nul
timeout /t 1 /nobreak > nul

echo Descomprimiendo y reemplazando archivos...
powershell -Command "Expand-Archive -Path '{downloaded_zip_path}' -DestinationPath '{app_dir}' -Force"

echo ==================================================
echo   ¡ACTUALIZACIÓN COMPLETADA CON ÉXITO!
echo ==================================================
timeout /t 1 /nobreak > nul

if exist "{os.path.join(app_dir, exe_name)}" (
    start "" "{os.path.join(app_dir, exe_name)}"
) else (
    echo Iniciando aplicacion...
    start "" "{sys.executable}" main.py
)

del "%~f0"
exit
"""
        with open(bat_script, "w", encoding="utf-8") as f:
            f.write(bat_content)

        subprocess.Popen(["cmd.exe", "/c", bat_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        sys.exit(0)
