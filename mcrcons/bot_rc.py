# -------------- Импорт функций --------------
import time

from mcrcon import MCRcon

# -------------- Импорт локальных функций --------------
from config import localhost, password

# -------------- Функция запуска MCRcon подключения --------------
def mcrcon_start():
    global mcr
    try:
        mcr = MCRcon(localhost, password)
        mcr.connect()
        return True
    except:
        return False

# -------------- Функции для пользователей --------------
async def client_rc_ListPlayers():
    tps = mcr.command('tps')
    tps_split = tps.split()[6]
    tps_val = tps_split[3:][:-1]
    list = mcr.command('list')
    list_split = list.split()
    list_val = list_split[2]
    list_slice = list_split[10:]
    list_users = ''
    for ret in list_slice:
        list_users += f' {ret}'
    if list_users == '':
        list_users = ' no one'
        list_users = ' no one'
    data = [tps_val, list_val, list_users]
    return data

# -------------- Функции для админов --------------
async def admin_rc_ListPlayers():
    list = mcr.command('list')
    list_split = list.split()
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

# -------------- Остальные функции --------------
async def bot_rc_ServerOnline():
    try:
        response = mcr.command('list')
        return True
    except:
        return False

# -------------- Универсальная функция --------------
async def bot_rc_Universal(command):
    response = mcr.command(command)
    return response