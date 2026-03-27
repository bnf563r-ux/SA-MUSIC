FROM python:3.11-slim

# تثبيت ffmpeg وباقي الأدوات المطلوبة
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# مجلد الشغل
WORKDIR /app

# نسخ ملف المتطلبات أول شي وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# مجلد التحميلات
RUN mkdir -p downloads

CMD ["python", "music_bot.py"]
