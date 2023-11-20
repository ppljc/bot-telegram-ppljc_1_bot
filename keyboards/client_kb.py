from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

kc1 = KeyboardButton('Статус')
kc2 = KeyboardButton('Проблема')
kc3 = KeyboardButton('Поддержать')
kc4 = KeyboardButton('/help')
kc5 = KeyboardButton('Добавить карту')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
kb_client.row(kc1, kc2, kc3, kc4, kc5)

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

kcc1 = KeyboardButton('Отмена')
kb_client_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_cancel.add(kcc1)

def kbgen_inline_Format(ratio):
    kb_inline_format = InlineKeyboardMarkup(row_width=4)
    for i in range(1, 5):
        ratio_button = f'{ratio[0] * i}:{ratio[1] * i}'
        ratio_callback = f'{ratio[0] * i} {ratio[1] * i}'
        kb_inline_format.insert(InlineKeyboardButton(text=f'{ratio_button}', callback_data=f'scale {ratio_callback}'))
    return kb_inline_format