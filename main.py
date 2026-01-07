import os
import sqlite3
import re
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8092965995:AAEvD6DLj0vI3eBJHkjkVOgfAfzgosdu96Y"
OWNER_ID = 6703335929
OWNER_NAME = "ᴅX-ᴄᴏᴅᴇX"
BOT_NAME = "ɴɪᴋᴏ"

app = Client("niko_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- DATABASE SETUP ---
db = sqlite3.connect("niko_brain.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS brain (question TEXT, answer TEXT)")
db.commit()

# --- WEB SERVER (For Render 24/7) ---
web = Flask('')
@web.route('/')
def home(): return f"{BOT_NAME} AI is Online!"

def run():
    web.run(host='0.0.0.0', port=8080)

# --- ADVANCED ML LEARNING MODULE ---
def learn(q, a):
    q = q.strip().lower()
    a = a.strip()
    if not q or not a: return
    cursor.execute("SELECT answer FROM brain WHERE question=?", (q,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO brain (question, answer) VALUES (?, ?)", (q, a))
        db.commit()

def get_ml_answer(user_query):
    user_query = user_query.strip().lower()
    
    cursor.execute("SELECT question, answer FROM brain")
    data = cursor.fetchall()
    
    if not data: return None
    
    questions = [row[0] for row in data]
    answers = [row[1] for row in data]
    
    # ML Logic: TF-IDF Vectorization
    vectorizer = TfidfVectorizer().fit_transform(questions + [user_query])
    vectors = vectorizer.toarray()
    
    # Cosine Similarity check
    user_vector = vectors[-1].reshape(1, -1)
    question_vectors = vectors[:-1]
    
    similarities = cosine_similarity(user_vector, question_vectors)[0]
    best_match_index = np.argmax(similarities)
    
    # Confidence Score (0.4 means 40% mil thakle reply debe)
    if similarities[best_match_index] > 0.4:
        return answers[best_match_index]
    
    return None

# --- MESSAGE HANDLER ---
@app.on_message(filters.group & ~filters.bot)
async def niko_chat(client, message: Message):
    if not message.text: return
    text = message.text

    # Triggers
    triggers = ["niko", "NIKO", "Niko"]
    words = text.split()
    first_word = words[0] if words else ""
    
    # 1. Hidden Auto-Learning (Saving context from group chats)
    if message.reply_to_message and message.reply_to_message.text:
        learn(message.reply_to_message.text, text)

    # 2. Response System
    if first_word in triggers:
        query = text.replace(first_word, "", 1).strip()
        
        # Developer Respect
        if message.from_user.id == OWNER_ID:
            if not query:
                await message.reply_text(f" <b>{OWNER_NAME}</b>. <code>I am here, Boss!</code>", quote=True)
                return

        if not query: return

        # Get Answer from ML Module
        ans = get_ml_answer(query)
        
        if ans:
            # HTML Style as requested
            final_reply = f"<b>{ans}</b>\n\n<code>— {BOT_NAME}</code>"
        else:
            final_reply = f"I'm learning this... <b>Please teach me.</b>\n<code>Reply to my name to teach.</code>"

        await message.reply_text(final_reply, quote=True)

# --- START BOT ---
if __name__ == "__main__":
    Thread(target=run).start()
    print(f"🚀 {BOT_NAME} started with Machine Learning Engine!")
    app.run()
