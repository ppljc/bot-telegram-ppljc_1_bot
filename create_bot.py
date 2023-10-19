import os
import config
import logging

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

storage = MemoryStorage()

bot = Bot(token = config.TOKEN)
dp = Dispatcher(bot, storage = storage)
dp.middleware.setup(LoggingMiddleware())