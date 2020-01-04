from AioCacheBucket import AioMultiCacheBucket
from fastapi import FastAPI
from contextlib import contextmanager
import asyncio

app = FastAPI(openapi_url='/openapi/openapi.json')
cache_pool = AioMultiCacheBucket({})

def include_sub():
    from natrium.applications.yggdrasil import router as Yggdrasil
    from natrium.applications.natrium import router as Natrium
    app.include_router(Yggdrasil, prefix="/api/yggdrasil")
    app.include_router(Natrium, prefix="/natrium")

def pool_close():
    cache_pool.close_scavenger()

@contextmanager
def makeapp():
    include_sub()
    try:
        yield app
    finally:
        pool_close()