from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from agents.schema_agent import SchemaAgent
from agents.sql_agent import SQLAgent
from agents.retriever_agent import RetrieverAgent
from agents.synth_agent import SynthesizerAgent

import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "ragdb"),
    "user": os.getenv("DB_USER", "rag_user"),
    "password": os.getenv("DB_PASSWORD", "Rag@123"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

app = FastAPI(title="Multi-Agent RAG NL-to-SQL System")

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
schema_agent = SchemaAgent()
sql_agent = SQLAgent()
retriever_agent = RetrieverAgent(DB_CONFIG)
synth_agent = SynthesizerAgent()


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: AskRequest):
    question = req.question.strip()

    if not question:
        return {
            "answer": "Please provide a valid question.",
            "error": "Empty question.",
            "steps": {
                "schema_used": None,
                "generated_sql": None,
                "result_rows": None
            }
        }

    # Step 1 — Schema Agent
    relevant = schema_agent.identify_relevant_tables(question)

    if not relevant:
        return {
            "answer": "I couldn't find any relevant tables for your question.",
            "error": "Schema or table not found.",
            "steps": {
                "schema_used": None,
                "generated_sql": None,
                "result_rows": None
            }
        }

    # Step 2 — SQL Agent
    sql_data = sql_agent.generate_sql(question, relevant)

    if sql_data.get("error"):
        return {
            "answer": "Sorry, I could not understand your question or generate SQL.",
            "error": sql_data["error"],
            "steps": {
                "schema_used": relevant,
                "generated_sql": None,
                "result_rows": None
            }
        }

    sql = sql_data.get("sql")
    params = sql_data.get("params", [])

    # Step 3 — Retriever (DB Execution)
    db_output = retriever_agent.execute_query(sql, params)

    if db_output.get("error"):
        return {
            "answer": "There was an error while running your SQL query.",
            "error": db_output["error"],
            "steps": {
                "schema_used": relevant,
                "generated_sql": sql,
                "result_rows": None
            }
        }

    rows = db_output.get("rows", [])

    # Step 4 — Handle NO MATCH FOUND
    if len(rows) == 0:
        return {
            "answer": "No matching records found for your question.",
            "error": None,
            "steps": {
                "schema_used": relevant,
                "generated_sql": sql,
                "result_rows": []
            }
        }

    # Step 5 — Synthesize natural answer
    answer = synth_agent.synthesize(question, sql, rows)

    return {
        "answer": answer,
        "error": None,
        "steps": {
            "schema_used": relevant,
            "generated_sql": sql,
            "result_rows": rows
        }
    }

    # Make rows JSON-serializable (convert e.g., date to string)
    def serialize_row(row):
        return {k: (str(v) if not isinstance(v, (int, float, type(None))) else v) for k, v in row.items()}

    serialized_rows = [serialize_row(r) for r in rows]

    return {
        "answer": answer,
        "error": None,
        "steps": {
            "schema_used": relevant_schema,
            "generated_sql": sql,
            "result_rows": serialized_rows,
        },
    }


@app.get("/")
def root():
    return {"message": "Multi-Agent RAG NL-to-SQL API. Use POST /ask with a question."}
