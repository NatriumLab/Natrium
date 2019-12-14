from fastapi import APIRouter
from starlette.responses import FileResponse
from pathlib import Path

router = APIRouter()

@router.get("/static/picture/resource/{resource}")
async def static_resource(resource: str):
    return FileResponse(str(Path(f"./assets/resources/{resource}.png").absolute()))