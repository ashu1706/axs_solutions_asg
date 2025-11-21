# backend/agents/synth_agent.py

from typing import Any, Dict, List

class SynthesizerAgent:
    def synthesize(self, question, sql, rows):
        q = question.lower()

        if not rows:
            return "No matching results were returned."

        try:
            # SUM
            if "total" in q or "sum" in q:
                return f"The total sales amount is {rows[0].get('total_sales')}."

            # COUNT
            if "how many" in q or "count" in q:
                return f"The total count is {rows[0].get('count')}."

            # AVG
            if "average" in q or "avg" in q:
                return f"The average sale amount is {rows[0].get('avg_sale')}."

            # Joins & lists
            if "top" in q or "highest" in q:
                return f"The top record is: {rows[0]}"

            if "list" in q or "show" in q:
                return f"Found {len(rows)} records. Example: {rows[0]}"

            # fallback
            return f"Here are {len(rows)} results. Example: {rows[0]}"

        except Exception as e:
            return f"An error occurred while generating the answer: {e}"
