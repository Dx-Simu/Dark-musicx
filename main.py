import os
import subprocess
import threading
import asyncio
import time
import shutil
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait

# --- CONFIGURATIONS ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8538226909:AAEKBGQPJ95MTJzYtpIG1-kUltuey42rbLU"
OWNER_ID = 6703335929
DEV = "ᴅx–ᴄᴏᴅᴇx"

app = Client("host_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
web_app = Flask(__name__)

# System States
user_state = {}

# --- WEB SERVER (KEEP-ALIVE) ---
@web_app.route('/')
def home():
    return f"⚡ {DEV} ᴘᴏᴡᴇʀᴇᴅ ʜᴏsᴛɪɴɢ ɪs ᴀᴄᴛɪᴠᴇ!"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

# --- ADVANCE TERMINAL ENGINE ---
def execute_terminal(command, message):
    header = f"<b>💻 ᴛᴇʀᴍɪɴᴀʟ ʙʏ {DEV}</b>\n<code>$ {command}</code>\n"
    header += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    
    output = ""
    last_update = 0
    msg = message.reply_text("<b>⏳ ᴇxᴇᴄᴜᴛɪɴɢ...</b>")

    for line in iter(process.stdout.readline, ""):
        output += line
        if time.time() - last_update > 2:
            try:
                msg.edit_text(f"{header}<code>{output[-3500:]}</code>")
                last_update = time.time()
            except: pass
    
    process.wait()
    msg.edit_text(f"{header}<code>{output[-3500:] if output else 'No Output'}</code>\n\n✅ <b>ᴇxᴇᴄᴜᴛɪᴏɴ ᴅᴏɴᴇ!</b>")

# --- BOT COMMANDS ---

@app.on_message(filters.command("start") & filters.user(OWNER_ID))
async def start(client, message):
    text = (
        f"<b>👋 ᴡᴇʟᴄᴏᴍᴇ ᴍᴀsᴛᴇʀ, {DEV}!</b>\n\n"
        "✨ <b>sʏsᴛᴇᴍ sᴛᴀᴛᴜs:</b> ᴏɴʟɪɴᴇ\n"
        "⚡ <b>ʜᴏsᴛɪɴɢ:</b> ᴘʏᴛʜᴏɴ, ɴᴏᴅᴇᴊs, ʜᴛᴍʟ\n\n"
        "ᴄʜᴏᴏsᴇ ᴀɴ ᴀᴄᴛɪᴏɴ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ:"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐍 ᴘʏᴛʜᴏɴ", callback_data="set_python"),
         InlineKeyboardButton("🟢 ɴᴏᴅᴇ.ᴊs", callback_data="set_node")],
        [InlineKeyboardButton("🌐 ʜᴛᴍʟ ᴡᴇʙ", callback_data="set_html")],
        [InlineKeyboardButton("🛠 ᴄʀᴇᴀᴛᴇ ᴡᴏʀᴋsᴘᴀᴄᴇ", callback_data="create_folder")],
        [InlineKeyboardButton("📂 ᴍʏ ᴘʀᴏᴊᴇᴄᴛs", callback_data="view_projects")]
    ])
    await message.reply_text(text, reply_markup=buttons)

@app.on_message(filters.command("terminal") & filters.user(OWNER_ID))
async def terminal_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("✨ <b>ᴜsᴀɢᴇ:</b> <code>/terminal [command]</code>")
    cmd = message.text.split(None, 1)[1]
    threading.Thread(target=execute_terminal, args=(cmd, message)).start()

@app.on_message(filters.command("projects") & filters.user(OWNER_ID))
async def projects_cmd(client, message):
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
    if not folders:
        return await message.reply_text(f"<b>📂 ɴᴏ ᴘʀᴏᴊᴇᴄᴛs ғᴏᴜɴᴅ ɪɴ {DEV} sᴇʀᴠᴇʀ.</b>")
    
    project_list = f"<b>📂 ᴀʟʟ ᴘʀᴏᴊᴇᴄᴛs ʙʏ {DEV}:</b>\n\n"
    for folder in folders:
        files = os.listdir(folder)
        project_list += f"📁 <code>{folder}</code> ({len(files)} ғɪʟᴇs)\n"
    
    await message.reply_text(project_list)

@app.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    uid = query.from_user.id
    if uid != OWNER_ID: return

    if query.data == "view_projects":
        folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
        if not folders:
            return await query.answer("No Projects Found!", show_alert=True)
        
        text = "<b>📂 ᴄᴜʀʀᴇɴᴛ ᴡᴏʀᴋsᴘᴀᴄᴇs:</b>\n"
        for f in folders: text += f"• <code>{f}</code>\n"
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_start")]]))

    elif query.data == "back_start":
        await start(client, query.message)

    elif query.data.startswith("set_"):
        env = query.data.split("_")[1]
        user_state[uid] = {"env": env, "files": []}
        await query.message.edit_text(
            f"⚡ <b>ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ sᴇᴛ:</b> <code>{env.upper()}</code>\n"
            "ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴛᴜᴘ ғᴏʟᴅᴇʀ.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📁 ɴᴀᴍᴇ ғᴏʟᴅᴇʀ", callback_data="create_folder")]])
        )

    elif query.data == "create_folder":
        user_state[uid]['action'] = "naming"
        await query.message.reply_text("📥 <b>sᴇɴᴅ ᴀ ɴᴀᴍᴇ ғᴏʀ ʏᴏᴜʀ ᴘʀᴏᴊᴇᴄᴛ ғᴏʟᴅᴇʀ:</b>")

    elif query.data == "run_project":
        data = user_state.get(uid)
        if not data: return
        env, path = data['env'], data['path']
        
        if env == "python":
            cmd = f"pip install -r {path}/requirements.txt && python3 {path}/main.py"
        elif env == "node":
            cmd = f"cd {path} && npm install && node server.js"
        else:
            cmd = f"echo 'Static Web Hosting Active'"

        # Reuse terminal engine for deployment
        threading.Thread(target=execute_terminal, args=(cmd, query.message)).start()

@app.on_message(filters.text & filters.user(OWNER_ID))
async def handle_text(client, message):
    uid = message.from_user.id
    if uid in user_state and user_state[uid].get('action') == "naming":
        folder_name = message.text.replace(" ", "_")
        os.makedirs(folder_name, exist_ok=True)
        user_state[uid].update({"path": folder_name, "action": "uploading"})
        await message.reply_text(f"📂 <b>ᴡᴏʀᴋsᴘᴀᴄᴇ:</b> <code>{folder_name}/</code> ʀᴇᴀᴅʏ!\nsᴇɴᴅ ғɪʟᴇs ɴᴏᴡ.")

@app.on_message(filters.document & filters.user(OWNER_ID))
async def handle_docs(client, message):
    uid = message.from_user.id
    if uid in user_state and user_state[uid].get('path'):
        path = user_state[uid]['path']
        file_name = message.document.file_name
        await message.download(file_name=f"{path}/{file_name}")
        user_state[uid]['files'].append(file_name)
        
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 ʟᴀᴜɴᴄʜ ᴘʀᴏᴊᴇᴄᴛ", callback_data="run_project")]])
        await message.reply_text(f"📥 <b>ᴀᴄᴄᴇᴘᴛᴇᴅ:</b> <code>{file_name}</code>", reply_markup=btn)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    print(f"--- {DEV} sʏsᴛᴇᴍ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ---")
    app.run()
