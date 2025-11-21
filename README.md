# title: Multi-Agent RAG System for Natural Language Querying of a Relational Database
## description: 
  A multi-agent Retrieval-Augmented Generation (RAG) system that interprets
  natural language questions, generates SQL queries, executes them on PostgreSQL,
  and synthesizes human-readable answers. Includes a FastAPI backend, PostgreSQL 
  database, and a simple HTML frontend.

## overview:
  - The system interprets natural language queries.
  - Generates SQL queries using multi-agent processing.
  - Retrieves results from a PostgreSQL database.
  - Synthesizes human-readable answers.
  - Provides POST /ask API endpoint.
  - Includes web interface for user queries.

## architecture:
  schema_agent:
    description: Identifies relevant tables and fields based on query keywords.
    tasks:
      - Uses predefined static schema for reasoning.
      - Helps SQL Agent determine which tables to use.

  sql_generator_agent:
    description: Converts natural language + schema context into SQL queries.
    supports:
      - direct_lookup
      - filtering
      - aggregations (SUM, AVG, COUNT)
      - joins
      - temporal_references (last year, Q1 2023)

  retriever_agent:
    description: Executes SQL queries using psycopg2.
    tasks:
      - Runs SQL securely
      - Returns result rows
      - Handles PostgreSQL errors

  synthesizer_agent:
    description: Turns raw SQL results into natural-language answers.
    tasks:
      - Builds summary responses
      - Handles lists, rankings, aggregates
      - Provides fallback templates

tech_stack:
  backend: Python, FastAPI, psycopg2
  database: PostgreSQL
  frontend: HTML, JavaScript (Fetch API)

## setup_instructions:

  database:
    steps:
      - Create the database using:
      - |
        CREATE DATABASE ragdb;

      - Apply schema using:
      - |
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            city VARCHAR(100),
            age INT
        );

        CREATE TABLE employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(100),
            joining_date DATE
        );

        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(100),
            price NUMERIC(10,2)
        );

        CREATE TABLE sales (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES customers(id),
            employee_id INT REFERENCES employees(id),
            product_id INT REFERENCES products(id),
            quantity INT NOT NULL,
            sale_amount NUMERIC(10,2) NOT NULL,
            sale_date DATE NOT NULL
        );

      - Seed synthetic data:
      - "python backend/db/seed_data.py"

  ## backend:
    steps:
      - Navigate to backend folder:
      - "cd backend"
      - Create venv:
      - "python -m venv venv"
      - Activate venv:
      - ".\\venv\\Scripts\\activate"
      - Install dependencies:
      - "pip install -r requirements.txt"
      - Start server:
      - "uvicorn main:app --reload"

  ## frontend:
    steps:
      - Open:
      - "frontend/index.html"

api_examples:
  endpoint: POST /ask
  request_example: |
    {
      "question": "What is the total sales last year?"
    }
  response_example: |
    {
      "answer": "The total sales amount is 51344636.63.",
      "error": null,
      "steps": {
        "schema_used": { "sales": ["id", "customer_id", "sale_amount"] },
        "generated_sql": "SELECT SUM(sale_amount) ...",
        "result_rows": [
          { "total_sales": "51344636.63" }
        ]
      }
    }

## supported_query_types:
  - Direct lookup:
      - List all customers
      - Show all employees
      - List all products

  - Filtering and conditions:
      - Customers from Mumbai
      - Products above 50000
      - Employees in Sales department

  - Aggregations:
      - Total sales last year
      - Count of sales in 2023
      - Average sale amount in 2024

  - Table joins:
      - Employee with highest sales
      - Product with highest revenue
      - Sales with customer names

  - Temporal queries:
      - Sales last year
      - Sales in Q1 2023
      - Sales in 2024

## error_handling:
  description: The system safely handles all error conditions.
  handles:
    - Missing schema/table
    - SQL generation errors
    - SQL execution errors
    - No matching records
    - Invalid or empty questions
