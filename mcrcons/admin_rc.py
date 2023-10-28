from mcrcon import MCRcon

async def admin_rc_Whitelist(nickname, type):
    with MCRcon('localhost', 'password') as mcr:
        response = mcr.command(f'whitelist {type} {nickname}')
    return response

# Просмотр списка игроков
async def admin_rc_ListPlayers():
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

async def admin_rc_Op(nickname, type):
    with MCRcon('localhost', 'password') as mcr:
        response = mcr.command(f'{type}op {nickname}')
    return response
    # Made ppljc a server operator
    # Nothing changed. The player already is an operator

    # Made tfsi no longer a server operator
    # Nothing changed. The player is not an operator