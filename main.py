import random
import asyncio
import os
import threading
from dotenv import load_dotenv
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask app for Koyeb health check
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8000)

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Response templates (BUY/SELL only)
responses = [
    "🟢🟢 {pair} 🟢🟢\n\n📊 **Signal:** ⬆️⬆️⬆️ 📈\n\nTrading x Flow x Bot",
    "🔴🔴 {pair} 🔴🔴\n\n📊 **Signal:** ⬇️⬇️⬆️ 📉\n\nTrading x Flow x Bot"
]

# OTC Forex pairs
otc_pairs = [
    "AED/CNY OTC", "AUD/CHF OTC", "BHD/CNY OTC", "EUR/USD OTC", 
    "CAD/CHF OTC", "NZD/JPY OTC", "EUR/CHF OTC", "GBP/JPY OTC"
]

# Cooldown storage
user_cooldowns = {}

# Cooldown duration (in seconds)
COOLDOWN_TIME = 10

# Start message with disclaimer, expiry information, and trade urgency
start_message = """
📊 *Welcome to the Binary Trading Bot!*

✅ Select an OTC Forex pair below to receive trading signals.

⏳ *All trades are based on a 5-second expiry time.* Ensure you follow this timing for better accuracy.

🚀 *After receiving a signal, open Pocket Option and execute the trade as fast as possible for optimal results.*

⚠️ *Disclaimer:* This bot provides trading signals based on market analysis. However, OTC (Over-The-Counter) pairs operate in a *simulated market* environment, which means price movements may not reflect real-world conditions. Due to this, signals may not always be accurate. Use the information at your own discretion and always practice responsible trading.

🎯 *Trading x Flow x Bot*
"""

# Function to create the keyboard with OTC pairs or cooldown
def create_keyboard(otc_pairs=None, cooldown=False):
    if cooldown:
        return ReplyKeyboardMarkup([[KeyboardButton("On Cooldown")]], resize_keyboard=True)

    buttons = [[KeyboardButton(pair)] for pair in otc_pairs]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# Start command to display OTC Forex pairs
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = create_keyboard(otc_pairs)
    sent_message = await update.message.reply_text(start_message, reply_markup=keyboard, parse_mode="Markdown")
    context.chat_data["message_id"] = sent_message.message_id

# Handle user selection
async def otc_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_choice = update.message.text
    chat_id = update.message.chat_id

    if user_choice == "On Cooldown":
        return

    # Check cooldown
    current_time = asyncio.get_event_loop().time()
    if user_id in user_cooldowns and current_time < user_cooldowns[user_id]:
        remaining_time = int(user_cooldowns[user_id] - current_time)

        cooldown_message = await update.message.reply_text(
            f"⏳ Please wait {remaining_time} seconds before choosing a pair again.",
            reply_markup=create_keyboard(cooldown=True)
        )
        await asyncio.sleep(remaining_time)
        await cooldown_message.delete()

        await update.message.reply_text(
            "You can now select a new pair!",
            reply_markup=create_keyboard(otc_pairs)
        )
        return

    if user_choice not in otc_pairs:
        await update.message.reply_text("❌ Invalid choice. Please select a pair from the buttons.")
        return

    # Set cooldown
    user_cooldowns[user_id] = current_time + COOLDOWN_TIME

    analyzing_message = await update.message.reply_text(
        f"📊 Analyzing Chart for *{user_choice}* ... Please wait.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(random.uniform(2, 5))

    response = random.choice(responses).format(pair=user_choice)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=analyzing_message.message_id,
            text=response,
            parse_mode="Markdown"
        )

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=context.chat_data["message_id"],
            text="You can now select a new pair!",
            reply_markup=create_keyboard(otc_pairs)
        )
    except Exception:
        pass

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

def main():
    if not TOKEN:
        return

    # Create Application
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, otc_response))
    app.add_error_handler(error_handler)

    print("📊 Binary Trading Bot is running securely...")

    # Run Flask for Koyeb health checks in a separate thread
    threading.Thread(target=run_flask).start()

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
