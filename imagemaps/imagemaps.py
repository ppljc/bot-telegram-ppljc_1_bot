import cv2

def format_map(name):
    possible_ratio = [[1.0,"1:1"], [0.5,"1:2"], [2.0,"2:1"], [1.5,"3:2"], [0.6,"2:3"]]
    image = cv2.imread(f"C:\\Users\\stepa\\Documents\\Repos\\ES53BOT\\imagemaps\\maps\\{name}.png")
    height = image.shape[0]
    width = image.shape[1]
    cropped_height = height//128
    cropped_width = width//128
    ratio = cropped_height/cropped_width
    closest = [20, 0]
    for rat in possible_ratio:
        #print(abs(ratio - rat[0]))
        if closest[0] > abs(ratio - rat[0]):
            closest = [abs(ratio-rat[0]), rat]
    image = cv2.resize(image, (128*int(closest[1][1][0]), 128*int(closest[1][1][2])))
    cv2.imwrite(f"C:\\Users\\stepa\\Documents\\Repos\\ES53BOT\\imagemaps\\maps\\{name}.png",image)
    return(closest[1][1])