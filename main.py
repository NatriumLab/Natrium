from fastapi import FastAPI
import asyncio
from starlette.responses import UJSONResponse
from natrium.util.randoms import String
import maya
import random
import uuid

app = FastAPI(title="Natrium", openapi_prefix="/openapi/")
from natrium import app as NatriumSubApp

app.mount("/", NatriumSubApp)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)