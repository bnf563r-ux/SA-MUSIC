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

# تثبيت المكتبات الأساسية واحدة واحدة لتفادي تعارض dependencies
RUN pip install --no-cache-dir pyrogram
RUN pip install --no-cache-dir tgcrypto
RUN pip install --no-cache-dir pytgcalls==2.0.0
RUN pip install --no-cache-dir yt-dlp

# تشغيل البوت
CMD ["python", "bot.py"]
