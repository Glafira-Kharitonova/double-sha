import telebot
import random

bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

# Функция для загрузки сообщений для i am sad из файла
def load_support_messages(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        messages = file.readlines()
    return [message.strip() for message in messages]

support_messages = load_support_messages('support_messages.txt')

# Обработчик команды /iamsad
@bot.message_handler(commands=['iamsad'])
def send_support_message(message):
    support_message = random.choice(support_messages)
    bot.send_message(message.chat.id, support_message)


@bot.message_handler(content_types=['text'])
def start_message(message):
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()
    if message.text == "/start":
        bot.send_message(message.chat.id, answer)


bot.infinity_polling()