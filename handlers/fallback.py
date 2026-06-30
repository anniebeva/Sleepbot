from bot import bot, user_sessions
from telebot.types import Message

@bot.message_handler(commands=['help'])
def help_command(message: Message):
    """
    Выводит список доступных команд.
    """
    bot.send_message(
        message.chat.id,
        "📋 Доступные команды:\n"
        "/start: главное меню\n"
        "/sleep: записать сон\n"
        "/stats: статистика сна\n"
        "/view: посмотреть записи за дату\n"
        "/edit: редактировать запись\n"
        "/delete: удалить запись\n"
        "/help: показать это сообщение"
    )

@bot.message_handler(func=lambda message: True)
def catch_all(message: Message):
    """
    Срабатывает для любых сообщений, которые не были обработаны другими хендлерами.
    - Если пользователь в диалоге – игнорируем (не мешаем).
    - Если сообщение начинается с '/' считаем неизвестной командой.
    - Иначе просто не поняли.
    """
    user_id = message.from_user.id

    if user_id in user_sessions and 'state' in user_sessions[user_id]:
        return

    text = message.text or ""

    if text.startswith('/'):
        bot.send_message(
            message.chat.id,
            "❓ Неизвестная команда.\n"
            "Используйте /start для главного меню или /help для списка команд."
        )
    else:
        bot.send_message(
            message.chat.id,
            "🤔 Извините, я не понял ваше сообщение.\n"
            "Пожалуйста, используйте кнопки меню или введите /start для начала."
        )
