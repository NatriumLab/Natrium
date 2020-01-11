from fastapi import Depends
from .. import depends
from .. import router
from .. import exceptions
import uuid
from pony import orm
from typing import Optional
from natrium.database.models import Account, Resource, Character

@router.get("/resourceserver/account/{accountId}")
@router.post("/resourceserver/account/{accountId}")
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

@router.get("/resourceserver/character/{characterId}")
@router.post("/resourceserver/character/{characterId}")
async def resources_character_id(
        characterId: uuid.UUID,
        optionalAccount: Optional[Account] = Depends(depends.O_N_Owen)
    ):
    with orm.db_session:
        character = orm.select(i for i in Character if i.Id == characterId)
        if not character.exists():
            raise exceptions.NoSuchResourceException()
        character: Character = character.first()

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

@router.get("/resourceserver/resource/{resourceId}")
@router.post("/resourceserver/resource/{resourceId}")
async def resources_resource_id(
        resource: Resource = Depends(depends.ResourceFromPath),
        optionalAccount: Optional[Account] = Depends(depends.O_N_Owen),
        requestHash: bool = False
    ):
    with orm.db_session:
        resource: Resource = Resource.get(Id=resource.Id)
        if resource.IsPrivate and \
                    resource.Owner.Id != (optionalAccount.Id if optionalAccount else None):
            raise exceptions.PermissionDenied()
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

@router.post("/resourceserver/resource/{resourceId}/forks")
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