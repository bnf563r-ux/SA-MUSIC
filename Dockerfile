FROM python:3.10-slim

# تثبيت FFmpeg و build tools و مكتبات tgcrypto
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# تحديث pip
RUN pip install --upgrade pip

# تثبيت Cython أولًا (tgcrypto يحتاجها)
RUN pip install --no-cache-dir Cython

# تثبيت المكتبات الأساسية بدون تحديد نسخة
RUN pip install --no-cache-dir pyrogram
RUN pip install --no-cache-dir tgcrypto
RUN pip install --no-cache-dir pytgcalls
RUN pip install --no-cache-dir yt-dlp

# تشغيل البوت
CMD ["python", "bot.py"]
