import sqlite3

DB_PATH = "auto_replies.db"


def init_db():
    """Создает таблицу автоответов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auto_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            response TEXT NOT NULL,
            parent_keyword TEXT DEFAULT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_auto_reply(keyword, response, parent_keyword=None):
    """Добавляет автоответ в базу"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO auto_replies (keyword, response, parent_keyword) VALUES (?, ?, ?)",
            (keyword, response, parent_keyword)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Ответ для '{keyword}' уже существует.")
    conn.close()


def get_auto_reply_options(parent_keyword):
    """Возвращает список вложенных вариантов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, response FROM auto_replies WHERE parent_keyword = ?", (parent_keyword,))
    options = cursor.fetchall()
    conn.close()

    if options:
        return "Выберите вариант:\n" + "\n".join([f"{opt[0]}️⃣ - {opt[1]}" for opt in options])
    return None


def get_auto_reply(keyword):
    """Возвращает сам ответ (если нет вложенных)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM auto_replies WHERE keyword = ?", (keyword,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None
