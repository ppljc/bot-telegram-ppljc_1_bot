from mcrcon import MCRcon

# Получение статуса сервера
async def client__rc__server_status(user_id):
    with MCRcon('localhost', 'password') as mcr:
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
        data = [tps_val, list_val, list_users]
    return data