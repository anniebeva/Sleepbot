from bot import bot, user_sessions
from telebot import types
from telebot.types import Message
import datetime
from functools import partial

from .handlers_validators import record_not_found_error_bot, wrong_time_format_error_bot, \
    wrong_date_format_error_bot, find_record_by_number, validate_num_input_bot, return_to_start
from database import update_record
from helpers import load_records_by_date
from errors_validators import parse_user_time, parse_user_date

@bot.message_handler(commands=['update_record'])
def handle_update_record(message: Message) -> None:
    """
    Команда update records
    Бот высылает сообщение c просьбой ввести дату для поиска
    Отправляет пользователя на следующий шаг -> update_record

    :param message: команда show records
    """
    bot.send_message(message.chat.id,
                'Да, конечно, давай изменим детали' 
                    'Какая дата тебя интересует (в формате DD-MM-YYYY)?')
    bot.register_next_step_handler(message, update_record_by_date)


def update_record_by_date(message: Message) -> None:
    """
    Бот позволяет изменить информацию о сне за конкретную дату
    Если за данную дату несколько записаей, выводит их и запрашивает номер для удаления

    :param message: Message: ввод пользователя Даты для изменений
    :return: None, бот выдает информацию о ползьзователе
    """
    user_id = message.from_user.id

    search_date = parse_user_date(message.text)
    if not search_date:
        wrong_date_format_error_bot(message, update_record_by_date)
        return

    records_found = load_records_by_date(user_id, search_date)
    if not records_found:
        record_not_found_error_bot(message, return_to_start)
        return

    user_sessions.setdefault(user_id, {})
    user_sessions[user_id]['records_found'] = records_found
    user_sessions[user_id]['search_date'] = search_date

    if len(records_found) == 1:
        record = records_found[0]
        user_sessions[user_id]['record_to_update'] = record
        select_record_to_update(message, record, search_date)
        return

    message_lines = []
    for i, record in enumerate(records_found, start=1):
        message_lines.append(
            f'Запись {i}\n'
            f'💤 Сон: {record["sleep_time"]}\n'
            f'⏰ Пробуждение: {record["wake_time"]}\n'
            f'⭐ Качество: {record["sleep_quality"]}\n'
            f'📝 Заметки: {record["notes"]}\n'
        )

    bot.send_message(message.chat.id,
                     'Какую именно запись ты хочешь изменить? Введи номер:\n\n' +
                     '\n'.join(message_lines))
    bot.register_next_step_handler(message, update_record_by_number)
    return

def select_record_to_update(message: Message, record: dict, date: datetime.date) -> None:
    message_to_send = (
        f'Твоя запись за {date.strftime("%d-%m-%Y")}:\n'
        f'💤 Сон: {record["sleep_time"]}\n'
        f'⏰ Пробуждение: {record["wake_time"]}\n'
        f'⭐ Качество: {record["sleep_quality"]}\n'
        f'📝 Заметки: {record["notes"]}\n'
    )

    bot.send_message(message.chat.id, message_to_send)
    update_record_menu(message)

def update_record_by_number(message:Message) -> None:
    """
    Получает номер записи и удаляет ее из базы данных
    :param message: выбор пользователя
    :return:  None, удаляет запись
    """
    record_id = find_record_by_number(message, user_sessions)

    if record_id is None:
        return

    user_id = message.from_user.id
    record = next(r for r in user_sessions[user_id]['records_found'] if r['record_id'] == record_id)
    user_sessions[user_id]['record_to_update'] = record
    select_record_to_update(message, record, user_sessions[user_id].get('search_date'))


def update_record_menu(message: Message):
    name = message.from_user.first_name

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button_sleep_time = types.KeyboardButton('💤 Изменить время сна')
    button_wake_time = types.KeyboardButton('⏰ Изменить время пробуждения')
    button_quality = types.KeyboardButton('⭐ Изменить качество')
    button_notes = types.KeyboardButton('📝 Редактировать заметки')
    # button_full_rec = types.KeyboardButton('💣 Изменить всю запись')

    markup.add(button_sleep_time,
               button_wake_time,
               button_quality,
               button_notes)
               # button_full_rec

    bot.send_message(
        message.chat.id,
        f'Привет {name}! Что ты хочешь изменить?',
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text in [
    '💤 Изменить время сна',
    '⏰ Изменить время пробуждения',
    '⭐ Изменить качество',
    '📝 Редактировать заметки',
    # '💣 Изменить всю запись TBD'
])

def handle_menu_choice(message: Message) -> None:
    """
    Функция обработки выбора пользователя для изменения
    """
    text = message.text
    bot.send_message(message.chat.id, 'Окей, введи новые данные 👇',
                     reply_markup=types.ReplyKeyboardRemove())

    if text == '💤 Изменить время сна':
        bot.register_next_step_handler(message, update_sleep_time)
        return
    elif text == '⏰ Изменить время пробуждения':
        bot.register_next_step_handler(message, update_wake_time)
        return
    elif text == '⭐ Изменить качество':
        bot.register_next_step_handler(message, update_quality)
        return
    elif text == '📝 Редактировать заметки':
        bot.register_next_step_handler(message, update_notes)
        return


@bot.message_handler(commands=['update_sleep_time'])
def handle_update_sleep(message: Message):
    bot.send_message(message.chat.id, 'Введи верное время сна в формате hr:min')
    bot.register_next_step_handler(message, update_sleep_time)


def update_sleep_time(message: Message, show_msg=True):
    user_id = message.from_user.id
    record = user_sessions[user_id]['record_to_update']

    new_sleep_time_str = message.text.strip()

    new_time = parse_user_time(new_sleep_time_str)

    if not new_time:
        wrong_time_format_error_bot(
            message,
            partial(update_sleep_time, record=record)
        )
        return

    old_sleep_dt = record['sleep_time']
    if isinstance(old_sleep_dt, str):
        old_sleep_dt = datetime.datetime.fromisoformat(old_sleep_dt)

    new_sleep_dt = old_sleep_dt.replace(hour=new_time.hour, minute=new_time.minute)

    update_record(
        record['record_id'],
        new_sleep_dt,
        record['wake_time'],
        record['quality'],
        record['notes']
    )

    updated_record = {
        'record_id': record['record_id'],
        'sleep_time': new_sleep_dt,
        'wake_time': record['wake_time'],
        'quality': record['quality'],
        'notes': record['notes']
    }

    if show_msg:
        updated_rec_bot_msg(message, updated_record)

    return updated_record

@bot.message_handler(commands=['update_wake_time'])
def handle_update_wake(message: Message):
    bot.send_message(message.chat.id, 'Введи верное время подъема в формате hr:min')
    bot.register_next_step_handler(message, update_wake_time)

def update_wake_time(message: Message, show_msg=True):
    user_id = message.from_user.id
    record = user_sessions[user_id]['record_to_update']

    new_wake_time_str = message.text.strip()

    new_time = parse_user_time(new_wake_time_str)

    if not new_time:
        wrong_time_format_error_bot(
            message,
            partial(update_wake_time, record=record)
        )
        return

    old_wake_dt = record['wake_time']
    if isinstance(old_wake_dt, str):
        old_wake_dt = datetime.datetime.fromisoformat(old_wake_dt)

    new_wake_dt = old_wake_dt.replace(hour=new_time.hour, minute=new_time.minute)

    update_record(
        record['record_id'],
        record['sleep_time'],
        new_wake_dt,
        record['quality'],
        record['notes']
    )

    updated_record = {
        'record_id': record['record_id'],
        'sleep_time': record['sleep_time'],
        'wake_time': new_wake_dt,
        'quality': record['quality'],
        'notes': record['notes']
    }

    if show_msg:
        updated_rec_bot_msg(message, updated_record)

    return updated_record

@bot.message_handler(commands=['update_quality'])
def handle_update_quality(message: Message):
    bot.send_message(message.chat.id, 'Оцени свой сон от 1 до 10')
    bot.register_next_step_handler(message, update_quality)

def update_quality(message: Message, show_msg=True):
    user_id = message.from_user.id
    record = user_sessions[user_id]['record_to_update']
    new_quality = validate_num_input_bot(message, update_quality, 1, 10)

    update_record(
        record['record_id'],
        record['sleep_time'],
        record['wake_time'],
        new_quality,
        record['notes']
    )

    updated_record = {
        'record_id': record['record_id'],
        'sleep_time': record['sleep_time'],
        'wake_time': record['wake_time'],
        'quality': new_quality,
        'notes': record['notes']
    }

    if show_msg:
        updated_rec_bot_msg(message, updated_record)

    return updated_record

@bot.message_handler(commands=['update_notes'])

def handle_update_notes(message: Message):
    bot.send_message(message.chat.id, 'Какую заметку ты хочешь оставить?')
    bot.register_next_step_handler(message, update_wake_time)

def update_notes(message: Message, show_msg=True):
    user_id = message.from_user.id
    record = user_sessions[user_id]['record_to_update']

    new_note = message.text

    update_record(
        record['record_id'],
        record['sleep_time'],
        record['wake_time'],
        record['quality'],
        new_note
    )

    updated_record = {
        'record_id': record['record_id'],
        'sleep_time': record['sleep_time'],
        'wake_time': record['wake_time'],
        'quality': record['quality'],
        'notes': new_note
    }

    if show_msg:
        updated_rec_bot_msg(message, updated_record)

    return updated_record


def updated_rec_bot_msg(message: Message, updated_record):
    message_to_send = (
        f'💤 Сон: {updated_record["sleep_time"]}\n'
        f'⏰ Пробуждение: {updated_record["wake_time"]}\n'
        f'⭐ Качество: {updated_record["quality"]}\n'
        f'📝 Заметки: {updated_record["notes"]}'
    )

    bot.send_message(message.chat.id, f'✅ Твоя запись изменена:\n{message_to_send}')