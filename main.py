import asyncio
import random
import os
import re
import requests
import yt_dlp
from io import BytesIO
from threading import Thread
from flask import Flask
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ParseMode

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8538226909:AAEKBGQPJ95MTJzYtpIG1-kUltuey42rbLU"
OWNER_ID = 6703335929 
MONGO_URL = "mongodb+srv://shadowur6_db_user:8AIIxZUjpanaQBjh@dx-codex.fmqcovu.mongodb.net/?retryWrites=true&w=majority&appName=Dx-codex"

# --- DATABASE SETUP ---
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.DxFinalDB
users_db = db.users
settings_db = db.settings
warns_db = db.warns
badwords_db = db.badwords

app = Client("Dx-Final-Bot", API_ID, API_HASH, bot_token=BOT_TOKEN)

# --- UI ELEMENTS (SMALL CAPS FONT) ---
B = "╼━━━━━━╾"
S = "➲"
DEV = "ᴅx–ᴄᴏᴅᴇx"

# --- RENDER SELF-KEEP ACTIVE ---
web = Flask('')
@web.route('/')
def home(): return f"{DEV} ғɪɴᴀʟ ʙᴏᴛ"
def run_web(): web.run(host='0.0.0.0', port=8080)

async def auto_ping():
    while True:
        try: requests.get("http://localhost:8080")
        except: pass
        await asyncio.sleep(180)

# --- HELPERS ---
async def is_admin(chat_id, user_id):
    if user_id == OWNER_ID: return True
    try:
        m = await app.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

# --- 1. SERVICE MESSAGE CLEANER ---
@app.on_message(filters.service)
async def service_cleaner(client, message: Message):
    try: await message.delete()
    except: pass

# --- 2. START & PRIVATE WELCOME ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await users_db.update_one({"user_id": message.from_user.id}, {"$set": {"user_id": message.from_user.id}}, upsert=True)
    text = (f"<b>╭{B}╮</b>\n"
            f"  <b>✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {DEV} ✨</b>\n"
            f"<b>╰{B}╯</b>\n\n"
            f"<b>{S} ᴜsᴇʀ:</b> {message.from_user.mention}\n"
            f"<b>ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇʀ ʙᴏᴛ.</b>\n\n"
            f"<b>❤️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {DEV}</b>")
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 ᴜᴘᴅᴀᴛᴇ", url="https://t.me/Dx_Update"),
         InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url="https://t.me/Dx_Codex")],
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# --- 3. ADVANCED MULTI-BUTTON BROADCAST ---
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ!</b>")
    
    msg = message.reply_to_message
    raw_text = msg.text or msg.caption or ""
    
    buttons = []
    if "[" in raw_text and "](buttonurl:" in raw_text:
        pattern = r"\[(.*?)\]\(buttonurl:(.*?)\)"
        matches = re.findall(pattern, raw_text)
        for b_text, b_url in matches:
            buttons.append([InlineKeyboardButton(b_text, url=b_url.strip())])
        raw_text = re.sub(pattern, "", raw_text)

    markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    count = 0
    async for user in users_db.find():
        try:
            if msg.photo:
                await client.send_photo(user['user_id'], msg.photo.file_id, caption=raw_text, reply_markup=markup)
            else:
                await client.send_message(user['user_id'], raw_text, reply_markup=markup, disable_web_page_preview=True)
            count += 1
            await asyncio.sleep(0.1)
        except: pass
    await message.reply_text(f"<b>✅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛᴏ {count} ɪᴅs.</b>")

# --- 4. ADVANCED MODERATION (WARN 1-3, BAN, MUTE) ---
@app.on_message(filters.command(["warn", "ban", "tmute", "pin", "filter"]) & filters.group)
async def moderation_logic(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    cmd = message.command[0]
    await message.delete()

    if not message.reply_to_message: return
    target = message.reply_to_message.from_user

    if cmd == "warn":
        val = int(message.command[1]) if len(message.command) > 1 and message.command[1].isdigit() else 1
        res = await warns_db.find_one({"chat_id": message.chat.id, "user_id": target.id})
        count = (res["count"] if res else 0) + val
        
        if count >= 3:
            await client.ban_chat_member(message.chat.id, target.id)
            await warns_db.delete_one({"chat_id": message.chat.id, "user_id": target.id})
            text = f"<b>{B}</b>\n<b>{S} ᴀᴄᴛɪᴏɴ:</b> ᴀᴜᴛᴏ-ʙᴀɴ\n<b>{S} ᴜsᴇʀ:</b> {target.mention}\n<b>{S} ʀᴇᴀsᴏɴ:</b> 3 ᴡᴀʀɴs ʀᴇᴀᴄʜᴇᴅ\n<b>{B}</b>"
        else:
            await warns_db.update_one({"chat_id": message.chat.id, "user_id": target.id}, {"$set": {"count": count}}, upsert=True)
            text = f"<b>{B}</b>\n<b>{S} ᴀᴄᴛɪᴏɴ:</b> ᴡᴀʀɴ\n<b>{S} ᴜsᴇʀ:</b> {target.mention}\n<b>{S} ᴡᴀʀɴs:</b> {count}/3\n<b>{S} ʙʏ:</b> {message.from_user.mention}\n<b>{B}</b>"
        await client.send_message(message.chat.id, text)

    elif cmd == "ban":
        await client.ban_chat_member(message.chat.id, target.id)
        await client.send_message(message.chat.id, f"<b>{B}</b>\n<b>{S} ᴀᴄᴛɪᴏɴ:</b> ʙᴀɴ\n<b>{S} ᴛᴀʀɢᴇᴛ:</b> {target.mention}\n<b>{S} ᴀᴅᴍɪɴ:</b> {message.from_user.mention}\n<b>{B}</b>")

# --- 5. TOGGLE SETTINGS ---
@app.on_message(filters.command(["url", "welcome", "fwd", "badword"]) & filters.group)
async def toggle_settings(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    cmd = message.command[0]
    status = message.command[1].lower() == "on" if len(message.command) > 1 else False
    
    await settings_db.update_one({"chat_id": message.chat.id}, {"$set": {cmd: status}}, upsert=True)
    await message.reply_text(f"<b>{B}</b>\n<b>{S} {cmd.upper()} sᴇᴛ ᴛᴏ {'ᴏɴ' if status else 'ᴏғғ'}</b>\n<b>{B}</b>")
    await message.delete()

# --- 6. ADVANCED MUSIC ---
@app.on_message(filters.command("song"))
async def song_downloader(client, message: Message):
    if len(message.command) < 2: return
    query = message.text.split(None, 1)[1]
    m = await message.reply_text(f"<b>{B}</b>\n<b>🎵 sᴇᴀʀᴄʜɪɴɢ...</b>\n<b>{B}</b>")
    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            await message.reply_audio(info['url'], title=info['title'], caption=f"<b>{B}</b>\n<b>{S} ᴛɪᴛʟᴇ:</b> {info['title'][:30]}\n<b>{S} ᴜsᴇʀ:</b> {message.from_user.mention}\n<b>{B}</b>")
            await m.delete()
    except: await m.edit("<b>❌ ᴀᴜᴅɪᴏ ɴᴏᴛ ғᴏᴜɴᴅ!</b>")
    await message.delete()

# --- 7. MENU COMMAND ---
@app.on_message(filters.command("menu"))
async def help_menu(client, message: Message):
    text = (f"<b>╭{B}╮</b>\n"
            f"  <b>🛠 ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs 🛠</b>\n"
            f"<b>╰{B}╯</b>\n"
            f"<b>{S} /song:</b> ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴜsɪᴄ\n"
            f"<b>{S} /tagall:</b> ᴛᴀɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs\n"
            f"<b>{S} /profile:</b> ᴜsᴇʀ ɪɴғᴏ\n"
            f"<b>{S} /warn:</b> ᴡᴀʀɴɪɴɢ (3 = ʙᴀɴ)\n"
            f"<b>{S} /ban:</b> ʙᴀɴ ᴀ ᴜsᴇʀ\n"
            f"<b>{S} /pin:</b> ᴘɪɴ ᴀ ᴍᴇssᴀɢᴇ\n"
            f"<b>{S} /url [ᴏɴ/ᴏғғ]:</b> ᴀɴᴛɪ-ʟɪɴᴋ\n"
            f"<b>{S} /fwd [ᴏɴ/ᴏғғ]:</b> ᴀɴᴛɪ-ғᴏʀᴡᴀʀᴅ\n"
            f"<b>{S} /welcome [ᴏɴ/ᴏғғ]:</b> ᴛᴏɢɢʟᴇ ᴡᴇʟᴄᴏᴍᴇ\n"
            f"<b>{S} /badword [ᴏɴ/ᴏғғ]:</b> ʙᴀᴅᴡᴏʀᴅ ғɪʟᴛᴇʀ\n"
            f"<b>╰{B}╯</b>\n"
            f"<b>{S} sᴇɴᴅᴇʀ:</b> {message.from_user.mention}")
    await message.reply_text(text)
    await message.delete()

# --- 8. TAGALL & WELCOME ---
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_master(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    await message.delete()
    members = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot: members.append(f"<a href='tg://user?id={m.user.id}'>✨</a>")
    for i in range(0, len(members), 5):
        await client.send_message(message.chat.id, f"<b>{B}</b>\n<b>{S} ᴀᴛᴛᴇɴᴛɪᴏɴ ᴘʟᴇᴀsᴇ!</b>\n{' '.join(members[i:i+5])}\n<b>{B}</b>")
        await asyncio.sleep(2)

@app.on_message(filters.new_chat_members)
async def welcome_bot(client, message: Message):
    settings = await settings_db.find_one({"chat_id": message.chat.id})
    if settings and not settings.get("welcome", True): return
    for user in message.new_chat_members:
        await message.reply_photo(
            photo="https://graph.org/file/welcome.jpg",
            caption=f"<b>╭{B}╮</b>\n<b>✨ ᴡᴇʟᴄᴏᴍᴇ ✨</b>\n<b>╰{B}╯</b>\n<b>{S} ʜɪ:</b> {user.mention}\n<b>{S} ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]])
        )

# --- STARTUP ---
if __name__ == "__main__":
    Thread(target=run_web).start()
    loop = asyncio.get_event_loop()
    loop.create_task(auto_ping())
    print("Dx Final Master Bot Started!")
    app.run()
