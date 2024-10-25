import telebot
from telebot import types
from datetime import datetime, timedelta
import json
import os
import pandas as pd
import threading
import time

bot = telebot.TeleBot('8179560224:AAF6aFKzEp6zJN1s31whhtHB-ABgKDzzv_E')

# Словари для хранения выбора пользователей
user_group_choice = {} 
user_deadlines = {}
user_states = {}

# Файлы
DEADLINES_FILE = 'files/deadlines.json'
LECTURER_INFO_FILE = 'files/lecturer_info.xlsx'
NAME_GROUP_FILE = 'eng timetable files/names_groups.xlsx'  # Первый Excel файл с именами и группами
GROUP_INFO_FILE = 'eng timetable files/group_info.xlsx'    # Второй Excel файл с расписанием по группам
SCHEDULE_DAY_FILE_TEMPLATE = 'timetables/day/day_timetable_{}.json'  # Шаблон для имени файла

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

# Функция для автоудаления просроченных дедлайнов
def check_and_remove_expired_deadlines():
    current_date = datetime.now().date()
    for chat_id, deadlines in user_deadlines.items():
        expired_deadlines = []
        
        # Проверяем каждый дедлайн
        for deadline in deadlines:
            deadline_date = datetime.strptime(deadline['date'], '%d.%m.%Y').date()
            
            if deadline_date < current_date:
                expired_deadlines.append(deadline)
        
        if expired_deadlines:
            # Удаляем просроченные дедлайны
            user_deadlines[chat_id] = [d for d in deadlines if d not in expired_deadlines]
            save_deadlines()
            
            # Уведомляем пользователя
            expired_names = ', '.join([d['name'] for d in expired_deadlines])
            bot.send_message(chat_id, f"Истекшие дедлайны удалены: {expired_names}")

# Загрузка дедлайнов при старте бота
load_deadlines()

# Функция для отправки напоминаний
def send_reminders():
    while True:
        now = datetime.now()
        for chat_id, deadlines in user_deadlines.items():
            for deadline in deadlines:
                deadline_date = datetime.strptime(deadline['date'], '%d.%m.%Y').date()
                # Определяем даты для напоминаний
                reminder_dates = [
                    deadline_date - timedelta(weeks=1),  # за неделю
                    deadline_date - timedelta(days=3),    # за 3 дня
                    deadline_date - timedelta(days=1),    # за день
                    deadline_date                          # в день дедлайна
                ]
                # Проверяем, нужно ли отправить напоминание
                for reminder_date in reminder_dates:
                    if now.date() == reminder_date:
                        bot.send_message(chat_id, f"❗️Напоминание: Дедлайн '{deadline['name']}' наступает {deadline['date']}!")

        
        time.sleep(86400)  # Проверяем раз сутки

# Запускаем поток для отправки напоминаний
reminder_thread = threading.Thread(target=send_reminders, daemon=True)
reminder_thread.start()

# Проверка на истекшие дедлайны при старте бота
check_and_remove_expired_deadlines()

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

def get_day_name_en(date):
    days_en = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return days_en[date.weekday()]

def get_day_name_ru(date):
    days_ru = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    return days_ru[date.weekday()]

# Функция для отправки кнопок выбора расписания
def send_schedule_options(chat_id, group):
    markup = types.InlineKeyboardMarkup()
    button_week = types.InlineKeyboardButton("На неделю", callback_data=f'week_timetable_{group}')
    button_today = types.InlineKeyboardButton("На день", callback_data=f'today_timetable_{group}')
    markup.add(button_week, button_today)
    bot.send_message(chat_id, "Выбери нужное расписание.", reply_markup=markup)

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    with open('files/start_message.txt', 'r', encoding='utf-8') as file:
        answer = file.read()
    if message.text == "/start":
        bot.send_message(message.chat.id, answer)

input_day = None

# Команда /timetable
@bot.message_handler(commands=['timetable'])
def timetable_message(message):
    chat_id = message.chat.id

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("24КНТ-4", callback_data='group_4')
    button2 = types.InlineKeyboardButton("24КНТ-5", callback_data='group_5')
    button3 = types.InlineKeyboardButton("24КНТ-6", callback_data='group_6')
    markup.add(button1, button2, button3)

    bot.send_message(chat_id, "Выбери свою группу.", reply_markup=markup)

        
# Команда /deadline
@bot.message_handler(commands=['deadline'])
def deadline_command(message):
    # Создаем кнопки для дедлайнов
    markup = types.InlineKeyboardMarkup()
    button_add = types.InlineKeyboardButton("➕ Добавить дедлайн", callback_data='deadline_add_deadline')
    button_view = types.InlineKeyboardButton("📋 Посмотреть дедлайны", callback_data='deadline_view_deadlines')
    markup.add(button_add, button_view)

    # Отправляем сообщение с кнопками для дедлайнов
    bot.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=markup)

# Команда /lecturer
@bot.message_handler(commands=['lecturer'])
def lecturer_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введи название предмета для получения информации о преподавателях (например, 'программирование c/c++').")
    user_states[chat_id] = 'awaiting_subject_name'

# Обработчик для получения информации о преподавателях
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_subject_name')
def handle_subject_input(message):
    chat_id = message.chat.id
    subject_input = message.text.strip().lower()
    user_states.pop(chat_id, None)

    try:
        df = pd.read_excel(LECTURER_INFO_FILE, header=None)
        
        subject_data = df[df[0].str.lower().str.contains(subject_input, na=False)]

        lecturers_info = []
        formulas_info = []
        modules_info_set = set() 

        if not subject_data.empty:
            course_name = subject_data[0].iloc[0]

            # Заполняем списки
            for _, row in subject_data.iterrows():
                lecturer = row[1] if not pd.isna(row[1]) else None
                email = row[2] if not pd.isna(row[2]) else None
                modules = row[3] if not pd.isna(row[3]) else None
                formula = row[4] if not pd.isna(row[4]) else None

                # Формируем информацию о преподавателе и почте
                if lecturer:
                    lecturer_info = f"📚 Преподаватель: {lecturer}"
                    if email:
                        lecturer_info += f"\n✉️ Почта: {email}"
                    else:
                        lecturer_info += "\n✉️ Почта: Информация отсутствует"
                    lecturers_info.append(lecturer_info + "\n")

                if formula:
                    formulas_info.append(f"📐 {formula}")

                if modules:
                    modules_info_set.add(modules)

            # Формируем ответ
            response = f"Информация о курсе '{course_name}':\n\n"

            # Проверяем наличие информации о преподавателях
            if lecturers_info:
                response += "\n".join(lecturers_info) + "\n"
            else:
                response += "📚 Преподаватели: Информация отсутствует\n\n"

            if formulas_info:
                response += "\n".join(formulas_info) + "\n\n"
            else:
                response += "📐 Формула для оценки: Информация отсутствует\n\n"

            if modules_info_set:
                response += "📆 Модули с экзаменами: " + ", ".join(modules_info_set)
            else:
                response += "📆 Модули с экзаменами: Информация отсутствует"

            bot.send_message(chat_id, response)
        else:
            bot.send_message(chat_id, f"Предмет, содержащий '{subject_input}', не найден. Проверьте название и попробуйте снова.")
    except Exception as e:
        print(f"Error while reading lecturer data: {e}")
        bot.send_message(chat_id, "Произошла ошибка при обработке данных. Пожалуйста, попробуйте позже.")

# Обработчик ввода дня недели
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) in ['awaiting_day', 'awaiting_specific_day'])
def handle_day_input(message):
    global input_day
    chat_id = message.chat.id
    input_day = message.text.strip().lower()
    user_states.pop(chat_id, None)

    # Проверяем, что введен корректный день недели
    valid_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    if input_day not in valid_days:
        bot.send_message(chat_id, "Неверный день недели. Пожалуйста, введите корректный день.")
        return

    group = user_group_choice.get(chat_id)
    schedule_file = SCHEDULE_DAY_FILE_TEMPLATE.format(group)

    # Проверка для "четверг" и "суббота" - дни английского языка
    if input_day in ["четверг", "суббота"]:
        bot.send_message(chat_id, "Пожалуйста, введите свое полное ФИО (например, Иванов Иван Иванович):")
        user_states[chat_id] = 'awaiting_name'  # Устанавливаем состояние ожидания ФИО
    else:
        # Для остальных дней выводим обычное расписание
        try:
            with open(schedule_file, 'r', encoding='utf-8') as f:
                schedule = json.load(f)

            response_day = f'{input_day[:-1]}у' if input_day in ['пятница', 'среда'] else input_day
            lessons = schedule['schedule'].get(input_day, [])
            
            if lessons:
                response = f"✏️ _Расписание на {response_day} для группы {group}_: ✏️\n\n"
                for lesson in lessons:
                    response += f"*{lesson['subject']}*\n"
                    response += f"\u200B    •    *{lesson['time']}* - {lesson['lesson_type']}\n"
                    response += f"\u200B          *Преподаватель:* _{lesson['lecturer']}_\n"
                    response += f"\u200B          *Аудитория:* _{lesson['room']}_\n"
                    if 'dates' in lesson and lesson['dates']:
                        response += f"\u200B          *Даты:* {', '.join(lesson['dates'])}\n"

                    response += f"\n"

                bot.send_message(chat_id, response.strip(), parse_mode='Markdown')
            else:
                bot.send_message(chat_id, f"На {response_day} нет занятий.")
        except Exception as e:
            bot.send_message(chat_id, "Произошла ошибка при получении расписания.")

# Обработчик ввода ФИО
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_name')
def handle_name_input(message):
    global input_day
    chat_id = message.chat.id
    full_name = message.text.strip()
    response_day = f'{input_day[:-1]}у' if input_day in ['пятница', 'среда'] else input_day
    user_states.pop(chat_id, None)

    try:
        name_group_df = pd.read_excel(NAME_GROUP_FILE, header=None)

        # Проверяем, существует ли ФИО в столбце с именами (B)
        group_row = name_group_df[name_group_df[1].str.contains(full_name, na=False)]
        if not group_row.empty:
            group_number = group_row.iloc[0][3]  # Извлекаем группу из столбца с группами (D)

            # Загрузка расписания по английскому на нужный день (четверг или суббота)
            try:
                group_info_df = pd.read_excel(GROUP_INFO_FILE, sheet_name=input_day, header=None)
                group_info_rows = group_info_df[group_info_df[1] == group_number]

                if not group_info_rows.empty:
                    response_lines = [f"✏️ _Расписание английского для группы {group_number}_: ✏️\n"]
                    for _, row in group_info_rows.iterrows():
                        time = row[0]  # Время занятия
                        audience_number = f"{int(row[2]):03}"  # Номер аудитории с ведущими нулями, если необходимо
                        building = row[3]  # Корпус
                        teacher = row[4]  # Преподаватель из столбца E

                        response_lines.append(f"\u200B    •    *Время:* _{time}_")
                        response_lines.append(f"\u200B          *Преподаватель:* _{teacher}_")
                        response_lines.append(f"\u200B          *Аудитория:* _{audience_number}_ - _{building}_\n")
                
                    response = "\n".join(response_lines)
                    bot.send_message(chat_id, response, parse_mode='Markdown')
                else:
                    bot.send_message(chat_id, f"У группы {group_number} в {response_day} нет занятий по английскому.")
            except Exception as e:
                bot.send_message(chat_id, "Произошла ошибка при получении расписания по английскому.")
        else:
            bot.send_message(chat_id, "ФИО не найдено. Пожалуйста, проверь написание и попробуй снова.")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка при поиске группы по ФИО.")

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    global input_day
    data = call.data
    chat_id = call.message.chat.id

    # Обработка выбора группы
    if data.startswith('group_'):
        group = data.split('_')[1]  # Получаем номер группы
        user_group_choice[chat_id] = group  # Сохраняем выбранную группу

        bot.answer_callback_query(call.id, f"Твоя группа 24КНТ-{group}.")

        # Используем функцию для отправки кнопок выбора расписания
        send_schedule_options(chat_id, group)

    # Обработка расписания на неделю
    elif data.startswith('week_timetable_'):
        group = user_group_choice.get(chat_id)
        filename = f'timetables/week/week_timetable_{group}.jpg'  # Формируем имя файла расписания

        try:
            with open(filename, 'rb') as image:
                text = f"Вот расписание на неделю для группы 24КНТ-{group}."
                bot.send_message(chat_id, text)
                bot.send_photo(chat_id, image)
        except FileNotFoundError:
            bot.send_message(chat_id, "Извини, твоё расписание пока не готово.")

    # Обработка расписания на сегодня и завтра
    elif data.startswith('today_timetable_'):
        group = user_group_choice.get(chat_id)

        # Просим пользователя ввести день недели
        bot.send_message(chat_id, "Введите день недели (например, понедельник):")
        user_states[chat_id] = 'awaiting_day'  # Устанавливаем состояние ожидания дня недели
        bot.answer_callback_query(call.id)
        
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
                response = "📋 *Твои дедлайны:*\n"
                markup = types.InlineKeyboardMarkup()
                for idx, deadline in enumerate(deadlines, 1):
                    response += f"{idx}. *{deadline['name']}* - {deadline['date']}\n"
                    edit_button = types.InlineKeyboardButton(f"✏ Изменить {idx}", callback_data=f'deadline_edit_{idx-1}_name')
                    delete_button = types.InlineKeyboardButton(f"🗑 Удалить {idx}", callback_data=f'deadline_delete_{idx-1}')
                    markup.add(edit_button, delete_button)
                bot.send_message(chat_id, response, parse_mode='Markdown', reply_markup=markup)

        elif data.startswith('deadline_edit_'):
            try:
                parts = data.split('_')
                idx = int(parts[2])
                if len(parts) > 3 and parts[3] == 'name':
                    user_states[chat_id] = f'editing_deadline_{idx}_name'
                    bot.send_message(chat_id, f"Введи новое название дедлайна #{idx+1}:")
                else:
                    bot.send_message(chat_id, "Что-то пошло не так...")
            except ValueError:
                bot.send_message(chat_id, "Ошибка обработки данных.")
        
        elif data.startswith('deadline_delete_'):
            try:
                idx = int(data.split('_')[-1])
                deadlines = user_deadlines.get(str(chat_id), [])
                if 0 <= idx < len(deadlines):
                    deleted = deadlines.pop(idx)
                    user_deadlines[str(chat_id)] = deadlines
                    save_deadlines()
                    bot.send_message(chat_id, f"✅ Дедлайн *'{deleted['name']}'* удалён.", parse_mode='Markdown')
                else:
                    bot.send_message(chat_id, "Неверный индекс дедлайна.")
            except ValueError:
                bot.send_message(chat_id, "Ошибка обработки данных.")

    bot.answer_callback_query(call.id)

# Обработчик для добавления дедлайна
@bot.message_handler(func=lambda message: True)
def handle_deadline_input(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id, '')

    if state == 'awaiting_deadline_name':
        deadline_name = message.text.strip()
        if not deadline_name:
            bot.send_message(chat_id, "⚠️ Название дедлайна не может быть пустым. Введи название:")
            return
        # Сохраняем название дедлайна и ожидаем дату
        user_deadlines.setdefault(str(chat_id), []).append({'name': deadline_name, 'date': ''})
        user_states[chat_id] = 'awaiting_deadline_date'
        bot.send_message(chat_id, "Введи дату дедлайна в формате День.Месяц.Год (например, 31.12.2024):")
    
    elif state == 'awaiting_deadline_date':
        deadline_date_input = message.text.strip()
        # Проверяем формат даты
        try:
            deadline_date = datetime.strptime(message.text, '%d.%m.%Y').date()
            deadline_date_str = deadline_date.strftime('%d.%m.%Y')

            # Проверка на просроченность
            if deadline_date < datetime.now().date():
                bot.send_message(chat_id, "⚠️ Ошибка: дата дедлайна не может быть в прошлом. Введите корректную дату:")
                return
        except ValueError:
            bot.send_message(chat_id, "⚠️ Неверный формат даты. Пожалуйста, введи дату в формате День.Месяц.Год (например, 31.12.2024):")
            return
        # Сохраняем дату в последний добавленный дедлайн
        deadlines = user_deadlines.get(str(chat_id), [])
        if deadlines and deadlines[-1]['date'] == '':
            deadlines[-1]['date'] = deadline_date_str
            user_deadlines[str(chat_id)] = deadlines
            save_deadlines()
            bot.send_message(chat_id, f"✅ Дедлайн *'{deadlines[-1]['name']}'* с датой *{deadline_date_str}* добавлен.", parse_mode='Markdown')
            user_states.pop(chat_id, None)
        else:
            bot.send_message(chat_id, "Произошла ошибка при сохранении дедлайна.")
            user_states.pop(chat_id, None)
    
    elif state.startswith('editing_deadline_'):
        try:
            parts = state.split('_')
            if len(parts) == 4 and parts[2].isdigit() and parts[3] == 'name':
                idx = int(parts[2])
                new_name = message.text.strip()
                if not new_name:
                    bot.send_message(chat_id, "Название дедлайна не может быть пустым. Введи новое название:")
                    return
                deadlines = user_deadlines.get(str(chat_id), [])
                if 0 <= idx < len(deadlines):
                    old_name = deadlines[idx]['name']
                    deadlines[idx]['name'] = new_name
                    user_deadlines[str(chat_id)] = deadlines
                    bot.send_message(chat_id, f"✅ Дедлайн #{idx+1} успешно изменён с *'{old_name}'* на *'{new_name}'*.", parse_mode='Markdown')
                    user_states[chat_id] = f'editing_deadline_{idx}_date'
                    bot.send_message(chat_id, f"Введи новую дату дедлайна #{idx+1} в формате День.Месяц.Год (например, 31.12.2024):")
                else:
                    bot.send_message(chat_id, "Неверный индекс дедлайна.")

            elif len(parts) == 4 and parts[2].isdigit() and parts[3] == 'date':
                idx = int(parts[2])
                new_date_input = message.text.strip()
                try:
                    new_date = datetime.strptime(new_date_input, '%d.%m.%Y').date()
                    new_date_str = new_date.strftime('%d.%m.%Y')
                except ValueError:
                    bot.send_message(chat_id, "Неверный формат даты. Пожалуйста, введи дату в формате День.Месяц.Год (например, 31.12.2024):")
                    return
                deadlines = user_deadlines.get(str(chat_id), [])
                if 0 <= idx < len(deadlines):
                    old_date = deadlines[idx]['date']
                    deadlines[idx]['date'] = new_date_str
                    user_deadlines[str(chat_id)] = deadlines
                    save_deadlines()
                    bot.send_message(chat_id, f"✅ Дедлайн #{idx+1} успешно обновлён:\n*Название:* {deadlines[idx]['name']}\n*Дата:* {new_date_str}", parse_mode='Markdown')
                else:
                    bot.send_message(chat_id, "Неверный индекс дедлайна.")

                user_states.pop(chat_id, None)
            else:
                bot.send_message(chat_id, "Неверный формат состояния.")
        except Exception as e:
            bot.send_message(chat_id, "Произошла ошибка при обработке запроса.")
            user_states.pop(chat_id, None)
        except ValueError:
            bot.send_message(chat_id, "Ошибка обработки данных.")
            user_states.pop(chat_id, None)
    
bot.infinity_polling() 