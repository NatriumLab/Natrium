import uuid
from typing import Any, Dict, Optional

import maya
from fastapi import Body, Depends, Form, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from pony import orm
from pydantic import errors as PydanticErrors
from pydantic.error_wrappers import ErrorWrapper
from starlette.requests import Request

import orjson
from natrium.database.models import Account, Character, Resource
from natrium.json_interface import handler as json
from natrium.planets.buckets.natrium import TokenBucket
from natrium.planets.exceptions import natrium as exceptions
from natrium.planets.models.token.natrium import Token

from natrium.planets.models.request.natrium import AInfo, OptionalAInfo
from AioCacheBucket import AioCacheBucket


def JSONForm(*args, **kwargs) -> Any:
    async def JSONForm_warpper(formdata: str = Form(*args, **kwargs)) -> Any:
        try:
            return json.loads(formdata)
        except:
            # 这种情况只能判断为客户端传了个非json字符串过来...
            raise RequestValidationError([
                ErrorWrapper(PydanticErrors.JsonError(), ["body", "<JSONFormField>"])
            ])
            
    return Depends(JSONForm_warpper)

def TokenVerify(form=False, alias=None):
    if not form:
        async def warpper(Authenticate: AInfo) -> Token:
            try:
                token = Token.getToken(
                    Authenticate.auth.accessToken,
                    ClientToken=Authenticate.auth.clientToken
                )
            except ValueError:
                raise exceptions.AuthenticateVerifyException()
            if not token:
                raise exceptions.AuthenticateVerifyException()
            if not token.is_alive:
                raise exceptions.AuthenticateVerifyException()
            return token
        return warpper
    else:
        async def warpper(Authenticate = JSONForm(..., alias=alias)):
            data = AInfo.parse_obj(Authenticate)
            try:
                token = Token.getToken(
                    data.auth.accessToken,
                    ClientToken=data.auth.clientToken
                )
            except ValueError:
                raise exceptions.AuthenticateVerifyException()
            if not token:
                raise exceptions.AuthenticateVerifyException()
            if not token.is_alive:
                raise exceptions.AuthenticateVerifyException()
            return token
        return warpper

async def AccountFromRequest(token: Token = Depends(TokenVerify())):
    return token.Account

def AccountFromRequestForm(alias=None):
    async def AccountFromRequestForm_warpper(token = Depends(TokenVerify(True, alias=alias))):
        return token.Account
    return AccountFromRequestForm_warpper

async def TokenStatus(Authenticate: AInfo) -> Dict:
    try:
        token = Token.getToken(
            Authenticate.auth.accessToken,
            ClientToken=Authenticate.auth.clientToken
        )
    except ValueError:
        return {"status": "unknown"}
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
    try:
        token = Token.getToken(
            Authenticate.auth.accessToken,
            ClientToken=Authenticate.auth.clientToken
        )
    except ValueError:
        return None
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

def AutoIPLimits(bucket: AioCacheBucket, delta={}):
    async def warpper(request: Request):
        if bucket.get(request.client.host):
            raise exceptions.FrequencyLimit()
        bucket.setByTimedelta(request.client.host, "LOCKED", delta=delta)
    return Depends(warpper)