import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL

# إعدادات من .env
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# إنشاء بوت وPyTgCalls
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)

# أمر تشغيل أغنية يوتيوب
@app.on_message(filters.command("شغل") & filters.group)
async def play_song(client, message):
    if len(message.command) < 2:
        await message.reply_text("هات رابط اليوتيوب أو اسم الأغنية 😎")
        return

    query = " ".join(message.command[1:])
    
    # تحميل أفضل نتيجة من يوتيوب
    ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']

    chat_id = message.chat.id

    # تشغيل الأغنية
    try:
        await pytgcalls.join_group_call(chat_id, AudioPiped(url))
        await message.reply_text(f"شغلتلك الأغنية 🎵: {info['title']}")
    except Exception as e:
        await message.reply_text(f"صارت مشكلة 😅: {e}")

# تشغيل البوت
app.start()
pytgcalls.start()
print("البوت شغال 24/7 🚀")
app.idle()
