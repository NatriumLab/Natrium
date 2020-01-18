from .. import depends, router
from natrium.planets.buckets.natrium import MostimaBuckets
from natrium.planets.models.request.natrium import MostimaRegister
from natrium.planets.components.email import emailer
from natrium.planets.models.response.natrium import MostimaRequest_Response
from natrium.database.models import Account
from natrium.planets.exceptions import natrium as exceptions
from starlette.requests import Request
from starlette.responses import RedirectResponse
from AioCacheBucket import AioCacheBucket
from i18n import t as Ts_
from natrium.util.randoms import String
from conf import config
from urllib.parse import ParseResult, urlunparse, urlencode, urlparse
import bcrypt
from natrium.json_interface import selected_jsonencoder
from pony import orm

requests_bucket = MostimaBuckets.requests

@router.post(
    "/mostima/register/request",
    dependencies=[
        depends.AutoIPLimits(MostimaBuckets.requestLimit),
    ],
    tags=["Mostima"],
    summary=Ts_("apidoc.natrium.mostima_register.request.summary"),
    description=Ts_("apidoc.natrium.mostima_register.request.description"),
    response_model=MostimaRequest_Response
)
async def mostima_register_request(register_info: MostimaRegister, request: Request):
    attempt_assert_occupy = Account.get(Email=register_info.email)
    if attempt_assert_occupy:
        raise exceptions.OccupyExistedAddress({
            "accountId": attempt_assert_occupy.Id
        })
    # 尝试断言: 有无Email相同账号

    # 断言被跳过, 无Email相同账号
    if not MostimaBuckets.requestLimit.get(register_info.email):
        MostimaBuckets.requestLimit.setByTimedelta(register_info.email, "LOCKED", delta={
            "seconds": 60
        })
    else:
        raise exceptions.FrequencyLimit({
            "email": register_info.email
        })

    # 生成verifyId
    verifyId = String(config['natrium']['mostima']['request']['verifyId-length'])
    salt = bcrypt.gensalt()

    requests_bucket: AioCacheBucket = MostimaBuckets.requests
    
    try:
        emailer.send_mail(register_info.email, {
            'subject': Ts_("mostima.mail_content.subject"),
            "content_text": Ts_("mostima.mail_content.content_text")\
                .format(verify_url=urlunparse(
                    ParseResult(
                        scheme=request.url.scheme,
                        netloc=request.url.netloc,
                        path="/natrium/mostima/register/request/verify",
                        params="",
                        query=urlencode({
                            "verifyId": verifyId
                        }),
                        fragment=""
                    )
                ))
        })
        requests_bucket.setByTimedelta(verifyId, {
            "email": register_info.email,
            "name": register_info.accountName,
            "password": bcrypt.hashpw(register_info.password.encode(), salt),
            "salt": salt,
            "redirectTo": register_info.redirectTo
        })
    except Exception as e:
        print(e)
        return selected_jsonencoder(
            MostimaRequest_Response(operator="failed").dict(), 
            status_code=500
        )
    return MostimaRequest_Response(operator="success")

@router.get(
    "/mostima/register/request/verify",
    dependencies=[
        depends.AutoIPLimits(MostimaBuckets.requestLimit),
    ],
    tags=["Mostima"],
    summary=Ts_("apidoc.natrium.mostima_register.request.verify.summary"),
    description=Ts_("apidoc.natrium.mostima_register.request.verify.description")
)
async def mostima_register_request_verify(verifyId: str, request: Request):
    verify_result = requests_bucket.get(verifyId)
    if not verify_result:
        raise exceptions.BrokenData({
            "position": "query_params.verifyId"
        })
    result = Account(
        Email=verify_result['email'],
        AccountName=verify_result['name'],
        Password=verify_result['password'],
        Salt=verify_result['salt']
    )
    orm.commit()
    if verify_result['redirectTo']:
        redirect: ParseResult = urlparse(verify_result['redirectTo'])
        redirect.query = urlencode({
            "accountId": result.Id
        })
        return RedirectResponse(urlunparse(redirect), status_code=302)
    return {
        "id": result.Id
    }