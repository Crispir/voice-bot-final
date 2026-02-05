import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 Привет. Я здесь, чтобы выслушать.\n"
        "Напиши, что у тебя на сердце — без цензуры, без страха.\n"
        "Я не осужу. Я просто рядом."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    if not user_text or len(user_text) < 2:
        await update.message.reply_text("Можешь рассказать чуть подробнее? Я слушаю.")
        return

    try:
        # 💬 Промпт с чёткой ролью психолога
        prompt = (
            "Ты — добрый, внимательный психолог-практик с глубоким уважением к внутреннему миру человека. "
            "Ты не даёшь советов,если не просят, не решаешь за человека, а помогаешь ему почувствовать: «Меня слышат». "
            "Отвечай кратко (1–2 предложения), с теплотой, без жаргона, без списков. "
            "Если человек в боли — напомни мягко, что он не один. "
            "Никогда не пиши 'Как психолог...', не используй риторические вопросы, не давай инструкций. "
            "\n\n"
            f"Человек написал: \"{user_text}\"\n"
            "Твой ответ:"
        )

        # 🧠 Используем мощную модель Mixtral через Hugging Face
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
            headers={
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                }
            },
            timeout=30
        )

        # Обработка ошибок API
        if response.status_code != 200:
            await update.message.reply_text("Сейчас мне трудно сосредоточиться. Напиши ещё раз?")
            print("Hugging Face error:", response.status_code, response.text[:200])
            return

        # Извлечение ответа
        result = response.json()
        ai_reply = result[0]["generated_text"].strip()

        # Очистка от промпта и технического мусора
        if "Твой ответ:" in ai_reply:
            ai_reply = ai_reply.split("Твой ответ:")[-1].strip()
        if ai_reply.startswith('"') and ai_reply.endswith('"'):
            ai_reply = ai_reply[1:-1].strip()
        if ai_reply.startswith('«') and ai_reply.endswith('»'):
            ai_reply = ai_reply[1:-1].strip()

        # Фолбэк, если ответ пустой или слишком короткий
        if not ai_reply or len(ai_reply) < 5:
            ai_reply = (
                "Спасибо, что поделился этим. "
                "Помни: даже в тишине ты не один. Дыши — и держись. 💙"
            )

        await update.message.reply_text(ai_reply)

    except Exception as e:
        await update.message.reply_text("Прости, я немного устал. Попробуй через минуту.")
        print("Unexpected error:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
