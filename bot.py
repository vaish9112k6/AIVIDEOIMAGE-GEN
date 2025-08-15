import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

CONFIG_FILE = "config.json"

# --- Interactive setup ---
if not os.path.exists(CONFIG_FILE):
    bot_token = input("Enter your Bot Token: ").strip()
    owner_id = input("Enter your Telegram ID (Owner): ").strip()
    start_msg = input("Enter your /start message: ").strip()
    img_button = input("Text for Image button (default: Image 🖼️): ").strip() or "Image 🖼️"
    vid_button = input("Text for Video button (default: Video 🎬): ").strip() or "Video 🎬"
    config = {
        "BOT_TOKEN": bot_token,
        "OWNER_ID": owner_id,
        "START_MSG": start_msg,
        "IMG_BUTTON": img_button,
        "VID_BUTTON": vid_button
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
else:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

bot_token = config["BOT_TOKEN"]
owner_id = config["OWNER_ID"]
start_msg = config.get("START_MSG", "🤖 Welcome! Send me a prompt.")
IMG_BUTTON = config.get("IMG_BUTTON", "Image 🖼️")
VID_BUTTON = config.get("VID_BUTTON", "Video 🎬")

# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_msg)

# --- Handle user messages ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton(IMG_BUTTON, callback_data=f"image|{prompt}"),
         InlineKeyboardButton(VID_BUTTON, callback_data=f"video|{prompt}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose what to generate:", reply_markup=reply_markup)

# --- Handle button clicks ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    media_type, prompt = query.data.split("|")
    msg = await query.message.reply_text("⏳ Generating... please wait")

    try:
        api_url = f"https://api-yshzap.vercel.app/api/aiapi/aivideo?prompt={prompt}&type={media_type}"
        resp = requests.get(api_url).json()
        if resp["status"]:
            url = resp["data"]["url"]
            if media_type == "image":
                await query.message.reply_photo(photo=url, caption=f"Prompt: {prompt}")
            else:
                await query.message.reply_video(video=url, caption=f"Prompt: {prompt}")
        else:
            await query.message.reply_text("❌ Failed to generate AI content.")
    except Exception as e:
        await query.message.reply_text(f"❌ Error: {e}")
    finally:
        await msg.delete()

# --- Main ---
app = ApplicationBuilder().token(bot_token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot is running...")
app.run_polling()
