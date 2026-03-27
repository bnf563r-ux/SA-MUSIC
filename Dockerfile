# استخدم صورة Python كاملة
FROM python:3.10-slim

# تثبيت FFmpeg و build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملفات البوت
WORKDIR /app
COPY . /app

# تثبيت المكتبات
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# أمر تشغيل البوت
CMD ["python", "bot.py"]
