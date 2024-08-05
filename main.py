# Локальные модули
from create_bot import dp, db, bot, rcon
from utilities.logger import logger
from utilities import values
from handlers import client


# Python модули
from aiogram.utils import executor

import nest_asyncio


# Функции onstartup и onshutdown
async def onstartup(_):
	nest_asyncio.apply()

	bot_user = await bot.get_me()
	logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="up and running..."')

	if await db.connect():
		logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database started"')
	else:
		logger.error(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database NOT started"')

	if await rcon.connect():
		logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="rcon started"')
	else:
		logger.error(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="rcon NOT started"')

	await values.read_values(file='admins')


async def onshutdown(_):
	bot_user = await bot.get_me()

	if await db.close():
		logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database finished"')
	else:
		logger.error(
			f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database NOT finished correct"')

	if await rcon.close():
		logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="rcon finished"')
	else:
		logger.error(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="rcon NOT finished correct"')

	logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="shutting down..."')


# Регистрация хендлеров
client.register_handlers(dp=dp)


# Запуск бота
executor.start_polling(dp, skip_updates=True, on_startup=onstartup)
