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
from natrium.applications.yggdrasil import exceptions, session_server_join
from natrium.applications.yggdrasil.models import Token
import uuid
from i18n import t as Ts_

@router.post("/sessionserver/session/minecraft/join", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.sessionserver.joinServer.summary"),
    description=Ts_("apidoc.yggdrasil.sessionserver.joinServer.description"))
async def session_minecraft_join(request: Request):
    data = await request.json()
    token = Token.getToken(data.get("accessToken"))
    if not token:
        return error_handle(exceptions.InvalidToken())
    if not token.is_alived:
        return error_handle(exceptions.InvalidToken())
    if not token.Character:
        return error_handle(exceptions.InvalidToken())
    with orm.db_session:
        result = orm.select(i for i in Character if i.Id == token.Character.Id)
        if not result.exists():
            return error_handle(exceptions.InvalidToken())
        result: Character = result.first()
        if data.get("selectedProfile") != result.PlayerId.hex:
            return error_handle(exceptions.InvalidToken())
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
