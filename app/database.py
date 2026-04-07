import sqlite3
from contextlib import contextmanager
import os

# NOTE: On import, app now checks the environment for a DATABASE_FILE variable.
# Defaults to chat.db if not set -- allows tests to override with a throwaway database.
DATABASE_FILE = os.environ.get("DATABASE_FILE", "chat.db")

@contextmanager
def get_database_connection():
    """Manages database connections safely (auto-commits or rollback)."""
    database_connection = sqlite3.connect(DATABASE_FILE)
    database_connection.row_factory = sqlite3.Row  # This allows access to columns by name.
    database_connection.execute("PRAGMA foreign_keys = ON")    # Enable foreign keys.
    try:
        yield database_connection
        database_connection.commit()
    except Exception:
        database_connection.rollback()
        raise
    finally:
        database_connection.close()

def initialize_database():
    """Initializes the database by creating three tables: users, rooms, and messages."""
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        db_cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,      
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name text UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                           
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                message_content TEXT NOT NULL,
                message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (room_id) REFERENCES rooms (room_id)
            );
        ''')
    print("Database initialized successfully!")

