# Python модули
import aiofiles


# Функции
async def add_values(values: list[str], file: str) -> None:
    try:
        async with aiofiles.open(f'{file}.txt', 'r') as f:
            values_old = list(map(int, await f.readlines()))
    except FileNotFoundError:
        values_old = []
    async with aiofiles.open(f'{file}.txt', 'w') as f:
        await f.write('\n'.join(map(str, values_old + values)))


async def read_values(file: str) -> list:
    try:
        async with aiofiles.open(f'{file}.txt', 'r') as f:
            values = list(map(int, await f.readlines()))
    except FileNotFoundError:
        await add_values(values=[''], file=file)
        values = []
    return values


async def remove_values(values: list[str], file: str) -> None:
    try:
        async with aiofiles.open(f'{file}.txt', 'r') as f:
            values_list = list(map(int, await f.readlines()))
        for value in values:
            values_list.remove(int(value))
        async with aiofiles.open(f'{file}.txt', 'w') as f:
            await f.write('\n'.join(map(str, values_list)))
    except FileNotFoundError:
        await add_values(values=[''], file=file)
