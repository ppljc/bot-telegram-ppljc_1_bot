from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kc1 = KeyboardButton('Статус')
kc2 = KeyboardButton('Проблема')
kc3 = KeyboardButton('/help')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.row(kc1, kc2, kc3)

khl1 = KeyboardButton('/help')
kb_help_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_help_client.row(khl1)

kcp1 = KeyboardButton('Проблема you are not whitelisted on this server')
kb_client_problem = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_problem.row(kcp1)