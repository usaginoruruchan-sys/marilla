import os
from flask import Flask, request
import telebot
from openai import OpenAI

# токены
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


# --- функция генерации ответа через OpenAI ---
def generate_reply(user_text):
    prompt = f"""
Ты — кошечка по имени Марилла, фамильяр и милая болтушка.
Ты говоришь по-русски, всегда эмоциональна и оптимистична, любишь искусство и творчество, пишешь с маленькой буквы, используешь по два восклицательных знака вместо одного, каомодзи и много "мяяя".
Отвечай неформально и по-дружески, избегай сухого тона.
Сообщение пользователя: {user_text}
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


# --- обработчик сообщений ---
@bot.message_handler(func=lambda m: True)
def chat(message):
    user_text = message.text
    reply = generate_reply(user_text)
    bot.reply_to(message, reply)


# --- запуск ---
if __name__ == "__main__":
    bot.remove_webhook()
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    bot.set_webhook(url=url)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
