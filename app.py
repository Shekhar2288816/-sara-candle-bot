from flask import Flask
import yfinance as yf
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/')
def home():
    try:
        data = yf.download("^NSEI", period="1d", interval="5m", progress=False)
        if data.empty:
            return "Market band hai"
        data.index = data.index.tz_convert('Asia/Kolkata')
        c = data.between_time('09:15','09:20')
        if c.empty:
            return "<h2>9:20 Candle abhi nahi bani</h2>"
        high = float(c.iloc[-1]['High'])
        low = float(c.iloc[-1]['Low'])
        live = float(data['Close'].iloc[-1])
        if live > high:
            sig = f"BUY - High {high} cross - Live {live}"
        elif live < low:
            sig = f"SELL - Low {low} cross - Live {live}"
        else:
            sig = f"WAIT - H:{high} L:{low} Live:{live}"
        return f"<h1>Sara 9:20 Bot</h1><h2>{sig}</h2>"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
