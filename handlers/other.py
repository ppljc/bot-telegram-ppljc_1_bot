# -------------- Импорт функций --------------
import asyncio
import config

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
async def other__source__user_alert(user_id, type, admin_id=0, val='', exception='', username=''):
    data = await sqlite_db.user__database__user_check_all(
        column='isadmin',
        val='yes',
        line='user_id'
    )
    if type == 'user_delete':
        await bot.send_message(
            user_id,
            text='Мы сожалеем, но вы были удалены из базы данных сервера.',
            reply_markup=client_kb.kb_help_client
        )
        print(f'Пользователь {user_id} @{username} оповещён о том, что он удалён из базы данных сервера.')
        for ret in data:
            if ret[0] != admin_id:
                await bot.send_message(
                    ret[0],
                    text=f'Админ {admin_id} удалил пользователя {user_id} @{username}.'
                )
            elif ret[0] == admin_id:
                await bot.send_message(
                    ret[0],
                    text=f'Пользователь {user_id} @{username} удалён из базы данных.'
                )
            print(f'Админ {ret[0]} оповещён о том, что админ {admin_id} удалил пользователя {user_id}.')
    elif type == 'exception':
        await bot.send_message(
            user_id,
            text='Возникла ошибка! Но мы её уже решаем.',
            reply_markup=client_kb.kb_help_client
        )
        print(f'Пользователь {user_id} своими действиями вызвал ошибку "{exception}" в функции "{val}".')
        for ret in data:
            if ret[0] != user_id:
                await bot.send_message(
                    ret[0],
                    text=f'Пользователь {user_id} при вызове функции "{val}" получил ошибку "{exception}".'
                )
                print(f'Админ {ret[0]} оповещён о том, что пользователь {user_id} при вызове функции "{val}" получил ошибку "{exception}".')
            elif ret[0] == user_id:
                await bot.send_message(
                    ret[0],
                    text=f'При вызове функции "{val}" вы получили ошибку "{exception}".'
                )
                print(f'Админ {ret[0]} оповещён о том, что при вызове функции "{val}" получил ошибку "{exception}".')
    elif type == 'approval':
        await bot.send_message(
            user_id,
            text=f'Ваша заявка на регистрацию {val}.'
        )
        print(f'Пользователь {user_id} оповещён, о том, что его заявка {val}.')
    elif type == 'request':
        for ret in data:
            await bot.send_message(
                ret[0],
                text=f'Новая заявка на регистрацию от пользователя {user_id} @{username} с ником {val}.'
            )
            print(f'Админ {ret[0]} оповещён о заявке на регистрацию от {user_id} @{username} с ником {val}.')
    elif type == 'problem_whitelist':
        for ret in data:
            if ret[0] != user_id:
                await bot.send_message(
                    ret[0],
                    text=f'У пользователя {user_id} @{username} возникли проблемы с whitelist.'
                )
                print(f'Админ {ret[0]} оповещён о проблеме с whitelist {user_id} @{username}.')
    elif type == 'another':
        await bot.send_message(
            chat_id=user_id,
            text='Мы сообщили администратору о вашей проблеме, ожидайте.',
            reply_markup=client_kb.kb_client
        )
        print(f'Пользователь {user_id} @{username} обратился с неизвестной проблемой "{exception}".')
        for ret in data:
            if ret[0] != user_id:
                await bot.send_message(
                    ret[0],
                    text=f'У пользователя {user_id} @{username} возникла неизвестная проблема "{exception}".'
                )
                print(f'Админ {ret[0]} оповещён о неизвестной проблеме "{exception}" у {user_id} @{username}.')