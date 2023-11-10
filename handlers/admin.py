# -------------- Импорт функций --------------
import asyncio
import datetime
import emoji

# -------------- Импорт локальных функций --------------
from handlers import client, other
from mcrcons import bot_rc
from create_bot import bot, dp
from data_base import sqlite_db
from keyboards import admin_kb, client_kb

# -------------- Импорт модулей Aiogram --------------
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# -------------- Переменные --------------
is_monitoring = False
filename = 'admin.py'

# -------------- Вспомогательные функции --------------
async def admin_source_OnStartUp():
    '''
    Управление мониторингом сервера
    :return: Отсылает сообщение в чат админам
    '''
    list_admins = await sqlite_db.user_database_UserCheckAll(
        line='id',
        column='isadmin',
        val='yes'
    )
    for ret in list_admins:
        await bot.send_message(
            chat_id=ret[0],
            text='Мониторинг игроков.',
            reply_markup=admin_kb.kb_inline_monitoring
        )
        await other.other_source_Logging(
            id=ret[0],
            filename=filename,
            function='admin_source_OnStartUp',
            exception='',
            content='Оповещён, что можно включить мониторинг.'
        )

async def admin_source_ForException(id, exception, function):
    if str(exception) == "name 'ID' is not defined":
        data = await other.other_source_UserData(
            id=id,
            formatted=False
        )
        message = ''
        message_logging = ''
        keyboard = client_kb.kb_help_client
        if data['isadmin'] == 'yes':
            message = 'Вы не вошли в админ мод!'
            message_logging = 'Не вошёл в админ мод, перед использованием команды.'
            keyboard = client_kb.kb_client
        elif data['isadmin'] == 'not':
            message = 'Вы не админ!'
            message_logging = 'Не является админом, но пытается выполнить его команды.'
            keyboard = client_kb.kb_client
        elif data['isadmin'] == '':
            message = (
                'Вы ещё не зарегистрировались.\n'
                'Сделайте это с помощью команды "Регистрация никнейм_из_майнкрафта".\n'
                'Затем используй /help для получения списка команд.'
            )
            message_logging = 'Не зарегистрировался, но пытается выполнить команды админа'
            keyboard = ReplyKeyboardRemove
        await bot.send_message(
            chat_id=id,
            text=message,
            reply_markup=keyboard
        )
        await other.other_source_Logging(
            id=id,
            filename=filename,
            function=function,
            exception='',
            content=message_logging
        )
    else:
        await other.other_source_UserAlert(
            id=id,
            type='exception',
            filename='admin.py',
            function=function,
            exception=exception
        )

async def admin_source_ForElse(id, function):
    data = await other.other_source_UserData(
        id=id,
        formatted=False
    )
    await bot.send_message(
        chat_id=id,
        text='Вы не админ!',
        reply_markup=client_kb.kb_help_client
    )
    await other.other_source_Logging(
        id=id,
        filename=filename,
        function=function,
        exception='',
        content='Пытался вызвать эту команду.'
    )

# -------------- CallBack функции --------------
async def admin_callback_ApplicationAccept(query: types.CallbackQuery):
    '''
    Одобрение заявки на регистрацию от пользователя
    :param query:
    :return:
    '''
    # Обозначаем переменные id админа и пользователя
    id = query.data[19:]
    admin_id = query.from_user.id
    # Получаем отформатированную и неотформатированную информацию о пользователе и админе
    data = await other.other_source_UserData(
        id=id,
        formatted=False
    )
    data_formatted = await other.other_source_UserData(
        id=id,
        formatted=True
    )
    data_admin = await other.other_source_UserData(
        id=admin_id,
        formatted=False
    )
    data_admin_formatted = await other.other_source_UserData(
        id=admin_id,
        formatted=True
    )
    try:
        # wl в названии переменных сокращение от whitelist
        # sa - сокращение set approval
        # Добавление в whitelist
        response_wl = await bot_rc.bot_rc_Universal(command=f'whitelist add {data["nickname"]}')
        if response_wl == 'Player is already whitelisted':
            message_wl = f'Пользователь уже находится в белом списке {emoji.emojize(":cross_mark:")}'
            message_wl_logging = f'Пытался добавить в белый список присутствующего там игрока {data}'
        elif response_wl == f'Added {data["nickname"]} to the whitelist':
            message_wl = f'Пользователь добавлен в белый список {emoji.emojize(":check_mark:")}'
            message_wl_logging = f'Добавил в белый список игрока {data}'
        # Изменение статуса завяки в базе данных
        response_sa = await sqlite_db.user_database_UserSetApproval(
            id=id,
            val='yes'
        )
        # Сообщение админу результатов вышеперечисленных действий
        await bot.send_message(
            chat_id=admin_id,
            text=f'{data_formatted}\n\n'
                 f'{message_wl}\n\n'
                 f'Пользователь добавлен в базу данных {emoji.emojize(":check_mark:")}',
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        await other.other_source_Logging(
            id=admin_id,
            filename=filename,
            function='admin_callback_ApplicationAccept',
            exception='',
            content=f'{message_wl_logging}. | Одобряет заявку на регистрацию от {data}.'
        )
        # Сообщение пользователю, что его заявка одобрена
        await other.other_source_UserAlert(
            id=id,
            filename=filename,
            type='approval_yes',
            function='admin_callback_ApplicationAccept',
            exception='',
            admin_id=admin_id
        )
        # Отправляем админа смотреть следующие заявки
        await admin_handler_AdminRequests(query)
    except Exception as exception:
        # Если сервер онлайн, то используем опопвещение об ошибке
        if await bot_rc.bot_rc_ServerOnline():
            await other.other_source_UserAlert(
                id=query.from_user.id,
                type='exception',
                filename='admin.py',
                function='admin_callback_ApplicationAccept',
                exception=exception
            )
        # Если сервер оффлайн, то сообщаем админу об этом
        else:
            await bot.send_message(
                chat_id=admin_id,
                text='Сервер оффлайн.',
            )
            await other.other_source_Logging(
                id=admin_id,
                filename=filename,
                function='admin_callback_ApplicationAccept',
                exception='Server is offline.',
                content=''
            )
    # Удаляем сообщение в котором отражены данные заявки на регистрацию
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )

async def admin_callback_ApplicationReject(query: types.CallbackQuery):
    '''
    Отклонение заявки на регистрацию
    :param query:
    :return:
    '''
    id = query.data[19:]
    admin_id = query.from_user.id
    # Получаем отформатированную и неотформатированную информацию о пользователе и админе
    data = await other.other_source_UserData(
        id=id,
        formatted=False
    )
    data_formatted = await other.other_source_UserData(
        id=id,
        formatted=True
    )
    data_admin = await other.other_source_UserData(
        id=admin_id,
        formatted=False
    )
    data_admin_formatted = await other.other_source_UserData(
        id=admin_id,
        formatted=True
    )
    # Устанаваливаем статус заявки пользователя в базе данных
    await sqlite_db.user_database_UserSetApproval(
        id=id,
        val='ban'
    )
    await other.other_source_UserAlert(
        id=id,
        type='approval_ban',
        filename='admin.py',
        function='admin_callback_ApplicationReject',
        exception='',
        admin_id=admin_id
    )
    # Оповещаем админа о успешности вышеперечисленных действий
    await bot.send_message(
        chat_id=admin_id,
        text=f'{data_formatted}\n\n'
             f'Заявка пользователя отклонена {emoji.emojize(":check_mark:")}',
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
    await other.other_source_Logging(
        id=admin_id,
        filename=filename,
        function='admin_callback_ApplicationReject',
        exception='',
        content=f'Одобряет заявку на регистрацию от {data}.'
    )
    # Удаляем сообщение в котором отражены данные заявки на регистрацию
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )

async def admin_callback_PlayersMonitoringOn(query: types.CallbackQuery):
    '''
    Включаем мониторинг игроков на майнкрафт сервере
    :param query:
    :return:
    '''
    global is_monitoring
    if not is_monitoring:
        await bot.delete_message(
            chat_id=query.from_user.id,
            message_id=query.message.message_id
        )
        if await bot_rc.bot_rc_ServerOnline():
            await bot.send_message(
                chat_id=query.from_user.id,
                text=f'Мониторинг запущен.',
            )
            await other.other_source_Logging(
                id=query.from_user.id,
                filename=filename,
                function='admin_callback_PlayersMonitoringOn',
                exception='',
                content='Запустил мониторинг сервера.'
            )
            is_monitoring = True
        else:
            await other.other_source_UserAlert(
                id=query.from_user.id,
                type='server_offline',
                filename=filename,
                function='admin_callback_PlayersMonitoringOn',
                exception=''
            )
            return
        player_pr = []
        while True:
            response = ''
            try:
                player_rn = await bot_rc.admin_rc_ListPlayers()
            except:
                await other.other_source_UserAlert(
                    id=query.from_user.id,
                    type='server_offline',
                    filename=filename,
                    function='admin_callback_PlayersMonitoringOn',
                    exception='monitoring'
                )
                is_monitoring = False
                return
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
                    response += f' Сервер покинул: {player_quited[0]}.'
                elif len(player_quited) > 1:
                    response += ' Сервер покинули:'
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
                    await bot.send_message(ret[0], text=response)
                await other.other_source_Logging(
                    id=000000,
                    filename=filename,
                    function='admin_callback_PlayersMonitoringOn',
                    exception='',
                    content=response
                )
            player_pr = player_rn
            await asyncio.sleep(30)
    else:
        await bot.send_message(
            chat_id=query.from_user.id,
            text='Мониторинг уже работает.'
        )
        await other.other_source_Logging(
            id=query.from_user.id,
            filename=filename,
            function='admin_callback_PlayersMonitoringOn',
            exception='Monitoring is already enabled',
            content=''
        )
        await bot.delete_message(
            chat_id=query.from_user.id,
            message_id=query.message.message_id
        )

# -------------- Handler функции --------------

# Проверка на присутствие админа в базе данных и добавление его туда в случае отстутствия
async def admin_handler_AdminActivation(message: types.Message):
    global ID
    chat_id = f'{message.chat.id}'[1:]
    if chat_id == '832082275' or chat_id == '648541799':
        data = await other.other_source_UserData(
            id=message.from_user.id,
            formatted=False
        )
        if data['isadmin'] == 'yes':
            ID = message.from_user.id
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Админ мод включен.\n'
                     'Что будем делать?',
                reply_markup=admin_kb.kb_main_admin
            )
            await other.other_source_Logging(
                id=message.from_user.id,
                filename=filename,
                function='admin_handler_AdminActivation',
                exception='',
                content='Входит в режим админа.'
            )
        else:
            if data['approval'] == 'yes':
                await sqlite_db.admin_database_AdminAdd(id=message.from_user.id)
                ID = message.from_user.id
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Вы стали админом.\n'
                         'Что будем делать?',
                    reply_markup=admin_kb.kb_main_admin)
                data_op = await bot_rc.bot_rc_Universal(command=f'op {data["nickname"]}')
                if data_op == 'Nothing changed. The player already is an operator':
                    message_chat = 'Вы уже являетесь оператором сервера'
                    message_logging = 'Пытается повторно стать оператором сервера'
                elif data_op == f'Made {data["nickname"]} a server operator':
                    message_chat = 'Теперь вы являетесь оператором сервера'
                    message_logging = 'Становится оператором сервера'
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=f'{message_chat}',
                    reply_markup=admin_kb.kb_main_admin
                )
                await other.other_source_Logging(
                    id=message.from_user.id,
                    filename=filename,
                    function='admin_handler_AdminActivation',
                    exception='',
                    content=f'Получает права администратора | {message_logging}'
                )
            else:
                await other.other_source_UserAlert(
                    id=message.from_user.id,
                    type='no_register',
                    filename=filename,
                    function='admin_handler_AdminActivation',
                    exception=True
                )
                await client.client_handler_UserStart(message)
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text='Ваша группа не является группой админов сервера.'
        )
    await message.delete()

async def admin_handler_AdminRequests(message: types.Message):
    '''
    Просмотр списка пользователей с неподтвержденными заявками
    :param message:
    :return:
    '''
    try:
        if message.from_user.id == ID:
            id = await sqlite_db.user_database_UserCheckOne(
                line='id',
                column='approval',
                val='not',
            )
            if id:
                id = id[0]
                data = await other.other_source_UserData(
                    id=id,
                    formatted=False
                )
                data_formatted = await other.other_source_UserData(
                    id=id,
                    formatted=True
                )
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=data_formatted,
                    reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton('Одобрить',callback_data=f'accept_application {id}'),
                                                            InlineKeyboardButton('Отклонить', callback_data=f'reject_application {id}')),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                response = f'заявку пользователя {data}'
            else:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Неподтвержденных заявок не осталось.'
                )
                response = 'пустой список заявок'
            await other.other_source_Logging(
                id=message.from_user.id,
                filename=filename,
                function='admin_handler_AdminRequests',
                exception='',
                content=f'Просмотрел {response}.'
            )
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                function='admin_handler_AdminRequests'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_AdminRequests'
        )

async def admin_handler_UserRemove(message: types.Message):
    '''
    Удаление пользователя из базы данных, белого списка и списка операторов сервера
    :param message:
    :return:
    '''
    try:
        if message.from_user.id == ID:
            id = message.text[21:]
            if not id:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Напишите в формате "Удалить пользователя id"'
                )
                await other.other_source_Logging(
                    id=message.from_user.id,
                    filename=filename,
                    function='admin_handler_UserRemove',
                    exception='Incomplete command.',
                    content=''
                )
                return
            data = await other.other_source_UserData(
                id=id,
                formatted=False,
            )
            data_formatted = await other.other_source_UserData(
                id=id,
                formatted=True
            )
            data_admin = await other.other_source_UserData(
                id=message.from_user.id,
                formatted=False
            )
            data_admin_formatted = await other.other_source_UserData(
                id=message.from_user.id,
                formatted=True
            )
            try:
                response_wl = await bot_rc.bot_rc_Universal(command=f'whitelist remove {data["nickname"]}')
                response_dp = await bot_rc.bot_rc_Universal(command=f'deop {data["nickname"]}')
            except:
                await other.other_source_UserAlert(
                    id=message.from_user.id,
                    type='server_offline',
                    filename=filename,
                    function='admin_handler_UserRemove',
                    exception=''
                )
                return

            list_admins = await sqlite_db.user_database_UserCheckAll(
                line='id',
                column='isadmin',
                val='yes'
            )

            try:
                await bot.send_message(
                    chat_id=id,
                    text='Мы сожалеем, но вы были удалены из базы данных сервера.',
                    reply_markup=client_kb.kb_help_client
                )
                await other.other_source_Logging(
                    id=id,
                    filename=filename,
                    function='admin_handler_UserRemove',
                    exception='',
                    content='Оповещён о том, что он удалён из базы данных сервера.'
                )
            except:
                await other.other_source_UserAlert(
                    id=id,
                    type='blocked',
                    filename=filename,
                    function='admin_handler_UserRemove',
                    exception='',
                    admin_id=message.from_user.id
                )

            response_logging = ''
            response_db_chat = ''
            response_db_logging = ''
            response_wl_chat = ''
            response_wl_logging = ''
            response_dp_chat = ''
            response_dp_logging = ''

            if response_wl == 'Player is not whitelisted':
                response_wl_chat = 'Не находился в белом списке.'
                response_wl_logging = f'Попытался удалить из белого списка отсутствующего там игрока.'
            elif response_wl == f'Removed {data["nickname"]} from the whitelist':
                response_wl_chat = 'Удалён из белого списка.'
                response_wl_logging = f'Удалил из белого списка игрока.'

            if data['isadmin'] == 'yes':
                if response_dp == 'Nothing changed. The player is not an operator':
                    response_dp_chat = 'Не являлся оператором сервера.'
                    response_dp_logging = f'| Попытался забрать отсутствующие права оператора у игрока. '
                elif response_dp == f'Made {data["nickname"]} no longer a server operator':
                    response_dp_chat = 'Больше не является оператором сервера.'
                    response_dp_logging = f'| Забрал права оператора у игрока. '

            response_db = await sqlite_db.admin_database_UserRemove(id=id)
            if response_db:
                response_db_chat = 'Удалён из базы данных сервера.'
                response_db_logging = 'Удалил из базы данных сервера пользователя.'
            else:
                response_db_chat = 'Отсутствует в базе данных.'
                response_db_logging = 'Попытался удалить отсутствуещего в базе данных пользователя.'

            await bot.send_message(
                chat_id=message.from_user.id,
                text=f'{data_formatted}\n\n'
                     f'{response_db_chat}\n'
                     f'{response_wl_chat}\n'
                     f'{response_dp_chat}',
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            await other.other_source_Logging(
                id=message.from_user.id,
                filename=filename,
                function='admin_handler_UserRemove',
                exception='',
                content=f'{response_db_logging} | {response_wl_logging} {response_dp_logging}{data}.'
            )
            for ret in list_admins:
                if ret[0] != message.from_user.id:
                    response_logging = f'{data_admin} удалил'
                    await bot.send_message(
                        chat_id=ret[0],
                        text=f'{data_formatted}\n\n'
                             f'Удалён из базы данных сервера админом:\n\n'
                             f'{data_admin_formatted}',
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                elif ret[0] == message.from_user.id:
                    response_logging = 'он удалил'
                await other.other_source_Logging(
                    id=ret[0],
                    filename=filename,
                    function='admin_handler_UserRemove',
                    exception='',
                    content=f'Оповещён, что {response_logging} пользователя {data}'
                )
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                function='admin_handler_UserRemove'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserRemove'
        )

async def admin_handler_UserListApproved(message: types.Message):
    '''
    Получение списка пользователей с одобренными заявками
    :param message:
    :return:
    '''
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user_database_UserCheckAll(
                line='*',
                column='approval',
                val='yes'
            )
            amount = len(data)
            if amount != 0:
                response = f'Количество: {amount}\n\n'
                for ret in data:
                    account = await other.other_source_UserData(
                        id=ret[1],
                        formatted=True
                    )
                    response += f'{account}\n\n'
            else:
                response = 'Отсутствуют.'
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f'**Белый список**\n\n'
                     f'{response}',
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            await other.other_source_Logging(
                id=message.from_user.id,
                filename=filename,
                function='admin_handler_UserListApproved',
                exception='',
                content=f'Просмотрел список пользователей из {amount} человек.'
            )
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                function='admin_handler_UserListApproved'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserListApproved'
        )

async def admin_handler_UserListBanned(message: types.Message):
    '''
    Получение списка пользователей с отклоненными заявками
    :param message:
    :return:
    '''
    try:
        if message.from_user.id == ID:
            data = await sqlite_db.user_database_UserCheckAll(
                line='*',
                column='approval',
                val='ban'
            )
            amount = len(data)
            if amount != 0:
                response = f'Количество: {amount}\n\n'
                for ret in data:
                    account = await other.other_source_UserData(
                        id=ret[1],
                        formatted=True
                    )
                    response += f'{account}\n\n'
            else:
                response = 'Отсутствуют.'
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f'**Белый список**\n\n'
                     f'{response}',
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            await other.other_source_Logging(
                id=message.from_user.id,
                filename=filename,
                function='admin_handler_UserListBanned',
                exception='',
                content=f'Просмотрел список пользователей из {amount} человек.'
            )
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                function='admin_handler_UserListBanned'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserListBanned'
        )

async def admin_handler_UserNotify(message: types.Message):
    '''
    Оповещение всех пользователей о чём либо
    :param message:
    :return:
    '''
    try:
        if message.from_user.id == ID:
            response = message.text[11:]
            if not response:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Напишите в формате:\n'
                         'Оповестить "текст вашего сообщения".'
                )
                await other.other_source_Logging(
                    id=message.from_user.id,
                    filename=filename,
                    function='admin_handler_UserNotify',
                    exception='Incomplete command.',
                    content=''
                )
            else:
                data = await sqlite_db.user_database_UserCheckAll(
                    column='approval',
                    val='yes',
                    line='id'
                )
                dot = ''
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
                            text=f'Важное увeдомление!\n'
                                 f'{response}{dot}'
                        )
                    except:
                        await other.other_source_UserAlert(
                            id=ret[0],
                            type='blocked',
                            filename=filename,
                            function='admin_handler_UserNotify',
                            exception='',
                            admin_id=message.from_user.id
                        )
                await other.other_source_Logging(
                    id=message.from_user.id,
                    filename=filename,
                    function='admin_handler_UserNotify',
                    exception='',
                    content=f'Оповещение "{response}"'
                )
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                function='admin_handler_UserNotify'
            )
    except Exception as exception:
        await admin_source_ForException(
            id=message.from_user.id,
            exception=exception,
            function='admin_handler_UserNotify'
        )

async def admin_handler_PlayersMonitoring(message: types.Message):
    try:
        bot_rc.mcrcon_start()
        if message.from_user.id == ID:
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Мониторинг игроков.',
                reply_markup=admin_kb.kb_inline_monitoring
            )
            await other.other_source_Logging(
                id=message.from_user.id,
                filename=filename,
                function='admin_handler_PlayersMonitoring',
                exception='',
                content='Вызвал данную команду.'
            )
        else:
            await admin_source_ForElse(
                id=message.from_user.id,
                function='admin_handler_PlayersMonitoring'
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
