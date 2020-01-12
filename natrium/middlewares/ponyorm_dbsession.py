from natrium import app
from starlette.requests import Request
from pony import orm

# PonyORM db_session middlewire
@app.middleware("http")
async def db_session_middlewire(request: Request, call_next):
    with orm.db_session:
        return await call_next(request)