# -------------- Импорт локальных функций --------------
from handlers import other

# -------------- Импорт функций --------------
import sqlite3
import datetime

# -------------- Обозначение переменных --------------
# Имя и путь базы данных
db_file = "server53.db"

# -------------- Функция запуска базы данных --------------
def sql_start():
    '''
    Открываем базу данных, или при отсутствии её создаем со столбцами: дата, Telegram ID, имя пользователя для Minecraft,
    состояния заявки на регистрацию и принадлежность к админам.
    :return:
    '''
    global base, cur
    base = sqlite3.connect(db_file)
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS users'
                 '(date DATE, id INTEGER UNIQUE, username TEXT UNIQUE, nickname TEXT UNIQUE, approval TEXT, isadmin TEXT)')
    base.commit()
    return True

# -------------- Функции для пользователей --------------

async def user_database_UserAdd(id, username, nickname):
    '''
    При регистрации пользователя указываем значения: конкретное время регистрации, Telegram ID, имя пользователя для Minecraft,
    а так же указываем отрицательные значения в поле подтверждения заявки на регистрацию и принадлежности к админам.
    :param id: id from telegram
    :param username: username from telegram
    :param nickname: nickname for minecraft
    :return: commited database or 0
    '''
    try:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('INSERT INTO users (date, id, username, nickname, approval, isadmin, phone) VALUES (?, ?, ?, ?, ?, ?, ?)', (date, id, username, nickname, 'not', 'not', 'not'))
        base.commit()
    except:
        return 0

async def user_database_UpdateUsernameNickname(id, username, nickname):
    try:
        cur.execute('UPDATE users SET username = ? WHERE id = ?', (username, id,))
        cur.execute('UPDATE users SET nickname = ? WHERE id = ?', (nickname, id,))
        base.commit()
    except:
        return 0

async def user_databse_UserRemove(id, nickname):
    '''
    Проверяем, совпадает ли указанное пользователем имя с именем пользователя, привязанным к его Telegram ID, и только
    затем удаляем его.
    :param id: id from telegram
    :param nickname: nickname for minecraft
    :return: commited database or 0
    '''
    data = await user_database_UserCheckOne(
        line='nickname',
        column='id',
        val=id,
    )
    if data == nickname:
        cur.execute('DELETE FROM users WHERE userd_id = ?', (id,))
        base.commit()
    else:
        return 0

async def user_database_UserCheckOne(line, column, val, type=0):
    '''

    :param line: choose this ("*" for all)
    :param column: where this
    :param val: equals this
    :param type: 0 for first result, 1 for second and etc.
    :return: line with numder type
    '''
    try:
        return cur.execute(f'SELECT {line} FROM users WHERE {column} = ?', (val,)).fetchall()[type]
    except:
        return 0

async def user_database_UserCheckAll(line, column, val):
    '''

    :param line: choose this ("*" for all)
    :param column: where this
    :param val: equals this
    :return: all lines
    '''
    try:
        return cur.execute(f'SELECT {line} FROM users WHERE {column} = ?', (val,)).fetchall()
    except:
        return 0

async def user_database_UserSetApproval(id, val):
    '''
    Первым аргументом получаем необходимое значение (yes/ban), а вторым - Telegram ID пользователя, которому в столбец
    approval нужно назначить его.
    :param id: id from telegram
    :param val: "yes" or "ban"
    :return: commited database or 0
    '''
    try:
        cur.execute('UPDATE users SET approval = ? WHERE id = ?', (val, id,))
        base.commit()
    except:
        return 0

async def user_database_UserSetPhone(id, phone):
    try:
        cur.execute('UPDATE users SET phone = ? WHERE id = ?', (phone, id,))
        base.commit()
    except Exception as e:
        return 0

async def user_database_UsernameUpdate(message, filename, function):
    try:
        data = await other.other_source_UserData(
            id=message.from_user.id,
            formatted=False
        )
        if message.from_user.username:
            username = f'[{message.from_user.first_name}](https://t.me/{message.from_user.username})'
        else:
            username = f'[{message.from_user.first_name}](https://t.me/{data["phone"]})'
        if data['username'] != username:
            cur.execute('UPDATE users SET username = ? WHERE id = ?', (username, message.from_user.id,))
            base.commit()
            await other.other_source_Logging(
                id=message.from_user.id,
                filename=filename,
                function=function,
                exception='',
                content=f'Обновил username с "{data["username"]}" на "{username}".'
            )
    except:
        return 0

# -------------- Функции для админов --------------

async def admin_database_AdminAdd(id):
    '''
    Получаем Telegram ID пользователя и назначаем ему в столбец isadmin значение yes, после чего он считается админом.
    :param id: id from telegram
    :return: commited database or 0
    '''
    try:
        cur.execute('UPDATE users SET isadmin = ? WHERE id = ?', ('yes', id,))
        base.commit()
    except:
        return 0

async def admin_database_UserRemove(id):
    '''
    По запросу от админа (проверка должна находится в функции, которая использует эту) удаляем пользователя с заданным
    Telegram ID.
    :param id: id from telegram
    :return: commited database or 0
    '''
    try:
        cur.execute('DELETE FROM users WHERE id = ?', (id,))
        base.commit()
        return 1
    except:
        return 0