import os
import re

import requests

import config
from chats import close_chat, switch_to_operator
from db import get_auto_reply_options, get_operator_contact, sender_is_operator_contact, get_auto_reply, get_next_state


def send_message(to, text):
    print("sending message")
    url = f"{config.OPENWA_API_URL}/{config.SESSION_NAME}/send-message"

    payload = {
        "phone": to,
        "isGroup": False if to.endswith("@c.us") else True,
        "isNewsletter": False,
        "isLid": False,
        "message": text
    }
    print(payload)

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
    if not sender_is_operator_contact(sender):
        if config.redis_client.get(f"{sender}_operator") == "true":
            operator_contact = get_operator_contact(current_state)
            send_message(operator_contact, f"{sender}\n {message_text}")
        elif message_text.lower() == "оператор":
            send_message(sender, "Пожалуйста, напишите Ваше сообщение! Первый освободившийся оператор ответит Вам!")
            switch_to_operator(sender)
        elif get_auto_reply_options(current_state):
            next_state = get_next_state(message_text, current_state)
            if next_state:
                config.redis_client.set(sender, next_state)
                send_message(sender, get_auto_reply_options(next_state))
        else:
            # Если нет вложенных опций — показать простой ответ
            response = get_auto_reply(message_text, current_state)
            if response:
                send_message(sender, response)
            else:
                send_message(sender, "Неизвестная команда. Попробуйте снова.")

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
