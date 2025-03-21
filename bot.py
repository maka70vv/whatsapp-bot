import os
import threading

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from chats import check_chat_status, open_chat
from messages import process_message_sending

app = Flask(__name__)


def process_webhook(data):
    if data:
        # Извлекаем текст сообщения, если это событие "onmessage"
        if data.get("event") == "onmessage":
            message_text = data.get("body") or data.get("content")
            sender = data.get("sender", {}).get("pushname", "Unknown")
            sender_num = data.get("from")

            if not check_chat_status(sender_num):
                open_chat(sender_num)

            process_message_sending(sender_num, message_text)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    threading.Thread(target=process_webhook, args=(data,)).start()
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=bool(os.getenv("DEBUG", default=False)), threaded=True)
