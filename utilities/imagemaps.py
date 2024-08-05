# Python модули
from PIL import Image

import asyncio
import concurrent.futures


# Локальные модули
from utilities.logger import logger


# Переменные
__all__ = ['image_format', 'image_scale']


# Функции
def side_image_format(name: str):
    ratio_possible = [1.0, 0.5, 2.0, 1.5, 0.6]
    ratio_list = {
        1.0: [1, 1],
        0.5: [1, 2],
        2.0: [2, 1],
        1.5: [3, 2],
        0.6: [2, 3],
    }
    image = Image.open(fp=f'images/{name}.png')
    ratio = image.height / image.width
    closest_number = min(ratio_possible, key=(lambda x: abs(x - ratio)))
    height_absolute = 512 * ratio_list[closest_number][0]
    width_absolute = 512 * ratio_list[closest_number][1]
    size_new = (width_absolute, height_absolute,)
    logger.debug(
        f'USER=BOT, MESSAGE="ratio={ratio}, closest_number={closest_number}, '
        f'height_absolute={height_absolute}, width_absolute={width_absolute}, size_new={size_new}"'
    )
    image = image.resize(size_new)
    image.save(f'images/{name}.png')
    return ratio_list[closest_number]


async def image_format(name: str):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, side_image_format, name)
    return result


def side_image_scale(name: str, ratio: list):
    image = Image.open(fp=f'images/{name}.png')
    height = 128 * ratio[0]
    width = 128 * ratio[1]
    size_new = (width, height,)
    image = image.resize(size_new)
    image.save(f'images/{name}.png')


async def image_scale(name: str, ratio: list):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, side_image_scale, name, ratio)
    return result
