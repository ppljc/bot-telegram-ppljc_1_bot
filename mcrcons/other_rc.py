from mcrcon import MCRcon

# Добавление игрока в вайтлист
async def other__rc__server_online():
    try:
        with MCRcon('localhost', 'password') as mcr:
            response = mcr.command('list')
        return True
    except:
        return False