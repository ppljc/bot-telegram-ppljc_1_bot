from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from data_base import sqlite_db

kma1 = KeyboardButton('Удалить пользователя')
kma2 = KeyboardButton('Просмотреть заявки')
kma3 = KeyboardButton('Список пользователей')
kma4 = KeyboardButton('Оповестить')
kma5 = KeyboardButton('ЧС')
kma6 = KeyboardButton('Мониторинг')
kb_main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
kb_main_admin.add(kma1, kma2, kma3)
kb_main_admin.add(kma4, kma5, kma6)
