import asyncio
import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream, InputAudioStream
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

queue = {}

def search_youtube(query):
    with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        return info["entries"][0]["url"], info["entries"][0]["title"]

@app.on_message(filters.text & filters.group)
async def music_handler(_, message):
    text = message.text

    if text.startswith("شغل"):
        query = text.replace("شغل", "").strip()
        await message.reply("🔎 دا أدورلك...")

        url, title = search_youtube(query)
        chat_id = message.chat.id

        if chat_id not in queue:
            queue[chat_id] = []

        queue[chat_id].append(url)

        if len(queue[chat_id]) == 1:
            await call.join_group_call(
                chat_id,
                InputStream(InputAudioStream(url))
            )
            await message.reply(f"🎧 هسه شغلتلك: {title}")
        else:
            await message.reply(f"📀 ضفتها للقائمة: {title}")

    elif text == "تخطي":
        chat_id = message.chat.id
        if chat_id in queue and len(queue[chat_id]) > 1:
            queue[chat_id].pop(0)
            next_song = queue[chat_id][0]

            await call.change_stream(
                chat_id,
                InputStream(InputAudioStream(next_song))
            )
            await message.reply("⏭ تم التخطي")
        else:
            await message.reply("❌ ماكو شي بعد")

    elif text == "اطلع":
        await call.leave_group_call(message.chat.id)
        await message.reply("👋 طلعت من المكالمة")

async def main():
    await app.start()
    await call.start()
    print("🔥 البوت اشتغل!")
    await asyncio.Event().wait()

asyncio.run(main())
