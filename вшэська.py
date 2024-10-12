import telebot
from telebot import types
bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')
@bot.message_handler(content_types=['text'])

def start_message(message):
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()
    if message.text == "/start":
        bot.send_message(message.chat.id, answer)
bot.infinity_polling()