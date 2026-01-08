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
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, CallbackQuery
from pyrogram.enums import ChatMemberStatus, ParseMode

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8538226909:AAEKBGQPJ95MTJzYtpIG1-kUltuey42rbLU"
OWNER_ID = 6703335929 
MONGO_URL = "mongodb+srv://shadowur6_db_user:8AIIxZUjpanaQBjh@dx-codex.fmqcovu.mongodb.net/?retryWrites=true&w=majority&appName=Dx-codex"
CHANNEL_USERNAME = "Dx_Update" # Your Channel Username without @

# --- DATABASE SETUP ---
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.DxFinalDB
users_db = db.users
settings_db = db.settings
warns_db = db.warns

app = Client("Dx-Final-Bot", API_ID, API_HASH, bot_token=BOT_TOKEN)

# --- UI ELEMENTS ---
B = "╼━━━━━━━━━━━━━━╾"
S = "➲"
DEV = "ᴅx–ᴄᴏᴅᴇx"

# --- WEB SERVER FOR ALIVE ---
web = Flask('')
@web.route('/')
def home(): return f"{DEV} ғɪɴᴀʟ ʙᴏᴛ"
def run_web(): web.run(host='0.0.0.0', port=8080)

# --- HELPERS ---
async def is_admin(chat_id, user_id):
    if user_id == OWNER_ID: return True
    try:
        m = await app.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

async def is_subscribed(user_id):
    try:
        member = await app.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]
    except: return False

# --- VERIFY & START SYSTEM ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    await users_db.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    
    if not await is_subscribed(user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ ᴠᴇʀɪғʏ ᴍᴇ", callback_data="verify_user")]
        ])
        return await message.reply_text(f"<b>╭{B}╮</b>\n<b>      ⚠️ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ ⚠️</b>\n<b>╰{B}╯</b>\n\n<b>{S} ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ.</b>", reply_markup=buttons)

    text = (f"<b>╭{B}╮</b>\n"
            f"  <b>✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {DEV} ✨</b>\n"
            f"<b>╰{B}╯</b>\n\n"
            f"<b>{S} ʜᴇʟʟᴏ:</b> {message.from_user.mention}\n"
            f"<b>{S} sᴛᴀᴛᴜs:</b> ᴠᴇʀɪғɪᴇᴅ ᴜsᴇʀ ✅\n"
            f"<b>{S} ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀғᴜʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.</b>\n\n"
            f"<b>❤️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {DEV}</b>")
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
        [InlineKeyboardButton("🛠 ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_menu")]
    ])
    await message.reply_text(text, reply_markup=buttons)

@app.on_callback_query(filters.regex("verify_user"))
async def verify_callback(client, callback_query: CallbackQuery):
    if await is_subscribed(callback_query.from_user.id):
        await callback_query.answer("✅ Verified Successfully!", show_alert=True)
        await start_handler(client, callback_query.message)
        await callback_query.message.delete()
    else:
        await callback_query.answer("❌ You haven't joined yet!", show_alert=True)

# --- GROUP ONLY CHECK DECORATOR ---
def group_only(func):
    async def wrapper(client, message: Message):
        if message.chat.type == ChatMemberStatus.PRIVATE:
            return await message.reply_text(f"<b>{B}</b>\n<b>❌ sᴏʀʀʏ {message.from_user.mention}, ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!</b>\n<b>{B}</b>")
        return await func(client, message)
    return wrapper

# --- SEPARATED COMMAND FUNCTIONS ---

@app.on_message(filters.command("song"))
@group_only
async def song_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"<b>{B}</b>\n<b>{S} ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ!</b>\n<b>{B}</b>")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text(f"<b>{B}</b>\n<b>🔍 sᴇᴀʀᴄʜɪɴɢ ʏᴏᴜʀ sᴏɴɢ...</b>\n<b>{B}</b>")
    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            await message.reply_audio(info['url'], title=info['title'], caption=f"<b>{B}</b>\n<b>{S} ᴛɪᴛʟᴇ:</b> {info['title'][:30]}\n<b>{S} ʙʏ:</b> {message.from_user.mention}\n<b>{B}</b>")
            await m.delete()
    except: await m.edit("<b>❌ ɴᴏᴛ ғᴏᴜɴᴅ!</b>")

@app.on_message(filters.command("ban"))
@group_only
async def ban_cmd(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ!</b>")
    
    target = message.reply_to_message.from_user
    await client.ban_chat_member(message.chat.id, target.id)
    await message.reply_text(f"<b>╭{B}╮</b>\n<b>{S} ᴀᴄᴛɪᴏɴ:</b> ʙᴀɴ\n<b>{S} ᴜsᴇʀ:</b> {target.mention}\n<b>{S} ᴀᴅᴍɪɴ:</b> {message.from_user.mention}\n<b>╰{B}╯</b>")

@app.on_message(filters.command("warn"))
@group_only
async def warn_cmd(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    
    target = message.reply_to_message.from_user
    res = await warns_db.find_one({"chat_id": message.chat.id, "user_id": target.id})
    count = (res["count"] if res else 0) + 1
    
    if count >= 3:
        await client.ban_chat_member(message.chat.id, target.id)
        await warns_db.delete_one({"chat_id": message.chat.id, "user_id": target.id})
        text = f"<b>╭{B}╮</b>\n<b>{S} ᴀᴜᴛᴏ-ʙᴀɴ:</b> {target.mention}\n<b>{S} ʀᴇᴀsᴏɴ:</b> 3 ᴡᴀʀɴs ᴅᴏɴᴇ\n<b>╰{B}╯</b>"
    else:
        await warns_db.update_one({"chat_id": message.chat.id, "user_id": target.id}, {"$set": {"count": count}}, upsert=True)
        text = f"<b>╭{B}╮</b>\n<b>{S} ᴀᴄᴛɪᴏɴ:</b> ᴡᴀʀɴ\n<b>{S} ᴜsᴇʀ:</b> {target.mention}\n<b>{S} ʟᴇᴠᴇʟ:</b> {count}/3\n<b>╰{B}╯</b>"
    await message.reply_text(text)

@app.on_message(filters.command("tagall"))
@group_only
async def tagall_cmd(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    members = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot: members.append(f"<a href='tg://user?id={m.user.id}'>👤</a>")
    
    for i in range(0, len(members), 5):
        await client.send_message(message.chat.id, f"<b>{B}</b>\n<b>{S} ʜᴇʏ ᴇᴠᴇʀʏᴏɴᴇ ʟᴏᴏᴋ ʜᴇʀᴇ!</b>\n{' '.join(members[i:i+5])}\n<b>{B}</b>")
        await asyncio.sleep(1.5)

@app.on_message(filters.command(["url", "welcome", "badword"]))
@group_only
async def toggle_cmd(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    cmd = message.command[0]
    status = "on" in message.text.lower()
    await settings_db.update_one({"chat_id": message.chat.id}, {"$set": {cmd: status}}, upsert=True)
    await message.reply_text(f"<b>╭{B}╮</b>\n<b>{S} sᴇᴛᴛɪɴɢ:</b> {cmd.upper()}\n<b>{S} sᴛᴀᴛᴜs:</b> {'ᴇɴᴀʙʟᴇᴅ ✅' if status else 'ᴅɪsᴀʙʟᴇᴅ ❌'}\n<b>╰{B}╯</b>")

# --- ADVANCED WELCOME ---
@app.on_message(filters.new_chat_members)
async def welcome_bot(client, message: Message):
    settings = await settings_db.find_one({"chat_id": message.chat.id})
    if settings and not settings.get("welcome", True): return
    for user in message.new_chat_members:
        text = (f"<b>╭{B}╮</b>\n"
                f"  <b>✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ ✨</b>\n"
                f"<b>╰{B}╯</b>\n\n"
                f"<b>{S} ʜᴇʏ:</b> {user.mention}\n"
                f"<b>{S} ᴡᴇ ᴀʀᴇ ʜᴀᴘᴘʏ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ!</b>\n"
                f"<b>{S} ᴍᴀᴋᴇ sᴜʀᴇ ᴛᴏ ʀᴇᴀᴅ ʀᴜʟᴇs.</b>\n\n"
                f"<b>❤️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {DEV}</b>")
        await message.reply_photo(
            photo="https://graph.org/file/welcome.jpg",
            caption=text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✨ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/Dx_Codex")]])
        )

# --- MENU COMMAND ---
@app.on_message(filters.command("menu"))
async def menu_cmd(client, message: Message):
    text = (f"<b>╭{B}╮</b>\n"
            f"   <b>🛠 {DEV} ᴄᴏᴍᴍᴀɴᴅ ᴘᴀɴᴇʟ 🛠</b>\n"
            f"<b>╰{B}╯</b>\n"
            f"<b>{S} /sᴏɴɢ:</b> ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴜsɪᴄ\n"
            f"<b>{S} /ᴛᴀɢᴀʟʟ:</b> ᴍᴇɴᴛɪᴏɴ ᴀʟʟ\n"
            f"<b>{S} /ᴡᴀʀɴ:</b> ᴡᴀʀɴ ᴜsᴇʀ (1-3)\n"
            f"<b>{S} /ʙᴀɴ:</b> ʙᴀɴ ᴀ ᴍᴇᴍʙᴇʀ\n"
            f"<b>{S} /ᴜʀʟ [ᴏɴ/ᴏғғ]:</b> ᴀɴᴛɪ-ʟɪɴᴋ\n"
            f"<b>{S} /ᴡᴇʟᴄᴏᴍᴇ [ᴏɴ/ᴏғғ]:</b> ᴛᴏɢɢʟᴇ\n"
            f"<b>{S} /ʙᴀᴅᴡᴏʀᴅ [ᴏɴ/ᴏғғ]:</b> ғɪʟᴛᴇʀ\n"
            f"<b>╰{B}╯</b>\n"
            f"<b>{S} ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:</b> {message.from_user.mention}")
    await message.reply_text(text)

# --- STARTUP ---
if __name__ == "__main__":
    Thread(target=run_web).start()
    print("Dx Final Master Bot Started!")
    app.run()
