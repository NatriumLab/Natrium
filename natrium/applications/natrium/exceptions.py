from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse as Response
from natrium import app
import json

@app.exception_handler(RequestValidationError)
async def RequestValidateExceptionHandler(request, exc: RequestValidationError):
    before = json.loads(exc.json())
    return Response({
        "error": "RequestValidationException",
        "detail": before['detail']
    }, status_code=403)

@app.exception_handler(json.decoder.JSONDecodeError)
async def JSONDecodeExceptionHandler(request, exc):
    return Response({
        "error": "ForbiddenOperationException",
        "errorMessage": "Duplicate data."
    }, status_code=403)

class BaseException(Exception):
    NoAnyMoreConfiure = False
    def __init__(self, error=None, errorMessage=None, code=None, message="SomethingWrong"):
        if not self.NoAnyMoreConfiure:
            self.error = error
            self.message = errorMessage,
            self.code = code
        super().__init__(message)

    def json(self):
        return {
            "error": self.error,
            "errorMessage": self.message
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