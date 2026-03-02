from fastmcp import FastMCP
import os
import sqlite3
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "todos.db")
TAGS_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("TodoManager")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS todos(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                priority TEXT NOT NULL DEFAULT 'medium',
                tag TEXT DEFAULT '',
                due_date TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

init_db()


@mcp.tool()
def add_todo(title: str, description: str = "", priority: str = "medium", tag: str = "", due_date: str = ""):
    """Add a new to-do task.

    Args:
        title: Short title of the task (required).
        description: Longer description or notes.
        priority: 'low', 'medium', or 'high'.
        tag: Category tag (e.g. 'work', 'personal').
        due_date: Due date in YYYY-MM-DD format.
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO todos(title, description, status, priority, tag, due_date, created_at) VALUES (?,?,?,?,?,?,?)",
            (title, description, "pending", priority, tag, due_date, created_at)
        )
        return {"status": "ok", "id": cur.lastrowid, "title": title}


@mcp.tool()
def list_todos(status: str = "", priority: str = "", tag: str = ""):
    """List to-do tasks with optional filters.

    Args:
        status: Filter by status: 'pending', 'in_progress', or 'done'. Leave blank for all.
        priority: Filter by priority: 'low', 'medium', or 'high'. Leave blank for all.
        tag: Filter by tag. Leave blank for all.
    """
    query = "SELECT id, title, description, status, priority, tag, due_date, created_at FROM todos WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if tag:
        query += " AND tag = ?"
        params.append(tag)

    query += " ORDER BY id ASC"

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def update_todo(id: int, title: str = "", description: str = "", status: str = "", priority: str = "", tag: str = "", due_date: str = ""):
    """Update fields of an existing to-do task.

    Args:
        id: The task ID to update (required).
        title: New title.
        description: New description.
        status: New status: 'pending', 'in_progress', or 'done'.
        priority: New priority: 'low', 'medium', or 'high'.
        tag: New tag.
        due_date: New due date in YYYY-MM-DD format.
    """
    fields = []
    params = []

    if title:
        fields.append("title = ?"); params.append(title)
    if description:
        fields.append("description = ?"); params.append(description)
    if status:
        fields.append("status = ?"); params.append(status)
    if priority:
        fields.append("priority = ?"); params.append(priority)
    if tag:
        fields.append("tag = ?"); params.append(tag)
    if due_date:
        fields.append("due_date = ?"); params.append(due_date)

    if not fields:
        return {"status": "error", "message": "No fields to update provided."}

    params.append(id)
    with sqlite3.connect(DB_PATH) as c:
        c.execute(f"UPDATE todos SET {', '.join(fields)} WHERE id = ?", params)
        return {"status": "ok", "updated_id": id}


@mcp.tool()
def complete_todo(id: int):
    """Mark a to-do task as done.

    Args:
        id: The task ID to mark as done.
    """
    with sqlite3.connect(DB_PATH) as c:
        c.execute("UPDATE todos SET status = 'done' WHERE id = ?", (id,))
        return {"status": "ok", "completed_id": id}


@mcp.tool()
def delete_todo(id: int):
    """Delete a to-do task permanently.

    Args:
        id: The task ID to delete.
    """
    with sqlite3.connect(DB_PATH) as c:
        c.execute("DELETE FROM todos WHERE id = ?", (id,))
        return {"status": "ok", "deleted_id": id}


@mcp.tool()
def summarize_todos():
    """Get a summary count of tasks grouped by status and priority."""
    with sqlite3.connect(DB_PATH) as c:
        by_status = c.execute(
            "SELECT status, COUNT(*) as count FROM todos GROUP BY status"
        ).fetchall()
        by_priority = c.execute(
            "SELECT priority, COUNT(*) as count FROM todos WHERE status != 'done' GROUP BY priority"
        ).fetchall()
        return {
            "by_status": [{"status": r[0], "count": r[1]} for r in by_status],
            "open_by_priority": [{"priority": r[0], "count": r[1]} for r in by_priority],
        }


@mcp.resource("todo://categories", mime_type="application/json")
def categories():
    """Expose available categories as a resource."""
    with open(TAGS_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()
