from fastapi.exceptions import RequestValidationError
from pydantic.error_wrappers import ValidationError
from natrium.json_interface import selected_jsonencoder as Response
from natrium import app
import json

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

class BaseException(Exception):
    NoAnyMoreConfiure = False
    metadata = None

    def __init__(self, metadata=None, error=None, errorMessage=None, code=None, message="SomethingWrong"):
        if not self.NoAnyMoreConfiure:
            self.error = error
            self.message = errorMessage,
            self.code = code
        if metadata:
            self.metadata = metadata
        super().__init__(message)

    def json(self):
        return {
            "error": self.error,
            "errorMessage": self.message
        } if not self.metadata else {
            "error": self.error,
            "errorMessage": self.message,
            "metadata": self.metadata
        }

    def response(self):
        return Response(self.json(), status_code=self.code)

@app.exception_handler(BaseException)
async def CustomExceptionHandler(request, exc: BaseException):
    return exc.response()

class AuthenticateVerifyException(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Invalid token."
    code = 403

class InvalidCredentials(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Invalid credentials. Invalid username or password."
    code = 403

class FrequencyLimit(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Frequency limit is triggered, please try again later."
    code = 403

class NoSuchResourceException(BaseException):
    NoAnyMoreConfiure = True
    error = "NoSuchResourceException"
    message = "The server does not have the resource you requested. Please confirm that the request is correct."
    code = 404

class PermissionDenied(AuthenticateVerifyException):
    NoAnyMoreConfiure = True
    error = "PermissionDenied"

class NonCompliantMsg(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "You submitted a field that failed verification."
    code = 403

class OccupyExistedAddress(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Please do not try to occupy an existing address."
    code = 403

class SizeLimit(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "The uploaded image file content size exceeds the limit."
    code = 403

class UnrecognizedContent(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "The server does not accept an unrecognized request body."
    code = 403

class DuplicateRegulations(BaseException):
    """当出现冲突事务时将抛出该error"""
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Your request triggered a duplicate regulation restriction."
    code = 403

class BrokenData(BaseException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Broken data appears in the server database, \
    please contact the site administrator immediately."
    code = 403