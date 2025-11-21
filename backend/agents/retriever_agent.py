import psycopg2
from psycopg2.extras import RealDictCursor

class RetrieverAgent:
    def __init__(self, db_config):
        # IMPORTANT: Store db_config
        self.db = db_config

    def execute_query(self, sql, params=None):
        try:
            conn = psycopg2.connect(**self.db)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(sql, params or [])
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return {"rows": rows}

        except psycopg2.Error as e:
            return {"error": f"Database execution error: {str(e)}"}

        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
