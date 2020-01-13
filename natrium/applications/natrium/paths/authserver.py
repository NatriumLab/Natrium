import uuid
from typing import Optional

import bcrypt
import maya
from fastapi import Body, Depends
from i18n import t as Ts_
from pony import orm
from pydantic import BaseModel
from starlette.requests import Request

from natrium.applications.natrium import depends, router
from natrium.database.models import Account
from natrium.planets.buckets.natrium import (TokenBucket, ValidateIpLocks,
                                             VerifyLocks)
from natrium.planets.exceptions import natrium as exceptions
from natrium.planets.models.request.natrium import (AccountAuth,
                                                    AuthenticateRequest)
from natrium.planets.models.token.natrium import Token
from natrium.util.randoms import String


@router.post("/authserver/", tags=['AuthServer'],
    summary=Ts_("apidoc.natrium.authserver.index.summary"),
    description=Ts_("apidoc.natrium.authserver.index.description"))
async def authserver_authenticate(authinfo: AuthenticateRequest):
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
    TokenBucket.setByTimedelta(token.AccessToken, token)
    
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


@router.post("/authserver/refresh", tags=['AuthServer'],
    summary=Ts_("apidoc.natrium.authserver.refresh.summary"),
    description=Ts_("apidoc.natrium.authserver.refresh.description"))
async def authserver_refresh(old_token: Token = Depends(depends.TokenVerify)):
    account = Token.Account

    # 频率限制
    if not VerifyLocks.get(account.Id):
        VerifyLocks.setByTimedelta(account.Id, "LOCKED")
    else:
        raise exceptions.FrequencyLimit()

    if Token.ClientToken:
        clientToken = Token.ClientToken
    else:
        clientToken = String(16)
    
    TokenBucket.delete(old_token.AccessToken)
    NewToken = Token(account, clientToken)
    return {
        "auth": {
            "accessToken": NewToken.AccessToken.hex,
            "clientToken": NewToken.ClientToken,
            "metadata": {
                "stages": {
                    "create": NewToken.CreateAt.rfc2822(),
                    "alive": NewToken.AliveDate.rfc2822(),
                    "expire": NewToken.ExpireDate.rfc2822(),
                }
            }
        }
    }

@router.post("/authserver/validate", tags=['AuthServer'],
    summary=Ts_("apidoc.natrium.authserver.validate.summary"),
    description=Ts_("apidoc.natrium.authserver.validate.description"))
async def authserver_validate(
        request: Request,
        status = Depends(depends.TokenStatus)
    ):
    """请求Token状态, 对于该API, 使用了IP限制, 约为3s一次."""

    if not ValidateIpLocks.get(request.client.host):
        ValidateIpLocks.setByTimedelta(request.client.host, "LOCKED")
    else:
        raise exceptions.FrequencyLimit()

    return {
        "status": "alive" if status['status'] == "alive" else "non-alive"
    }

@router.post("/authserver/invalidate", tags=['AuthServer'],
    summary=Ts_("apidoc.natrium.authserver.invalidate.summary"),
    description=Ts_("apidoc.natrium.authserver.invalidate.description"))
async def authserver_invalidate(token: Token = Depends(depends.TokenVerify)):
    """注销请求中给出的Token"""
    TokenBucket.delete(token.AccessToken)
    return {"operator": "success"}

@router.post("/authserver/signout", tags=['AuthServer'],
    summary=Ts_("apidoc.natrium.authserver.signout.summary"),
    description=Ts_("apidoc.natrium.authserver.signout.description"))
async def authserver_signout(authinfo: AccountAuth):
    account = Account.get(Email=authinfo.email)
    if not account.exists():
        raise exceptions.InvalidCredentials()

    if not VerifyLocks.get(account.Id):
        VerifyLocks.setByTimedelta(account.Id, "LOCKED")
    else:
        raise exceptions.FrequencyLimit()

    AuthentidcateVerifyResult = bcrypt.checkpw(authinfo.password.encode(), account.Password)
    if not AuthentidcateVerifyResult:
        raise exceptions.InvalidCredentials()

    for i in TokenBucket:
        if TokenBucket.get(i).Account.Id == account.Id:
            TokenBucket.delete(i)
    return {"operator": "success"}
