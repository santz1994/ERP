"""Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved.

Purchasing API Endpoints
Handles purchase orders, supplier management, material receiving

🆕 UPDATE (Feb 6, 2026): Added PO Reference System
- PO Type (KAIN/LABEL/ACCESSORIES)
- Parent-child relationship (PO LABEL → PO KAIN)
- Auto-inheritance (Article, Week, Destination)
- Business rule validation (PO LABEL must reference PO KAIN)
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.models.users import User
from app.core.models.warehouse import PurchaseOrder, POType, POStatus
from app.core.models.products import Product, Partner, PartnerType
from app.core.dependencies import require_permission
from app.core.permissions import ModuleName, Permission
from app.modules.purchasing import PurchasingService

router = APIRouter(prefix="/purchasing", tags=["Purchasing"])


# Pydantic Schemas
class POItemRequest(BaseModel):
    product_id: int = Field(..., description="Raw material product ID")
    quantity: int = Field(..., gt=0, description="Order quantity")
    unit_price: float = Field(..., gt=0, description="Unit price in IDR")


class CreatePORequest(BaseModel):
    po_number: str = Field(..., description="PO number")
    supplier_id: int = Field(..., description="Supplier ID")
    order_date: date = Field(..., description="Order date")
    expected_date: date = Field(..., description="Expected delivery date")
    items: list[POItemRequest] = Field(..., description="PO items")
    
    # 🆕 PO REFERENCE SYSTEM FIELDS (Added: Feb 6, 2026)
    po_type: POType = Field(POType.ACCESSORIES, description="PO Type: KAIN (Fabric-TRIGGER 1), LABEL (TRIGGER 2), ACCESSORIES")
    source_po_kain_id: Optional[int] = Field(None, description="Reference to parent PO KAIN (required for PO LABEL)")
    article_id: Optional[int] = Field(None, description="Article/Product reference (required for PO KAIN/LABEL)")
    article_qty: Optional[int] = Field(None, gt=0, description="Article quantity (pcs)")
    week: Optional[str] = Field(None, description="Production week (e.g., W5, W12) - required for PO LABEL")
    destination: Optional[str] = Field(None, description="Delivery destination - required for PO LABEL")
    linked_mo_id: Optional[int] = Field(None, description="Linked Manufacturing Order (MO)")
    
    @validator('source_po_kain_id')
    def validate_reference(cls, v: Optional[int], values) -> Optional[int]:
        """Validate PO reference based on PO type.
        
        Business Rules:
        1. PO LABEL MUST have source_po_kain_id
        2. PO KAIN cannot have source_po_kain_id (no self-reference)
        3. PO ACCESSORIES can optionally have source_po_kain_id
        """
        po_type = values.get('po_type')
        
        # Rule 1: PO LABEL must reference PO KAIN
        if po_type == POType.LABEL and not v:
            raise ValueError("PO LABEL must reference a PO KAIN (source_po_kain_id required)")
        
        # Rule 2: PO KAIN cannot have reference
        if po_type == POType.KAIN and v:
            raise ValueError("PO KAIN cannot reference another PO (must be master PO)")
        
        return v
    
    @validator('week')
    def validate_week(cls, v: Optional[str], values) -> Optional[str]:
        """Validate week for PO LABEL.
        
        Business Rule:
        - PO LABEL MUST have week
        - Week is auto-inherited to MO when PO LABEL received
        """
        po_type = values.get('po_type')
        
        if po_type == POType.LABEL and not v:
            raise ValueError("PO LABEL must have week (required for TRIGGER 2)")
        
        return v
    
    @validator('destination')
    def validate_destination(cls, v: Optional[str], values) -> Optional[str]:
        """Validate destination for PO LABEL.
        
        Business Rule:
        - PO LABEL MUST have destination
        - Destination is auto-inherited to MO when PO LABEL received
        """
        po_type = values.get('po_type')
        
        if po_type == POType.LABEL and not v:
            raise ValueError("PO LABEL must have destination (required for TRIGGER 2)")
        
        return v
    
    @validator('article_id')
    def validate_article(cls, v: Optional[int], values) -> Optional[int]:
        """Validate article_id for PO KAIN/LABEL.
        
        Business Rule:
        - PO KAIN and PO LABEL MUST have article_id
        - PO ACCESSORIES optional (can be generic materials)
        """
        po_type = values.get('po_type')
        
        if po_type in (POType.KAIN, POType.LABEL) and not v:
            raise ValueError(f"PO {po_type.value} must have article_id (required for traceability)")
        
        return v


class ReceiveItemRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Received quantity")
    lot_number: str | None = Field(None, description="Lot/Batch number")


class ReceivePORequest(BaseModel):
    received_items: list[ReceiveItemRequest] = Field(..., description="Received items")
    location_id: int = Field(1, description="Warehouse location ID")


class CancelPORequest(BaseModel):
    reason: str = Field(..., description="Cancellation reason")


class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    order_date: date
    expected_date: date
    status: str
    total_amount: float
    currency: str
    approved_by: int | None
    approved_at: str | None
    received_by: int | None
    received_at: str | None
    metadata: dict | None

    class Config:
        from_attributes = True


class SupplierPerformanceResponse(BaseModel):
    supplier_id: int
    total_purchase_orders: int
    completed_orders: int
    on_time_delivery: int
    on_time_rate: float
    completion_rate: float


# Endpoints
@router.get("/purchase-orders", response_model=list[PurchaseOrderResponse])
def get_purchase_orders(
    status: str | None = None,
    supplier_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get all purchase orders with optional filters.

    - **status**: Filter by status (Draft, Sent, Received, Done, Cancelled)
    - **supplier_id**: Filter by supplier
    """
    service = PurchasingService(db)
    pos = service.get_purchase_orders(status=status, supplier_id=supplier_id)
    return pos


@router.post("/purchase-order", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    request: CreatePORequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.CREATE))
):
    """Create new purchase order with PO Reference System support.
    
    🆕 PO Reference System (Feb 6, 2026):
    - **PO KAIN** (Fabric) - TRIGGER 1: Enables Cutting/Embroidery (MO PARTIAL)
    - **PO LABEL** - TRIGGER 2: Full MO Release + Week/Destination inheritance
    - **PO ACCESSORIES** - Optional reference to PO KAIN for traceability
    
    Validations:
    1. PO LABEL must reference active PO KAIN
    2. PO LABEL must have week & destination
    3. Article auto-inherited from PO KAIN for PO LABEL
    4. Cannot create PO KAIN with self-reference

    - **po_number**: Unique PO number
    - **po_type**: KAIN | LABEL | ACCESSORIES
    - **supplier_id**: Supplier/vendor ID
    - **order_date**: Date when PO is created
    - **expected_date**: Expected delivery date
    - **items**: List of materials to purchase with quantities and prices
    - **source_po_kain_id**: Reference to parent PO KAIN (required for PO LABEL)
    - **article_id**: Article reference (required for PO KAIN/LABEL)
    - **article_qty**: Article quantity in pcs
    - **week**: Production week (required for PO LABEL)
    - **destination**: Delivery destination (required for PO LABEL)
    """
    try:
        # 🆕 VALIDATION 1: Check PO KAIN exists and is active (for PO LABEL)
        if request.source_po_kain_id:
            po_kain = db.query(PurchaseOrder).filter(
                PurchaseOrder.id == request.source_po_kain_id,
                PurchaseOrder.po_type == POType.KAIN,
                PurchaseOrder.status.in_([POStatus.SENT, POStatus.RECEIVED])
            ).first()
            
            if not po_kain:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"PO KAIN with ID {request.source_po_kain_id} not found or not active (status must be SENT or RECEIVED)"
                )
            
            # 🆕 AUTO-INHERIT: Article & Quantity from PO KAIN
            if request.po_type == POType.LABEL:
                request.article_id = po_kain.article_id
                request.article_qty = po_kain.article_qty
                print(f"✅ Auto-inherited from PO KAIN {po_kain.po_number}: article_id={request.article_id}, article_qty={request.article_qty}")
        
        # 🆕 VALIDATION 2: Article exists (for PO KAIN & PO LABEL)
        if request.article_id:
            article = db.query(Product).filter(Product.id == request.article_id).first()
            if not article:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Article with ID {request.article_id} not found"
                )
        
        # Create PO with PO Reference System fields
        service = PurchasingService(db)
        po = service.create_purchase_order(
            po_number=request.po_number,
            supplier_id=request.supplier_id,
            order_date=request.order_date,
            expected_date=request.expected_date,
            items=[item.dict() for item in request.items],
            user_id=current_user.id,
            # 🆕 PO Reference System fields
            po_type=request.po_type,
            source_po_kain_id=request.source_po_kain_id,
            article_id=request.article_id,
            article_qty=request.article_qty,
            week=request.week,
            destination=request.destination,
            linked_mo_id=request.linked_mo_id
        )
        
        print(f"✅ Created PO: {po.po_number} (Type: {po.po_type.value if po.po_type else 'N/A'})")
        return po
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating PO: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/purchase-order/{po_id}/approve", response_model=PurchaseOrderResponse)
def approve_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.APPROVE))
):
    """Approve purchase order (Manager only).

    Changes status from Draft to Sent
    """
    try:
        service = PurchasingService(db)
        po = service.approve_purchase_order(po_id, current_user.id)
        return po
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/purchase-order/{po_id}/receive", response_model=PurchaseOrderResponse)
def receive_purchase_order(
    po_id: int,
    request: ReceivePORequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.EXECUTE))
):
    """Receive materials from purchase order.

    - Creates stock lots for traceability
    - Updates inventory quantities (FIFO)
    - Records stock movements
    - Changes PO status to Received
    """
    try:
        service = PurchasingService(db)
        po = service.receive_purchase_order(
            po_id=po_id,
            received_items=[item.dict() for item in request.received_items],
            user_id=current_user.id,
            location_id=request.location_id
        )
        return po
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/purchase-order/{po_id}/cancel", response_model=PurchaseOrderResponse)
def cancel_purchase_order(
    po_id: int,
    request: CancelPORequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.DELETE))
):
    """Cancel purchase order.

    Can only cancel Draft or Sent POs, not Received/Done
    """
    try:
        service = PurchasingService(db)
        po = service.cancel_purchase_order(po_id, request.reason, current_user.id)
        return po
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/supplier/{supplier_id}/performance", response_model=SupplierPerformanceResponse)
def get_supplier_performance(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get supplier performance metrics.

    - Total purchase orders
    - Completion rate
    - On-time delivery rate
    """
    service = PurchasingService(db)
    performance = service.get_supplier_performance(supplier_id)
    return performance


# 🆕 NEW ENDPOINTS FOR PO REFERENCE SYSTEM (Feb 6, 2026)

@router.get("/purchase-orders/available-kain")
def get_available_po_kain(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get list of active PO KAIN for dropdown reference in PO LABEL creation.
    
    Returns only PO KAIN with status SENT or RECEIVED (active POs that can be referenced).
    Used in CreatePOPage when creating PO LABEL or PO ACCESSORIES.
    
    Response includes:
    - id: PO KAIN ID
    - po_number: PO KAIN number
    - article_id: Article ID
    - article_code: Article code
    - article_name: Article name
    - article_qty: Article quantity
    - order_date: PO order date
    - status: PO status
    - supplier_name: Supplier name
    """
    try:
        po_kain_list = db.query(PurchaseOrder).filter(
            PurchaseOrder.po_type == POType.KAIN,
            PurchaseOrder.status.in_([POStatus.SENT, POStatus.RECEIVED])
        ).options(
            joinedload(PurchaseOrder.article),
            joinedload(PurchaseOrder.supplier)
        ).order_by(PurchaseOrder.order_date.desc()).all()
        
        result = [
            {
                "id": po.id,
                "po_number": po.po_number,
                "article_id": po.article_id,
                "article_code": po.article.code if po.article else None,
                "article_name": po.article.name if po.article else None,
                "article_qty": po.article_qty,
                "order_date": po.order_date.isoformat() if po.order_date else None,
                "status": po.status.value if po.status else None,
                "supplier_name": po.supplier.name if hasattr(po, 'supplier') and po.supplier else None
            }
            for po in po_kain_list
        ]
        
        print(f"✅ Retrieved {len(result)} active PO KAIN")
        return {"data": result, "count": len(result)}
        
    except Exception as e:
        print(f"❌ Error fetching available PO KAIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch available PO KAIN: {str(e)}"
        )


@router.get("/purchase-orders/{po_kain_id}/related")
def get_po_family_tree(
    po_kain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get complete PO family tree for traceability.
    
    Shows complete parent-child relationship:
    - PO KAIN (Master)
    - Related PO LABEL (1:1 relationship)
    - Related PO ACCESSORIES (1:N relationship)
    - Linked Manufacturing Order (if exists)
    - Grand total (sum of all related POs)
    
    Used for:
    - Traceability: Track all materials for 1 article
    - Cost Analysis: Total project cost (KAIN + LABEL + ACC)
    - Production Status: Check if all POs ready for production
    """
    try:
        # Get PO KAIN
        po_kain = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == po_kain_id,
            PurchaseOrder.po_type == POType.KAIN
        ).options(
            joinedload(PurchaseOrder.article),
            joinedload(PurchaseOrder.linked_mo),
            joinedload(PurchaseOrder.supplier)
        ).first()
        
        if not po_kain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PO KAIN with ID {po_kain_id} not found"
            )
        
        # Get related PO LABEL (1:1 relationship)
        related_label = db.query(PurchaseOrder).filter(
            PurchaseOrder.source_po_kain_id == po_kain_id,
            PurchaseOrder.po_type == POType.LABEL
        ).options(
            joinedload(PurchaseOrder.supplier)
        ).all()
        
        # Get related PO ACCESSORIES (1:N relationship)
        related_accessories = db.query(PurchaseOrder).filter(
            PurchaseOrder.source_po_kain_id == po_kain_id,
            PurchaseOrder.po_type == POType.ACCESSORIES
        ).options(
            joinedload(PurchaseOrder.supplier)
        ).all()
        
        # Calculate grand total (sum of all PO amounts)
        # Note: Assuming PO has total_amount field calculated from items
        po_kain_amount = getattr(po_kain, 'total_amount', 0) or 0
        label_amount = sum([getattr(po, 'total_amount', 0) or 0 for po in related_label])
        acc_amount = sum([getattr(po, 'total_amount', 0) or 0 for po in related_accessories])
        grand_total = po_kain_amount + label_amount + acc_amount
        
        # Build response
        result = {
            "po_kain": {
                "id": po_kain.id,
                "po_number": po_kain.po_number,
                "article_code": po_kain.article.code if po_kain.article else None,
                "article_name": po_kain.article.name if po_kain.article else None,
                "article_qty": po_kain.article_qty,
                "order_date": po_kain.order_date.isoformat() if po_kain.order_date else None,
                "status": po_kain.status.value if po_kain.status else None,
                "supplier_name": po_kain.supplier.name if hasattr(po_kain, 'supplier') and po_kain.supplier else None,
                "mo_number": po_kain.linked_mo.mo_number if po_kain.linked_mo else None,
                "mo_status": po_kain.linked_mo.status if po_kain.linked_mo else None,
                "total_amount": po_kain_amount
            },
            "related_po_label": [
                {
                    "id": po.id,
                    "po_number": po.po_number,
                    "week": po.week,
                    "destination": po.destination,
                    "order_date": po.order_date.isoformat() if po.order_date else None,
                    "status": po.status.value if po.status else None,
                    "supplier_name": po.supplier.name if hasattr(po, 'supplier') and po.supplier else None,
                    "total_amount": getattr(po, 'total_amount', 0) or 0
                }
                for po in related_label
            ],
            "related_po_accessories": [
                {
                    "id": po.id,
                    "po_number": po.po_number,
                    "order_date": po.order_date.isoformat() if po.order_date else None,
                    "status": po.status.value if po.status else None,
                    "supplier_name": po.supplier.name if hasattr(po, 'supplier') and po.supplier else None,
                    "items_count": len(getattr(po, 'items', [])),
                    "total_amount": getattr(po, 'total_amount', 0) or 0
                }
                for po in related_accessories
            ],
            "summary": {
                "grand_total": grand_total,
                "po_kain_amount": po_kain_amount,
                "label_amount": label_amount,
                "accessories_amount": acc_amount,
                "total_related_pos": len(related_label) + len(related_accessories)
            }
        }
        
        print(f"✅ Retrieved PO family tree for {po_kain.po_number}: {len(related_label)} LABEL + {len(related_accessories)} ACC")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching PO family tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch PO family tree: {str(e)}"
        )


# 🆕 SESSION 49 PHASE 9: Article Dropdown + BOM Auto-Generation (Feb 6, 2026)
@router.get("/articles", response_model=list[dict])
def get_articles(
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get all articles (finished goods) for PO creation dropdown.
    
    🆕 Purpose: Enable article selection in PO creation form with auto-BOM generation.
    
    Articles are filtered to FINISH_GOOD product type only.
    Optionally filter by search term (code or name).
    
    Returns:
        List of articles with id, code, name for dropdown
    """
    try:
        from app.core.models.products import ProductType
        
        query = db.query(Product).filter(
            Product.type == ProductType.FINISH_GOOD
        )
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Product.code.ilike(search_pattern)) |
                (Product.name.ilike(search_pattern))
            )
        
        articles = query.order_by(Product.code).all()
        
        result = [
            {
                "id": article.id,
                "code": article.code,
                "name": article.name
            }
            for article in articles
        ]
        
        print(f"✅ Retrieved {len(result)} articles (search: {search or 'all'})")
        return result
        
    except Exception as e:
        print(f"❌ Error fetching articles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch articles: {str(e)}"
        )


@router.get("/bom-materials/{article_id}", response_model=dict)
def get_bom_materials(
    article_id: int,
    quantity: int = 1,
    material_type_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get BOM materials for an article with optional filtering.
    
    🆕 Purpose: Auto-generate PO materials from article BOM.
    
    For PO KAIN (Fabric): material_type_filter = 'FABRIC'
    For PO LABEL: material_type_filter = 'LABEL'
    For PO ACCESSORIES: material_type_filter = 'ACCESSORIES' or None (all)
    
    Args:
        article_id: Article/Finished Good ID
        quantity: Article quantity to calculate material requirements
        material_type_filter: Optional filter (FABRIC, LABEL, ACCESSORIES, THREAD, FILLING)
    
    Returns:
        Dict with article info and list of materials with quantities
    """
    try:
        from app.core.models.bom import BOMHeader, BOMDetail
        from app.core.models.products import ProductType
        
        # Get article
        article = db.query(Product).filter(Product.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with ID {article_id} not found"
            )
        
        # Get BOM Header
        bom_header = db.query(BOMHeader).filter(
            BOMHeader.product_id == article_id,
            BOMHeader.is_active == True
        ).first()
        
        if not bom_header:
            # No BOM found - return empty materials list
            print(f"⚠️ No BOM found for article {article.code}")
            return {
                "article": {
                    "id": article.id,
                    "code": article.code,
                    "name": article.name
                },
                "quantity": quantity,
                "materials": [],
                "message": f"No BOM found for article {article.code}. You can add materials manually."
            }
        
        # Get BOM Details
        bom_details = db.query(BOMDetail).filter(
            BOMDetail.bom_header_id == bom_header.id
        ).all()
        
        materials = []
        for detail in bom_details:
            component = detail.component
            
            # Calculate total quantity needed
            qty_per_unit = float(detail.qty_needed)
            total_qty = qty_per_unit * quantity
            wastage_pct = float(detail.wastage_percent or 0)
            qty_with_wastage = total_qty * (1 + wastage_pct / 100)
            
            # Determine material category from product code or name
            material_category = _detect_material_category(component.code, component.name)
            
            # Apply filter if specified
            if material_type_filter:
                filter_upper = material_type_filter.upper()
                if filter_upper == 'FABRIC':
                    # For PO KAIN: Include fabric materials only (KOHAIR, JS BOA, POLYESTER, etc.)
                    if material_category not in ['FABRIC', 'KAIN']:
                        continue
                elif filter_upper == 'LABEL':
                    # For PO LABEL: Include label materials only
                    if material_category != 'LABEL':
                        continue
                elif filter_upper == 'ACCESSORIES':
                    # For PO ACCESSORIES: Include thread, filling, box, etc.
                    if material_category in ['FABRIC', 'KAIN', 'LABEL']:
                        continue
            
            materials.append({
                "material_id": component.id,
                "material_code": component.code,
                "material_name": component.name,
                "material_type": component.type.value if hasattr(component, 'type') else 'RAW_MATERIAL',
                "material_category": material_category,
                "qty_per_unit": qty_per_unit,
                "total_qty_needed": round(qty_with_wastage, 4),
                "wastage_percent": wastage_pct,
                "uom": getattr(component, 'uom', 'PCS'),
                "description": component.description
            })
        
        # Sort materials by code
        materials.sort(key=lambda x: x['material_code'])
        
        result = {
            "article": {
                "id": article.id,
                "code": article.code,
                "name": article.name
            },
            "quantity": quantity,
            "materials": materials,
            "summary": {
                "total_materials": len(materials),
                "filter_applied": material_type_filter,
                "total_bom_lines": len(bom_details)
            }
        }
        
        print(f"✅ Retrieved {len(materials)} materials for {article.code} (filter: {material_type_filter or 'none'}, qty: {quantity})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching BOM materials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch BOM materials: {str(e)}"
        )


def _detect_material_category(material_code: str, material_name: str) -> str:
    """Helper function to detect material category from code/name.
    
    Categories:
    - FABRIC/KAIN: Fabric materials (KOHAIR, JS BOA, POLYESTER, NYLEX, etc.)
    - LABEL: Labels (Hang Tag, Care Label, EU Label)
    - THREAD: Sewing thread
    - FILLING: Filling/Kapas
    - BOX: Carton/Box
    - ACCESSORIES: Other accessories
    """
    code_upper = material_code.upper()
    name_upper = material_name.upper()
    
    # Fabric detection (common fabric codes)
    fabric_keywords = ['IKHR', 'IJBR', 'INYR', 'INYNR', 'IPPR', 'IPR', 'KOHAIR', 'BOA', 'POLYESTER', 'NYLEX', 'FABRIC', 'KAIN']
    if any(kw in code_upper or kw in name_upper for kw in fabric_keywords):
        return 'FABRIC'
    
    # Label detection
    label_keywords = ['LABEL', 'TAG', 'HANG', 'CARE', 'EU']
    if any(kw in name_upper for kw in label_keywords):
        return 'LABEL'
    
    # Thread detection
    thread_keywords = ['THREAD', 'BENANG', 'YARN']
    if any(kw in name_upper for kw in thread_keywords):
        return 'THREAD'
    
    # Filling detection
    filling_keywords = ['FILLING', 'KAPAS', 'DACRON', 'POLYESTER FILL']
    if any(kw in name_upper for kw in filling_keywords):
        return 'FILLING'
    
    # Box detection
    box_keywords = ['BOX', 'CARTON', 'ACB']
    if any(kw in code_upper or kw in name_upper for kw in box_keywords):
        return 'BOX'
    
    # Default: ACCESSORIES
    return 'ACCESSORIES'


@router.get("/suppliers")
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get all suppliers (partners with type=Supplier).
    
    Returns:
        List of suppliers with id, name, contact info
    """
    suppliers = db.query(Partner).filter(
        Partner.type == PartnerType.SUPPLIER
    ).order_by(Partner.name).all()
    
    result = [
        {
            "id": supplier.id,
            "name": supplier.name,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "email": supplier.email
        }
        for supplier in suppliers
    ]
    
    print(f"✅ Retrieved {len(result)} suppliers")
    return result


@router.get("/available-po-kain")
def get_available_po_kain(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get available PO KAIN for reference by PO LABEL/ACCESSORIES.
    
    Returns list of PO KAIN with status SENT or RECEIVED that can be
    referenced by child PO LABEL or PO ACCESSORIES.
    
    Used by: POCreateModal dropdown for PO Reference System
    
    🔑 Business Rule:
    - Only PO KAIN (po_type=KAIN) with status SENT/RECEIVED eligible
    - Include article information for display (Article Code - Name)
    - Include week & destination for context
    
    Response Format:
    ```json
    [
      {
        "id": 123,
        "po_number": "PO-FAB-2026-0456",
        "article": {
          "id": 45,
          "code": "40551542",
          "name": "TEDDY BEAR 25CM"
        },
        "week": "W5",
        "destination": "EU",
        "status": "SENT",
        "order_date": "2026-02-05"
      }
    ]
    ```
    """
    try:
        # Query PO KAIN with status SENT or RECEIVED
        po_kain_list = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.po_type == POType.KAIN,
                PurchaseOrder.status.in_([POStatus.SENT, POStatus.RECEIVED])
            )
            .options(joinedload(PurchaseOrder.article))  # Eager load article
            .order_by(PurchaseOrder.order_date.desc())
            .all()
        )
        
        # Format response with article information
        result = []
        for po in po_kain_list:
            po_data = {
                "id": po.id,
                "po_number": po.po_number,
                "status": po.status.value if hasattr(po.status, 'value') else str(po.status),
                "order_date": po.order_date.isoformat() if po.order_date else None,
                "week": po.week,
                "destination": po.destination,
            }
            
            # Include article if exists
            if po.article:
                po_data["article"] = {
                    "id": po.article.id,
                    "code": po.article.code,
                    "name": po.article.name
                }
            else:
                po_data["article"] = None
            
            result.append(po_data)
        
        print(f"✅ Retrieved {len(result)} available PO KAIN for reference")
        return result
        
    except Exception as e:
        print(f"❌ Error fetching available PO KAIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch available PO KAIN: {str(e)}"
        )


@router.post("/bom/explosion")
def bom_explosion(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """BOM Explosion for AUTO mode - Generate materials from article + quantity.
    
    Used by: POCreateModal AUTO mode to auto-generate materials from BOM
    
    🚀 80% Time Saving: Traditional 30-material entry (15 min) → AUTO mode (3 min)
    
    Request Body:
    ```json
    {
      "article_code": "40551542",
      "quantity": 1000,
      "material_type_filter": "FABRIC"  // Optional: FABRIC, LABEL, ACCESSORIES
    }
    ```
    
    Response Format:
    ```json
    {
      "article": {
        "id": 45,
        "code": "40551542",
        "name": "TEDDY BEAR 25CM"
      },
      "quantity": 1000,
      "materials": [
        {
          "code": "IKHR504",
          "name": "KOHAIR 7MM D.BROWN",
          "type": "RAW",
          "qty_required": 2500,
          "uom": "M"
        },
        // ... 30+ materials
      ],
      "explosion_timestamp": "2026-02-10T14:30:00Z"
    }
    ```
    
    🔑 Business Rule:
    - Aggregates materials from BOM across all departments
    - Scales qty_required by article quantity
    - Includes wastage percentage
    - Optional filter by material type (FABRIC for PO KAIN, LABEL for PO LABEL, etc.)
    """
    try:
        from app.core.models.bom import BOMHeader, BOMDetail
        from app.core.models.products import ProductType
        from datetime import datetime
        
        article_code = request.get("article_code")
        quantity = request.get("quantity", 1)
        material_type_filter = request.get("material_type_filter")
        
        if not article_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="article_code is required"
            )
        
        # Find article by code
        article = db.query(Product).filter(Product.code == article_code).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with code '{article_code}' not found"
            )
        
        # Get BOM Header
        bom_header = db.query(BOMHeader).filter(
            BOMHeader.product_id == article.id,
            BOMHeader.is_active == True
        ).first()
        
        if not bom_header:
            # No BOM found - return empty materials list with message
            print(f"⚠️ No BOM found for article {article.code}")
            return {
                "article": {
                    "id": article.id,
                    "code": article.code,
                    "name": article.name
                },
                "quantity": quantity,
                "materials": [],
                "message": f"No BOM found for article {article.code}. You can add materials manually.",
                "explosion_timestamp": datetime.now().isoformat()
            }
        
        # Get BOM Details
        bom_details = db.query(BOMDetail).filter(
            BOMDetail.bom_header_id == bom_header.id
        ).all()
        
        materials = []
        for detail in bom_details:
            component = detail.component
            
            # Calculate total quantity needed
            qty_per_unit = float(detail.qty_needed)
            total_qty = qty_per_unit * quantity
            wastage_pct = float(detail.wastage_percent or 0)
            qty_with_wastage = total_qty * (1 + wastage_pct / 100)
            
            # Determine material category from product code or name
            material_category = _detect_material_category(component.code, component.name)
            
            # Apply filter if specified
            if material_type_filter:
                filter_upper = material_type_filter.upper()
                if filter_upper == 'FABRIC':
                    # For PO KAIN: Include fabric materials only
                    if material_category not in ['FABRIC', 'KAIN']:
                        continue
                elif filter_upper == 'LABEL':
                    # For PO LABEL: Include label materials only
                    if material_category != 'LABEL':
                        continue
                elif filter_upper == 'ACCESSORIES':
                    # For PO ACC: Include accessories, thread, filling, box
                    if material_category in ['FABRIC', 'KAIN', 'LABEL']:
                        continue
            
            # Get material type for PO
            material_type = 'BAHAN_PENOLONG' if material_category in ['THREAD', 'ACCESSORIES'] else 'RAW'
            if material_category == 'WIP':
                material_type = 'WIP'
            
            materials.append({
                "code": component.code,
                "name": component.name,
                "type": material_type,
                "qty_required": round(qty_with_wastage, 2),
                "uom": detail.unit or "PCS",
                "category": material_category
            })
        
        result = {
            "article": {
                "id": article.id,
                "code": article.code,
                "name": article.name
            },
            "quantity": quantity,
            "materials": materials,
            "explosion_timestamp": datetime.now().isoformat(),
            "filter_applied": material_type_filter,
            "total_materials": len(materials)
        }
        
        print(f"✅ BOM Explosion for {article.code}: {len(materials)} materials generated (filter: {material_type_filter or 'none'})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in BOM explosion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BOM explosion failed: {str(e)}"
        )
