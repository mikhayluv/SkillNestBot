import sqlite3


def create_connection(db_file):
    conn = sqlite3.connect(db_file, check_same_thread=False)
    return conn


def create_messages_log_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
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


def add_message_to_log_table(conn, user_id, username, message_text):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages_log (user_id, username, message_text) VALUES (?, ?, ?)",
                   (user_id, username, message_text))
    conn.commit()
    cursor.close()


def create_vacancy_data_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vacancy_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    vacancy_id BIGINT NOT NULL, 
                    vacancy_name TEXT,
                    area TEXT, 
                    description TEXT,
                    lang TEXT,
                    skills TEXT,
                    text_search TEXT)''')
    conn.commit()
    cursor.close()


def add_vacancy_data(conn, vacancy_id, vacancy_name, area, description, lang, skills, text_search):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vacancy_data (vacancy_id, vacancy_name, area, \
                    description, lang, skills, text_search) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (vacancy_id, vacancy_name, area, description, lang, skills, text_search))
    conn.commit()
    cursor.close()


def get_skills(conn, text_search):
    cursor = conn.cursor()
    cursor.execute("SELECT skills FROM vacancy_data WHERE text_search = ? AND skills IS NOT NULL", (text_search,))
    skills = cursor.fetchall()
    cursor.close()
    return skills
