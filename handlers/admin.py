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
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# -------------- Переменные --------------
is_monitoring = False

# -------------- Вспомогательные функции --------------
async def admin_source_OnStartUp():
    '''
    Управление мониторингом сервера
    :return: Отсылает сообщение в чат админам
    '''
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(text='Запустить', callback_data='monitoring on'),
        InlineKeyboardButton(text='Остановить', callback_data='monitoring off')
    )
    isadmin = await sqlite_db.user_database_UserCheckAll(
        line='id',
        column='isadmin',
        val='yes'
    )
    for ret in isadmin:
        await bot.send_message(chat_id=ret[0],
                               text='Мониторинг игроков.',
                               reply_markup=keyboard)
        print(f'{ret[0]} оповещён о том, что можно включить мониторинг игроков.')

async def admin_source_UserIsntAdmin(id, exception):
    '''
    Предупреждение о ошибке активации админ мода
    :param id: id from telegram
    :param exception: exception
    :return: Рассылка сообщений
    '''
    isadmin = await sqlite_db.user_database_UserCheckOne(
        line='isadmin',
        column='id',
        val=id
    )
    if isadmin[0] == 'yes' and (str(exception) == "name 'ID' is not defined"):
        await bot.send_message(
            chat_id=id,
            text='Вы не вошли в админ мод!'
        )
        print(f'Пользователь {id} не вошел в админ мод перед использованием команд.')
    elif isadmin[0] == 'not' and (str(exception) == "name 'ID' is not defined"):
        await bot.send_message(
            caht_id=id,
            text='Вы не админ!'
        )
        print(f'Пользователь {id} не является админом, но пытается выполнить его команды.')
    elif isadmin[0] == '' and (str(exception) == "name 'ID' is not defined"):
        await bot.send_message(
            caht_id=id,
            text='Вы ещё не зарегистрировались.\n'
                 'Сделайте это с помощью команды "Регистрация никнейм_из_майнкрафта".\n'
                 'Затем используй /help для получения списка команд.'
        )
        print(f'Пользователь {id} не зарегистрировался, но пытался выполнить команды админа.')
    else:
        return False

async def admin_source_ForException(id, exception, function):
    data = await admin_source_UserIsntAdmin(
        id=id,
        exception=exception
    )
    if data != False:
        return
    else:
        await other.other_source_UserAlert(
            id=id,
            type='exception',
            filename='admin.py',
            function=function,
            exception=exception
        )

async def admin_source_ForElse(id, username, val):
    await bot.send_message(
        chat_id=id,
        text='Вы не админ!',
        reply_markup=client_kb.kb_help_client
    )
    print(f'Пользователь {id} {username} пытался выполнить команду админа "{val}".')

# -------------- CallBack функции --------------

# Одобрение завяки с помощью коллбэка
async def admin_callback_ApplicationAccept(query: types.CallbackQuery):
    nickname = await sqlite_db.user_database_UserCheckOne(
        line='nickname',
        column='id',
        val=query.data[19:]
    )
    try:
        response = await admin_rc.admin_rc_Whitelist(
            nickname=nickname,
            type='add'
        )
        if response == 'Player is already whitelisted':
            await bot.send_message(
                query.from_user.id,
                text=f'Игрок {nickname} уже находится в вайтлисте.'
            )
            print(f'Админ {query.from_user.id} пытался добавить в вайтлист уже присутствующего там игрока {query.data[19:]} {nickname}.')
        elif response == f'Added {nickname} to the whitelist':
            await bot.send_message(
                query.from_user.id,
                text=f'Игрок {nickname} добавлен в вайтлист.'
            )
            print(f'Админ {query.from_user.id} добавил в вайтлист игрока {query.data[19:]} {nickname}.')
        if nickname:
            await sqlite_db.user_database_UserSetApproval(
                id=query.data[19:],
                val='yes'
            )
            print(f'Админ {query.from_user.id} одобряет заявку пользователя {query.data[19:]} {nickname}.')
            await query.answer(
                text='Одобрено.',
                show_alert=True
            )
            await other.other_source_UserAlert(
                id=query.data[19:],
                filename='admin.py',
                type='approval_yes',
                function='admin_callback_ApplicationAccept',
                exception='',
                admin_id=query.from_user.id
            )
            data = await sqlite_db.user_database_UserCheckAll(
                line='*',
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
                await admin_handler_AdminRequests(query)
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
        if await other_rc.other_rc_ServerOnline():
            await other.other_source_UserAlert(
                id=query.from_user.id,
                type='exception',
                filename='admin.py',
                function='admin_callback_ApplicationAccept',
                exception=exception
            )
        else:
            print(f'Админ {query.from_user.id} {query.from_user.username} обратился с коммандой "whitelist add" к выключенному серверу.')
            await query.answer(
                text='Сервер оффлайн!',
                show_alert=True
            )
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )

# Отклонение заявки с помощью коллбэка
async def admin_callback_ApplicationReject(query: types.CallbackQuery):
    await sqlite_db.user_database_UserSetApproval(
        id=query.data[19:],
        val='ban'
    )
    await query.answer(
        text='Отклонено.',
        show_alert=True
    )
    await other.other_source_UserAlert(
        id=query.data[19:],
        type='approval_ban',
        filename='admin.py',
        function='admin_callback_ApplicationReject',
        exception=query,
        admin_id=query.from_user.id
    )
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )

# Мониторинг игроков на сервере
async def admin_callback_PlayersMonitoringOn(query: types.CallbackQuery):
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
            player_rn = await admin_rc.admin_rc_ListPlayers()
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
                data = await sqlite_db.user_database_UserCheckAll(
                    column='isadmin',
                    val='yes',
                    line='id'
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
async def admin_handler_AdminActivation(message: types.Message):
    global ID
    chat_id = f'{message.chat.id}'[1:]
    if chat_id == '832082275' or chat_id == '648541799':
        data = await other.other_source_UserData(id=message.from_user.id)
        if data['isadmin'] == 'yes':
            ID = message.from_user.id
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Админ мод включен.\n'
                     'Что будем делать?',
                reply_markup=admin_kb.kb_main_admin
            )
            print(f'Пользователь {message.from_user.id} {message.from_user.username} входит в режим админа.')
        else:
            if data['approval'] == 'yes':
                await sqlite_db.admin_database_AdminAdd(id=message.from_user.id)
                ID = message.from_user.id
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Вы стали админом.\n'
                         'Что будем делать?',
                    reply_markup=admin_kb.kb_main_admi)
                nickname = data['nickname']
                data_op = await admin_rc.admin_rc_Op(
                    nickname=nickname,
                    type=''
                )
                if data_op == 'Nothing changed. The player already is an operator':
                    await bot.send_message(
                        chat_id=message.from_user.id,
                        text='Вы уже являетесь оператором сервера.',
                        reply_markup=admin_kb.kb_main_admin
                    )
                    print(f'Пользователь {message.from_user.id} {nickname} попытался стать оператором сервера, хоть им уже является.')
                elif data_op == f'Made {nickname} a server operator':
                    await bot.send_message(
                        chat_id=message.from_user.id,
                        text='Теперь вы являетесь оператором сервера.',
                        reply_markup=admin_kb.kb_main_admin
                    )
                    print(f'Пользователь {message.from_user.id} {nickname} стал оператором сервера.')
                print(f'Пользователь {message.from_user.id} {message.from_user.username} получает права админа.')
            else:
                await client.client_handler_UserStart(message)
                print(f'Пользователь {message.from_user.id} {message.from_user.username} не зарегистрировался, но пытался получить права админа.')
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text='Ага, пососите)'
        )
    await message.delete()

async def admin_handler_AdminRequests(message: types.Message):
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user_database_UserCheckAll(
                line='*',
                column='approval',
                val='not'
            )
            try:
                data_user = data[0]
            except:
                data_user = []
            if len(data_user):
                id = data_user[1]
                username = data_user[2]
                nickname = data_user[3]
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=f'{id} {username} {nickname}',
                    reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton('Одобрить',callback_data=f'accept_application {id}'),
                                                            InlineKeyboardButton('Отклонить', callback_data=f'reject_application {id}')),
                    parse_mode=ParseMode.MARKDOWN
                )
                print(f'Админ {message.from_user.id} {message.from_user.username} просмотрел заявку пользователя {id} {username}.')
            else:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Неподтвержденных заявок не осталось.'
                )
                print(f'Админ {message.from_user.id} {message.from_user.username} просмотрел пустой список заявок.')
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                username=message.from_user.username,
                val='Просмотреть заявки'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_AdminRequests'
        )

# Удаление пользователя из базы данных
async def admin_handler_UserRemove(message: types.Message):
    try:
        if message.from_user.id == ID:
            if len(message.text) <= 21:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Напишите в формате "Удалить пользователя id"'
                )
                print(f'Админ {message.from_user.id} {message.from_user.username} использовал неполную команду удаления пользователя.')
            else:
                data = await sqlite_db.user_database_UserCheckOne(
                    line='*',
                    column='id',
                    val=message.text[21:]
                )
                try:
                    response_wl = await admin_rc.admin_rc_Whitelist(
                        nickname=data[3],
                        type='remove'
                    )
                    response_op = await admin_rc.admin_rc_Op(
                        nickname=data[3],
                        type='de'
                    )
                    if response_wl == 'Player is not whitelisted':
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text='Игрок не находится в вайтлисте.'
                        )
                        print(f'Админ {message.from_user.id} {message.from_user.username} пытался удалить из вайтлиста отсутсвующего там игрока {data[2]} {data[3]}.')
                    elif response_wl == f'Removed {data[3]} from the whitelist':
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text=f'Игрок {data[3]} удален из вайтлиста.'
                        )
                        print(f'Админ {message.from_user.id} {message.from_user.username} удалил из вайтлиста игрока {data[2]} {data[3]}.')
                    if nickname:
                        await sqlite_db.admin_database_UserRemove(id=int(data[2]))
                        await other.other_source_UserAlert(
                            id=data[2],
                            type='user_delete',
                            filename='admin.py',
                            function='admin_handler_UserRemove',
                            exception='',
                            admin_id=message.from_user.id
                        )
                    else:
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text=f'Пользователь {data[2]} не находится в базе данных.'
                        )
                        print(f'Админ {message.from_user.id} попытался удалить из базы данных отсутсвуеющего там игрока {data[2]}.')
                    if response_op == 'Nothing changed. The player is not an operator':
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text=f'Админ {data[2]} не являлся оператором сервера.',
                            reply_markup=admin_kb.kb_main_admin
                        )
                        print(f'Админ {message.from_user.id} попытался забрать отсутствующие у админа {data[4]} права оператора.')
                    elif response_op == f'Made {data[3]} no longer a server operator':
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text=f'Пользователь {data[3]} больше не оператор сервера.',
                            reply_markup=admin_kb.kb_main_admin
                        )
                        print(f'Админ {message.from_user.id} забрал у админа {data[4]} права оператора.')
                except Exception as exception:
                    if await other_rc.other_rc_ServerOnline():
                        await other.other_source_UserAlert(
                            id=message.from_user.id,
                            type='exception',
                            filename='admin.py',
                            function='admin_handler_UserRemove',
                            exception=exception
                        )
                    else:
                        print(f'Админ {message.from_user.id} {message.from_user.username} обратился с коммандой "whitelist remove" к выключенному серверу.')
                        await message.answer(
                            text='Сервер оффлайн!'
                        )
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                username=message.from_user.username,
                val='Удалить пользователя'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserRemove'
        )

# Получение списка пользователей с одобренными заявками
async def admin_handler_UserListApproved(message: types.Message):
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user_database_UserCheckAll(
                line='*',
                column='approval',
                val='yes'
            )
            amount = len(data)
            if amount != 0:
                response = '**Пользователи**\n'
                for ret in data:
                    response += f'Аккаунт: {ret[2]}\n Telegram ID: {ret[1]}\n Minecraft ник: {ret[3]}\n Время регистрации: {ret[0]}\n Является админом: {ret[5]}\n\n'
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=response,
                    parse_mode=ParseMode.MARKDOWN
                )
                print(f'Админ {message.from_user.id} {message.from_user.username} просмотрел список подтвержденных пользователей из {amount} человек.')
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                username=message.from_user.username,
                val='Список игроков'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserListApproved'
        )

# Получение списка пользователей с отклоненными заявками
async def admin_handler_UserListBanned(message: types.Message):
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user_database_UserCheckAll(
                column='approval',
                val='ban'
            )
            amount = len(data)
            if amount != 0:
                response = '**Черный список**\n'
                for ret in data:
                    response += f'Telegram тег: {ret[2]}\n Telegram ID: {ret[1]}\n Minecraft ник: {ret[3]}\n Время регистрации: {ret[0]}\n Является админом: {ret[5]}\n\n'
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=response
                )
                print(f'Админ {message.from_user.id} {message.from_user.username} просмотрел список забаненных пользователей из {amount} человек.')
            else:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Тут пока никого нет',
                    reply_markup=admin_kb.kb_main_admin
                )
                print(
                    f'Админ {message.from_user.id} {message.from_user.username} просмотрел пустой список забаненных пользователей.')
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                username=message.from_user.username,
                val='ЧС'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserListBanned'
        )

# Оповещение всех пользователей о чем-то
async def admin_handler_UserNotify(message: types.Message):
    try:
        if message.from_user.id == ID:
            if message.text[11:] == '':
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Напишите в формате:\n'
                         'Оповестить "текст вашего сообщения".'
                )
                print(f'Админ {message.from_user.id} {message.from_user.username} использовал неполную команду "Оповестить".')
            else:
                data = await sqlite_db.user_database_UserCheckAll(
                    column='approval',
                    val='yes',
                    line='id'
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
                    await bot.send_message(
                        chat_id=ret[0],
                        text=f'Важное увeдомление!\n'
                             f'{response}{dot}'
                    )
                print(f'Админ {message.from_user.id} {message.from_user.username} выполнил команду "Оповестить" с текстом "{response}"')
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                username=message.from_user.username,
                val='Оповестить'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserNotify'
        )

async def admin_handler_PlayersMonitoring(message: types.Message):
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
            print(f'Админ {message.from_user.id} {message.from_user.username} вызвал конмаду "Мониторинг".')
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                username=message.from_user.username,
                val='Мониторинг'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_PlayersMonitoring'
        )

def register_handlers_admin(dp: Dispatcher):
    dp.register_callback_query_handler(admin_callback_ApplicationAccept, lambda x: x.data.startswith('accept_application'))
    dp.register_callback_query_handler(admin_callback_ApplicationReject, lambda x: x.data.startswith('reject_application'))
    dp.register_callback_query_handler(admin_callback_PlayersMonitoringOn, lambda x: x.data.startswith('monitoring'))
    dp.register_message_handler(admin_handler_AdminActivation, commands=['Admin'], is_chat_admin=True, )
    dp.register_message_handler(admin_handler_UserListBanned, Text('ЧС'))
    dp.register_message_handler(admin_handler_PlayersMonitoring, Text('Мониторинг'))
    dp.register_message_handler(admin_handler_AdminRequests, Text('Просмотреть заявки'))
    dp.register_message_handler(admin_handler_UserListApproved, Text('Список пользователей'))
    dp.register_message_handler(admin_handler_UserRemove, Text(startswith='Удалить пользователя'))
    dp.register_message_handler(admin_handler_UserNotify, Text(startswith='Оповестить'))
