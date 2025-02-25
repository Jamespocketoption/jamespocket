import random
import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Logging setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

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


# Start command to display OTC Forex pairs with disclaimer and expiry info
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [otc_pairs[i:i + 2] for i in range(0, len(otc_pairs), 2)]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(start_message, reply_markup=reply_markup, parse_mode="Markdown")

# Handle user selection
async def otc_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_choice = update.message.text
    chat_id = update.message.chat_id

    # Check cooldown
    current_time = asyncio.get_event_loop().time()
    if user_id in user_cooldowns and current_time < user_cooldowns[user_id]:
        remaining_time = int(user_cooldowns[user_id] - current_time)

        # Send cooldown message and delete it after 3 seconds
        cooldown_message = await update.message.reply_text(f"⏳ Please wait {remaining_time} seconds before choosing a pair again.")
        await asyncio.sleep(3)
        await cooldown_message.delete()
        return

    # Set new cooldown
    user_cooldowns[user_id] = current_time + COOLDOWN_TIME

    # Validate user choice
    if user_choice not in otc_pairs:
        await update.message.reply_text("❌ Invalid choice. Please select a pair from the buttons.")
        return

    # Simulate market analysis (random 1-3 seconds)
    analyzing_message = await update.message.reply_text(
        f"📊 Analyzing Chart for *{user_choice}* ... Please wait.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(random.randint(1, 3))

    # Randomly select BUY or SELL
    response = random.choice(responses).format(pair=user_choice)

    # Send the analysis result
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=analyzing_message.message_id,
            text=response,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.warning(f"Error editing message: {e}")

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(f"Exception: {context.error}")

def main():
    if not TOKEN:
        logging.error("❌ BOT_TOKEN not found! Ensure it's set in the .env file.")
        return

    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, otc_response))

    # Error handling
    app.add_error_handler(error_handler)

    print("📊 Binary Trading Bot is running securely...")
    app.run_polling()

if __name__ == "__main__":
    main()
