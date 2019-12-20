from fastapi import FastAPI
import asyncio
from starlette.responses import UJSONResponse
from natrium.util.randoms import String
import maya
import random
import uuid
from natrium import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8080, reload=True)