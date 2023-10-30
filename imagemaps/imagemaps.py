import cv2

from keyboards import client_kb

def format_map(name):
    possible_ratio = [[1.0,"1:1",["1:1","2:2", "3:3", "4:4"]], 
                      [0.5,"1:2",["1:2","2:4", "3:6", "4:8"]], 
                      [2.0,"2:1",["2:1","4:2", "6:3", "8:4"]], 
                      [1.5,"3:2",["3:2","6:4", "9:6", "12:8"]], 
                      [0.6,"2:3",["2:3","4:6", "6:9", "8:12"]]]
    image = cv2.imread(f"C:\\Users\\stepa\\Documents\\Repos\\ES53BOT\\imagemaps\\maps\\{name}.png")
    height = image.shape[0]
    width = image.shape[1]
    cropped_height = height//128
    cropped_width = width//128
    ratio = cropped_height/cropped_width
    closest = [20, 0]
    for rat in possible_ratio:
        if closest[0] > abs(ratio - rat[0]):
            closest = [abs(ratio-rat[0]), rat]
    image = cv2.resize(image, (128*int(closest[1][1][0]), 128*int(closest[1][1][2])))
    cv2.imwrite(f"C:\\Users\\stepa\\Documents\\Repos\\ES53BOT\\imagemaps\\maps\\{name}.png",image)
    return([name, closest[1]])


def resize_map(name: str, value: int):
    image = cv2.imread(f"C:\\Users\\stepa\\Documents\\Repos\\ES53BOT\\imagemaps\\maps\\{name}.png")
    shape = image.shape
    image = cv2.resize(image, (shape[0]*value, shape[1]*value))
    cv2.imwrite(f"C:\\Users\\stepa\\Documents\\Repos\\ES53BOT\\imagemaps\\maps\\{name}.png", image)