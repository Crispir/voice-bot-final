import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Отправьте голосовое — я распознаю текст.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Скачиваем голосовое
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()

        # Отправляем в Whisper
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "audio/ogg"
        }
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
            headers=headers,
            data=voice_bytes
        )

        # Логируем ответ (для отладки)
        print("STT Status:", response.status_code)
        print("STT Response:", response.text[:200])

        # Парсим результат
        result = response.json()
        if isinstance(result, dict) and "text" in result:
            user_text = result["text"].strip()
            if user_text:
                await update.message.reply_text(f"Распознано:\n«{user_text}»")
                return

        await update.message.reply_text("Не удалось распознать речь. Попробуйте говорить чётче.")

    except Exception as e:
        error_msg = str(e)[:150]
        await update.message.reply_text(f"Ошибка STT: {error_msg}")
        print("Full error:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()
