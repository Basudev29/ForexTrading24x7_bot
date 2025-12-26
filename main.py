import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing — Render ENV Vars me set karo")


# ===== BASIC COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste 👋\n\nBot successfully deployed on Render!\n\n"
        "Type /help for commands."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available Commands:\n"
        "/start – Bot Status\n"
        "/help – Command List\n"
        "/about – Bot Info"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Advanced Telegram Bot\n"
        "Hosted on Render — Auto Online 24x7"
    )


# ===== AUTO-REPLY CHATBOT =====
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    reply = f"🟢 Received: {text}"
    await update.message.reply_text(reply)


# ====== MAIN APP RUNNER ======
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    print("🚀 Bot Started — Polling Active")

    await app.run_polling(close_loop=False)


if __name__ == "__main__":
    asyncio.run(main())
