import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

CONFIG_FILE = "config.json"
REPO_URL = "https://github.com/vaish9112k6/AIVIDEOIMAGE-GEN.git"

# --- Load config or create default ---
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

# --- Clear screen ---
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

# --- Print fancy header ---
def print_header():
    print("▚▘ ▟▛ █▬█ ▜▙ ▞▚ ▛\n")
    print("      ⚡ AI Image & Video Bot ⚡\n")
    print("────────────────────────────────────────\n")

# --- Interactive settings editor ---
def edit_config():
    while True:
        clear_screen()
        print_header()
        print("[1] Edit Bot Token        : {}".format(config.get("BOT_TOKEN")))
        print("[2] Edit Owner ID         : {}".format(config.get("OWNER_ID")))
        print("[3] Edit Start Message    : {}".format(config.get("START_MSG")))
        print("[4] Edit Image Button     : {}".format(config.get("IMG_BUTTON")))
        print("[5] Edit Video Button     : {}".format(config.get("VID_BUTTON")))
        print("[6] Save & Exit")
        print("[7] Exit without saving")
        print("────────────────────────────────────────")
        choice = input("Enter number to edit: ").strip()

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
            print("\n✅ Config saved. Continuing...")
            break
        elif choice == "7":
            print("\n❌ Exiting without saving.")
            exit()
        else:
            print("❌ Invalid choice. Try again.")

# --- Git update function ---
def update_git():
    print("\n⏳ Updating Git repository...")
    os.system(f"git pull {REPO_URL}")
    print("✅ Git update completed. Press Enter to continue...")
    input()

# --- Post-header menu before starting bot ---
def pre_start_menu():
    while True:
        clear_screen()
        print_header()
        print("Bot is starting...\n")
        print("[1] Back to Edit Settings")
        print("[2] Update Git Repository")
        print("[3] Start Bot")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            edit_config()
        elif choice == "2":
            update_git()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice. Try again.")

# --- Ask to edit settings if missing or first run ---
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

# --- Pre-start menu ---
pre_start_menu()

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

# --- Main bot ---
app = ApplicationBuilder().token(bot_token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

clear_screen()
print_header()
print("Bot is running...\n")
app.run_polling()
