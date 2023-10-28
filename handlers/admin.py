# -------------- Импорт функций --------------
import asyncio
import config

# -------------- Импорт локальных функций --------------
from handlers import client, other
from mcrcons import admin_rc, other_rc
from create_bot import bot, dp
from data_base import sqlite_db
from keyboards import admin_kb, client_kb

# -------------- Импорт модулей Aiogram --------------
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

# -------------- Переменные --------------
is_monitoring = False

# -------------- Вспомогательные функции --------------
async def admin__source__on_startup():
    '''
    Управление мониторингом сервера
    :return: Отсылает сообщение в чат админам
    '''
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(text='Запустить', callback_data='monitoring on'),
        InlineKeyboardButton(text='Остановить', callback_data='monitoring off')
    )
    data = await sqlite_db.user__database__user_check_all(
        column='isadmin',
        val='yes'
    )
    for ret in data:
        await bot.send_message(chat_id=ret[1],
                               text='Мониторинг игроков.',
                               reply_markup=keyboard)
        print(f'Админ {ret[1]} @{ret[2]} оповещён о том, что можно включить мониторинг игроков.')

async def admin__source__user_isnt_admin(user_id, exception):
    '''
    Предупреждение о ошибке активации админ мода
    :param user_id: Telegram ID пользователя
    :param exception: Ошибка
    :type user_id: int
    :return: Рассылка сообщений
    '''
    isadmin = await sqlite_db.user__database__user_check_one(
        line='isadmin',
        column='user_id',
        val=user_id
    )
    if isadmin == 'yes' and (str(exception) == "name 'ID' is not defined"):
        await bot.send_message(
            chat_id=user_id,
            text='Вы не вошли в админ мод!'
        )
        print(f'Пользователь {user_id} не вошел в админ мод перед использованием команд.')
    elif isadmin == 'not' and (str(exception) == "name 'ID' is not defined"):
        await bot.send_message(
            caht_id=user_id,
            text='Вы не админ!'
        )
        print(f'Пользователь {user_id} не является админом, но пытается выполнить его команды.')
    elif isadmin == '' and (str(exception) == "name 'ID' is not defined"):
        await bot.send_message(
            caht_id=user_id,
            text='Вы ещё не зарегистрировались.\n'
                 'Сделайте это с помощью команды "Регистрация никнейм_из_майнкрафта".\n'
                 'Затем используй /help для получения списка команд.'
        )
        print(f'Пользователь {user_id} не зарегистрировался, но пытался выполнить команды админа.')
    else:
        return False

async def admin__source__for_exception(user_id, username, exception, val):
    data = await admin__source__user_isnt_admin(
        user_id=user_id,
        exception=exception
    )
    if data != False:
        return
    else:
        await other.other__source__user_alert(
            user_id=user_id,
            username=username,
            type='exception',
            val=val,
            exception=exception
        )

async def admin__source__for_else(user_id, tg_name, val):
    await bot.send_message(
        chat_id=user_id,
        text='Вы не админ!',
        reply_markup=client_kb.kb_help_client
    )
    print(f'Пользователь {user_id} @{tg_name} пытался выполнить команду админа "{val}".')

# -------------- CallBack функции --------------

# Одобрение завяки с помощью коллбэка
async def admin__callback__application_accept(query: types.CallbackQuery):
    username = await sqlite_db.user__database__user_check_one(
        line='username',
        column='user_id',
        val=query.data[19:]
    )
    try:
        response = await admin_rc.admin__rc__whitelist_add(username)
        if response == 'Player is already whitelisted':
            await bot.send_message(
                query.from_user.id,
                text=f'Игрок {username} уже находится в вайтлисте.'
            )
            print(f'Админ {query.from_user.id} пытался добавить в вайтлист уже присутствующего там игрока {query.data[19:]} {username}.')
        elif response == f'Added {username} to the whitelist':
            await bot.send_message(
                query.from_user.id,
                text=f'Игрок {username} добавлен в вайтлист.'
            )
            print(f'Админ {query.from_user.id} добавил в вайтлист игрока {query.data[19:]} {username}.')
        if username:
            await sqlite_db.user__database__user_set_approval(
                user_id=query.data[19:],
                val='yes'
            )
            print(f'Админ {query.from_user.id} одобряет заявку пользователя {query.data[19:]} {username}.')
            await query.answer(
                text='Одобрено.',
                show_alert=True
            )
            await other.other__source__user_alert(
                user_id=query.data[19:],
                type='approval',
                val='одобрена'
            )
            data = await sqlite_db.user__database__user_check_all(
                column='approval',
                val='not'
            )
            amount = len(data)
            if amount != 0:
                await bot.send_message(
                    chat_id=query.from_user.id,
                    text=f'Количество оставшихся заявок: {amount}.'
                )
                print(f'Админ {query.from_user.id} оповещён, что количество оставшихся заявок: {amount}.')
                await admin__handler__admin_requests(query)
            else:
                await bot.send_message(
                    chat_id=query.from_user.id,
                    text='Больше заявок не осталось.'
                )
                print(f'Админ {query.from_user.id} оповещён, что больше заявок не осталось.')
        else:
            await bot.send_message(
                chat_id=query.from_user.id,
                text=f'Пользователь {query.data[19:]} уже находится в базе данных.'
            )
    except Exception as exception:
        if await other_rc.other__rc__server_online():
            await other.other__source__user_alert(
                user_id=query.from_user.id,
                username=query.from_user.username,
                type='exception',
                val='admin__callback__application_accept',
                exception=exception
            )
        else:
            print(
                f'Админ {query.from_user.id} @{query.from_user.username} обратился с коммандой "whitelist add" к выключенному серверу.')
            await query.answer(
                text='Сервер оффлайн!',
                show_alert=True
            )
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )

# Отклонение заявки с помощью коллбэка
async def admin__callback__application_reject(query: types.CallbackQuery):
    await sqlite_db.user__database__user_set_approval(
        user_id=query.data[19:],
        val='ban'
    )
    await query.answer(
        text='Отклонено.',
        show_alert=True
    )
    await other.other__source__user_alert(
        user_id=query.data[19:],
        type='approval',
        val='отклонена'
    )
    print(f'Пользователь {query.data[19:]} получает отклонение заявки от админа {query.from_user.id}.')
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )

# Мониторинг игроков на сервере
async def admin__callback__players_monitoring(query: types.CallbackQuery):
    global is_monitoring
    if not is_monitoring:
        is_monitoring = True
        await query.answer(
            text='Вы запустили мониторинг.',
            show_alert=True
        )
        print(f'Админ {query.from_user.id} включил мониторинг игроков.')
        await bot.delete_message(
            chat_id=query.from_user.id,
            message_id=query.message.message_id
        )
        player_pr = []
        while True:
            response = ''
            player_rn = await admin_rc.admin__rc__players_list()
            if len(player_pr) < len(player_rn):
                player_new = [item for item in player_rn if item not in player_pr]
                if len(player_new) == 1:
                    response = f'К серверу присоединился: {player_new[0]}.'
                elif len(player_new) > 1:
                    response = 'К серверу присоеднились:'
                    for val in player_new:
                        response += f' {val},'
                    response = f'{response[:-1]}.'
            elif len(player_pr) > len(player_rn):
                player_quited = [item for item in player_pr if item not in player_rn]
                if len(player_quited) == 1:
                    response = f'Сервер покинул: {player_quited[0]}.'
                elif len(player_quited) > 1:
                    response = 'Сервер покинули:'
                    for val in player_quited:
                        response += f' {val},'
                    response = f'{response[:-1]}.'
            elif len(player_pr) == len(player_rn) and player_pr != player_rn:
                player_new = [item for item in player_rn if item not in player_pr]
                player_quited = [item for item in player_pr if item not in player_rn]
                if len(player_new) == 1:
                    response += f'К серверу присоединился: {player_new[0]}.'
                elif len(player_new) > 1:
                    response += 'К серверу присоеднились:'
                    for val in player_new:
                        response += f' {val},'
                    response = f'{response[:-1]}.'
                if len(player_quited) == 1:
                    response += f'Сервер покинул: {player_quited[0]}.'
                elif len(player_quited) > 1:
                    response += 'Сервер покинули:'
                    for val in player_quited:
                        response += f' {val},'
                    response = f'{response[:-1]}.'
            if response:
                data = await sqlite_db.user__database__user_check_all(
                    column='isadmin',
                    val='yes',
                    line='user_id'
                )
                for ret in data:
                    await bot.send_message(ret[0], text=f'{response}')
                print(response)
            player_pr = player_rn
            await asyncio.sleep(30)
    else:
        await query.answer(
            text='Уже работает.',
            show_alert=True
        )
        print(f'Админ {query.from_user.id} попытался включить уже запущенный мониторинг игроков.')
    await bot.delete_message(query.from_user.id, query.message.message_id)

# -------------- Handler функции --------------

# Проверка на присутствие админа в базе данных и добавление его туда в случае отстутствия
async def admin__handler__admin_activate(message: types.Message):
    global ID
    data_isadmin = await sqlite_db.user__database__user_check_one(
        line='isadmin',
        column='user_id',
        val=message.from_user.id
    )
    data_approval = await sqlite_db.user__database__user_check_one(
        line='approval',
        column='user_id',
        val=message.from_user.id
    )
    if data_isadmin == 'yes':
        ID = message.from_user.id
        await bot.send_message(message.from_user.id,
                               text='Админ мод включен.\n'
                                    'Что будем делать?',
                               reply_markup=admin_kb.kb_main_admin)
        print(f'Пользователь {message.from_user.id} @{message.from_user.username} входит в режим админа.')
    else:
        if data_approval == 'yes':
            await sqlite_db.admin__database__admin_add(message.from_user.id)
            ID = message.from_user.id
            await bot.send_message(message.from_user.id,
                                   text='Вы стали админом.\n'
                                        'Что будем делать?',
                                   reply_markup=admin_kb.kb_main_admin)
            print(f'Пользователь {message.from_user.id} @{message.from_user.username} получает права админа.')
        else:
            await client.client__handler__user_start(message)
            print(f'Пользователь {message.from_user.id} @{message.from_user.username} не зарегистрировался, но пытался получить права админа.')
    await message.delete()

# Добавление пользователя в вайтлист
async def admin__handler__admin_requests(message: types.Message):
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user__database__user_check_all(
                column='approval',
                val='not'
            )
            try:
                data_user = data[0]
            except:
                data_user = []
            if len(data_user):
                user_id = data_user[1]
                tgname = data_user[2]
                username = data_user[3]
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=f'{user_id} @{tgname} {username}',
                    reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton('Одобрить',callback_data=f'accept_application {user_id}'),
                                                            InlineKeyboardButton('Отклонить', callback_data=f'reject_application {user_id}'))
                )
                print(f'Админ {message.from_user.id} @{message.from_user.username} просмотрел заявку пользователя {user_id} @{tgname}.')
            else:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Неподтвержденных заявок не осталось.'
                )
                print(f'Админ {message.from_user.id} @{message.from_user.username} просмотрел пустой список заявок.')
        else:
            await admin__source__for_else(
                user_id=message.from_user.id,
                tg_name=message.from_user.username,
                val='Просмотреть заявки'
            )
    except Exception as exception:
        await admin__source__for_exception(
            user_id=message.from_user.id,
            username=message.from_user.username,
            exception=exception,
            val='admin__handler__admin_requests'
        )

# Удаление пользователя из базы данных
async def admin__handler__user_remove(message: types.Message):
    try:
        if message.from_user.id == ID:
            if len(message.text) <= 21:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Напишите в формате "Удалить пользователя id"'
                )
                print(f'Админ {message.from_user.id} @{message.from_user.username} использовал неполную команду удаления пользователя.')
            else:
                username = await sqlite_db.user__database__user_check_one(
                    line='username',
                    column='user_id',
                    val=message.text[21:]
                )
                tgname = await sqlite_db.user__database__user_check_one(
                    line='tgname',
                    column='user_id',
                    val=message.text[21:]
                )
                try:
                    response = await admin_rc.admin__rc__whitelist_remove(username)
                    if response == 'Player is not whitelisted':
                        print(f'Админ {message.from_user.id} @{message.from_user.username} пытался удалить из вайтлиста отсутсвующего там игрока {message.text[21:]} {username}.')
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text='Игрок не находится в вайтлисте.'
                        )
                    elif response == f'Removed {username} from the whitelist':
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text=f'Игрок {username} удален из вайтлиста.'
                        )
                        print(f'Админ {message.from_user.id} @{message.from_user.username} удалил из вайтлиста игрока {message.text[21:]} {username}.')
                    if username:
                        await sqlite_db.admin__database__user_remove(
                            user_id=int(message.text[21:])
                        )
                        print(f'Админ {message.from_user.id} @{message.from_user.username} удалил из базы данных пользователя {message.text[21:]} {tgname}.')
                        await other.other__source__user_alert(
                            user_id=message.text[21:],
                            username=tgname,
                            type='user_delete',
                            admin_id=message.from_user.id
                        )
                    else:
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text=f'Пользователь {message.text[21:]} не находится в базе данных.'
                        )
                        print(f'Админ {message.from_user.id} попытался удалить из базы данных отсутсвуеющего там игрока {message.text[21:]}.')
                except Exception as exception:
                    if await other_rc.other__rc__server_online():
                        await other.other__source__user_alert(
                            user_id=message.from_user.id,
                            username=message.from_user.username,
                            type='exception',
                            val='admin__handler__user_remove',
                            exception=exception
                        )
                    else:
                        print(f'Админ {message.from_user.id} @{message.from_user.username} обратился с коммандой "whitelist remove" к выключенному серверу.')
                        await message.answer(
                            text='Сервер оффлайн!'
                        )
        else:
            await admin__source__for_else(
                user_id=message.from_user.id,
                tg_name=message.from_user.username,
                val='Удалить пользователя'
            )
    except Exception as exception:
        await admin__source__for_exception(
            user_id=message.from_user.id,
            username=message.from_user.username,
            exception=exception,
            val='admin__handler__user_remove'
        )

# Получение списка пользователей с одобренными заявками
async def admin__handler__user_approved_list(message: types.Message):
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user__database__user_check_all(
                column='approval',
                val='yes'
            )
            amount = len(data)
            if amount != 0:
                response = '**Пользователи**\n'
                for ret in data:
                    response += f'Telegram тег: @{ret[2]}\n Telegram ID: {ret[1]}\n Minecraft ник: {ret[3]}\n Время регистрации: {ret[0]}\n Является админом: {ret[5]}\n\n'
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=response
                )
                print(f'Админ {message.from_user.id} @{message.from_user.username} просмотрел список подтвержденных пользователей из {amount} человек.')
        else:
            await admin__source__for_else(
                user_id=message.from_user.id,
                tg_name=message.from_user.username,
                val='Список игроков'
            )
    except Exception as exception:
        await admin__source__for_exception(
            user_id=message.from_user.id,
            username=message.from_user.username,
            exception=exception,
            val='admin__handler__user_approved_list'
        )

# Получение списка пользователей с отклоненными заявками
async def admin__handler__user_banned_list(message: types.Message):
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user__database__user_check_all(
                column='approval',
                val='ban'
            )
            amount = len(data)
            if amount != 0:
                response = '**Черный список**\n'
                for ret in data:
                    response += f'Telegram тег: @{ret[2]}\n Telegram ID: {ret[1]}\n Minecraft ник: {ret[3]}\n Время регистрации: {ret[0]}\n Является админом: {ret[5]}\n\n'
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=response
                )
                print(f'Админ {message.from_user.id} @{message.from_user.username} просмотрел список забаненных пользователей из {amount} человек.')
            else:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Тут пока никого нет',
                    reply_markup=admin_kb.kb_main_admin
                )
                print(
                    f'Админ {message.from_user.id} @{message.from_user.username} просмотрел пустой список забаненных пользователей.')
        else:
            await admin__source__for_else(
                user_id=message.from_user.id,
                tg_name=message.from_user.username,
                val='ЧС'
            )
    except Exception as exception:
        await admin__source__for_exception(
            user_id=message.from_user.id,
            username=message.from_user.username,
            exception=exception,
            val='admin__handler__user_banned_list'
        )

# Оповещение всех пользователей о чем-то
async def admin__handler__user_notify(message: types.Message):
    try:
        if message.from_user.id == ID:
            if message.text[11:] == '':
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Напишите в формате:\n'
                         'Оповестить "текст вашего сообщения".'
                )
                print(f'Админ {message.from_user.id} @{message.from_user.username} использовал неполную команду "Оповестить".')
            else:
                data = await sqlite_db.user__database__user_check_all(
                    column='approval',
                    val='yes',
                    line='user_id'
                )
                response = message.text[11:]
                if response[-1] == '.' or response[-1] == '!' or response[-1] == '?':
                    dot = ''
                elif response[-1] == ',' or response[-1] == '\\' or response[-1] == '>' or response[-1] == '<':
                    response[-1] = '.'
                else:
                    dot = '.'
                if response[0].islower():
                    response = response[0].upper() + response[1:]
                for ret in data:
                    try:
                        await bot.send_message(
                            chat_id=ret[0],
                            text=f'Важное увдомление!\n'
                                 f'{response}{dot}'
                        )
                    except:
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text=f'Пользователь {ret[0]} заблокировал бота и не может получить сообщение.'
                        )
                print(f'Админ {message.from_user.id} @{message.from_user.username} выполнил команду "Оповестить" с текстом "{response}"')
        else:
            await admin__source__for_else(
                user_id=message.from_user.id,
                tg_name=message.from_user.username,
                val='Оповестить'
            )
    except Exception as exception:
        await admin__source__for_exception(
            user_id=message.from_user.id,
            username=message.from_user.username,
            exception=exception,
            val='admin__handler__user_notify'
        )

async def admin__handler__players_monitoring(message: types.Message):
    try:
        if message.from_user.id == ID:
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton(text='Запустить', callback_data='monitoring on'),
                InlineKeyboardButton(text='Остановить', callback_data='monitoring off')
            )
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Мониторинг игроков.',
                reply_markup=keyboard
            )
            print(f'Админ {message.from_user.id} @{message.from_user.username} вызвал конмаду "Мониторинг".')
        else:
            await admin__source__for_else(
                user_id=message.from_user.id,
                tg_name=message.from_user.username,
                val='Мониторинг'
            )
    except Exception as exception:
        await admin__source__for_exception(
            user_id=message.from_user.id,
            username=message.from_user.username,
            exception=exception,
            val='admin__handler__players_monitoring'
        )

def register_handlers_admin(dp: Dispatcher):
    dp.register_callback_query_handler(admin__callback__application_accept, lambda x: x.data.startswith('accept_application'))
    dp.register_callback_query_handler(admin__callback__application_reject, lambda x: x.data.startswith('reject_application'))
    dp.register_callback_query_handler(admin__callback__players_monitoring, lambda x: x.data.startswith('monitoring'))
    dp.register_message_handler(admin__handler__admin_activate, commands=['Admin'], is_chat_admin=True)
    dp.register_message_handler(admin__handler__user_banned_list, Text('ЧС'))
    dp.register_message_handler(admin__handler__players_monitoring, Text('Мониторинг'))
    dp.register_message_handler(admin__handler__admin_requests, Text('Просмотреть заявки'))
    dp.register_message_handler(admin__handler__user_approved_list, Text('Список пользователей'))
    dp.register_message_handler(admin__handler__user_remove, Text(startswith='Удалить пользователя'))
    dp.register_message_handler(admin__handler__user_notify, Text(startswith='Оповестить'))
