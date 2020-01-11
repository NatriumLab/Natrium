from AioCacheBucket import AioMultiCacheBucket
from fastapi import FastAPI
from contextlib import contextmanager
import asyncio
from .util.iife import IIFE
from starlette.responses import JSONResponse
import maya
from natrium.json_interface import selected_jsonencoder

app = FastAPI(openapi_url='/openapi/openapi.json', default_response_class=selected_jsonencoder)
cache_pool = AioMultiCacheBucket({})
app.add_event_handler("shutdown", cache_pool.close_scavenger)

@IIFE()
def include_sub():
    import natrium.database.connection
    import natrium.database.models

    from natrium.applications.yggdrasil import router as Yggdrasil
    from natrium.applications.natrium import router as Natrium
    app.include_router(Yggdrasil, prefix="/api/yggdrasil")
    app.include_router(Natrium, prefix="/natrium")