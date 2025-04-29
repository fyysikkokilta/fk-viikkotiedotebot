import os
import time
import datetime
from telegram.ext import Application, CommandHandler, ContextTypes
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
    message = dp.current_news()
    if message == "":
        message = "Tiedote on tyhjä"
    await update.message.reply_text(message, parse_mode="html")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = dp.current_news_en()
    if message == "":
        message = "No weekly news"
    await update.message.reply_text(message, parse_mode="html")


async def scheduled(context: ContextTypes.DEFAULT_TYPE):
    finnish_message = dp.current_news()
    english_message = dp.current_news_en()
    for message in schedule:
        if (message["language"] == "fi") & (finnish_message != ""):
            await context.bot.send_message(
                message["chat_id"],
                finnish_message,
                parse_mode="html",
            )
            logger.debug(f"Sent Finnish weekly to {message['chat_id']}")
        elif (message["language"] == "en") & (english_message != ""):
            await context.bot.send_message(
                message["chat_id"],
                english_message,
                parse_mode="html",
            )
            logger.debug(f"Sent English weekly to {message['chat_id']}")
    if finnish_message != "" and english_message != "":
        context.job.schedule_removal()


async def schedule_weekly_message(context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Running scheduled messages...")
    context.job_queue.run_custom(
        scheduled,
        {
            "id": "weekly_message",
            "trigger": "cron",
            "hour": "7-15",
            "replace_existing": True,
        },
    )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def flush_messages(bot: Bot):
    """Flushes the messages send to the bot during downtime so that the bot
    does not start spamming when it gets online again."""

    updates = await bot.get_updates()
    while updates:
        print(f"Flushing {len(updates)} messages.")
        time.sleep(1)
        updates = await bot.get_updates(updates[-1]["update_id"] + 1)


async def post_init(app: Application):
    jq = app.job_queue
    if jq is None:
        raise ValueError("JobQueue is None")
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
        schedule_weekly_message,
        interval=datetime.timedelta(weeks=1),
        first=datetime.datetime(2021, 2, 22, hour=0),
    )

    app.add_error_handler(error)

    logger.info("Post init done.")


def main():
    app = Application.builder().token(token).concurrent_updates(False).build()
    app.post_init = post_init
    app.run_polling()


if __name__ == "__main__":
    main()
