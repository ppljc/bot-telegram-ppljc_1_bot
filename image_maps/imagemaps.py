# -------------- Импорт функций --------------
import math
from PIL import Image

# -------------- Импорт локальных функций --------------
import config

# -------------- Функции форматирования изображений --------------
def imagemaps_pillow_ImageFormat(name):
    ratio_possible = [1.0, 0.5, 2.0, 1.5, 0.6]
    ratio_list = {
        1.0: [1, 1],
        0.5: [1, 2],
        2.0: [2, 1],
        1.5: [3, 2],
        0.6: [2, 3],
    }
    image = Image.open(fp=f'{config.imagemaps_path}\\{name}.png')
    ratio = image.height / image.width
    closest_number = min(ratio_possible, key=(lambda x: abs(x - ratio)))
    height_absolute = 512 * ratio_list[closest_number][0]
    width_absolute = 512 * ratio_list[closest_number][1]
    size_new = (width_absolute, height_absolute,)
    print(f'ratio: {ratio}\n'
          f'closest_number: {closest_number}\n'
          f'height_absolute: {height_absolute}\n'
          f'width_absolute: {width_absolute}\n'
          f'size_new: {size_new}')
    image = image.resize(size_new)
    image.save(f'{config.imagemaps_path}\\{name}.png')
    return ratio_list[closest_number]

def imagemaps_pillow_ImageScale(name, ratio):
    image = Image.open(fp=f'{config.imagemaps_path}\\{name}.png')
    height = 128 * ratio[0]
    width = 128 * ratio[1]
    size_new = (width, height,)
    image = image.resize(size_new)
    image.save(f'{config.imagemaps_path}\\{name}.png')