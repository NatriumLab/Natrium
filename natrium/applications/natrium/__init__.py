from fastapi import APIRouter
from natrium import app

router = APIRouter()

# sub.
import natrium.planets.buckets.natrium # register cache buckets

import natrium.applications.natrium.paths.amadeus
import natrium.applications.natrium.paths.authserver
import natrium.applications.natrium.paths.optionserver
import natrium.applications.natrium.paths.resourceserver