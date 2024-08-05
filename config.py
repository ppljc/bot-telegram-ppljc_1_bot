# Python модули
from dotenv import load_dotenv

import os


# Чтение переменных окружения из .env файла
load_dotenv(override=True)

BOT_TOKEN = os.environ['BOT_TOKEN']
DB_NAME = os.environ['DB_NAME']
IMAGEMAPS_PATH = os.environ['IMAGEMAPS_PATH']
RCON_HOST = os.environ['RCON_HOST']
RCON_PORT = os.environ['RCON_PORT']
RCON_PASSWORD = os.environ['RCON_PASSWORD']
