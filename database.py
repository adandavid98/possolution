import pyodbc
from config import Config

def get_installed_driver():
    """Finds the first available SQL Server ODBC driver on the system."""
    available_drivers = pyodbc.drivers()
    for driver in Config.PREFERRED_DRIVERS:
        if driver in available_drivers:
            return driver
    # Fallback to standard SQL Server driver if none match specifically
    return "SQL Server"

def get_connection():
    """Establishes and returns a pyodbc connection to Microsoft SQL Server."""
    driver = get_installed_driver()
    
    if Config.DB_USER and Config.DB_PASSWORD:
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_NAME};"
            f"UID={Config.DB_USER};"
            f"PWD={Config.DB_PASSWORD};"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    else:
        # Windows Authentication (Trusted_Connection)
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_NAME};"
            f"Trusted_Connection=yes;"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    
    return pyodbc.connect(conn_str)

def execute_query(sql, params=(), fetch_one=False, fetch_all=False, commit=False):
    """
    Executes a SQL statement with pyodbc.
    Returns list of dicts for SELECT, affected count for DML, or single dict for fetch_one.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        
        result = None
        if fetch_one:
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, row))
        elif fetch_all:
            rows = cursor.fetchall()
            if rows:
                columns = [column[0] for column in cursor.description]
                result = [dict(zip(columns, row)) for row in rows]
            else:
                result = []
        elif commit:
            conn.commit()
            result = cursor.rowcount
            
        return result
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def test_db_connection():
    """Tests connection to SQL Server and returns version string."""
    try:
        res = execute_query("SELECT @@VERSION AS version", fetch_one=True)
        return True, res["version"]
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, info = test_db_connection()
    if success:
        print("Conexión exitosa a SQL Server!")
        print("Versión:", info.split('\n')[0])
    else:
        print("Error al conectar con SQL Server:", info)
