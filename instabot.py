# =========================================
#     THE RION NETWORK - INSTAGRAM BOT
#     CREATOR: DEMON | DRAGON v1.0
# =========================================

import re
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# =========================================
#              CONFIGURATION
# =========================================

TOKEN = "8801358661:AAG5jgAhSIjxSpNNfidnqGjCyfy5ILvlxkM"  # CHANGE THIS
ADMIN_ID = 8801358661  # CHANGE THIS (Your Telegram User ID)
BRAND = "𝐈𝐍𝐒𝐓𝐀 𝐕𝐄𝐃𝐈𝐎 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐄𝐑"
API_URL = "https://tele-social.vercel.app/down?url="

# Cooldown in seconds
COOLDOWN_SECONDS = 20

# Store user last request time
user_cooldown = {}

# =========================================
#              BROADCAST SYSTEM
# =========================================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /broadcast message"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("Usage: /broadcast Hello everyone!")
        return
    
    # Get all chat IDs from context.bot_data
    chats = context.bot_data.get("chats", set())
    if not chats:
        await update.message.reply_text("No chats to broadcast!")
        return
    
    sent = 0
    failed = 0
    
    await update.message.reply_text(f"📢 Broadcasting to {len(chats)} users...")
    
    for chat_id in chats:
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"📢 *{BRAND} Announcement*\n\n{msg}", parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.05)  # avoid flood wait
        except:
            failed += 1
    
    await update.message.reply_text(f"✅ Sent: {sent}\n❌ Failed: {failed}")

async def broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /broadcast_photo - reply to a photo"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Reply to a photo with /broadcast_photo caption")
        return
    
    caption = " ".join(context.args) if context.args else f"📢 *{BRAND} Announcement*"
    photo = update.message.reply_to_message.photo[-1].file_id
    
    chats = context.bot_data.get("chats", set())
    sent = 0
    failed = 0
    
    await update.message.reply_text(f"📸 Broadcasting photo to {len(chats)} users...")
    
    for chat_id in chats:
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    
    await update.message.reply_text(f"✅ Sent: {sent}\n❌ Failed: {failed}")

# =========================================
#                 START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Store chat for broadcast
    if "chats" not in context.bot_data:
        context.bot_data["chats"] = set()
    context.bot_data["chats"].add(chat_id)
    
    banner = f"""
🔥 *{BRAND}* 🔥

📥 *INSTAGRAM DOWNLOADER BOT* 📥

✅ 24/7 Active
✅ Fast Download  
✅ Reel Support
✅ Post Support
✅ Free to Use

*How to use?*
Simply send me any Instagram Reel or Post link!

⚡ *Powered by YadavXModer*
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎈 Example Link 🎈", url="https://www.instagram.com/reel/DVNiiqbiU1J/?igsi=YmhkeTZucHZ3Y3V6")],
        [InlineKeyboardButton("🔓 Join Channel 🔓", url="https://t.me/+Mm6JRg0esm5lM2Nl")]
    ])
    
    await update.message.reply_text(banner, parse_mode="Markdown", reply_markup=keyboard)

# =========================================
#           INSTAGRAM DOWNLOADER
# =========================================

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Store chat for broadcast
    if "chats" not in context.bot_data:
        context.bot_data["chats"] = set()
    context.bot_data["chats"].add(chat_id)
    
    text = update.message.text.strip()
    
    # Instagram link pattern
    pattern = r"(https?:\/\/)?(www\.)?instagram\.com\/(p|reel|tv)\/[A-Za-z0-9\-_]+"
    
    if not re.search(pattern, text):
        await update.message.reply_text("❌ Please send a valid Instagram Reel or Post link!")
        return
    
    # Cooldown check
    now = time.time()
    last = user_cooldown.get(chat_id, 0)
    
    if now - last < COOLDOWN_SECONDS:
        left = int(COOLDOWN_SECONDS - (now - last))
        await update.message.reply_text(f"⏳ Wait {left} seconds before next download!")
        return
    
    user_cooldown[chat_id] = now
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Send wait message
    wait_msg = await update.message.reply_text("⏳ *Downloading...*", parse_mode="Markdown")
    
    try:
        # Call API
        encoded_url = requests.utils.quote(text, safe='')
        response = requests.get(API_URL + encoded_url, timeout=30)
        
        if response.status_code != 200:
            raise Exception("API request failed")
        
        data = response.json()
        
        if not data or data.get("status") != True:
            raise Exception("Invalid link or API error")
        
        payload = data.get("data", {})
        media_type = payload.get("type")
        media_data = payload.get("media", {})
        
        caption = f"✅ *Downloaded Successfully*\n\n⚡ *Powered by {BRAND}*"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔓 Join Channel 🔓", url="https://t.me/+Mm6JRg0esm5lM2Nl")]
        ])
        
        if media_type == "video":
            video_url = media_data.get("video")
            if not video_url:
                raise Exception("Video URL not found")
            
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        
        elif media_type == "image":
            image_url = media_data.get("image")
            if not image_url:
                raise Exception("Image URL not found")
            
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        
        else:
            raise Exception("Unsupported media type")
        
        # Delete wait message
        await wait_msg.delete()
        
        # Try to delete user message (optional)
        try:
            await update.message.delete()
        except:
            pass
    
    except Exception as e:
        await wait_msg.edit_text(f"❌ *Error:* Failed to download!\n\nTry another link.", parse_mode="Markdown")

# =========================================
#                 STATS
# =========================================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Authorized personnel only!")
        return
    
    chats = len(context.bot_data.get("chats", set()))
    await update.message.reply_text(f"📊 *{BRAND} Stats*\n\n👥 Total Users: {chats}", parse_mode="Markdown")

# =========================================
#                  MAIN
# =========================================

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("broadcast_photo", broadcast_photo))
    app.add_handler(CommandHandler("stats", stats))
    
    # Message handler for Instagram links
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))
    
    print(f"🔥 {BRAND} - Instagram Downloader Bot Started!")
    print("⚡ Powered by @YadavXModer v1.0")
    
    app.run_polling()

if __name__ == "__main__":
    main()