from mcrcon import MCRcon

async def add_whitelist(admin_id, username):
    with MCRcon('localhost', 'password') as mcr:
        response = mcr.command(f'whitelist add {username}')
    return response

async def rem_whitelist(admin_id, username):
    with MCRcon('localhost', 'password') as mcr:
        response = mcr.command(f'whitelist remove {username}')
    return response