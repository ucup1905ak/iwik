from db_master import *

def create_cashier(first_name: str, last_name: str, salary: float) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")
    
    cursor.execute("INSERT INTO Cashier (FirstName, LastName, Salary) VALUES (?, ?, ?)",
                    (first_name, last_name, salary))
    conn.commit()


def read_cashier(cashier_id: int) -> tuple | None:
    if cursor is None:
        raise RuntimeError("Database connection was not initialized")
    
    cursor.execute("SELECT * FROM Cashier WHERE ID = ?", (cashier_id,))
    return cursor.fetchone()


def update_cashier(cashier_id: int, first_name: str, last_name: str, salary: float) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")
    
    cursor.execute("UPDATE Cashier SET FirstName = ?, LastName = ?, Salary = ? WHERE ID = ?",
                    (first_name, last_name, salary, cashier_id))
    conn.commit()


def delete_cashier(cashier_id: int) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")
    
    cursor.execute("DELETE FROM Cashier WHERE ID = ?", (cashier_id,))
    conn.commit()


def list_cashiers() -> list:
    if cursor is None:
        raise RuntimeError("Database connection was not initialized")
    
    cursor.execute("SELECT * FROM Cashier")
    return cursor.fetchall()
