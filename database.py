import sqlite3


def create_connection(db_file):
    conn = sqlite3.connect(db_file, check_same_thread=False)
    return conn


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages_log 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    user_id INTEGER, 
                    username TEXT, 
                    message_text TEXT,
                    timestamp TIMESTAMP  DEFAULT (datetime('now', 'localtime')) NOT NULL)''')
    conn.commit()
    cursor.close()


def drop_table(conn, name):
    cursor = conn.cursor()
    query = f"DROP TABLE IF EXISTS {name}"
    cursor.execute(query)
    conn.commit()
    cursor.close()


def add_message(conn, user_id, username, message_text):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages_log (user_id, username, message_text) VALUES (?, ?, ?)",
                   (user_id, username, message_text))
    conn.commit()
    cursor.close()
