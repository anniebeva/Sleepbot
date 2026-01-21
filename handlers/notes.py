from bot import bot

from telebot.types import Message

from .handlers_validators import return_to_start
from .sleep import add_sleep_rec_to_db_get_id
from database import add_note


@bot.message_handler(commands=['notes'])
def handle_notes_cmd(message):
    """
    Команда notes
    Бот высылает сообщение c просьбой добавить заметки
    Отправляет пользователя на следующий шаг -> record_quality

    :param message: команда notes
    """
    bot.send_message(message.chat.id, 'Оставь заметки для более здорового сна в будущем!')
    bot.register_next_step_handler(message, record_notes)


def record_notes(message: Message) -> None:
    """
    Получает и добавляет заметки от пользователя в таблицу notes БД sleepbot.db

    :param message: Message: telegram сообщение от пользователя с заметками
    :return: None: сохранет заметки в таблицу notes по record_id
    """
    user_id = message.from_user.id

    try:
        record_id = add_sleep_rec_to_db_get_id(user_id)
    except ValueError:
        bot.send_message(message.chat.id, 'No record found')
        bot.register_next_step_handler(message, return_to_start)
        return

    note = message.text
    add_note(record_id, note)

    bot.send_message(message.chat.id,'Заметки сохранены. Хорошего дня!')
