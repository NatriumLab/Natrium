from dataclasses import dataclass
import uuid
from typing import Optional, List, Dict
import maya
from natrium.util import enums
import bcrypt
from datetime import datetime
from natrium.util import verify, summon
from .account import Account
import re

@dataclass(init=False, repr=True, eq=True)
class Resource(object):
    Id: uuid.UUID
    Name: uuid.UUID
    Hash: str
    Owner: uuid.UUID
    CreationDate: maya.MayaDT
    Metadata: List[Dict] = [summon.ResourceMetadata.MCTexture()]
    IsPrivated: bool = False

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    async def Create(cls, Hash, Name, Owner: Account, IsPrivated=False):
        if not re.match(verify.CharacterName, Name):
            return

        FactoryResult = cls()

        FactoryResult.Id = uuid.uuid4()
        FactoryResult.Name = Name
        FactoryResult.Hash = Owner.Id
        FactoryResult.CreationDate = maya.now()
        FactoryResult.IsPrivated = IsPrivated

        return FactoryResult

    def format(self):
        return {
            "id": self.Id,
            "name": self.Name,
            "hash": self.Hash,
            "meta": self.Metadata,
            "creationDate": self.CreationDate.datetime(),
            "isPrivated": self.IsPrivated,
            "owner": self.Owner
        }

    @classmethod
    def CreateFromFormat(cls, message):
        FactoryResult = cls()

        FactoryResult.Id = message['id']
        FactoryResult.Name = message['name']
        FactoryResult.Hash = message['hash']
        FactoryResult.CreationDate = maya.MayaDT(message['creationDate'].timestamp())
        FactoryResult.IsPrivated = message['isPrivated']
        FactoryResult.Metadata = message['meta']
        FactoryResult.Owner = message['owner']

        return FactoryResult

    def IsUsable(self, Account: Account):
        return Account.Id == self.Owner or not self.IsPrivated