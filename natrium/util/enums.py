from enum import Enum

class MCTextureType(str, Enum):
    skin = "skin"
    cape = "cape"

class MCTextureModel(str, Enum):
    steve = "steve"
    alex = "alex"
    auto = "auto"

class Classes(Enum):
    standard = "standard"
    coordinator = "coordinator"
    admin = "admin"

class GroupJoin(Enum):
    invite = "invite" # 邀请人或邀请码
    problems = "problems" # 需要回答问题并通过管理员的验证
    directly = "directly" # 直接进入
    deny = "deny" # 无法发出申请

class PublicStatus(str, Enum):
    Public = "public",
    Private = "private"