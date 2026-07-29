"""Patch models.py to ensure search_live and get_by_id include departamento_nombre."""
with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_search_live = 'sql = "SELECT TOP (?) p.*, s.nombre as subdepartamento_nombre FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id WHERE 1=1"'
new_search_live = 'sql = "SELECT TOP (?) p.*, s.nombre as subdepartamento_nombre, d.nombre as departamento_nombre, d.id as departamento_id FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id LEFT JOIN departamentos d ON s.departamento_id = d.id WHERE 1=1"'

old_get_by_id = 'sql = "SELECT * FROM productos WHERE id = ?"'
new_get_by_id = 'sql = "SELECT p.*, s.nombre as subdepartamento_nombre, d.nombre as departamento_nombre, d.id as departamento_id FROM productos p LEFT JOIN subdepartamentos s ON p.subdepartamento_id = s.id LEFT JOIN departamentos d ON s.departamento_id = d.id WHERE p.id = ?"'

code = code.replace(old_search_live, new_search_live)
code = code.replace(old_get_by_id, new_get_by_id)

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("models.py successfully updated with department joins in search_live and get_by_id!")
