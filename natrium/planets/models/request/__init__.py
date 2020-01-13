from pydantic import BaseModel, Field
import uuid
from datetime import datetime
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