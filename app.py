import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 🌿 Я — бот поддержки.\n"
        "Отправь голосовое сообщение — я прослушаю и отвечу с заботой."
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Скачиваем голосовое сообщение (в формате OGG/OPUS)
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()

        # Отправляем напрямую в Whisper (он принимает OGG!)
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "audio/ogg"
        }
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
            headers=headers,
            data=voice_bytes
        )
        
        # Извлекаем распознанный текст
        result = response.json()
        user_text = result.get("text", "").strip() if isinstance(result, dict) else ""

        if not user_text:
            await update.message.reply_text("Не удалось распознать речь. Попробуй говорить чётче.")
            return

        # Генерируем ответ через ИИ
        prompt = (
            f"Пользователь сказал: '{user_text}'. "
            "Ты — добрый, мудрый психолог. Ответь кратко (1–2 предложения), с эмпатией, "
            "без советов, если не просят. Напомни, что человек не один."
        )

        llm_response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct",
            headers={
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "inputs": prompt,
                "parameters": {"max_new_tokens": 120, "temperature": 0.7}
            }
        )

        try:
            ai_reply = llm_response.json()[0]["generated_text"].strip()
            # Убираем повтор промпта (иногда модель возвращает его)
            if ai_reply.startswith(prompt):
                ai_reply = ai_reply[len(prompt):].strip()
        except:
            ai_reply = (
                f"Спасибо, что поделился этим: «{user_text}». "
                "Помни: даже в трудные моменты ты не один. Дыши глубже — всё пройдёт. 💙"
            )

        await update.message.reply_text(ai_reply)

    except Exception as e:
        await update.message.reply_text("Произошла ошибка. Попробуй позже.")
        print("Error:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()
