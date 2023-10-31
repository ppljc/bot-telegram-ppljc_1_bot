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
# Комманда срабатывающая при старте бота
async def client_handler_UserStart(message: types.Message):
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
		elif data['approval'] == 0:
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
	try:
		nickname = message.text[12:]
		val = 0
		for ret in nickname:
			for let in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789_':
				if ret == let:
					val += 1
					break
		if val != len(nickname):
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
			data = await sqlite_db.user_database_UserCheckOne(
				line='approval',
				column='id',
				val=message.from_user.id
			)
			if data == 'ban':
				await client_handler_UserStart(message)
				print(f'Пользователь {message.from_user.id} попытался отправить на модерацию заявку, хотя она была ранее отклонена.')
			elif data == 'not':
				await client_handler_UserStart(message)
				print(f'Пользователь {message.from_user.id} попытался повторно отправить заявку на модерацию.')
			elif data == 'yes':
				await client_handler_UserStart(message)
				print(f'Пользователь {message.from_user.id} попытался отправить заявку на модерацию, хотя она уже одобрена.')
			else:
				await sqlite_db.user_database_UserAdd(
					id=message.from_user.id,
					username=message.from_user.username,
					nickname=nickname
				)
				await other.other_source_UserAlert(
					id=message.from_user.id,
					type='request',
					filename=filename,
					function='client_handler_UserRegister',
					exception=''
				)
			message
	except Exception as exception:
		await other.other_source_UserAlert(
			id=message.from_user.id,
			type='exception',
			filename=filename,
			function='client_handler_UserRegister',
			exception=exception
		)

# Статус сервера
async def client_handler_ClientServerStatus(message: types.Message):
	try:
		data = await sqlite_db.user_database_UserCheckOne(
			line='approval',
			column='id',
			val=message.from_user.id
		)
		if data == 'yes':
			values = await client_rc.client_rc_ServerStatus()
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
			await client_handler_UserStart(message)
	except Exception as exception:
		if await other_rc.other_rc_ServerOnline():
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='exception',
				filename=filename,
				function='client_handler_ClientServerStatus',
				exception=exception
			)
		else:
			print(f'Пользователь {message.from_user.id} @{message.from_user.username} обратился с коммандой "Статус" к выключенному серверу.')
			await message.answer(
				text='Сервер оффлайн!'
			)

# Приемка проблем
async def client_handler_ClientIssue(message: types.Message):
	try:
		data = await sqlite_db.user_database_UserCheckOne(
			line='approval',
			column='id',
			val=message.from_user.id
		)
		if data == 'yes':
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
			await other.other_source_Logging(
				id=message.from_user.id,
				filename=filename,
				function='client_handler_ClientIssue',
				exception='User not approved or banned.',
				content=''
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

# Предложение проспонсировать проект
async def client_handler_ClientSponsor(message: types.Message):
	try:
		data = await sqlite_db.user_database_UserCheckOne(
			line='approval',
			column='id',
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
			await client_handler_UserStart(message)
	except Exception as exception:
		await other.other_source_UserAlert(
			id=message.from_user.id,
			type='exception',
			filename=filename,
			function='client_handler_ClientSponsor',
			exception=exception
		)

async def client_handler_ChangeNickname(message: types.Message):
	pass

async def client_handler_Any(message: types.Message):
	if not message.chat.title:
		await bot.send_message(message.from_user.id, text=f'{message.from_user.first_name}, я вас не понимаю.', reply_markup=client_kb.kb_help_client)

def register_handlers_client(dp: Dispatcher):
	dp.register_message_handler(client_handler_UserStart, commands=['start', 'help'])
	dp.register_message_handler(client_handler_UserRegister, Text(startswith='Регистрация'))
	dp.register_message_handler(client_handler_ClientIssue, Text(startswith='Проблема'))
	dp.register_message_handler(client_handler_ClientServerStatus, Text('Статус'))
	dp.register_message_handler(client_handler_ClientSponsor, Text('Поддержать'))
	dp.register_message_handler(client_handler_Any)