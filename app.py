import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 Привет! Я — бот поддержки.\n"
        "Напиши, что у тебя на сердце — я выслушаю и отвечу с заботой."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    if not user_text or len(user_text) < 2:
        await update.message.reply_text("Расскажи чуть подробнее — я рядом.")
        return

    try:
        # Генерируем ответ через ИИ
        prompt = (
            f"Пользователь написал: '{user_text}'. "
            "Ты — добрый, мудрый психолог. Ответь кратко (1–2 предложения), с эмпатией, "
            "без советов, если не просят. Напомни, что человек не один."
        )

        response = requests.post(
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
            result = response.json()
            ai_reply = result[0]["generated_text"].strip()
            # Убираем повтор промпта
            if ai_reply.startswith(prompt):
                ai_reply = ai_reply[len(prompt):].strip()
        except:
            ai_reply = (
                f"Спасибо, что поделился этим. "
                "Помни: даже в трудные моменты ты не один. Дыши глубже — всё пройдёт. 💙"
            )

        await update.message.reply_text(ai_reply)

    except Exception as e:
        await update.message.reply_text("Произошла ошибка. Попробуй позже.")
        print("Error:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
