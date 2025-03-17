import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

# Конфигурация
OPENWA_API_URL = os.getenv("OPENWA_API_URL")
SESSION_NAME = os.getenv("SESSION_NAME")
SUPPORT_GROUP_ID = os.getenv("SUPPORT_GROUP_ID")

app = Flask(__name__)

# Обработчик входящих сообщений
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    sender = data.get('from')
    message = data.get('body')

    if not sender or not message:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    # Игнорируем сообщения из групп
    if "g.us" in sender:
        return jsonify({"status": "ignored", "message": "Group message ignored"}), 200

    # Приветственное сообщение
    send_message(sender, f"Привет! 👋 Чем могу помочь?")

    # Если клиент запрашивает оператора
    if "оператор" in message.lower():
        send_message(SUPPORT_GROUP_ID, f"🔔 Пользователь *{sender}* запросил оператора.")
        send_message(sender, "✅ Ваш запрос передан оператору.")

    return jsonify({"status": "success"}), 200

# Функция отправки сообщений
def send_message(to, text):
    url = f"{OPENWA_API_URL}/sendText"
    payload = {
        "session": SESSION_NAME,
        "to": to,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()

# Запуск сервера Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
