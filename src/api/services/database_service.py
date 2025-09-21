import sqlite3
from typing import Optional


class DatabaseService:
    def __init__(self, db_path: str = "ecommerce_research.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self) -> None:
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                analysis_id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                report TEXT,
                error TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_analysis(self, **kwargs) -> None:
        conn = self._get_connection()
        conn.execute(
            """
            INSERT INTO analysis_history 
            (analysis_id, query, status, created_at, completed_at, report, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                kwargs.get("analysis_id"),
                kwargs.get("query"),
                kwargs.get("status"),
                kwargs.get("created_at"),
                kwargs.get("completed_at"),
                kwargs.get("report"),
                kwargs.get("error"),
            ),
        )
        conn.commit()
        conn.close()

    def get_analysis(self, analysis_id: str) -> Optional[dict]:
        conn = self._get_connection()
        result = conn.execute(
            """
            SELECT analysis_id, query, status, created_at, completed_at, report, error
            FROM analysis_history 
            WHERE analysis_id = ?
        """,
            (analysis_id,),
        ).fetchone()
        conn.close()

        if result:
            return dict(result)
        return None

    def get_all_analyses(self) -> list[dict]:
        conn = self._get_connection()
        results = conn.execute("""
            SELECT analysis_id, query, status, created_at, completed_at, report, error
            FROM analysis_history 
            ORDER BY created_at DESC
        """).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def update_analysis(self, analysis_id: str, **kwargs) -> None:
        conn = self._get_connection()

        set_clauses = []
        values = []

        for key, value in kwargs.items():
            if key != "analysis_id":  # Don't update the ID
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if set_clauses:
            query = f"UPDATE analysis_history SET {', '.join(set_clauses)} WHERE analysis_id = ?"
            values.append(analysis_id)
            conn.execute(query, values)
            conn.commit()

        conn.close()


db_service = DatabaseService()
