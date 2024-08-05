# Python модули
from aiogram import types
from aiogram.types import ParseMode, ContentTypes


# Локальные модули
from create_bot import bot, dp
from keyboards import admin_kb
from utilities.logger import logger


# Функции
@dp.message_handler()
async def message_any(message: types.Message):
    try:
        await message.reply(text='Я вас не понимаю!')

        logger.info(f'USER={message.from_user.id}, MESSAGE="unknown: {message.text}"')
    except Exception as e:
        logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


@dp.callback_query_handler()
async def callback_any(query: types.CallbackQuery):
    try:
        await query.answer(text='Такой кнопки пока нет!', show_alert=True)

        logger.info(f'USER={query.from_user.id}, MESSAGE="unknown: {query.data}"')
    except Exception as e:
        logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


async def other_source_UserAlert(id, type, filename, function, exception, admin_id=0):
    message = ''
    if type == 'blocked':
        await bot.send_message(
            chat_id=admin_id,
            text=f'{data_formatted}\n\n'
                 f'Заблокировал бота и не может получить сообщение.',
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

    elif type == 'exception':
        exception = str(exception)
        await bot.send_message(
            chat_id=id,
            text='Возникла ошибка! Но мы её уже решаем.',
            reply_markup=client_kb.kb_help_client
        )
        response_message = ''
        response_logging = ''
        for ret in list_admins:
            if ret[0] != id:
                response_message = (f'{data_formatted}\n\n'
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

    elif type == 'request':
        await bot.send_message(
            chat_id=id,
            text='Ваша заявка отправлена на модерацию.',
            reply_markup=client_kb.kb_client_phonenumber
        )
        for ret in list_admins:
            await bot.send_message(
                chat_id=ret[0],
                text=f'{data_formatted}\n\n'
                     f'Отправил заявку на регистрацию.',
                reply_markup=admin_kb.kb_main_admin,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

    elif type[:8] == 'approval':
        value_message = ''
        value_logging = ''
        if type[9:] == 'yes':
            value_message = 'одобрена'
            value_logging = 'одобрение'
        elif type[9:] == 'ban':
            value_message = 'отклонена'
            value_logging = 'отклонение'
        await bot.send_message(
            chat_id=id,
            text=f'Ваша заявка на регистрацию {value_message}.'
        )
        for ret in list_admins:
            if ret[0] != admin_id:
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'{data_formatted}\n\n'
                         f'Пользователь получил {value_logging} заявки от админа:\n\n'
                         f'{data_admin_formatted}',
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
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
            message = f'с проблемой "{issue}".'
            await bot.send_message(
                chat_id=ret[0],
                text=f'{data_formatted}\n\n'
                     f'Обратился {message}',
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
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
        else:
            return False

    elif type == 'server_status':
        values = await bot_rc.mcrcon_client_list_players()
        tps = values[0]
        list = values[1]
        list_users = values[2]
        for ret in list_admins:
            if id == ret[0]:
                message = f'Игроки:{list_users}\n'
        await bot.send_message(
            chat_id=id,
            text=f'Текущее состояние сервера:\n'
                 f' Число игроков: {list}\n'
                 f' {message}'
                 f' TPS: {tps}\n\n'
                 f' Постояный IP сервера: mc.server53.ru',
            reply_markup=client_kb.kb_client
        )

    elif type == 'server_offline':
        response = ''
        if exception == 'monitoring':
            response = 'Перезапустите мониторинг.'
        await bot.send_message(
            chat_id=id,
            text=f'Сервер оффлайн.\n'
                 f'{response}'
        )
        for ret in list_admins:
            if ret[0] != id:
                message = data
                await bot.send_message(
                    chat_id=ret[0],
                    text=f'{data_formatted}\n\n'
                         f'Обнаружил, что сервер оффлайн при вызове функции "{function}".'
                )
            elif ret[0] == id:
                message = 'он'
