# -------------- Импорт локальных функций --------------
import config
from handlers import other
from create_bot import bot
from mcrcons import bot_rc
from keyboards import client_kb
from data_base import sqlite_db
from image_maps import imagemaps

# -------------- Импорт модулей Aiogram --------------
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters.state import State, StatesGroup

# -------------- Импорт функций --------------
import emoji

# -------------- Объявление переменных --------------
filename = 'client.py'

# -------------- FSM классы --------------
class FSMImageMapsUpload(StatesGroup):
	file = State()
	format = State()

# -------------- Вспомогательные функции --------------
async def client_source_Phone(message, function):
	data = await other.other_source_UserData(
		id=message.from_user.id,
		formatted=False,
	)
	if data['phone'] == 'not':
		await bot.send_message(
			chat_id=message.from_user.id,
			text='Для взаимодейсвия с ботом вам нужно поделиться с ним номером телефона. Мы гарантируем, что ваш номер телефона не попадёт третьим лицам.',
			reply_markup=client_kb.kb_client_phonenumber
		)
		await other.other_source_Logging(
			id=message.from_user.id,
			filename=filename,
			function=function,
			exception='',
			content='Оповещён, что для взаимодействия с ботом должен предоставить номер телефона.'
		)
		await sqlite_db.user_database_UsernameUpdate(
			message=message,
			filename=filename,
			function=function
		)
		return 0
	else:
		return 1

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
		if data['approval']:
			phone_check = await client_source_Phone(
				message=message,
				function='client_handler_Any'
			)
			if not phone_check:
				return
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
		for ret in nickname:
			for let in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789':
				if ret == let:
					val_let += 1
					break
		if val_let != len(nickname) or nickname == '':
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
	phone_check = await client_source_Phone(
		message=message,
		function='client_handler_Any'
	)
	if phone_check:
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
			if await bot_rc.bot_rc_ServerOnline():
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
	phone_check = await client_source_Phone(
		message=message,
		function='client_handler_Any'
	)
	if phone_check:
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
						exception='Incomplete command.',
						content=''
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
	phone_check = await client_source_Phone(
		message=message,
		function='client_handler_Any'
	)
	await sqlite_db.user_database_UsernameUpdate(
		message=message,
		filename=filename,
		function='client_handler_ClientSponsor'
	)
	if phone_check:
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
	phone_check = await client_source_Phone(
		message=message,
		function='client_handler_Any'
	)
	if phone_check:
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
	phone_check = await client_source_Phone(
		message=message,
		function='client_handler_Any'
	)
	if phone_check:
		await sqlite_db.user_database_UsernameUpdate(
			message=message,
			filename=filename,
			function='client_handler_Any'
		)
		if not message.chat.title:
			await bot.send_message(message.from_user.id, text=f'{message.from_user.first_name}, я вас не понимаю.', reply_markup=client_kb.kb_help_client)

async def client_handler_ClientPhone(message: types.Message):
	'''

	:param message:
	:return:
	'''
	data = await other.other_source_UserData(
		id=message.from_user.id,
		formatted=False,
	)
	if data['phone'] == 'not':
		phone = message.contact.phone_number
		if message.contact.phone_number[0] != '+':
			phone = f'+{phone}'
		await sqlite_db.user_database_UserSetPhone(
			id=message.from_user.id,
			phone=phone
		)
		await bot.send_message(
			chat_id=message.from_user.id,
			text='Вы успешно предоставили номер телефона.',
			reply_markup=client_kb.kb_help_client
		)
		await other.other_source_Logging(
			id=message.from_user.id,
			filename=filename,
			function='client_handler_ClientPhone',
			exception='',
			content=f'Предоставил свой номер телефона "{phone}"'
		)
		await sqlite_db.user_database_UsernameUpdate(
			message=message,
			filename=filename,
			function='client_handler_ClientPhone'
		)

async def client_handler_ClientImagemapsUploadStart(message: types.Message, state: FSMContext):
	'''
	Старт добавления новой карты на сервер
	:param message:
	:param state:
	:return:
	'''
	phone_check = await client_source_Phone(
		message=message,
		function='client_handler_ClientImagemapsUploadStart'
	)
	if phone_check:
		try:
			data = await other.other_source_UserData(
				id=message.from_user.id,
				formatted=False
			)
			if data['approval'] == 'yes':
				await bot.send_message(
					chat_id=message.from_user.id,
					text=f'Добавление карты на сервер {emoji.emojize(":sunrise_over_mountains:")}\n\n️'
						 f'Если хотите добавить картинку на сервер в виде карты, отправьте её с подписью в качестве названия.\n\n'
						 f'Лучше всего будут выглядеть картинки с размером кратным 128px.\n'
						 f'И в соотношение сторон: 1:1, 1:2, 2:3 и тп.',
					reply_markup=client_kb.kb_client_cancel
				)
				await FSMImageMapsUpload.file.set()
				await other.other_source_Logging(
					id=message.from_user.id,
					filename=filename,
					function='client_handler_ClientImagemapsUploadStart',
					exception='',
					content='Начинает добавлять карту на сервер.'
				)
			else:
				await other.other_source_UserAlert(
					id=message.from_user.id,
					type='no_register',
					filename=filename,
					function='client_handler_ClientImagemapsUploadStart',
					exception=True
				)
				await client_handler_UserStart(message)
		except Exception as exception:
			await other.other_source_UserAlert(
				id=message.from_user.id,
				type='exception',
				filename=filename,
				function='client_handler_ClientImagemapsUploadStart',
				exception=exception
			)

async def client_handler_ClientImagemapsUploadFile(message: types.Message, state: FSMContext):
	'''
	Загрузка файла для добавления карты на сервер
	:param message:
	:param state:
	:return:
	'''
	try:
		if message.caption != None and (message.content_type == 'photo' or message.content_type == 'document'):
			async with state.proxy() as data:
				if message.content_type == 'photo':
					await message.photo[-1].download(destination_file=f'{config.imagemaps_path}\\{message.caption}.png')
				else:
					await message.document.download(destination_file=f'{config.imagemaps_path}\\{message.caption}.png')
				data['file'] = [message.caption, imagemaps.imagemaps_pillow_ImageFormat(name=message.caption)]
				await bot.send_message(
					chat_id=message.from_user.id,
					text=f'Соотношение сторон карты {message.caption} определено как: {data["file"][1][0]}:{data["file"][1][1]}',
					reply_markup=client_kb.kb_client_cancel
				)
				await bot.send_message(
					chat_id=message.from_user.id,
					text=f'Выберите размер карты (в блоках) {emoji.emojize(":triangular_ruler:")}',
					reply_markup=client_kb.kbgen_inline_Format(ratio=data['file'][1])
				)
			await other.other_source_Logging(
				id=message.from_user.id,
				filename=filename,
				function='client_handler_ClientImagemapsUploadFile',
				exception='',
				content=f'Начал добавление на сервер карты с названием "{message.caption}".'
			)
			await FSMImageMapsUpload.next()
		else:
			await bot.send_message(
				chat_id=message.from_user.id,
				text='Отправьте файл снова, но с подписанным названием!',
				reply_markup=client_kb.kb_client_cancel
			)
			await other.other_source_Logging(
				id=message.from_user.id,
				filename=filename,
				function='client_handler_ClientImagemapsUploadFile',
				exception=f'No caption with {message.content_type}.',
				content=''
			)
			await FSMImageMapsUpload.file.set()
	except Exception as exception:
		await other.other_source_UserAlert(
			id=message.from_user.id,
			type='exception',
			filename=filename,
			function='client_handler_ClientImagemapsUploadFile',
			exception=exception
		)

async def client_handler_ClientImagemapsUploadCancel(message: types.Message, state: FSMContext):
	'''
	Отмена добавления карты на сервер
	:param message:
	:param state:
	:return:
	'''
	await state.finish()
	await message.delete()
	await bot.send_message(
		chat_id=message.from_user.id,
		text='Добавление карты отменено.',
		reply_markup=client_kb.kb_client
	)
	await other.other_source_Logging(
		id=message.from_user.id,
		filename=filename,
		function='client_handler_ClientImagemapsUploadCancel',
		exception='',
		content='Отменил добавление карты на сервер.'
	)

async def client_handler_ClientImagemapsUploadFormat(query: types.CallbackQuery, state: FSMContext):
	'''
	Установка нужного соотношения в блоках для карты
	:param query:
	:param state:
	:return:
	'''
	try:
		async with state.proxy() as data:
			name = data['file'][0]
			ratio = str.split(query.data[6:])
			ratio = [int(ratio[0]), int(ratio[1])]
			ratio_message = f'{ratio[0]}:{ratio[1]}'
			imagemaps.imagemaps_pillow_ImageScale(
				name=name,
				ratio=ratio
			)
			await bot.send_message(
				chat_id=query.from_user.id,
				text=f'Карта {name} в размере {ratio_message} добавлена на сервер {emoji.emojize(":check_mark:")}',
				reply_markup=client_kb.kb_client
			)
		await other.other_source_Logging(
			id=query.from_user.id,
			filename=filename,
			function='client_handler_ClientImagemapsUploadFormat',
			exception='',
			content=f'Закончил добавление карты {name} с размером {ratio_message}.'
		)
		await state.finish()
	except Exception as exception:
		await other.other_source_UserAlert(
			id=query.from_user.id,
			type='exception',
			filename=filename,
			function='client_handler_ClientImagemapsUploadFormat',
			exception=exception
		)

def register_handlers_client(dp: Dispatcher):
	dp.register_message_handler(client_handler_UserStart, commands=['start', 'help'])
	dp.register_message_handler(client_handler_UserRegister, Text(startswith='Регистрация'))
	dp.register_message_handler(client_handler_ClientIssue, Text(startswith='Проблема'))
	dp.register_message_handler(client_handler_ClientServerStatus, Text('Статус'))
	dp.register_message_handler(client_handler_ClientSponsor, Text('Поддержать'))
	dp.register_message_handler(client_handler_ClientPhone, content_types=types.ContentType.CONTACT)

	dp.register_message_handler(client_handler_ClientImagemapsUploadStart, Text('Добавить карту'), state='*')
	dp.register_message_handler(client_handler_ClientImagemapsUploadFile, content_types=['document', 'photo'], state=FSMImageMapsUpload.file)
	dp.register_message_handler(client_handler_ClientImagemapsUploadCancel, Text('Отмена'), state='*')
	dp.register_callback_query_handler(client_handler_ClientImagemapsUploadFormat, lambda x: x.data.startswith('scale'), state=FSMImageMapsUpload.format)

	dp.register_message_handler(client_handler_Any)