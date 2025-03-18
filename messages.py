import json
import os
import re
import requests
import config


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

    print(f"📤 Запрос к API: {url}")
    print(f"📦 Данные запроса: {json.dumps(payload, indent=2)}")

    try:
        requests.post(url, json=payload, headers=headers)
        return

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return


def process_message_sending(sender, message_text):
    if sender != config.SUPPORT_GROUP_ID:
        send_message(config.SUPPORT_GROUP_ID, f"{sender} \n {message_text}")
    else:
        customer_number, message_text = process_operator_answer(message_text)
        send_message(customer_number, message_text)


def process_operator_answer(text):
    pattern = r"(\b\d+@(?:c|g)\.us\b)"
    match = re.search(pattern, text)

    if match:
        extracted_object = match.group(0)
        cleaned_text = text.replace(extracted_object, "").strip(" -:\n")
        return extracted_object, cleaned_text

    return None, text.strip()
