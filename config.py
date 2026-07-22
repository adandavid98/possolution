import os

class Config:
    # SQL Server Connection Parameters
    DB_SERVER = os.environ.get("POS_DB_SERVER", r".\SQLEXPRESS")
    DB_NAME = os.environ.get("POS_DB_NAME", "POS_LaRuta_DB")
    DB_USER = os.environ.get("POS_DB_USER", None)  # None for Windows Authentication
    DB_PASSWORD = os.environ.get("POS_DB_PASSWORD", None)
    
    # Drivers available for SQL Server
    PREFERRED_DRIVERS = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 13 for SQL Server",
        "ODBC Driver 11 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server"
    ]

    # App Settings
    APP_NAME = "Minimarket La Ruta del Este - POS & Inventarios"
    FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
    SECRET_KEY = "la_ruta_del_este_secret_key_2026"
