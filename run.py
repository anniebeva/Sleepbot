"""
run.py - Точка входа в приложение. Поддерживает два режима:
- Вебхуки (для продакшена на Render)
- Поллинг (для локальной разработки)
"""

import os
import logging
from flask import Flask, request
import telebot

# Инициализация базы данных (таблицы и SQL-функции создаются при старте)
from database.init_db import init_db

# Импорт всех хендлеров
import handlers.start
import handlers.edit
import handlers.stats
import handlers.notes
import handlers.show
import handlers.delete
import handlers.sleep

# --- Переменные окружения ---
TOKEN = os.getenv('TELEGRAM_API_KEY')
if not TOKEN:
    raise ValueError("❌ TELEGRAM_API_KEY не задан")

# --- Инициализация бота и Flask-приложения ---
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- Создание таблиц и функций БД при старте ---
init_db()


# --- Вебхук (точка входа для Telegram) ---
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    """
    Обрабатывает входящие обновления от Telegram.
    :return: 'OK' при успехе, 'ERROR' при ошибке
    """
    try:
        json_string = request.stream.read().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        logging.error(f"Ошибка в вебхуке: {e}")
        return "ERROR", 500


# --- Health check для пингов (необязательно) ---
@app.route('/')
def health():
    """
    Проверка работоспособности сервиса. Возвращает 'OK'.
    """
    return "OK", 200


def set_webhook():
    """
    Устанавливает вебхук для бота на основе RENDER_EXTERNAL_HOSTNAME.
    :return: True если вебхук установлен, False если переменная не задана
    """
    bot.remove_webhook()
    host = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    if not host:
        logging.warning("RENDER_EXTERNAL_HOSTNAME не задан, вебхук не устанавливается")
        return False
    webhook_url = f"https://{host}/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    logging.info(f"✅ Вебхук установлен: {webhook_url}")
    return True


# --- Точка входа ---
if __name__ == '__main__':
    use_webhook = os.getenv('USE_WEBHOOK', 'false').lower() == 'true'
    if use_webhook:
        # Режим продакшена: запуск Flask-сервера с вебхуком
        set_webhook()
        port = int(os.getenv('PORT', 10000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Режим локальной разработки: поллинг
        logging.info("Запускаем polling (локально)")
        bot.polling(none_stop=True)