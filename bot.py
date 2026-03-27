import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioStream
from yt_dlp import YoutubeDL

# إعدادات البوت
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")  # سشن الـPyrogram
GROUP_ID = int(os.getenv("GROUP_ID"))  # آي دي الجروب

app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)
pytgcalls = PyTgCalls(app)

ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True
}

@app.on_message(filters.command("شغل") & filters.chat(GROUP_ID))
async def play_song(client: Client, message: Message):
    try:
        text = message.text.split(" ", 1)[1]  # ناخذ اسم الأغنية
    except IndexError:
        await message.reply("گوللي شنو تريد تشغل 😅")
        return

    # نبحث على يوتيوب
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{text}", download=False)['entries'][0]
        url = info['url']

    await message.reply(f"آهلا بيك 😎، رح أشغل: {info['title']}")
    
    # تشغیل الصوت
    pytgcalls.join_group_call(
        GROUP_ID,
        AudioStream(url)
    )

if __name__ == "__main__":
    app.start()
    pytgcalls.start()
    print("البوت شغّال 😎")
    app.idle()
