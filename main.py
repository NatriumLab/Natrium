from fastapi import FastAPI
import asyncio
from natrium.util.expiredb import AioExpireDB
from starlette.responses import UJSONResponse
import maya

app = FastAPI(title="Natrium", openapi_prefix="/openapi/")

r = AioExpireDB(app)
# 无内鬼,导入点骚玩意
r.set("1", "1", date=maya.now()+20)
r.set("2", "2", date=maya.now()+16)
r.set("3", "3", date=maya.now()+12)
r.set("4", "4", date=maya.now()+8)
r.set("5", "5", date=maya.now()+4)

@app.get("/natrium/hello_world")
async def helloworld():
    print(r.Body)
    return r.Body