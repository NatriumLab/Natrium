import uuid
from functools import reduce
from urllib.parse import parse_qs, urlencode, urlparse

import bcrypt
from i18n import t as Ts_
from pony import orm
from starlette.requests import Request
from starlette.responses import JSONResponse as Response

from conf import config
from natrium.applications.yggdrasil import router
from natrium.database.connection import db
from natrium.database.models import Account, Character, Resource
from natrium.planets.buckets.yggdrasil import (auth_token_pool,
                                               user_auth_cooling_bucket)
from natrium.planets.exceptions import yggdrasil as exceptions
from natrium.planets.models.token.yggdrasil import Token
from natrium.util.sign import key
from natrium.planets.models.request import yggdrasil as RModels

@router.post("/authserver/authenticate", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.authserver.authenticate.summary"),
    description=Ts_("apidoc.yggdrasil.authserver.authenticate.description")
)
async def authenticate(info: RModels.Authserver_Authenticate):
    user: Account = Account.get(Email=info.username)
    if not user:
        raise exceptions.InvalidCredentials()

    if not user_auth_cooling_bucket.get(user.Email):
        user_auth_cooling_bucket.setByTimedelta(user.Email, "LOCKED")
    else:
        raise exceptions.InvalidCredentials()

    if not bcrypt.checkpw(info.password.encode(), user.Password):
        raise (exceptions.InvalidCredentials())
 
    TokenUnit = Token(user, ClientToken=info.clientToken)
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
    if info.requestUser:
        result['user'] = {
            "id": user.Id.hex,
            "properties": []
        }
    return Response(result)


@router.post("/authserver/refresh", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.authserver.refresh.summary"),
    description=Ts_("apidoc.yggdrasil.authserver.refresh.description")
)
async def refresh(info: RModels.Authserver_Refresh):
    origin_token = Token.getToken(info.accessToken, ClientToken=info.clientToken)

    if not origin_token:
        raise exceptions.InvalidToken()

    if origin_token.is_disabled:
        # 如果过期了还被获取到...啊当然这种可能性很小, 但也不是没有, 以防万一
        raise exceptions.InvalidToken()

    user = origin_token.Account
    selected_profile = origin_token.Character or None

    if info.selectedProfile:
        if selected_profile:
            raise exceptions.IllegalArgumentException()

        with orm.db_session:
            try:
                attempt_select = Character.get(
                    PlayerId=info.selectedProfile.id,
                    PlayerName=info.selectedProfile.name
                )
            except (AttributeError, ValueError):
                raise exceptions.IllegalArgumentException()
            if not attempt_select:
                raise exceptions.IllegalArgumentException()

            if attempt_select.Owner.Id != user.Id:  # 直接eq会爆炸, 故匹配ID
                raise exceptions.WrongBind()
            selected_profile = attempt_select

    auth_token_pool.delete(origin_token.AccessToken)
    TokenUnit = Token(
        Account=user,
        ClientToken=origin_token.ClientToken,
        Character=selected_profile if info.selectedProfile else None
    )
    auth_token_pool.setByTimedelta(TokenUnit.AccessToken, TokenUnit)

    result = {
        "accessToken": TokenUnit.AccessToken.hex,
        "clientToken": TokenUnit.ClientToken
    }
    # print("!!!", data.get("clientToken"), TokenUnit.ClientToken, origin_token.ClientToken)
    if selected_profile:
        result['selectedProfile'] = selected_profile.FormatCharacter(unsigned=True)

    if info.requestUser:
        result['user'] = {
            "id": user.Id.hex,
            "properties": []
        }

    return Response(result)


@router.post("/authserver/validate", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.authserver.validate.summary"),
    description=Ts_("apidoc.yggdrasil.authserver.validate.description")
)
async def validate(info: RModels.Authserver_Validate):
    origin_token = Token.getToken(info.accessToken, ClientToken=info.clientToken)
    if not origin_token:
        raise exceptions.InvalidToken()
    if origin_token.is_alived:
        return Response(status_code=204)
    else:
        raise exceptions.InvalidToken()


@router.post("/authserver/invalidate", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.authserver.invalidate.summary"),
    description=Ts_("apidoc.yggdrasil.authserver.invalidate.description")
)
async def invalidate(info: RModels.Authserver_Invalidate):
    """注销请求中给出的Token"""
    origin_token = Token.getToken(info.accessToken, ClientToken=info.clientToken)
    if origin_token:
        auth_token_pool.delete(origin_token.AccessToken)
    else:
        if info.clientToken:
            origin_token = Token.getToken(info.accessToken)
            if not origin_token:
                raise exceptions.InvalidToken()
            auth_token_pool.delete(origin_token.AccessToken)
        else:
            return Response(status_code=204)
    return Response(status_code=204)


@router.post("/authserver/signout", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.authserver.signout.summary"),
    description=Ts_("apidoc.yggdrasil.authserver.signout.description"),
)
async def signout(info: RModels.Authserver_Signout):
    user: Account = Account.get(Email=info.username)
    if not user:
        raise exceptions.InvalidCredentials()

    if not user_auth_cooling_bucket.get(user.Email):
        user_auth_cooling_bucket.setByTimedelta(user.Email, "LOCKED")
    else:
        raise exceptions.InvalidCredentials()

    if not bcrypt.checkpw(info.password.encode("utf-8"), user.Password):
        raise exceptions.InvalidCredentials()
    for i in Token.getManyTokens(user):
        auth_token_pool.delete(i.AccessToken)
    return Response(status_code=204)
