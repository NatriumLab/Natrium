from . import router
from conf import config
from starlette.requests import Request
from starlette.responses import JSONResponse as Response
from i18n import t as Ts_
from natrium.util.sign import key
from functools import reduce
from pony import orm
from natrium.database.models import Character
import typing
from natrium.planets.models.request import yggdrasil as RModels


@router.get("/",
    tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.index.summary"),
    description=Ts_("apidoc.yggdrasil.index.description")
)
async def yggdrasil_index(request: Request):
    return Response({
        "meta": {
            "serverName": config['meta']["serverName"],
            "implementationName": config['meta']['implementationName'],
            "implementationVersion": config['meta']['version']
        },
        "skinDomains": config['meta'].get("siteDomains") or [request.url.netloc.split(":")[0]],
        "signaturePublickey": key['public'].export_key().decode()
    })

@router.post("/api/profiles/minecraft", tags=['Yggdrasil'],
    summary=Ts_("apidoc.yggdrasil.profilesQuery.summary"),
    description=Ts_("apidoc.yggdrasil.profilesQuery.description"),
    response_model=RModels.MultiCharacters
)
async def yggdrasil_profiles_query(request: Request) -> RModels.MultiCharacters:
    data = await request.json()
    data = reduce(lambda x, y: x if y in x else x + [y], [[], ] + data)
    with orm.db_session:
        result = [i.FormatCharacter(unsigned=True) for i in list(
            orm.select(i for i in Character if i.PlayerName in data[0:config['meta']['ProfilesQueryLimit'] - 1]))]
    return result