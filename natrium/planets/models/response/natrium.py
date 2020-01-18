from pydantic import BaseModel
from natrium.util.enums import OperatorStatus
from typing import Any, Optional

class MostimaRequest_Response(BaseModel):
    operator: OperatorStatus
    metadata: Optional[Any]