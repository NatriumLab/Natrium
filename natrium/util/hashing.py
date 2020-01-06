import hashlib
import uuid
from PIL import Image
from io import BytesIO

def hex2bin(hexstring):
    return ''.join([chr(int(b, 16)) for b in [hexstring[i:i+2] for i in range(0, len(hexstring), 2)]])

def bin2hex(sendbin):
    e = 0
    for i in sendbin:
       e = e * 256 + ord(i)
    return hex(e)[2:]

def md5(string):
    return hashlib.md5(string.encode(encoding='utf-8')).hexdigest()

def substr(string, start, length=None):
    return string[start if start >= 0 else 0:][:length if length != None else len(string) - start]

def OfflinePlayerUUID(name) -> uuid.UUID:
    data = list(hex2bin(md5("OfflinePlayer:" + name)))
    data[6] = chr(ord(data[6]) & 0x0f | 0x30)
    data[8] = chr(ord(data[8]) & 0x3f | 0x80)
    return uuid.UUID(bin2hex("".join(data)))

def PicHash(image):
    width, height = image.size
    with BytesIO() as Buf:
        Buf.write(width.to_bytes(4, "big"))
        Buf.write(height.to_bytes(4, "big"))
        for w in range(width):
            for h in range(height):
                data = list(image.getpixel((w, h)))
                Buf.write(data[3].to_bytes(1, "big"))
                if data[3] == 0:
                    for _ in range(3):
                        Buf.write((0).to_bytes(1, "big"))
                else:
                    Buf.write(data[0].to_bytes(1, "big"))
                    Buf.write(data[1].to_bytes(1, "big"))
                    Buf.write(data[2].to_bytes(1, "big"))
        return hashlib.sha256(Buf.getvalue()).hexdigest()


if __name__ == "__main__":
    print(OfflinePlayerUUID("Chenwe_i_lin"))