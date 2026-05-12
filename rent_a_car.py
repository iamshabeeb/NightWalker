from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import random
import os

# ENV VARIABLES
TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = int(os.getenv("CHAT_ID"))

# STATES
ASK_PHONE, ASK_CAR, ASK_DAYS, CONFIRM, ASK_SCREENSHOT = range(5)

# LOCATIONS
CAR_LOCATIONS = [
    ("Kuttippuram Bus Stand", "https://maps.google.com/?q=Kuttippuram+Bus+Stand"),
    ("Changaramkulam Bus Stand", "https://maps.google.com/?q=Changaramkulam+Bus+Stand"),
    ("Guruvayoor Temple", "https://maps.google.com/?q=Guruvayoor+Temple"),
]


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey there 👋\n\nWelcome to Our Rent Car Service 🚗\n\nPlease Enter Your Mobile Number"
    )
    return ASK_PHONE


# PHONE
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    user = update.effective_user
    username = f"@{user.username}" if user.username else "No username"

    if not phone.isdigit() or len(phone) != 10:
        await update.message.reply_text("❌ Please enter a valid 10-digit mobile number.")

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"🚨 Invalid Phone Number\n\n"
                f"User: {user.full_name}\n"
                f"Username: {username}\n"
                f"User ID: {user.id}\n\n"
                f"Entered Value: {phone}"
            ),
        )
        return ASK_PHONE

    context.user_data["phone"] = phone

    await update.message.reply_text("Which car do you want?")
    return ASK_CAR


# CAR
async def ask_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    car = update.message.text
    user = update.effective_user
    username = f"@{user.username}" if user.username else "No username"

    if car == "12121234":
        context.user_data["car"] = car

        keyboard = [
            [InlineKeyboardButton(".5 day", callback_data="0.5")],
            [InlineKeyboardButton("1 day", callback_data="1")],
            [InlineKeyboardButton("1.5 day", callback_data="1.5")],
            [InlineKeyboardButton("2 day", callback_data="2")],
        ]

        await update.message.reply_text(
            "How many days?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ASK_DAYS

    else:
        await update.message.reply_text("Sorry, not available ❌")

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"🚨 Invalid Car Input\n\n"
                f"User: {user.full_name}\n"
                f"Username: {username}\n"
                f"User ID: {user.id}\n"
                f"Mobile: {context.user_data.get('phone')}\n\n"
                f"Entered Value: {car}"
            ),
        )
        return ASK_CAR


# DAYS (INLINE)
async def ask_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == "0.5":
        price = 1500
        days = ".5 day"
    elif choice == "1":
        price = 3000
        days = "1 day"
    else:
        await query.edit_message_text("Sorry, not available ❌")
        return ConversationHandler.END

    context.user_data["days"] = days
    context.user_data["price"] = price

    keyboard = [[
        InlineKeyboardButton("Confirm ✅", callback_data="confirm"),
        InlineKeyboardButton("Cancel ❌", callback_data="cancel"),
    ]]

    await query.edit_message_text(
        text=(
            f"Car: {context.user_data['car']}\n"
            f"Duration: {days}\n"
            f"Amount: ₹{price}\n\n"
            "Confirm booking?"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return CONFIRM


# CONFIRM
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == "confirm":
        user = update.effective_user
        username = f"@{user.username}" if user.username else "No username"

        car = context.user_data.get("car")
        days = context.user_data.get("days")
        price = context.user_data.get("price")
        phone = context.user_data.get("phone")

        await query.edit_message_text(
            f"✅ Booking Confirmed!\n\n"
            f"Please pay ₹{price} to 8787898967 📱\n\n"
            f"Send payment screenshot after payment."
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"🚨 New Booking Alert\n\n"
                f"User: {user.full_name}\n"
                f"Username: {username}\n"
                f"User ID: {user.id}\n"
                f"Mobile: {phone}\n\n"
                f"Car: {car}\n"
                f"Duration: {days}\n"
                f"Amount: ₹{price}"
            ),
        )

        return ASK_SCREENSHOT

    else:
        await query.edit_message_text("❌ Booking cancelled.")
        return ConversationHandler.END


# SCREENSHOT
async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.message.photo:
        location_name, map_link = random.choice(CAR_LOCATIONS)

        context.user_data.clear()

        keyboard = [[InlineKeyboardButton("🔁 Start Again", callback_data="restart")]]

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"✅ Payment received!\n\n"
                f"🚗 Your car is ready:\n"
                f"{location_name}\n"
                f"{map_link}\n\n"
                f"📞 Contact: 8787898967\n\n"
                f"⚠️ Don't forget to clear chat history"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return ConversationHandler.END

    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📸 Please send any payment screenshot to continue."
        )
        return ASK_SCREENSHOT


# RESTART BUTTON
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Hey there 👋\n\nWelcome to Our Rent Car Service 🚗\n\nPlease Enter Your Mobile Number"
    )

    return ASK_PHONE


# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_CAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_car)],
            ASK_DAYS: [CallbackQueryHandler(ask_days)],
            CONFIRM: [CallbackQueryHandler(confirm)],
            ASK_SCREENSHOT: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_screenshot),
                MessageHandler(~(filters.PHOTO | filters.Document.IMAGE), handle_screenshot),
            ],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()