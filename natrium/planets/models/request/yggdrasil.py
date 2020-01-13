from pydantic import BaseModel, Field
from pydantic import EmailStr, AnyHttpUrl
import typing
import uuid
from datetime import datetime
from natrium.util import enums
from enum import Enum
import base64

class EncodeConfig:
    json_encoders = {
        datetime: lambda v: int(v.timestamp()),
        uuid.UUID: lambda v: v.hex,
        "Texture": lambda v: base64.b64encode(v.json().encode("utf-8")).decode("utf-8")
    }

class ConfiedModel(BaseModel):
    class Config(EncodeConfig):
        pass

class GameAgent(BaseModel):
    name: str
    version: int

class CharacterPropertyItem(BaseModel):
    name: str
    value: str

class CharacterPropertyItemWithSignature(CharacterPropertyItem):
    signature: str

class Character(ConfiedModel):
    id: uuid.UUID
    name: str

class CharacterWithProperties(Character):
    properties: typing.List[
        typing.Union[
            CharacterPropertyItem,
            CharacterPropertyItemWithSignature
        ]
    ]

class TextureMetadataKeys(Enum):
    model = "model"

class TextureInfo(BaseModel):
    url: AnyHttpUrl
    metadata: typing.Dict[TextureMetadataKeys, enums.MCTextureModel]

class Texture(ConfiedModel):
    timestamp: datetime
    profileId: uuid.UUID
    profileName: str
    textures: typing.Dict[
        enums.MCTextureModel, TextureInfo
    ]

    class Config(EncodeConfig):
        pass

class Auth(ConfiedModel):
    accessToken: uuid.UUID
    clientToken: typing.Optional[str]

class AccountLogin(BaseModel):
    username: EmailStr
    password: str

class Authserver_Authenticate(AccountLogin):
    clientToken: typing.Optional[str] = ""
    requestUser: typing.Optional[bool] = False
    agent: typing.Optional[GameAgent] = None

class Authserver_Refresh(ConfiedModel):
    accessToken: uuid.UUID
    clientToken: typing.Optional[str] = ""
    requestUser: typing.Optional[bool] = False
    selectedProfile: typing.Optional[Character]

class Authserver_Validate(Auth):
    pass

class Authserver_Invalidate(Auth):
    pass

class Authserver_Signout(AccountLogin):
    pass

class Sessionserver_ServerJoin(BaseModel):
    accessToken: uuid.UUID
    selectedProfile: uuid.UUID
    serverId: str

class MultiCharacters(ConfiedModel):
    __root__: typing.List[
        typing.Union[
            Character,
            CharacterWithProperties
        ]
    ]