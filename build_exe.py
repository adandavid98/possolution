import os
import shutil
import subprocess
import sys

def build_executable():
    print("==================================================")
    print(" Compilando Sistema POS & Inventarios a .EXE")
    print(" Minimarket La Ruta del Este (PyInstaller)")
    print("==================================================")

    # Terminate any running instances of POS_LaRuta_Este.exe to release file locks
    try:
        subprocess.run(["taskkill", "/F", "/IM", "POS_LaRuta_Este.exe"], capture_output=True)
    except Exception:
        pass

    # Clean build directory if exists
    if os.path.exists("build"):
        try:
            shutil.rmtree("build")
        except Exception as e:
            print("Warning cleaning build directory:", e)

    # PyInstaller Arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--icon=assets/app_icon.ico",
        "--name=POS_LaRuta_Este",
        "--add-data=templates;templates",
        "--add-data=assets;assets",
        "--add-data=Script_BaseDeDatos_SSMS.sql;.",
        "main.py"
    ]

    print("Ejecutando comando PyInstaller...")
    print(" ".join(cmd))
    res = subprocess.run(cmd)

    if res.returncode == 0:
        print("\n¡Compilacion exitosa!")
        print(f"El ejecutable se encuentra en: {os.path.abspath('dist/POS_LaRuta_Este/POS_LaRuta_Este.exe')}")
    else:
        print("\nError al compilar el proyecto a ejecutable.")

if __name__ == "__main__":
    build_executable()
