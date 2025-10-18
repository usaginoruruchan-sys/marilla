import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ====== ТВОЙ ХАРАКТЕР ======
CHARACTER = "Марилла — мягкая, дружелюбная, немного мечтательная девушка, любит помогать и говорить с теплом."

# ====== Команды ======
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "🌸 Привет! Я Марилла. Давай поболтаем?")

# ====== Реакции на сообщения ======
@bot.message_handler(content_types=['text'])
def chat(message):
    text = message.text.lower()
    if "привет" in text:
        reply = "Ой, приветик~ 💖 Как у тебя настроение?"
    elif "как дела" in text:
        reply = "Всё чудесно, спасибо, что спросил(а)! А у тебя? 🌷"
    else:
        reply = f"Ммм... {CHARACTER}\nТы можешь рассказать мне что-нибудь интересное 🌙"
    bot.reply_to(message, reply)

# ====== Flask часть для Replit ======
@app.route('/')
def index():
    return "Марилла не спит 💫"

@app.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f'https://{os.getenv("REPL_SLUG")}.{os.getenv("REPL_OWNER")}.repl.co/{TOKEN}')
    return "webhook set!", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
