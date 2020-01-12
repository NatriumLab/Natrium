import uuid
from functools import reduce
from urllib.parse import parse_qs, urlencode, urlparse

from i18n import t as Ts_
from pony import orm
from starlette.requests import Request
from starlette.responses import JSONResponse as Response

from conf import config
from natrium.applications.yggdrasil import router, session_server_join
from natrium.applications.yggdrasil.models import Token
from natrium.database.connection import db
from natrium.database.models import Account, Character, Resource
from natrium.planets.exceptions import yggdrasil as exceptions
from natrium.util.sign import key


@router.post("/sessionserver/session/minecraft/join", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.sessionserver.joinServer.summary"),
    description=Ts_("apidoc.yggdrasil.sessionserver.joinServer.description"))
async def session_minecraft_join(request: Request):
    data = await request.json()
    token = Token.getToken(data.get("accessToken"))
    if not (bool(token) and any([
        not token.Character,
        not token.is_alived,
    ])):
        raise exceptions.InvalidToken()

    with orm.db_session:
        result = orm.select(i for i in Character if i.Id == token.Character.Id)
        if not result.exists():
            raise exceptions.InvalidToken()
        result: Character = result.first()
        if data.get("selectedProfile") != result.PlayerId.hex:
            raise exceptions.InvalidToken()
        session_server_join.setByTimedelta(data.get("serverId"), {
            "token": token,
            "character": result.FormatCharacter(Properties=True, auto=True),
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
    with orm.db_session:
        char = orm.select(i for i in Character if i.PlayerId == profile)
        if not char.exists():
            return Response(status_code=204)
        char: Character = char.first()
        return char.FormatCharacter(
            unsigned=unsigned, Properties=True, auto=True,
            url=f"{request.url.scheme}://{request.url.netloc}"
        )
