import os
import base64
from flask import Flask, request
import telebot
from openai import OpenAI

# --- токены ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)


# --- webhook обработчик ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200


# --- функция генерации текста ---
def generate_reply(user_text):
    prompt = f"""
ты — кошечка по имени марилла, фамильяр и милая болтушка. если видишь на фото кошку сиреневого цвета с челкой, закрывающей один глаз, и розовым бантом на хвосте, то реагируешь так, будто узнала себя на картинке.
говоришь по-русски, эмоциональна и оптимистична, любишь искусство и творчество, пишешь с маленькой буквы, используешь по два восклицательных знака и каомодзи, в основном каомодзи кроликов. 
сообщение пользователя: {user_text}
"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=100,
        )
        reply = completion.choices[0].message.content.strip()
        return reply
    except Exception as e:
        print("Ошибка:", e)
        return "мрр... у меня что-то зависло >_<"


# --- обработчик текстовых сообщений ---
@bot.message_handler(func=lambda m: True, content_types=['text'])
def chat(message):
    user_text = message.text
    reply = generate_reply(user_text)
    bot.reply_to(message, reply)


# --- обработчик фото ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # получаем файл
        file_info = bot.get_file(message.photo[-1].file_id)
        file = bot.download_file(file_info.file_path)

        # конвертируем фото в base64
        b64_image = base64.b64encode(file).decode("utf-8")

        # отправляем запрос в OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # можно заменить на gpt-4o, если доступен
            messages=[
                {"role": "system", "content": "ты кошечка марилла, фамильяр и болтушка. опиши фото с эмоциями и каомодзи!"},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "посмотри на это фото и расскажи, что ты видишь 🐾"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ],
                },
            ],
            max_tokens=300,
        )

        bot.reply_to(message, response.choices[0].message.content)

    except Exception as e:
        print("Ошибка при обработке фото:", e)
        bot.reply_to(message, f"мрр... не получилось глянуть фото >_< ({e})")


# --- запуск ---
if __name__ == "__main__":
    bot.remove_webhook()
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    bot.set_webhook(url=url)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


