from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, TWELVEDATA_API_KEY
from utils import fetch_price, format_response

PAIRS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "GOLD": "XAU/USD"
}

# ---------- Commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ForexTrading24x7 Bot Active\nUse /market for full update")

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for name, sym in PAIRS.items():
        price = fetch_price(sym, TWELVEDATA_API_KEY)
        await update.message.reply_text(format_response(name, price))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"🟢 You said: {text}")

# ---------- Admin Broadcast ----------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized")
        return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("Provide message to broadcast")
        return
    # Broadcast logic will go here (future DB tracking)
    await update.message.reply_text(f"✅ Broadcast sent: {msg}")

# ---------- Main ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("🚀 Bot Started — Polling...")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
