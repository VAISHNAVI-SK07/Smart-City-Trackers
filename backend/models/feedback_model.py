from utils.db import get_db_connection


def create_feedback(complaint_id, user_id, rating, comment):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO feedback (complaint_id, user_id, rating, comment)
               VALUES (%s, %s, %s, %s)""",
            (complaint_id, user_id, rating, comment)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_feedback_by_complaint(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM feedback WHERE complaint_id = %s", (complaint_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
