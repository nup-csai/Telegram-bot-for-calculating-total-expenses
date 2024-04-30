import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import openai
from openai import OpenAI
import re
import os
from dotenv import load_dotenv
from db import BotDB

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
token = os.getenv('BOT_TOKEN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

bot_db = BotDB('accountant.db')

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.message.from_user.id
    print(user_id)
    user = update.effective_user
    if not bot_db.user_exists(user_id):
        bot_db.add_user(user_id)
        await update.message.reply_html(rf"Hi {user.mention_html()}! You've been added to the database.",
        reply_markup=ForceReply(selective=True),
    )
    else:
        await update.message.reply_html(rf"Welcome back {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)



messages = [{'role': 'system', 'content': 'Keep replies within 20 words'}]


async def bot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    logger.info("Question from User: %s", update.message.text)

    if update.message.text != '':
        user_input = update.message.text

        messages.append({'role': 'user', 'content': user_input})

        response = client.chat.completions.create(model = 'gpt-4',
        messages = messages,
        temperature = 0,
        max_tokens = 50)

        messages.append({'role':'assistant','content':response.choices[0].message.content})
        llm_reply = response.choices[0].message.content

    else:
        return

    await update.message.reply_text(llm_reply)

async def add_record(update: Update, context) -> None:
    operation = '-' if update.message.text.split()[0] in ('/spent', '/s') else '+'

    value = re.sub(r'[\d,.]+', '', update.message.text).strip()

    if value:
        x = re.findall(r"\d+(?:.\d+)?", update.message.text)
        if x:
            value = float(x[0].replace(',', '.'))

            bot_db.add_record(update.message.from_user.id, operation, value)

            if operation == '-':
                await update.message.reply_text("✅ Income record successfully added!")
            else:
                await update.message.reply_text("✅ Expense record successfully added!")
        else:
            await update.message.reply_text("Give the correct number of money")
    else:
        await update.message.reply_text("No amount of money provided!")

async def history(update: Update, context) -> None:
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }

    cmd = re.sub(r'/h(?:istory)?', '', update.message.text).strip().lower()

    within = 'day'
    for k, als in within_als.items():
        if cmd in als:
            within = k
            break

    records = bot_db.get_records(update.message.from_user.id, within)

    if records:
        answer = f"History for the {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("-- Expense" if not r[2] else "++ Income") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        await update.message.reply_text(answer, parse_mode='HTML')
    else:
        await update.message.reply_text("No records found!")


CMD_VARIANTS = ('spent', 's', 'earned', 'e')
CMD_HISTORY = ('history', 'h')

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_reply))
    application.add_handler(CommandHandler(CMD_VARIANTS, add_record))
    application.add_handler(CommandHandler(CMD_HISTORY, history))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
