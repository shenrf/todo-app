import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.db")

CATEGORIES = ["Ruofei", "Ruiqi", "Family"]


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
        # Migration: add category column if missing (for existing DBs)
        columns = [row[1] for row in conn.execute("PRAGMA table_info(todos)").fetchall()]
        if "category" not in columns:
            conn.execute("ALTER TABLE todos ADD COLUMN category TEXT NOT NULL DEFAULT 'Family'")


def get_todos(category: str | None = None) -> list[dict]:
    with _get_conn() as conn:
        if category:
            rows = conn.execute(
                "SELECT id, title, completed, category, created_at FROM todos "
                "WHERE category = ? ORDER BY created_at DESC",
                (category,),
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
