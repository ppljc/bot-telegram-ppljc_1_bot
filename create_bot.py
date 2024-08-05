# Локальные модули
from config import BOT_TOKEN, RCON_HOST, RCON_PORT, RCON_PASSWORD, DB_NAME
from data_base.sqlite_db import SQLiteDB
from utilities.mcrcon import MCRcon


# Python модули
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Переменные
storage = MemoryStorage()

bot = Bot(
	token=BOT_TOKEN,
	disable_web_page_preview=True,
	parse_mode=ParseMode.HTML
)

dp = Dispatcher(
	bot=bot,
	storage=storage,
)

db = SQLiteDB(
	db_name=DB_NAME
)

rcon = MCRcon(
	rcon_host=RCON_HOST,
	rcon_port=RCON_PORT,
	rcon_password=RCON_PASSWORD
)
