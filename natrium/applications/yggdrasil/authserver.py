from natrium.applications.yggdrasil import router
from conf import config
from starlette.responses import JSONResponse as Response
from starlette.requests import Request
from urllib.parse import parse_qs, urlencode, urlparse
from natrium.util.sign import key
from functools import reduce
from natrium.database.models import Character, Account, Resource
from natrium.database.connection import db
from pony import orm
from .utils import error_handle
from natrium.applications.yggdrasil import exceptions, user_auth_cooling_bucket, auth_token_pool
import bcrypt
from natrium.applications.yggdrasil.models import Token
import uuid


@router.post("/authserver/authenticate")
async def authenticate(request: Request):
    data = await request.json()
    with orm.db_session:
        user = orm.select(i for i in Account if i.Email == data.get("username"))
        if not user.exists():
            return error_handle(exceptions.InvalidCredentials())
        user: Account = user.first()

        if not user_auth_cooling_bucket.get(user.Email):
            user_auth_cooling_bucket.setByTimedelta(user.Email, "LOCKED")
        else:
            return error_handle(exceptions.InvalidCredentials())

        AuthenticateVerifyResult = bcrypt.hashpw(data.get("password").encode(), user.Salt) == user.Password
        if not AuthenticateVerifyResult:
            return error_handle(exceptions.InvalidCredentials())
        TokenUnit = Token(user, ClientToken=data.get("clientToken"))

        auth_token_pool.setByTimedelta(TokenUnit.AccessToken, TokenUnit)
        result = {
            "accessToken": TokenUnit.AccessToken.hex,
            "clientToken": TokenUnit.ClientToken,
            "availableProfiles": [
                i.FormatCharacter(unsigned=True) for i in list(user.Characters)
            ],
            "selectedProfile": {}
        }
        # print(data.get("clientToken"), TokenUnit.ClientToken)
        if user.Characters.count() == 1:  # 如果只拥有一个角色, 则自动绑定, 并修改result
            TokenUnit.setupCharacter(list(user.Characters)[0])
            result['selectedProfile'] = list(user.Characters)[0].FormatCharacter(unsigned=True)
        else:
            del result['selectedProfile']

        if data.get("requestUser"):
            result['user'] = {
                "id": user.Id.hex,
                "properties": []
            }
        return Response(result)


@router.post("/authserver/refresh")
async def refresh(request: Request):
    data = await request.json()

    origin_token = Token.getToken(data.get("accessToken"), ClientToken=data.get("clientToken"))

    if not origin_token:
        return error_handle(exceptions.InvalidToken())

    if origin_token.is_disabled:
        # 如果过期了还被获取到...啊当然这种可能性很小, 但也不是没有, 以防万一
        return error_handle(exceptions.InvalidToken())

    user = origin_token.Account
    selected_profile = origin_token.Character or None

    if data.get("selectedProfile"):
        if selected_profile:
            return error_handle(exceptions.IllegalArgumentException())

        with orm.db_session:
            try:
                attempt_select = orm.select(i \
                                            for i in Character \
                                            if i.PlayerId == uuid.UUID(data['selectedProfile'].get("id")) and \
                                            i.PlayerName == data['selectedProfile'].get("name")
                                            )  # 查询要绑定的角色
            except (AttributeError, ValueError):
                return error_handle(exceptions.IllegalArgumentException())
            if not attempt_select.exists():
                return error_handle(exceptions.IllegalArgumentException())
            else:
                attempt_select = attempt_select.first()

            if attempt_select.Owner.Id != user.Id:  # 直接eq会爆炸, 故匹配ID
                return error_handle(exceptions.WrongBind())
            selected_profile = attempt_select

    auth_token_pool.delete(origin_token.AccessToken)
    TokenUnit = Token(
        Account=user,
        ClientToken=origin_token.ClientToken,
        Character=selected_profile if data.get('selectedProfile') else None
    )
    auth_token_pool.setByTimedelta(TokenUnit.AccessToken, TokenUnit)

    result = {
        "accessToken": TokenUnit.AccessToken.hex,
        "clientToken": TokenUnit.ClientToken
    }
    # print("!!!", data.get("clientToken"), TokenUnit.ClientToken, origin_token.ClientToken)
    if selected_profile:
        result['selectedProfile'] = selected_profile.FormatCharacter(unsigned=True)

    if data.get("requestUser"):
        result['user'] = {
            "id": user.Id.hex,
            "properties": []
        }

    return Response(result)


@router.post("/authserver/validate")
async def validate(request: Request):
    data = await request.json()
    origin_token = Token.getToken(data.get("accessToken"), ClientToken=data.get("clientToken"))
    if not origin_token:
        return error_handle(exceptions.InvalidToken())
    if origin_token.is_alived:
        return Response(status_code=204)
    else:
        return error_handle(exceptions.InvalidToken())


@router.post("/authserver/invalidate")
async def invalidate(request: Request):
    """注销请求中给出的Token"""
    data: dict = await request.json()
    origin_token = Token.getToken(data.get("accessToken"), ClientToken=data.get("clientToken"))
    if origin_token:
        auth_token_pool.delete(origin_token.AccessToken)
    else:
        if data.get("clientToken"):
            origin_token = Token.getToken(data.get("accessToken"))
            if not origin_token:
                return error_handle(exceptions.InvalidToken())
            auth_token_pool.delete(origin_token.AccessToken)
        else:
            return Response(status_code=204)
    return Response(status_code=204)


@router.post("/authserver/signout")
async def signout(request: Request):
    data = await request.json()
    with orm.db_session:
        user = orm.select(i for i in Account if i.Email == data.get("username"))
        if not user.exists():
            return error_handle(exceptions.InvalidCredentials())
        user: Account = user.first()

        if not user_auth_cooling_bucket.get(user.Email):
            user_auth_cooling_bucket.setByTimedelta(user.Email, "LOCKED")
        else:
            return error_handle(exceptions.InvalidCredentials())

        AuthenticateVerifyResult = bcrypt.hashpw(data.get("password").encode(), user.Salt) == user.Password
        if not AuthenticateVerifyResult:
            return error_handle(exceptions.InvalidCredentials())
        for i in Token.getManyTokens(user):
            auth_token_pool.delete(i.AccessToken)
        return Response(status_code=204)
