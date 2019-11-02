import random
import string

def String(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))