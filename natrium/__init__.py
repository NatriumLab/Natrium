from fastapi import FastAPI
from .util.iife import IIFE
from natrium.json_interface import selected_jsonencoder
from pathlib import Path
from conf import config
import logging

app = FastAPI(openapi_url='/openapi/openapi.json', default_response_class=selected_jsonencoder)
from natrium.planets.buckets import cache_pool

@IIFE()
def init_cache_close_scavenger():
    app.add_event_handler("shutdown", cache_pool.close_scavenger)

@IIFE()
def include_middlewares():
    import natrium.middlewares

@IIFE()
def load_i18n():
    import i18n
    i18n.load_path.append(str(Path("./assets/i18n/").resolve()))
    i18n.set("locale", config['language']['default'])
    i18n.set("fallback", config['language']['fallback'])

@IIFE()
def include_sub():
    import natrium.database.connection
    import natrium.database.models

    from natrium.applications.yggdrasil import router as Yggdrasil
    from natrium.applications.natrium import router as Natrium
    app.include_router(Yggdrasil, prefix="/api/yggdrasil")
    app.include_router(Natrium, prefix="/natrium")

def run():
    import uvicorn
    try:
        uvicorn.run(app, port=8000)
    finally:
        cache_pool.close_scavenger()