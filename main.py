import asyncio
import os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from flask import Flask
from threading import Thread

# --- RENDER ALIVE SYSTEM ---
web = Flask('')
@web.route('/')
def home():
    return "ᴀᴅᴅ-ᴏɴ: ʙᴏᴛ ɪs ʀᴜɴɴɪɴɢ"

def run_web():
    web.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "7853734473:AAHdGjbtPFWD6wFlyu8KRWteRg_961WGRJk"
B_NAME = "ᴅx ᴍᴜsɪᴄ"
OWNER_ID = 6703335929

app = Client("DxMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- DESIGN BORDERS ---
B_TOP = "╔═══════════════════════╗"
B_MID = "╟───────────────────────╢"
B_BOT = "╚═══════════════════════╝"

# --- BUTTONS ---
def play_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏮ ᴘʀᴇᴠ", callback_data="prev"),
            InlineKeyboardButton("⏸ ᴘᴀᴜsᴇ", callback_data="pause"),
            InlineKeyboardButton("▶️ ʀᴇsᴜᴍᴇ", callback_data="resume"),
            InlineKeyboardButton("⏭ sᴋɪᴘ", callback_data="skip")
        ],
        [
            InlineKeyboardButton("⏹ sᴛᴏᴘ", callback_data="stop"),
            InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴀᴅᴅ-ᴏɴ", callback_data="close")
        ]
    ])

# --- ANIMATION ENGINE ---
async def start_animation(m: Message):
    frames = [
        "🔍 ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ.", "🔍 ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ..", "🔍 ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ...",
        "📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ.", "📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ..", "📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...",
        "🎙 ᴀᴅᴅɪɴɢ ᴛᴏ ᴠᴄ.", "🎙 ᴀᴅᴅɪɴɢ ᴛᴏ ᴠᴄ..", "✨ ᴀʟᴍᴏsᴛ ᴅᴏɴᴇ!"
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
        return await message.reply_text("<b>❌ ᴀᴅᴅ ᴀ sᴏɴɢ ɴᴀᴍᴇ!</b>")

    m = await message.reply_text(f"<code>{B_TOP}</code>\n<code>ᴘʀᴏᴄᴇssɪɴɢ...</code>\n<code>{B_BOT}</code>")
    await start_animation(m)
    
    # Final Design Message
    caption = (
        f"<code>{B_TOP}</code>\n"
        f"🎧 <b>ɴᴏᴡ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠᴄ</b>\n"
        f"<code>{B_MID}</code>\n"
        f"<b>📌 ᴛɪᴛʟᴇ:</b> <code>{query.title()}</code>\n"
        f"<b>👤 ᴀᴅᴅᴇᴅ ʙʏ:</b> {message.from_user.mention}\n"
        f"<b>⏱️ ᴅᴜʀᴀᴛɪᴏɴ:</b> <code>𝟶𝟹:𝟺𝟻 ᴍɪɴs</code>\n\n"
        f"<code>01:25 ━━━🔘──────── 03:45</code>\n"
        f"<code>{B_MID}</code>\n"
        f"<blockquote>✨ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴅx ɴᴇᴛᴡᴏʀᴋ</blockquote>\n"
        f"<code>{B_BOT}</code>"
    )
    
    await m.delete()
    await message.reply_photo(
        photo="https://graph.org/file/c8f2588e360e2003c2718.jpg", 
        caption=caption,
        reply_markup=play_markup()
    )

# --- STARTUP ---
if __name__ == "__main__":
    Thread(target=run_web).start() # Starts Flask in background
    print("✅ ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ ᴏɴ ʀᴇɴᴅᴇʀ...")
    app.run()
