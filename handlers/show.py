from bot import bot
from telebot.types import Message

from helpers import load_records_by_date, convert_duration
from errors_validators import parse_user_date
from .handlers_validators import return_to_start

@bot.message_handler(commands=['show_records'])
def handle_show_records(message):
    """
    Команда show records
    Бот высылает сообщение c просьбой ввести дату для поиска
    Отправляет пользователя на следующий шаг -> show_records_by_date

    :param message: команда show records
    """
    bot.send_message(message.chat.id,
                'Я сохраняю данные твоего сна! '
                    'Какая дата тебя интересует (в формате DD-MM-YYYY)?')
    bot.register_next_step_handler(message, show_records_by_date)


def wrong_date_format_error_bot(message: Message, next_step):
    bot.send_message(message.chat.id, '❌ Неверный формат даты. Попробуй ещё раз (DD-MM-YYYY).')
    bot.register_next_step_handler(message, next_step)
    return

def wrong_time_format_error_bot(message: Message, next_step):
    bot.send_message(message.chat.id, '❌ Неверный формат времени. Попробуй ещё раз (HH-MM).')
    bot.register_next_step_handler(message, next_step)
    return

def record_not_found_error_bot(message: Message, next_step):
    bot.send_message(message.chat.id, 'Записей не найдено.')
    bot.register_next_step_handler(message, next_step)
    return


def show_records_by_date(message: Message) -> None:
    """
    Бот выдает информацию о сне
    :param message: Message: ввод пользователя
    :return: None, бот выдает информацию о ползьзователе
    """

    user_id = message.from_user.id
    search_date = parse_user_date(message.text)

    records_found = load_records_by_date(user_id, search_date)

    if not search_date:
        wrong_date_format_error_bot(message, show_records_by_date)

    if not records_found:
        record_not_found_error_bot(message, return_to_start)

    for record in records_found:
        sleep_time_str = record['sleep_time'].strftime('%d-%m-%Y %H:%M')
        wake_time_str = record['wake_time'].strftime('%d-%m-%Y %H:%M')

        duration = convert_duration(record["duration"])

        message_to_send = []
        message_to_send.append(
        f'💤 Сон: {sleep_time_str}\n'
        f'⏰ Пробуждение: {wake_time_str}\n'
        f'🛌 Длительность: {duration['hrs']} ч {duration['min']} мин\n'
        f'⭐ Качество: {record["sleep_quality"]}\n'
        f'📝 Заметки: {record["notes"]}\n'
    )

        bot.send_message(message.chat.id, "\n".join(message_to_send))

