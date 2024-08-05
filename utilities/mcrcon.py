# Python модули
from typing import List, Any

from aiomcrcon import Client
from aiogram.types import Message


# Локальные модули
from utilities.logger import logger


# Классы
class MCRcon:
    def __init__(self, rcon_host: str, rcon_port: int, rcon_password: str):
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        self.connection = Client(
            host=self.rcon_host,
            port=self.rcon_port,
            password=self.rcon_password
        )

    async def connect(self):
        try:
            await self.connection.connect()
            return True
        except Exception as e:
            logger.error(f'USER=BOT, MESSAGE="{e}"')
            return False

    async def close(self):
        try:
            await self.connection.close()
            return True
        except Exception as e:
            logger.error(f'USER=BOT, MESSAGE="{e}"')
            return False

    async def check_connection(self):
        try:
            await self.connection.send_cmd("checkconnection")
            return True
        except:
            logger.debug(f'USER=BOT, MESSAGE="connection to mcrcon was broken"')
            try:
                await self.connection.connect()
                logger.debug(f'USER=BOT, MESSAGE="connection to mcrcon was established"')
                return True
            except Exception as e:
                logger.error(f'USER=BOT, MESSAGE="{e}"')
                return False

    async def send_cmd(self, cmd: str):
        try:
            await self.check_connection()

            response = await self.connection.send_cmd(cmd)
            return response[0]
        except Exception as e:
            logger.error(f'USER=BOT, MESSAGE="{e}"')

    async def client_status(self):
        try:
            await self.check_connection()

            tps_raw = await self.send_cmd('tps')
            tps_val = tps_raw.split(': ')[1].split(', ')[0][2:]

            list_raw = await self.send_cmd('list')
            list_val = list_raw.split(' ')[2]
            list_users = list_raw.split(': ')[1]

            if list_users == '\n':
                list_users = ' пусто'

            return [tps_val, list_val, list_users]
        except Exception as e:
            logger.error(f'USER=BOT, MESSAGE="{e}"')

    async def admin_status(self):
        try:
            await self.check_connection()

            list_raw = await self.send_cmd('list')
            list_split = list_raw.split()
            list_slice = list_split[10:]

            if len(list_slice) <= 1:
                return list_slice
            elif len(list_slice) > 1:
                val = 0
                for ret in list_slice:
                    list_slice[val] = ret[:-1]
                    if val + 2 == len(list_slice):
                        break
                    val += 1
                return list_slice
        except Exception as e:
            logger.error(f'USER=BOT, MESSAGE="{e}"')
