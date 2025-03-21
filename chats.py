from config import redis_client


def open_chat(chat_id):
    from messages import send_message
    from db import get_auto_reply_options

    if not redis_client.exists(chat_id):
        redis_client.set(chat_id, "root")
        send_message(chat_id, get_auto_reply_options("root"))

def switch_to_operator(chat_id):
    redis_client.set(f"{chat_id}_operator", "true")

def close_chat(chat_id):
    redis_client.delete(chat_id)
    redis_client.delete(f"{chat_id}_operator")

def check_chat_status(chat_id):
    return redis_client.exists(chat_id)