from fastapi import Depends, BackgroundTasks
from .. import depends
from .. import router
from .. import exceptions
import uuid
from pony import orm
from typing import Optional
from natrium.database.models import Account, Resource, Character
from natrium.util import enums
from .. import models
from .. import resource_manager
from natrium.util import res
from natrium.util.hashing import OfflinePlayerUUID
from datetime import datetime as dt
from i18n import t as Ts_

@router.post(
    "/optionserver/character/{characterId}/textures/bind/{resourceId}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.character.textures.bind.summary"),
    description=Ts_("apidoc.natrium.optionserver.character.textures.bind.description")
)
async def os_char_textures_bind(
        character: Character = Depends(depends.CharacterFromPath),
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    if resource.IsPrivate and resource.Owner != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        character = Character.get(Id=character.Id)
        resource = Resource.get(Id=resource.Id)

        if resource.Type == 'skin':
            character.Skin = resource
        elif resource.Type == "cape":
            character.Cape = resource
        character.update_UpdatedAt()

        orm.commit()
        return character.format_self()

@router.post(
    "/optionserver/character/{characterId}/textures/unbind/{resourceType}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.character.textures.unbind.summary"),
    description=Ts_("apidoc.natrium.optionserver.character.textures.unbind.description")
)
async def os_char_textures_unbind(
        resourceType: enums.MCTextureType,
        character: Character = Depends(depends.CharacterFromPath),
        account: Account = Depends(depends.AccountFromRequest),
    ):
    with orm.db_session:
        character = Character.get(Id=character.Id)

        if resourceType == enums.MCTextureType.skin:
            character.Skin = None
        elif resourceType == enums.MCTextureType.cape:
            character.Cape = None
        character.update_UpdatedAt()
        
        orm.commit()
        return character.format_self()

@router.post(
    "/optionserver/character/create/",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.character.create.summary"),
    description=Ts_("apidoc.natrium.optionserver.character.create.description")
)
async def os_char_create(
        createInfo: models.CharacterCreate,
        account: Account = Depends(depends.AccountFromRequest)
    ):
    if not res.verify(createInfo.create.name, res.CharacterName):
        raise exceptions.NonCompliantMsg()

    with orm.db_session:
        if Character.get(PlayerName=createInfo.create.name):
            raise exceptions.OccupyExistedAddress()

        account = Account.get(Id=account.Id)

        character = Character(
            PlayerId=OfflinePlayerUUID(createInfo.create.name),
            PlayerName=createInfo.create.name,

            Owner=account,
            CreatedAt=dt.now(),
            UpdatedAt=dt.now(),

            Public=createInfo.create.public
        )
        orm.commit()
        return character.format_self()

@router.post(
    "/optionserver/character/delete/{characterId}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.character.delete.summary"),
    description=Ts_("apidoc.natrium.optionserver.character.delete.description")
)
async def os_char_delete(
        account: Account = Depends(depends.AccountFromRequest),
        character: Character = Depends(depends.CharacterFromPath)
    ):
    if character.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        character = Character.get(Id=character.Id).delete()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/character/{characterId}/publicStats/transformTo/{public}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.character.publicStats.transformTo.summary"),
    description=Ts_("apidoc.natrium.optionserver.character.publicStats.transformTo.description")
)
async def os_char_publicStats_transform(
        public: enums.PublicStatus,
        account: Account = Depends(depends.AccountFromRequest),
        character: Character = Depends(depends.CharacterFromPath)
    ):
    if character.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        character = Character.get(Id=character.Id)
        character.Public = public == enums.PublicStatus.Public
        character.update_UpdatedAt()
        orm.commit()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/resource/{resourceId}/publicStats/transformTo/{public}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.resource.publicStats.transformTo.summary"),
    description=Ts_("apidoc.natrium.optionserver.resource.publicStats.transformTo.description")
)
async def os_reso_transform_publicStats(
        public: enums.PublicStatus,
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    if resource.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        resource = Resource.get(Id=resource.Id)
        # 检查是否有origin
        if resource.Origin:
            if resource.Origin.Protect or resource.Origin.Private:
                # 如果是私有或带保护, 则不准公开.
                if public == "public":
                    raise exceptions.PermissionDenied()

        resource.IsPrivate = public != "public"
        if public == "private":
            resource.Protect = False
        orm.commit()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/resource/{resourceId}/protectStats/transformTo/{stats}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.resource.protectStats.transformTo.summary"),
    description=Ts_("apidoc.natrium.optionserver.resource.protectStats.transformTo.description")
)
async def os_reso_transform_protectStats(
        stats: bool,
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    if resource.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        resource = Resource.get(Id=resource.Id)
        # 检查是否有origin
        if resource.Origin:
            if resource.Origin.Protect or resource.Origin.Private:
                # 如果是私有或带保护, 则不准更改保护状态.
                # 注意: 这里需要强制转变保护状态
                if resource.Protect:
                    resource.Protect = False
                    orm.commit()
                raise exceptions.PermissionDenied()

        resource.Protect = stats
        orm.commit()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/resource/delete/{resourceId}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.resource.delete.summary"),
    description=Ts_("apidoc.natrium.optionserver.resource.delete.description")
)
async def os_reso_delete(
        bgTasks: BackgroundTasks,

        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    if resource.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        resource = Resource.get(Id=resource.Id)
        # 检查其fork, 因为该资源被删除, 所以资源的各个Fork也应该被删除.
        if resource.Forks[:]:
            for i in resource.Forks:
                # 解除角色绑定
                if i.UsedforSkin:
                    for ii in i.UsedforSkin:
                        ii.Skin = None
                if i.UsedforCape:
                    for ii in i.UsedforCape:
                        ii.Cape = None
                # 删除.
                i.delete()

        bgTasks.add_task(resource_manager.Delete, resource.PicHash)
        resource.delete()
        orm.commit()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/resource/update/{resourceId}",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.resource.update.summary"),
    description=Ts_("apidoc.natrium.optionserver.resource.update.description")
)
async def os_reso_update(
        update_info: models.ResourceUpdate,
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    if resource.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        resource = Resource.get(Id=resource.Id)
        try:
            if update_info.update.name:
                resource.Name = update_info.update.name
            if update_info.update.type:
                resource.Type = update_info.update.type
                if update_info.update.type == "cape":
                    resource.Model = "none"
            if update_info.update.model:
                if update_info.update.type == "cape":
                    if update_info.update.model != 'none':
                        raise exceptions.UnrecognizedContent({
                            "field": "update_info.update.model",
                            "conflictItems": [
                                {"update_info.update.type": "cape"}
                            ]
                        })
                resource.Model = update_info.update.model
            orm.commit()
        except ValueError:
            raise exceptions.NonCompliantMsg()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/character/{characterId}/update/name",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['OptionServer'],
    summary=Ts_("apidoc.natrium.optionserver.character.rename.summary"),
    description=Ts_("apidoc.natrium.optionserver.character.rename.description")
)
async def os_char_update_name(
        update_info: models.Update,
        account: Account = Depends(depends.AccountFromRequest),
        character: Character = Depends(depends.CharacterFromPath)
    ):
    if character.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    
    if not res.verify(update_info.update.name, res.CharacterName):
        raise exceptions.NonCompliantMsg()

    with orm.db_session:
        if Character.get(PlayerName=update_info.update.name):
            raise exceptions.OccupyExistedAddress()

        character = Character.get(Id=character.Id)
        character.PlayerName = update_info.update.name
        character.PlayerId = OfflinePlayerUUID(update_info.update.name)
        character.update_UpdatedAt()
        orm.commit()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id,
            "character": character.Id
        }
    }