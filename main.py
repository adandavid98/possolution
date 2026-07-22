import sys
import threading
import argparse
from database import test_db_connection
from seed_data import verify_and_seed_data
from web_app import run_web_server
from app_gui import POSApp

def start_web_thread():
    web_thread = threading.Thread(target=run_web_server, kwargs={"port": 5000, "debug": False}, daemon=True)
    web_thread.start()
    print("Servidor Web Flask iniciado en segundo plano (http://localhost:5000)")

def main():
    print("==========================================================")
    print(" MINIMARKET LA RUTA DEL ESTE, S.R.L. - SISTEMA POS")
    print(" Proyecto Integrador I - UTESA | Base de Datos: SQL Server")
    print("==========================================================")

    # 1. Test SQL Server DB Connection
    print("Verificando conexión con Microsoft SQL Server (SSMS)...")
    success, info = test_db_connection()
    if not success:
        print(f"\n[ERROR] No se pudo conectar a SQL Server: {info}")
        print("Asegúrese de que el servicio SQL Server (SQLEXPRESS) esté activo y la BD 'POS_LaRuta_DB' creada.")
        sys.exit(1)
        
    print(f"[OK] Conectado a SQL Server ({info.splitlines()[0]})")
    
    # 2. Verify Seed Data
    verify_and_seed_data()

    # 3. Argument Parser
    parser = argparse.ArgumentParser(description="Launcher del Sistema POS La Ruta del Este")
    parser.add_argument("--web", action="store_true", help="Iniciar solo servidor web Flask")
    parser.add_argument("--desktop", action="store_true", help="Iniciar solo app de escritorio GUI")
    parser.add_argument("--both", action="store_true", help="Iniciar ambos (Desktop GUI + Web Flask)")
    args = parser.parse_args()

    if args.web:
        run_web_server(debug=False)
    elif args.desktop:
        app = POSApp()
        app.mainloop()
    else:
        # Default behavior: Both Desktop GUI and Web Server
        start_web_thread()
        app = POSApp()
        app.mainloop()

if __name__ == "__main__":
    main()
