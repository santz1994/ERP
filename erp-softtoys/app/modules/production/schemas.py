
from pydantic import BaseModel

from .models import RoutingType


class MOCreate(BaseModel):
    po_number: str
    article_code: str
    qty_planned: int
    routing_type: RoutingType

class MOResponse(MOCreate):
    id: int

    class Config:
        from_attributes = True
