import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ⚠️ Временный fallback — замени xxx на свой токен
HF_TOKEN = os.environ.get("HF_TOKEN") or "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"
BOT_TOKEN = os.environ["BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Привет! Отправь голосовое сообщение — я распознаю речь.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Скачиваем голосовое сообщение от Telegram
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()

        # Отправляем в faster-whisper-small (стабильная модель)
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "audio/ogg"
        }
        response = requests.post(
            "https://api-inference.huggingface.co/models/systran/faster-whisper-small",
            headers=headers,
            data=voice_bytes
        )

        # Логируем статус (для отладки в Railway Logs)
        print("STT Status:", response.status_code)

        # Обрабатываем ответ
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            # faster-whisper возвращает список сегментов
            text = " ".join(seg.get("text", "") for seg in result).strip()
            if text:
                await update.message.reply_text(f"🎤 Распознано:\n«{text}»")
                return

        await update.message.reply_text("Не удалось распознать речь. Попробуйте говорить чётче.")

    except Exception as e:
        error_name = type(e).__name__
        await update.message.reply_text(f"Ошибка: {error_name}")
        print("Full error:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()
