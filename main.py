import os
import subprocess
import threading
import time
import asyncio
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, FloodWait

# --- CONFIGURATIONS ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8538226909:AAEKBGQPJ95MTJzYtpIG1-kUltuey42rbLU"
OWNER_ID = 6703335929
DEV = "ᴅx–ᴄᴏᴅᴇx"
CHANNELS = ["alphacodex369", "Termuxcodex"] # Channel usernames without @

app = Client("ultimate_terminal", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
web_app = Flask(__name__)

# Terminal States
editing_file = {} # Store file content during nano/vim sessions

# --- RENDER KEEP-ALIVE ---
@web_app.route('/')
def home(): return f"🚀 {DEV} ᴛᴇʀᴍɪɴᴀʟ sʏsᴛᴇᴍ ɪs ᴀʟɪᴠᴇ!"

def run_web(): web_app.run(host="0.0.0.0", port=8080)

# --- FORCE JOIN CHECKER ---
async def is_subscribed(client, message):
    if message.from_user.id == OWNER_ID: return True
    for chat in CHANNELS:
        try:
            await client.get_chat_member(chat, message.from_user.id)
        except UserNotParticipant:
            return False
    return True

# --- TERMINAL ENGINE ---
def execute_shell(command, message):
    # Nano/Vim Simulation
    if command.startswith(("nano ", "vim ", "vi ")):
        file_name = command.split(" ", 1)[1]
        editing_file[message.from_user.id] = {"name": file_name, "content": ""}
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("💾 sᴀᴠᴇ ғɪʟᴇ", callback_data=f"save_{message.from_user.id}")]])
        message.reply_text(f"📝 ᴇᴅɪᴛɪɴɢ: <code>{file_name}</code>\n\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ɴᴏᴡ.", reply_markup=btn)
        return

    # Real-time Execution
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    header = f"╭─ 👤 <b>ᴜsᴇʀ:</b> <code>{message.from_user.first_name}</code>\n╰─ 💻 <b>ᴄᴏᴅᴇx-ᴛᴇʀᴍ:</b> <code>$ {command}</code>\n\n"
    
    msg = message.reply_text("⏳ ᴘʀᴏᴄᴇssɪɴɢ...")
    output = ""
    last_update = 0

    for line in iter(process.stdout.readline, ""):
        output += line
        if time.time() - last_update > 2.5:
            try:
                msg.edit_text(f"{header}<code>{output[-3800:]}</code>")
                last_update = time.time()
            except: pass
            
    process.wait()
    final_output = output if output else "No output / Process finished."
    try:
        msg.edit_text(f"{header}<code>{final_output[-3800:]}</code>\n\n✅ ᴇxᴇᴄᴜᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ")
    except: pass

# --- HANDLERS ---

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    text = (
        f"╭──╼ <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴄᴏᴅᴇx ᴛᴇʀᴍ</b>\n"
        f"│ 👤 <b>ᴜsᴇʀ:</b> <code>{user.first_name}</code>\n"
        f"│ ⚡ <b>sᴛᴀᴛᴜs:</b> ᴀᴄᴛɪᴠᴇ\n"
        f"╰──────────────╼\n\n"
        f"✨ <i>ᴘʟᴇᴀsᴇ sᴜʙsᴄʀɪʙᴇ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴜsᴇ ᴛʜɪs ᴛᴇʀᴍɪɴᴀʟ.</i>"
    )
    buttons = [
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 1", url=f"https://t.me/{CHANNELS[0]}")],
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 2", url=f"https://t.me/{CHANNELS[1]}")],
        [InlineKeyboardButton("✅ ᴠᴇʀɪғʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ", callback_data="verify_sub")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
async def cb_handler(client, query):
    if query.data == "verify_sub":
        if await is_subscribed(client, query.message):
            await query.message.edit_text(f"✅ <b>ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟ!</b>\n\nᴍᴀsᴛᴇʀ {DEV}, ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ sᴇɴᴅ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴅɪʀᴇᴄᴛʟʏ.")
        else:
            await query.answer("❌ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴄʜᴀɴɴᴇʟs!", show_alert=True)
            
    elif query.data.startswith("save_"):
        uid = int(query.data.split("_")[1])
        if uid in editing_file:
            data = editing_file[uid]
            with open(data['name'], 'w') as f:
                f.write(data['content'])
            await query.message.edit_text(f"💾 <b>ғɪʟᴇ sᴀᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ:</b> <code>{data['name']}</code>")
            del editing_file[uid]

@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def terminal_input(client, message):
    # Check if owner or verified
    if not await is_subscribed(client, message):
        return await message.reply_text("❌ ᴘʟᴇᴀsᴇ ᴠᴇʀɪғʏ ғɪʀsᴛ ᴜsɪɴɢ /start")

    uid = message.from_user.id
    # If user is in Nano/Vim mode
    if uid in editing_file:
        editing_file[uid]['content'] += message.text + "\n"
        return await message.reply_text("📍 ᴄᴏɴᴛᴇɴᴛ ᴀᴅᴅᴇᴅ. sᴇɴᴅ ᴍᴏʀᴇ ᴏʀ ᴄʟɪᴄᴋ sᴀᴠᴇ.")

    # Direct Terminal Execution
    cmd = message.text
    threading.Thread(target=execute_shell, args=(cmd, message)).start()

# --- RUN BOT ---
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    print(f"--- {DEV} ᴛᴇʀᴍɪɴᴀʟ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ ---")
    app.run()
