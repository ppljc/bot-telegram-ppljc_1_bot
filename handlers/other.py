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
async def other_source_UserAlert(id, type, filename, function, admin_id=0, exception=''):
    data = await other_source_UserData(id=id)
    data_admin = await other_source_UserData(id=admin_id)
    if type == 'user_delete':
        await bot.send_message(
            chat_id=data['id'],
            text='Мы сожалеем, но вы были удалены из базы данных сервера.',
            reply_markup=client_kb.kb_help_client
        )
        await other_source_Logging(
            id=admin_id,
            filename=filename,
            function=function,
            exception='',
            content=f'Админ удалил из БД пользователя {data}'
        )
        await other_source_Logging(
            id=data['id'],
            filename=filename,
            function=function,
            exception='',
            content='Пользователь оповещён о том, что он удалён из БД сервера'
        )
        list_admins = await sqlite_db.user_database_UserCheckAll(
            line='id',
            column='isadmin',
            val='yes'
        )
        for ret in list_admins:
            if ret != admin_id:
                await bot.send_message(
                    chat_id=ret,
                    text=f'{data_admin} удалил пользователя {data} из БД сервера.'
                )
            elif ret == admin_id:
                await bot.send_message(
                    chat_id=ret,
                    text=f'Вы удалили пользователя {data} из БД сервера.'
                )
            print(f'Админ {ret} оповещён о том, что админ {admin_id} удалил пользователя {user_id}.') !!!!!!!!!!

    elif type == 'exception':
        await bot.send_message(
            chat_id=user_id,
            text='Возникла ошибка! Но мы её уже решаем.',
            reply_markup=client_kb.kb_help_client
        )
        print(f'Пользователь {user_id} своими действиями вызвал ошибку "{exception}" в функции "{val}".')
        for ret in data:
            if ret[0] != user_id:
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'Пользователь {user_id} при вызове функции "{val}" получил ошибку "{exception}".'
                )
                print(f'Админ {ret[0]} оповещён о том, что пользователь {user_id} при вызове функции "{val}" получил ошибку "{exception}".')
            elif ret[0] == user_id:
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'При вызове функции "{val}" вы получили ошибку "{exception}".'
                )
                print(f'Админ {ret[0]} оповещён о том, что при вызове функции "{val}" получил ошибку "{exception}".')

    elif type == 'approval':
        await bot.send_message(
            chat_id=user_id,
            text=f'Ваша заявка на регистрацию {val}.'
        )
        print(f'Пользователь {user_id} оповещён, о том, что его заявка {val}.')

    elif type == 'request':
        for ret in data:
            await bot.send_message(
                chat_id=ret[0],
                text=f'Новая заявка на регистрацию от пользователя {user_id} @{username} с ником {val}.'
            )
            print(f'Админ {ret[0]} оповещён о заявке на регистрацию от {user_id} @{username} с ником {val}.')

    elif type == 'issue_whitelist':
        for ret in data:
            if ret[0] != user_id:
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'У пользователя {user_id} @{username} возникли проблемы с whitelist.'
                )
                print(f'Админ {ret[0]} оповещён о проблеме с whitelist {user_id} @{username}.')

    elif type == 'issue_another':
        await bot.send_message(
            chat_id=user_id,
            text='Мы сообщили администратору о вашей проблеме, ожидайте.',
            reply_markup=client_kb.kb_client
        )
        print(f'Пользователь {user_id} @{username} обратился с неизвестной проблемой "{exception}".')
        for ret in data:
            if ret[0] != user_id:
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'У пользователя {user_id} @{username} возникла неизвестная проблема "{exception}".'
                )
                print(f'Админ {ret[0]} оповещён о неизвестной проблеме "{exception}" у {user_id} @{username}.')

async def other_source_UserData(id):
    response = await sqlite_db.user_database_UserCheckOne(
        line='*',
        column='id',
        val=id
    )
    data = {
        'date': data[0],
        'id': data[1],
        'username': data[2],
        'nickname': data[3],
        'approval': data[4],
        'isadmin': data[5],
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