import api.db_master as db_master

def create_cashier(first_name: str, last_name: str, salary: float) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "INSERT INTO Cashier (FirstName, LastName, Salary) VALUES (?, ?, ?)",
        (first_name, last_name, salary),
    )
    conn.commit()


def read_cashier(cashier_id: int) -> tuple | None:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Cashier WHERE ID = ?", (cashier_id,))
    return cursor.fetchone()


def update_cashier(cashier_id: int, first_name: str, last_name: str, salary: float) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "UPDATE Cashier SET FirstName = ?, LastName = ?, Salary = ? WHERE ID = ?",
        (first_name, last_name, salary, cashier_id),
    )
    conn.commit()


def delete_cashier(cashier_id: int) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute("DELETE FROM Cashier WHERE ID = ?", (cashier_id,))
    conn.commit()


def list_cashiers() -> list:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Cashier")
    return cursor.fetchall()
