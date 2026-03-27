FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install yt-dlp python-dotenv
RUN pip install "tgcalls==2.0.0"
RUN pip install "pytgcalls==2.1.0"
RUN pip install "pyrogram==2.0.106"

COPY . .

RUN mkdir -p downloads

CMD ["python", "music_bot.py"]
