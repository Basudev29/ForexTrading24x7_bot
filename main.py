import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TELEGRAM_BOT_TOKEN, TWELVEDATA_API_KEY, PAIRS
import math


BASE_URL = "https://api.twelvedata.com/price"


def fetch_price(symbol):
    try:
        params = {
            "symbol": symbol,
            "apikey": TWELVEDATA_API_KEY
        }
        res = requests.get(BASE_URL, params=params).json()

        if "price" in res:
            return float(res["price"])

        return None

    except Exception:
        return None


def support(price):
    return round(price - (price * 0.008), 3)


def resistance(price):
    return round(price + (price * 0.008), 3)


def signal_status(price):
    return "Overbought — Possible Correction" if price else "Waiting for Data"


async def full_market(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply = "📊 *Forex Market Live Update*\n\n"

    for title, symbol in PAIRS.items():
        price = fetch_price(symbol)

        if not price:
            reply += f"{title}\n⚠ Live price not available\n\n"
            continue

        reply += (
            f"📈 *{title}*\n"
            f"Price: `{price}`\n"
            f"Support: `{support(price)}`\n"
            f"Resistance: `{resistance(price)}`\n"
            f"Signal: {signal_status(price)}\n\n"
        )

    await update.message.reply_markdown(reply)


async def start(update: Update, context):
    await update.message.reply_text(
        "👋 ForexTrading24x7 Bot Activated\n\n"
        "Commands:\n"
        "/market — Full Market Update\n"
        "/eurusd\n/gbpusd\n/usdjpy\n/xauusd"
    )


async def pair_update(update: Update, context, pair_name, symbol):

    price = fetch_price(symbol)

    if not price:
        await update.message.reply_text("⚠ Live price not available")
        return

    text = (
        f"📈 {pair_name} — Live Update\n\n"
        f"Price: {price}\n"
        f"Support: {support(price)}\n"
        f"Resistance: {resistance(price)}\n"
        f"Signal: {signal_status(price)}"
    )

    await update.message.reply_text(text)


async def eur(update, ctx):
    await pair_update(update, ctx, "EUR/USD", "EUR/USD")


async def gbp(update, ctx):
    await pair_update(update, ctx, "GBP/USD", "GBP/USD")


async def jpy(update, ctx):
    await pair_update(update, ctx, "USD/JPY", "USD/JPY")


async def gold(update, ctx):
    await pair_update(update, ctx, "XAU/USD", "XAU/USD")


application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()


application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("market", full_market))
application.add_handler(CommandHandler("eurusd", eur))
application.add_handler(CommandHandler("gbpusd", gbp))
application.add_handler(CommandHandler("usdjpy", jpy))
application.add_handler(CommandHandler("xauusd", gold))


scheduler = AsyncIOScheduler()


async def auto_broadcast():
    chat_id = YOUR_PRIVATE_CHANNEL_OR_CHAT_ID   # optional
    # later we will enable broadcast mode


scheduler.start()


if __name__ == "__main__":
    application.run_polling()
