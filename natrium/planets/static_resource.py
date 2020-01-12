from i18n import t as Ts_
from natrium import app
from starlette.responses import FileResponse
from pathlib import Path

@app.get("/natrium/static/picture/resource/{resource}", tags=["Utils"],
    summary=Ts_("apidoc.utils.static_resource.summary"),
    description=Ts_("apidoc.utils.static_resource.description"),
)
async def static_resource(resource: str):
    return FileResponse(str(Path(f"./assets/resources/{resource}.png").absolute()))