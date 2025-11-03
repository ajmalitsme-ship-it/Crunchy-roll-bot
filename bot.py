import os
import json
import yt_dlp
from pyrogram import Client, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads")
COOKIE_DIR = os.getenv("COOKIE_DIR", "./cookies")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(COOKIE_DIR, exist_ok=True)

app = Client("crunchyroll_bot", bot_token=BOT_TOKEN)

# /start
@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply_text(
        "👋 **Welcome to Crunchyroll Downloader Bot!**\n\n"
        "Use /setcookie to set your Crunchyroll cookies.\n"
        "Then send any Crunchyroll video URL to download it 🍿"
    )

# /setcookie
@app.on_message(filters.command("setcookie"))
async def set_cookie(_, msg):
    await msg.reply_text(
        "🍪 Send your Crunchyroll cookie JSON now.\n\n"
        "**Steps:**\n"
        "1. Open [crunchyroll.com](https://www.crunchyroll.com) (logged in)\n"
        "2. Export cookies with *Cookie-Editor* extension\n"
        "3. Copy full JSON and paste it here."
    )

@app.on_message(filters.text & ~filters.command(["start", "setcookie"]))
async def handle_text(_, msg):
    text = msg.text.strip()

    # If this is a cookie JSON
    if text.startswith('[') and text.endswith(']'):
        try:
            data = json.loads(text)
            cookie_path = os.path.join(COOKIE_DIR, f"{msg.from_user.id}.json")
            with open(cookie_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            await msg.reply_text("✅ Cookie saved successfully!\nNow send any Crunchyroll link to download.")
        except Exception as e:
            await msg.reply_text(f"❌ Invalid JSON format.\nError: {e}")
        return

    # If this is a Crunchyroll URL
    if "crunchyroll.com" in text:
        cookie_path = os.path.join(COOKIE_DIR, f"{msg.from_user.id}.json")
        if not os.path.exists(cookie_path):
            await msg.reply_text("⚠️ No cookie found! Use /setcookie first.")
            return

        await msg.reply_text("⏳ Downloading video, please wait...")
        outtmpl = os.path.join(DOWNLOAD_DIR, f"{msg.from_user.id}_%(title)s.%(ext)s")

        try:
            ydl_opts = {
                "outtmpl": outtmpl,
                "cookiesfrombrowser": None,
                "cookiefile": cookie_path,
                "format": "best",
                "quiet": True,
                "merge_output_format": "mp4",
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file_path = ydl.prepare_filename(info)

            await msg.reply_video(file_path, caption=f"🎬 **{info.get('title')}**\n✅ Downloaded from Crunchyroll")
        except Exception as e:
            await msg.reply_text(f"❌ Error: {e}")
        return

    await msg.reply_text("❗ Unknown input. Use /setcookie or send Crunchyroll link.")

print("✅ Bot is running...")
app.run()
