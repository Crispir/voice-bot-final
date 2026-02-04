async def handle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
            headers=headers,
            data=voice_bytes
        )
        
        print("STT Response:", response.status_code, response.text)  # ← ключевая строка
        
        result = response.json()
        user_text = result.get("text", "").strip() if isinstance(result, dict) else ""

        if not user_text:
            await update.message.reply_text("Не удалось распознать речь.")
            return

        await update.message.reply_text(f"Распознано: «{user_text}»")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)[:100]}")
        print("Full error:", e)
