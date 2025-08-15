import os
import json
import requests
import threading
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

CONFIG_FILE = "config.json"
REPO_URL = "https://github.com/vaish9112k6/AIVIDEOIMAGE-GEN.git"

# --- Colors ---
GREEN = "\033[1;32m"
BRIGHT_GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BLINK = "\033[5m"

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

# --- Print fancy colored header ---
def print_header():
    print(f"{GREEN}{BLINK}▚▘ ▟▛ █▬█ ▜▙ ▞▚ ▛{RESET}\n")
    print(f"{BRIGHT_GREEN}      ⚡ AI Image & Video Bot ⚡{RESET}\n")
    print(f"{CYAN}────────────────────────────────────────{RESET}\n")

# --- Interactive settings editor ---
def edit_config():
    while True:
        clear_screen()
        print_header()
        print(f"{YELLOW}[1]{RESET} Edit Bot Token        : {config.get('BOT_TOKEN')}")
        print(f"{YELLOW}[2]{RESET} Edit Owner ID         : {config.get('OWNER_ID')}")
        print(f"{YELLOW}[3]{RESET} Edit Start Message    : {config.get('START_MSG')}")
        print(f"{YELLOW}[4]{RESET} Edit Image Button     : {config.get('IMG_BUTTON')}")
        print(f"{YELLOW}[5]{RESET} Edit Video Button     : {config.get('VID_BUTTON')}")
        print(f"{YELLOW}[6]{RESET} Save & Exit")
        print(f"{YELLOW}[7]{RESET} Exit without saving")
        print(f"{CYAN}────────────────────────────────────────{RESET}")
        choice = input(f"{BRIGHT_GREEN}Enter number to edit: {RESET}").strip()

        if choice == "1":
            config["BOT_TOKEN"] = input(f"{BRIGHT_GREEN}Enter new Bot Token: {RESET}").strip()
        elif choice == "2":
            config["OWNER_ID"] = input(f"{BRIGHT_GREEN}Enter new Owner ID: {RESET}").strip()
        elif choice == "3":
            config["START_MSG"] = input(f"{BRIGHT_GREEN}Enter new Start Message: {RESET}").strip()
        elif choice == "4":
            config["IMG_BUTTON"] = input(f"{BRIGHT_GREEN}Enter new Image Button Text: {RESET}").strip()
        elif choice == "5":
            config["VID_BUTTON"] = input(f"{BRIGHT_GREEN}Enter new Video Button Text: {RESET}").strip()
        elif choice == "6":
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            print(f"{GREEN}\n✅ Config saved. Continuing...{RESET}")
            input("Press Enter to continue...")
            break
        elif choice == "7":
            print(f"{RED}\n❌ Exiting without saving.{RESET}")
            exit()
        else:
            print(f"{RED}❌ Invalid choice. Try again.{RESET}")
            input("Press Enter to continue...")

# --- Git update function ---
def update_git():
    print(f"{CYAN}\n⏳ Updating Git repository...{RESET}")
    os.system(f"git pull {REPO_URL}")
    print(f"{GREEN}✅ Git update completed. Press Enter to continue...{RESET}")
    input()

# --- Telegram bot handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(config.get("START_MSG", "🤖 Welcome! Send me a prompt."))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton(config.get("IMG_BUTTON", "Image 🖼️"), callback_data=f"image|{prompt}"),
         InlineKeyboardButton(config.get("VID_BUTTON", "Video 🎬"), callback_data=f"video|{prompt}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose what to generate:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    media_type, prompt = query.data.split("|")
    msg = await query.message.reply_text(f"{CYAN}⏳ Generating... please wait{RESET}")

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
            await query.message.reply_text(f"{RED}❌ Failed to generate AI content.{RESET}")
    except Exception as e:
        await query.message.reply_text(f"{RED}❌ Error: {e}{RESET}")
    finally:
        await msg.delete()

# --- Ask to edit settings if missing or first run ---
if not os.path.exists(CONFIG_FILE) or not config["BOT_TOKEN"] or not config["OWNER_ID"]:
    print(f"{YELLOW}⚡ First run setup or missing Bot Token/Owner ID{RESET}")
    edit_config()
else:
    edit = input(f"{BRIGHT_GREEN}Do you want to edit bot settings? (y/n): {RESET}").strip().lower()
    if edit == "y":
        edit_config()

bot_token = config["BOT_TOKEN"]

# --- Build Telegram app ---
app = ApplicationBuilder().token(bot_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

# --- Menu thread while bot runs ---
def menu_thread():
    while True:
        clear_screen()
        print_header()
        print(f"{BRIGHT_GREEN}Bot is running...\n{RESET}")
        print(f"{YELLOW}[1]{RESET} Back to Edit Settings")
        print(f"{YELLOW}[2]{RESET} Update Git Repository")
        print(f"{YELLOW}[0]{RESET} Exit")
        choice = input(f"{BRIGHT_GREEN}Choose an option: {RESET}").strip()

        if choice == "1":
            edit_config()
        elif choice == "2":
            update_git()
        elif choice == "0":
            print(f"{RED}Exiting...{RESET}")
            os._exit(0)
        else:
            print(f"{RED}❌ Invalid choice. Try again.{RESET}")
            input("Press Enter to continue...")

# --- Start menu in separate daemon thread ---
threading.Thread(target=menu_thread, daemon=True).start()

# --- Run bot in main thread ---
asyncio.run(app.run_polling())
