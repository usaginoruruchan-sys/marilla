import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def hello():
    return "Marilla is alive!"

@app.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "(ฅ^•ﻌ•^ฅ) hi-hi!! i'm marilla!! what's up??")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"meow! you said: {message.text}")

def start_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


