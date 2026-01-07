import asyncio
import time
import os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from flask import Flask
from threading import Thread

# --- RENDER PORT BINDING (Fixes R10 Error) ---
web = Flask('')
@web.route('/')
def home():
    return "ʙᴏᴛ ɪs ᴀʟɪᴠᴇ!"

def run_web():
    web.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "7853734473:AAHdGjbtPFWD6wFlyu8KRWteRg_961WGRJk"
B_NAME = "ᴅx—ᴍᴜsɪᴄ"
OWNER_ID = 6703335929
BOT_USERNAME = "@Dark_x7272bot"

app = Client("DxMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- PREMIUM DESIGN ELEMENTS ---
B_TOP = "╔═══════════════════════╗"
B_MID = "╟───────────────────────╢"
B_BOT = "╚═══════════════════════╝"

# --- KEYBOARDS ---
def play_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏮", callback_data="prev"),
            InlineKeyboardButton("⏸", callback_data="pause"),
            InlineKeyboardButton("▶️", callback_data="resume"),
            InlineKeyboardButton("⏭", callback_data="skip")
        ],
        [
            InlineKeyboardButton("⏹ sᴛᴏᴘ", callback_data="stop"),
            InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="close")
        ]
    ])

# --- ADVANCED ANIMATION LOGIC ---
async def play_animation(m: Message, query: str):
    frames = [
        "🔍 ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ.",
        "🔍 ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ..",
        "🔍 ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ...",
        "📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ.",
        "📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ..",
        "📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ...",
        "🎙 ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴠᴄ.",
        "🎙 ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴠᴄ..",
        "🎙 ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴠᴄ...",
        "✨ ᴀʟᴍᴏsᴛ ᴅᴏɴᴇ..."
    ]
    for frame in frames:
        try:
            await m.edit_text(f"<code>{B_TOP}</code>\n<code>{frame}</code>\n<code>{B_BOT}</code>")
            await asyncio.sleep(0.4)
        except:
            break

# --- COMMANDS ---

@app.on_message(filters.command("play"))
async def play_cmd(_, message: Message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("<b>❌ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ!</b>")

    # Start Animation
    m = await message.reply_text(f"<code>{B_TOP}</code>\n<code>🔍 ᴀᴅᴅɪɴɢ...</code>\n<code>{B_BOT}</code>")
    await play_animation(m, query)
    
    # Final Ultra Design
    caption = (
        f"<code>{B_TOP}</code>\n"
        f"🎧 <b>ɴᴏᴡ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠᴄ</b>\n"
        f"<code>{B_MID}</code>\n"
        f"<b>📌 ᴛɪᴛʟᴇ:</b> <code>{query.title()}</code>\n"
        f"<b>👤 ᴀᴅᴅᴇᴅ ʙʏ:</b> {message.from_user.mention}\n"
        f"<b>⏱️ ᴅᴜʀᴀᴛɪᴏɴ:</b> <code>𝟶𝟹:𝟺𝟻 ᴍɪɴs</code>\n\n"
        f"<code>01:25 ━━━🔘──────── 03:45</code>\n"
        f"<code>{B_MID}</code>\n"
        f"<blockquote>ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴅx ɴᴇᴛᴡᴏʀᴋ</blockquote>\n"
        f"<code>{B_BOT}</code>"
    )
    
    await m.delete()
    await message.reply_photo(
        photo="https://graph.org/file/c8f2588e360e2003c2718.jpg", 
        caption=caption,
        reply_markup=play_markup()
    )

# --- RUN BOT & WEB SERVER ---
if __name__ == "__main__":
    print("🚀 Starting Web Server for Render...")
    Thread(target=run_web).start()
    print("✅ DX Music Bot is starting...")
    app.run()
