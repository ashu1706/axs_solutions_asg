import random
from datetime import date, timedelta
import psycopg2
from faker import Faker

# 🔧 Adjust DB credentials as needed
DB_NAME = "ragdb"
DB_USER = "postgres"
DB_PASSWORD = "yourpassword"
DB_HOST = "localhost"
DB_PORT = "5432"

fake = Faker()

def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

def seed():
    conn = get_conn()
    cur = conn.cursor()

    # Clear tables
    cur.execute("DELETE FROM sales;")
    cur.execute("DELETE FROM products;")
    cur.execute("DELETE FROM employees;")
    cur.execute("DELETE FROM customers;")

    # Seed customers
    customers = []
    for _ in range(200):
        name = fake.name()
        city = random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad"])
        age = random.randint(20, 65)
        customers.append((name, city, age))
    cur.executemany(
        "INSERT INTO customers (name, city, age) VALUES (%s, %s, %s);",
        customers,
    )

    # Seed employees
    employees = []
    for _ in range(50):
        name = fake.name()
        dept = random.choice(["Sales", "Support", "HR", "Tech"])
        join_date = fake.date_between(start_date="-5y", end_date="today")
        employees.append((name, dept, join_date))
    cur.executemany(
        "INSERT INTO employees (name, department, joining_date) VALUES (%s, %s, %s);",
        employees,
    )

    # Seed products
    products = []
    for _ in range(50):
        name = random.choice(["Laptop", "Phone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse"]) + " " + fake.color_name()
        category = random.choice(["Electronics", "Accessories"])
        price = round(random.uniform(1000, 100000), 2)
        products.append((name, category, price))
    cur.executemany(
        "INSERT INTO products (name, category, price) VALUES (%s, %s, %s);",
        products,
    )

    # Get IDs
    cur.execute("SELECT id FROM customers;")
    customer_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id FROM employees;")
    employee_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id FROM products;")
    product_ids = [row[0] for row in cur.fetchall()]

    # Seed sales (e.g., 1000 rows)
    sales = []
    today = date.today()
    for _ in range(1000):
        customer_id = random.choice(customer_ids)
        employee_id = random.choice(employee_ids)
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 5)
        base_price = random.uniform(1000, 100000)
        sale_amount = round(base_price * quantity, 2)

        # Random date in last 3 years
        delta_days = random.randint(0, 3 * 365)
        sale_date = today - timedelta(days=delta_days)
        sales.append((customer_id, employee_id, product_id, quantity, sale_amount, sale_date))

    cur.executemany(
        """
        INSERT INTO sales (customer_id, employee_id, product_id, quantity, sale_amount, sale_date)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        sales,
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Seeded data successfully.")

if __name__ == "__main__":
    seed()
