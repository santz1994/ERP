"""Finish Good Label Schema - IKEA Traceability"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class SPKWOInfo(BaseModel):
    """SPK/Work Order Information"""
    wo_number: str = Field(..., description="Work Order number")
    department: str = Field(..., description="Department name (CUTTING, SEWING, etc)")
    sequence: int = Field(..., description="Sequence in production flow")
    target_qty: Decimal = Field(..., description="Target quantity")
    actual_start_date: Optional[date] = Field(None, description="Actual start date")
    actual_completion_date: Optional[date] = Field(None, description="Actual completion date")
    production_date_stamp: Optional[date] = Field(None, description="Production date stamp")
    operator: Optional[str] = Field(None, description="Operator/Admin name")


class MOInfo(BaseModel):
    """Manufacturing Order Information"""
    mo_number: str = Field(..., description="MO batch number")
    production_week: str = Field(..., description="Production week (e.g., 10-2026)")
    qty_planned: Decimal = Field(..., description="Planned quantity")
    qty_produced: Decimal = Field(..., description="Actual produced quantity")
    planned_production_date: Optional[date] = Field(None, description="Planned production date")
    actual_production_start_date: Optional[date] = Field(None, description="Actual start date")
    actual_production_end_date: Optional[date] = Field(None, description="Actual completion date")
    label_production_date: Optional[date] = Field(None, description="Date on physical label")
    destination_country: Optional[str] = Field(None, description="Destination country")
    traceability_code: str = Field(..., description="IKEA traceability code")
    routing_type: str = Field(..., description="Production routing (Route 1/2/3)")
    
    # Child SPK/WO list
    work_orders: List[SPKWOInfo] = Field(default_factory=list, description="All SPK/WO in sequence")


class POInfo(BaseModel):
    """Purchase Order Information"""
    po_number: str = Field(..., description="PO number")
    po_type: str = Field(..., description="PO Type (KAIN, LABEL, ACCESSORIES)")
    qty_ordered: Decimal = Field(..., description="Ordered quantity")
    week: Optional[str] = Field(None, description="PO week target")
    destination: Optional[str] = Field(None, description="PO destination")
    
    # Child MO list
    manufacturing_orders: List[MOInfo] = Field(default_factory=list, description="All MOs from this PO")


class ProductInfo(BaseModel):
    """Product Information"""
    product_code: str = Field(..., description="Product code (e.g., 302.213.49)")
    product_name: str = Field(..., description="Product name")
    product_category: str = Field(..., description="Category (FINISH GOOD)")
    description: Optional[str] = Field(None, description="Product description")


class FinishGoodLabel(BaseModel):
    """Complete Finish Good Label for IKEA Traceability
    
    Structure:
    FG → PO → MO (Week) → SPK/WO (all departments)
    """
    
    # FG Information
    fg_barcode: str = Field(..., description="FG Barcode (e.g., FG-2026-00001-CTN001)")
    carton_number: str = Field(..., description="Carton number (e.g., CTN001)")
    qty_in_carton: int = Field(..., description="Quantity in this carton")
    packing_date: date = Field(..., description="Date when packed")
    
    # Product
    product: ProductInfo = Field(..., description="Product information")
    
    # Traceability Chain
    purchase_orders: List[POInfo] = Field(default_factory=list, description="All POs involved")
    
    # Summary
    total_qty: Decimal = Field(..., description="Total quantity in all cartons")
    total_cartons: int = Field(..., description="Total number of cartons")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fg_barcode": "FG-2026-00001-CTN001",
                "carton_number": "CTN001",
                "qty_in_carton": 60,
                "packing_date": "2026-03-10",
                "product": {
                    "product_code": "302.213.49",
                    "product_name": "AFTONSPARV",
                    "product_category": "FINISH GOOD",
                    "description": "Soft toy, astronaut, white"
                },
                "purchase_orders": [
                    {
                        "po_number": "PO-2026-001",
                        "po_type": "KAIN",
                        "qty_ordered": 500,
                        "week": "10-2026",
                        "destination": "Belgium",
                        "manufacturing_orders": [
                            {
                                "mo_number": "MO-20260301-001",
                                "production_week": "10-2026",
                                "qty_planned": 450,
                                "qty_produced": 465,
                                "label_production_date": "2026-03-05",
                                "destination_country": "Belgium",
                                "traceability_code": "MO-W10-001-BE",
                                "routing_type": "Route 1",
                                "work_orders": [
                                    {
                                        "wo_number": "WO-CUT-001",
                                        "department": "CUTTING",
                                        "sequence": 1,
                                        "target_qty": 495,
                                        "actual_start_date": "2026-03-01",
                                        "actual_completion_date": "2026-03-02",
                                        "production_date_stamp": "2026-03-01"
                                    },
                                    {
                                        "wo_number": "WO-EMBO-001",
                                        "department": "EMBROIDERY",
                                        "sequence": 2,
                                        "target_qty": 495,
                                        "actual_start_date": "2026-03-02",
                                        "actual_completion_date": "2026-03-03"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "total_qty": 465,
                "total_cartons": 8
            }
        }


class FinishGoodLabelPrintRequest(BaseModel):
    """Request to print FG label"""
    mo_id: int = Field(..., description="Manufacturing Order ID")
    carton_numbers: List[str] = Field(..., description="Carton numbers to print (e.g., ['CTN001', 'CTN002'])")
    qty_per_carton: List[int] = Field(..., description="Quantity in each carton (same length as carton_numbers)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mo_id": 123,
                "carton_numbers": ["CTN001", "CTN002", "CTN003"],
                "qty_per_carton": [60, 60, 45]
            }
        }


class FinishGoodLabelResponse(BaseModel):
    """Response after generating FG labels"""
    success: bool
    message: str
    labels: List[FinishGoodLabel] = Field(default_factory=list)
    qr_codes: List[str] = Field(default_factory=list, description="Base64 encoded QR codes")
