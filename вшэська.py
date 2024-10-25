import telebot
from telebot import TeleBot, types
import random
bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

#Сообщение-приветствие
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


#Обработчик команды \where
@bot.message_handler(commands=['where'])
def where(message):
    markup = types.InlineKeyboardMarkup()
    livovka_button = types.InlineKeyboardButton("на Львовской", callback_data='liv_where')
    pecherskaya_button = types.InlineKeyboardButton("на Б.Печерской", callback_data='pecher_where')
    markup.add(livovka_button, pecherskaya_button)
    bot.send_message(message.chat.id, 'Какой корпус Вас интересует?', reply_markup=markup)


@bot.callback_query_handler(func=lambda called: called.data in ['liv_where', 'pecher_where'])
def corpus(called):
    if called.data == 'liv_where':
        bot.send_message(called.message.chat.id, 'Напишите, что вы ищите.')
        reply_markup = types.ReplyKeyboardRemove()
        bot.register_next_step_handler(called.message, livovka_where_handler)

    elif called.data == 'pecher_where':
        bot.send_message(called.message.chat.id, 'Напишите, что вы ищите.')
        reply_markup = types.ReplyKeyboardRemove()
        bot.register_next_step_handler(called.message, pecherskaya_where_handler)


def livovka_where_handler(message):
    where_of_livovka = {}
    with open('where_of_livovka.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            where_of_livovka[key] = value
    user_input = message.text
    response = where_of_livovka.get(user_input.upper(), "Я вас не понимаю. Попробуйте точнее сформулировать свой запрос.")
    bot.send_message(message.chat.id, response)


def pecherskaya_where_handler(message):
    where_of_pecherskaya = {}
    with open('where_of_pecherskaya.txt.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            where_of_pecherskaya[key] = value
    user_input = message.text
    response = where_of_pecherskaya.get(user_input.upper(), "Я вас не понимаю. Попробуйте точнее сформулировать свой запрос.")
    bot.send_message(message.chat.id, response)


#Обработчик команды \audience
@bot.message_handler(commands=['audience'])
def audience(message):
    markup = types.InlineKeyboardMarkup()
    livovka_button = types.InlineKeyboardButton("на Львовской", callback_data='livovka')
    pecherskaya_button = types.InlineKeyboardButton("на Б.Печерской", callback_data='pecherskaya')
    markup.add(livovka_button, pecherskaya_button)
    bot.send_message(message.chat.id, 'В каком корпусе находится аудитория?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['livovka', 'pecherskaya'])
def building(call):
    if call.data == 'livovka':
        bot.send_message(call.message.chat.id, 'Напишите номер аудитории.')
        bot.register_next_step_handler(call.message, livovka_handler)

    elif call.data == 'pecherskaya':
        bot.send_message(call.message.chat.id, 'Напишите номер аудитории.')
        bot.register_next_step_handler(call.message, pecherskaya_handler)


def livovka_handler(message):
    audience_of_livovka = {}
    with open('audience_of_livovka.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            audience_of_livovka[key] = value
    user_input = message.text
    draw_of_auditories = {}
    with open('photo_path.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            draw_of_auditories[key] = value
    if user_input in draw_of_auditories:
        photo_path = draw_of_auditories.get(user_input)
        response = audience_of_livovka.get(user_input, "Аудитория не найдена. Попробуйте ещё раз.")
        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=response)
    else:
        response = audience_of_livovka.get(user_input, "Аудитория не найдена. Попробуйте ещё раз.")
        bot.send_message(message.chat.id, response)


def pecherskaya_handler(message):
    audience_of_pecherskaya = {}
    with open('audience_of_pecherskaya.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(': ')
            audience_of_pecherskaya[key] = value
    user_input = message.text
    response = audience_of_pecherskaya.get(user_input, "Аудитория не найдена. Попробуйте ещё раз")
    bot.send_message(message.chat.id, response)

#Ответ на благодарность от пользователя
@bot.message_handler(func=lambda message: 'спасибо' in message.text.lower())
def thank(message):
    answer_for_thank = ['Не за что!', 'Обращайтесь!', 'Рад помочь!', 'Успехов Вам!', 'Не потеряйтесь!']
    bot.send_message(message.chat.id, random.choice(answer_for_thank))


bot.infinity_polling()