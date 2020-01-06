import re

CharacterName = r"^[a-zA-Z][_a-zA-Z0-9]{2,16}$"
Email = r"^[A-Za-z0-9\u4e00-\u9fa5_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$"
AccountName = r"^[A-Za-z0-9\u4e00-\u9fa5_-]{4,}$"
ResourceName = r"^[A-Za-z0-9\u4e00-\u9fa5_-]{,40}$"

def verify(text, res):
    return bool(re.match(res, text))