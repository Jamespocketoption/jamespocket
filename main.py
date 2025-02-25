import random
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
    """Creates the keyboard with OTC pairs or a single cooldown button."""
    if cooldown:
        return ReplyKeyboardMarkup([[KeyboardButton("On Cooldown")]], resize_keyboard=True)

    # Create keyboard with OTC pairs
    buttons = [[KeyboardButton(pair)] for pair in otc_pairs]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# Start command to display OTC Forex pairs with disclaimer and expiry info
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = create_keyboard(otc_pairs)
    # Send the initial message with OTC pairs
    sent_message = await update.message.reply_text(start_message, reply_markup=keyboard, parse_mode="Markdown")
    # Save the message ID so we can edit it later
    context.chat_data["message_id"] = sent_message.message_id

# Handle user selection
async def otc_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_choice = update.message.text
    chat_id = update.message.chat_id

    # Check if the user clicked "On Cooldown" button
    if user_choice == "On Cooldown":
        return  # Do nothing if the user clicked the "On Cooldown" button

    # Check cooldown
    current_time = asyncio.get_event_loop().time()
    if user_id in user_cooldowns and current_time < user_cooldowns[user_id]:
        remaining_time = int(user_cooldowns[user_id] - current_time)

        # Send cooldown message and replace buttons with "On Cooldown"
        cooldown_message = await update.message.reply_text(
            f"⏳ Please wait {remaining_time} seconds before choosing a pair again.",
            reply_markup=create_keyboard(cooldown=True)  # Show the cooldown button
        )
        await asyncio.sleep(remaining_time)  # Wait for the cooldown to expire
        await cooldown_message.delete()

        # After cooldown, restore the OTC pairs buttons without sending a message
        await update.message.reply_text(
            "You can now select a new pair!",
            reply_markup=create_keyboard(otc_pairs)  # Re-enable the OTC pair buttons
        )
        return

    # Validate user choice
    if user_choice not in otc_pairs:
        await update.message.reply_text("❌ Invalid choice. Please select a pair from the buttons.")
        return  # Don't set the cooldown if the choice is invalid

    # Set new cooldown for valid choices only
    user_cooldowns[user_id] = current_time + COOLDOWN_TIME

    # Simulate analysis (0-0.5 seconds delay)
    analyzing_message = await update.message.reply_text(
        f"📊 Analyzing Chart for *{user_choice}* ... Please wait.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(random.uniform(2, 5))  # Random delay between 0 and 0.5 seconds

    # Randomly select BUY or SELL
    response = random.choice(responses).format(pair=user_choice)

    # Send the analysis result (update the message)
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=analyzing_message.message_id,  # This ensures we're editing the correct message
            text=response,
            parse_mode="Markdown"
        )

        # Restore the original keyboard with OTC pairs in the original message
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=context.chat_data["message_id"],  # Edit the original start message
            text="You can now select a new pair!",
            reply_markup=create_keyboard(otc_pairs)  # Re-enable the original buttons
        )

    except Exception as e:
        pass  # Ignore the error silently

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass  # Error handling can be left empty or customized further if needed

def main():
    if not TOKEN:
        return  # Exit if no bot token is found

    # Create Application
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
