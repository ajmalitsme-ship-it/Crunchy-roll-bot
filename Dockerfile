# Base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    git \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone (optional)
ENV TZ=Asia/Kolkata

# Set working directory
WORKDIR /app

# Copy requirements first (for better build caching)
COPY requirements.txt .

# Upgrade pip & install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir yt-dlp

# Copy all application files
COPY . .

# Create required directories
RUN mkdir -p /app/downloads /app/cookies /app/logs

# Environment variables (optional, can be overridden at runtime)
ENV DOWNLOAD_DIR=/app/downloads
ENV COOKIE_DIR=/app/cookies
ENV LOG_DIR=/app/logs
ENV PYTHONUNBUFFERED=1

# Expose nothing (bot runs on Telegram)
# EXPOSE 8080

# Run the bot
CMD ["python", "bot.py"]
