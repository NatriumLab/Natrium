from fastapi import APIRouter
from conf import config
from starlette.responses import JSONResponse as Response
from starlette.requests import Request
from urllib.parse import parse_qs, urlencode, urlparse
from natrium.util.sign import key
from functools import reduce
from natrium.database.connection import db
from natrium.database.models import Character
from pony import orm
from natrium import cache_pool

# 设置缓存池
cache_pool.setup({
    "yggdrasil.authserver.user.verify.cooldown": {
        "default_expire_delta": {
            "seconds": 0.5
        }
    },
    "yggdrasil.authserver.authenticate.token_pool": {
        "default_expire_delta": config['token']['validate']['maya-configure']
    },
    "yggdrasil.sessionserver.joinserver": {
        "default_expire_delta": {
            "seconds": 30
        }
    }
})
user_auth_cooling_bucket = cache_pool.getBucket("yggdrasil.authserver.user.verify.cooldown")
auth_token_pool = cache_pool.getBucket("yggdrasil.authserver.authenticate.token_pool")
session_server_join = cache_pool.getBucket("yggdrasil.sessionserver.joinserver")

router = APIRouter()

@router.get("/")
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

@router.post("/api/profiles/minecraft")
async def yggdrasil_profiles_query(request: Request):
    data = await request.json()
    data = reduce(lambda x, y: x if y in x else x + [y], [[], ] + data)
    with orm.db_session:
        result = [i.FormatCharacter(unsigned=True) for i in list(
            orm.select(i for i in Character if i.PlayerName in data[0:config['meta']['ProfilesQueryLimit'] - 1]))]
    return result


# 子模块
import natrium.applications.yggdrasil.authserver
import natrium.applications.yggdrasil.sessionserver
