from mcrcon import MCRcon

# Добавление игрока в вайтлист
async def admin__rc__whitelist_add(username):
    with MCRcon('localhost', 'password') as mcr:
        response = mcr.command(f'whitelist add {username}')
    return response

# Удаление игрока из вайтлиста
async def admin__rc__whitelist_remove(username):
    with MCRcon('localhost', 'password') as mcr:
        response = mcr.command(f'whitelist remove {username}')
    return response

# Просмотр списка игроков
async def admin__rc__players_list():
    with MCRcon('localhost', 'password') as mcr:
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