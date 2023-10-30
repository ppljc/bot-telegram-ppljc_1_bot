from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

kc1 = KeyboardButton('Статус')
kc2 = KeyboardButton('Проблема')
kc3 = KeyboardButton('Поддержать')
kc4 = KeyboardButton('/help')
kc5 = KeyboardButton('Добавить карту на сервер')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.row(kc1, kc2, kc3, kc4).row(kc5)

khl1 = KeyboardButton('/help')
kb_help_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_help_client.add(khl1)

kcp1 = KeyboardButton('Проблема you are not whitelisted on this server')
kcp2 = KeyboardButton('/help')
kb_client_problem = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_problem.row(kcp1, kcp2)

kcc1 = KeyboardButton('Отмена')
kb_client_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_cancel.add(kcc1)

def generate_inline_kb(amount: int, txt_dict: list, row_width: int):
    kb = InlineKeyboardMarkup(row_width=row_width)
    for i in range(amount):
        kb.insert(InlineKeyboardButton(text=f"{txt_dict[i]}", callback_data=f"{i}"))
    return kb