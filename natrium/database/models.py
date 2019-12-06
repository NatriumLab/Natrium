from pony import orm
from .connection import db
import uuid
from datetime import datetime
import re

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
    type = orm.Required(str, py_check=lambda i: i in ['skin', 'cape', 'elytra'])
    createdAt = orm.Required(datetime, default=datetime.now)

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
    createdAt = orm.Required(datetime, default=datetime.now)

class Character(db.Entity):
    Id = orm.Required(uuid.UUID, default=uuid.uuid4, unique=True, index=True)
    PlayerId = orm.Required(uuid.UUID, unique=True, index=True)
    PlayerName = orm.Required(str, py_check=lambda value: bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_\-]*$", value)))
    Owner = orm.Required(Account)

    Skin = orm.Required(Resource, py_check=lambda value: value.type == "skin")
    Cape = orm.Required(Resource, py_check=lambda value: value.type == "cape")
    Elytra = orm.Required(Resource, py_check=lambda value: value.type == "elytra")

    createdAt = orm.Required(datetime, default=datetime.now)
