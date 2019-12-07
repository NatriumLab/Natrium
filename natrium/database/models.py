from pony import orm
from .connection import db
import uuid
from datetime import datetime
import re
from conf import config

class Resource(db.Entity):
    Id = orm.Required(uuid.UUID, default=uuid.uuid4, unique=True, index=True)
    PicHash = orm.Required(orm.LongStr)
    Name = orm.Required(str, py_check=lambda value: \
        isinstance(value, str) and\
        bool(re.match(r"^[a-zA-Z\u4e00-\u9fa5][a-zA-Z\u4e00-\u9fa5_\-0-9]*$", value)) and\
        len(value) <= 40
    )
    PicHeight = orm.Required(int, py_check=lambda value: not bool(value % 16))
    PicWidth = orm.Required(int, py_check=lambda value: not bool(value % 16))
    Model = orm.Required(str, py_check=lambda i: i in ['steve', 'alex'], null=True)
    Type = orm.Required(str, py_check=lambda i: i in ['skin', 'cape', 'elytra'])
    CreatedAt = orm.Required(datetime, default=datetime.now)

class Account(db.Entity):
    Id = orm.Required(uuid.UUID, default=uuid.uuid4, unique=True, index=True)
    Email = orm.Required(str, py_check=lambda value: \
        isinstance(value, str) and\
        bool(re.match(r"^[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?$", value)) and\
        len(value) <= 40
    )
    AccountName = orm.Required(str, py_check=lambda value: \
        isinstance(value, str) and\
        bool(re.match(r"^[a-zA-Z\u4e00-\u9fa5][a-zA-Z\u4e00-\u9fa5_\-0-9]*$", value)) and\
        len(value) <= 40
    )
    Avatar = orm.Optional(Resource, py_check=lambda value: value.type == "skin")
    Password = orm.Required(orm.LongStr)
    CreatedAt = orm.Required(datetime, default=datetime.now)

    Permission = orm.Required(str, default="Normal", py_check=lambda value: value in ['Normal', 'Manager'])

class Character(db.Entity):
    Id = orm.Required(uuid.UUID, default=uuid.uuid4, unique=True, index=True)
    PlayerId = orm.Required(uuid.UUID, unique=True, index=True)
    PlayerName = orm.Required(str, unique=True, py_check=lambda value: bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_\-]*$", value)))
    Owner = orm.Required(Account)

    Skin = orm.Required(Resource, py_check=lambda value: value.type == "skin", null=True)
    Cape = orm.Required(Resource, py_check=lambda value: value.type == "cape", null=True)
    Elytra = orm.Required(Resource, py_check=lambda value: value.type == "elytra", null=True)

    CreatedAt = orm.Required(datetime, default=datetime.now)
    UpdatedAt = orm.Required(datetime, default=datetime.now)

    def FormatResources(self, metadata=True, auto=False, url=config['hosturl'].rstrip("/")):
        if auto: # 是否依据资源模型自动生成metadata(model==alex)
            if self.Skin:
                if self.Skin.Model == "alex":
                    metadata = True
                else:
                    metadata = False
        result = {
            "timestamp": self.CreatedAt.timestamp(),
            "profileId": self.Id,
            "profileName": self.PlayerName,
            "textures": {}
        }
        if self.Skin:
            result['textures'].update({
                'skin': {
                    "url": f"{url}{config['static-resource-path'].format(hash=self.Skin.PicHash)}",
                }
            })
            if metadata:
                result['textures']['skin']['metadata'] = {
                    "model": {"steve": "default", "alex": "slim"}[self.Skin.Model]
                }
        if self.Cape:
            result['textures'].update({
                'cape': {
                    "url": f"{url}{config['static-resource-path'].format(hash=self.Cape.PicHash)}",
                }
            })
        if self.Elytra:
            result['textures'].update({
                "elytra": {
                    "url": f"{url}{config['static-resource-path'].format(hash=self.Elytra.PicHash)}",
                }
            })
        return result

    def FormatCharacter(self, unsigned=False, Properties=False, metadata=True):
        