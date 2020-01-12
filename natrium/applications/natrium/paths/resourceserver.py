from fastapi import Depends
from .. import depends
from .. import router
from .. import exceptions
import uuid
from pony import orm
from typing import Optional
from natrium.database.models import Account, Resource, Character
from i18n import t as Ts_

@router.get("/resourceserver/account/{accountId}", tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.account.guest.summary"),
    description=Ts_("apidoc.natrium.resourceserver.account.guest.description"))
@router.post("/resourceserver/account/{accountId}", tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.account.certified.summary"),
    description=Ts_("apidoc.natrium.resourceserver.account.certified.description"))
async def resources_account(
        accountId: uuid.UUID, 
        optionalAccount: Optional[Account] = Depends(depends.O_N_Owen)
    ):
    with orm.db_session:
        account = orm.select(i for i in Account if i.Id == accountId)
        if not account.exists():
            raise exceptions.NoSuchResourceException()
        account: Account = account.first()

        return {
            "accountId": account.Id,
            "email": "".join([account.Email[0:3], "*" * (len(account.Email) - 6), account.Email[-3:]]),
            "username": account.AccountName,
            "characters": [
                {
                    "characterId": i.Id,
                    "player": {
                        "id": i.PlayerId,
                        "name": i.PlayerName
                    }
                } for i in account.Characters if i.Public
            ],
            "resources": [
                {
                    "id": i.Id,
                    "name": i.Name,
                    "createAt": i.CreatedAt,
                    "metadata": {
                        "type": i.Type,
                        "model": i.Model
                    }
                } for i in account.OwnedResources if not i.IsPrivate or\
                    accountId == (optionalAccount.Id if optionalAccount else None)
            ]
        }

@router.get("/resourceserver/character/{characterId}", tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.character.guest.summary"),
    description=Ts_("apidoc.natrium.resourceserver.character.guest.description"))
@router.post("/resourceserver/character/{characterId}", tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.character.certified.summary"),
    description=Ts_("apidoc.natrium.resourceserver.character.certified.description"))
async def resources_character_id(
        characterId: uuid.UUID,
        optionalAccount: Optional[Account] = Depends(depends.O_N_Owen)
    ):
    with orm.db_session:
        character = orm.select(i for i in Character if i.Id == characterId)
        if not character.exists():
            raise exceptions.NoSuchResourceException()
        character: Character = character.first()

        if not character.Public:
            if not optionalAccount:
                raise exceptions.NoSuchResourceException()
            if character.Owner.Id != optionalAccount.Id:
                raise exceptions.NoSuchResourceException()

        result = {
            "id": character.Id,
            "player": {
                "id": character.PlayerId,
                "name": character.PlayerName
            },
            "createdAt": character.CreatedAt,
            "lastUpdatedAt": character.UpdatedAt,
            "loadedTextures": {}
        }
        if character.Skin:
            if character.Skin.IsPrivate and \
                    character.Owner.Id != (optionalAccount.Id if optionalAccount else None):
                # 如果私有且Owner匹配不能
                result['loadedTextures']['skin'] = {
                    "private": True
                }
            else:
                result['loadedTextures']['skin'] = {
                    "id": character.Skin.Id,
                    "name": character.Skin.Name,
                    "createdAt": character.Skin.CreatedAt,
                    "metadata": {
                        "type": character.Skin.Type,
                        "model": character.Skin.Model
                    }
                }
        
        if character.Cape:
            if character.Cape.IsPrivate and \
                    character.Owner.Id != (optionalAccount.Id if optionalAccount else None):
                result['loadedTextures']['cape'] = {
                    "private": True
                }
            else:
                result['loadedTextures']['cape'] = {
                    "id": character.Cape.Id,
                    "name": character.Cape.Name,
                    "createdAt": character.Cape.CreatedAt,
                    "metadata": {
                        "type": character.Cape.Type,
                        "model": character.Cape.Model
                    }
                }
        return result

@router.get("/resourceserver/resource/{resourceId}", tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.resource.guest.summary"),
    description=Ts_("apidoc.natrium.resourceserver.resource.guest.description"))
@router.post("/resourceserver/resource/{resourceId}", tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.resource.certified.summary"),
    description=Ts_("apidoc.natrium.resourceserver.resource.certified.description"))
async def resources_resource_id(
        resource: Resource = Depends(depends.ResourceFromPath),
        optionalAccount: Optional[Account] = Depends(depends.O_N_Owen),
        requestHash: bool = False
    ):
    with orm.db_session:
        resource: Resource = Resource.get(Id=resource.Id)

        if resource.IsPrivate and \
                    resource.Owner.Id != (optionalAccount.Id if optionalAccount else None):
            raise exceptions.NoSuchResourceException()
        result = {
            "id": resource.Id,
            "name": resource.Name,
            "createdAt": resource.CreatedAt,
            "metadata": {
                "type": resource.Type,
                "model": resource.Model
            }
        }
        if requestHash:
            result['metadata']['hash'] = resource.PicHash
        return result

@router.post("/resourceserver/resource/{resourceId}/forks", tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.resource.forks.summary"),
    description=Ts_("apidoc.natrium.resourceserver.resource.forks.description"))
async def resources_resource_forks(
        resource: Resource = Depends(depends.ResourceFromPath),
        Account: Account = Depends(depends.AccountFromRequest)
    ):
    with orm.db_session:
        resource: Resource = Resource.get(Id=resource.Id)
        if not resource.Owner.Id != Account.Id:
            raise exceptions.PermissionDenied()
        return [{
            "id": i.Id,
            "name": i.Name,
            "uploader": i.Owner,
            "createAt": i.CreatedAt
        } for i in resource.Forks]

@router.post(
    "/resourceserver/resource/{resourceId}/protectStats/",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.resource.protectStats.summary"),
    description=Ts_("apidoc.natrium.resourceserver.resource.protectStats.description")
)
async def rs_reso_protectStats(
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    with orm.db_session:
        if account.Id != resource.Owner.Id:
            raise exceptions.PermissionDenied()
        
        return {
            "protectStats": resource.Protect
        }

@router.post(
    "/resourceserver/resource/{resourceId}/publicStats/",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.resource.publicStats.summary"),
    description=Ts_("apidoc.natrium.resourceserver.resource.publicStats.description")
)
async def rs_reso_publicStats(
        account: Account = Depends(depends.AccountFromRequest),
        resource: Resource = Depends(depends.ResourceFromPath)
    ):
    with orm.db_session:
        if account.Id != resource.Owner.Id:
            raise exceptions.PermissionDenied()
        
        return {
            "publicStats": not resource.IsPrivate
        }


@router.post(
    "/resourceserver/character/{characterId}/publicStats/",
    dependencies=[Depends(depends.Permissison("Normal"))],
    tags=['ResourceServer'],
    summary=Ts_("apidoc.natrium.resourceserver.character.publicStats.summary"),
    description=Ts_("apidoc.natrium.resourceserver.character.publicStats.description")
)
async def rs_char_publicStats(
        account: Account = Depends(depends.AccountFromRequest),
        character: Character = Depends(depends.CharacterFromPath)
    ):
    with orm.db_session:
        if account.Id != character.Owner.Id:
            raise exceptions.PermissionDenied()
        
        return {
            "publicStats": character.Public
        }