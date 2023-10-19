import config
from mcrcons import admin_rc
from create_bot import bot, dp
from keyboards import admin_kb, client_kb
from data_base import sqlite_db

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

# -------------- Вспомогательные функции --------------

# Предупреждение о ошибке при активации админ мода
async def admin_source_warning(user_id):
    if await sqlite_db.user_check('isadmin', 'user_id', user_id) == 'yes':
        await bot.send_message(user_id, text='Вы не вошли в админ мод!')
        print(f'Пользователь {user_id} не вошел в админ мод перед использованием команд.')
    elif await sqlite_db.user_check('isadmin', 'user_id', user_id) == 'not':
        await bot.send_message(user_id, text='Вы не админ!')
        print(f'Пользователь {user_id} не является админом, но пытается выполнить его команды.')
    elif await sqlite_db.user_check('isadmin', 'user_id', user_id) == 0:
        await bot.send_message(user_id, text='Вы ещё не зарегистрировались.\n' \
                                             'Сделайте это с помощью команды "Регистрация никнейм_из_майнкрафта".\n' \
                                             'Затем используй /help для получения списка команд.')
        print(f'Пользователь {user_id} не зарегистрировался, но пытался выполнить команды админа.')

# Сообщение о активации админ мода
async def admin_source_activate(message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Админ мод включен.\n' \
                                                 'Что будем делать?', reply_markup=admin_kb.kb_main_admin)
    await message.delete()

# Проверка на наличие заявок помимо рассматриваемой
async def admin_source_requests(message, user_id, val):
    await bot.send_message(user_id, text=f'Ваша заявка на регистрацию {val}.')
    if await sqlite_db.user_list('approval', 'not', 'user_id') != 0:
        amount = len(await sqlite_db.user_list('approval', 'not'))
        await bot.send_message(message.from_user.id, text=f'Количество оставшихся заявок: {amount}.')
        print(f'Админу {message.from_user.id} сообщено, что количество оставшихся заявок: {amount}.')
        return 1
    else:
        await bot.send_message(message.from_user.id, text='Больше заявок не осталось.')
        print(f'Админу {message.from_user.id} сообщено, что больше заявок не осталось.')

async def admin_source_alert(admin_id, user_id, type):
    if type == 'delete':
        for ret in await sqlite_db.user_list('isadmin', 'yes', 'user_id'):
            if ret[0] != admin_id:
                await bot.send_message(ret[0], text=f'Админ {admin_id} удалил пользователя {user_id}.')
                print(f'Админ {ret[0]} оповещён о том, что админ {admin_id} удалил пользователя {user_id}.')

# -------------- CallBack функции --------------

# Одобрение завяки с помощью коллбэка
async def on_accept_application(query: types.CallbackQuery):
    username = await sqlite_db.user_check('username', 'user_id', query.data[19:])
    try:
        response = await admin_rc.add_whitelist(query.from_user.id, username)
        await admin_rc.add_whitelist(query.from_user.id, username)
        if response == 'Player is not whitelisted':
            print(f'Админ {query.from_user.id} пытался удалить из вайтлиста отсутсвующего там игрока {username}.')
            await bot.send_message(message.from_user.id, text='Игрок не находится в вайтлсите.')
        elif response == f'Removed {username} from the whitelist':
            print(f'Админ {query.from_user.id} удалил из вайтлиста игрока {username}.')
            await bot.send_message(message.from_user.id, text=f'Игрок {username} удален из вайтлиста.')
    except:
        print(f'Админ {query.from_user.id} обратился с коммандой whitelist add к выключенному серверу.')
        await query.answer(text='Сервер оффлайн!', show_alert=True)
        return
    await sqlite_db.user_approval('yes', query.data[19:])
    await query.answer(text='Одобрено.', show_alert=True)
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await admin_source_requests(query, query.data[19:], 'одобрена')
    print(f'Пользователь {query.data[19:]} получает одобрение заявки от админа {query.from_user.id}.')

# Отклонение заявки с помощью коллбэка
async def on_reject_application(query: types.CallbackQuery):
    await query.answer(text='Отклонено.', show_alert=True)
    await sqlite_db.user_approval('ban', query.data[19:])
    print(f'Пользователь {query.data[19:]} получает отклонение заявки от админа {query.from_user.id}.')
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await admin_source_requests(query, query.data[19:], 'отклонена')

# -------------- Handler функции --------------

# Проверка на присутствие админа в базе данных и добавление его туда в случае отстутствия
async def admin_activate(message: types.Message):
    if await sqlite_db.user_check('isadmin', 'user_id', message.from_user.id) == 'yes':
        await admin_source_activate(message)
        print(f'Пользователь с Telegram ID {message.from_user.id} входит в режим админа.')
    else:
        await sqlite_db.admin_add(message.from_user.id)
        await admin_source_activate(message)
        print(f'Пользователь с Telegram ID {message.from_user.id} получает права админа.')

# Добавление пользователя в вайтлист
async def admin_requests(message: types.Message):
    try:
        if message.from_user.id == ID:
            if await sqlite_db.user_check('user_id', 'approval', 'not') != 0:
                ret = str(await sqlite_db.user_check('user_id', 'approval', 'not'))
                await bot.send_message(message.from_user.id, text=ret, reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton('Одобрить', callback_data=f'accept_application {ret}'), InlineKeyboardButton('Отклонить', callback_data=f'reject_application {ret}')))
                print(f'Админ {message.from_user.id} просмотрел заявку пользователя {ret}.')
            else:
                await bot.send_message(message.from_user.id, text='Неподтвержденных заявок не осталось.')
                print(f'Админ {message.from_user.id} просмотрел пустой список заявок.')
        else:
            await bot.send_message(message.from_user.id, text='Вы не админ!')
            print(f'Пользователь {message.from_user.id} пытался выполнить команду админа "Посмотреть заявки".')
    except:
        await admin_source_warning(message.from_user.id)

# Удаление пользователя из базы данных
async def admin_removal(message: types.Message):
    try:
        if message.from_user.id == ID:
            if len(message.text) <= 21:
                await bot.send_message(message.from_user.id, text='Напишите в формате "Удалить пользователя id"')
                print(f'Админ {message.from_user.id} использовал неполную команду удаления пользователя.')
            else:
                username = await sqlite_db.user_check('username', 'user_id', message.text[21:])
                try:
                    response = await admin_rc.rem_whitelist(message.from_user.id, username)
                    if response == 'Player is not whitelisted':
                        print(f'Админ {message.from_user.id} пытался удалить из вайтлиста отсутсвующего там игрока {username}.')
                        await bot.send_message(message.from_user.id, text='Игрок не находится в вайтлисте.')
                    elif response == f'Removed {username} from the whitelist':
                        print(f'Админ {message.from_user.id} удалил из вайтлиста игрока {username}.')
                        await bot.send_message(message.from_user.id, text=f'Игрок {username} удален из вайтлиста.')
                except Exception as e:
                    print(e)
                    print(f'Админ {message.from_user.id} обратился с коммандой whitelist remove к выключенному серверу.')
                    await message.answer(text='Сервер оффлайн!', show_alert=True)
                    return
                await sqlite_db.admin_delete(int(message.text[21:]))
                await bot.send_message(message.text[21:], text='Мы сожалеем, но вы были удалены из базы данных сервера.', reply_markup=client_kb.kb_help_client)
                await bot.send_message(message.from_user.id, text=f'Пользователь {message.text[21:]} удалён.')
                await admin_source_alert(message.from_user.id, message.text[21:], 'delete')
                print(f'Админ {message.from_user.id} удалил пользователя {message.text[21:]}.')
        else:
            await bot.send_message(message.from_user.id, text='Вы не админ!')
            print(f'Пользователь {message.from_user.id} пытался выполнить команду админа "Удалить пользователя".')
    except:
        await admin_source_warning(message.from_user.id)

# Получение списка пользователей
async def admin_userslist(message: types.Message):
    try:
        if message.from_user.id == ID:
            if await sqlite_db.user_list('approval', 'yes') != 0:
                response = '**Пользователи:**\n'
                for ret in (await sqlite_db.user_list('approval', 'yes')):
                    response += f'Telegram тег: @{ret[2]}\n Telegram ID: {ret[1]}\n Minecraft ник: {ret[3]}\n Время регистрации: {ret[0]}\n Является админом: {ret[5]}\n\n'
                await bot.send_message(message.from_user.id, text=response)
                print(f'Админ {message.from_user.id} просмотрел список подтвержденных пользователей из {len(await sqlite_db.user_list("approval", "yes"))} человек.')
        else:
            await bot.send_message(message.from_user.id, text='Вы не админ!')
            print(f'Пользователь {message.from_user.id} пытался выполнить команду админа "Список игроков".')
    except:
        await admin_source_warning(message.from_user.id)

async def admin_bannedlist(message: types.Message):
    try:
        if message.from_user.id == ID:
            if await sqlite_db.user_list('approval', 'ban') != 0:
                response = '**Черный список:**\n'
                for ret in (await sqlite_db.user_list('approval', 'ban')):
                    response += f'Telegram тег: @{ret[2]}\n Telegram ID: {ret[1]}\n Minecraft ник: {ret[3]}\n Время регистрации: {ret[0]}\n Является админом: {ret[5]}\n\n'
                await bot.send_message(message.from_user.id, text=response)
                print(f'Админ {message.from_user.id} просмотрел список забаненных пользователей из {len(await sqlite_db.user_list("approval", "ban"))} человек.')
        else:
            await bot.send_message(message.from_user.id, text='Вы не админ!')
            print(f'Пользователь {message.from_user.id} пытался выполнить команду админа "ЧС".')
    except:
        await admin_source_warning(message.from_user.id)

def register_handlers_admin(dp: Dispatcher):
    dp.register_callback_query_handler(on_accept_application, lambda x: x.data.startswith('accept_application'))
    dp.register_callback_query_handler(on_reject_application, lambda x: x.data.startswith('reject_application'))
    dp.register_message_handler(admin_activate, commands=['Admin'], is_chat_admin=True)
    dp.register_message_handler(admin_requests, Text('Просмотреть заявки'))
    dp.register_message_handler(admin_removal, Text(startswith='Удалить пользователя'))
    dp.register_message_handler(admin_userslist, Text('Список пользователей'))
    dp.register_message_handler(admin_bannedlist, Text('ЧС'))
    # dp.register_message_handler(admin_update, commands=['Update'])
