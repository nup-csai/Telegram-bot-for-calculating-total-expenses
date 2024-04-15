from helper import application
from telegram.ext import CommandHandler, MessageHandler, Filters
from bot import BotDB  # Подключение модуля BotDB
from telegram.ext.dispatcher import run_async  # Подключение декоратора run_async из telegram.ext.dispatcher

import re  # Импорт модуля re для работы с регулярными выражениями
import config  # Импорт модуля config.py для доступа к конфигурационным данным

# Обработчик команды /start
@run_async
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

# Обработчик команд /spent, /earned, /s, /e
@run_async
async def add_record(update: Update, context):
    cmd_variants = ('/spent', '/s', '/earned', '/e', '!spent', '!s', '!earned', '!e')
    operation = '-' if update.message.text.split()[0] in ('/spent', '/s', '!spent', '!s') else '+'

    value = re.sub(r'[\d,.]+', '', update.message.text).strip()

    if value:
        x = re.findall(r"\d+(?:.\d+)?", update.message.text)
        if x:
            value = float(x[0].replace(',', '.'))

            BotDB.add_record(update.message.from_user.id, operation, value)

            if operation == '-':
                update.message.reply_text("✅ Запись о расходе успешно внесена!")
            else:
                update.message.reply_text("✅ Запись о доходе успешно внесена!")
        else:
            update.message.reply_text("Не удалось определить сумму!")
    else:
        update.message.reply_text("Не введена сумма!")

# Обработчик команд /history, /h
@run_async
async def history(update: Update, context):
    cmd_variants = ('/history', '/h', '!history', '!h')
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

    records = BotDB.get_records(update.message.from_user.id, within)

    if records:
        answer = f"История операций за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        update.message.reply_text(answer, parse_mode='HTML')
    else:
        update.message.reply_text("Записей не обнаружено!")

# Добавление обработчиков команд
def add_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("spent", add_record))
    application.add_handler(CommandHandler("history", history))

add_handlers(application)  # Добавление обработчиков в Dispatcher
