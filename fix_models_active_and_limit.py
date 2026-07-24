with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_recent and search_live methods
old_methods = """    @staticmethod
    def get_recent(limit=40, active_only=False):
        \"\"\"Returns the most recently added/modified products (for fast initial load).\"\"\"
        extra = "AND p.estado = 'Activo'" if active_only else ""
        sql = f\"\"\"
            SELECT TOP {limit} p.*,
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre,
                   c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE 1=1 {extra}
            ORDER BY p.id DESC
        \"\"\"
        return execute_query(sql, (), fetch_all=True) or []

    @staticmethod
    def search_live(term, limit=100, active_only=False, subdep_id=None):
        \"\"\"SQL-level live search — fast even with 100,000+ products.\"\"\"
        t = f"%{term}%"
        conditions = ["(p.nombre LIKE ? OR p.codigo_barras LIKE ?)"]
        params = [t, t]

        if active_only:
            conditions.append("p.estado = 'Activo'")
        if subdep_id:
            conditions.append("p.subdepartamento_id = ?")
            params.append(subdep_id)

        where = " AND ".join(conditions)
        sql = f\"\"\"
            SELECT TOP {limit} p.*,
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre,
                   c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE {where}
            ORDER BY p.nombre ASC
        \"\"\"
        return execute_query(sql, tuple(params), fetch_all=True) or []"""

new_methods = """    @staticmethod
    def get_recent(limit=20, active_only=False):
        \"\"\"Returns the top initial essential products (limit 20).\"\"\"
        extra = "AND (p.estado IS NULL OR p.estado = '' OR p.estado = 'Activo')" if active_only else ""
        sql = f\"\"\"
            SELECT TOP {limit} p.*,
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre,
                   c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE 1=1 {extra}
            ORDER BY p.nombre ASC
        \"\"\"
        return execute_query(sql, (), fetch_all=True) or []

    @staticmethod
    def search_live(term="", limit=100, active_only=False, subdep_id=None):
        \"\"\"SQL-level live search — handles search terms and subdepartment filtering.\"\"\"
        conditions = []
        params = []

        if term:
            t = f"%{term}%"
            conditions.append("(p.nombre LIKE ? OR p.codigo_barras LIKE ?)")
            params.extend([t, t])

        if active_only:
            conditions.append("(p.estado IS NULL OR p.estado = '' OR p.estado = 'Activo')")

        if subdep_id is not None:
            conditions.append("p.subdepartamento_id = ?")
            params.append(subdep_id)

        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        eff_limit = limit if (term or subdep_id is not None) else 20

        sql = f\"\"\"
            SELECT TOP {eff_limit} p.*,
                   sd.nombre AS subdepartamento_nombre,
                   d.nombre AS departamento_nombre,
                   c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN subdepartamentos sd ON p.subdepartamento_id = sd.id
            LEFT JOIN departamentos d ON sd.departamento_id = d.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            {where}
            ORDER BY p.nombre ASC
        \"\"\"
        return execute_query(sql, tuple(params), fetch_all=True) or []"""

if old_methods in content:
    content = content.replace(old_methods, new_methods)
    print("models.py ProductModel methods updated successfully!")
else:
    print("WARNING: old_methods block not found exactly in models.py")

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content)
