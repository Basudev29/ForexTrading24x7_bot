import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from config import TELEGRAM_BOT_TOKEN, TWELVEDATA_API_KEY, PAIRS


BASE_URL = "https://api.twelvedata.com/price"


def fetch_price(symbol):
    try:
        r = requests.get(BASE_URL, params={
            "symbol": symbol,
            "apikey": TWELVEDATA_API_KEY
        }).json()

        return float(r["price"]) if "price" in r else None

    except Exception:
        return None


def support(price): return round(price * 0.992, 3)
def resistance(price): return round(price * 1.008, 3)


def signal_status(price):
    return "Overbought — Possible Correction" if price else "Waiting for Data"


async def start(update: Update, context):
    await update.message.reply_text(
        "👋 ForexTrading24x7 Bot Activated\n\n"
        "Commands:\n"
        "/market — Full Market Update\n"
        "/eurusd\n/gbpusd\n/usdjpy\n/xauusd"
    )


async def full_market(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply = "📊 *Forex Market Live Update*\n\n"

    for name, symbol in PAIRS.items():
        price = fetch_price(symbol)

        if not price:
            reply += f"{name}\n⚠ Live price not available\n\n"
            continue

        reply += (
            f"📈 *{name}*\n"
            f"Price: `{price}`\n"
            f"Support: `{support(price)}`\n"
            f"Resistance: `{resistance(price)}`\n"
            f"Signal: {signal_status(price)}\n\n"
        )

    await update.message.reply_markdown(reply)


async def pair(update, ctx, name, symbol):
    price = fetch_price(symbol)

    if not price:
        await update.message.reply_text("⚠ Live price not available")
        return

    await update.message.reply_text(
        f"📈 {name}\n\n"
        f"Price: {price}\n"
        f"Support: {support(price)}\n"
        f"Resistance: {resistance(price)}\n"
        f"Signal: {signal_status(price)}"
    )


async def eur(update, ctx):  await pair(update, ctx, "EUR/USD", "EUR/USD")
async def gbp(update, ctx):  await pair(update, ctx, "GBP/USD", "GBP/USD")
async def jpy(update, ctx):  await pair(update, ctx, "USD/JPY", "USD/JPY")
async def gold(update, ctx): await pair(update, ctx, "XAU/USD", "XAU/USD")


application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("market", full_market))
application.add_handler(CommandHandler("eurusd", eur))
application.add_handler(CommandHandler("gbpusd", gbp))
application.add_handler(CommandHandler("usdjpy", jpy))
application.add_handler(CommandHandler("xauusd", gold))


# ===========================
# 🔁 AUTO BROADCAST (job queue)
# ===========================
async def auto_market_push(context):
    chat_id = context.job.chat_id
    price = fetch_price("EUR/USD")
    if price:
        await context.bot.send_message(
            chat_id,
            f"⏰ Auto Update — EUR/USD: {price}"
        )


def enable_auto_updates(application):
    # change chat id later (admin group / channel)
    chat_id = None   # keep None for now

    if chat_id:
            application.job_queue.run_repeating(
                auto_market_push,
                interval=3600,   # every 1 hour
                first=10,
                chat_id=chat_id
            )


enable_auto_updates(application)


if __name__ == "__main__":
    application.run_polling()
