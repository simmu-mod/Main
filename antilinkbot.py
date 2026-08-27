import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Flask Server for Render Uptime (Anti-Sleep)
app_web = Flask('')

@app_web.route('/')
def home():
    return "Anti-Link Bot is alive and running!"

@app_web.route('/register')
def register():
    return "OK", 200

def run_web():
    app_web.run(host='0.0.0.0', port=10000)

TOKEN = "8921783814:AAHx6Z4gWzp0yXtmfSZLOPYNrtkb9BDCUQA"  # BotFather se liya gaya naya token yahan dalein
ADMIN_ID = 8921783814  # Apni Telegram User ID yahan dalein

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ *Anti-Link Bot Activated!*\n\nAdd me as an admin in your group/channel with 'Delete Messages' permission, and I will block all links automatically.")

# Anti-Link Handler
async def check_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    
    chat = update.effective_chat
    user = update.effective_user

    # Agar private chat hai toh links delete nahi honge (sirf Group/Channel ke liye)
    if chat.type == "private":
        return

    # Check karein ki user group ka Admin toh nahi hai (Admins ko links bhejne ki chut mil sakti hai)
    try:
        member = await chat.get_member(user.id)
        if member.status in ["administrator", "creator"]:
            return  # Admin ke links delete nahi honge
    except Exception:
        pass

    # Link detect karne ka pattern (HTTP, HTTPS, www, ya Telegram links jaise t.me)
    link_pattern = r"(https?://\S+|www\.\S+|t\.me/\S+)"

    if re.search(link_pattern, message.text):
        try:
            # Link milte hi message delete kar do
            await message.delete()
            
            # Optional: Warning message bhejna (agar nahi bhejna ho toh yeh line hata sakte hain)
            warn_msg = await chat.send_message(f"⚠️ Hey {user.mention_html()}, links are not allowed here!", parse_mode="HTML")
            
            # 5 second baad warning message bhi apne aap gayab ho jaye
            import asyncio
            await asyncio.sleep(5)
            await warn_msg.delete()
        except Exception as e:
            print(f"Failed to delete link: {e}")

def main():
    # Flask server background thread start karein
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    
    # Text messages ko monitor karne ke liye handler (Commands ko chhod kar)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_links))
    
    print("🛡️ Anti-Link Bot Started!")
    app.run_polling()

if __name__ == "__main__":
    main()
    