import re

class SQLGeneratorAgent:
    def __init__(self, schema):
        self.schema = schema

    def generate_sql(self, question: str):
        q = question.lower().strip()

        # ===========================================================
        # 1. DIRECT LOOKUPS
        # ===========================================================
        if "list all customers" in q or "show all customers" in q:
            return {"sql": "SELECT * FROM customers;", "params": []}

        if "list all employees" in q or "show all employees" in q:
            return {"sql": "SELECT * FROM employees;", "params": []}

        if "list all products" in q or "show all products" in q:
            return {"sql": "SELECT * FROM products;", "params": []}

        # ===========================================================
        # 2. FILTERING & CONDITIONS
        # ===========================================================
        if "customers from" in q:
            city = q.split("from")[-1].strip()
            return {
                "sql": "SELECT * FROM customers WHERE LOWER(city) = LOWER(%s);",
                "params": [city],
            }

        if "products above" in q:
            price = re.findall(r"\d+", q)
            if price:
                return {
                    "sql": "SELECT * FROM products WHERE price > %s;",
                    "params": [int(price[0])]
                }

        if "employees in" in q:
            department = q.split("in")[-1].strip()
            return {
                "sql": "SELECT * FROM employees WHERE LOWER(department) = LOWER(%s);",
                "params": [department],
            }

        # ===========================================================
        # 3. AGGREGATIONS
        # ===========================================================

        # Total sales last year
        if "total sales last year" in q:
            return {
                "sql": """
                    SELECT SUM(sale_amount) AS total_sales
                    FROM sales
                    WHERE sale_date BETWEEN
                    DATE_TRUNC('year', CURRENT_DATE - INTERVAL '1 year') AND
                    DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1 day';
                """,
                "params": []
            }

        # Count of sales in a specific year
        if "count of sales" in q or "how many sales" in q:
            year = re.findall(r"\d{4}", q)
            if year:
                yr = int(year[0])
                return {
                    "sql": f"""
                        SELECT COUNT(*) AS total_sales
                        FROM sales
                        WHERE DATE_PART('year', sale_date) = {yr};
                    """,
                    "params": []
                }

        # Average sale amount for a specific year
        if "average sale" in q or "avg sale" in q:
            year = re.findall(r"\d{4}", q)
            if year:
                yr = int(year[0])
                return {
                    "sql": f"""
                        SELECT AVG(sale_amount) AS avg_sale
                        FROM sales
                        WHERE DATE_PART('year', sale_date) = {yr};
                    """,
                    "params": []
                }

        # ===========================================================
        # 4. TABLE JOINS
        # ===========================================================

        # Employee with highest sales
        if "employee with highest sales" in q or "highest sales employee" in q:
            return {
                "sql": """
                    SELECT e.id, e.name, e.department,
                           SUM(s.sale_amount) AS total_sales
                    FROM employees e
                    JOIN sales s ON e.id = s.employee_id
                    GROUP BY e.id, e.name, e.department
                    ORDER BY total_sales DESC
                    LIMIT 1;
                """,
                "params": []
            }

        # Product with highest revenue
        if "product with highest revenue" in q:
            return {
                "sql": """
                    SELECT p.id, p.name, p.category,
                           SUM(s.sale_amount) AS total_revenue
                    FROM products p
                    JOIN sales s ON p.id = s.product_id
                    GROUP BY p.id, p.name, p.category
                    ORDER BY total_revenue DESC
                    LIMIT 1;
                """,
                "params": []
            }

        # Sales with customer names
        if "sales with customer names" in q or "show sales with customers" in q:
            return {
                "sql": """
                    SELECT s.id, c.name AS customer_name, s.sale_amount, s.sale_date
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.id;
                """,
                "params": []
            }

        # ===========================================================
        # 5. TEMPORAL QUERIES
        # ===========================================================

        # Sales last year
        if "sales last year" in q:
            return {
                "sql": """
                    SELECT *
                    FROM sales
                    WHERE DATE_PART('year', sale_date) = DATE_PART('year', CURRENT_DATE) - 1;
                """,
                "params": []
            }

        # Sales in specific year
        if "sales in" in q:
            year = re.findall(r"\d{4}", q)
            if year:
                return {
                    "sql": f"SELECT * FROM sales WHERE DATE_PART('year', sale_date) = {year[0]};",
                    "params": []
                }

        # Sales in Q1 2023, Q2 2024, etc.
        if "q1" in q or "q2" in q or "q3" in q or "q4" in q:
            quarter = q[q.index("q")+1]
            year = re.findall(r"\d{4}", q)[0]

            return {
                "sql": f"""
                    SELECT *
                    FROM sales
                    WHERE DATE_PART('year', sale_date) = {year}
                    AND DATE_PART('quarter', sale_date) = {quarter};
                """,
                "params": []
            }

        # ===========================================================
        # IF NOTHING MATCHES
        # ===========================================================

        return {
            "sql": None,
            "params": [],
            "error": "Unsupported query type. Please ask about customers, employees, products, or sales."
        }
