import telebot
from telebot import types
bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

user_choices = {} # Словарь для хранения выбора пользователей

@bot.message_handler(commands=['start'])
def start_message(message):
    with open('start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()

    # Создаем кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("4 группа")
    button2 = types.KeyboardButton("5 группа")
    button3 = types.KeyboardButton("6 группа")
    markup.add(button1, button2, button3)

    # Сообщение вместе с кнопками
    bot.send_message(message.chat.id, answer + "\nПожалуйста, выбери один из вариантов:", reply_markup=markup)

# Обработчик выбора группы    
@bot.message_handler(func=lambda message: message.text in ["4 группа", "5 группа", "6 группа"])
def handle_choice(message):
    # Сохраняем выбор
    user_choices[message.chat.id] = message.text
    
    # Отправляем подтверждение выбора и убираем кнопки
    bot.send_message(message.chat.id, f"Ты из {message.text[:-1]}ы. Теперь все команды будут основываться на этом выборе.", reply_markup=types.ReplyKeyboardRemove())
    
# Команда с расписанием
@bot.message_handler(commands=['timetable'])
def timetable_message(message):
    user_group = user_choices.get(message.chat.id)
    
    if not user_group:
        bot.send_message(message.chat.id, "Я не знаю из какой ты группы. Используй команду /start и выбери свою группу.")
    else:
        # Создаем кнопки
        markup = types.InlineKeyboardMarkup()
        button_week = types.InlineKeyboardButton("Расписание на неделю", callback_data=f'week_timetable_{user_group[0]}')
        button_day = types.InlineKeyboardButton("Расписание на день", callback_data=f'day_timetable_{user_group[0]}')
        markup.add(button_week, button_day)

        # Отправляем сообщение с кнопками
        bot.send_message(message.chat.id, "Тебе нужно расписание на день или на неделю?", reply_markup=markup)

# Обработчик для кнопок расписания
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    group = call.data.split('_')[-1]
    if call.data.startswith('week_timetable_'):
        try:
            with open(f'week_timetable_{group}.jpg', 'rb') as image:
                text = f"Вот расписание на неделю для {group} группы."
                bot.send_message(call.message.chat.id, text)
                bot.send_photo(call.message.chat.id, image)
        except FileNotFoundError:
            bot.send_message(call.message.chat.id, "Извини, твое расписание пока не готово.")
        bot.answer_callback_query(call.id)

    elif call.data.startswith('day_timetable_'):
        try:
            with open(f'day_timetable_{group}.jpg', 'rb') as image:
                text = f"Вот расписание на день для {group} группы."
                bot.send_message(call.message.chat.id, text)
                bot.send_photo(call.message.chat.id, image)
        except FileNotFoundError:
            bot.send_message(call.message.chat.id, "Извини, твое расписание пока не готово.")
        bot.answer_callback_query(call.id)

bot.infinity_polling()