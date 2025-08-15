import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext

# --- Ask for Bot Token and Owner ID if not saved ---
if not os.path.exists("config.json"):
    bot_token = input("Enter your Bot Token: ").strip()
    owner_id = input("Enter your Telegram ID (Owner): ").strip()
    with open("config.json", "w") as f:
        json.dump({"BOT_TOKEN": bot_token, "OWNER_ID": owner_id}, f)
else:
    with open("config.json", "r") as f:
        config = json.load(f)
        bot_token = config["BOT_TOKEN"]
        owner_id = config["OWNER_ID"]

# --- /start command ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 Welcome! Send me any prompt and I will generate an AI Image or Video."
    )

# --- Handle user messages ---
def handle_message(update: Update, context: CallbackContext):
    prompt = update.message.text.strip()
    keyboard = [
        [
            InlineKeyboardButton("Image 🖼️", callback_data=f"image|{prompt}"),
            InlineKeyboardButton("Video 🎬", callback_data=f"video|{prompt}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose what to generate:", reply_markup=reply_markup)

# --- Handle button clicks ---
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    media_type, prompt = query.data.split("|")
    msg = query.message.reply_text("⏳ Generating... please wait")

    try:
        api_url = f"https://api-yshzap.vercel.app/api/aiapi/aivideo?prompt={prompt}&type={media_type}"
        resp = requests.get(api_url).json()
        if resp["status"]:
            url = resp["data"]["url"]
            if media_type == "image":
                query.message.reply_photo(photo=url, caption=f"Prompt: {prompt}")
            else:
                query.message.reply_video(video=url, caption=f"Prompt: {prompt}")
        else:
            query.message.reply_text("❌ Failed to generate AI content.")
    except Exception as e:
        query.message.reply_text(f"❌ Error: {e}")
    finally:
        msg.delete()

# --- Main ---
updater = Updater(bot_token)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dp.add_handler(CallbackQueryHandler(button_handler))

print("Bot is running...")
updater.start_polling()
updater.idle()
