from bot import bot
from telebot.types import Message
from helpers import convert_duration, load_records_by_date, format_date_for_output
from errors_validators import parse_user_date
from db import show_full_stats
from .handlers_validators import record_not_found_error_bot, wrong_date_format_error_bot, return_to_start

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
        return

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


@bot.message_handler(commands=['show_sleep_statistics'])
def handle_stat_cmd(message:Message):
    user_id = message.from_user.id
    stat_data = show_full_stats(user_id)
    if not stat_data:
        bot.send_message(message.chat.id, 'Нет данных для статистики 💤')
        return

    avg_duration = convert_duration(stat_data['avg_duration'])
    max_duration = convert_duration(stat_data['max_duration'])
    min_duration = convert_duration(stat_data['min_duration'])
    max_duration_date = format_date_for_output(stat_data['max_duration_date'])
    min_duration_date = format_date_for_output(stat_data['min_duration_date'])
    max_quality_date = format_date_for_output(stat_data['max_quality_date'])
    min_quality_date = format_date_for_output(stat_data['min_quality_date'])

    message_to_send = [
        '🕖 Продолжительность сна\n'
        f'⚖️ Средняя продолжительность сна: {avg_duration['hrs']} ч {avg_duration['min']} мин\n'
        f'🔺 Максимальная продолжительность сна ({max_duration_date}): {max_duration['hrs']} ч {max_duration['min']} мин\n'
        f'🔻 Минимальная продолжительность сна ({min_duration_date}): {min_duration['hrs']} ч {min_duration['min']} мин\n'
        '\n💫 Качество сна\n'
        f'⚖️ Среднее качество: {stat_data['avg_quality']}\n'
        f'🔺 Лучшее качество сна ({max_quality_date}): {stat_data['max_quality']}\n'
        f'🔻 Худшее качество сна ({min_quality_date}): {stat_data['min_quality']}'
    ]

    bot.send_message(message.chat.id, "\n".join(message_to_send))
