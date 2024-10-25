import telebot
from telebot import types
import random
bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

@bot.message_handler(commands=['start'])
def start_message(message):
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()
    bot.send_message(message.chat.id, answer)

# Обработчик команды /iamsad
@bot.message_handler(commands=['iamsad'])
def send_support_message(message):
    with open('support_messages.txt', 'r', encoding='utf-8') as file:
        support_messages = [line for line in file.readlines()]
    bot.send_message(message.chat.id, random.choice(support_messages))


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
    answer_for_thank = ['Не за что!', 'Обращайся!', 'Рад помочь!', 'Успехов Вам!']
    bot.send_message(message.chat.id, random.choice(answer_for_thank))


bot.infinity_polling()