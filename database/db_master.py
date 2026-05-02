import sqlite3

cursor: sqlite3.Cursor | None = None
conn: sqlite3.Connection | None = None


def connect_db(databaseFile: str) -> None:
    global conn, cursor
    conn = sqlite3.connect(databaseFile)
    cursor = conn.cursor()


def require_connection() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    if conn is None or cursor is None:
        raise RuntimeError("Database connection was not initialized")
    return conn, cursor


def init_db(databaseFile: str, sqlFile: str) -> None:
    if cursor is None or conn is None:
        connect_db(databaseFile)

    _conn, _cursor = require_connection()

    with open(sqlFile, "r", encoding="utf-8") as f:
        sql = f.read()

    _conn.executescript(sql)
    _conn.commit()


