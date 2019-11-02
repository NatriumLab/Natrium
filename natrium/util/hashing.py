import hashlib
import uuid

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

def OfflinePlayerUUID(name):
    data = list(hex2bin(md5("OfflinePlayer:" + name)))
    data[6] = chr(ord(data[6]) & 0x0f | 0x30)
    data[8] = chr(ord(data[8]) & 0x3f | 0x80)
    return uuid.UUID(bin2hex("".join(data)))

if __name__ == "__main__":
    print(OfflinePlayerUUID("Chenwe_i_lin"))