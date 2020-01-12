from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import FileResponse
from pathlib import Path
from .depends import JSONForm
from natrium import app
from i18n import t as Ts_
from pony import orm

router = APIRouter()

import natrium.applications.natrium.buckets
import natrium.applications.natrium.exceptions

# sub.
import natrium.applications.natrium.paths.authserver
import natrium.applications.natrium.paths.resourceserver
import natrium.applications.natrium.paths.optionserver
import natrium.applications.natrium.paths.amadeus