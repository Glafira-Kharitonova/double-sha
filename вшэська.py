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

@bot.message_handler(commands=['start'])
def start_message(message):
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()
    bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=['audience'])
def audience(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    livovka, pecherskaya = types.KeyboardButton("на Львовской"), types.KeyboardButton("на Большой Печерской")
    markup.add(livovka, pecherskaya)
    bot.send_message(message.chat.id, 'В каком корпусе находится аудитория?', reply_markup=markup)
    reply_markup = types.ReplyKeyboardRemove()

@bot.message_handler(func=lambda message: message.text in ['на Львовской', 'на Большой Печерской'])
def building(message):
    if message.text == 'на Львовской':
        bot.send_message(message.chat.id, 'Напишите номер аудитории.')
        bot.register_next_step_handler(message, livovka_handler)
    if message.text == 'на Большой Печерской':
        bot.send_message(message.chat.id, 'Напишите номер аудитории.')
        bot.register_next_step_handler(message, pecherskaya_handler)

def livovka_handler(message):
    audience_of_livovka = {}
    with open('audience_of_livovka.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            audience_of_livovka[key] = value
    user_input = message.text
    response = audience_of_livovka.get(str(user_input), "Аудитория не найдена.")
    bot.send_message(message.chat.id, response)


def pecherskaya_handler(message):
    audience_of_pecherskaya = {}
    with open('audience_of_pecherskaya.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            audience_of_pecherskaya[key] = value
    user_input = message.text
    response = audience_of_pecherskaya.get(str(user_input), "Аудитория не найдена.")
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: 'спасибо' in message.text.lower())
def thank():
    answer_for_thank = ['Не за что!', 'Обращайся!', 'Рад помочь!']
    bot.send_message(message.chat.id, random.choice(answer_for_thank))


bot.infinity_polling()