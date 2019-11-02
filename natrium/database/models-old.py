from tortoise.models import Model
from tortoise import fields
#from ..util.summon import ResourceMetadata
#from ..util.enums import MCTextureType, MCTextureModel, Classes, GroupJoin
from ..util import summon, enums
from conf import config

class Account(Model):
    Id = fields.UUIDField(pk=True)
    Name = fields.CharField(null=True, max_length=64)
    Avatar = fields.UUIDField()
    Email = fields.CharField(unique=True, max_length=64)

    Password = fields.CharField(max_length=2048) # 因为使用了Bcrypt,所以用不用salt无所谓.

    Rank = fields.CharField(max_length=256, default=enums.Classes.standard.value)

    RegisterDate = fields.DatetimeField(auto_now_add=True)

class Character(Model):
    Id = fields.UUIDField(pk=True)
    Name = fields.CharField(max_length=256, index=True)
    Uuid = fields.UUIDField(index=True)
    
    skin = fields.UUIDField(pk=False)
    cape = fields.UUIDField(pk=False)

    CreationDate = fields.DatetimeField(auto_now_add=True)
    owner = fields.UUIDField()

class Resource(Model):
    Id = fields.UUIDField(pk=True)
    Name = fields.CharField(max_length=256, index=True)
    Hash = fields.TextField(index=True)

    Uploader = fields.UUIDField()
    UploadTime = fields.DatetimeField(auto_now_add=True)

    Metadata = fields.JSONField(default=[
        summon.ResourceMetadata.MCTexture()
    ])

    IsPrivated = fields.BooleanField(default=False)

    def Usable(self, AccountId: str) -> bool:
        return AccountId == self.Uploader.hex or not self.IsPrivated

class Group(Model):
    Id = fields.UUIDField(pk=True)
    Owner = fields.UUIDField()
    Creater = fields.UUIDField()
    Maximum = fields.IntField(default=config['group']['default']['maximum'])

    CreationDate = fields.DatetimeField(auto_now_add=True)

    road = fields.CharField(max_length=256, default=enums.GroupJoin.directly)
    problems = fields.JSONField(default=[])
    # blacklist = fields.JSONField(default=[]) 等下写个表...
    EnabledModules = fields.JSONField(default={})
    Metadata = fields.JSONField(default=[])

    Globalify = fields.BooleanField(default=False)
    # 是否为全局组, 若是, 则Maximum失效.
    # 程序内部保证不会出现关于全局组的member信息.
    # 程序内部保证不会出现第二个全局组.
    # 程序内部保证一定会有一个可用的全局组

class Member(Model):
    Target = fields.UUIDField() # Account
    Source = fields.UUIDField() # Group

    Rank = fields.CharField(max_length=256, default=enums.Classes.standard)
    Nickname = fields.CharField(max_length=256, default="")

    EntryDate = fields.DatetimeField(auto_now_add=True)

class GroupBlacklist(Model):
    """
    不再接受申请的名单
    """
    Group = fields.UUIDField()
    Account = fields.UUIDField()

    CreationDate = fields.DatetimeField(auto_now_add=True)
    ValidateDate = fields.DatetimeField(auto_now_add=True)