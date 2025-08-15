import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

CONFIG_FILE = "config.json"

# --- Load or create config ---
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {
        "BOT_TOKEN": "",
        "OWNER_ID": "",
        "START_MSG": "🤖 Welcome! Send me a prompt.",
        "IMG_BUTTON": "Image 🖼️",
        "VID_BUTTON": "Video 🎬"
    }

# --- Interactive menu to edit settings ---
def edit_config():
    while True:
        print("\n--- BOT SETTINGS EDITOR ---")
        print(f"1. Bot Token        : {config.get('BOT_TOKEN')}")
        print(f"2. Owner ID         : {config.get('OWNER_ID')}")
        print(f"3. Start Message    : {config.get('START_MSG')}")
        print(f"4. Image Button     : {config.get('IMG_BUTTON')}")
        print(f"5. Video Button     : {config.get('VID_BUTTON')}")
        print("6. Save & Exit")
        print("7. Exit without saving")

        choice = input("\nEnter number to edit (or 6 to save & continue): ").strip()

        if choice == "1":
            config["BOT_TOKEN"] = input("Enter new Bot Token: ").strip()
        elif choice == "2":
            config["OWNER_ID"] = input("Enter new Owner ID: ").strip()
        elif choice == "3":
            config["START_MSG"] = input("Enter new Start Message: ").strip()
        elif choice == "4":
            config["IMG_BUTTON"] = input("Enter new Image Button Text: ").strip()
        elif choice == "5":
            config["VID_BUTTON"] = input("Enter new Video Button Text: ").strip()
        elif choice == "6":
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            print("✅ Config saved. Continuing...")
            break
        elif choice == "7":
            print("❌ Exiting without saving.")
            exit()
        else:
            print("❌ Invalid choice. Try again.")

# --- Ask to edit settings on first run or empty fields ---
if not config["BOT_TOKEN"] or not config["OWNER_ID"]:
    print("⚡ First run setup or missing Bot Token/Owner ID")
    edit_config()
else:
    edit = input("Do you want to edit bot settings? (y/n): ").strip().lower()
    if edit == "y":
        edit_config()

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
