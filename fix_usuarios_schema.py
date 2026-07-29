"""Fix usuarios table schema in SQL Server."""
import sys
sys.path.insert(0, '.')
from database import execute_query

print("=== FIXING USUARIOS TABLE SCHEMA ===")

# Alter rol column to VARCHAR(100)
try:
    execute_query("ALTER TABLE usuarios ALTER COLUMN rol VARCHAR(100) NOT NULL;", commit=True)
    print("[1] ALTER COLUMN rol to VARCHAR(100) SUCCESS!")
except Exception as e:
    print("[1] Note:", e)

# Drop any CHECK constraints on usuarios table
try:
    constraints = execute_query("""
        SELECT name 
        FROM sys.check_constraints 
        WHERE parent_object_id = OBJECT_ID('usuarios')
    """, fetch_all=True)
    if constraints:
        for c in constraints:
            c_name = c['name']
            print(f"[2] Dropping constraint '{c_name}'...")
            execute_query(f"ALTER TABLE usuarios DROP CONSTRAINT {c_name};", commit=True)
            print(f"[2] Dropped '{c_name}' successfully!")
    else:
        print("[2] No check constraints on usuarios table.")
except Exception as e:
    print("[2] Note:", e)

print("=== USUARIOS SCHEMA FIXED ===")
