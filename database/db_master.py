import sqlite3
import os


class DatabaseManager:
    """
    Manages a single, shared SQLite database connection for the entire application.
    This class uses class-level variables to maintain a single database
    connection (`conn`) and cursor (`cursor`). This means that once a connection
    is established by any instance of `DatabaseManager`, it is available to all
    other parts of the application through the class's static/class-level methods.
    This design pattern is similar to a Singleton but focused on the connection
    resource.
    Class Attributes:
        cursor (sqlite3.Cursor | None): The shared cursor object for the database
            connection. None if not connected.
        conn (sqlite3.Connection | None): The shared connection object to the
            SQLite database. None if not connected.
        database_files (str | None): The file path to the SQLite database file.
    Methods:
        isConected(): Checks if the database connection is currently active.
        require_connection(): Returns the active connection and cursor, raising an
            error if not connected.
        close(): Closes the shared database connection and resets class attributes.
        connect(databaseFile): Establishes the shared database connection.
        init_db(databaseFile, sqlFile): Initializes the database by executing an
            SQL script.
    Usage:
        # To initialize and connect
        db_manager = DatabaseManager("my_database.db", "schema.sql")
        # To check connection from anywhere
            print("Database is connected.")
        # To get the connection and cursor from anywhere
        try:
            conn, cursor = DatabaseManager.require_connection()
            cursor.execute("SELECT * FROM my_table")
        except RuntimeError as e:
            print(e)
        # To close the connection from anywhere
        DatabaseManager.close()
    """
    ## CLASS VARIABLE semua ini, sekali buat instance gak perlu init lagi
    cursor: sqlite3.Cursor | None = None
    conn: sqlite3.Connection | None = None
    database_files: str | None = None


  ########################################################
    #Bisa langsung Panggil ==> DatabaseManager.isConected()
    @staticmethod
    def isConected() -> int:
        if DatabaseManager.conn is None or DatabaseManager.cursor is None:
            return 0
        else:
            return 1
        
    #Bisa langsung Panggil     DatabaseManager.require_connection()
    @staticmethod
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
    

