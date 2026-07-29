import os

class Config:
    # App Version & Auto-Update URLs
    APP_VERSION = "1.0.0"
    UPDATE_CHECK_URL_GITHUB = "https://raw.githubusercontent.com/adanozoria/Anti-POS_Project/main/version.json"
    UPDATE_CHECK_URL_LOCAL = "http://10.0.0.101:5000/api/version"

    # SQL Server Connection Parameters
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
    APP_NAME = "POS-SOLUTION"
    FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
    SECRET_KEY = "la_ruta_del_este_secret_key_2026"
