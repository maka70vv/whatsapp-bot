import json

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
        print("Request:", data)  # Выводим все полученные данные

        # Извлекаем текст сообщения, если это событие "onmessage"
        if data.get("event") == "onmessage":
            message_text = data.get("body") or data.get("content")
            sender = data.get("sender", {}).get("pushname", "Unknown")
            sender_num = data.get("from")
            print(f"Сообщение от {sender}: {message_text}")
            send_message(sender_num, message_text)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    threading.Thread(target=process_webhook, args=(data,)).start()
    return jsonify({"status": "success"}), 200


# Функция отправки сообщений
def send_message(to, text):
    print("sending message func")
    url = f"{OPENWA_API_URL}/{SESSION_NAME}/send-message"
    print(url)
    payload = {
      "phone": to,
      "isGroup": False,
      "isNewsletter": False,
      "isLid": False,
      "message": "Hi from WPPConnect"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENWA_API_TOKEN')}"
    }

    print(f"📤 Запрос к API: {url}")
    print(f"📦 Данные запроса: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)  # Устанавливаем таймаут
        print(f"🔍 Ответ API: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")

    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
