# Локальные модули
from create_bot import db


# Функции
async def user_data(user_id: int, formatted: bool = False):
    response = await db.read(
        line='*',
        column='user_id',
        value=user_id
    )
    if response:
        response = response[0]

    if not formatted:
        if not response:
            response = ['', user_id, '', '']
        data = {
            'date': response[0],
            'user_id': response[1],
            'nickname': response[2],
            'approval': response[3]
        }
    else:
        if not response:
            data = (
                f'Пользователь не зарегистрирован в боте!\n'
                f'• Telegram ID: <a href="tg://user?id={user_id}">{user_id}</a>'
            )
        else:
            data = (
                f'Зарегистрирован: {response[0]}\n'
                f'• Telegram ID: <a href="tg://user?id={user_id}">{response[1]}</a>\n'
                f'• Minecraft ник: {response[2]}\n'
                f'• Статус заявки: {response[3]}'
            )
    return data
