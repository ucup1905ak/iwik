# models/user_model.py

import hashlib
from database.db_master import DatabaseManager

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def create_user(name: str, pin: str, role: int):
    """
    role:
    1 = Admin
    2 = Cashier
    """
    conn, _ = DatabaseManager.require_connection()
    cursor = conn.cursor()

    encrypted_pin = hash_pin(pin)

    cursor.execute(
        "INSERT INTO users (name, pin, role) VALUES (?, ?, ?)",
        (name, encrypted_pin, role)
    )

    conn.commit()
    
def get_all_users():
    conn, _ = DatabaseManager.require_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, role FROM users")
    users = cursor.fetchall()

    
    return users


def verify_user_pin(name: str, input_pin: str):
    conn, _ = DatabaseManager.require_connection()
    cursor = conn.cursor()

    encrypted_pin = hash_pin(input_pin)

    cursor.execute(
        "SELECT * FROM users WHERE name = ? AND pin = ?",
        (name, encrypted_pin)
    )

    user = cursor.fetchone()

    
    return user

def update_user(user_id: int, name: str, role: int, pin: str = None):
    """
    Update user data. PIN hanya diupdate jika pin tidak None.
    """
    conn, _ = DatabaseManager.require_connection()
    cursor = conn.cursor()

    if pin is not None:
        cursor.execute(
            "UPDATE users SET name = ?, pin = ?, role = ? WHERE id = ?",
            (name, hash_pin(pin), role, user_id)
        )
    else:
        cursor.execute(
            "UPDATE users SET name = ?, role = ? WHERE id = ?",
            (name, role, user_id)
        )

    conn.commit()
    
def delete_user(user_id: int):
    conn, _ = DatabaseManager.require_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    
def get_first_admin_id() -> int | None:
    conn, _ = DatabaseManager.require_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(id) FROM users WHERE role = 1")
    row = cursor.fetchone()
    return row[0] if row and row[0] is not None else None