"""Audit log (SQLite): who asked what, which tools ran. / 감사 로그."""
import json
import sqlite3
import time

from erp.settings import settings


def _conn():
    c = sqlite3.connect(settings.audit_db)
    c.execute("CREATE TABLE IF NOT EXISTS audit_log "
              "(ts REAL, user_id TEXT, question TEXT, tool_calls TEXT, answer TEXT)")
    return c


def log_query(user_id: str, question: str, tool_calls: list, answer: str) -> None:
    with _conn() as c:
        c.execute("INSERT INTO audit_log VALUES (?,?,?,?,?)",
                  (time.time(), user_id, question, json.dumps(tool_calls, ensure_ascii=False), answer))
