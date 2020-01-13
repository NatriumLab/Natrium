import uuid
from functools import reduce
from urllib.parse import parse_qs, urlencode, urlparse

from i18n import t as Ts_
from pony import orm
from starlette.requests import Request
from starlette.responses import JSONResponse as Response

from conf import config
from natrium.applications.yggdrasil import router
from natrium.planets.buckets.yggdrasil import session_server_join
from natrium.planets.models.token.yggdrasil import Token
from natrium.database.connection import db
from natrium.database.models import Account, Character, Resource
from natrium.planets.exceptions import yggdrasil as exceptions
from natrium.util.sign import key
from natrium.planets.models.request import yggdrasil as RModels


@router.post("/sessionserver/session/minecraft/join", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.sessionserver.joinServer.summary"),
    description=Ts_("apidoc.yggdrasil.sessionserver.joinServer.description"))
async def session_minecraft_join(info: RModels.Sessionserver_ServerJoin, request: Request):
    token = Token.getToken(info.accessToken)
    if not token:
        raise exceptions.InvalidToken()
    if not token.is_alived:
        raise exceptions.InvalidToken()
    if not token.Character:
        raise exceptions.InvalidToken()

    character: Character = Character.get(Id=token.Character.Id)
    if not character:
        raise exceptions.InvalidToken()

    if info.selectedProfile != character.PlayerId:
        raise exceptions.InvalidToken()

    session_server_join.setByTimedelta(info.serverId, {
        "token": token,
        "character": character.FormatCharacter(Properties=True, auto=True),
        "remoteIp": request.client
    })
    return Response(status_code=204)


@router.get("/sessionserver/session/minecraft/hasJoined", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.sessionserver.hasJoined.summary"),
    description=Ts_("apidoc.yggdrasil.sessionserver.hasJoined.description"))
async def session_minecraft_hasJoined(username, serverId, ip=None):
    info = session_server_join.get(serverId)
    if not info:
        return Response(status_code=204)
    if all([
        username == info['character']['name'],
        ip == info['remoteIp'] if ip else True
    ]):
        return info['character']
    else:
        return Response(status_code=204)


@router.get("/sessionserver/session/minecraft/profile/{profile}", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.sessionserver.profileQuery.summary"),
    description=Ts_("apidoc.yggdrasil.sessionserver.profileQuery.description"))
async def session_minecraft_query_profiles(request: Request, profile: uuid.UUID, unsigned: bool = True):
    character: Character = Character.get(PlayerId=profile)
    if not character:
        return Response(status_code=204)

    return character.FormatCharacter(
        unsigned=unsigned, Properties=True, auto=True,
        url=f"{request.url.scheme}://{request.url.netloc}"
    )
