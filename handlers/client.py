# Локальные модули
from create_bot import bot, db, rcon
from utilities import imagemaps
from utilities.formatter import user_data
from utilities.logger import logger
from utilities.other import admin_mailing, image_to_server

# Python модули
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ContentTypes
from aiogram.dispatcher.filters.state import State, StatesGroup

# Переменные
keyboard_sub = InlineKeyboardMarkup()
keyboard_sub.row(
	InlineKeyboardButton(text='Статус 🔎', callback_data='server_status'),
	InlineKeyboardButton(text='Проблема ❓', callback_data='issue'),
)
keyboard_sub.row(
	InlineKeyboardButton(text='Картинки 🖼️', callback_data='imagemaps'),
	InlineKeyboardButton(text='Поддержать 💸', callback_data='donate')
)

keyboard_unsub = InlineKeyboardMarkup()
keyboard_unsub.row(
	InlineKeyboardButton(text='Статус 🔎', callback_data='server_status'),
	InlineKeyboardButton(text='Поддержать 💸', callback_data='donate')
)

keyboard_register = InlineKeyboardMarkup()
keyboard_register.row(InlineKeyboardButton(text='Зарегистрироваться ⚒️', callback_data='register'))

keyboard_menu = InlineKeyboardMarkup()
keyboard_menu.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='menu'))


# Классы
class FSMRegister(StatesGroup):
	first_message = State()
	nickname = State()


class FSMIssue(StatesGroup):
	first_message = State()
	issue = State()


class FSMImagemaps(StatesGroup):
	first_message = State()
	name = State()
	format = State()


# Функции
async def message_start(message: types.Message):
	try:
		await message.delete()

		data = await user_data(user_id=message.from_user.id)

		if data['approval'] == 'yes':
			text = 'Вы уже зарегистрированы и у вас куча возможностей ⬇️'
			reply_markup = keyboard_sub
		elif data['approval'] == 'not':
			text = (
				'Ваша заявка на рассмотрении, ожидайте\n'
				'Пока что можете глянуть, как там дела с сервером ⬇️'
			)
			reply_markup = keyboard_unsub
		elif data['approval'] == 'ban':
			text = (
				'Ваша заявка отклонена\n'
				'Вы можете куда-то обратиться по этому поводу..'
			)
			reply_markup = None
		else:
			text = (
				'Привет, это ассистент Сервер53\n'
				'Чтобы начать, жми на кнопку ⬇️'
			)
			reply_markup = keyboard_register

		await message.answer(
			text=text,
			reply_markup=reply_markup
		)

		logger.info(f'USER={message.from_user.id}, MESSAGE="approval={data["approval"]}"')
	except Exception as e:
		logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


async def callback_cancel(query: types.CallbackQuery, state: FSMContext):
	try:
		await query.answer()

		await state.finish()

		data = await user_data(user_id=query.from_user.id)

		if data['approval'] == 'yes':
			text = 'Вы уже зарегистрированы и у вас куча возможностей ⬇️'
			reply_markup = keyboard_sub
		elif data['approval'] == 'not':
			text = (
				'Ваша заявка на рассмотрении, ожидайте\n'
				'Пока что можете глянуть, как там дела с сервером ⬇️'
			)
			reply_markup = keyboard_unsub
		elif data['approval'] == 'ban':
			text = (
				'Ваша заявка отклонена\n'
				'Вы можете куда-то обратиться по этому поводу..'
			)
			reply_markup = None
		else:
			text = (
				'Чтож, я ассистент Сервер53\n'
				'Чтобы начать, жми на кнопку ⬇️'
			)
			reply_markup = keyboard_register

		await query.message.edit_text(
			text=text,
			reply_markup=reply_markup
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


async def callback_register(query: types.CallbackQuery, state: FSMContext):
	try:
		await query.answer()

		data = await user_data(user_id=query.from_user.id)

		if data['approval'] == '':
			text = 'Введи свой никнейм из майнкрафта:'

			await state.update_data(first_message=query.message.message_id)
			await FSMRegister.nickname.set()
		else:
			text = 'Кажется, вам не сюда.'

		await query.message.edit_text(
			text=text,
			reply_markup=keyboard_menu
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


async def message_register_nickname(message: types.Message, state: FSMContext):
	try:
		data = await state.get_data()
		await state.finish()

		await db.add(
			user_id=message.from_user.id,
			nickname=message.text
		)

		user = await user_data(
			user_id=message.from_user.id,
			formatted=True
		)

		reply_markup = InlineKeyboardMarkup()
		reply_markup.row(
			InlineKeyboardButton(text='Принять ✅', callback_data=f'register_accept_{message.from_user.id}'),
			InlineKeyboardButton(text='Отклонить ❌', callback_data=f'register_reject_{message.from_user.id}')
		)

		await admin_mailing(
			text=(
				'❗❗ Новая заявка на регистрацию\n\n'
				f'{user}'
			),
			reply_markup=reply_markup
		)

		await message.delete()
		await bot.edit_message_text(
			chat_id=message.from_user.id,
			message_id=data['first_message'],
			text=f'Ваша заявка с никнеймом "{message.text}" отправлена на рассмотрение модераторам 🔍',
			reply_markup=keyboard_menu
		)

		logger.info(f'USER={message.from_user.id}, MESSAGE="nickname={message.text}"')
	except Exception as e:
		logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


async def callback_server_status(query: types.CallbackQuery):
	try:
		await query.answer()

		status = await rcon.client_status()

		logger.debug(f'USER={query.from_user.id}, MESSAGE="status={status}"')

		data = await user_data(user_id=query.from_user.id)

		if data['approval'] == 'yes':
			text = (
				'Текущее состояние сервера <b>mc.server53.ru</b>:\n'
				f'• TPS: {status[0]}\n'
				f'• Число игроков: {status[1]}\n'
				f'• Список игроков: {status[2]}'
			)
		elif data['approval'] == 'not':
			text = (
				'Текущее состояние сервера <b>mc.server53.ru</b>:\n'
				f'• TPS: {status[0]}\n'
				f'• Число игроков: {status[1]}'
			)
		else:
			text = 'Кажется, вам не сюда.'

		await query.message.edit_text(
			text=text,
			reply_markup=keyboard_menu
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


async def callback_issue(query: types.CallbackQuery, state: FSMContext):
	try:
		await query.answer()

		data = await user_data(user_id=query.from_user.id)

		if data['approval'] == 'yes':
			text = 'Опишите свою проблему текстом:'

			await state.update_data(first_message=query.message.message_id)
			await FSMIssue.issue.set()
		else:
			text = 'Кажется, вам не сюда.'

		await query.message.edit_text(
			text=text,
			reply_markup=keyboard_menu
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


async def message_issue_text(message: types.Message, state: FSMContext):
	try:
		data = await state.get_data()
		await state.finish()

		user = await user_data(
			user_id=message.from_user.id,
			formatted=True
		)
		await admin_mailing(
			text=(
				'❗❗ Сообщение о проблеме\n\n'
				f'{user}\n\n'
				'Описание:\n'
				f'{message.text}'
			)
		)

		await message.delete()
		await bot.edit_message_text(
			chat_id=message.from_user.id,
			message_id=data['first_message'],
			text=(
				'Ваше обращение отправлено модераторам 🔍\n'
				'Вы описали проблему так:\n'
				f'{message.text}'
			),
			reply_markup=keyboard_menu
		)

		logger.info(f'USER={message.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


async def callback_donate(query: types.CallbackQuery):
	try:
		await query.answer()

		data = await user_data(user_id=query.from_user.id)

		if data['approval'] == 'yes' or 'not':
			text = (
				'Мы будем благодарны, если вы поддержите наш проект!\n'
				'Крипто: BEP20(BSC) - USDT - 0x892fda42e19812bb01f8683caad0520c16ac2e0d\n'
				'СБП: +79136610052'
			)
		else:
			text = 'Кажется, вам не сюда.'

		await query.message.edit_text(
			text=text,
			reply_markup=keyboard_menu
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


async def callback_imagemaps(query: types.CallbackQuery, state: FSMContext):
	try:
		await query.answer()

		data = await user_data(user_id=query.from_user.id)

		if data['approval'] == 'yes':
			text = (
				'Добавление карты на сервер 🖼️\n\n'
				'Если хотите добавить картинку на сервер в виде карты, отправьте её с подписью в качестве названия.\n\n'
				'Лучше всего будут выглядеть картинки с размером кратным 128px.\n'
				'И в соотношение сторон: 1:1, 1:2, 2:3 и тп.'
			)

			await state.update_data(first_message=query.message.message_id)
			await FSMImagemaps.name.set()
		else:
			text = 'Кажется, вам не сюда.'

		await query.message.edit_text(
			text=text,
			reply_markup=keyboard_menu
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


async def message_imagemaps_file(message: types.Message, state: FSMContext):
	try:
		await message.delete()

		data = await state.get_data()

		if message.caption is not None:
			logger.debug(f'USER={message.from_user.id}, MESSAGE="name={message.caption}"')

			if message.content_type == 'photo':
				await message.photo[-1].download(destination_file=f'images\\{message.caption}.png')
			elif message.content_type == 'document':
				await message.document.download(destination_file=f'images\\{message.caption}.png')

			image_format = await imagemaps.image_format(name=message.caption)

			text = (
				f'Соотношение сторон определено как {image_format[0]}:{image_format[1]}\n'
				f'Теперь выберите размер карты в блоках:'
			)

			reply_markup = InlineKeyboardMarkup()
			for i in range(1, 5):
				ratio_button = f'{image_format[0] * i}:{image_format[1] * i}'
				ratio_callback = f'{image_format[0] * i}_{image_format[1] * i}'
				reply_markup.insert(InlineKeyboardButton(text=f'{ratio_button}', callback_data=f'scale_{ratio_callback}'))
			reply_markup.insert(InlineKeyboardButton(text='⬅️ Назад', callback_data='menu'))

			await state.update_data(name=message.caption)
			await FSMImagemaps.format.set()
		else:
			text = 'Подпишите изображение!'
			reply_markup = keyboard_menu

		await bot.edit_message_text(
			chat_id=message.from_user.id,
			message_id=data['first_message'],
			text=text,
			reply_markup=reply_markup
		)

		logger.info(f'USER={message.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


async def callback_imagemaps_format(query: types.CallbackQuery, state: FSMContext):
	try:
		await query.answer()

		data = await state.get_data()
		name = data['name']
		ratio = [int(i) for i in query.data.split('_')[1:]]

		await imagemaps.image_scale(
			name=name,
			ratio=ratio
		)
		await image_to_server(image=name)

		await query.message.edit_text(
			text=f'Карта "{name}" в размере {ratio[0]}:{ratio[1]} добавлена на сервер ✅',
			reply_markup=keyboard_menu
		)

		await state.finish()

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


def register_handlers(dp: Dispatcher):
	dp.register_message_handler(message_start, commands=['start', 'help'])

	dp.register_callback_query_handler(callback_cancel, lambda x: x.data == 'menu', state='*')

	dp.register_callback_query_handler(callback_register, lambda x: x.data == 'register')
	dp.register_message_handler(message_register_nickname, state=FSMRegister.nickname)

	dp.register_callback_query_handler(callback_server_status, lambda x: x.data == 'server_status')

	dp.register_callback_query_handler(callback_issue, lambda x: x.data == 'issue')
	dp.register_message_handler(message_issue_text, lambda x: x.content_type == 'text', state=FSMIssue.issue)

	dp.register_callback_query_handler(callback_donate, lambda x: x.data == 'donate')

	dp.register_callback_query_handler(callback_imagemaps, lambda x: x.data == 'imagemaps')
	dp.register_message_handler(message_imagemaps_file, lambda x: x.content_type in ('photo', 'document'), state=FSMImagemaps.name)
	dp.register_callback_query_handler(
		callback_imagemaps_format,
		lambda x: x.data.startswith('scale_'),
		state=FSMImagemaps.format
	)
