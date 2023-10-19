from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from data_base import sqlite_db

kma1 = KeyboardButton('Удалить пользователя')
kma2 = KeyboardButton('Просмотреть заявки')
kma3 = KeyboardButton('Список пользователей')
kma4 = KeyboardButton('ЧС')
kb_main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
kb_main_admin.row(kma1, kma2, kma3, kma4)

