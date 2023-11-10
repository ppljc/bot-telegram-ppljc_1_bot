from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kc1 = KeyboardButton('Статус')
kc2 = KeyboardButton('Проблема')
kc3 = KeyboardButton('Поддержать')
kc4 = KeyboardButton('/help')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.row(kc1, kc2, kc3, kc4)

khl1 = KeyboardButton('/help')
kb_help_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_help_client.add(khl1)

kcp1 = KeyboardButton('Проблема you are not whitelisted on this server')
kcp2 = KeyboardButton('/help')
kb_client_problem = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_problem.row(kcp1, kcp2)

kcpn = KeyboardButton('Отправить номер телефона', request_contact=True)
kb_client_phonenumber = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_phonenumber.add(kcpn)