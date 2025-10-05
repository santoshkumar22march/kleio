"""
Telegram Bot for Kleio
"""

import os
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

from database import SessionLocal
from crud.user import get_user_by_telegram_id
from crud.telegram import create_verification_code, get_verification_code, delete_verification_code
from agent.langchain_agent import process_message

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    logger.info("Received /start command")
    telegram_id = update.message.from_user.id
    db = SessionLocal()
    user = get_user_by_telegram_id(db, telegram_id)
    db.close()

    if user:
        await update.message.reply_text(
            "👋 Welcome back!\n\nYour account is connected! You can now:\n"
            "• Add items: 'bought 2kg tomatoes'\n"
            "• Get shopping list: 'shopping list'\n"
            "• Get recipes: 'recipe for dinner'\n"
            "• Check inventory: 'what do I have?'\n\n"
            "Try asking me something!"
        )
    else:
        db = SessionLocal()
        code = create_verification_code(db, telegram_id)
        db.close()
        await update.message.reply_text(
            "🔐 Link Your Account\n\n"
            "To connect this Telegram to Kleio.ai:\n\n"
            "1. Go to: https://kleio.ai/settings\n"
            "2. Click 'Connect Telegram'\n"
            f"3. Enter this code: {code}\n\n"
            "⏰ Code expires in 10 minutes."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    telegram_id = update.message.from_user.id
    message_text = update.message.text
    chat_id = update.message.chat_id

    db = SessionLocal()
    user = get_user_by_telegram_id(db, telegram_id)
    db.close()

    if not user:
        await start(update, context)
        return

    await bot.send_chat_action(chat_id=chat_id, action="typing")

    response = await process_message(user.firebase_uid, message_text, str(chat_id))

    await update.message.reply_text(response)


def run_bot():
    """Run the Telegram bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram bot...")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
