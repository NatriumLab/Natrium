from dataclasses import dataclass
import uuid
from typing import Optional
import maya
from natrium.util import enums
import bcrypt
from datetime import datetime
from natrium.util import verify, hashing
import re
from .account import Account

@dataclass(init=False, repr=True, eq=True)
class Character(object):
    Id: uuid.UUID
    Name: str
    PlayerUUID: uuid.UUID
    
    SkinBinding: Optional[uuid.UUID] = None
    CapeBinding: Optional[uuid.UUID] = None

    CreationDate: maya.MayaDT
    Owner: uuid.UUID

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    async def Create(cls, Name, Owner: Account):
        """实例化一个Character对象, 并自动生成各种信息
        """
        if not re.match(verify.CharacterName, Name):
            return

        FactoryResult = cls()

        FactoryResult.Id = uuid.uuid4()
        FactoryResult.Name = Name
        FactoryResult.PlayerUUID = hashing.OfflinePlayerUUID(Name)

        FactoryResult.CreationDate = maya.now()
        FactoryResult.Owner = Owner.Id

        return FactoryResult

    def format(self):
        return {
            "id": self.Id,
            "name": self.Name,
            "playeruuid": self.PlayerUUID,
            "creationDate": self.CreationDate,
            "owner": self.Owner,
            "binding": {
                "skin": self.SkinBinding,
                "cape": self.CapeBinding
            }
        }

    @classmethod
    def CreateFromFormat(cls, message):
        FactoryResult = cls()

        FactoryResult.Id = message['id']
        FactoryResult.Name = message['name']
        FactoryResult.PlayerUUID = message['playeruuid']
        FactoryResult.CreationDate = message['creationDate']
        FactoryResult.Owner = message['owner']
        FactoryResult.SkinBinding = message['binding']['skin']
        FactoryResult.CapeBinding = message['binding']['cape']

        return FactoryResult

    def UpdateQueryMsg(self):
        return {
            "id": self.Id
        }