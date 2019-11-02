from enum import Enum

class MCTextureType(Enum):
    skin = "skin"
    cape = "cape"
    elytra = "elytra"

class MCTextureModel(Enum):
    steve = "steve"
    alex = "alex"

class Classes(Enum):
    standard = "standard"
    coordinator = "coordinator"
    admin = "admin"

class GroupJoin(Enum):
    invite = "invite" # 邀请人或邀请码
    problems = "problems" # 需要回答问题并通过管理员的验证
    directly = "directly" # 直接进入
    deny = "deny" # 无法发出申请