from fastapi import Depends, Header, Body, HTTPException
from pony import orm
from .models import AInfo
from .buckets import TokenBucket
from .token import Token 
from .exceptions import AuthenticateVerifyException
from typing import Dict
import maya

async def TokenVerify(Authenticate: AInfo) -> Token:
    token = Token.getToken(
        Authenticate.auth.accessToken,
        ClientToken=Authenticate.auth.clientToken
    )
    if not token:
        raise AuthenticateVerifyException()
    if not token.is_alive:
        raise AuthenticateVerifyException()
    return token

async def TokenStatus(Authenticate: AInfo) -> Dict:
    token = Token.getToken(
        Authenticate.auth.accessToken,
        ClientToken=Authenticate.auth.clientToken
    )
    if not token:
        return {"status": "non-exist"}
    if token.ExpireDate > maya.now() > token.AliveDate:
        return {"status": "requireRefresh"}
    elif token.is_alive:
        return {"status": "alive"}
    elif token.is_expired:
        return {"status": "expired"}
    else:
        return {"status": "unknown"}
    