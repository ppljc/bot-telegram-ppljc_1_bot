from handlers import other
from create_bot import bot
from mcrcons import client_rc
from keyboards import client_kb
from data_base import sqlite_db

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

# -------------- Вспомогательные функции --------------

# -------------- Handler функции --------------
# Комманда срабатывающая при старте бота
async def client__handler__user_start(message: types.Message):
	try:
		data = await sqlite_db.user__database__user_check_one(
			line='approval',
			column='user_id',
			val=message.from_user.id
		)
		if data == 'yes':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Вы уже зарегистрированы!',
				reply_markup=client_kb.kb_client
			)
		elif data == 'not':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Ваша заявка на рассмотрении, просим подождать.',
				reply_markup=client_kb.kb_help_client
			)
		elif data == 'ban':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Ваша заявка отклонена. Вы можете обратиться по этому поводу к Васгену.',
				reply_markup=ReplyKeyboardRemove()
			)
		elif data == 0:
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Привет. Это ассистент Сервера53.\n' \
					 'Чтобы зарегистрироваться напиши "Регистрация никнейм_из_майнкрафта".\n' \
					 'Затем используй /help для получения списка команд.',
				reply_markup=ReplyKeyboardRemove()
			)
		if message.text == '/help':
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} только что вызвал "/help".')
		elif message.text == '/start':
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} только что вызвал "/start".')
	except Exception as exception:
		await message.reply(text='Общение с ботом через ЛС, напишите ему: @server53_helper_bot')
		print(f'Пользователь {message.from_user.id} обратился к боту через группу.')
	await message.delete()

# Регистрация на сервер
async def client__handler__user_register(message: types.Message):
	try:
		username = message.text[12:]
		val = 0
		for ret in username:
			for let in 'abcdefghijklmnopqrstuvwxyz0123456789_':
				if ret == let:
					val += 1
					break
		if val != len(username):
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Нельзя использовать в никнейме пробелы и любые другие символы, кроме английского алфавита, арабских цифры и нижнего подчеркивания!'
			)
			print(f'Пользователь {message.from_user.id} попытался отправить на модерацию заявку, где никнейм содержит запрещенные символы.')
		else:
			data = await sqlite_db.user__database__user_check_one(
				line='approval',
				column='user_id',
				val=message.from_user.id
			)
			if data == 'ban':
				await client__handler__user_start(message)
				print(f'Пользователь {message.from_user.id} попытался отправить на модерацию заявку, хотя она была ранее отклонена.')
			elif data == 'not':
				await client__handler__user_start(message)
				print(f'Пользователь {message.from_user.id} попытался повторно отправить заявку на модерацию.')
			elif data == 'yes':
				await client__handler__user_start(message)
				print(f'Пользователь {message.from_user.id} попытался отправить заявку на модерацию, хотя она уже одобрена.')
			else:
				await sqlite_db.user__database__user_add(
					user_id=message.from_user.id,
					tg_name=message.from_user.username,
					username=username
				)
				await bot.send_message(
					chat_id=message.from_user.id,
					text='Ваша заявка отправлена на модерацию',
					reply_markup=client_kb.kb_help_client
				)
				print(f'Пользователь {message.from_user.id} @{message.from_user.username} отправил заявку с ником {username} на модерацию.')
				await other.other__source__user_alert(
					user_id=message.from_user.id,
					username=message.from_user.username,
					type='request',
					val=username,
				)
	except Exception as exception:
		await other.other__source__user_alert(
			user_id=message.from_user.id,
			username=message.from_user.username,
			type='exception',
			exception=exception,
			val='client__handler__user_register'
		)

# Статус сервера
async def client__handler__client_server_status(message: types.Message):
	try:
		data = await sqlite_db.user__database__user_check_one(
			line='approval',
			column='user_id',
			val=message.from_user.id
		)
		if data == 'yes':
			values = await client_rc.client__rc__server_status(
				user_id=message.from_user.id
			)
			tps = values[0]
			list = values[1]
			list_users = values[2]
			await bot.send_message(
				chat_id=message.from_user.id,
			    text=f'Текущее состояние сервера:\n'
					 f' Число игроков: {list}\n'
					 f' TPS: {tps}\n\n'
					 f' Постояный IP сервера: 92.124.132.235',
				reply_markup=client_kb.kb_client
			)
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} запросил статус сервера: TPS: {tps}; LIST:{list_users}.')
		else:
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} не зарегистрировался, но пытался использовать команду "Статус".')
			await client__handler__user_start(message)
	except Exception as exception:
		if await other_rc.other__rc__server_online():
			await other.other__source__user_alert(
				user_id=message.from_user.id,
				username=message.from_user.username,
				type='exception',
				val='client__handler__server_status',
				exception=exception
			)
		else:
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} обратился с коммандой "Статус" к выключенному серверу.')
			await message.answer(
				text='Сервер оффлайн!'
			)

# Приемка проблем
async def client__handler__client_issue(message: types.Message):
	try:
		data = await sqlite_db.user__database__user_check_one(
			line='approval',
			column='user_id',
			val=message.from_user.id
		)
		if data == 'yes':
			problem = message.text[9:]
			if problem == '':
				await bot.send_message(
					message.from_user.id,
					text='Какова суть проблемы?\n'
						 'Если вашей проблемы нет на появивщейся клавиатуре, напишите в формате:\n'
						 'Проблема "текст проблемы".',
					reply_markup=client_kb.kb_client_problem
				)
				print(f'Пользователь {message.from_user.id} @{message.from_user.username} вызвал неполную команду проблемы.')
				return
			elif problem == 'you are not whitelisted on this server':
				await other.other__source__user_alert(
					user_id=message.from_user.id,
					username=message.from_user.username,
					type='porblem-whitelist'
				)
				await bot.send_message(
					chat_id=message.from_user.id,
					text='Мы сообщили администратору о вашей проблеме, ожидайте.'
				)
				await bot.send_message(
					chat_id=message.from_user.id,
					text='Нам очень жаль, что так вышло.\n'
						 'Данная проблема возникает из-за использования whitelist из ванильного Minecraft. Скорее всего, ваш ник уже зарегестрирован в системе аккаунтов Mojang, а потому UUID берётся привязанный к нему. Из-за этого при входе на сервер Minecraft сравнивает ваш сгенерированный случайно UUID с UUID, привязанным к аккаунту Mojang. Данная проблема исправляется только вручную в данном исполнении системы whitelist. Наша команда уже ищет достойную и надежную замену данной технологии, которая не будет приводить к таким ошибкам.',
					reply_markup=client_kb.kb_client
				)
				print(f'Пользователь {message.from_user.id} @{message.from_user.username} обратился с проблемой "you are not whitelisted on this server".')
				await other.other__source__user_alert(
					user_id=message.from_user.id,
					username=message.from_user.username,
					type='problem_whitelist',
					exception=problem
				)
			else:
				await other.other__source__user_alert(
					user_id=message.from_user.id,
					username=message.from_user.username,
					type='another',
					exception=problem
				)
		else:
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} не зарегистрировался, но пытался использовать команду "Проблема".')
			await client__handler__user_start(message)
	except Exception as exception:
		await other.other__source__user_alert(
			user_id=message.from_user.id,
			username=message.from_user.username,
			type='exception',
			exception=exception,
			val='client__handler__client_issue'
		)

# Предложение проспонсировать проект
async def client__handler__client_sponsor(message: types.Message):
	try:
		data = await sqlite_db.user__database__user_check_one(
			line='approval',
			column='user_id',
			val=message.from_user.id
		)
		if data == 'yes':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Мы будем очень благодарны, если вы поддержите наш проект!\n'
					 'Крипто: BEP20(BSC) - USDT - 0x892fda42e19812bb01f8683caad0520c16ac2e0d\n'
					 'СБП: +79136610052',
				reply_markup=client_kb.kb_client
			)
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} узнал о том, куда донатить.')
		else:
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} не зарегистрировался, но пытался использовать команду "Поддержать".')
			await client__handler__user_start(message)
	except Exception as exception:
		await other.other__source__user_alert(
			user_id=message.from_user.id,
			username=message.from_user.username,
			type='exception',
			exception=exception,
			val='client__handler__client_sponsor'
		)

async def client__change_nickname(message: types.Message):
	pass

async def client_any(message: types.Message):
	await bot.send_message(message.from_user.id, text=f'{message.from_user.first_name}, я вас не понимаю.', reply_markup=client_kb.kb_help_client)

def register_handlers_client(dp: Dispatcher):
	dp.register_message_handler(client__handler__user_start, commands=['start', 'help'])
	dp.register_message_handler(client__handler__user_register, Text(startswith='Регистрация'))
	dp.register_message_handler(client__handler__client_issue, Text(startswith='Проблема'))
	dp.register_message_handler(client__handler__client_server_status, Text('Статус'))
	dp.register_message_handler(client__handler__client_sponsor, Text('Поддержать'))
	dp.register_message_handler(client_any)