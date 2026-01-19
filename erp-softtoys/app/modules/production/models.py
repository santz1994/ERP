from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from app.core.database import Base
import enum
from datetime import datetime

class RoutingType(str, enum.Enum):
    ROUTE1 = "Route 1 (Full)"
    ROUTE2 = "Route 2 (Direct)"
    ROUTE3 = "Route 3 (Subcon)"

class ManufacturingOrder(Base):
    __tablename__ = "manufacturing_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, index=True) # Referensi PO IKEA
    article_code = Column(String)
    qty_planned = Column(Integer)
    routing_type = Column(Enum(RoutingType))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Nanti disini bisa tambah relasi ke WorkOrders, MaterialRequirements, dll. sesuai kebutuhan