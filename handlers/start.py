from bot import bot
from db import add_user
from telebot import types
from telebot.types import Message

from .stats import handle_stat_cmd
from .edit import update_record_by_date
from .delete import delete_record_by_date
from .show import show_records_by_date


@bot.message_handler(commands=['start'])
def start_menu(message: Message) -> None:
    user_id = message.from_user.id
    name = message.from_user.first_name
    add_user(user_id, name)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('📝 Добавить новую запись'),
        types.KeyboardButton('🔍 Посмотреть запись по дате'),
        types.KeyboardButton('✏️ Изменить запись'),
        types.KeyboardButton('🗑 Удалить запись'),
        types.KeyboardButton('📊 Статистика сна')
    )

    bot.send_message(message.chat.id,
                     f'Привет {name}! Выбери действие:',
                     reply_markup=markup)


@bot.message_handler(func=lambda m: m.text in [
    '📝 Добавить новую запись',
    '🔍 Посмотреть запись по дате',
    '✏️ Изменить запись',
    '🗑 Удалить запись',
    '📊 Статистика сна'
])
def handle_menu_choice(message: Message) -> None:
    if message.text == '📝 Добавить новую запись':
        bot.send_message(message.chat.id, 'Начнем новую запись! Введи команду /sleep, когда готов(а) идти спать.')
    elif message.text == '🔍 Посмотреть запись по дате':
        bot.send_message(message.chat.id, 'Введите дату в формате DD-MM-YYYY')
        bot.register_next_step_handler(message, show_records_by_date)
    elif message.text == '🗑 Удалить запись':
        bot.send_message(message.chat.id, 'Выберите запись для удаления. Введите дату в формате DD-MM-YYYY')
        bot.register_next_step_handler(message, delete_record_by_date)
    elif message.text == '✏️ Изменить запись':
        bot.send_message(message.chat.id, 'Выберите запись для изменения. Введите дату в формате DD-MM-YYYY')
        bot.register_next_step_handler(message, update_record_by_date)
    elif message.text == '📊 Статистика сна':
        bot.register_next_step_handler(message, handle_stat_cmd)