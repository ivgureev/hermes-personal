from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "hermes.db"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Новая',
            priority TEXT NOT NULL DEFAULT 'Обычная',
            due_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stored_name TEXT NOT NULL UNIQUE,
            original_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            trust TEXT NOT NULL DEFAULT 'Недоверенные данные',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            parameters TEXT NOT NULL,
            consequences TEXT NOT NULL,
            risks TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Ожидает',
            created_at TEXT NOT NULL,
            decided_at TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            object_type TEXT NOT NULL,
            object_id TEXT,
            status TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)


def log_event(event_type: str, object_type: str, status: str, details: str, object_id: str = "") -> None:
    with connect() as con:
        con.execute(
            "INSERT INTO audit_log(event_type, object_type, object_id, status, details, created_at) VALUES (?,?,?,?,?,?)",
            (event_type, object_type, object_id, status, details[:4000], now_iso()),
        )


def add_message(session_id: str, role: str, content: str) -> int:
    with connect() as con:
        cur = con.execute(
            "INSERT INTO messages(session_id, role, content, created_at) VALUES (?,?,?,?)",
            (session_id, role, content, now_iso()),
        )
        mid = cur.lastrowid
    log_event("Сообщение", "chat", "Сохранено", f"Роль: {role}", str(mid))
    return mid


def get_messages(session_id: str, limit: int = 100) -> list[dict]:
    with connect() as con:
        rows = con.execute(
            "SELECT * FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?", (session_id, limit)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def clear_messages(session_id: str) -> None:
    with connect() as con:
        con.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    log_event("Очистка", "chat", "Выполнено", f"Сессия {session_id}")


def create_task(title: str, description: str, priority: str, due_date: str | None) -> int:
    ts = now_iso()
    with connect() as con:
        cur = con.execute(
            "INSERT INTO tasks(title, description, priority, due_date, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (title, description, priority, due_date, ts, ts),
        )
        task_id = cur.lastrowid
    log_event("Создание", "task", "Выполнено", title, str(task_id))
    return task_id


def list_tasks() -> list[dict]:
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()]


def update_task_status(task_id: int, status: str) -> None:
    with connect() as con:
        con.execute("UPDATE tasks SET status=?, updated_at=? WHERE id=?", (status, now_iso(), task_id))
    log_event("Изменение статуса", "task", "Выполнено", status, str(task_id))


def register_file(stored_name: str, original_name: str, size: int, sha256: str) -> int:
    with connect() as con:
        cur = con.execute(
            "INSERT INTO files(stored_name, original_name, size, sha256, created_at) VALUES (?,?,?,?,?)",
            (stored_name, original_name, size, sha256, now_iso()),
        )
        file_id = cur.lastrowid
    log_event("Загрузка", "file", "Выполнено", f"{original_name}; SHA-256 {sha256}", str(file_id))
    return file_id


def list_files() -> list[dict]:
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM files ORDER BY id DESC").fetchall()]


def create_approval(action: str, target: str, parameters: dict, consequences: str, risks: str) -> int:
    with connect() as con:
        cur = con.execute(
            "INSERT INTO approvals(action,target,parameters,consequences,risks,created_at) VALUES (?,?,?,?,?,?)",
            (action, target, json.dumps(parameters, ensure_ascii=False), consequences, risks, now_iso()),
        )
        approval_id = cur.lastrowid
    log_event("Запрос подтверждения", "approval", "Ожидает", action, str(approval_id))
    return approval_id


def list_approvals() -> list[dict]:
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM approvals ORDER BY id DESC").fetchall()]


def decide_approval(approval_id: int, status: str) -> None:
    if status not in {"Подтверждено", "Отклонено"}:
        raise ValueError("Недопустимый статус")
    with connect() as con:
        con.execute("UPDATE approvals SET status=?, decided_at=? WHERE id=?", (status, now_iso(), approval_id))
    log_event("Решение", "approval", status, "Решение пользователя", str(approval_id))


def list_logs(limit: int = 300) -> list[dict]:
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
