from fastapi import APIRouter
from i18n import t as Ts_
from pony import orm
from starlette.requests import Request
from starlette.responses import FileResponse

import natrium.applications.natrium.buckets

from natrium import app
from .depends import JSONForm

router = APIRouter()

# sub.
import natrium.applications.natrium.paths.amadeus
import natrium.applications.natrium.paths.authserver
import natrium.applications.natrium.paths.optionserver
import natrium.applications.natrium.paths.resourceserver