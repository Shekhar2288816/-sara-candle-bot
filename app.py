from flask import Flask, request
import os, requests
app = Flask(__name__)
BOT_TOKEN = "8541512258:AAGbTVEGIr7UqZ-1f5XVyh6C8tLrxZBMhmE"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route('/')
def home():
    return "Bot is Live"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        txt = data["message"].get("text","")
        requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": f"Aapne bheja: {txt} - Bot ON hai!"})
    return "ok"
