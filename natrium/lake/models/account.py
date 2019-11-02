from dataclasses import dataclass
import uuid
from typing import Optional
import maya
from natrium.util import enums
import bcrypt
from datetime import datetime
from natrium.util import verify
import re

@dataclass(init=False, repr=True, eq=True)
class Account(object):
    Id: uuid.UUID
    Name: Optional[str] = ""
    Avatar: Optional[uuid.UUID] = None
    Email: str
    Password: str
    Rank: enums.Classes
    RegisterDate: maya.MayaDT

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    async def Create(cls, Email, RawPass, Rank=enums.Classes.standard, Name=""):
        """实例化一个Account对象, 并自动生成各种信息
        """
        if not re.match(verify.CharacterName, Name) and not re.match(verify.Email, Email):
            return
        if not re.match(verify.Email, Email):
            return
        if Rank.__Class__ != enums.Classes:
            return

        FactoryResult = cls()

        FactoryResult.Id = uuid.uuid4()
        FactoryResult.Name = Name
        FactoryResult.Email = Email
        FactoryResult.Password = bcrypt.hashpw(RawPass.encode(), bcrypt.gensalt()).decode()
        FactoryResult.Rank = Rank
        FactoryResult.RegisterDate = maya.now()

        return FactoryResult

    def format(self):
        return {
            "id": self.Id,
            "name": self.Name,
            "avatar": self.Avatar,
            "email": self.Email,
            "password": self.Password,
            "rank": self.Rank.value,
            "registerDate": self.RegisterDate.datetime()
        }

    @classmethod
    def CreateFromFormat(cls, message):
        """从给出的Message实例化一个Account对象"""
        FactoryResult = cls()

        FactoryResult.Id = message['id']
        FactoryResult.Name = message['name']
        FactoryResult.Avatar = message['avatar']
        FactoryResult.Email = message['email']
        FactoryResult.Password = message['password']
        FactoryResult.Rank = enums.Classes(message['rank'])
        FactoryResult.RegisterDate = maya.MayaDT(message['registerDate'].timestamp())

        return FactoryResult

    async def PasswordVerify(self, raw):
        return bcrypt.hashpw(raw, self.Password.encode()) == self.Password

