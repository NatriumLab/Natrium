from fastapi import Depends
from .. import depends
from .. import router
from .. import exceptions
import uuid
from pony import orm
from typing import Optional
from natrium.database.models import Account, Resource, Character
from natrium.util import enums
from .. import models
from natrium.util import res
from natrium.util.hashing import OfflinePlayerUUID
from datetime import datetime as dt

@router.post(
    "/optionserver/character/{characterId}/textures/bind/{resourceId}",
    dependencies=[Depends(depends.Permissison("Normal"))]
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
    dependencies=[Depends(depends.Permissison("Normal"))]
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
    dependencies=[Depends(depends.Permissison("Normal"))]
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
    dependencies=[Depends(depends.Permissison("Normal"))]
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
    dependencies=[Depends(depends.Permissison("Normal"))]
)
async def os_char_transform(
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
    dependencies=[Depends(depends.Permissison("Normal"))]
)
async def os_reso_transform(
        public: enums.PublicStatus,
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    if resource.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        resource = Resource.get(Id=resource.Id)
        resource.IsPrivate = public != enums.PublicStatus.Public
        orm.commit()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/resource/delete/{resourceId}",
    dependencies=[Depends(depends.Permissison("Normal"))]
)
async def os_reso_delete(
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    if resource.Owner.Id != account.Id:
        raise exceptions.PermissionDenied()
    with orm.db_session:
        resource = Resource.get(Id=resource.Id).delete()
    return {
        "operator": "success",
        "metadata": {
            "account": account.Id
        }
    }

@router.post(
    "/optionserver/resource/update/{resourceId}",
    dependencies=[Depends(depends.Permissison("Normal"))]
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
            if update_info.update.model:
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
    dependencies=[Depends(depends.Permissison("Normal"))]
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