import uuid
from typing import Optional

from pydantic import BaseModel

from natrium.util import enums


class AuthenticateInfo(BaseModel):
    accessToken: str
    clientToken: Optional[str] = None

class OptionalAInfo(BaseModel):
    auth: Optional[AuthenticateInfo] = None

class AInfo(BaseModel):
    auth: AuthenticateInfo

class OptionalClientToken(BaseModel):
    clientToken: Optional[str] = None

class AccountAuth(BaseModel):
    email: str
    password: str

class AuthenticateRequest(AccountAuth):
    requestAccount: bool = False
    authenticate: Optional[OptionalClientToken] = OptionalClientToken()

class AuthenticateResponse(AuthenticateInfo):
    accountId: uuid.UUID
    auth: AuthenticateInfo

class JustName(BaseModel):
    name: str

class CharacterCreateInfo(JustName):
    name: str
    public: Optional[bool] = False

class CharacterCreate(BaseModel):
    create: CharacterCreateInfo

class Update(BaseModel):
    update: JustName

class ResourceUpdateOptions(BaseModel):
    name: Optional[str] = None
    type: Optional[enums.MCTextureType] = None
    model: Optional[enums.MCTextureModel] = None

class ResourceUpdate(BaseModel):
    update: ResourceUpdateOptions
