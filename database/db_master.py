import sqlite3
import os


class DatabaseManager:
    ## CLASS VARIABLE semua ini, sekali buat instance gak perlu init lagi
    cursor: sqlite3.Cursor | None = None
    conn: sqlite3.Connection | None = None
    database_files: str | None = None


  ########################################################
    #Bisa langsung Panggil ==> DatabaseManager.isConected()
    def isConected() -> int:
        if DatabaseManager.conn is None or DatabaseManager.cursor is None:
            return 0
        else:
            return 1
        
    #Bisa langsung Panggil     DatabaseManager.require_connection()
    def require_connection() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        if not DatabaseManager.isConected():
            raise RuntimeError("Database Is Not Connected")
        return DatabaseManager.conn, DatabaseManager.cursor


    #Bisa langsung Panggil     DatabaseManager.close()
    @staticmethod
    def close():
        if DatabaseManager.isConected():
            DatabaseManager.conn.close()
            DatabaseManager.conn = None
            DatabaseManager.cursor = None


#############################################################

    # Kalau ketika dibuat instance disediakan file database maka bakal buat connection
    # Kalau disediain juga sql, maka bakal langsung di run scriptnyas
    def __init__(self, database_files:str, sql_script_file:str = None):
        DatabaseManager.database_files = database_files
        self.connect(DatabaseManager.database_files)
        if sql_script_file:
            self.init_db(databaseFile=database_files, sqlFile=sql_script_file)    
  
    # Create connection dan cursor
    def connect(self, databaseFile: str) -> None:
        DatabaseManager.conn = sqlite3.connect(databaseFile)
        DatabaseManager.cursor = self.conn.cursor()

    # Run SQL Script
    def init_db(self, databaseFile: str, sqlFile: str) -> None:
        if not DatabaseManager.isConected():
            self.connect(databaseFile)

        _conn, _cursor = DatabaseManager.require_connection()
                                                                        
        with open(sqlFile, "r", encoding="utf-8") as f:
            sql = f.read()

        _conn.executescript(sql)
        _conn.commit()
    

