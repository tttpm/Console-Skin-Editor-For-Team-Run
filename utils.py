from zlib import decompress, compressobj, MAX_WBITS, DEFLATED
from PIL import Image, ImageColor, ImageDraw
from base64 import b64encode, b64decode
from requests import post


def color(r: int, g: int, b: int, fore = True, back = False):
    res = ''
    if fore: res += f"\033[38;2;{r};{g};{b}m"
    if back: res += f"\033[48;2;{r};{g};{b}m"
    return res



def decode_hex(hexx: str):
    hexx = hexx.replace('#', '')
    if len(hexx) == 8 and hexx[-2:] == '00':
        return None
    else:
        #assert len(hexx) == 6
        pass
    hexx = hexx.upper()
    digits = '0123456789ABCDEF'
    cat = list(map(lambda d: digits.index(d), hexx[:]))
    return (cat[0]*16 + cat[1], cat[2]*16 + cat[3], cat[4]*16 + cat[5])



def encode_hex(r: int, g: int, b: int):
    res = ''
    digits = '0123456789ABCDEF'
    res += digits[r//16] + digits[r%16]
    res += digits[g//16] + digits[g%16]
    res += digits[b//16] + digits[b%16]
    return res + 'FF'



def skin_to_png(skin: str):

    compressed = b64decode(skin[7:])
    decompressed = str(decompress(compressed, -MAX_WBITS).decode())

    img = Image.new("RGBA",(20, 18), (0,0,0,0))

    draw = ImageDraw.Draw(img)

    width = 20
    height = 18


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



def skin_to_list(trskin: str):
    res = [[None]*20 for i in range(18)]
    compressed = b64decode(trskin[7:])
    hexes = str(decompress(compressed, -MAX_WBITS).decode()).split(';')
    hexes.pop()
    i, j = 0, 0
    for hehex in hexes:
        if j == 20:
            i += 1
            j = 0
        res[i][j] = decode_hex(hehex)
        j += 1
    return res



def list_to_skin(pic: list):
    res = ''
    for line in pic:
        for pixel in line:
            if not pixel:
                res += '00000000;'
                continue
            res += encode_hex(*pixel) + ';'

    if not res: return 'trSkin1'
    deflate_compress = compressobj(9, DEFLATED, -MAX_WBITS)
    compressed = deflate_compress.compress(bytes(res, encoding ='utf-8')) + deflate_compress.flush()
    encrypted = b64encode(compressed)
    return "trSkin1" + encrypted.decode()




def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():             #thanks to StackOverFlow xdxdxd
            msvcrt.getch()
    except ImportError:
        import sys, termios    
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)



TRSS_url = 'http://trsstest.crystalcloud.xyz/game-dev/TRSSDatabase/'

def TRSS_req(php: str, **kwargs):
    try:
        response = post(TRSS_url + php, data = kwargs).text
        try:
            json = response.json()
            if 'error_code' in json.keys():
                return (1, {
                    
                        "0": "wrong user or password",
                        
                        "1": "user not found in TR database",
                        
                        "2": "please try again later",
                        
                        "3": "user already registered",
                        
                        "4": "user or skin not found",
                        
                        "5": "that skin from that user was uploaded before",
                        
                        "6": "skin not found",
                        
                        "7": "user's ID doesn't match skin author's ID",
                        
                        "-1": "wth dude o_0"
                        
                        }[json["error_code"]])

                return (0, json)
        except:
            return (0, response)
    except:
        return (1, 'check your internet connection')

clear_color = '\033[0m'

suncat = 'trSkin17ZZBCoAwDAS/VFCk4qmt5v9P8iBIsTVuYqwIelq0ZidhJTq3XZODBdFRiF43r8NbLF0InnKhMLWqA1rMQ1pSzMWZaVUo6hiiMqaMENVRwEu9rERL5jIJusM/8yeYd5F8H8aYi+eYy0ci5hIVgWcImTNlZRy+Ol6kC4YQuXPJjGxPEBVJCzJwxXjV2RCFpEE29k/YnJBZJVbZQPayuVBkg+mrpbj/U0r0gmgAf7NBxH0F'
