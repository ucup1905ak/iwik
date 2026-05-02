# models/user_model.py

import hashlib
from database.db_master import require_connection


def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def create_user(name: str, pin: str, role: int):
    """
    role:
    1 = Admin
    2 = Cashier
    """
    conn, _ = require_connection()
    cursor = conn.cursor()

    encrypted_pin = hash_pin(pin)

    cursor.execute(
        "INSERT INTO users (name, pin, role) VALUES (?, ?, ?)",
        (name, encrypted_pin, role)
    )

    conn.commit()
    


def get_all_users():
    conn, _ = require_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, role FROM users")
    users = cursor.fetchall()

    
    return users


def verify_user_pin(name: str, input_pin: str):
    conn, _ = require_connection()
    cursor = conn.cursor()

    encrypted_pin = hash_pin(input_pin)

    cursor.execute(
        "SELECT * FROM users WHERE name = ? AND pin = ?",
        (name, encrypted_pin)
    )

    user = cursor.fetchone()

    
    return user