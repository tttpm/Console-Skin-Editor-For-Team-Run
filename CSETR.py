from time import sleep
from os import system  #built-in libs
import zlib
import base64
import traceback

import keyboard as kb
import colorama
from PIL import Image, ImageColor, ImageDraw #other libs

import ImgConv #yeah

colorama.init()

picture = [[None] * 20 for i in range (18)]

pic_size = (len(picture), len(picture[0]))

#################################################################################################################################################################################################
def color(r,g,b, fore = True, back = False):
    
    res = ''
    if fore: res += f"\033[38;2;{r};{g};{b}m"
    if back: res += f"\033[48;2;{r};{g};{b}m"
    return res
   
def decode_hex(hexx):
    if len(hexx) == 8:
        if hexx[-2:] == '00':
            return None
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


def skin_to_png(skin):
    
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


def import_skin(trskin):
    res = [[None]*pic_size[1] for i in range(pic_size[0])]
    compressed = base64.b64decode(trskin[7:])
    hexes = str(zlib.decompress(compressed, -zlib.MAX_WBITS).decode()).split(';')
    hexes.pop()
    i, j = 0, 0
    for hehex in hexes:
        if j == pic_size[1]:
            i += 1
            j = 0
        res[i][j] = decode_hex(hehex)
        j += 1
    return res


def export_skin(pic):
    res = ''
    for line in pic:
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



##################################################################################################################################################################################################
clear_color = '\033[0m'


try:
    with open("CSETR_config.txt") as file:
        text = file.read().split('\n')
    text.pop()
    
    bgc_hex, def_hex, bg_skin = text
    
    
except:
    
    bgc_hex = "0c0c0c"
    def_hex = 'cccccc'
    bg_skin = 'trSkin1MzCAAGuDUcYAMRwNQNDNDcFwgwJ6MIaQU8lz/Eh2s6OriamlCzKDPDWjbh5182Bw82i5gd/NZi5GTmZGQMVwBmYM0pMx6uZRN1Pi5kHieOo3+Sizi55OHSRuBgA='

def save_config():
    with open("CSETR_config.txt", 'w') as file:
        print(bgc_hex,
              def_hex,
              bg_skin,
              
              file = file, sep = '\n')
    
bgcf = color(*decode_hex(bgc_hex))
bgcb = color(*decode_hex(bgc_hex), back = True, fore = False)
default = color(*decode_hex(def_hex))
bg = import_skin(bg_skin)

sqr = '■'
selected = [0, 0]
current_color = (255,255,255)
mode = 'brush'
suncat = 'trSkin17ZZBCoAwDAS/VFCk4qmt5v9P8iBIsTVuYqwIelq0ZidhJTq3XZODBdFRiF43r8NbLF0InnKhMLWqA1rMQ1pSzMWZaVUo6hiiMqaMENVRwEu9rERL5jIJusM/8yeYd5F8H8aYi+eYy0ci5hIVgWcImTNlZRy+Ol6kC4YQuXPJjGxPEBVJCzJwxXjV2RCFpEE29k/YnJBZJVbZQPayuVBkg+mrpbj/U0r0gmgAf7NBxH0F'
b, w, g, a = (174,69,157), (255,255,255), (160, 160, 160), None



def print_pic():
    print(default + '#'*62)
    for i in range(pic_size[0]):
        print('#', end = '')
        for j in range(pic_size[1]):
            #back and fore
            
            if not picture[i][j]:
                
                back, fore, pix = bgcb, bgcf, 'e'
                
                if bg[i][j]:
                    back, fore, pix = bgcb, color(*bg[i][j]), 'e'
                    
            else:
                back, fore, pix = color(*picture[i][j], back = True, fore = False), color(*picture[i][j]), sqr


            if [i, j] == selected:
                if not current_color: lmao = color(*decode_hex(bgc_hex))
                else: lmao = color(*current_color)
                print(back+lmao+'['+fore+pix+lmao+']'+clear_color, end = '')
                
            else:
                print(back+fore+' '+pix+' '+clear_color, end = '') 
        
        print(default + "#")
    print(default + '#'*62)
 

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


def import_png(img):
    
    pixels = img.load()

    i = 0
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            
            r,g,b,alpha = pixels[x, y]

            if alpha < 100:
                picture[y][x] = a
            else:
                picture[y][x] = (r,g,b)



##################################################################################################################################################################################################


w, x = (255,255,255),(0,0,0)
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
            r, g, b = logo[i][j] 
            pix = sqr
            clr = color(*logo[i][j], back = True)
            if i == 7:
                if 2 < j < 6:
                    clr = color(*logo[i][j]) + color(*w, fore = False, back = True)
                    pix = {3:'C', 4:'S', 5:'E'}[j]

                
            print(clr+pix+' '+clear_color, end = '')
        print()


print_logo()
print(default+'Console Skin Editor for Team Run (by '+color(255,102,0, back=False)+'Tipim'+default+')')
print('press [alt] to start')
kb.wait('alt')
while 1:
    try:
        system("cls")
        print_pic()
        if not current_color: lol1, lol2 = default, 'empty'
        else: lol1, lol2 = color(*current_color), '#' + encode_hex(current_color)[:-2]
        print(f"\ncurrent color = {lol1+lol2+default}\ncurrent mode = {mode}\n\nto open menu, press [esc];\npress [ctrl] for help")
        key = kb.read_key()
        
        if key == 'down' and selected[0] < pic_size[0] - 1: selected[0] += 1
        if key == 'up' and selected[0] > 0: selected[0] -= 1
        if key == 'right' and selected[1] < pic_size[1] - 1: selected[1] += 1
        if key == 'left' and selected[1] > 0: selected[1] -= 1

        if key == 'esc':
            print('''

"c" - change color
"m" - change mode
"e" - export skin
"i" - import skin
"cl" - clear canvas
"cu" - customize Editor''')
            action = input("\nwhat do you want to do?\n>> ")

            if action == 'cl': picture = [[a] * 20 for i in range (18)][::]
            
            elif action == 'c':
                print('enter six-digit HEX (like #ABCDEF) of new color:\n>> ', end = '')
                HEX = input().replace('#','')
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
                print('your skin:\n')
                text = export_skin(picture)
                print(text)
                bebra = input('\nwrite "png" to save skin as .PNG file;\nwrite "otrmap" to save skin as .OTRMAP file\nwrite something else to continue\n>> ')

                png = skin_to_png(text)
                
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
                amogum = input('\nLoad skin from...\n"t" - text\n"i" - image (PNG)\n"b" - background\n>> ')
                if amogum == 't':
                    inp = input('enter your skin:\n>> ')
                    if inp.lower() in ['suncat', 'tdf', 'солнцекот', 'cjkywtrjn']:
                        picture = import_skin(suncat)[::]
                    else:
                        picture = import_skin(inp)[::]
                    print('press [esc] to continue')
                    kb.wait("esc")
                    continue
                elif amogum == 'i':
                    print(f"\nAttention! CSETR does {color(252,0,0)}not{default} support RGBA, only RGB!")
                    
                    path = input("\nenter full path to your image:\n>> ")
                    png = Image.open(path)

                    if png.size[0] != 20 or png.size[1] != 18:
                        print('image must be 20x18')
                        print('press [esc] to continue')
                        kb.wait("esc")
                        continue
                        
                    import_png(png)
                    
                    print('done!\npress [esc] to continue')
                    kb.wait("esc")
                elif amogum == "b":
                    picture = bg[::]
                    print('done!\npress [esc] to continue')
                    kb.wait("esc")

            elif action == 'cu':
                print(f'''

current parameters:


background color - {bgcf}#{bgc_hex}{default}(default - #0c0c0c)


UI color - #{def_hex} (default - #cccccc)


background skin - {bg_skin}

(default - trSkin1MzCAAGuDUcYAMRwNQNDNDcFwgwJ6MIaQU8lz/Eh2s6OriamlCzKDPDWjbh5182Bw82i5gd/NZi5GTmZGQMVwBmYM0pMx6uZRN1Pi5kHieOo3+Sizi55OHSRuBgA=)
''')
                act = input('\n"bc" - change background color\n"bs" - change background skin\n"ui" - change UI color\n>> ')
                if act == 'bc':
                    bgc_hex = input("new background color:\n>> ").replace('#','')
                    bgcb = color(*decode_hex(bgc_hex), back  = True, fore = False)
                    bgcf = color(*decode_hex(bgc_hex))
                elif act == 'ui':
                    def_hex = input("new UI color:\n>> ").replace('#','')
                    default = color(*decode_hex(def_hex))
                elif act == 'bs':
                    bg_skin = input("new background skin:\n>> ")
                    bg = import_skin(bg_skin)
                    
                
                save_config()
                
                print('done!\npress [esc] to continue')
                kb.wait("esc")
                
                
            else:
                print('unknown command!')
                print('press [esc] to continue')
                kb.wait("esc")

                
        if key == 'space':
            if mode == 'brush': picture[selected[0]][selected[1]] = current_color

            elif mode == 'eraser': picture[selected[0]][selected[1]] = a

            elif mode == 'pipette':
                current_color = picture[selected[0]][selected[1]]

            elif mode == 'fill': fill()
        if key == 'ctrl':
            print('\n\narrow keys - move "cursor"')
            print('space - "click" on selected pixel')
            print(f'"e" means that pixel is actually empty, but its {color(255,0,0)}c{color(255,127,0)}o{color(255,255,0)}l{color(0,255,0)}o{color(0,255,255)}r{color(0,0,255)}e{color(75,0,130)}d{default} for your convenience')
            print('\ni hope u enjoy my little project :p')
            print('(and sorry for my not good english)')

            print(f'\n\nspecial thanks:\n{color(255,255,255)}\ngstroin{default} for help and some code\n{color(108,174,69)}coolamoeba{default} for few cool ideas\n{color(255,200,200)}tdf {default}for being the cutest girl in the whole universe <3 <3 <3')
            
            print('\npress [esc] to continue')
            kb.wait("esc")

            
    except Exception:
        print('\nERROR CAUGHT:\n')
        traceback.print_exc()
        print('\npress [esc] to continue')
        kb.wait("esc")
