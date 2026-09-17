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
        symbol = symbol.upper().strip()
        ticker_str = symbol if "." in symbol else f"{symbol}.NS"

        stock = yf.Ticker(ticker_str)
        # History is more stable than download on Render
        hist = stock.history(period="5d")

        if hist.empty:
            return f"❌ {symbol} nahi mila. NSE naam likh jaise TCS, RELIANCE, INFY"

        # Last 2 days
        today = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else today

        open_p = float(today['Open'])
        close_p = float(today['Close'])
        high_p = float(today['High'])
        low_p = float(today['Low'])
        prev_close = float(prev['Close'])

        change = close_p - prev_close
        perc = (change/prev_close*100) if prev_close else 0

        if close_p > open_p:
            candle = "🟢 GREEN Bullish"
            trend = "Buyer Strong"
        elif close_p < open_p:
            candle = "🔴 RED Bearish"
            trend = "Seller Strong"
        else:
            candle = "⚪ Doji"
            trend = "Confusion"

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist).strftime("%d-%b %I:%M %p")

        msg = f"""📊 *{symbol}* - {candle}
_{trend}_

💰 Close: {close_p:.2f} ({perc:+.2f}%)
🔓 Open: {open_p:.2f}
⬆️ High: {high_p:.2f}
⬇️ Low: {low_p:.2f}
📉 Prev Close: {prev_close:.2f}

🕐 {now} IST
🤖 SARA Bot"""
        return msg
    except Exception as e:
        print(f"Error: {e}")
        return f"⚠️ {symbol} pe thoda issue hai ({e}). 2 min baad TCS dobara try kar."

@app.route('/')
def home():
    return "SARA Bot Live"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        if text.startswith('/start'):
            reply = "👋 Namaste! Stock naam bhejo\nJaise: TCS, RELIANCE, NIFTY, BANKNIFTY"
        else:
            sym = text.split()[0].replace("$","")
            reply = get_candle(sym)
        requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
    return "ok"

if __name__ == '__main__':
    app.run()
