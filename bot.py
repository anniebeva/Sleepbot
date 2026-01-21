import telebot
from telebot import TeleBot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN=os.getenv('TELEGRAM_API_KEY')
bot = telebot.TeleBot(TOKEN)
user_sessions = {}
