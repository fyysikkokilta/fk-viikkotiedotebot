import os
import time
import datetime
from telegram.ext import (Updater, CommandHandler)
from bot_log import Logger
import data_processing as dp

token = os.getenv("TIEDOTE_BOT_TOKEN")
log_path = os.getenv("TIEDOTE_BOT_LOG_PATH")
admins = os.getenv("TIEDOTE_BOT_ADMINS").split(",")

logger = Logger(log_path).logger
logger.debug(os.getcwd())

schedule = dp.get_schedule_data('schedule.txt')


def start(update, context):
    update.message.reply_text("Hello!")


def info(update, context):
    update.message.reply_text("This bot summarizes the current weekly news\n\n"
                              "Preview-command might output spoilers")


def viikkotiedote(update, context):
    message = dp.news_message_fi(dp.current_news)
    update.message.reply_text(message, parse_mode="html")


def weekly(update, context):
    message = dp.news_message_en(dp.current_news_en)
    update.message.reply_text(message, parse_mode="html")


def preview(update, context):
    if (update.message.chat.type == "private") & (update.message.from_user.username in admins):
        message_fi = dp.news_message_fi(dp.next_week_news)
        message_en = dp.news_message_en(dp.next_week_news_en)
        update.message.reply_text(message_fi+"\n\n"+message_en, parse_mode="html")
    else:
        update.message.reply_text("<a>&#x1F440;</a>", parse_mode="html")


def scheduled(context):
    logger.debug('Running scheduled messages...')
    for message in schedule:
        if (message['language'] == 'fi') & (dp.current_news() != {}):
            context.bot.send_message(message['chat_id'], dp.news_message_fi(dp.current_news), parse_mode="html")
        elif (message['language'] == 'en') & (dp.current_news_en() != {}):
            context.bot.send_message(message['chat_id'], dp.news_message_en(dp.current_news_en), parse_mode="html")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def flush_messages(bot):
    """Flushes the messages send to the bot during downtime so that the bot
    does not start spamming when it gets online again."""

    updates = bot.get_updates()
    while updates:
        print("Flushing {} messages.".format(len(updates)))
        time.sleep(1)
        updates = bot.get_updates(updates[-1]["update_id"] + 1)


def main():
    updater = Updater(token)
    disp = updater.dispatcher
    jq = updater.job_queue

    flush_messages(updater.bot)

    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(CommandHandler("help", info))
    disp.add_handler(CommandHandler("weekly", weekly))
    disp.add_handler(CommandHandler("viikkotiedote", viikkotiedote))
    disp.add_handler(CommandHandler("preview", preview))

    jq.run_repeating(scheduled, context=updater.bot,
                     interval=datetime.timedelta(weeks=1),
                     first=datetime.datetime(2021, 2, 22, hour=7))

    disp.add_error_handler(error)
    updater.start_polling()


if __name__ == '__main__':
    main()
