"""API Endpoints for Finish Good Label Generation"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.finish_good_label import (
    FinishGoodLabelPrintRequest,
    FinishGoodLabelResponse,
    FinishGoodLabel
)
from app.services.finish_good_label_service import FinishGoodLabelService

router = APIRouter(prefix="/api/finish-good-labels", tags=["Finish Good Labels"])


@router.post("/generate", response_model=FinishGoodLabelResponse)
async def generate_finish_good_labels(
    request: FinishGoodLabelPrintRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate Finish Good Labels dengan complete traceability
    
    **IKEA Compliance**: Label berisi informasi lengkap untuk traceability:
    - PO Number & Details
    - MO Number dengan Week
    - Semua SPK/WO yang involved (CUTTING → SEWING → FINISHING → PACKING)
    - Production dates & operators
    - Destination country
    
    **Request Example**:
    ```json
    {
        "mo_id": 123,
        "carton_numbers": ["CTN001", "CTN002", "CTN003"],
        "qty_per_carton": [60, 60, 45]
    }
    ```
    
    **Response**:
    - List of labels (satu per carton)
    - QR codes untuk scanning
    - Complete traceability chain: PO → MO → WO
    
    **Use Cases**:
    1. Packing dept generate labels saat selesai packing
    2. Quality control scan untuk verify traceability
    3. Warehouse verify FG receiving
    4. Customer service trace product history
    """
    
    service = FinishGoodLabelService(db)
    result = await service.generate_fg_labels(request)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return result


@router.get("/barcode/{barcode}", response_model=FinishGoodLabel)
async def get_label_by_barcode(
    barcode: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve label information by scanning FG barcode
    
    **Barcode Format**: `FG-YYYY-MOID-CTNXXX`
    - FG: Prefix untuk Finish Good
    - YYYY: Year
    - MOID: Manufacturing Order ID (5 digits)
    - CTNXXX: Carton number
    
    **Example**: `FG-2026-00123-CTN001`
    
    **Use Cases**:
    1. Warehouse scan FG untuk verify receiving
    2. QC scan untuk inspection traceability
    3. Shipping dept scan untuk verify correct carton
    4. Customer service trace product origin
    """
    
    service = FinishGoodLabelService(db)
    label = await service.get_label_by_barcode(barcode)
    
    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Label not found for barcode: {barcode}"
        )
    
    return label


@router.post("/print/{mo_id}", response_model=dict)
async def print_label_to_thermal_printer(
    mo_id: int,
    carton_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Print label ke thermal printer (80mm width)
    
    **Output Format**: Plain text formatted untuk printer thermal
    
    **Include**:
    - Product information
    - Carton details
    - Complete traceability chain
    - All work orders dengan status
    
    **Use Case**: Direct print dari packing station
    """
    
    service = FinishGoodLabelService(db)
    
    # Generate label
    request = FinishGoodLabelPrintRequest(
        mo_id=mo_id,
        carton_numbers=[carton_number],
        qty_per_carton=[0]  # Will be filled from actual data
    )
    
    result = await service.generate_fg_labels(request)
    
    if not result.success or not result.labels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    # Format untuk printer
    label = result.labels[0]
    print_text = service.format_label_for_print(label)
    
    return {
        "success": True,
        "message": "Label ready for printing",
        "print_text": print_text,
        "label": label
    }


@router.get("/mo/{mo_id}/preview", response_model=dict)
async def preview_label_structure(
    mo_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Preview label structure untuk MO tertentu (tanpa print)
    
    **Use Case**: 
    - PPIC preview traceability structure sebelum production complete
    - QC verify data completeness
    - Management review production flow
    """
    
    service = FinishGoodLabelService(db)
    
    # Generate preview (1 carton dummy)
    request = FinishGoodLabelPrintRequest(
        mo_id=mo_id,
        carton_numbers=["PREVIEW"],
        qty_per_carton=[1]
    )
    
    result = await service.generate_fg_labels(request)
    
    if not result.success or not result.labels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    label = result.labels[0]
    
    return {
        "success": True,
        "message": "Preview generated",
        "label": label,
        "print_preview": service.format_label_for_print(label),
        "mobile_format": service.format_label_for_mobile(label)
    }


@router.get("/traceability/{fg_barcode}", response_model=dict)
async def get_complete_traceability(
    fg_barcode: str,
    db: AsyncSession = Depends(get_db)
):
    """Get complete traceability chain dari FG barcode
    
    **Returns**:
    - PO information (number, week, destination)
    - MO information (number, week, dates, routing)
    - All WO information (department, dates, operators)
    - Material consumption per stage
    - Quality metrics per department
    
    **Use Case**:
    - Customer complaint investigation
    - Quality issue root cause analysis
    - Production performance analysis
    - IKEA audit compliance
    """
    
    service = FinishGoodLabelService(db)
    label = await service.get_label_by_barcode(fg_barcode)
    
    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traceability not found for barcode: {fg_barcode}"
        )
    
    # Build hierarchical structure
    traceability = {
        "fg_barcode": fg_barcode,
        "product": label.product.dict(),
        "chain": []
    }
    
    for po in label.purchase_orders:
        po_chain = {
            "po_number": po.po_number,
            "po_type": po.po_type,
            "qty_ordered": str(po.qty_ordered),
            "week": po.week,
            "destination": po.destination,
            "manufacturing_orders": []
        }
        
        for mo in po.manufacturing_orders:
            mo_chain = {
                "mo_number": mo.mo_number,
                "production_week": mo.production_week,
                "qty_planned": str(mo.qty_planned),
                "qty_produced": str(mo.qty_produced),
                "label_date": str(mo.label_production_date),
                "traceability_code": mo.traceability_code,
                "routing": mo.routing_type,
                "dates": {
                    "planned": str(mo.planned_production_date) if mo.planned_production_date else None,
                    "actual_start": str(mo.actual_production_start_date) if mo.actual_production_start_date else None,
                    "actual_end": str(mo.actual_production_end_date) if mo.actual_production_end_date else None
                },
                "work_orders": []
            }
            
            for wo in mo.work_orders:
                wo_chain = {
                    "wo_number": wo.wo_number,
                    "department": wo.department,
                    "sequence": wo.sequence,
                    "target_qty": str(wo.target_qty),
                    "dates": {
                        "start": str(wo.actual_start_date) if wo.actual_start_date else None,
                        "completion": str(wo.actual_completion_date) if wo.actual_completion_date else None,
                        "stamp": str(wo.production_date_stamp) if wo.production_date_stamp else None
                    },
                    "status": "COMPLETED" if wo.actual_completion_date else "IN_PROGRESS"
                }
                mo_chain["work_orders"].append(wo_chain)
            
            po_chain["manufacturing_orders"].append(mo_chain)
        
        traceability["chain"].append(po_chain)
    
    return {
        "success": True,
        "traceability": traceability
    }
