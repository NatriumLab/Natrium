from .. import depends, router
from natrium.planets.buckets.natrium import MostimaBuckets
from natrium.planets.models.request.natrium import MostimaRegister
from natrium.planets.models.response.natrium import MostimaRequest_Response
from natrium.database.models import Account
from natrium.planets.exceptions import natrium as exceptions
from i18n import t as Ts_

requests_bucket = MostimaBuckets.requests

@router.post(
    "/mostima/register/request",
    dependencies=[
        depends.AutoIPLimits(MostimaBuckets.requestLimit),
    ],
    summary=Ts_("apidoc.natrium.mostima_register.request.summary"),
    description=Ts_("apidoc.natrium.mostima_register.request.description"),
    response_model=MostimaRequest_Response
)
async def mostima_register_request(mr: MostimaRegister):
    if Account.get(Email=mr.email):
        raise exceptions.OccupyExistedAddress()
    