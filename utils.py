import requests
from datetime import datetime

def fetch_price(symbol, api_key):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"
    try:
        res = requests.get(url, timeout=10).json()
        return float(res.get("price", 0))
    except:
        return None

def generate_signal(price):
    if not price:
        return "⚠ Price not available"
    return "Overbought — Possible correction" if price % 2 == 0 else "Oversold — Possible rebound"

def format_response(pair, price):
    signal = generate_signal(price)
    return f"{pair}\nPrice: {price}\nSignal: {signal}\nUpdated: {datetime.utcnow()} UTC"
