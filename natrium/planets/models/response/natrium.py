from pydantic import BaseModel
from natrium.util.enums import OperatorStatus
from typing import Any

class MostimaRequest_Response(BaseModel):
    operator: OperatorStatus
    metadata: Any