from enum import Enum

from pydantic import BaseModel


class IndexType(str, Enum):
    R085 = "r085"
    R025 = "r025"
    R085_V3 = "r085_v3"


class IndexRequest(BaseModel):
    index_type: IndexType
