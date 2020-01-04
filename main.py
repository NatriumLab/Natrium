from fastapi import FastAPI
import asyncio
from starlette.responses import UJSONResponse
from natrium.util.randoms import String
import maya
import random
import uuid
from natrium import makeapp

if __name__ == "__main__":
    import uvicorn
    with makeapp() as app:
        uvicorn.run(app, port=8000)
