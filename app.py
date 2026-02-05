import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 🟢 Используем новый токен напрямую (временно)
BOT_TOKEN = "8260383113:AAGdldTXdKgeYpMwRk6YgrAIvu2B9gd6nu0"  # ← замени на новый!
HF_TOKEN = os.environ.get("HF_TOKEN") or "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"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Готов к голосу.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = await update.message.voice.get_file()
        voice_bytes = await voice.download_as_bytearray()

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(
            "https://api-inference.huggingface.co/models/systran/faster-whisper-small",
            headers=headers,
            data=voice_bytes
        )
        print("STT:", response.status_code)

        try:
            result = response.json()
            text = " ".join(seg.get("text", "") for seg in result).strip() if isinstance(result, list) else ""
            if text:
                await update.message.reply_text(f"🎤 {text}")
            else:
                await update.message.reply_text("Говорите чётче.")
        except Exception as e:
            await update.message.reply_text(f"STT error: {e}")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()
