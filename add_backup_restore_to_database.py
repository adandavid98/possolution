with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

backup_restore_code = """
def backup_database_sqlserver(destination_path):
    \"\"\"Generates a native SQL Server database backup (.bak) to destination_path.\"\"\"
    driver = get_installed_driver()
    if Config.DB_USER and Config.DB_PASSWORD:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"UID={Config.DB_USER};"
            f"PWD={Config.DB_PASSWORD};"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    else:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    
    conn = pyodbc.connect(master_str, autocommit=True)
    cursor = conn.cursor()
    try:
        clean_path = destination_path.replace("'", "''")
        db_name = Config.DB_NAME
        sql = f"BACKUP DATABASE [{db_name}] TO DISK = '{clean_path}' WITH FORMAT, INIT, NAME = 'POS_LaRuta_DB-Full Backup';"
        cursor.execute(sql)
        return True, "Respaldo generado con éxito."
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def restore_database_sqlserver(backup_path):
    \"\"\"Restores SQL Server POS_LaRuta_DB from a .bak file.\"\"\"
    driver = get_installed_driver()
    if Config.DB_USER and Config.DB_PASSWORD:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"UID={Config.DB_USER};"
            f"PWD={Config.DB_PASSWORD};"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )
    else:
        master_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
            f"Encrypt=no;TrustServerCertificate=yes;"
        )

    conn = pyodbc.connect(master_str, autocommit=True)
    cursor = conn.cursor()
    try:
        clean_path = backup_path.replace("'", "''")
        db_name = Config.DB_NAME
        
        # Set DB to single user to terminate active connections
        cursor.execute(f"IF EXISTS (SELECT * FROM sys.databases WHERE name = '{db_name}') ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;")
        
        # Restore database
        cursor.execute(f"RESTORE DATABASE [{db_name}] FROM DISK = '{clean_path}' WITH REPLACE;")
        
        # Set DB back to multi user
        cursor.execute(f"ALTER DATABASE [{db_name}] SET MULTI_USER;")
        
        return True, "Base de datos restaurada con éxito."
    except Exception as e:
        try:
            cursor.execute(f"ALTER DATABASE [{Config.DB_NAME}] SET MULTI_USER;")
        except Exception:
            pass
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
"""

if "def backup_database_sqlserver" not in content:
    content += backup_restore_code
    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("database.py updated with backup and restore methods!")
else:
    print("backup methods already exist in database.py")
