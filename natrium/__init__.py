from fastapi import FastAPI
from .util.iife import IIFE
from natrium.json_interface import selected_jsonencoder

app = FastAPI(openapi_url='/openapi/openapi.json', default_response_class=selected_jsonencoder)
from natrium.planets.buckets import cache_pool
app.add_event_handler("shutdown", cache_pool.close_scavenger)

@IIFE()
def include_sub():
    import natrium.database.connection
    import natrium.database.models

    from natrium.applications.yggdrasil import router as Yggdrasil
    from natrium.applications.natrium import router as Natrium
    app.include_router(Yggdrasil, prefix="/api/yggdrasil")
    app.include_router(Natrium, prefix="/natrium")

@IIFE()
def include_middlewares():
    import natrium.middlewares

@IIFE()
def include_planets():
    import natrium.planets

def run():
    import uvicorn
    try:
        uvicorn.run(app, port=8000)
    finally:
        cache_pool.close_scavenger()