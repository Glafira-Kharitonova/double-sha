import telebot
from telebot import types
from datetime import datetime
import json
import os
import pandas as pd

bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

# Словари для хранения выбора пользователей
user_group_choice = {} 
user_deadlines = {}
user_states = {}

# Файлы
DEADLINES_FILE = 'files/deadlines.json'
NAME_GROUP_FILE = 'eng timetable files/names_groups.xlsx'  # Первый Excel файл с именами и группами
GROUP_INFO_FILE = 'eng timetable files/group_info.xlsx'    # Второй Excel файл с расписанием по группам

# Функция для загрузки дедлайнов из файла
def load_deadlines():
    global user_deadlines
    if os.path.exists(DEADLINES_FILE):
        try:
            with open(DEADLINES_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    user_deadlines = json.loads(content)
                else:
                    user_deadlines = {}
        except json.JSONDecodeError:
            user_deadlines = {}
            save_deadlines()
    else:
        user_deadlines = {}
        save_deadlines()

# Функция для сохранения дедлайнов в файл
def save_deadlines():
    with open(DEADLINES_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_deadlines, f, ensure_ascii=False, indent=4)

# Загрузка дедлайнов при старте бота
load_deadlines()

# Функция для получения группы по ФИО
def get_group_by_fio(fio):
    df_names_groups = pd.read_excel(NAME_GROUP_FILE, header=None)
    # Ищем ФИО в столбце B (индекс 1) и возвращаем группу из столбца D (индекс 3)
    group_row = df_names_groups[df_names_groups[1].str.contains(fio, na=False)]
    if not group_row.empty:
        return group_row[3].values[0]  # Возвращаем первую найденную группу
    return None

# Функция для получения информации о группе из второго файла
def get_group_info(group):
    df_group_info = pd.read_excel(GROUP_INFO_FILE, header=None)
    # Фильтруем по группе в столбце B (индекс 1)
    group_info = df_group_info[df_group_info[1].str.contains(group, na=False)]
    return group_info

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    with open('files/start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()
    if message.text == "/start":
        bot.send_message(message.chat.id, answer)

# Команда /timetable
@bot.message_handler(commands=['timetable'])
def timetable_message(message):
    today = datetime.now().weekday()  # 0 - понедельник, 6 - воскресенье
    chat_id = message.chat.id

    #Отправка обычного расписания
    if today not in [3, 5]:
        group = user_group_choice.get(chat_id)

        if not group:
            # Создаем кнопки для выбора группы
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("24КНТ-4", callback_data='group_4')
            button2 = types.InlineKeyboardButton("24КНТ-5", callback_data='group_5')
            button3 = types.InlineKeyboardButton("24КНТ-6", callback_data='group_6')
            markup.add(button1, button2, button3)

            # Отправляем сообщение с кнопками выбора группы
            bot.send_message(chat_id, "Выбери свою группу.", reply_markup=markup)
        else:
            # Создаем кнопки для выбора расписания
            markup = types.InlineKeyboardMarkup()
            button_week = types.InlineKeyboardButton("Расписание на неделю", callback_data=f'week_timetable_{group}')
            button_day = types.InlineKeyboardButton("Расписание на день", callback_data=f'day_timetable_{group}')
            markup.add(button_week, button_day)

            # Отправляем сообщение с кнопками выбора расписания
            bot.send_message(chat_id, "Тебе нужно расписание на день или на неделю?", reply_markup=markup)
    else:
        # Расписание по английскому
        user_states[chat_id] = 'awaiting_name'
        bot.send_message(chat_id, "Сегодня у тебя английский язык. Пожалуйста, введи свое полное имя (Фамилия Имя Отчество) (например, Иванов Иван Иванович):")
        
# Команда /deadline
@bot.message_handler(commands=['deadline'])
def deadline_command(message):
    markup_remove = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=markup_remove)

    # Создаем кнопки для дедлайнов
    markup = types.InlineKeyboardMarkup()
    button_add = types.InlineKeyboardButton("Добавить дедлайн", callback_data='deadline_add_deadline')
    button_view = types.InlineKeyboardButton("Посмотреть дедлайны", callback_data='deadline_view_deadlines')
    markup.add(button_add, button_view)

    # Отправляем сообщение с кнопками для дедлайнов
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Обработчик ввода ФИО
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_name')
def handle_name_input(message):
    chat_id = message.chat.id
    full_name = message.text.strip()

    # Чтение файла с именами и группами
    name_group_df = pd.read_excel(NAME_GROUP_FILE, header=None)

    # Проверяем, существует ли ФИО в столбце B
    if full_name in name_group_df[1].values:
        # Находим номер группы
        group_row = name_group_df[name_group_df[1] == full_name]
        group_number = group_row.iloc[0][3]  # Извлекаем группу из столбца D

        # Определяем день недели и соответствующий лист
        today = datetime.now().weekday()
        sheet_name = 'Четверг' if today == 3 else 'Суббота'  # 3 - четверг, 5 - суббота

        # Чтение второго файла с информацией по группам
        try:
            group_info_df = pd.read_excel(GROUP_INFO_FILE, sheet_name=sheet_name, header=None)
        except ValueError as e:
            bot.send_message(chat_id, "Похоже файл с твоим расписанием отсутствует.")
            return

        # Находим строки, соответствующие номеру группы
        group_info_rows = group_info_df[group_info_df[1] == group_number]

        if not group_info_rows.empty:
            # Собираем данные из всех строк
            response_lines = []
            for _, row in group_info_rows.iterrows():
                time = str(row[0])  # Время
                audience_number = str(int(row[2])) if len(str(int(row[2]))) == 3 else '0' + str(int(row[2])) # Аудитория
                building = str(row[3])  # Корпус

                # Формируем строку ответа
                response_lines.append(f"Время: {time}, Аудитория: {audience_number}, Корпус: {building}")

            # Формируем ответ
            response = f"Группа: {group_number}\n" + "\n".join(response_lines)
            bot.send_message(chat_id, response)
        else:
            bot.send_message(chat_id, f"У этой группы {group_number} сегодня нет английского.\nПопробуй в другой день.")
    else:
        bot.send_message(chat_id, "Твоё ФИО не найдено.")

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    data = call.data
    chat_id = call.message.chat.id

    # Обработка выбора группы
    if data.startswith('group_'):
        group = data.split('_')[1]  # Получаем номер группы
        user_group_choice[chat_id] = group  # Сохраняем выбранную группу

        bot.answer_callback_query(call.id, f"Вы выбрали группу 24КНТ-{group}.")

        # Создаем кнопки для выбора расписания
        markup = types.InlineKeyboardMarkup()
        button_week = types.InlineKeyboardButton("Расписание на неделю", callback_data=f'week_timetable_{group}')
        button_day = types.InlineKeyboardButton("Расписание на день", callback_data=f'day_timetable_{group}')
        markup.add(button_week, button_day)

        # Отправляем сообщение с кнопками выбора расписания
        bot.send_message(chat_id, "Тебе нужно расписание на день или на неделю?", reply_markup=markup)

    # Обработка расписания
    elif data.startswith('week_timetable_') or data.startswith('day_timetable_'):
        parts = data.split('_')
        timetable_type = parts[0]  # 'week' или 'day'
        group = parts[-1]  # Номер группы
        filename = f'{timetable_type}_timetable_{group}.jpg'  # Формируем имя файла расписания

        try:
            with open(filename, 'rb') as image:
                text = f"Вот расписание на {'неделю' if timetable_type == 'week' else 'день'} для 24КНТ-{group} группы."
                bot.send_message(chat_id, text)
                bot.send_photo(chat_id, image)
        except FileNotFoundError:
            bot.send_message(chat_id, "Извини, твоё расписание пока не готово.")

    # Обработка дедлайнов
    elif data.startswith('deadline_'):
        if data == 'deadline_add_deadline':
            user_states[chat_id] = 'awaiting_deadline_name'
            bot.send_message(chat_id, "Введи название дедлайна:")
        elif data == 'deadline_view_deadlines':
            deadlines = user_deadlines.get(str(chat_id), [])
            if not deadlines:
                bot.send_message(chat_id, "У тебя пока нет дедлайнов.")
            else:
                response = "Твои дедлайны:\n"
                for idx, deadline in enumerate(deadlines, 1):
                    response += f"{idx}. {deadline['name']} - {deadline['date']}\n"
                bot.send_message(chat_id, response)

# Обработчик для добавления дедлайна
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) in ['awaiting_deadline_name', 'awaiting_deadline_date'])
def handle_deadline_input(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state == 'awaiting_deadline_name':
        # Сохраняем название дедлайна и ожидаем дату
        user_deadlines.setdefault(str(chat_id), []).append({'name': message.text, 'date': None})
        user_states[chat_id] = 'awaiting_deadline_date'
        bot.send_message(chat_id, "Введите дату дедлайна в формате День.Месяц.Год (например, 31.12.2024):")
    elif state == 'awaiting_deadline_date':
        # Проверяем формат даты
        try:
            deadline_date = datetime.strptime(message.text, '%d.%m.%Y').date()
            # Сохраняем дату в последний добавленный дедлайн
            deadlines = user_deadlines.get(str(chat_id), [])
            if deadlines and deadlines[-1]['date'] is None:
                deadlines[-1]['date'] = message.text
                save_deadlines()
                bot.send_message(chat_id, "Дедлайн успешно добавлен!")
            else:
                bot.send_message(chat_id, "Произошла ошибка при сохранении дедлайна.")
        except ValueError:
            bot.send_message(chat_id, "Неверный формат даты. Пожалуйста, введи дату в формате День.Месяц.Год (например, 31.12.2024):")
            return

        user_states.pop(chat_id, None)

bot.infinity_polling()