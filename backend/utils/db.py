import mysql.connector
from mysql.connector import Error
from config import Config


def get_db_connection():
    """
    Opens and returns a fresh MySQL connection.

    Pattern used throughout this project: every function that needs the
    database calls this, does its work, then closes the connection in a
    `finally` block. This is simpler and safer for a student project than
    managing a shared connection pool, and avoids connections leaking or
    going stale.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except Error as e:
        # In a real production app this would go to a logging system.
        # For now, printing to the console is enough to see what went wrong.
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        raise
