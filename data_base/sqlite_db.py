# Локальные модули
from utilities.logger import logger


# Python модули
import sqlite3
import datetime
import aiosqlite


# Классы
class SQLiteDB:
	def __init__(self, db_name):
		self.db_name = db_name
		self.connection = None

	async def connect(self):
		try:
			self.connection = await aiosqlite.connect(self.db_name)
			await self.connection.execute(
				'''CREATE TABLE IF NOT EXISTS users'''
				'''(date DATE, user_id INTEGER UNIQUE, nickname TEXT UNIQUE, approval TEXT)'''
			)
			await self.connection.commit()
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

	async def add(self, user_id, nickname):
		try:
			date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			await self.connection.execute(
				'''INSERT INTO users (date, user_id, nickname, approval) VALUES (?, ?, ?, ?)''',
				(date, user_id, nickname, 'not')
			)
			await self.connection.commit()
			logger.debug(f'USER={user_id}, MESSAGE=""')
		except sqlite3.IntegrityError:
			logger.debug(f'USER={user_id}, MESSAGE="already exists"')
		except Exception as e:
			logger.error(f'USER={user_id}, MESSAGE="{e}"')

	async def remove(self, user_id):
		try:
			await self.connection.execute('''DELETE FROM users WHERE user_id = ?''', (user_id,))
			await self.connection.commit()
			logger.debug(f'USER={user_id}, MESSAGE=""')
		except Exception as e:
			logger.error(f'USER={user_id}, MESSAGE="{e}"')

	async def read(self, line, column, value):
		try:
			cursor = await self.connection.execute(f'''SELECT {line} FROM users WHERE {column} = ?''', (value,))
			rows = await cursor.fetchall()
			logger.debug(f'USER=BOT, MESSAGE="users={len(rows)}"')
			return rows
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')

	async def update(self, line, column, value_0, value_1):
		try:
			cursor = await self.connection.execute(f'''UPDATE users SET {line} = ? WHERE {column} = ?''', (value_0, value_1))
			rows = await cursor.fetchall()
			logger.debug(f'USER=BOT, MESSAGE="amount={len(rows)}"')
			return rows
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')
