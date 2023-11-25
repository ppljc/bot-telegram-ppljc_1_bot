from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from data_base import sqlite_db

kma1 = KeyboardButton('Удалить пользователя')
kma2 = KeyboardButton('Просмотреть заявки')
kma3 = KeyboardButton('Список пользователей')
kma4 = KeyboardButton('Оповестить')
kma5 = KeyboardButton('ЧС')
kma6 = KeyboardButton('Мониторинг')
kma7 = KeyboardButton('Команда')
kma8 = KeyboardButton('Забанить')
kb_main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
kb_main_admin.add(kma1, kma2, kma3)
kb_main_admin.add(kma4, kma5, kma6)
kb_main_admin.add(kma7, kma8)

kim1 = InlineKeyboardButton(text='Запустить', callback_data='monitoring on')
kim2 = InlineKeyboardButton(text='Остановить', callback_data='monitoring off')
kb_inline_monitoring = InlineKeyboardMarkup()
kb_inline_monitoring.row(kim1, kim2)