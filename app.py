from flask import Flask, request
import requests
import yfinance as yf
from datetime import datetime
import pytz

app = Flask(__name__)
BOT_TOKEN = "8541512258:AAGbTVEGIr7UqZ-1f5XVyh6C8tLrxZBMhmE"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_candle(symbol):
    try:
        ticker = symbol
        if "." not in symbol.upper():
            ticker = f"{symbol.upper()}.NS"

        # Fast download
        data = yf.download(ticker, period="2d", interval="1d", progress=False, auto_adjust=True)
        if data.empty:
            return f"{symbol} nahi mila. NSE wala naam likh jaise TCS, RELIANCE"

        today = data.iloc[-1]
        yesterday = data.iloc[-2] if len(data) > 1 else today

        open_p = float(today['Open'])
        close_p = float(today['Close'])
        high_p = float(today['High'])
        low_p = float(today['Low'])
        prev_close = float(yesterday['Close'])

        change = close_p - prev_close
        perc = (change/prev_close*100) if prev_close!=0 else 0

        # Candle Type
        if close_p > open_p:
            candle = "🟢 GREEN / Bullish"
        elif close_p < open_p:
            candle = "🔴 RED / Bearish"
        else:
            candle = "⚪ Doji"

        body = abs(close_p - open_p)
        total_range = high_p - low_p

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist).strftime("%d-%b %I:%M %p")

        msg = f"""📊 *{symbol.upper()}* - {candle}

💰 *Price:* {close_p:.2f} ({perc:+.2f}%)
🔓 Open: {open_p:.2f}
🔒 Close: {close_p:.2f}
⬆️ High: {high_p:.2f}
⬇️ Low: {low_p:.2f}

📏 Body: {body:.2f} | Range: {total_range:.2f}

🕐 {now} IST
Bot: SARA Candle Bot"""
        return msg
    except Exception as e:
        print(f"Error: {e}")
        return f"Error aa gaya {symbol} pe. Dobara try kar."

@app.route('/')
def home():
    return "SARA Bot Live Hai"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text","").strip()
        if not text or text.startswith('/start'):
            reply = "👋 Namaste! Koi bhi Stock naam bhejo jaise:\nTCS, INFY, RELIANCE, NIFTY"
        else:
            # Symbol nikal - sirf pehla word
            symbol = text.split()[0].replace("$","")
            reply = get_candle(symbol)

        requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
    return "ok"

if __name__ == '__main__':
    app.run()
