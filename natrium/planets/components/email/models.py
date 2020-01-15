from pydantic import BaseModel
from pydantic import EmailStr

class Email(BaseModel):
    __root__: EmailStr