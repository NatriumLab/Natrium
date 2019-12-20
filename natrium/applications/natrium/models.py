from pydantic import BaseModel
from typing import Optional
import uuid

class AuthenticateInfo(BaseModel):
    accessToken: str
    clientToken: Optional[str] = None

class AInfo(BaseModel):
    auth: AuthenticateInfo

class OptionalClientToken(BaseModel):
    clientToken: Optional[str] = None

class AuthenticateRequest(BaseModel):
    email: str
    password: str
    requestAccount: bool = False
    authenticate: Optional[OptionalClientToken] = OptionalClientToken()

class AuthenticateResponse(AuthenticateInfo):
    accountId: uuid.UUID
    auth: AuthenticateInfo