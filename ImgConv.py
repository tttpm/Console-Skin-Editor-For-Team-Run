#yes, this i took from gstroin's TRIC
from PIL import Image

def convert(img, level_path, pix_size = 1, layer = 0):
    offset = 1 - pix_size
    
    pixels = img.load()
    level = open(level_path, "w", encoding = "utf-8")
    last_obj = 0
    level.write("info;\n")
        
    img.mode = 'RGBA'
        
    i = 0
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            
            red = pixels[x, img.size[1] - 1 - y][0]
            green = pixels[x, img.size[1] - 1 - y][1]
            blue = pixels[x, img.size[1] - 1 - y][2]
            alpha = pixels[x, img.size[1] - 1 - y][3]

            if not alpha:
                continue
            
            color = ('%02x%02x%02x%02x' % (red, green, blue, alpha)).upper()
            
            level.write("20;" + str(last_obj + 1 + i) + ";" + str(x - (x * offset)).replace(".", ",") + ";" + str(y + 1 - img.size[1] * pix_size- (y * offset)).replace(".", ",") + ";" + str(pix_size).replace(".", ",") + ";" + str(pix_size).replace(".", ",") + ";;C;" + color + ";" + str(layer) + ";C;\n")
            last_obj += 1
    level.close()

def picture_to_text(img, levelPath, size):
    imgData = img.load()
    level = open(levelPath, "w")
    lastObj = 0
    level.write("info;\n")
    
        
    string = "<size=0>made by gstroin, used by tipim :D"
    string += "<size=" + str(size) + ">"
    for y in range(0, img.size[1]):
        for x in range (0, img.size[0]):
            red = imgData[x, y][0]
            green = imgData[x, y][1]
            blue = imgData[x, y][2]
            alpha = imgData[x, y][3]
            hexColor = "%02x%02x%02x%02x" % (red, green, blue, alpha)
            string += "<color=#" + hexColor + "><mark=#" + hexColor + ">q<sub>q</sub>"
        string += "<br>"
    print("17;0;0;0;1;1;;¶;" + string + ";¶;\n", file = level)
    lastObj += 1
    return string
