# Python модули
from os import path
from aioshutil import move


# Локальные модули
from utilities import values
from utilities.logger import logger
from create_bot import bot
from config import IMAGEMAPS_PATH


# Функции
async def admin_mailing(text: str, reply_markup=None):
	try:
		admins = await values.read_values('admins')
		for admin in admins:
			await bot.send_message(
				chat_id=admin,
				text=text,
				reply_markup=reply_markup,
			)
		logger.debug(f'USER=BOT, MESSAGE="admins={len(admins)}"')
	except Exception as e:
		logger.error(f'USER=BOT, MESSAGE="{e}"')


async def image_to_server(image: str):
	try:
		old_path = path.abspath(f'images\\{image}.png')
		await move(old_path, IMAGEMAPS_PATH)
	except Exception as e:
		logger.error(f'USER=BOT, MESSAGE="{e}"')
