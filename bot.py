import os
from telegram.ext import (Updater, CommandHandler)
from bot_log import Logger
import data_processing as dp

token = os.getenv("TIEDOTE_BOT_TOKEN")
log_path = os.getenv("TIEDOTE_BOT_LOG_PATH")

logger = Logger(log_path).logger
logger.debug(os.getcwd())


def start(update, context):
    update.message.reply_text("Hello!")


def info(update, context):
    update.message.reply_text("This bot summarizes the current weekly news\n\n"
                              "Preview-command might output spoilers")


def viikkotiedote(update, context):
    data = dp.current_news()
    headers = ["-" + data["_default"][key]["header"] for key in data["_default"]]
    summary = "\n\n".join(headers)
    update.message.reply_text("Viikkotiedote\n\n" + summary)


def weekly(update, context):
    data = dp.current_news_en()
    headers = ["-" + data["_default"][key]["header"] for key in data["_default"]]
    summary = "\n\n".join(headers)
    update.message.reply_text("Weekly News\n\n"+summary)


def preview(update, context):
    data = dp.next_week_news()
    headers = ["-" + data["_default"][key]["header"] for key in data["_default"]]
    summary = "\n\n".join(headers)
    update.message.reply_text("Viikkotiedote / Weekly News\n\n" + summary)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token)

    disp = updater.dispatcher

    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(CommandHandler("help", info))
    disp.add_handler(CommandHandler("weekly", weekly))
    disp.add_handler(CommandHandler("viikkotiedote", viikkotiedote))
    disp.add_handler(CommandHandler("preview", preview))
    disp.add_error_handler(error)

    updater.start_polling()


if __name__ == '__main__':
    main()
