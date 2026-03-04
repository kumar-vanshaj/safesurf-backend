import sqlite3
import threading

_db_lock = threading.Lock()
_conn = None

def get_db():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(
            "safesurf.db",
            check_same_thread=False,
            isolation_level=None  # 🔥 AUTOCOMMIT MODE
        )
    return _conn

def get_lock():
    return _db_lock


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url TEXT,
        text TEXT,
        risk_score REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
