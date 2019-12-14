from pony import orm
from .connection import db
import uuid
from datetime import datetime
import re
from conf import config
from ..util.sign import Signature
import json
import base64

class Resource(db.Entity):
    Id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    PicHash = orm.Required(orm.LongStr)
    Name = orm.Required(str, py_check=lambda value: \
        isinstance(value, str) and\
        bool(re.match(r"^[a-zA-Z\u4e00-\u9fa5][a-zA-Z\u4e00-\u9fa5_\-0-9]*$", value)) and\
        len(value) <= 40
    )
    PicHeight = orm.Required(int, py_check=lambda value: not bool(value % 16))
    PicWidth = orm.Required(int, py_check=lambda value: not bool(value % 16))
    Model = orm.Optional(str, py_check=lambda i: i in ['steve', 'alex', 'none'], default="steve")
    Type = orm.Required(str, py_check=lambda i: i in ['skin', 'cape', 'elytra'])
    CreatedAt = orm.Required(datetime, default=datetime.now)
    Owner = orm.Required(lambda: Account)
    IsPrivate = orm.Required(bool, default=False)
    UsedforSkin = orm.Set("Character", reverse='Skin', lazy=True)
    UsedforCape = orm.Set("Character", reverse='Cape', lazy=True)
    UsedforElytra = orm.Set("Character", reverse='Elytra', lazy=True)

class Account(db.Entity):
    Id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    Email = orm.Required(str, py_check=lambda value: \
        isinstance(value, str) and\
        bool(re.match(r"^[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?$", value)) and\
        len(value) <= 40,
        unique=True
    )
    AccountName = orm.Required(str, py_check=lambda value: \
        isinstance(value, str) and\
        bool(re.match(r"^[a-zA-Z\u4e00-\u9fa5][a-zA-Z\u4e00-\u9fa5_\-0-9]*$", value)) and\
        len(value) <= 40
    )
    #Avatar = orm.Optional(Resource, py_check=lambda value: value.Type == "skin")
    OwnedResources = orm.Set(Resource, reverse="Owner", lazy=True)
    Password = orm.Required(bytes)
    Salt = orm.Required(bytes)
    CreatedAt = orm.Required(datetime, default=datetime.now)
    Characters = orm.Set("Character", reverse="Owner", lazy=True)

    Permission = orm.Required(str, default="Normal", py_check=lambda value: value in ['Normal', 'Manager'])

class Character(db.Entity):
    Id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    PlayerId = orm.Required(uuid.UUID, index=True)
    PlayerName = orm.Required(str, py_check=lambda value: bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_\-]*$", value)))
    Owner = orm.Required(Account)

    Skin = orm.Optional(Resource, py_check=lambda value: value.Type == "skin")
    Cape = orm.Optional(Resource, py_check=lambda value: value.Type == "cape")
    Elytra = orm.Optional(Resource, py_check=lambda value: value.Type == "elytra")

    CreatedAt = orm.Required(datetime, default=datetime.now)
    UpdatedAt = orm.Required(datetime, default=datetime.now)

    def FormatResources(self, metadata=True, auto=False, url=config['hosturl'].rstrip("/")):
        if auto and self.Skin: # 是否依据资源模型自动生成metadata(model==alex)
            metadata = self.Skin.Model == "alex"
        result = {
            "timestamp": self.CreatedAt.timestamp(),
            "profileId": self.PlayerId.hex,
            "profileName": self.PlayerName,
            "textures": {}
        }
        if self.Skin:
            result['textures'].update({
                'SKIN': {
                    "url": f"{url}{config['resource-static-path'].format(hash=self.Skin.PicHash)}",
                }
            })
            if metadata:
                result['textures']['SKIN']['metadata'] = {
                    "model": {"steve": "default", "alex": "slim"}[self.Skin.Model]
                }
        if self.Cape:
            result['textures'].update({
                'CAPE': { 
                    "url": f"{url}{config['resource-static-path'].format(hash=self.Cape.PicHash)}",
                }
            })
        if self.Elytra: # 大部分时候大家都不处理这个, 但是考虑到兼容性和可维护性, 还是整上.
            result['textures'].update({
                "ELYTRA": {
                    "url": f"{url}/{config['resource-static-path'].format(hash=self.Elytra.PicHash)}",
                }
            })
        return result

    def FormatCharacter(self, unsigned=False, Properties=False, metadata=True, auto=False, url=config['hosturl'].rstrip("/")):
        if auto and self.Skin: # 是否依据资源模型自动生成metadata(model==alex)
            metadata = self.Skin.Model == "alex"
        result = {
            "id": self.PlayerId.hex,
            "name": self.PlayerName
        }
        if Properties:
            #print(self.FormatResources(metadata=metadata))
            textures = json.dumps(self.FormatResources(metadata=metadata, url=url))
            result['properties'] = [
                {
                    "name": 'textures',
                    "value": base64.b64encode(textures.encode("utf-8")).decode("utf-8")
                }
            ]
            if not unsigned:
                for i in range(len(result['properties'])):
                    result['properties'][i]['signature'] = Signature(result['properties'][i]['value'])
        return result