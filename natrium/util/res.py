import re

CharacterName = r"^[a-zA-Z][_a-zA-Z0-9]{2,16}$"
Email = r"^[A-Za-z0-9\u4e00-\u9fa5_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$"
AccountName = r"^[A-Za-z0-9\u4e00-\u9fa5_-]{4,}$"
ResourceName = r"^[A-Za-z0-9\u4e00-\u9fa5_-]{,40}$"
Password = r"^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,16}$" 
# 密码不能是纯数字或者是纯英文字母, 应该同时包括数字和字母(大小写均可)

def verify(text, res):
    return bool(re.match(res, text))