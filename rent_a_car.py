from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import random



import os
TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = os.getenv("CHAT_ID")

# States
ASK_CAR, ASK_DAYS, CONFIRM, ASK_SCREENSHOT = range(4)

# Car locations (Google Maps)
CAR_LOCATIONS = [
    ("Kuttippuram Bus Stand", "https://maps.google.com/?q=Kuttippuram+Bus+Stand"),
    ("Kuttippuram Railway Station", "https://maps.google.com/?q=Kuttippuram+Railway+Station"),
    ("Changaramkulam Bus Stand", "https://maps.google.com/?q=Changaramkulam+Bus+Stand"),
    ("Changaramkulam Town", "https://maps.google.com/?q=Changaramkulam"),
    ("Guruvayoor Temple", "https://maps.google.com/?q=Guruvayoor+Temple"),
    ("Guruvayoor Railway Station", "https://maps.google.com/?q=Guruvayoor+Railway+Station"),
]


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to our Rent Car Service 🚗\n\nWhich car do you want?"
    )
    print(update.effective_user.id)
    return ASK_CAR


# Step 1: Car input
async def ask_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    car = update.message.text

    if car == "12121234":
        context.user_data["car"] = car

        keyboard = [
            [".5 day", "1 day"],
            ["1.5 day", "2 day"],
        ]

        await update.message.reply_text(
            "How many days?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )
        return ASK_DAYS

    else:
        await update.message.reply_text("Sorry, not available ❌")
        return ConversationHandler.END


# Step 2: Days selection
async def ask_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days = update.message.text

    if days == ".5 day":
        price = 1500
    elif days == "1 day":
        price = 3000
    else:
        await update.message.reply_text("Sorry, not available ❌")
        return ConversationHandler.END

    context.user_data["days"] = days
    context.user_data["price"] = price

    keyboard = [["Confirm ✅", "Cancel ❌"]]

    await update.message.reply_text(
        f"Car: {context.user_data['car']}\n"
        f"Duration: {days}\n"
        f"Amount: ₹{price}\n\n"
        "Do you want to confirm booking?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
    )

    return CONFIRM


# Step 3: Confirm booking
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text

    if "Confirm" in choice:
        car = context.user_data.get("car")
        days = context.user_data.get("days")
        price = context.user_data.get("price")

        user = update.effective_user

        # Ask for screenshot
        await update.message.reply_text(
            f"✅ Booking Confirmed!\n\n"
            f"Please pay ₹{price} to 8787898967 📱\n\n"
            f"Send payment screenshot after payment."
        )

        # Notify admin
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"🚨 New Booking Alert\n\n"
                f"User: {user.full_name}\n"
                f"Username: @{user.username}\n"
                f"User ID: {user.id}\n\n"
                f"Car: {car}\n"
                f"Duration: {days}\n"
                f"Amount: ₹{price}"
            ),
        )

        return ASK_SCREENSHOT

    else:
        await update.message.reply_text("❌ Booking cancelled.")
        return ConversationHandler.END


# Step 4: Handle screenshot
async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # If user sends ANY photo
    if update.message.photo:
        user = update.effective_user

        # Random car location
        location_name, map_link = random.choice(CAR_LOCATIONS)

        # Send final response to user
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"✅ Payment received!\n\n"
                f"🚗 Your car is ready:\n"
                f"{location_name}\n"
                f"{map_link}\n\n"
                f"📞 Contact: 8787898967\n"
                f"Drive safe 🙌"
            )
        )

        # Notify admin (optional but useful)
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"📸 Screenshot Received\n\n"
                f"User: {user.full_name}\n"
                f"@{user.username}\n"
                f"User ID: {user.id}"
            )
        )

        return ConversationHandler.END

    # If NOT photo
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📸 Please send any payment screenshot to continue."
        )
        return ASK_SCREENSHOT


# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_CAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_car)],
            ASK_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_days)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
            ASK_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_screenshot),
                MessageHandler(~filters.PHOTO, handle_screenshot),
            ],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
    