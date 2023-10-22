from create_bot import bot
from mcrcons import client_rc
from keyboards import client_kb
from data_base import sqlite_db

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

# -------------- Вспомогательные функции --------------

async def client_source_alert(message, type, exception='', function=''):
	if type == 'request':
		for ret in await sqlite_db.user_list('isadmin', 'yes', 'user_id'):
			await bot.send_message(ret[0], text=f'Новая заявка на регистрацию от пользователя {message.from_user.id} @{message.from_user.username}.')
			print(f'Админ {ret[0]} оповещён о заявке на регистрацию от {message.from_user.id}.')
	elif type == 'problem_whitelist':
		for ret in await sqlite_db.user_list('isadmin', 'yes', 'user_id'):
			await bot.send_message(ret[0], text=f'У пользователя {message.from_user.id} возникли проблемы с whitelist.')
			print(f'Админ {ret[0]} оповещён о проблеме с whitelist {message.from_user.id}.')
	elif type == 'another':
		for ret in await sqlite_db.user_list('isadmin', 'yes', 'user_id'):
			await bot.send_message(ret[0], text=f'У пользователя {message.from_user.id} @{message.from_user.username} возникла неизвестная проблема "{message.text[9:]}".')
			print(f'Админ {ret[0]} оповещён о неизвестной проблеме "{message.text[9:]}" у {message.from_user.id}.')
	elif type == 'exception':
		for ret in await sqlite_db.user_list('isadmin', 'yes', 'user_id'):
			await bot.send_message(ret[0], text=f'Пользователь {message.from_user.id} при вызове функции "{function}" получил ошибку "{exception}".')
			print(f'Админ {ret[0]} оповещён о том, что пользователь {message.from_user.id} при вызове функции {function} получил ошибку {exception}.')

async def client_source_warning(message, exception, function):
	if exception:
		await bot.send_message(message.from_user.id, text='Возникла ошибка! Но мы её уже решаем.')
		print(f'Пользователь {message.from_user.id} своими действиями вызвал ошибку "{exception}" в функции "{function}".')
		await client_source_alert(message, 'exception', exception=exception, function=function)

# -------------- Handler функции --------------

# Комманда срабатывающая при старте бота
async def client_start(message: types.Message):
	try:
		if await sqlite_db.user_check('approval', 'user_id', message.from_user.id) == 'yes':
			await bot.send_message(message.from_user.id, text='Вы уже зарегистрированы!', reply_markup=client_kb.kb_client)
		elif await sqlite_db.user_check('approval', 'user_id', message.from_user.id) == 'not':
			await bot.send_message(message.from_user.id, text='Ваша заявка на рассмотрении.', reply_markup=client_kb.kb_client)
		elif await sqlite_db.user_check('approval', 'user_id', message.from_user.id) == 'ban':
			await bot.send_message(message.from_user.id, text='Ваша заявка отклонена. Вы можете обратиться по этому поводу к Васгену.', reply_markup=ReplyKeyboardRemove())
		elif await sqlite_db.user_check('approval', 'user_id', message.from_user.id) == 0:
			await bot.send_message(message.from_user.id, text='Привет. Это ассистент Сервера53.\n' \
															  'Чтобы зарегистрироваться напиши "Регистрация никнейм_из_майнкрафта".\n' \
															  'Затем используй /help для получения списка команд.', reply_markup=ReplyKeyboardRemove())
		if message.text == '/help':
			print(f'Пользователь {message.from_user.id} только что вызвал "/help".')
		elif message.text == '/start':
			print(f'Пользователь {message.from_user.id} только что вызвал "/start".')
	except Exception as exception:
		if exception:
			await client_source_warning(message, exception, 'client_start')
			return
		await message.reply(text='Общение с ботом через ЛС, напишите ему: @server53_helper_bot')
		print(f'Пользователь {message.from_user.id} обратился к боту через группу.')
	await message.delete()

# Регистрация на сервер
async def client_register(message: types.Message):
	try:
		text = message.text[12:]
		spaces = text.count(' ')
		if spaces == 0:
			username = text
		else:
			if await sqlite_db.user_check('approval', 'user_id', message.from_user.id):
				await bot.send_message(message.from_user.id, text='Ваша заявка уже была отклонена')
				print(f'Пользователь {message.from_user.id} попытался отправить на модерацию заявку, хотя она была ранее отклонена.')
				return
			else:
				await bot.send_message(message.from_user.id, text='Нельзя использовать пробелы в никнеймах!')
				print(f'Пользователь {message.from_user.id} попытался отправить на модерацию заявку, где никнейм с пробелом.')
				return
		await sqlite_db.user_add(message.from_user.id, message.from_user.username, username)
		await bot.send_message(message.from_user.id, text='Ваша заявка отправлена на модерацию', reply_markup=client_kb.kb_help_client)
		print(f'Пользователь {message.from_user.id} отправил заявку с ником {username} на модерацию.')
		await client_source_alert(message, 'request')
	except Exception as exception:
		await client_source_warning(message, exception, 'client_register')

# Статус сервера
async def client_server(message: types.Message):
	try:
		data = await client_rc.server_info(message.from_user.id)
		tps = data[0]
		list = data[1]
		list_users = data[2]
		await bot.send_message(message.from_user.id, text=f'Текущее состояние сервера:\n'
														  f' Число игроков: {list}\n'
														  f' TPS: {tps}\n\n'
														  f' Постояный IP сервера: 92.124.132.235')
		print(f'Пользователь {message.from_user.id} запросил статус сервера: TPS: {tps}; LIST:{list_users}.')
	except Exception as exception:
		if exception:
			await client_source_warning(message, exception, 'client_server')
			return
		print(f'Пользователь {message.from_user.id} попытался узнать статус выключенного сервера.')
		await bot.send_message(message.from_user.id, text='Сервер находится оффлайн.')

async def client_problem(message: types.Message):
	try:
		if await sqlite_db.user_check('approval', 'user_id', message.from_user.id) == 'yes':
			problem = message.text[9:]
			if problem == '':
				await bot.send_message(message.from_user.id, text='Какова суть проблемы?\n'
																  'Если вашей проблемы нет на появивщейся клавиатуре, напишите в формате:\n'
																  'Проблема "текст проблемы".', reply_markup=client_kb.kb_client_problem)
				print(f'Пользователь {message.from_user.id} вызвал неполную команду проблемы.')
				return
			elif problem == 'you are not whitelisted on this server':
				await client_source_alert(message, 'problem_whitelist')
				await bot.send_message(message.from_user.id, text='Мы сообщили администратору о вашей проблеме, ожидайте.')
				await bot.send_message(message.from_user.id, text='Нам очень жаль, что так вышло.\n'
																  'Данная проблема возникает из-за использования whitelist из ванильного Minecraft. Скорее всего, ваш ник уже зарегестрирован в системе аккаунтов Mojang, а потому UUID берётся привязанный к нему. Из-за этого при входе на сервер Minecraft сравнивает ваш сгенерированный случайно UUID с UUID, привязанным к аккаунту Mojang. Данная проблема исправляется только вручную в данном исполнении системы whitelist. Наша команда уже ищет достойную и надежную замену данной технологии, которая не будет приводить к таким ошибкам.',
																  reply_markup=client_kb.kb_client)
				print(f'Пользователь {message.from_user.id} обратился с проблемой "you are not whitelisted on this server".')
			else:
				print(f'Пользователь {message.from_user.id} обратился с неизвестной проблемой "{problem}".')
				await client_source_alert(message, 'another')
				await bot.send_message(message.from_user.id, text='Мы сообщили администратору о вашей проблеме, ожидайте.')
		else:
			print(f'Пользователь {message.from_user.id} не зарегистрировался, но пытался использовать команду проблемы.')
			await client_start(message)
	except Exception as exception:
		await client_source_warning(message, exception, 'client_problem')


def register_handlers_client(dp: Dispatcher):
	dp.register_message_handler(client_start, commands=['start', 'help'])
	dp.register_message_handler(client_register, Text(startswith='Регистрация'))
	dp.register_message_handler(client_server, Text('Статус'))
	dp.register_message_handler(client_problem, Text(startswith='Проблема'))