from config import redis_client

WELCOME_MESSAGE = "Добро пожаловать! Чем могу помочь?"

def open_chat(chat_id):
    from messages import send_message

    if not redis_client.exists(chat_id):
        redis_client.set(chat_id, "open")
        send_message(chat_id, WELCOME_MESSAGE)

def close_chat(chat_id):
    redis_client.delete(chat_id)

def check_chat_status(chat_id):
    return redis_client.exists(chat_id)