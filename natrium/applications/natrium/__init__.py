from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import FileResponse

import natrium.planets.buckets.natrium

from natrium import app

router = APIRouter()

# sub.
import natrium.applications.natrium.paths.amadeus
import natrium.applications.natrium.paths.authserver
import natrium.applications.natrium.paths.optionserver
import natrium.applications.natrium.paths.resourceserver