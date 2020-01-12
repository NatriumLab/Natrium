from .base import OriginException

class InvalidRequestData(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Invalid request data."
    code = 403

class WrongBind(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Attempting to bind a token to a role that does not belong to its corresponding user."
    code = 403

class InvalidToken(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Invalid token."
    code = 403

class InvalidCredentials(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Invalid credentials. Invalid username or password."
    code = 403

class IllegalArgumentException(OriginException):
    NoAnyMoreConfiure = True
    error = "IllegalArgumentException"
    message = "Access token already has a profile assigned."
    code = 400
    
class DuplicateData(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Duplicate data."
    code = 403