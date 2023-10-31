# -------------- Импорт функций --------------
import asyncio
import config
import datetime

# -------------- Импорт локальных функций --------------
from handlers import client
from mcrcons import admin_rc
from create_bot import bot, dp
from data_base import sqlite_db
from keyboards import admin_kb, client_kb

# -------------- Импорт модулей Aiogram --------------
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

# -------------- Вспомогательные функции --------------
async def other_source_UserAlert(id, type, filename, function, exception, admin_id=0):
    data = await other_source_UserData(id=id)
    data_admin = await other_source_UserData(id=admin_id)
    list_admins = await sqlite_db.user_database_UserCheckAll(
        line='id',
        column='isadmin',
        val='yes'
    )

    if type == 'user_delete':
        await other_source_Logging(
            id=admin_id,
            filename=filename,
            function=function,
            exception='',
            content=f'Удалил из БД пользователя {data}.'
        )
        response_message = ''
        response_logging = ''
        for ret in list_admins:
            if ret != admin_id:
                response_message = f'{data_admin} удалил'
                response_logging = response_message
            elif ret == admin_id:
                response_message = 'Вы удалили'
                response_logging = 'он удалил'
            message = f'пользователя {data} из БД сервера.'
            await bot.send_message(
                chat_id=ret,
                text=f'{response_message} {message}'
            )
            await other_source_Logging(
                id=ret,
                filename=filename,
                function=function,
                exception='',
                content=f'Оповещён, что {response_logging} {message}'
            )
        try:
            await bot.send_message(
                chat_id=id,
                text='Мы сожалеем, но вы были удалены из базы данных сервера.',
                reply_markup=client_kb.kb_help_client
            )
            await other_source_Logging(
                id=id,
                filename=filename,
                function=function,
                exception='',
                content='Оповещён о том, что он удалён из БД сервера.'
            )
        except:
            await bot.send_message(
                chat_id=admin_id,
                text=f'{data} заблокировал бота, а потому не может получить сообщение.'
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
            if ret != id:
                response_message = f'{data} получил'
                response_logging = response_message
            elif ret == id:
                response_message = 'Вы получили'
                response_logging = 'он получил'
            message = f'ошибку "{exception}" в файле "{filename}" в функции "{function}".'
            await bot.send_message(
                chat_id=ret,
                text=f'{response_message} {message}'
            )
            await other_source_Logging(
                id=id,
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
        for ret in data_admin:
            message = f'на регистрацию от пользователя {data}.'
            await bot.send_message(
                chat_id=ret,
                text=f'Новая заявка {message}'
            )
            await other_source_Logging(
                id=ret,
                filename=filename,
                function=function,
                exception='',
                content=f'Оповещён о новой заявке {message}'
            )

    elif type[:8] == 'approval':
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
            if ret != admin_id:
                await bot.send_message(
                    chat_id=ret,
                    text=f'{message} {data_admin}.'
                )
                response_logging = data_admin
            elif ret == admin_id:
                await exception.answer(
                    text=value_query,
                    show_alert=True
                )
                response_logging = 'него'
            await other_source_Logging(
                id=ret,
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
            message = f'{data} обратился с проблемой "{issue}".'
            await bot.send_message(
                chat_id=ret,
                text=message
            )
            await other_source_Logging(
                id=ret,
                filename=filename,
                function=function,
                exception='',
                content=f'Оповещён, что {message}'
            )

    elif type == 'no_register':
        if data['approval'] == 'not':


async def other_source_UserData(id):
    response = await sqlite_db.user_database_UserCheckOne(
        line='*',
        column='id',
        val=id
    )
    data = {
        'date': response[0],
        'id': id,
        'username': response[2],
        'nickname': response[3],
        'approval': response[4],
        'isadmin': response[5],
    }
    if response:
        return data
    else:
        return False

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