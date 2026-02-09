import os
import sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL")

CATEGORIES = ["Ruofei", "Ruiqi", "Family"]

# --- Database abstraction: PostgreSQL (cloud) or SQLite (local) ---

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras

    def _get_conn():
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn

    def _fetchall(cursor) -> list[dict]:
        cols = [desc[0] for desc in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def _fetchone(cursor) -> dict | None:
        cols = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        return dict(zip(cols, row)) if row else None

    def init_db() -> None:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                category TEXT NOT NULL DEFAULT 'Family',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.close()

    def get_todos(category: str | None = None) -> list[dict]:
        conn = _get_conn()
        cur = conn.cursor()
        if category:
            cur.execute(
                "SELECT id, title, completed, category, created_at FROM todos "
                "WHERE category = %s ORDER BY created_at DESC", (category,)
            )
        else:
            cur.execute(
                "SELECT id, title, completed, category, created_at FROM todos "
                "ORDER BY created_at DESC"
            )
        result = _fetchall(cur)
        conn.close()
        return result

    def add_todo(title: str, category: str = "Family") -> dict:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO todos (title, category) VALUES (%s, %s) RETURNING id, title, completed, category, created_at",
            (title, category),
        )
        result = _fetchone(cur)
        conn.close()
        return result

    def toggle_todo(todo_id: int) -> dict | None:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE todos SET completed = NOT completed WHERE id = %s "
            "RETURNING id, title, completed, category, created_at",
            (todo_id,),
        )
        result = _fetchone(cur)
        conn.close()
        return result

    def update_todo(todo_id: int, title: str) -> dict | None:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE todos SET title = %s WHERE id = %s "
            "RETURNING id, title, completed, category, created_at",
            (title, todo_id),
        )
        result = _fetchone(cur)
        conn.close()
        return result

    def delete_todo(todo_id: int) -> bool:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        deleted = cur.rowcount > 0
        conn.close()
        return deleted

else:
    # --- SQLite fallback for local development ---

    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.db")

    def _get_conn() -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def init_db() -> None:
        with _get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed BOOLEAN DEFAULT 0,
                    category TEXT NOT NULL DEFAULT 'Family',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = [row[1] for row in conn.execute("PRAGMA table_info(todos)").fetchall()]
            if "category" not in columns:
                conn.execute("ALTER TABLE todos ADD COLUMN category TEXT NOT NULL DEFAULT 'Family'")

    def get_todos(category: str | None = None) -> list[dict]:
        with _get_conn() as conn:
            if category:
                rows = conn.execute(
                    "SELECT id, title, completed, category, created_at FROM todos "
                    "WHERE category = ? ORDER BY created_at DESC", (category,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, title, completed, category, created_at FROM todos "
                    "ORDER BY created_at DESC"
                ).fetchall()
            return [dict(row) for row in rows]

    def add_todo(title: str, category: str = "Family") -> dict:
        with _get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO todos (title, category) VALUES (?, ?)", (title, category)
            )
            row = conn.execute(
                "SELECT id, title, completed, category, created_at FROM todos WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return dict(row)

    def toggle_todo(todo_id: int) -> dict | None:
        with _get_conn() as conn:
            conn.execute(
                "UPDATE todos SET completed = NOT completed WHERE id = ?", (todo_id,)
            )
            row = conn.execute(
                "SELECT id, title, completed, category, created_at FROM todos WHERE id = ?",
                (todo_id,),
            ).fetchone()
            return dict(row) if row else None

    def update_todo(todo_id: int, title: str) -> dict | None:
        with _get_conn() as conn:
            conn.execute(
                "UPDATE todos SET title = ? WHERE id = ?", (title, todo_id)
            )
            row = conn.execute(
                "SELECT id, title, completed, category, created_at FROM todos WHERE id = ?",
                (todo_id,),
            ).fetchone()
            return dict(row) if row else None

    def delete_todo(todo_id: int) -> bool:
        with _get_conn() as conn:
            cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            return cursor.rowcount > 0
