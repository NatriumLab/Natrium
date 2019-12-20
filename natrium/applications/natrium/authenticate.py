from natrium.applications.natrium import router
from natrium.applications.natrium.buckets import TokenBucket
from pydantic import BaseModel
from typing import Optional
from fastapi import Body
import uuid
from natrium.database.models import Account
from pony import orm
from .models import AuthenticateRequest
import natrium.applications.natrium.exceptions as exceptions
from natrium.applications.natrium import models
import bcrypt
from .buckets import VerifyLocks
from .token import Token
import maya

@router.post("/authenticate/")
async def authenticate(authinfo: models.AuthenticateRequest):
    with orm.db_session:
        account = orm.select(i for i in Account if i.Email == authinfo.email)
        if not account.exists():
            raise exceptions.InvalidCredentials()
        account: Account = account.first()

        if not VerifyLocks.get(account.Id):
            VerifyLocks.setByTimedelta(account.Id, "LOCKED")
        else:
            raise exceptions.FrequencyLimit()

        AuthentidcateVerifyResult = bcrypt.checkpw(authinfo.password.encode(), account.Password)
        if not AuthentidcateVerifyResult:
            raise exceptions.InvalidCredentials()
        
        token = Token(account, authinfo.authenticate.clientToken)
        result = {
            "auth": {
                "accessToken": token.AccessToken.hex,
                "clientToken": token.ClientToken,
                "metadata": {
                    "stages": {
                        "create": token.CreateAt.rfc2822(),
                        "alive": token.AliveDate.rfc2822(),
                        "expire": token.ExpireDate.rfc2822(),
                    }
                }
            }
        }
        if authinfo.requestAccount:
            result['account'] = {
                "id": account.Id.hex,
                "email": account.Email,
                "createAt": maya.MayaDT(account.CreatedAt.timestamp()).rfc2822(),
                "rank": account.Permission
            }
        return result