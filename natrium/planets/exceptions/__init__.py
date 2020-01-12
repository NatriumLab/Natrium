from fastapi.exceptions import RequestValidationError
from pydantic.error_wrappers import ValidationError
from natrium.json_interface import selected_jsonencoder as Response
from natrium import app
import json
from .base import OriginException

@app.exception_handler(ValidationError)
@app.exception_handler(RequestValidationError)
async def RequestValidateExceptionHandler(
        request, 
        exc: RequestValidationError or ValidationError
    ):
    before = json.loads(exc.json())
    return Response({
        "error": exc.__class__.__name__,
        "detail": before
    }, status_code=403)

@app.exception_handler(json.decoder.JSONDecodeError)
async def JSONDecodeExceptionHandler(request, exc):
    return Response({
        "error": "ForbiddenOperationException",
        "errorMessage": "Duplicate data."
    }, status_code=403)

@app.exception_handler(OriginException)
async def CustomExceptionHandler(request, exc: OriginException):
    return exc.response()