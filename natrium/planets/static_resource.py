from i18n import t as Ts_
from natrium import app
from starlette.responses import FileResponse, Response
from pathlib import Path

@app.get("/natrium/static/picture/resource/{resource}", tags=["Utils"],
    summary=Ts_("apidoc.utils.static_resource.summary"),
    description=Ts_("apidoc.utils.static_resource.description"),
)
async def static_resource(resource: str):
    try:
        if not Path(f"./assets/resources/{resource}.png").exists():
            return Response(status_code=404)
    except OSError:
        return Response(status_code=404)
    return FileResponse(str(Path(f"./assets/resources/{resource}.png").absolute()))
        