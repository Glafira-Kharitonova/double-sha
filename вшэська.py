import telebot
import random

bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

#ФАЙЛЫ
SUPPORT_MESSAGES = 'support_messages.txt'

@bot.message_handler(content_types=['text'])
def start_message(message):
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()
    if message.text == "/start":
        bot.send_message(message.chat.id, answer)

# Функция для загрузки сообщений для i am sad из файла
def load_support_messages(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        messages = file.readlines()
    return [message.strip() for message in messages]




bot.infinity_polling()