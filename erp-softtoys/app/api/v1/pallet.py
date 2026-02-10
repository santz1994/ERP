"""Pallet System API Endpoints
RESTful API for pallet-based packing and validation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.models.users import User
from app.services.pallet_service import PalletService
from app.schemas.pallet import (
    PalletSpecsResponse,
    POPalletCalculationRequest,
    POPalletCalculationResponse,
    POPalletValidationRequest,
    POPalletValidationResponse,
    PackingPalletUpdateRequest,
    PackingPalletUpdateResponse,
    FGPalletReceiveRequest,
    FGPalletReceiveResponse,
    PalletBarcodeCreate,
    PalletBarcodeResponse,
)

router = APIRouter(prefix="/api/v1/pallet", tags=["Pallet System"])


# ============================================================================
# PALLET SPECIFICATIONS
# ============================================================================

@router.get("/specs/{product_id}", response_model=PalletSpecsResponse)
def get_pallet_specifications(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pallet specifications for a product (Finish Good).
    
    **Business Use Case**: Display packing specs on PO creation form
    
    **Example**:
    ```
    GET /api/v1/pallet/specs/1
    
    Response:
    {
        "product_id": 1,
        "product_code": "AFTONSPARV",
        "product_name": "AFTONSPARV Bear 30cm",
        "pcs_per_carton": 60,
        "cartons_per_pallet": 8,
        "pcs_per_pallet": 480
    }
    ```
    
    **Access**: All authenticated users
    """
    service = PalletService(db)
    return service.get_pallet_specs(product_id)


# ============================================================================
# PO PALLET CALCULATION
# ============================================================================

@router.post("/calculate-po", response_model=POPalletCalculationResponse)
def calculate_po_pallet_quantities(
    request: POPalletCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate PO quantities based on pallet target.
    
    **Business Use Case**: Purchasing staff enters # of pallets → system calculates PCS quantity
    
    **Example**:
    ```
    POST /api/v1/pallet/calculate-po
    {
        "article_id": 1,
        "target_pallets": 5
    }
    
    Response:
    {
        "article_id": 1,
        "article_code": "AFTONSPARV",
        "target_pallets": 5,
        "expected_cartons": 40,
        "calculated_pcs": 2400,
        "pallet_specs": {...}
    }
    ```
    
    **Access**: Purchasing staff, PPIC, Managers
    """
    service = PalletService(db)
    return service.calculate_po_pallet_quantities(request)


@router.post("/validate-po", response_model=POPalletValidationResponse)
def validate_po_pallet_quantity(
    request: POPalletValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate if PO quantity is a pallet multiple.
    
    **Business Use Case**: Warn Purchasing if entered quantity is not pallet multiple
    
    **Example (Valid)**:
    ```
    POST /api/v1/pallet/validate-po
    {
        "article_id": 1,
        "quantity_pcs": 2400
    }
    
    Response:
    {
        "is_valid": true,
        "is_pallet_multiple": true,
        "quantity_pcs": 2400,
        "pallets": 5,
        "cartons": 40,
        "remainder_pcs": 0,
        "message": "✅ Valid pallet multiple",
        "recommendation": null
    }
    ```
    
    **Example (Invalid)**:
    ```
    POST /api/v1/pallet/validate-po
    {
        "article_id": 1,
        "quantity_pcs": 2500
    }
    
    Response:
    {
        "is_valid": false,
        "is_pallet_multiple": false,
        "quantity_pcs": 2500,
        "pallets": 5,
        "cartons": 41,
        "remainder_pcs": 100,
        "message": "⚠️ Not a complete pallet multiple",
        "recommendation": "Adjust to 2400 pcs (5 pallets) or 2880 pcs (6 pallets)"
    }
    ```
    
    **Access**: Purchasing staff, PPIC, Managers
    """
    service = PalletService(db)
    return service.validate_po_pallet_quantity(request)


# ============================================================================
# PACKING PALLET TRACKING
# ============================================================================

@router.post("/packing/update", response_model=PackingPalletUpdateResponse)
def update_packing_pallet_progress(
    request: PackingPalletUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update packing progress with pallet formation tracking.
    
    **Business Use Case**: Packing Admin inputs cartons packed → system validates complete pallets
    
    **Example (Valid)**:
    ```
    POST /api/v1/pallet/packing/update
    {
        "work_order_id": 123,
        "cartons_packed": 40,
        "validate_complete_pallets": true
    }
    
    Response:
    {
        "work_order_id": 123,
        "cartons_packed": 40,
        "pallets_formed": 5,
        "packing_validated": true,
        "message": "✅ Packed 40 cartons → 5 complete pallets"
    }
    ```
    
    **Example (Invalid - Partial Pallet)**:
    ```
    POST /api/v1/pallet/packing/update
    {
        "work_order_id": 123,
        "cartons_packed": 41,
        "validate_complete_pallets": true
    }
    
    Response (HTTP 400):
    {
        "error": "Partial pallet detected: 41 cartons = 5 pallets + 1 carton loose"
    }
    ```
    
    **Access**: Packing Admin, Supervisors, Managers
    """
    service = PalletService(db)
    return service.update_packing_pallet_progress(request)


# ============================================================================
# PALLET BARCODE MANAGEMENT
# ============================================================================

@router.post("/barcode/create", response_model=PalletBarcodeResponse)
def create_pallet_barcode(
    request: PalletBarcodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new pallet barcode after packing.
    
    **Business Use Case**: Packing dept forms pallet → generates barcode for FG tracking
    
    **Example**:
    ```
    POST /api/v1/pallet/barcode/create
    {
        "product_id": 1,
        "work_order_id": 123,
        "carton_count": 8,
        "total_pcs": 480
    }
    
    Response:
    {
        "id": 1,
        "barcode": "PLT-2026-00001",
        "product_id": 1,
        "product_code": "AFTONSPARV",
        "carton_count": 8,
        "total_pcs": 480,
        "status": "PACKED",
        "created_at": "2026-02-10T10:00:00+07:00"
    }
    ```
    
    **Access**: Packing Admin, FG Warehouse Admin
    """
    service = PalletService(db)
    return service.create_pallet_barcode(request)


@router.post("/fg-receive", response_model=FGPalletReceiveResponse)
def receive_pallet_in_fg_warehouse(
    request: FGPalletReceiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Receive pallet in FG warehouse by scanning barcode.
    
    **Business Use Case**: FG warehouse scans pallet barcode → updates status to RECEIVED
    
    **Example**:
    ```
    POST /api/v1/pallet/fg-receive
    {
        "pallet_barcode": "PLT-2026-00001",
        "location_id": 5,
        "received_by_user_id": 10
    }
    
    Response:
    {
        "pallet_barcode": "PLT-2026-00001",
        "status": "RECEIVED",
        "product_code": "AFTONSPARV",
        "product_name": "AFTONSPARV Bear 30cm",
        "carton_count": 8,
        "total_pcs": 480,
        "location_name": "FG Warehouse Zone A",
        "received_at": "2026-02-10T14:30:00+07:00",
        "message": "✅ Received 1 pallet (8 cartons / 480 pcs)"
    }
    ```
    
    **Access**: FG Warehouse Admin, Warehouse Manager
    """
    service = PalletService(db)
    return service.receive_pallet_in_fg_warehouse(request)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
def pallet_system_health_check():
    """Health check for pallet system API.
    
    Returns:
    {
        "status": "healthy",
        "service": "Pallet System API",
        "version": "1.0",
        "timestamp": "2026-02-10T15:00:00+07:00"
    }
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "Pallet System API",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    }
