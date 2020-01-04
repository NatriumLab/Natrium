from fastapi import Depends, Header, Body, HTTPException
from pony import orm
from .models import AInfo
from .buckets import TokenBucket
from .token import Token 
from .exceptions import AuthenticateVerifyException

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