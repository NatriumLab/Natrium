from fastapi import Depends, Header, Body, HTTPException, Form
from pony import orm
from .models import AInfo, OptionalAInfo
from .buckets import TokenBucket
from .token import Token 
from .exceptions import AuthenticateVerifyException
from . import exceptions
from natrium.database.models import Account, Resource, Character
from typing import Dict, Optional
import maya
from starlette.requests import Request
import uuid
from natrium.json_interface import handler as json
import orjson

def TokenVerify(form=False):
    if not form:
        async def warpper(Authenticate: AInfo) -> Token:
            token = Token.getToken(
                Authenticate.auth.accessToken,
                ClientToken=Authenticate.auth.clientToken
            )
            if not token:
                raise AuthenticateVerifyException()
            if not token.is_alive:
                raise AuthenticateVerifyException()
            return token
        return warpper
    else:
        async def warpper(Authenticate = Form(...)):
            data = AInfo.parse_raw(Authenticate)
            token = Token.getToken(
                data.auth.accessToken,
                ClientToken=data.auth.clientToken
            )
            if not token:
                raise AuthenticateVerifyException()
            if not token.is_alive:
                raise AuthenticateVerifyException()
            return token
        return warpper

async def AccountFromRequest(token: Token = Depends(TokenVerify())):
    return token.Account

async def AccountFromRequestForm(token = Depends(TokenVerify(True))):
    return token.Account

async def TokenStatus(Authenticate: AInfo) -> Dict:
    token = Token.getToken(
        Authenticate.auth.accessToken,
        ClientToken=Authenticate.auth.clientToken
    )
    if not token:
        return {"status": "non-exist"}
    if token.ExpireDate > maya.now() > token.AliveDate:
        return {"status": "requireRefresh", "_t": token}
    elif token.is_alive:
        return {"status": "alive", "_t": token}
    elif token.is_expired:
        return {"status": "expired", "_t": token}
    else:
        return {"status": "unknown"}
    
def Permissison(Permission):
    async def PermissionWarpper(token: Token = Depends(TokenVerify())):
        if token.Account.Permission != Permission:
            raise exceptions.PermissionDenied()
    return PermissionWarpper

async def OptionalTokenVerify(Authenticate: AInfo) -> Optional[Token]:
    token = Token.getToken(
        Authenticate.auth.accessToken,
        ClientToken=Authenticate.auth.clientToken
    )
    if not token:
        return None
    if not token.is_alive:
        return None
    return token

async def O_N_Owen(request: Request) -> Optional[Account]:
    """自动发现请求主体中包含的可用合法用户令牌 致敬 `O.N Owen 就是她吗?`.\n
    与单纯的验证令牌不同, 这个函数返回一个Account  \n
    请求中的合法用户令牌是可选的.
    """
    if request.method != 'POST':
        return

    try:
        data: dict = await request.json()
    except (json.decoder.JSONDecodeError, ValueError):
        data = {}

    auth = type("FAKE", (object,), {
        "auth": type("FAKE", (object,), {
            "accessToken": data.get("auth", {}).get("accessToken"),
            "clientToken": data.get("auth", {}).get("clientToken")
        })
    }) if data.get("auth") else None # ko no FAKE da.

    if not auth:
        return

    try:
        status = await TokenStatus(auth)
    except exceptions.AuthenticateVerifyException:
        return

    if status['status'] == "alive":
        return status['_t'].Account

async def CharacterFromPath(characterId: uuid.UUID):
    with orm.db_session:
        character = orm.select(i for i in Character if i.Id == characterId)
        if not character.exists():
            raise exceptions.NoSuchResourceException()
        character: Character = character.first()
        return character

async def ResourceFromPath(resourceId: uuid.UUID):
    with orm.db_session:
        resource = orm.select(i for i in Resource if i.Id == resourceId)
        if not resource.exists():
            raise exceptions.NoSuchResourceException()
        resource: Resource = resource.first()
        return resource