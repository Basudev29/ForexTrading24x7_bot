import os
import asyncio
import logging
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# --------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

# --------- ENV VARIABLES ----------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TD_API_KEY = os.getenv("TWELVEDATA_API_KEY")

if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in environment")

if not TD_API_KEY:
    logging.warning("⚠ TWELVEDATA_API_KEY missing — prices may fail")


# --------- PRICE FETCH FUNCTION ----------
def fetch_price(symbol):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TD_API_KEY}"
        res = requests.get(url, timeout=10).json()

        if "price" in res:
            return float(res["price"])

        logging.error(f"API Error for {symbol}: {res}")
        return None

    except Exception as e:
        logging.error(f"Request failed: {e}")
        return None


# --------- SIGNAL ENGINE ----------
def generate_signal(price):
    if not price:
        return "⚠ Price unavailable"

    return (
        "🟢 BUY Trend — Look for pullback" if price % 2 == 0
        else "🔴 SELL Trend — Possible correction"
    )


# --------- FORMAT OUTPUT ----------
def format_response(pair, price):
    if not price:
        return f"{pair}\n⚠ Live price not available"

    signal = generate_signal(price)

    return (
        f"{pair}\n"
        f"Price: {price}\n"
        f"Signal: {signal}\n"
        f"Updated: {datetime.utcnow()} UTC"
    )


# --------- COMMAND: /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *ForexTrading24x7 Auto Bot Activated*\n\n"
        "Select commands:\n\n"
        "📊 /market — Full Market Update\n"
        "💶 /eurusd\n"
        "💷 /gbpusd\n"
        "💹 /usdjpy\n"
        "🏆 /gold\n"
    )
    await update.message.reply_markdown(text)


# --------- COMMAND: MARKET UPDATE ----------
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pairs = {
        "📈 EUR/USD": "EUR/USD",
        "💷 GBP/USD": "GBP/USD",
        "💹 USD/JPY": "USD/JPY",
        "🏆 GOLD XAU/USD": "XAU/USD"
    }

    for name, sym in pairs.items():
        price = fetch_price(sym)
        await update.message.reply_text(format_response(name, price))


# --------- INDIVIDUAL PAIR COMMANDS ----------
async def eur(update: Update, ctx): 
    p = fetch_price("EUR/USD")
    await update.message.reply_text(format_response("📈 EUR/USD", p))

async def gbp(update: Update, ctx): 
    p = fetch_price("GBP/USD")
    await update.message.reply_text(format_response("💷 GBP/USD", p))

async def jpy(update: Update, ctx): 
    p = fetch_price("USD/JPY")
    await update.message.reply_text(format_response("💹 USD/JPY", p))

async def gold(update: Update, ctx): 
    p = fetch_price("XAU/USD")
    await update.message.reply_text(format_response("🏆 GOLD", p))


# --------- MAIN APP ----------
async def main():

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("market", market))
    application.add_handler(CommandHandler("eurusd", eur))
    application.add_handler(CommandHandler("gbpusd", gbp))
    application.add_handler(CommandHandler("usdjpy", jpy))
    application.add_handler(CommandHandler("gold", gold))

    logging.info("🚀 Bot started… polling updates")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
