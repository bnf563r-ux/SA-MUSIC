"""
🎵 بوت الموسيقى - بالهجة العراقية
يدور على يوتيوب ويشغل الأغاني بالمكالمات الصوتية

المتطلبات:
    pip install pyrogram tgcalls pytgcalls yt-dlp python-dotenv

متغيرات البيئة المطلوبة بملف .env:
    BOT_TOKEN   - توكن البوت من @BotFather
    API_ID      - من my.telegram.org
    API_HASH    - من my.telegram.org
"""

import asyncio
import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

load_dotenv()

# ───────────────────────────── إعداد العميل ──────────────────────────────

API_ID   = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app      = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
tgcalls  = PyTgCalls(app)

DOWNLOADS = Path("downloads")
DOWNLOADS.mkdir(exist_ok=True)

# ─────────────────────────── البحث على يوتيوب ────────────────────────────

def search_youtube(query: str) -> dict | None:
    """يبحث على يوتيوب ويرجع أفضل نتيجة"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,   # بحث سريع بدون تحميل
        "default_search": "ytsearch5",  # أول 5 نتائج
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{query}", download=False)
        if info and "entries" in info and info["entries"]:
            # نختار أكثر واحد مشاهدات (أفضل مطابقة شعبياً)
            entries = [e for e in info["entries"] if e]
            best = max(entries, key=lambda e: e.get("view_count") or 0)
            return best
    return None


def download_audio(url: str, out_path: str) -> str:
    """يحمّل الصوت بصيغة opus/mp3"""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_path,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return out_path + ".mp3"

# ───────────────────────────────── الأوامر ───────────────────────────────

@app.on_message(filters.command(["شغل", "play", "p"]) & filters.group)
async def play_command(client: Client, message: Message):
    """
    الأمر: شغل <اسم الأغنية>
    مثال: شغل childhood slowed reverbed
    """
    query = " ".join(message.command[1:]).strip()
    if not query:
        await message.reply(
            "⚠️ أخوي اكتب اسم الأغنية بعد الأمر 🎵\n"
            "مثال: `/شغل childhood slowed reverbed`"
        )
        return

    chat_id = message.chat.id
    status_msg = await message.reply(f"🔍 هسه أدور على: **{query}** ويا...")

    # ── 1. بحث يوتيوب ──
    result = search_youtube(query)
    if not result:
        await status_msg.edit(
            "😓 والله دورت بس ما لكيت شي على يوتيوب!\n"
            "جرب تكتب الاسم بشكل ثاني 🙏"
        )
        return

    title    = result.get("title", "مجهول")
    video_id = result.get("id", "")
    url      = f"https://www.youtube.com/watch?v={video_id}"
    duration = result.get("duration", 0)
    views    = result.get("view_count", 0)

    await status_msg.edit(
        f"✅ لكيتها! **{title}**\n"
        f"⏱ المدة: {duration//60}:{duration%60:02d}\n"
        f"👁 المشاهدات: {views:,}\n\n"
        f"⬇️ هسه أحملها وأشغلها..."
    )

    # ── 2. تحميل الصوت ──
    safe_name = re.sub(r'[^\w]', '_', video_id)
    out_path  = str(DOWNLOADS / safe_name)
    audio_file = out_path + ".mp3"

    if not Path(audio_file).exists():
        try:
            download_audio(url, out_path)
        except Exception as e:
            await status_msg.edit(
                f"😤 التحميل ما نجح أخوي، صار خطأ:\n`{e}`\n"
                f"جرب مرة ثانية بعد شوية!"
            )
            return

    await status_msg.edit(
        f"🎵 **{title}**\n"
        f"🔗 {url}\n\n"
        f"📞 هسه أدخل المكالمة وأشغلها..."
    )

    # ── 3. تشغيل في المكالمة الصوتية ──
    try:
        await tgcalls.join_group_call(
            chat_id,
            AudioPiped(audio_file),
        )
        await status_msg.edit(
            f"🎶 تفضلوا تستمعون!\n\n"
            f"▶️ هسه يشتغل: **{title}**\n"
            f"🔗 {url}\n\n"
            f"⏹ تريد توقفها؟ اكتب `/وقف`"
        )
    except Exception as e:
        # البوت موجود بالمكالمة، نغيّر الأغنية
        try:
            await tgcalls.change_stream(chat_id, AudioPiped(audio_file))
            await status_msg.edit(
                f"🔄 بدلت الأغنية إلى: **{title}**\n"
                f"🔗 {url}\n\n"
                f"استمتعوا 🎵"
            )
        except Exception as e2:
            await status_msg.edit(
                f"😩 ما كدرت أشغل الأغنية أخوي!\n"
                f"الخطأ: `{e2}`\n\n"
                f"تأكد إن البوت أدمن وفعّل صلاحية المكالمات الصوتية 🙏"
            )


@app.on_message(filters.command(["وقف", "stop", "s"]) & filters.group)
async def stop_command(client: Client, message: Message):
    """وقف التشغيل والخروج من المكالمة"""
    try:
        await tgcalls.leave_group_call(message.chat.id)
        await message.reply("⏹ خلاص وقفت الموسيقى وطلعت من المكالمة 👋")
    except Exception as e:
        await message.reply(f"😅 ما كدرت أوقف، الخطأ: `{e}`")


@app.on_message(filters.command(["بوز", "pause"]) & filters.group)
async def pause_command(client: Client, message: Message):
    """إيقاف مؤقت"""
    try:
        await tgcalls.pause_stream(message.chat.id)
        await message.reply("⏸ وقفتها مؤقتاً، كتب `/استمر` لو تريد ترجع تسمع 🎵")
    except Exception as e:
        await message.reply(f"😅 ما كدرت أوقف مؤقتاً، الخطأ: `{e}`")


@app.on_message(filters.command(["استمر", "resume"]) & filters.group)
async def resume_command(client: Client, message: Message):
    """متابعة بعد الإيقاف المؤقت"""
    try:
        await tgcalls.resume_stream(message.chat.id)
        await message.reply("▶️ يلا رجعنا! استمتعوا 🎶")
    except Exception as e:
        await message.reply(f"😅 ما كدرت أكمل، الخطأ: `{e}`")


@app.on_message(filters.command(["مساعدة", "help"]) & filters.group)
async def help_command(client: Client, message: Message):
    await message.reply(
        "🎵 **شلون تستخدم البوت؟**\n\n"
        "▶️ `/شغل <اسم الأغنية>` — يدور على يوتيوب ويشغل\n"
        "⏹ `/وقف` — يوقف ويطلع من المكالمة\n"
        "⏸ `/بوز` — وقفة مؤقتة\n"
        "▶️ `/استمر` — يكمل بعد الوقفة\n\n"
        "🔥 مثال:\n`/شغل childhood slowed reverbed`\n\n"
        "البوت يدور على يوتيوب ويشغل أحسن نتيجة ويا 💪"
    )

# ──────────────────────────────── التشغيل ────────────────────────────────

async def main():
    await tgcalls.start()
    print("✅ البوت شغّال ويا! اضغط Ctrl+C لو تريد توقفه.")
    await app.run()


if __name__ == "__main__":
    app.run(main())
