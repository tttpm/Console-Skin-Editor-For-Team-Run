from time import sleep
from os import system  #built-in libs
import zlib
import base64

import keyboard as kb
import colorama
from PIL import Image, ImageColor, ImageDraw #other libs

import ImgConv #yea

colorama.init()

color = lambda r, g, b: f"\033[38;2;{r};{g};{b}m"

default = '\033[0m'
sqr = '■'
selected = [0, 0]
current_color = (255,255,255)
mode = 'brush'
suncat = 'trSkin17ZZBCoAwDAS/VFCk4qmt5v9P8iBIsTVuYqwIelq0ZidhJTq3XZODBdFRiF43r8NbLF0InnKhMLWqA1rMQ1pSzMWZaVUo6hiiMqaMENVRwEu9rERL5jIJusM/8yeYd5F8H8aYi+eYy0ci5hIVgWcImTNlZRy+Ol6kC4YQuXPJjGxPEBVJCzJwxXjV2RCFpEE29k/YnJBZJVbZQPayuVBkg+mrpbj/U0r0gmgAf7NBxH0F'
b, w, g, a = (174,69,157), (255,255,255), (160, 160, 160), None

bg = [

[a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a], 
[a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a, a], 
[a, a, a, g, g, w, w, w, w, w, w, w, w, w, w, w, w, a, a, a],
[a, a, g, g, w, w, w, w, w, w, w, w, w, w, w, w, w, w, a, a],
[a, a, g, g, w, w, w, w, w, w, w, w, w, w, w, w, w, w, a, a],
[a, a, g, g, w, w, w, w, w, w, b, b, w, w, b, b, w, w, a, a],
[a, a, g, g, w, w, w, w, w, w, b, b, w, w, b, b, w, w, a, a],
[a, a, g, g, w, w, w, w, w, w, b, b, w, w, b, b, w, w, a, a],
[a, a, g, g, w, w, w, w, w, w, b, b, w, w, b, b, w, w, a, a],
[a, a, g, g, w, w, w, w, w, w, w, w, w, w, w, w, w, w, a, a],
[a, a, g, g, w, w, w, w, w, w, w, w, w, w, w, w, w, w, a, a],
[a, a, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, a, a],
[a, a, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, a, a],
[a, a, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, a, a],
[a, a, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, b, a, a],
[a, a, a, b, b, b, b, b, b, b, b, b, b, b, b, b, b, a, a, a],
[a, a, a, a, a, a, b, b, b, a, a, a, a, b, b, b, a, a, a, a],
[a, a, a, a, a, a, b, b, b, a, a, a, a, b, b, b, a, a, a, a]

]

picture = [[a] * 20 for i in range (18)]

pic_size = (len(picture), len(picture[0]))

def print_pic():
    print('#'*62)
    for i in range(pic_size[0]):
        print('#', end = '')
        for j in range(pic_size[1]):
            
            if not picture[i][j]:
                clr, pix = default, ' '
                if bg[i][j]:
                    clr, pix = color(*bg[i][j]), 'e'
            else:
                clr, pix = color(*picture[i][j]), sqr


            if [i, j] == selected:
                l, r = '[', ']'
            else:
                l, r = ' ', ' '

            print(l + clr + pix + default + r, end = '') 
        
        print("#")
    print('#'*62)

def decode_hex(hexx):
    if hexx[-2:] == '00' and len(hexx) == 8: return a
    hexx = hexx.upper()
    digits = '0123456789ABCDEF'
    cat = list(map(lambda d: digits.index(d), hexx[:]))
    return (cat[0]*16 + cat[1], cat[2]*16 + cat[3], cat[4]*16 + cat[5])
        


def encode_hex(rgb):
    res = ''
    digits = '0123456789ABCDEF'
    res += digits[rgb[0]//16]+digits[rgb[0]%16]
    res += digits[rgb[1]//16]+digits[rgb[1]%16]
    res += digits[rgb[2]//16]+digits[rgb[2]%16]
    return res + 'FF'
        
def export_skin():
    res = ''
    for line in picture:
        for pixel in line:
            if not pixel:
                res += '00000000;'
                continue
            res += encode_hex(pixel) + ';'
            
    if not res: return 'trSkin1'
    deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed = deflate_compress.compress(bytes(res, encoding ='utf-8')) + deflate_compress.flush()
    encrypted = base64.b64encode(compressed)
    return "trSkin1" + encrypted.decode()

def import_skin(trskin):
    compressed = base64.b64decode(trskin[7:])
    hexes = str(zlib.decompress(compressed, -zlib.MAX_WBITS).decode()).split(';')
    hexes.pop()
    i, j = 0, 0
    for hehex in hexes:
        if j == pic_size[1]:
            i += 1
            j = 0
        picture[i][j] = decode_hex(hehex)
        j += 1
    

def fill():
    x, y = selected
    checked = [[0]*pic_size[1] for i in range(pic_size[0])]
    start_color = picture[x][y]
    filled = [(x, y)]
    while filled:
        filling = []
        for pixel in filled:
            x, y = pixel
            if x > 0 and not checked[x-1][y]:
                checked[x-1][y] = 1
                if picture[x-1][y] == start_color:
                    filling.append((x-1, y))
                    
            if y > 0 and not checked[x][y-1]:
                checked[x][y-1] = 1
                if picture[x][y-1] == start_color:
                    filling.append((x, y-1))
                    
            if x < pic_size[0] - 1 and not checked[x+1][y]:
                checked[x+1][y] = 1
                if picture[x+1][y] == start_color:
                    filling.append((x+1, y))
                    
            if y < pic_size[1] - 1 and not checked[x][y+1]:
                checked[x][y+1] = 1
                if picture[x][y+1] == start_color:
                    filling.append((x, y+1))
                
            picture[x][y] = current_color
        filled = filling[::]
        
x = b
logo = [

[w, w, w, w, w, w, w, w, w],
[w, x, x, x, w, x, x, x, w],
[w, w, x, w, w, x, w, x, w],
[w, w, x, w, w, x, x, w, w],
[w, w, x, w, w, x, w, x, w],
[w, w, x, w, w, x, w, x, w],
[w, w, w, w, w, w, w, w, w],
[w, w, w, x, x, x, w, w, w],
[w, w, w, w, w, w, w, w, w]

]

def print_logo():
    for i in range(9):
        for j in range(9):
            pix = sqr
            if i == 7:
                if j == 3: pix = 'C'
                if j == 4: pix = 'S'
                if j == 5: pix = 'E'

                
            print(color(*logo[i][j])+pix+default, end = ' ')
        print()


def get_png(skin):
    
    compressed = base64.b64decode(skin.replace("trSkin1", ""))
    decompressed = str(zlib.decompress(compressed, -zlib.MAX_WBITS).decode())

    img = Image.new("RGBA",(20, 18), (0,0,0,0))

    draw = ImageDraw.Draw(img)

    width = img.size[0]
    height = img.size[1]


    hexColorsList = decompressed.split(";")
    colorList = []

    for color in hexColorsList:
        try:
            colorList.append(ImageColor.getcolor("#" + color, "RGBA"))
        except ValueError:
            break
    x = 0
    y = 0
    for color in colorList:
        xTimes = 0
        yTimes = 0
        if x == width:
            y += 1
            x = 0         
        draw.point((x, y), color)
        x += 1
    return img




print_logo()
print('Console Skin Editor for Team Run (by '+color(255,102,0)+'Tipim'+default+')')
print('press [esc] to start')
kb.wait('esc')

while 1:
    try:
        system("cls")
        print_pic()
        print(f"\ncurrent color = {color(*current_color)}this{default}\ncurrent mode = {mode}\n\nto change smth or import/export skin, press [esc];\npress [ctrl] for help")
        key = kb.read_key()
        
        if key == 'down' and selected[0] < pic_size[0] - 1: selected[0] += 1
        if key == 'up' and selected[0] > 0: selected[0] -= 1
        if key == 'right' and selected[1] < pic_size[1] - 1: selected[1] += 1
        if key == 'left' and selected[1] > 0: selected[1] -= 1

        if key == 'esc':
            print('\n\n"c" - change color\n"m" - change mode\n"e" - export skin\n"i" - import skin\n"cl" - clear canvas')
            action = input("\nwhat do you want to do?\n>> ")

            if action == 'cl': picture = [[a] * 20 for i in range (18)][::]
            
            elif action == 'c':
                print('enter six-digit HEX (like #ABCDEF) of new color:\n>> ', end = '')
                HEX = input()[1:]
                v = decode_hex(HEX)
                if v: current_color = v

            elif action == "m":
                print('\n\n"b" - brush\n"e" - eraser\n"p" - pipette\n"f" - fill')
                m = input("what do you need?\n>> ")
                qqq = {'b':'brush','e':'eraser', 'p': 'pipette', 'f':'fill'}
                if m in qqq.keys():
                    mode = qqq[m]
                else:
                    print("ayo wtf")
                    print('press [esc] to continue')
                    kb.wait("esc")

                
            elif action == 'e':
                print('your skin:')
                text = export_skin()
                print(text)
                bebra = input('\nwrite "png" to save skin as .PNG file;\nwrite "otrmap" to save skin as .OTRMAP file\nwrite something else to continue\n>> ')

                png = get_png(text)
                
                if bebra == 'png':
                    path = input("\nenter full path to file (if file with same name exists, it will be rewritten):\n>> ")
                    png.save(path)
                    print('done!\npress [esc] to continue')
                    kb.wait("esc")
                    
                if bebra == 'otrmap':
                    path = input("\nenter full path to file (if file with same name exists, it will be rewritten):\n>> ")
                    size = float(input("size of pixel:\n>> "))
                    layer = int(input("\nlayer:\n>> "))
                    ImgConv.convert(png, path, size, layer)
                        
                    print('done!\npress [esc] to continue')
                    kb.wait("esc")

            elif action == 'i':
                inp = input('enter your skin:\n>> ')
                if inp.lower() in ['suncat', 'tdf', 'солнцекот', 'cjkywtrjn']:
                    import_skin(suncat)
                else:
                    import_skin(inp)
            else:
                print('unknown command!')
                print('press [esc] to continue')
                kb.wait("esc")

                
        if key == 'space':
            if mode == 'brush': picture[selected[0]][selected[1]] = current_color

            elif mode == 'eraser': [selected[0]][selected[1]] = a

            elif mode == 'pipette':current_color = picture[selected[0]][selected[1]] 

            elif mode == 'fill': fill()
        if key == 'ctrl':
            print('\n\narrow keys - move "cursor"')
            print('space - "click" on selected pixel')
            print(f'"e" means that pixel is actually empty, but its {color(255,0,0)}c{color(255,127,0)}o{color(255,255,0)}l{color(0,255,0)}o{color(0,255,255)}r{color(0,0,255)}e{color(75,0,130)}d{default} for your convenience')
            print('\ni hope u enjoy my little project :p')
            print('(and sorry for my not good english)')

            print(f'\n\nspecial thanks:\n{color(255,255,255)}\ngstroin{default} for help and some code\n{color(108,174,69)}coolamoeba{default} for few ideas\n{color(255,200,200)}tdf {default}for being the cutest girl in the whole universe <3 <3 <3')
            
            print('\npress [esc] to continue')
            kb.wait("esc")

            
    except Exception as e:
        print('ERROR CAUGHT:', e)
        print('press [esc] to continue')
        kb.wait("esc")


