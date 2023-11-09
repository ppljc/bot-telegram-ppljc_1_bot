# -------------- Импорт функций --------------
import asyncio
import config
import datetime

# -------------- Импорт локальных функций --------------
from handlers import client
from mcrcons import admin_rc, client_rc, other_rc
from create_bot import bot, dp
from data_base import sqlite_db
from keyboards import admin_kb, client_kb

# -------------- Импорт модулей Aiogram --------------
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# -------------- Вспомогательные функции --------------
async def other_source_UserAlert(id, type, filename, function, exception, admin_id=0):
    data = await other_source_UserData(
        id=id,
        formatted=False
    )
    data_formatted = await other_source_UserData(
        id=id,
        formatted=True
    )
    data_admin = await other_source_UserData(id=admin_id)
    list_admins = await sqlite_db.user_database_UserCheckAll(
        line='id',
        column='isadmin',
        val='yes'
    )
    message = ''
    if type == 'blocked':
        await other_source_Logging(
            id=id,
            filename=filename,
            function=function,
            exception='Bot blocked by this user.',
            content=''
        )
        await bot.send_message(
            chat_id=admin_id,
            text=f'{data_formatted}'
                 f'Заблокировал бота и не может получить сообщение.',
            parse_mode=ParseMode.MARKDOWN
        )
        await other_source_Logging(
            id=admin_id,
            filename=filename,
            function=function,
            exception='',
            content=f'Оповещён о том, что {data} заблокировал бота и не может получить сообщение.'
        )

    elif type == 'exception':
        exception = str(exception)
        await bot.send_message(
            chat_id=id,
            text='Возникла ошибка! Но мы её уже решаем.',
            reply_markup=client_kb.kb_help_client
        )
        await other_source_Logging(
            id=id,
            filename=filename,
            function=function,
            exception=exception,
            content=''
        )
        response_message = ''
        response_logging = ''
        for ret in list_admins:
            if ret[0] != id:
                response_message = (f'{data_formatted}'
                                    f'Получил')
                response_logging = f'{data} получил'
            elif ret[0] == id:
                response_message = 'Вы получили'
                response_logging = 'он получил'
            message = f'ошибку "{exception}" в файле "{filename}" в функции "{function}".'
            await bot.send_message(
                chat_id=ret[0],
                text=f'{response_message} {message}'
            )
            await other_source_Logging(
                id=ret[0],
                filename=filename,
                function=function,
                exception='',
                content=f'Оповещён, что {response_logging} {message}'
            )

    elif type == 'request':
        await bot.send_message(
            chat_id=id,
            text='Ваша заявка отправлена на модерацию.',
            reply_markup=client_kb.kb_help_client
        )
        await other_source_Logging(
            id=id,
            filename=filename,
            function=function,
            exception='',
            content='Отправил заявку на регистрацию.'
        )
        for ret in list_admins:
            try:
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'{data_formatted}'
                         f'Отправил заявку на регистрацию.',
                    reply_markup=client_kb.kb_client,
                    parse_mode=ParseMode.MARKDOWN
                )
                await other_source_Logging(
                    id=ret[0],
                    filename=filename,
                    function=function,
                    exception='',
                    content=f'Оповещён о новой заявке на регистрацию от {data}.'
                )
            except:
                await other_source_Logging(
                    id=ret[0],
                    filename=filename,
                    function=function,
                    exception='Blocked bot.',
                    content=''
                )

    elif type[:8] == 'approval':
        query = exception
        value_message = ''
        value_logging = ''
        value_query = ''
        if type[9:] == 'yes':
            value_message = 'одобрена'
            value_logging = 'одобрение'
            value_query = 'Одобрено.'
        elif type[9:] == 'ban':
            value_message = 'отклонена'
            value_logging = 'отклонение'
            value_query = 'Отклонено.'
        await bot.send_message(
            chat_id=id,
            text=f'Ваша заявка на регистрацию {value_message}.'
        )
        await other_source_Logging(
            id=id,
            filename=filename,
            function=function,
            exception='',
            content=f'Оповещён, что его заявка {value_message}.'
        )
        response_logging = ''
        for ret in list_admins:
            message = f'{data} получил {value_logging} заявки от'
            if ret[0] != admin_id:
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'{message} {data_admin}.',
                    parse_mode=ParseMode.MARKDOWN
                )
                response_logging = data_admin
            elif ret[0] == admin_id:
                await query.answer(
                    text=value_query,
                    show_alert=True
                )
                response_logging = 'него'
            await other_source_Logging(
                id=ret[0],
                filename=filename,
                function=function,
                exception='',
                content=f'Оповещён, что {message} {response_logging}.'
            )

    elif type == 'issue':
        issue = exception
        await bot.send_message(
            chat_id=id,
            text='Мы сообщили администратору о вашей проблеме, ожидайте.',
            reply_markup=client_kb.kb_client
        )
        if issue == 'you are not whitelisted on this server':
            await bot.send_message(
                chat_id=id,
                text='Нам очень жаль, что так вышло.\n'
                     'Данная проблема возникает из-за использования whitelist из ванильного Minecraft. Скорее всего, ваш ник уже зарегестрирован в системе аккаунтов Mojang, а потому UUID берётся привязанный к нему. Из-за этого при входе на сервер Minecraft сравнивает ваш сгенерированный случайно UUID с UUID, привязанным к аккаунту Mojang. Данная проблема исправляется только вручную в данном исполнении системы whitelist. Наша команда уже ищет достойную и надежную замену данной технологии, которая не будет приводить к таким ошибкам.',
                reply_markup=client_kb.kb_client
            )
        for ret in list_admins:
            username = data['username']
            message = f'{data} обратился с проблемой "{issue}".'
            await bot.send_message(
                chat_id=ret[0],
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            await other_source_Logging(
                id=ret[0],
                filename=filename,
                function=function,
                exception='',
                content=f'Оповещён, что {message}'
            )

    elif type == 'no_register':
        approval = data['approval']
        if approval != '':
            if approval == 'yes':
                message = 'was registered'
            elif approval == 'not':
                message = 'not approved yet'
            elif approval == 'ban':
                message = 'was banned'
            if exception:
                message_previous = 'use this function'
            else:
                message_previous = 'register'
            await other_source_Logging(
                id=id,
                filename=filename,
                function=function,
                exception=f'Tried to {message_previous}, but {message}.',
                content=''
            )
        else:
            return False

    elif type == 'server_status':
        values = await client_rc.client_rc_ServerStatus()
        tps = values[0]
        list = values[1]
        list_users = values[2]
        for ret in list_admins:
            if id == ret[0]:
                message = f'Игроки: {list_users}\n'
        await bot.send_message(
            chat_id=id,
            text=f'Текущее состояние сервера:\n'
                 f' Число игроков: {list}\n'
                 f' {message}'
                 f' TPS: {tps}\n\n'
                 f' Постояный IP сервера: mc.server53.ru',
            reply_markup=client_kb.kb_client
        )
        await other_source_Logging(
            id=id,
            filename=filename,
            function=function,
            exception='',
            content=f'Запросил статус сервера TPS: {tps}; LIST: {list_users}.'
        )

    elif type == 'server_offline':
        await bot.send_message(
            chat_id=id,
            text='Сервер оффлайн.'
        )
        await other_source_Logging(
            id=id,
            filename=filename,
            function=function,
            exception='Server is offline.',
            content=''
        )
        for ret in list_admins:
            if ret[0] != id:
                message = data
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'{message} обнаружил, что сервер оффлайн при вызове функции "{function}".'
                )
            elif ret[0] == id:
                message = 'он'
            await other_source_Logging(
                id=ret[0],
                filename=filename,
                function=function,
                exception='',
                content=f'Оповещён, что {message} обнаружил, что сервер оффлайн.'
            )

async def other_source_UserData(id, formatted=False):
    response = await sqlite_db.user_database_UserCheckOne(
        line='*',
        column='id',
        val=id
    )
    if formatted == False:
        if not response:
            response = ['', id, '', '', '', '']
        data = {
            'date': response[0],
            'id': response[1],
            'username': response[2],
            'nickname': response[3],
            'approval': response[4],
            'isadmin': response[5]
        }
    elif formatted == True:
        if not response:
            data = (
                f'Пользователь не зарегистрирован!\n'
                f' Telegram ID: {id}\n'
                f' Аккаунт: [USER](tg://user?id={id})'
            )
        else:
            data = (
                f'Зарегистрирован: {response[0]}\n'
                f' Telegram ID: {response[1]}\n'
                f' Аккаунт: {response[2]}\n'
                f' Minecraft ник: {response[3]}\n'
                f' Статус заявки: {response[4]}\n'
                f' Является администратором: {response[5]}\n\n'
            )
    return data

async def other_source_Logging(id, filename, function, exception, content):
    '''

    :param id:
    :param filename:
    :param exception:
    :param content:
    :param function:
    :return:
    '''
    data = await other_source_UserData(id=id)
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'DATE="{date}"; DATA={data}; FILENAME="{filename}"; FUNCTION="{function}"; CONTENT="{content}"; EXCEPTION="{exception}";')