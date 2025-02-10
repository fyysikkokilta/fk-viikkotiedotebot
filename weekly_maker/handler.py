import base64
import os
from io import BytesIO
from slugify import slugify
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ExtBot,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from PIL import Image

from weekly_maker.bulletin import create_bulletin, create_preview
from weekly_maker.crud import (
    add_entry,
    add_entry_en,
    get_entries,
    get_entries_en,
    delete_entry,
    delete_entry_en,
    update_header,
    update_header_en,
    update_footer_image,
    update_footer_image_en,
)
from weekly_maker.utils import CATEGORIES, CATEGORIES_EN, get_week_number

LANGUAGE_NEW, CATEGORY, TITLE, CONTENT, DATE, IMAGE, CONFIRM_NEW = [
    "LANGUAGE_NEW",
    "CATEGORY",
    "TITLE",
    "CONTENT",
    "DATE",
    "IMAGE",
    "CONFIRM_NEW",
]
LANGUAGE_REMOVE, CHOOSE_ENTRY, CONFIRM_REMOVE = [
    "LANGUAGE_REMOVE",
    "CHOOSE_ENTRY",
    "CONFIRM_REMOVE",
]
LANGUAGE_HEADER, HEADER = ["LANGUAGE_HEADER", "HEADER"]
LANGUAGE_FOOTER, FOOTER_IMAGE = ["LANGUAGE_FOOTER", "FOOTER_IMAGE"]

ADMINS = os.getenv("TIEDOTE_BOT_ADMINS").split(",")


async def is_admin(bot: ExtBot, update: Update):
    """Check if user is admin."""
    if update.effective_user is None:
        raise ValueError("Update does not have effective_user")

    if str(update.effective_user.id) in ADMINS:
        return True
    else:
        if update.message is None:
            raise ValueError("Update does not have message")
        await bot.send_message(update.message.chat.id, "You are not authorized.")
        return False


async def new_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update):
        return ConversationHandler.END
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Finnish", callback_data="fi"),
                InlineKeyboardButton(text="English", callback_data="en"),
            ]
        ]
    )

    await update.message.reply_text(
        (
            f"You are about to add a new entry to the weekly news for the week number "
            f"{get_week_number()}. Are you adding it to the Finnish or English version?"
        ),
        reply_markup=keyboard,
    )

    return LANGUAGE_NEW


async def language_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()
    chat_data["language"] = query.data

    categories = CATEGORIES if query.data == "fi" else CATEGORIES_EN

    await query.edit_message_text("Choose the category of the entry")
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=category, callback_data=category)]
            for category in categories
        ]
    )
    await query.edit_message_reply_markup(keyboard)
    return CATEGORY


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()
    chat_data["category"] = query.data

    await query.edit_message_text("Enter the title of the entry")
    return TITLE


async def title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    chat_data["header"] = update.message.text

    await update.message.reply_text("Enter the content of the entry")
    return CONTENT


async def content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    chat_data["content"] = (
        update.message.text_html.replace("\n", "<br>") if update.message.text else ""
    )  # Use text_html to preserve the formatting

    await update.message.reply_text(
        "Enter the date of the entry in the format dd.mm.yyyy."
    )

    return DATE


async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    date_text = update.message.text
    try:
        day, month, year = map(int, date_text.split("."))
        chat_data["date"] = (day, month, year)
    except ValueError:
        await update.message.reply_text(
            "Invalid date format. Enter the date in the format dd.mm.yyyy."
        )
        return DATE

    await update.message.reply_text(
        "Send an image for the entry. Enter /skip if you don't want to add an image."
    )
    return IMAGE


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    if update.message.text == "/skip":
        chat_data["image"] = ""
    elif len(update.message.photo) > 0:
        image_data = await update.message.photo[-1].get_file()
        f = BytesIO(await image_data.download_as_bytearray())

        img = Image.open(f)

        width_percent = 350 / float(img.size[0])
        new_height = int((float(img.size[1]) * float(width_percent)))
        img = img.resize((350, new_height), Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format="PNG")
        chat_data["image"] = "data:image/png;base64, " + base64.b64encode(
            output.getvalue()
        ).decode("utf-8")
    else:
        return IMAGE

    await update.message.reply_text(
        "Are you sure you want to add this entry to the weekly news?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Yes", callback_data="yes"),
                    InlineKeyboardButton(text="No", callback_data="no"),
                ]
            ]
        ),
    )
    return CONFIRM_NEW


async def confirm_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()

    if query.data == "yes":
        await query.edit_message_text("Entry added successfully!")
        entry = {
            "id": slugify(chat_data["header"]),
            "category": chat_data["category"],
            "header": chat_data["header"],
            "content": chat_data["content"],
            "date": chat_data["date"],
            "image": chat_data["image"],
        }
        if chat_data["language"] == "fi":
            add_entry(entry)
        else:
            add_entry_en(entry)
        return ConversationHandler.END
    else:
        await query.edit_message_text("Cancelled the entry creation.")
        return ConversationHandler.END


async def remove_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update):
        return ConversationHandler.END
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Finnish", callback_data="fi"),
                InlineKeyboardButton(text="English", callback_data="en"),
            ]
        ]
    )

    await update.message.reply_text(
        (
            f"You are about to remove an entry from the weekly news for the week number "
            f"{get_week_number()}. Are you removing it from the Finnish or English version?"
        ),
        reply_markup=keyboard,
    )

    return LANGUAGE_REMOVE


async def language_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()
    chat_data["language"] = query.data
    if query.data == "fi":
        entries = get_entries()
    else:
        entries = get_entries_en()

    if not entries or len(entries) == 0:
        await query.edit_message_text("There are no entries.")
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=entry["header"], callback_data=str(i))]
            for i, entry in enumerate(entries)
        ]
    )

    await query.edit_message_text("Choose the entry to remove", reply_markup=keyboard)

    return CHOOSE_ENTRY


async def choose_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()
    chat_data["entry_index"] = int(query.data)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Yes", callback_data="yes"),
                InlineKeyboardButton(text="No", callback_data="no"),
            ]
        ]
    )

    await query.edit_message_text(
        "Are you sure you want to remove this entry?", reply_markup=keyboard
    )
    return CONFIRM_REMOVE


async def confirm_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()

    if query.data == "yes":
        await query.edit_message_text("Entry removed successfully.")
        if chat_data["language"] == "fi":
            delete_entry(chat_data["entry_index"])
        else:
            delete_entry_en(chat_data["entry_index"])
        return ConversationHandler.END
    else:
        await query.edit_message_text("Cancelled the entry removal.")
        return ConversationHandler.END


async def set_header(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update):
        return ConversationHandler.END
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Finnish", callback_data="fi"),
                InlineKeyboardButton(text="English", callback_data="en"),
            ]
        ]
    )

    await update.message.reply_text(
        (
            f"You are about to set the header for the weekly news for the week number "
            f"{get_week_number()}. Are you setting it for the Finnish or English version?"
        ),
        reply_markup=keyboard,
    )

    return LANGUAGE_HEADER


async def language_header(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()
    chat_data["language"] = query.data

    await query.edit_message_text("Enter the header for the weekly news")
    return HEADER


async def header(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    header_text = update.message.text

    await update.message.reply_text("Header set successfully!")
    if chat_data["language"] == "fi":
        update_header(header_text)
    else:
        update_header_en(header_text)
    return ConversationHandler.END


async def set_footer_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update):
        return ConversationHandler.END
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Finnish", callback_data="fi"),
                InlineKeyboardButton(text="English", callback_data="en"),
            ]
        ]
    )

    await update.message.reply_text(
        (
            f"You are about to set the footer image for the weekly news for the week number "
            f"{get_week_number()}. Are you setting it for the Finnish or English version?"
        ),
        reply_markup=keyboard,
    )

    return LANGUAGE_FOOTER


async def language_footer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_data = context.chat_data
    await query.answer()
    chat_data["language"] = query.data

    await query.edit_message_text("Send the image for the footer")
    return FOOTER_IMAGE


async def footer_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    image_data = await update.message.photo[-1].get_file()
    f = BytesIO(await image_data.download_as_bytearray())

    # Open and resize image
    img = Image.open(f)
    # Calculate new height maintaining aspect ratio
    width_percent = 400 / float(img.size[0])
    new_height = int((float(img.size[1]) * float(width_percent)))
    img = img.resize((400, new_height), Image.Resampling.LANCZOS)

    # Save resized image to BytesIO
    output = BytesIO()
    img.save(output, format="PNG")
    footer_image_data = "data:image/png;base64, " + base64.b64encode(
        output.getvalue()
    ).decode("utf-8")

    await update.message.reply_text("Footer image set successfully!")
    if chat_data["language"] == "fi":
        update_footer_image(footer_image_data)
    else:
        update_footer_image_en(footer_image_data)
    return ConversationHandler.END


async def generate_bulletin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update):
        return ConversationHandler.END
    bulletin_files = create_bulletin()
    await update.message.reply_text(
        f"Bulletin files for the week {get_week_number()} generated and added to Wordpress succesfully."
    )
    week = get_week_number()
    await context.bot.send_document(
        chat_id=update.message.chat_id,
        document=BytesIO(bulletin_files[0].encode("utf-8")),
        filename=f"kilta-tiedottaa-viikko-{week:02}.html",
    )
    await context.bot.send_document(
        chat_id=update.message.chat_id,
        document=BytesIO(bulletin_files[1].encode("utf-8")),
        filename=f"kilta-tiedottaa-viikko-{week:02}-en.html",
    )


async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update):
        return ConversationHandler.END
    message_fi, message_en = create_preview()
    await update.message.reply_text(message_fi + "\n\n" + message_en, parse_mode="html")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled the current operation.")
    return ConversationHandler.END


new_entry_handler = ConversationHandler(
    entry_points=[CommandHandler("new_entry", new_entry)],
    states={
        LANGUAGE_NEW: [CallbackQueryHandler(language_new)],
        CATEGORY: [CallbackQueryHandler(category)],
        TITLE: [MessageHandler(filters.TEXT, title)],
        CONTENT: [MessageHandler(filters.TEXT, content)],
        DATE: [MessageHandler(filters.TEXT, date)],
        IMAGE: [MessageHandler(filters.PHOTO | filters.COMMAND, image)],
        CONFIRM_NEW: [CallbackQueryHandler(confirm_new)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

remove_entry_handler = ConversationHandler(
    entry_points=[CommandHandler("remove_entry", remove_entry)],
    states={
        LANGUAGE_REMOVE: [CallbackQueryHandler(language_remove)],
        CHOOSE_ENTRY: [CallbackQueryHandler(choose_entry)],
        CONFIRM_REMOVE: [CallbackQueryHandler(confirm_remove)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

set_header_handler = ConversationHandler(
    entry_points=[CommandHandler("set_header", set_header)],
    states={
        LANGUAGE_HEADER: [CallbackQueryHandler(language_header)],
        HEADER: [MessageHandler(filters.TEXT, header)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
set_footer_image_handler = ConversationHandler(
    entry_points=[CommandHandler("set_footer_image", set_footer_image)],
    states={
        LANGUAGE_FOOTER: [CallbackQueryHandler(language_footer)],
        FOOTER_IMAGE: [MessageHandler(filters.PHOTO, footer_image)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

generate_bulletin_handler = CommandHandler(
    "generate_bulletin", generate_bulletin, filters=filters.ChatType.PRIVATE
)

preview_handler = CommandHandler("preview", preview, filters=filters.ChatType.PRIVATE)
