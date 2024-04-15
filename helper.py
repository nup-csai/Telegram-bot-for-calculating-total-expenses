import logging
from telegram import Bot, Update, ForceReply, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, Application, ContextTypes

import openai
from openai import OpenAI

import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Create bot instance
bot = Bot(token=config.BOT_TOKEN)
application = Application.builder().token(config.BOT_TOKEN).build()

# Define command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your bot.")

# Register command handlers
application.add_handler(CommandHandler("start", start))

# Start polling for updates
application.start_polling()
application.run_polling(allowed_updates=Update.ALL_TYPES)

