# Python модули
import logging
import datetime
import os


# Функционал
if not os.path.exists('./logs'):
    os.makedirs('./logs')

logger = logging.Logger('base')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    filename=f'./logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    mode='a',
    encoding='windows-1251'
)
console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    fmt='[%(asctime)s] %(levelname)s [%(filename)s; %(funcName)s]: %(message)s;',
    datefmt='%H:%M:%S'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
