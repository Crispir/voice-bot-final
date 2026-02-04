import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Готов к голосу. Отправьте голосовое.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = await update.message.voice.get_file()
        voice_bytes = await voice.download_as_bytearray()

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
            headers=headers,
            data=voice_bytes
        )

        print("STT status:", response.status_code)
        try:
            result = response.json()
            text = result.get("text", "").strip()
            if text:
                await update.message.reply_text(f"🎤 Распознано:\n{text}")
            else:
                await update.message.reply_text("Не распознано. Говорите чётче.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка парсинга: {e}")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {type(e).__name__}")
        print("Error:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()
