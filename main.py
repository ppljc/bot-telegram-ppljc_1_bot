# -------------- Импорт локальных функций --------------
from create_bot import dp
from data_base import sqlite_db
from handlers import client, admin, other


from aiogram.utils import executor

# -------------- Функции on_startup и on_shotdown --------------
async def on_startup(_):
	print('Бот вышел в онлайн')
	if sqlite_db.sql_start():
		print('Data base connected OK!')
	await admin.admin__source__on_startup()

async def on_shotdown(_):
	pass

# -------------- Регистрация всех hadler функций --------------
admin.register_handlers_admin(dp)
#other.register_handlers_other(dp)
client.register_handlers_client(dp)

# -------------- Запуск бота --------------
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

# -------------- Комментарии --------------
# Функции должны обзываться таким образом принадлежность__затрагиваемые_функции__название
