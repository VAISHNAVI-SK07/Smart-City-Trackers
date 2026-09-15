from utils.db import get_db_connection


def create_user(name, email, phone, password_hash, role, address):
    """Inserts a new user and returns their new id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO users (name, email, phone, password_hash, role, address)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, email, phone, password_hash, role, address)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    """Returns the full user row (including password_hash) — used only for login checks."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_user_by_id(user_id):
    """Returns public-safe user fields only (no password_hash)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name, email, phone, role, address, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def update_user_profile(user_id, name, phone, address):
    """Updates the editable profile fields for a user. Email and role are NEVER editable here."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET name = %s, phone = %s, address = %s WHERE id = %s",
            (name, phone, address, user_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_all_users():
    """Admin-only listing of all registered users, with their complaint counts."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT u.id, u.name, u.email, u.phone, u.role, u.address, u.created_at,
                      COUNT(c.id) AS complaint_count
               FROM users u
               LEFT JOIN complaints c ON c.user_id = u.id
               GROUP BY u.id
               ORDER BY u.created_at DESC"""
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
