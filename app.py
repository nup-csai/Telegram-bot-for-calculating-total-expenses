import logging
import os
import re
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import openai
from openai import OpenAI
from db import BotDB

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
token = os.getenv('BOT_TOKEN')

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

bot_db = BotDB('accountant.db')

Names = {}
Idis = {}

async def ask_for_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("What name would you like to be called by? Write command: /myName {name}")

async def my_name(update: Update, context) -> None:
    name = update.message.text.split()[1]
    user_id = update.message.from_user.id
    Names[name] = user_id
    Idis[user_id] = name

    chat_id = update.message.chat.id
    if not bot_db.chat_exists(chat_id):
        bot_db.add_chat(chat_id)

    if not bot_db.name_in_chat(name, chat_id):
        bot_db.add_name(chat_id, name, user_id)

    await update.message.reply_text(f"I am going to call you {name}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = update.effective_user

    if not bot_db.user_exists(user_id):
        bot_db.add_user(user_id)
        await update.message.reply_html(rf"Hi {user.mention_html()}! You've been added to the database.",
                                        reply_markup=ForceReply(selective=True))
        await ask_for_name(update, context)
    else:
        await update.message.reply_html(rf"Welcome back {user.mention_html()}!",
                                        reply_markup=ForceReply(selective=True))
        await ask_for_name(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

messages = [{'role': 'system', 'content': 'Keep replies within 20 words'}]
categories = [{'role': 'system', 'content': 'Keep replies within 20 words'}]
toWhom = [{'role': 'system', 'content': 'Keep replies within 20 words'}]

async def identify_message_category(message: str) -> str:
    categories.append({'role': 'user', 'content': f"identify whether the message '{message}' is about expense, income or neither. If it is neither give me one word: neither. If it is income or expense, give me two words: income or expense and amount of it"})

    responseM = client.chat.completions.create(model='gpt-4',
                                                messages=categories,
                                                temperature=0,
                                                max_tokens=50)

    categories.append({'role': 'assistant', 'content': responseM.choices[0].message.content})
    return responseM.choices[0].message.content

async def identify_name(message: str) -> str:
    toWhom.append({'role': 'user',
                   'content': f'Insert the name from the message {message}. Give only name in the nominative case or the word: "None" if there is no names.'})
    responseN = client.chat.completions.create(model='gpt-4',
                                               messages=toWhom,
                                               temperature=0,
                                               max_tokens=50)

    categories.append({'role': 'assistant', 'content': responseN.choices[0].message.content})
    return responseN.choices[0].message.content

async def bot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Question from User: %s", update.message.text)

    if update.message.text != '':
        user_input = update.message.text
        messages.append({'role': 'user', 'content': user_input})

        response = client.chat.completions.create(model='gpt-4',
                                                   messages=messages,
                                                   temperature=0,
                                                   max_tokens=50)

        messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        llm_reply = response.choices[0].message.content

        category = await identify_message_category(user_input)
        category = category.split()

        if category[0] == 'neither' or category[0] == 'Neither':
            await update.message.reply_text(llm_reply)
        elif category[0] == 'Income' or category[0] == 'income':
            inserted_name = await identify_name(user_input)
            if inserted_name != 'None':
                user_id = bot_db.get_name_id(inserted_name, update.message.chat.id)
                bot_db.add_record(user_id, '-', float(category[1].replace(',', '.')))
            bot_db.add_record(update.message.from_user.id, '+', float(category[1].replace(',', '.')))
            await update.message.reply_text("✅ record successfully added!")
        else:
            inserted_name = await identify_name(user_input)
            if inserted_name != 'None':
                user_id = bot_db.get_name_id(inserted_name, update.message.chat.id)
                bot_db.add_record(user_id, '+', float(category[1].replace(',', '.')))
            bot_db.add_record(update.message.from_user.id, '-', float(category[1].replace(',', '.')))
            await update.message.reply_text("✅ record successfully added!")
    else:
        return

async def add_record(update: Update, context) -> None:
    operation = '-' if update.message.text.split()[0] in ('/spent', '/s') else '+'
    value = re.sub(r'[\d,.]+', '', update.message.text).strip()

    if value:
        x = re.findall(r"\d+(?:.\d+)?", update.message.text)
        if x:
            value = float(x[0].replace(',', '.'))
            bot_db.add_record(update.message.from_user.id, operation, value)

            if operation == '-':
                await update.message.reply_text("✅ Expense record successfully added!")
            else:
                await update.message.reply_text("✅ Income record successfully added!")
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
        answer = f"History for the {within_als[within][1]}\n\n"

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
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_reply))

    application.add_handler(CommandHandler(CMD_VARIANTS, add_record))
    application.add_handler(CommandHandler("myName", my_name))
    application.add_handler(CommandHandler(CMD_HISTORY, history))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
