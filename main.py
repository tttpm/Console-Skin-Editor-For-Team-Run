#built-in libs
from time import sleep
from os import system, path, mkdir          
from zlib import decompress, compressobj, MAX_WBITS, DEFLATED 
from base64 import b64encode, b64decode                        
from traceback import print_exc
from copy import deepcopy as copy
from sys import platform, stdout


#other libs
try:
    from keyboard import read_key, wait
except ImportError:
    print('sorry, but u must be root on linux')
    input()
    exit(0)

from requests import get
from colorama import init as col_init
from PIL import Image, ImageColor, ImageDraw 
#import happiness :)


from utils import color, decode_hex, encode_hex, skin_to_png, skin_to_list, list_to_skin, flush_input, clear_color, suncat, TRSS_req




col_init()

picture = copy([[None] * 20 for i in range (18)])



bgc_hex = "0c0c0c"
ui_hex = 'cccccc'
bg_skin = 'trSkin1MzCAAGuDUcYAMRwNQNDNDcFwgwJ6MIaQU8lz/Ah0s6OriamlCzKDQsWjbh518wC6ebTcINLNZi5GTmZGQMVwBmYM0pMx6uZRN1Pi5kHieOo3+Sizi55OHSRuBgA='
max_history = 500
TRSS_token = None
    
try:
    with open(r"CSETR\config.txt") as file:
        text = file.read().split('\n')

    try:
        *_, bgc_hex = text[0].split()
        assert decode_hex(bgc_hex)
    except:
        pass
    
    try:
        *_, ui_hex = text[1].split()
        assert decode_hex(ui_hex)
    except:
        pass

    try:
        *_, bg_skin = text[2].split()
        skin_to_list(bg_skin)
    except:
        pass

    try:
        *_, max_history = text[3].split()
        max_history = int(max_history)
        assert max_history > 0 or max_history == -1
    except:
        max_history = 500

    try:
        *_, TRSS_token = text[4].split()
        assert 'error_code' not in TRSS_req('users.php', action = 'get_user_by_token', token = TRSS_token)
    except:
        TRSS_token = None
    
except:
   pass

default_hotkeys = {
        'start': 'alt',
        'menu': 'shift',
        'help': 'ctrl',
        'cursor_up': 'up',
        'cursor_down': 'down',
        'cursor_left':'left',
        'cursor_right': 'right',
        'click': 'space',
        'exit': 'esc',
        'brush': 'b',
        'eraser': 'e',
        'pipette': 'p',
        'fill': 'f',
        'color': 'c',
        'undo': 'z',
        'redo': 'y'
        }
try:
    with open(r"CSETR\hotkeys.txt") as file:
        text = file.read().split('\n')
    text = list(filter(lambda x: x, text))

    hotkeys = dict(map(tuple, map(lambda x: x.split(), text)))

    for key in default_hotkeys:
        assert key in hotkeys

except:
    hotkeys = default_hotkeys



def save_config():
    if not path.exists("CSETR"): mkdir("CSETR")
    with open(r"CSETR\config.txt", 'w') as file:
        print('background color: '+bgc_hex,
              'UI color: ' + ui_hex,
              'background skin: ' + bg_skin,
              'undo/redo history size: ' + str(max_history),
              'TRSS token(this is ur personal token, do not show it anybody lol): ' + TRSS_token,

              file = file, sep = '\n', end = '')


        
def save_hotkeys():
    if not path.exists("CSETR"): mkdir("CSETR")
    with open(r"CSETR\hotkeys.txt", 'w') as file:
        text = ''
        for key in hotkeys.keys():
            text += key + ' ' + hotkeys[key] + '\n'
        text.strip()
        print(text, file = file, end = '')


        
bgcf = color(*decode_hex(bgc_hex))
bgcb = color(*decode_hex(bgc_hex), back = True, fore = False)
ui_color = color(*decode_hex(ui_hex))
bg = skin_to_list(bg_skin)

sqr = '■'
selected = [0, 0]
current_color = (255,255,255)
mode = 'brush'
empty = None



def print_pic():
    print(ui_color + '#'*62)
    for i in range(18):
        print('#', end = '')
        for j in range(20):

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

        print(ui_color + "#")
    print(ui_color + '#'*62)



def fill():
    x, y = selected
    checked = [[0]*20 for i in range(18)]
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

            if x < 17 and not checked[x+1][y]:
                checked[x+1][y] = 1
                if picture[x+1][y] == start_color:
                    filling.append((x+1, y))

            if y < 19 and not checked[x][y+1]:
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
                picture[y][x] = empty
            else:
                picture[y][x] = (r,g,b)


def png_to_otrmap(img, level_path, pix_size = 1, layer = 0):
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


def back(message='done! '):
    print(f'{message}press [{hotkeys["exit"]}] to continue')
    wait(hotkeys['exit'])


        
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

history = [list_to_skin(picture)]
ur = -1

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


version = '1.0'
print(ui_color+'Console Skin Editor for Team Run v'+version+' by '+color(255,102,0)+'Tipim'+ui_color)

#yes, i took code from TRIC again :)
try:
    latest = get('https://pastebin.com/raw/MLSzvmus').text
    if version != latest:
        print(color(255, 255, 0) + 'new version available!' + clear_color)
except:
    pass

print(f'press [{hotkeys["start"]}] to start')
wait(hotkeys['start'])
while 1:
    try:
        sleep(0.1)
        system("cls" if platform == 'win32' else 'clear')
        picture = skin_to_list(history[ur])
        print_pic()
        if not current_color: lol1, lol2 = ui_color, 'empty'
        else: lol1, lol2 = color(*current_color), '#' + encode_hex(*current_color)[:-2]
        print(f"\ncurrent color = {lol1+lol2+ui_color}\ncurrent mode = {mode}\n\nto open menu, press [{hotkeys['menu']}];\npress [{hotkeys['help']}] for help")
        key = read_key()
        changed = 0 
         
        if key == hotkeys['cursor_down'] and selected[0] < 17: selected[0] += 1
        elif key == hotkeys['cursor_up'] and selected[0] > 0: selected[0] -= 1
        elif key == hotkeys['cursor_right'] and selected[1] < 19: selected[1] += 1
        elif key == hotkeys['cursor_left'] and selected[1] > 0: selected[1] -= 1
        elif key == hotkeys['brush']: mode = 'brush'
        elif key == hotkeys['eraser']: mode = 'eraser'
        elif key == hotkeys['pipette']: mode = 'pipette'
        elif key == hotkeys['fill']: mode = 'fill'
        elif key == hotkeys['color']: change_color()

            

        elif key == hotkeys['menu']:
            flush_input()
            print('''

"c" - change color
"m" - change mode
"e" - export skin
"i" - import skin
"cl" - clear canvas
"cu" - customize Editor
"h" - edit hotkeys
"u" - undo
"r" - redo
"f4" - close CSETR
"up" - upload skin to TRSS (https://drive.google.com/file/d/1RqncB4_rXmMGZmGo_YKDXSLaNfJ99KkO)''')
            action = input("\nwhat do you want to do?\n>> ")

            if action == 'cl':
                picture = copy([[empty] * 20 for i in range (18)])
                changed = 1

            elif action == 'c':
                flush_input()
                HEX = input('''\nenter six-digit HEX (like #123DEF) of new color:\n>> ''').replace('#','')
                current_color = decode_hex(HEX)
    


            elif action == "m":
                print('\n\n"b" - brush\n"e" - eraser\n"p" - pipette\n"f" - fill')
                m = input("what do you need?\n>> ")
                qqq = {'b':'brush','e':'eraser', 'p': 'pipette', 'f':'fill'}
                if m in qqq.keys():
                    mode = qqq[m]
                else:
                    print("ayo wtf")
                    


            elif action == 'e':
                print('your skin:\n')
                text = list_to_skin(picture)
                print(text)
                bebra = input('\nwrite "png" to save skin as .PNG file;\nwrite "otrmap" to save skin as .OTRMAP file\nwrite something else to continue\n>> ')

                png = skin_to_png(text)

                if bebra == 'png':
                    path = input("\nenter full path to file (if file with same name exists, it will be rewritten):\n>> ")
                    png.save(path)
                    back()

                if bebra == 'otrmap':
                    path = input("\nenter full path to file (if file with same name exists, it will be rewritten):\n>> ")
                    size = float(input("size of pixel:\n>> "))
                    layer = int(input("\nlayer:\n>> "))
                    png_to_otrmap(png, path, size, layer)

                    back()

            elif action == 'i':
                amogum = input('\nLoad skin from...\n"t" - text\n"i" - image (PNG)\n"b" - background\n>> ')
                if amogum == 't':
                    inp = input('enter your skin:\n>> ')
                    if inp.lower() in ['suncat', 'tdf', 'солнцекот', 'cjkywtrjn']:
                        picture = copy(skin_to_list(suncat))
                    else:
                        picture = copy(skin_to_list(inp))
                
                    
                elif amogum == 'i':
                    print(f"\nAttention! CSETR can {color(252,0,0)}not{ui_color} work with RGBA, only RGB (except #00000000)!")

                    path = input("\nenter full path to your image:\n>> ")
                    png = Image.open(path)

                    if png.size[0] != 20 or png.size[1] != 18:
                        back('image must be 20x18\n')

                    import_png(png)

                    
                elif amogum == "b":
                    picture = copy(bg)

                changed = 1
                back()

            elif action == 'cu':
                print(f'''

current parameters:


background color - {bgcf}#{bgc_hex}{ui_color}{"(default - #0c0c0c)" if bgc_hex != '0c0c0c' else ""}


UI color - #{ui_hex} {"(default - #cccccc)" if ui_hex != 'cccccc' else ""}


background skin - {bg_skin}

{"(default - trSkin1MzCAAGuDUcYAMRwNQNDNDcFwgwJ6MIaQU8lz/Ah0s6OriamlCzKDQsWjbh518wC6ebTcINLNZi5GTmZGQMVwBmYM0pMx6uZRN1Pi5kHieOo3+Sizi55OHSRuBgA=)" if bgc_hex != 'trSkin1MzCAAGuDUcYAMRwNQNDNDcFwgwJ6MIaQU8lz/Ah0s6OriamlCzKDQsWjbh518wC6ebTcINLNZi5GTmZGQMVwBmYM0pMx6uZRN1Pi5kHieOo3+Sizi55OHSRuBgA=' else ""}

max undo/redo depth - {max_history} {"(default - 500)" if max_history != 500 else ""}''')
                act = input('\n"bc" - change background color\n"bs" - change background skin\n"ui" - change UI color\n"urd" - change  max undo/redo depth\n>> ')
                if 'bc' in act:
                    bgc_hex = input("new background color:\n>> ").replace('#','')
                    bgcb = color(*decode_hex(bgc_hex), back  = True, fore = False)
                    bgcf = color(*decode_hex(bgc_hex))
                if 'ui' in act:
                    ui_hex = input("new UI color:\n>> ").replace('#','')
                    ui_color = color(*decode_hex(ui_hex))
                if 'bs' in act:
                    bg_skin = input("new background skin:\n>> ")
                    bg = skin_to_list(bg_skin)

                if 'urd' in act:
                    max_history = int(input('new max undo/redo depth ("-1" for limitless saving):\n>> '))

                save_config()

                back()


            elif action == 'h':
                newhotkeys = {}
                print('\nYou can choose only single keys, not combinations:((\n')
                sleep(0.1)
                
                for key in hotkeys.keys():
                    print(f'set "{key}" hotkey (current - [{hotkeys[key]}]): ', end = '')
                    stdout.flush()
                    sleep(0.5)
                    newhotkey = read_key()
                    print(f'[{newhotkey}]')
                    if newhotkey in newhotkeys.values():
                        raise Exception(f'[{newhotkey}] is already set')
                    newhotkeys[key] = newhotkey


                flush_input()
                if input('Are you sure? (type "Y" if you are)\n>> ') == 'Y':
                    hotkeys = newhotkeys
                    save_hotkeys()
                    back()
                else:
                    back('OK. ')


            elif action == 'u':
                if ur != -(len(history)):
                    ur -= 1
                    
            elif action == 'r':
                if ur != -1:
                    ur += 1

            elif action == 'f4':
                if input('Are you sure?? (type "Y" if you are)\n>> ') == 'Y':
                    exit(0)
                print('k')
                back('')

            elif action == 'up':
                if not TRSS_token:
                    print('You need to log into your TR account!')
                    login = input('login:\n>> ')
                    check = TRSS_req('users.php', action = 'login', login = login, password = input("password(don't worry, i don't store them):\n>> "))
                    try:
                        check = check.json()
                        match check['error_code']:
                            
                            case 0: print('wrong login or password')
                            
                            case 1: print(f'there is no "{login}" in TR database')
                            
                            case 2: print('try again later')
                            
                            case -1: print('wth dude')
                        back("")
                        continue
                    except:
                        TRSS_token = check
                        save_config()
                        
                primary_color = input('head color:\n>> ')
                secondary_color = input('pants color:\n>> ')
                skin_name = input('name of the skin:\n>> ')

                check = TRSS_req('skins.php', action = 'upload_skin', token = TRSS_token,
                                 skin = list_to_skin(picture), skin_name = skin_name,
                                 primary_color = primary_color, secondary_color = secondary_color)
                if check == '1':
                    back('success! ')
                else:
                    raise Exception(check)
            else:
                back('unknown command!\n')


        elif key == hotkeys['click']:
            
            changed = 1
            
            if mode == 'brush': picture[selected[0]][selected[1]] = current_color

            elif mode == 'eraser': picture[selected[0]][selected[1]] = empty

            elif mode == 'pipette': current_color = picture[selected[0]][selected[1]]

            elif mode == 'fill': fill()
            
        elif key == hotkeys['help']:
            print('\n\nhotkeys:')
            for k in hotkeys.keys():
                print(f'[{hotkeys[k]}] - {k}')
            
            print(f'\n\n"e" means that pixel is actually empty, but its {color(255,0,0)}c{color(255,127,0)}o{color(255,255,0)}l{color(0,255,0)}o{color(0,255,255)}r{color(0,0,255)}e{color(75,0,130)}d{ui_color} for your convenience')
            print('\ni hope u enjoy my little project :p')
            print('(and sorry for my not good english)')

            print(f'\n\nspecial thanks:\n{color(255,255,255)}\ngstroin{ui_color} for help and some code\n{color(108,174,69)}coolamoeba{ui_color} for few cool ideas\n{color(255,200,200)}tdf {ui_color}for being the cutest girl in the whole universe <3 <3 <3')

            back('\n')
        
        elif key == hotkeys['undo']:
            if ur != -(len(history)):
                ur -= 1
        elif key == hotkeys['redo']:
            if ur != -1:
                ur += 1

                
        if changed:
            if ur != -1:
                history = history[:ur+1]
                ur = -1
            history.append(list_to_skin(picture))
            if max_history != -1 and len(history) > max_history:
                history = history[1:]
        

    except Exception as e:
        print('\nERROR CAUGHT:\n')
        print_exc()
        print("(probably, it's not my fault :p)")
        back('\n')
