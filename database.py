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


'''
Поля для таблицы:
    - ID
    - ID вакансии
    - Название вакансии
    - Город
    - ЗП (от, до, валюта)
    - ОПИСАНИЕ 
'''


def create_vacancy_data_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vacancy_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    vacancy_id BIGINT NOT NULL, 
                    vacancy_name TEXT,
                    area TEXT, 
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency TEXT,
                    description TEXT)''')
    conn.commit()
    cursor.close()


def create_keys_kills_data_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS key_skills_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    vacancy_id BIGINT NOT NULL, 
                    vacancy_name TEXT,
                    key_skill TEXT)''')
    conn.commit()
    cursor.close()


def add_vacancy_data(conn, vacancy_id, vacancy_name, area, salary_from, salary_to, currency, description):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vacancy_data (vacancy_id, vacancy_name, area, salary_from, \
                    salary_to, currency, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (vacancy_id, vacancy_name, area, salary_from, salary_to, currency, description))
    conn.commit()
    cursor.close()


def add_keys_kills_data(conn, vacancy_id, vacancy_name, key_skill):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO key_skills_data (vacancy_id, vacancy_name, key_skill) VALUES (?, ?, ?)",
                   (vacancy_id, vacancy_name, key_skill))
    conn.commit()
    cursor.close()
