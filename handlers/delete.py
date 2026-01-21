from bot import bot, user_sessions
from telebot.types import Message

from .handlers_validators import record_not_found_error_bot, wrong_date_format_error_bot, \
    find_record_by_number, return_to_start
from helpers import load_records_by_date
from errors_validators import parse_user_date

from .show import show_records_by_date
from database import delete_record

@bot.message_handler(commands=['delete_record'])
def handle_delete_record(message: Message) -> None:
    """
    Команда update records
    Бот высылает сообщение c просьбой ввести дату для поиска
    Отправляет пользователя на следующий шаг -> update_record

    :param message: команда show records
    """
    bot.send_message(message.chat.id,
                'Да, конечно, давай удалим запись' 
                    'Какая дата тебя интересует (в формате DD-MM-YYYY)?')
    bot.register_next_step_handler(message, delete_record_by_date)

def delete_record_by_date(message: Message) -> None:
    """
    Бот позволяет удалить информацию о сне за конкретную дату
    Если за данную дату несколько записаей, выводит их и запрашивает номер для удаления

    :param message: Message: ввод пользователя Даты для изменений
    :return: None, бот выдает информацию о ползьзователе

    #пока что удаляет по дате, можно наверное сделать полный краткий список всех records и удалять по номеру
    """

    user_id = message.from_user.id
    search_date = parse_user_date(message.text)
    records_found = load_records_by_date(user_id, search_date)

    if not search_date:
        wrong_date_format_error_bot(message, show_records_by_date)

    if not records_found:
        record_not_found_error_bot(message, return_to_start)

    if len(records_found) == 1:
        record_id = records_found[0]['record_id']
        delete_record(record_id)
        bot.send_message(message.chat.id, 'Запись удалена!')

    else:
        message_to_send = []
        for i, record in enumerate(records_found):
            message_to_send.append(
                f'Запись {i + 1}\n'
                f'💤 Сон: {record["sleep_time"]}\n'
                f'⏰ Пробуждение: {record["wake_time"]}\n'
                f'⭐ Качество: {record["sleep_quality"]}\n'
                f'📝 Заметки: {record["notes"]}\n'
            )
        bot.send_message(message.chat.id, 'Какую именно запись ты хочешь удалить? Введи номер:\n'
                         + '\n'.join(message_to_send))

        user_sessions[user_id] = {'records_found': records_found}
        bot.register_next_step_handler(message, delete_record_by_number)

def delete_record_by_number(message:Message) -> None:
    """
    Получает номер записи и удаляет ее из базы данных
    :param message: выбор пользователя
    :return:  None, удаляет запись
    """
    record_id = find_record_by_number(message, user_sessions)
    if record_id:
        delete_record(record_id)
        bot.send_message(message.chat.id, 'Запись удалена!')
        user_sessions.pop(message.from_user.id, None)