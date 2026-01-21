from functools import wraps
from bot import bot
from telebot import TeleBot
from telebot.types import Message
from errors_validators import InvalidFormatError, OutOfRangeError, validate_nums_in_range

def find_record_by_number(message: Message, user_sessions) -> int | None:
    """
    Удаляет запись  в базе данных sleepbot.db по ее номеру в списке. Использует временный словарь user_sessions

    :return: dict: id записи, которую нужно удалить или изменить
    """
    user_id = message.from_user.id
    records_found = user_sessions[user_id].get('records_found', [])

    if not records_found:
        record_not_found_error_bot(message, find_record_by_number)

    choice = validate_num_input_bot(message, find_record_by_number, 0, len(records_found))

    record_id = records_found[choice -  1]['record_id']

    return record_id

def wrong_date_format_error_bot(message: Message, next_step):
    """Сообщение об ошибке в формате даты"""

    bot.send_message(message.chat.id, '❌ Неверный формат даты или дата в будущем. Попробуй ещё раз (DD-MM-YYYY).')
    bot.register_next_step_handler(message, next_step)
    return

def wrong_time_format_error_bot(message: Message, next_step):
    """Сообщение об ошибке в формате времени"""

    bot.send_message(message.chat.id, '❌ Неверный формат времени. Попробуй ещё раз (HH-MM).')
    bot.register_next_step_handler(message, next_step)
    return

def record_not_found_error_bot(message: Message, next_step):
    """Сообщение, что запись не найдена"""

    bot.send_message(message.chat.id, 'Записей не найдено.')
    bot.register_next_step_handler(message, next_step)
    return


def validate_num_input_bot(message: Message, next_step, start: int, end: int):
    """Проверяет ввод числа и переводит пользователя на следующий шаг."""

    try:
        num = validate_nums_in_range(message.text, start, end)
        next_step(message, num)
    except InvalidFormatError as e:
        bot.send_message(message.chat.id, f'❌ {str(e)}')
        bot.register_next_step_handler(message, lambda m: validate_num_input_bot(m, next_step, start, end))
    except OutOfRangeError as e:
        bot.send_message(message.chat.id, f'❌ {str(e)}')
        bot.register_next_step_handler(message, lambda m: validate_num_input_bot(m, next_step, start, end))



def return_to_start(message: Message):
    """Returns to start page"""
    from .start import start_menu
    start_menu(message)


