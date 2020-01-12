from .base import OriginException

class AuthenticateVerifyException(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Invalid token."
    code = 403

class InvalidCredentials(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Invalid credentials. Invalid username or password."
    code = 403

class FrequencyLimit(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Frequency limit is triggered, please try again later."
    code = 403

class NoSuchResourceException(OriginException):
    NoAnyMoreConfiure = True
    error = "NoSuchResourceException"
    message = "The server does not have the resource you requested. Please confirm that the request is correct."
    code = 404

class PermissionDenied(AuthenticateVerifyException):
    NoAnyMoreConfiure = True
    error = "PermissionDenied"

class NonCompliantMsg(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "You submitted a field that failed verification."
    code = 403

class OccupyExistedAddress(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Please do not try to occupy an existing address."
    code = 403

class SizeLimit(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "The uploaded image file content size exceeds the limit."
    code = 403

class UnrecognizedContent(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "The server does not accept an unrecognized request body."
    code = 403

class DuplicateRegulations(OriginException):
    """当出现冲突事务时将抛出该error"""
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Your request triggered a duplicate regulation restriction."
    code = 403

class BrokenData(OriginException):
    NoAnyMoreConfiure = True
    error = "ForbiddenOperationException"
    message = "Broken data appears in the server database, \
    please contact the site administrator immediately."
    code = 403