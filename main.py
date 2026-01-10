import os
import subprocess
import threading
import time
import asyncio
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, FloodWait, ChatAdminRequired, PeerIdInvalid

# --- CONFIGURATIONS ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8538226909:AAEKBGQPJ95MTJzYtpIG1-kUltuey42rbLU"
OWNER_ID = 6703335929
DEV = "ᴅx–ᴄᴏᴅᴇx"
CHANNELS = ["alphacodex369", "Termuxcodex"] 

app = Client("ultimate_terminal", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
web_app = Flask(__name__)

editing_file = {} 
user_dirs = {} 
last_warning_msg = {}

# --- RENDER KEEP-ALIVE ---
@web_app.route('/')
def home(): return f"🚀 {DEV} ᴛᴇʀᴍɪɴᴀʟ sʏsᴛᴇᴍ ɪs ᴀᴄᴛɪᴠᴇ!"

def run_web(): web_app.run(host="0.0.0.0", port=8080)

# --- FORCE JOIN CHECKER (UPGRADED) ---
async def is_subscribed(client, user_id):
    if user_id == OWNER_ID: return True
    for chat in CHANNELS:
        try:
            # Check user status in each channel
            await client.get_chat_member(chat, user_id)
        except UserNotParticipant:
            return False
        except ChatAdminRequired:
            print(f"❌ ERROR: Bot must be ADMIN in @{chat}")
            return False
        except Exception as e:
            print(f"❌ Verification Error for @{chat}: {e}")
            return False
    return True

# --- TERMINAL ENGINE ---
def execute_shell(command, message):
    uid = message.from_user.id
    if uid not in user_dirs: user_dirs[uid] = os.getcwd()
    current_path = user_dirs[uid]

    if command.startswith(("nano ", "vim ", "vi ")):
        parts = command.split(" ", 1)
        file_name = parts[1] if len(parts) > 1 else "untitled.txt"
        editing_file[uid] = {"name": file_name, "content": ""}
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("💾 sᴀᴠᴇ ғɪʟᴇ", callback_data=f"save_{uid}")]])
        message.reply_text(
            f"╭──╼ 📝 <b>ᴇᴅɪᴛɪɴɢ ᴍᴏᴅᴇ</b>\n│ 📂 <b>ғɪʟᴇ:</b> <code>{file_name}</code>\n"
            f"│ 👤 <b>ᴜsᴇʀ:</b> <a href='tg://user?id={uid}'>{message.from_user.first_name}</a>\n"
            f"╰──────────────╼\n\n✨ <i>sᴇɴᴅ ᴛᴇxᴛ ᴛᴏ ᴀᴅᴅ, ᴛʜᴇɴ ᴄʟɪᴄᴋ sᴀᴠᴇ.</i>", 
            reply_markup=btn
        )
        return

    header = (
        f"╭─ 👤 <b>ᴜsᴇʀ:</b> <a href='tg://user?id={uid}'>{message.from_user.first_name}</a>\n"
        f"├─ 📂 <b>ᴘᴀᴛʜ:</b> <code>{current_path}</code>\n"
        f"╰─ 💻 <b>ᴄᴏᴅᴇx-ᴛᴇʀᴍ:</b> <code>$ {command}</code>\n\n"
    )
    msg = message.reply_text("⏳ ᴇxᴇᴄᴜᴛɪɴɢ...")
    
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=current_path, env=os.environ.copy())
        output, last_update = "", 0
        while True:
            line = process.stdout.readline()
            if not line: break
            output += line
            if time.time() - last_update > 3.5:
                try:
                    msg.edit_text(f"{header}<code>{output[-3800:]}</code>")
                    last_update = time.time()
                except: pass
        process.wait()
        msg.edit_text(f"{header}<code>{output[-3800:] if output else 'Done.'}</code>\n\n✅ ᴇxᴇᴄᴜᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ")
    except Exception as e: msg.edit_text(f"❌ <b>ᴇʀʀᴏʀ:</b>\n<code>{str(e)}</code>")

# --- HANDLERS ---

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    text = (
        f"╭──╼ 🌟 <b>ᴄᴏᴅᴇx ᴜʟᴛɪᴍᴀᴛᴇ ᴛᴇʀᴍɪɴᴀʟ</b>\n│ 👤 <b>ᴜsᴇʀ:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
        f"│ 🆔 <b>ɪᴅ:</b> <code>{user.id}</code>\n│ ⚡ <b>sʏsᴛᴇᴍ:</b> ᴀᴄᴛɪᴠᴇ\n╰──────────────╼\n\n"
        f"🚀 <b>ᴛʜɪs ɪs ᴀ ᴘᴜʙʟɪᴄ ᴛᴇʀᴍɪɴᴀʟ ʙᴏᴛ.</b>\nᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴀᴄᴄᴇss ᴛʜᴇ sʜᴇʟʟ."
    )
    buttons = [[InlineKeyboardButton("📢 ᴀʟᴘʜᴀ ᴄᴏᴅᴇx", url=f"https://t.me/{CHANNELS[0]}"),
                InlineKeyboardButton("📢 ᴛᴇʀᴍᴜx ᴄᴏᴅᴇx", url=f"https://t.me/{CHANNELS[1]}")],
               [InlineKeyboardButton("✅ ᴠᴇʀɪғʏ ᴀɴᴅ ᴀᴄᴄᴇss", callback_data="verify_sub")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
async def cb_handler(client, query):
    uid = query.from_user.id
    if query.data == "verify_sub":
        if await is_subscribed(client, uid):
            if uid in last_warning_msg: del last_warning_msg[uid]
            await query.message.edit_text(f"╭──╼ ✅ <b>ᴀᴄᴄᴇss ɢʀᴀɴᴛᴇᴅ</b>\n│ 👤 <b>ᴜsᴇʀ:</b> <a href='tg://user?id={uid}'>{query.from_user.first_name}</a>\n╰──────────────╼\n\nᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {DEV} ᴛᴇʀᴍɪɴᴀʟ.\nʏᴏᴜ ᴄᴀɴ ɴᴏᴡ sᴇɴᴅ ᴄᴏᴍᴍᴀɴᴅs.")
        else: 
            await query.answer("❌ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ!", show_alert=True)
            
    elif query.data.startswith("save_"):
        sid = int(query.data.split("_")[1])
        if uid == sid and uid in editing_file:
            data = editing_file[uid]
            path = os.path.join(user_dirs.get(uid, os.getcwd()), data['name'])
            with open(path, 'w') as f: f.write(data['content'])
            await query.message.edit_text(f"💾 <b>ғɪʟᴇ sᴀᴠᴇᴅ:</b> <code>{data['name']}</code>"); del editing_file[uid]

@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def terminal_input(client, message):
    uid = message.from_user.id
    if not await is_subscribed(client, uid):
        if uid in last_warning_msg:
            try: await client.delete_messages(message.chat.id, last_warning_msg[uid])
            except: pass
        warn = await message.reply_text("❌ <b>ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴠᴇʀɪғʏ ᴜsɪɴɢ /start</b>")
        last_warning_msg[uid] = warn.id
        return
    if uid in editing_file:
        editing_file[uid]['content'] += message.text + "\n"
        return await message.reply_text("📍 ʟɪɴᴇ ᴀᴅᴅᴇᴅ.")
    threading.Thread(target=execute_shell, args=(message.text, message)).start()

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    app.run()
