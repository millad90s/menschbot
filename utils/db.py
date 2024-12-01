import sqlite3
import os
from utils import DB_PATHH

db_path = DB_PATHH

def init_database():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language_code TEXT,
            last_active TEXT
        )
    ''')
    conn.commit()
    conn.close()
def save_user(user_id, username, first_name, last_name, language_code):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT INTO users (user_id, username, first_name, last_name, language_code, last_active) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
                  (user_id, username, first_name, last_name, language_code))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

### update latest activity if user exist , create new user if not exists
def update_user_activity(user_id, username, first_name, last_name, language_code) -> bool:
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, language_code, last_active)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                last_active = CURRENT_TIMESTAMP
        ''', (user_id, username, first_name, last_name, language_code))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def fetch_user(user_id):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

### fetch all users
def fetch_all_users() -> list:
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"An error occurred: {e}")
        return None