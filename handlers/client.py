# -------------- Импорт локальных функций --------------
from handlers import other
from create_bot import bot
from mcrcons import client_rc, other_rc
from keyboards import client_kb
from data_base import sqlite_db

# -------------- Импорт модулей Aiogram --------------
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

# -------------- Объявление переменных --------------
filename = 'client.py'

# -------------- Вспомогательные функции --------------


# -------------- Handler функции --------------
async def client_handler_UserStart(message: types.Message):
	'''
	The command is triggered when the '/start' is called
	:param message: aiogram.types.Message
	:return: send message to user
	'''
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_UserStart'
	)
	try:
		data = await other.other_source_UserData(id=message.from_user.id)
		if data['approval'] == 'yes':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Вы уже зарегистрированы!',
				reply_markup=client_kb.kb_client
			)
		elif data['approval'] == 'not':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Ваша заявка на рассмотрении, просим подождать.',
				reply_markup=client_kb.kb_help_client
			)
		elif data['approval'] == 'ban':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Ваша заявка отклонена. Вы можете обратиться по этому поводу к Васгену.',
				reply_markup=ReplyKeyboardRemove()
			)
		elif data['approval'] == '':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Привет. Это ассистент Сервера53.\n' \
					 'Чтобы зарегистрироваться напиши "Регистрация никнейм_из_майнкрафта".\n' \
					 'Затем используй /help для получения списка команд.',
				reply_markup=ReplyKeyboardRemove()
			)
		await other.other_source_Logging(
			id=message.from_user.id,
			filename=filename,
			function='client_handler_UserStart',
			exception='',
			content=f'Вызвал "{message.text}".'
		)
	except Exception as exception:
		if message.chat.title:
			await other.other_source_Logging(
				id=message.from_user.id,
				filename=filename,
				function='client_handler_UserStart',
				exception=f'Used {message.text} from group.',
				content=''
			)
			await message.answer(text='Общение с ботом через ЛС, напишите ему: @server53_helper_bot')
		else:
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='exception',
				filename=filename,
				function='client_handler_UserStart',
				exception=exception
			)
	await message.delete()

async def client_handler_UserRegister(message: types.Message):
	'''
	The command is triggered when the 'Регистрация никнейм_из_майнкрафта' is called
	:param message: aiogram.types.Message
	:return: send message to user
	'''
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_UserRegister'
	)
	try:
		nickname = message.text[12:]
		val_let = 0
		val_ret = 0
		for ret in nickname:
			for let in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789_':
				if ret == let:
					if ret == '_':
						nickname = nickname[:val_ret] + '\_' + nickname[(val_ret + 1):]
					val_let += 1
					break
			val_ret += 1
		if val_let != len(nickname):
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Нельзя использовать в никнейме пробелы и любые другие символы, кроме английского алфавита, арабских цифры и нижнего подчеркивания!'
			)
			await other.other_source_Logging(
				id=message.from_user.id,
				filename=filename,
				function='client_handler_UserRegister',
				exception=f'Used forbidden symbols in nickname "{nickname}".',
				content=''
			)
		else:
			request = await other.other_source_UserAlert(
				id=message.from_user.id,
				type='no_register',
				filename=filename,
				function='client_handler_UserRegister',
				exception=''
			)
			if request:
				await client_handler_UserStart(message)
			else:
				if message.from_user.username:
					username = f'[{message.from_user.first_name}](https://t.me/{message.from_user.username})'
				else:
					username = f'[{message.from_user.first_name}](tg://user?id={message.from_user.id})'
				await sqlite_db.user_database_UserAdd(
					id=message.from_user.id,
					username=username,
					nickname=nickname
				)
				await other.other_source_UserAlert(
					id=message.from_user.id,
					type='request',
					filename=filename,
					function='client_handler_UserRegister',
					exception=''
				)
	except Exception as exception:
		await other.other_source_UserAlert(
			id=message.from_user.id,
			type='exception',
			filename=filename,
			function='client_handler_UserRegister',
			exception=exception
		)

async def client_handler_ClientServerStatus(message: types.Message):
	'''
	The command is triggered when the 'Статус' is called
	:param message: aiogram.types.Message
	:return: send message to user
	'''
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_ClientServerStatus'
	)
	try:
		data = await other.other_source_UserData(id=message.from_user.id)
		if data['approval'] == 'yes':
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='server_status',
				filename=filename,
				function='client_handler_ClientServerStatus',
				exception=''
			)
		else:
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='no_register',
				filename=filename,
				function='client_handler_ClientServerStatus',
				exception=True
			)
			await client_handler_UserStart(message)
	except Exception as exception:
		online = await other_rc.other_rc_ServerOnline()
		if online:
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='exception',
				filename=filename,
				function='client_handler_ClientServerStatus',
				exception=exception
			)
		else:
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='server_offline',
				filename=filename,
				function='client_handler_ClientServerStatus',
				exception=''
			)

async def client_handler_ClientIssue(message: types.Message):
	'''
	The command is triggered when the 'Проблема' is called
	:param message: aiogram.types.Message
	:return: send message to user
	'''
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_ClientIssue'
	)
	try:
		data = await other.other_source_UserData(id=message.from_user.id)
		if data['approval'] == 'yes':
			issue = message.text[9:]
			if issue == '':
				await bot.send_message(
					message.from_user.id,
					text='Какова суть проблемы?\n'
						 'Если вашей проблемы нет на появивщейся клавиатуре, напишите в формате:\n'
						 'Проблема "текст проблемы".',
					reply_markup=client_kb.kb_client_problem
				)
				await other.other_source_Logging(
					id=message.from_user.id,
					filename=filename,
					function='client_handler_ClientIssue',
					exception='',
					content='Вызвал неполную команду "Проблема".'
				)
				return
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='issue',
				filename=filename,
				function='client_handler_ClientIssue',
				exception=issue
			)
		else:
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='no_register',
				filename=filename,
				function='client_handler_ClientIssue',
				exception=True
			)
			await client_handler_UserStart(message)
	except Exception as exception:
		await other.other_source_UserAlert(
			id=message.from_user.id,
			type='exception',
			filename=filename,
			function='client_handler_ClientIssue',
			exception=exception
		)

async def client_handler_ClientSponsor(message: types.Message):
	'''
	The command is triggered when the 'Поддержать' is called
	:param message: aiogram.types.Message
	:return: send message to user
	'''
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_ClientSponsor'
	)
	try:
		data = await other.other_source_UserData(id=message.from_user.id)
		if data['approval'] == 'yes':
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Мы будем очень благодарны, если вы поддержите наш проект!\n'
					 'Крипто: BEP20(BSC) - USDT - 0x892fda42e19812bb01f8683caad0520c16ac2e0d\n'
					 'СБП: +79136610052',
				reply_markup=client_kb.kb_client
			)
			await other.other_source_Logging(
				id=message.from_user.id,
				filename=filename,
				function='client_handler_ClientSponsor',
				exception='',
				content='Узнал, как можно поддержать проект.'
			)
		else:
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='no_register',
				filename=filename,
				function='client_handler_ClientServerStatus',
				exception=True
			)
			await client_handler_UserStart(message)
	except Exception as exception:
		await other.other_source_UserAlert(
			id=message.from_user.id,
			type='exception',
			filename=filename,
			function='client_handler_ClientSponsor',
			exception=exception
		)

async def client_handler_ClientChangeNickname(message: types.Message):
	'''
	The command is triggered when the 'Изменить никнейм' is called
	:param message: aiogram.types.Message
	:return: send message to user
	'''
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_ClientChangeNickname'
	)
	pass

async def client_handler_Any(message: types.Message):
	'''
	The command is triggered when any other message send to bot
	:param message: aiogram.types.Message
	:return: send message to user
	'''
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_Any'
	)
	if not message.chat.title:
		await bot.send_message(message.from_user.id, text=f'{message.from_user.first_name}, я вас не понимаю.', reply_markup=client_kb.kb_help_client)

def register_handlers_client(dp: Dispatcher):
	dp.register_message_handler(client_handler_UserStart, commands=['start', 'help'])
	dp.register_message_handler(client_handler_UserRegister, Text(startswith='Регистрация'))
	dp.register_message_handler(client_handler_ClientIssue, Text(startswith='Проблема'))
	dp.register_message_handler(client_handler_ClientServerStatus, Text('Статус'))
	dp.register_message_handler(client_handler_ClientSponsor, Text('Поддержать'))
	dp.register_message_handler(client_handler_Any)