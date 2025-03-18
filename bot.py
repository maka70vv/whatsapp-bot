import json
import re

from dotenv import load_dotenv
import os
import threading

import requests
from flask import Flask, request, jsonify

load_dotenv()

# Конфигурация
OPENWA_API_URL = os.getenv("OPENWA_API_URL")
SESSION_NAME = os.getenv("SESSION_NAME")
SUPPORT_GROUP_ID = os.getenv("SUPPORT_GROUP_ID")

app = Flask(__name__)


def process_webhook(data):
    print(f"Обработка сообщения: {data}")

    if data:
        # Извлекаем текст сообщения, если это событие "onmessage"
        if data.get("event") == "onmessage":
            message_text = data.get("body") or data.get("content")
            sender = data.get("sender", {}).get("pushname", "Unknown")
            sender_num = data.get("from")
            process_message_sending(sender_num, message_text)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    threading.Thread(target=process_webhook, args=(data,)).start()
    return jsonify({"status": "success"}), 200


def send_message(to, text):
    print("📨 Sending message...")

    url = f"{OPENWA_API_URL}/{SESSION_NAME}/send-message"

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
    if sender != SUPPORT_GROUP_ID:
        send_message(SUPPORT_GROUP_ID, f"{sender} \n {message_text}")
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=bool(os.getenv("DEBUG", default=False)), threaded=True)
