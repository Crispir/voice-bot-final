import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает. Отправьте голосовое сообщение.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = await update.message.voice.get_file()
        voice_bytes = await voice.download_as_bytearray()

        # Тест: просто вернём подтверждение (без STT)
        await update.message.reply_text("Голосовое получено! 🎤 (STT временно отключён для отладки)")

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
