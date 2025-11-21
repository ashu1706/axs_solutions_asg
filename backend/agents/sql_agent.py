import re
from datetime import date

class SQLAgent:

    def __init__(self):
        pass

    # -----------------------------
    # DATE PARSING HELPERS
    # -----------------------------

    def _year_from_question(self, q):
        m = re.search(r"(20|19)\d{2}", q)
        return int(m.group(0)) if m else None

    def _quarter_from_question(self, q):
        m = re.search(r"q([1-4])\s*(\d{4})", q)
        if not m:
            return None
        q_num = int(m.group(1))
        year = int(m.group(2))
        start_month = (q_num - 1) * 3 + 1
        end_month = start_month + 2
        return year, start_month, end_month

    def _build_date_filters(self, q):
        q_lower = q.lower()
        today = date.today()

        year = self._year_from_question(q_lower)
        quarter = self._quarter_from_question(q_lower)

        if "last year" in q_lower:
            yr = today.year - 1
            return f"{yr}-01-01", f"{yr}-12-31"

        elif quarter:
            y, sm, em = quarter
            return f"{y}-{sm:02d}-01", f"{y}-{em:02d}-31"

        elif year:
            return f"{year}-01-01", f"{year}-12-31"

        return None, None

    # -----------------------------
    # MAIN SQL GENERATOR
    # -----------------------------

    def generate_sql(self, question, schema):
        q = question.lower()
        start_date, end_date = self._build_date_filters(q)

        # ==========================================
        # 1️. DIRECT LOOKUP QUERIES (Simple SELECT *)
        # ==========================================
        if "list customers" in q or "all customers" in q:
            return {"sql": "SELECT * FROM customers;", "params": []}

        if "list employees" in q or "all employees" in q:
            return {"sql": "SELECT * FROM employees;", "params": []}

        if "list products" in q or "all products" in q:
            return {"sql": "SELECT * FROM products;", "params": []}

        if "all sales" in q or "list sales" in q:
            return {"sql": "SELECT * FROM sales;", "params": []}

        # ==========================================
        # 2️. FILTERING / CONDITIONS
        # ==========================================

        # CUSTOMER CITY FILTER
        m = re.search(r"customers from ([a-zA-Z]+)", q)
        if m:
            city = m.group(1)
            sql = "SELECT * FROM customers WHERE city = %s;"
            return {"sql": sql, "params": [city]}

        # EMPLOYEE DEPARTMENT FILTER
        m = re.search(r"employees in (sales|hr|tech|support)", q)
        if m:
            dept = m.group(1).capitalize()
            sql = "SELECT * FROM employees WHERE department = %s;"
            return {"sql": sql, "params": [dept]}

        # PRODUCT PRICE FILTER
        m = re.search(r"products above (\d+)", q)
        if m:
            price = float(m.group(1))
            sql = "SELECT * FROM products WHERE price > %s;"
            return {"sql": sql, "params": [price]}

        # ==========================================
        # 3️. AGGREGATIONS: SUM, AVG, COUNT
        # ==========================================

        # ---- SUM (Total Revenue) ----
        if "total sales" in q or "total revenue" in q or "sum of sales" in q:
            sql = "SELECT SUM(sale_amount) AS total_sales FROM sales"
            if start_date:
                sql += f" WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'"
            return {"sql": sql, "params": []}

        # ---- COUNT (Number of Sales) ----
        if "how many sales" in q or "count sales" in q:
            sql = "SELECT COUNT(*) AS count FROM sales"
            if start_date:
                sql += f" WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'"
            return {"sql": sql, "params": []}

        # ---- AVG (Average Sale Amount) ----
        if "average sale" in q or "avg sale" in q:
            sql = "SELECT AVG(sale_amount) AS avg_sale FROM sales"
            if start_date:
                sql += f" WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'"
            return {"sql": sql, "params": []}

        # ==========================================
        # 4️. TABLE JOINS
        # ==========================================

        # Top employees by sales (JOIN employees + sales)
        if (
            "which employee" in q
            or "employee has the highest" in q
            or "highest sales employee" in q
            or "employee with highest sales" in q
            or "employee has most sales" in q
            or "top employee" in q
):
            sql = """
            SELECT e.id, e.name, e.department, SUM(s.sale_amount) AS total_sales
            FROM employees e
            JOIN sales s ON e.id = s.employee_id
            GROUP BY e.id, e.name, e.department
            ORDER BY total_sales DESC
            LIMIT 1;
            """
            return {"sql": sql, "params": []}
        if "top employees" in q or "highest sales employee" in q:
            sql = """
            SELECT e.id, e.name, e.department, SUM(s.sale_amount) AS total_sales
            FROM employees e
            JOIN sales s ON e.id = s.employee_id
            GROUP BY e.id, e.name, e.department
            ORDER BY total_sales DESC
            LIMIT 5;
            """
            return {"sql": sql, "params": []}

        # Sales with customer names (JOIN customers + sales)
        if "sales with customer names" in q:
            sql = """
            SELECT s.id, c.name AS customer_name, s.sale_amount, s.sale_date
            FROM sales s
            JOIN customers c ON s.customer_id = c.id;
            """
            return {"sql": sql, "params": []}

        # Product revenue (JOIN products + sales)
        if "product with highest revenue" in q or "top product" in q:
            sql = """
            SELECT p.name, SUM(s.sale_amount) AS revenue
            FROM products p
            JOIN sales s ON p.id = s.product_id
            GROUP BY p.name
            ORDER BY revenue DESC
            LIMIT 1;
            """
            return {"sql": sql, "params": []}

        # ==========================================
        # 5️. TEMPORAL QUERIES
        # (Already handled by the date functions)
        # ==========================================

        if "sales last year" in q:
            yr = date.today().year - 1
            sql = f"""
            SELECT SUM(sale_amount) AS total_sales
            FROM sales
            WHERE sale_date BETWEEN '{yr}-01-01' AND '{yr}-12-31';
            """
            return {"sql": sql, "params": []}

        # ==========================================
        # 6. FALLBACK
        # ==========================================

        return {
            "error": "Unsupported query type. Please ask a question related to customers, employees, products, or sales.",
            "sql": None,
            "params": []
}
