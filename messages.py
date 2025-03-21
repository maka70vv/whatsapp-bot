import json
import os
import re
import requests
import config
from chats import close_chat, switch_to_operator
from db import get_auto_reply_options, get_operator_contact, sender_is_operator_contact


def send_message(to, text):
    url = f"{config.OPENWA_API_URL}/{config.SESSION_NAME}/send-message"

    payload = {
        "phone": to,
        "isGroup": False if to.endswith("@c.us") else True,
        "isNewsletter": False,
        "isLid": False,
        "message": text
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENWA_API_TOKEN')}"
    }

    try:
        requests.post(url, json=payload, headers=headers)
        return

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return


def process_message_sending(sender, message_text):
    current_state = config.redis_client.get(sender)
    if sender != sender_is_operator_contact(sender):
        if message_text.lower() == "оператор":
            switch_to_operator(sender, current_state)
        elif get_auto_reply_options(message_text):
            send_message(sender, get_auto_reply_options(message_text))
        elif "_operator" in current_state:
            operator_contact = get_operator_contact(current_state)[0]
            send_message(operator_contact, message_text)


    else:
        customer_number, message_text = process_operator_answer(message_text)
        if message_text != "0":
            send_message(customer_number, message_text)
        else:
            close_chat(customer_number)


def process_operator_answer(text):
    pattern = r"(\b\d+@(?:c|g)\.us\b)"
    match = re.search(pattern, text)

    if match:
        extracted_object = match.group(0)
        cleaned_text = text.replace(extracted_object, "").strip(" -:\n")
        return extracted_object, cleaned_text

    return None, text.strip()
