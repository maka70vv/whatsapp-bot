import sqlite3

import config


def init_db():
    """Создает таблицу автоответов и номеров групп с операторами"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auto_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            response TEXT NOT NULL,
            current_state TEXT NOT NULL,
            next_state TEXT DEFAULT NULL,
            operator_contact_name TEXT NOT NULL
        )
    """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operator_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL
        )
    """)
    conn.commit()

    conn.close()


def add_auto_reply(keyword, response, current_state, operator_contact_name, next_state=None):
    """Добавляет автоответ в базу"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO auto_replies (keyword, response, current_state, next_state, operator_contact_name) VALUES (?, ?, ?, ?, ?)",
            (keyword, response, current_state, next_state, operator_contact_name)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Ответ для '{keyword}' уже существует.")
    conn.close()


def get_auto_reply_options(current_state):
    """Возвращает список вложенных вариантов"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, response FROM auto_replies WHERE current_state = ?", (current_state,))
    options = cursor.fetchall()
    conn.close()

    if options:
        return "Выберите вариант:\n" + "\n".join([f"{opt[0]}️⃣ - {opt[1]}" for opt in options])
    return None


def get_next_state(keyword, current_state):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT next_state FROM auto_replies WHERE keyword = ? AND current_state = ?",
        (keyword, current_state,),
    )
    states = cursor.fetchall()

    conn.close()

    return states[0][0]


def get_auto_reply(keyword):
    """Возвращает сам ответ (если нет вложенных)"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM auto_replies WHERE keyword = ?", (keyword,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def add_operator_contact(name, contact):
    """Добавляет контакт оператора в базу"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO operator_chats (name, contact) VALUES (?, ?)",
            (name, contact)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Контакт '{name}' уже существует.")
    conn.close()


def get_operator_contact(current_state):
    """Возвращает контакт оператора по текущему состоянию"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT oc.contact
        FROM auto_replies ar
        JOIN operator_chats oc ON ar.operator_contact_name = oc.name
        WHERE ar.current_state = ?
    """, (current_state,))

    result = cursor.fetchone()
    conn.close()

    return result[0][0] if result else None



def sender_is_operator_contact(sender):
    """Проверяет является ли отправитель оператором"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT contact FROM operator_chats")
    contact = cursor.fetchall()
    conn.close()

    contact_list = [c[0] for c in contact]

    return sender in contact_list
