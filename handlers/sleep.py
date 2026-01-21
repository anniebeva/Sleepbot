from bot import bot, user_sessions
from telebot.types import Message
import datetime

from database import add_sleep_record
from .handlers_validators import return_to_start, validate_num_input_bot


@bot.message_handler(commands=['sleep'])
def handle_sleep_cmd(message: Message) -> None:
    """
    Команда sleep сохраняет время отхода ко сну в dict user_sessions
    :param message: команда sleep
    :return: None, сохраняет время во временный словарь user_sessions
    """
    user_id = message.from_user.id
    name = message.from_user.first_name
    sleep_time = datetime.datetime.now()

    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    user_sessions[user_id]['sleep_time'] = sleep_time

    bot.send_message(message.chat.id,
                f'Спокойной Ночи, {name}! '
                     'Не забудь сообщить мне, когда проснешься, командой /wake')


@bot.message_handler(commands=['wake'])
def handle_wake_cmd(message: Message) -> None:
    """
    Команда wake сохраняет время, когда пользователь проснулся в dict user_sessions
    Завершает сессию, если пользователь ранее не ввел время отхода ко сну
    :param message: команда wake
    :return: None, сохраняет время во временный словарь user_sessions
    :print: message от бота, сообщая о времени сна
    """
    user_id = message.from_user.id
    name = message.from_user.first_name
    wake_time = datetime.datetime.now()

    if user_sessions[user_id]['sleep_time'] is None:
        bot.send_message(message.chat.id,
                    'Ты уснул так быстро, что забыл указать время. '
                        'Поэтому мы не можем проанализировать сон в эту ночь.')
        bot.register_next_step_handler(message, return_to_start)

    else:
        sleep_time = user_sessions[user_id].get('sleep_time')
        duration = wake_time - sleep_time

        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        user_sessions[user_id]['wake_time'] = wake_time

        bot.send_message(message.chat.id,
                    f'Доброе утро {name}! Ты проспал(а) {int(hours):02d} час(ов) {int(minutes):02d} минут(ы) и {int(seconds):02d} секунд(ы). '
                         f'Не забудь оценить качество сна /quality (1-10) и оставить дополнительные заметки /notes')


@bot.message_handler(commands=['quality'])
def handle_quality_cmd(message: Message) -> None:
    """
    Команда quality
    Бот высылает сообщение об оценке и отправляет пользователя на следующий шаг -> record_quality

    :param message: команда quality
    """
    bot.send_message(message.chat.id, 'Оцени качество сна 1-10')
    bot.register_next_step_handler(message, record_quality)


def record_quality(message: Message) -> None:
    '''
    Принимает сообщение от пользователя с оценкой качества сна,
    проверяет wake_time и вызывает validate_num_input_bot.
    '''

    user_id = message.from_user.id

    if user_sessions[user_id]['wake_time'] is None:
        bot.send_message(message.chat.id, 'Не забудь указать, что ты проснулся')
        bot.register_next_step_handler(message, handle_wake_cmd)
        return

    validate_num_input_bot(message, next_step=save_quality, start=1, end=10)


def save_quality(message: Message, quality: int) -> None:
    '''
    Сохраняет проверенную оценку сна и отправляет сообщение пользователю.
    '''

    user_id = message.from_user.id
    user_sessions[user_id]['quality'] = quality

    if quality < 5:
        msg = ('Очень жаль, что не получилось выспаться. '
               'Не забудь оставить заметку /notes, это поможет стремиться к здоровому сну!')
    else:
        msg = ('Спасибо за оценку качества сна! '
               'Есть ли дополнительные комментарии? Можешь всегда поделиться в /notes')

    bot.send_message(message.chat.id, msg)


def add_sleep_rec_to_db_get_id(user_id: int) -> int:
    """
    Добавляет все записи в таблицу sleep_records в БД sleepbot.db
    Очищает временный словарь user_sessions

    :param user_id: id пользователя
    :return: record_id для дальнейшего использования в таблице Notes
    """
    sleep_time = user_sessions[user_id]['sleep_time']
    wake_time = user_sessions[user_id]['wake_time']
    quality = user_sessions[user_id]['quality']
    record_id = add_sleep_record(user_id, sleep_time, wake_time, quality)
    user_sessions.pop(user_id, None)
    return record_id