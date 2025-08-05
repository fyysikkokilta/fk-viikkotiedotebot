import os
import time
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Bot, Update
from bot_log import Logger
import data_processing as dp

token = os.getenv("BOT_TOKEN")
base_url = os.getenv("NEWSLETTER_BASE_URL")

logger = Logger().logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello!")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot summarizes the current weekly news")


async def viikkotiedote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = dp.get_newsletter_data(base_url, "fi")
    await update.message.reply_text(message, parse_mode="html")


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = dp.get_newsletter_data(base_url, "en")
    await update.message.reply_text(message, parse_mode="html")


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
    await flush_messages(app.bot)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", info))
    app.add_handler(CommandHandler("weekly", weekly))
    app.add_handler(CommandHandler("viikkotiedote", viikkotiedote))

    app.add_error_handler(error)

    logger.info("Post init done.")


def main():
    app = Application.builder().token(token).concurrent_updates(False).build()
    app.post_init = post_init
    app.run_polling()


if __name__ == "__main__":
    main()
