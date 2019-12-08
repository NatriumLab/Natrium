from fastapi import FastAPI
import asyncio
from natrium.util.expiredb import AioExpireDB
from starlette.responses import UJSONResponse
import maya
import random
import uuid

app = FastAPI(title="Natrium", openapi_prefix="/openapi/")

r = AioExpireDB(app)
# 无内鬼,导入点骚玩意
"""
for _ in range(1, 100):
    r.set(uuid.uuid4(), uuid.uuid4(), date=maya.now()+random.randint(10, 20))
"""
@app.get("/natrium/hello_world")
async def helloworld():
    r.set(uuid.uuid4(), uuid.uuid4(), date=maya.now()+5)
    return {"count": 1}