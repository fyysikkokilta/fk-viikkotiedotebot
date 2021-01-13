import os
import requests
import datetime
from telegram.ext import (Updater, CommandHandler)
from bot_log import Logger

token = os.getenv("TIEDOTE_BOT_TOKEN")
log_path = os.getenv("TIEDOTE_BOT_LOG_PATH")

logger = Logger(log_path).logger
logger.debug(os.getcwd())
weekly_base_url = "https://www.fyysikkokilta.fi/wp-content/uploads/viikkotiedote-data/week{}.json"


def start(update, context):
    update.message.reply_text("Hello!")


def info(update, context):
    update.message.reply_text("This bot summarizes the current weekly news\n\n"
                              "Preview-command might output spoilers")


def get_weekly_data(week_number, base_url=weekly_base_url):
    week_string = "{:02}".format(week_number)
    url = base_url.format(week_string)
    return requests.get(url).json()


def current_week_number():
    today = datetime.date.today()
    week = today.isocalendar()[1]
    print(week)
    return 48


def weekly(update, context):
    data = get_weekly_data(current_week_number())
    headers = ["-" + data["_default"][key]["header"] for key in data["_default"]]
    summary = "\n\n".join(headers)
    update.message.reply_text("Viikkotiedote / Weekly News\n\n"+summary)


def preview(update, context):
    data = get_weekly_data(current_week_number()+1)
    headers = ["-" + data["_default"][key]["header"] for key in data["_default"]]
    summary = "\n\n".join(headers)
    update.message.reply_text("Viikkotiedote / Weekly News\n\n" + summary)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", info))
    dp.add_handler(CommandHandler("weekly", weekly))
    dp.add_handler(CommandHandler("preview", preview))
    dp.add_error_handler(error)

    updater.start_polling()


if __name__ == '__main__':
    main()
