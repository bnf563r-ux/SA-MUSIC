FROM python:3.10-slim

# تثبيت FFmpeg و build tools و مكتبات tgcrypto
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libffi-dev \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# تحديث pip
RUN pip install --upgrade pip

# تثبيت Cython أولًا (tgcrypto يحتاجها)
RUN pip install --no-cache-dir Cython

# تثبيت المكتبات الأساسية
RUN pip install --no-cache-dir pyrogram tgcrypto yt-dlp

# تثبيت pytgcalls و tgcalls مباشرة من GitHub
RUN pip install --no-cache-dir git+https://github.com/pytgcalls/pytgcalls.git
RUN pip install --no-cache-dir git+https://github.com/pytgcalls/tgcalls.git

# تشغيل البوت
CMD ["python", "bot.py"]
