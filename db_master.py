import sqlite3
#| None = None
cursor: sqlite3.Cursor | None = None
conn: sqlite3.Connection | None = None


# module Create Database Backend
def connect_db(databaseFile: str) -> None:
    print("CREATING DATABASE")
    global conn, cursor
    conn = sqlite3.connect(databaseFile)
    cursor = conn.cursor()


def init_db(databaseFile: str, sqlFile: str) -> None:
    if cursor is None or conn is None:
        connect_db(databaseFile)

    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")
    
    with open(sqlFile, "r", encoding="utf-8") as f:
        sql = f.read()

    # Use executescript for multi-statement SQL (CREATE TABLE, PRAGMA, etc.)
    conn.executescript(sql)
    conn.commit()
    


def main():
    connect_db("abc.db")
    init_db("abc.db", "sql/init.sql")

    result = list_cashiers()
    print(result)

    
    
    
if __name__ == "__main__":
    main()
