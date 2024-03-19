#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from dotenv import load_dotenv
load_dotenv()
import openai
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)



openai.api_type = "open_ai"
openai.base_url ="https://platform.openai.com/api-keys"
openai.api_key = "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"
messages = [{'role': 'system', 'content': 'Keep replies within 20 words'}]


async def bot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    logger.info("Question from User: %s", update.message.text)

    if update.message.text != '':
        user_input = update.message.text

        messages.append({'role': 'user', 'content': user_input})

        response = openai.ChatCompletion.create(
            model = 'gpt-4',
            messages = messages,
            tempreture = 0,
            max_tokens = -1
        )

        messages.append({'role':'assistent','content':response.choices[0].message.content})
        llm_reply = response.choices[0].message.content

    else:
        return

    await update.message.reply_text(llm_reply)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6806503070:AAG2v1CoC6bGNw9LU-N-jnhIKqHgXo-D24Q").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_reply))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
