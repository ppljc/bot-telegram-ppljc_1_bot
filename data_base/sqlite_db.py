# -------------- Импорт функций --------------
import sqlite3
import datetime

# -------------- Обозначение переменных --------------
# Имя и путь базы данных
db_file = "server53.db"

# -------------- Функция запуска базы данных --------------
# Создаем таблицу пользователей в базе данных
''' Открываем базу данных, или при отсутствии её создаем со столбцами: дата, Telegram ID, имя пользователя для Minecraft,
состояния заявки на регистрацию и принадлежность к админам. '''
def sql_start():
    global base, cur
    base = sqlite3.connect(db_file)
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS users'
                 '(date DATE, user_id INTEGER UNIQUE, tgname TEXT UNIQUE, username TEXT UNIQUE, approval TEXT, isadmin TEXT)')
    base.commit()

# -------------- Функции для пользователей --------------

# Добавление пользователя в базу данных
''' При регистрации пользователя указываем значения: конкретное время регистрации, Telegram ID, имя пользователя для Minecraft,
а так же указываем отрицательные значения в поле подтверждения заявки на регистрацию и принадлежности к админам. '''
async def user__database__user_add(user_id, tg_name, username):
    try:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('INSERT INTO users (date, user_id, tgname, username, approval, isadmin) VALUES (?, ?, ?, ?, ?, ?)', (date, user_id, tg_name, username, 'not', 'not'))
        base.commit()
    except:
        return 0

# Удаление пользователя (для самого пользователя)
''' Проверяем, совпадает ли указанное пользователем имя с именем пользователя, привязанным к его Telegram ID, и только
затем удаляем его. '''
async def user__database__user_remove(user_id, username):
    if cur.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()[0] == username:
        cur.execute('DELETE FROM users WHERE userd_id = ?', (user_id,))
        base.commit()
    else:
        return 0

# Проверка на что-то как-то и где-то
''' Передаем в функцию первым аргументом какую строку надо получить, чтобы её значение в столбце, переданном вторым
аргументом равнялось значению третьего аргумента. '''
async def user__database__user_check_one(line, column, val, type=0):
    '''

    :param line: Ячейка
    :param column: Где ячейка
    :param val: Равна этой переменной
    :param type: 0, 1, 2.. номер
    :return:
    '''
    try:
        return cur.execute(f'SELECT {line} FROM users WHERE {column} = ?', (val,)).fetchone()[type]
    except:
        return 0

# Получения списка пользователей
''' Получаем список чего-то с выполнением определенного условия. '''
async def user__database__user_check_all(column, val, line='*'):
    '''

    :param column: Где ячейка
    :param val: Равно этой переменно
    :param line: Ячейка, по умолчанию все
    :return:
    '''
    try:
        return cur.execute(f'SELECT {line} FROM users WHERE {column} = ?', (val,)).fetchall()
    except:
        return 0

# Одобрение/отклонение заявки пользователя
''' Первым аргументом получаем необходимое значение (yes/ban), а вторым - Telegram ID пользователя, которому в столбец
approval нужно назначить его. '''
async def user__database__user_set_approval(user_id, val):
    try:
        cur.execute('UPDATE users SET approval = ? WHERE user_id = ?', (val, user_id))
        base.commit()
    except:
        return 0

# -------------- Функции для админов --------------

# Функция для задания админских прав
async def admin__database__admin_add(user_id):
    '''
    Получаем Telegram ID пользователя и назначаем ему в столбец isadmin значение yes, после чего он считается админом.
    '''
    try:
        cur.execute('UPDATE users SET isadmin = ? WHERE user_id = ?', ('yes', user_id))
        base.commit()
    except:
        return 0

# Удаление пользователя (для админа)
''' По запросу от админа (проверка должна находится в функции, которая использует эту) удаляем пользователя с заданным
Telegram ID. '''
async def admin__database__user_remove(user_id):
    try:
        cur.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        base.commit()
    except:
        return 0