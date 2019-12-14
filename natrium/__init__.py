from natrium.util.cache import AioMultiCacheBucket
from fastapi import FastAPI

app = FastAPI(openapi_url='/openapi/openapi.json')
cache_pool = AioMultiCacheBucket(app, {})

from natrium.applications.yggdrasil import router as Yggdrasil
from natrium.applications.natrium import router as Natrium
app.include_router(Yggdrasil, prefix="/api/yggdrasil")
app.include_router(Natrium, prefix="/natrium")