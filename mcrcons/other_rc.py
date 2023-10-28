from mcrcon import MCRcon

# Добавление игрока в вайтлист
async def other_rc_ServerOnline():
    try:
        with MCRcon('localhost', 'password') as mcr:
            response = mcr.command('list')
        return True
    except:
        return False