import os
import time
import datetime
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from telegram import Bot, Update
from bot_log import Logger
import data_processing as dp
from weekly_maker import (
    new_entry_handler,
    remove_entry_handler,
    set_header_handler,
    set_footer_image_handler,
    generate_bulletin_handler,
    preview_handler,
)

token = os.getenv("TIEDOTE_BOT_TOKEN")
log_path = os.getenv("TIEDOTE_BOT_LOG_PATH")
admins = os.getenv("TIEDOTE_BOT_ADMINS").split(",")

logger = Logger(log_path).logger
logger.debug(os.getcwd())

schedule = dp.get_schedule_data("schedule.txt")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello!")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This bot summarizes the current weekly news\n\n"
        "Preview-command might output spoilers"
    )


async def viikkotiedote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = dp.news_message_fi(dp.current_news)
    await update.message.reply_text(message, parse_mode="html")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = dp.news_message_en(dp.current_news_en)
    await update.message.reply_text(message, parse_mode="html")


async def scheduled(context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Running scheduled messages...")
    for message in schedule:
        if (message["language"] == "fi") & (dp.current_news() != {}):
            await context.bot.send_message(
                message["chat_id"],
                dp.news_message_fi(dp.current_news),
                parse_mode="html",
            )
        elif (message["language"] == "en") & (dp.current_news_en() != {}):
            await context.bot.send_message(
                message["chat_id"],
                dp.news_message_en(dp.current_news_en),
                parse_mode="html",
            )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def flush_messages(bot: Bot):
    """Flushes the messages send to the bot during downtime so that the bot
    does not start spamming when it gets online again."""

    updates = await bot.get_updates()
    while updates:
        print("Flushing {} messages.".format(len(updates)))
        time.sleep(1)
        updates = await bot.get_updates(updates[-1]["update_id"] + 1)


async def post_init(app: Application):
    jq = app.job_queue
    if jq is None:
        raise Exception("JobQueue is None")
    await flush_messages(app.bot)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", info))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(CommandHandler("viikkotiedote", viikkotiedote))

    app.add_handler(new_entry_handler)
    app.add_handler(remove_entry_handler)
    app.add_handler(set_header_handler)
    app.add_handler(set_footer_image_handler)
    app.add_handler(generate_bulletin_handler)
    app.add_handler(preview_handler)

    jq.run_repeating(
        scheduled,
        interval=datetime.timedelta(weeks=1),
        first=datetime.datetime(2021, 2, 22, hour=7),
    )

    app.add_error_handler(error)

    logger.info("Post init done.")


def main():
    app = Application.builder().token(token).concurrent_updates(False).build()
    app.post_init = post_init
    app.run_polling()


if __name__ == "__main__":
    main()
