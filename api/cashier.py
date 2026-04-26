import api.db_master as db_master

def create_cashier(first_name: str, last_name: str, salary: float) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")
    
    db_master.cursor.execute("INSERT INTO Cashier (FirstName, LastName, Salary) VALUES (?, ?, ?)",
                    (first_name, last_name, salary))
    db_master.conn.commit()


def read_cashier(cashier_id: int) -> tuple | None:
    if db_master.cursor is None:
        raise RuntimeError("Database connection was not initialized")
    
    db_master.cursor.execute("SELECT * FROM Cashier WHERE ID = ?", (cashier_id,))
    return db_master.cursor.fetchone()


def update_cashier(cashier_id: int, first_name: str, last_name: str, salary: float) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")
    
    db_master.cursor.execute("UPDATE Cashier SET FirstName = ?, LastName = ?, Salary = ? WHERE ID = ?",
                    (first_name, last_name, salary, cashier_id))
    db_master.conn.commit()


def delete_cashier(cashier_id: int) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")
    
    db_master.cursor.execute("DELETE FROM Cashier WHERE ID = ?", (cashier_id,))
    db_master.conn.commit()


def list_cashiers() -> list:
    if db_master.cursor is None:
        raise RuntimeError("Database connection was not initialized")
    
    db_master.cursor.execute("SELECT * FROM Cashier")
    return db_master.cursor.fetchall()
