import telebot
from telebot import types
bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

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

def livovka_handler(message):
    audience_of_livovka = {}
    with open('audience_of_livovka.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            audience_of_livovka[key] = value
    user_input = message.text
    response = audience_of_livovka.get(str(user_input), "Аудитория не найдена.")
    bot.send_message(message.chat.id, response)
   
bot.infinity_polling()