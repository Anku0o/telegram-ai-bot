import replicate
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]
IMGBB_API_KEY = os.environ["IMGBB_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a photo and I’ll enhance it using AI!")

async def enhance_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()

    upload = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": IMGBB_API_KEY},
        files={"image": photo_bytes}
    )

    if not upload.ok:
        await update.message.reply_text("😢 Failed to upload image to imgbb.")
        return

    image_url = upload.json()["data"]["url"]
    await update.message.reply_text("✨ Enhancing your photo...")

    try:
        result = replicate_client.run(
            "xinntao/real-esrgan",
            input={"image": image_url}
        )
        await update.message.reply_photo(photo=result, caption="✅ Here's your enhanced image!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, enhance_photo))
app.run_polling()
