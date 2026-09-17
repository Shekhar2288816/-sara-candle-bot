from flask import Flask, request
import yfinance as yf
from datetime import datetime
import pytz
import os
import requests

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8541512258:AAGbTVEGIr7UqZ-1f5XVyh6C8tLrxZBMhmE")
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_msg(chat_id, text):
    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

@app.route('/')
def home():
    try:
        data = yf.download("^NSEI", period="1d", interval="1m", auto_adjust=True)
        if data.empty:
            return "Market band hai"
        # Fix for new yfinance
        if isinstance(data.columns, object) and hasattr(data.columns, 'levels'):
            data.columns = data.columns.droplevel(1) if data.columns.nlevels > 1 else data.columns
        
        data.index = data.index.tz_convert('Asia/Kolkata') if data.index.tz is not None else data.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        c = data.between_time('09:15','09:25')
        if c.empty:
            return "<h2>9:20 Candle abhi nahi bani</h2>"
        high = float(c.iloc[-1]['High'])
        low = float(c.iloc[-1]['Low'])
        live = float(data['Close'].iloc[-1])
        
        sig = ""
        if live > high:
            sig = f"BUY - High {high} cross"
        elif live < low:
            sig = f"SELL - Low {low} cross"
        else:
            sig = f"NO TRADE - Between {low} - {high}"
        return f"High: {high} Low: {low} Live: {live} <br> {sig}"
    except Exception as e:
        return f"Error: {e}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        msg = request.get_json()
        if "message" in msg:
            chat_id = msg["message"]["chat"]["id"]
            text = msg["message"].get("text","").upper().strip()
            if text in ["TCS","RELIANCE","NIFTY","INFY"]:
                # For now reply with home logic
                data = yf.download("^NSEI", period="1d", interval="1m", auto_adjust=True)
                if isinstance(data.columns, object) and hasattr(data.columns, 'levels'):
                    try:
                        data.columns = data.columns.droplevel(1)
                    except:
                        pass
                if not data.empty:
                    c = data.between_time('09:15','09:25') if hasattr(data.index, 'tz') else data
                    if not c.empty:
                        high = float(c.iloc[-1]['High'])
                        low = float(c.iloc[-1]['Low'])
                        live = float(data['Close'].iloc[-1])
                        reply = f"9:20 Candle\nHigh: {high}\nLow: {low}\nLive: {live}"
                        send_msg(chat_id, reply)
                    else:
                        send_msg(chat_id, "9:20 Candle abhi nahi bani")
                else:
                    send_msg(chat_id, "Market band hai")
            else:
                send_msg(chat_id, f"Aapne bheja: {text}\nTCS likho test ke liye")
        return "ok"
    except Exception as e:
        print(f"Webhook Error: {e}")
        return "ok"

if __name__ == '__main__':
    app.run()
