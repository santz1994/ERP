"""Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved.

Purchasing API Endpoints
Handles purchase orders, supplier management, material receiving

🆕 UPDATE (Feb 6, 2026): Added PO Reference System
- PO Type (KAIN/LABEL/ACCESSORIES)
- Parent-child relationship (PO LABEL → PO KAIN)
- Auto-inheritance (Article, Week, Destination)
- Business rule validation (PO LABEL must reference PO KAIN)
"""

from datetime import date, datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.models.users import User
from app.core.models.warehouse import PurchaseOrder, POType, POStatus
from app.core.models.products import Product, Partner, PartnerType
from app.core.models.manufacturing import (
    ManufacturingOrder, WorkOrder, MOState, WorkOrderStatus, Department, RoutingType, MOType
)
from app.core.dependencies import require_permission
from app.core.permissions import ModuleName, Permission
from app.modules.purchasing import PurchasingService

router = APIRouter(prefix="/purchasing", tags=["Purchasing"])


# Pydantic Schemas

class CreatePOUIRequest(BaseModel):
    """Frontend-friendly PO creation schema."""
    po_type: str = Field("ACCESSORIES", description="KAIN / LABEL / ACCESSORIES")
    po_date: date = Field(..., description="Order date")
    expected_delivery_date: date = Field(..., description="Expected delivery date")
    notes: Optional[str] = None
    primary_supplier_id: int = Field(..., description="Primary supplier ID")
    article_id: Optional[int] = None
    article_qty: Optional[int] = None
    source_po_kain_id: Optional[int] = None
    week: Optional[str] = None
    destination: Optional[str] = None
    materials: list[dict] = Field(default_factory=list)


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
    status: Optional[str]
    total_amount: Optional[float]
    currency: Optional[str]
    extra_metadata: Optional[dict]
    # PO Reference System fields
    po_type: Optional[str]
    source_po_kain_id: Optional[int]
    article_id: Optional[int]
    article_qty: Optional[int]
    week: Optional[str]
    destination: Optional[str]
    created_at: Optional[dt]
    updated_at: Optional[dt]

    @validator('status', 'po_type', pre=True)
    def enum_to_str(cls, v):
        if v is None:
            return v
        return v.value if hasattr(v, 'value') else str(v)

    class Config:
        orm_mode = True


class SupplierPerformanceResponse(BaseModel):
    supplier_id: int
    total_purchase_orders: int
    completed_orders: int
    on_time_delivery: int
    on_time_rate: float
    completion_rate: float


# ─── STOCK RECEIVE HELPER ───────────────────────────────────────────────────

def _receive_po_stock(db: Session, po: PurchaseOrder, user_id: int) -> dict:
    """
    Auto-create StockLot + StockMove + StockQuant when a PO is marked Received.
    Extracts line-item data from po.extra_metadata["items"].
    Returns {"received_lines": N, "wh_location_id": id} or {"skipped": reason}.
    """
    from datetime import datetime as _dt
    from app.core.models.warehouse import (
        Location, LocationType, StockLot, StockMove, StockQuant, StockMoveStatus
    )

    items = (po.extra_metadata or {}).get("items", [])
    if not items:
        return {"skipped": "no items in po.extra_metadata"}

    # Get or create Virtual/Supplier (source) location
    supplier_loc = db.query(Location).filter(Location.name == "Virtual/Supplier").first()
    if not supplier_loc:
        supplier_loc = Location(name="Virtual/Supplier", type=LocationType.SUPPLIER, is_active=True)
        db.add(supplier_loc)
        db.flush()

    # Get or create default Warehouse/Stock (destination) location
    wh_loc = db.query(Location).filter(Location.name == "Warehouse/Stock").first()
    if not wh_loc:
        wh_loc = db.query(Location).filter(Location.type == LocationType.INTERNAL).first()
    if not wh_loc:
        wh_loc = Location(name="Warehouse/Stock", type=LocationType.INTERNAL, is_active=True)
        db.add(wh_loc)
        db.flush()

    now = _dt.utcnow()
    received_lines = 0

    for item in items:
        pid = item.get("product_id")
        qty = float(item.get("quantity") or 0)
        uom = str(item.get("uom") or "PCS")
        code = str(item.get("material_code") or pid or "")

        if not pid or qty <= 0:
            continue

        lot_number = f"LOT-{po.po_number}-{code}-{now.strftime('%Y%m%d%H%M%S')}"

        # Create StockLot (traceability)
        lot = StockLot(
            lot_number=lot_number,
            product_id=pid,
            qty_initial=qty,
            qty_remaining=qty,
            supplier_id=po.supplier_id,
            purchase_order_id=po.id,
            received_date=now,
        )
        db.add(lot)
        db.flush()  # need lot.id for StockMove FK

        # Create StockMove (Supplier → Warehouse, DONE)
        move = StockMove(
            product_id=pid,
            qty=qty,
            uom=uom,
            location_id_from=supplier_loc.id,
            location_id_to=wh_loc.id,
            reference_doc=po.po_number,
            state=StockMoveStatus.DONE,
            lot_id=lot.id,
        )
        db.add(move)

        # Update StockQuant (aggregate balance at warehouse location)
        quant = db.query(StockQuant).filter(
            StockQuant.product_id == pid,
            StockQuant.location_id == wh_loc.id,
        ).first()
        if quant:
            quant.qty_on_hand += qty
        else:
            quant = StockQuant(
                product_id=pid,
                location_id=wh_loc.id,
                lot_id=lot.id,
                qty_on_hand=qty,
                qty_reserved=0,
            )
            db.add(quant)

        received_lines += 1

    db.flush()

    # Traceability: find linked MO batch via source_po_kain_id (ACCESSORIES/LABEL)
    linked_mo_batch = None
    ref_kain_id = po.source_po_kain_id
    if ref_kain_id:
        from app.core.models.manufacturing import ManufacturingOrder, MOType
        linked_mo = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.po_fabric_id == ref_kain_id,
            ManufacturingOrder.mo_type == MOType.PRODUCTION,
        ).first()
        if linked_mo:
            linked_mo_batch = linked_mo.batch_number

    print(f"✅ PO {po.po_number}: {received_lines} line(s) stock updated → Warehouse/Stock")
    return {
        "received_lines": received_lines,
        "wh_location_id": wh_loc.id,
        "linked_mo_batch": linked_mo_batch,
    }


# ─── AUTO MO/WO TRIGGER HELPER ─────────────────────────────────────────────

def _auto_trigger_mo_wo(db: Session, po: PurchaseOrder, user_id: int) -> dict | None:
    """
    Dual Trigger System:
      PO KAIN → Sent  : Create MO (PARTIAL) + Cutting WO
      PO LABEL → Sent : Escalate existing MO to RELEASED + create Sewing/Finishing/Packing WOs
    Returns a dict with info about what was created, or None if N/A.
    """
    try:
        po_type = po.po_type.value if po.po_type else None
        article_qty = int(po.article_qty or 0)

        # ── TRIGGER 1: PO KAIN ─────────────────────────────────────────
        if po_type == "KAIN":
            if not po.article_id:
                print(f"⚠ PO KAIN {po.po_number} has no article_id – skipping MO creation")
                return None

            # Prevent duplicate MOs for same PO KAIN
            existing_buyer = db.query(ManufacturingOrder).filter(
                ManufacturingOrder.po_fabric_id == po.id,
                ManufacturingOrder.mo_type == MOType.BUYER,
            ).first()
            if existing_buyer:
                existing_prod = db.query(ManufacturingOrder).filter(
                    ManufacturingOrder.buyer_mo_id == existing_buyer.id,
                ).first()
                print(f"ℹ MO BUYER {existing_buyer.batch_number} already exists for PO KAIN {po.po_number}")
                return {
                    "mo_buyer_id": existing_buyer.id,
                    "mo_production_id": existing_prod.id if existing_prod else None,
                    "batch_number": existing_buyer.batch_number,
                    "action": "existing",
                }

            ts = dt.now().strftime('%H%M%S')
            batch_buyer = f"MO-BUYER-{po.po_number}-{ts}"
            batch_prod  = f"MO-PROD-{po.po_number}-{ts}"

            # ── MO BUYER (reference / acuan — FIXED qty, locked) ─────────
            mo_buyer = ManufacturingOrder(
                po_fabric_id=po.id,
                po_id=po.id,
                product_id=po.article_id,
                qty_planned=article_qty,
                target_quantity=article_qty,
                buffer_quantity=0,
                production_quantity=article_qty,
                routing_type=RoutingType.ROUTE2,
                batch_number=batch_buyer,
                state=MOState.DRAFT,
                trigger_mode="PARTIAL",
                mo_type=MOType.BUYER,
                is_qty_locked=True,          # Locked to PO qty — cannot be changed
                production_week=po.week,
                destination_country=po.destination,
            )
            db.add(mo_buyer)
            db.flush()  # get mo_buyer.id

            # ── MO PRODUCTION (operational / daily tracking) ─────────────
            mo_prod = ManufacturingOrder(
                po_fabric_id=po.id,
                po_id=po.id,
                product_id=po.article_id,
                qty_planned=article_qty,
                target_quantity=article_qty,
                buffer_quantity=0,
                production_quantity=article_qty,
                routing_type=RoutingType.ROUTE2,
                batch_number=batch_prod,
                state=MOState.DRAFT,
                trigger_mode="PARTIAL",
                mo_type=MOType.PRODUCTION,
                buyer_mo_id=mo_buyer.id,          # linked to BUYER MO
                production_week=po.week,
                destination_country=po.destination,
            )
            db.add(mo_prod)
            db.flush()  # get mo_prod.id

            # Cutting WO linked to PRODUCTION MO (PARTIAL mode – Cutting only)
            wo_cutting = WorkOrder(
                mo_id=mo_prod.id,
                product_id=po.article_id,
                department=Department.CUTTING,
                status=WorkOrderStatus.PENDING,
                wo_number=f"WO-CUT-{batch_prod}",
                sequence=1,
                input_qty=article_qty,
                target_qty=article_qty,
            )
            db.add(wo_cutting)

            # Link back to PO → PRODUCTION MO is the operational link
            po.linked_mo_id = mo_prod.id
            db.commit()

            print(
                f"✅ AUTO MO BUYER created: {batch_buyer}\n"
                f"✅ AUTO MO PRODUCTION created: {batch_prod} | WO-CUT | PARTIAL mode | qty={article_qty}"
            )
            return {
                "mo_buyer_id": mo_buyer.id,
                "mo_buyer_batch": batch_buyer,
                "mo_production_id": mo_prod.id,
                "mo_production_batch": batch_prod,
                "trigger_mode": "PARTIAL",
                "work_orders_created": ["CUTTING"],
                "action": "created",
            }

        # ── NO TRIGGER: PO ACCESSORIES ────────────────────────────────
        elif po_type == "ACCESSORIES":
            # Accessories POs are stock-only — no MO/WO trigger.
            # They optionally link back to a PO KAIN for traceability.
            return {
                "action": "no_trigger",
                "po_type": "ACCESSORIES",
                "source_po_kain_id": po.source_po_kain_id,
                "reason": (
                    "PO ACCESSORIES does not trigger MO/WO "
                    "— stock will update on Receive"
                ),
            }

        # ── TRIGGER 2: PO LABEL ────────────────────────────────────────
        elif po_type == "LABEL":
            # Find the PRODUCTION MO created from PO KAIN (TRIGGER 1)
            # We target mo_type=PRODUCTION because that's the operational MO
            # (BUYER MO is the fixed reference — WOs go to PRODUCTION MO)
            mo = None
            if po.source_po_kain_id:
                mo = db.query(ManufacturingOrder).filter(
                    ManufacturingOrder.po_fabric_id == po.source_po_kain_id,
                    ManufacturingOrder.mo_type == MOType.PRODUCTION,
                ).first()
                # Fallback: legacy single-MO (before dual-MO update)
                if not mo:
                    mo = db.query(ManufacturingOrder).filter(
                        ManufacturingOrder.po_fabric_id == po.source_po_kain_id
                    ).first()

            if not mo:
                print(f"⚠ No existing PRODUCTION MO found for source PO KAIN {po.source_po_kain_id} – cannot RELEASE")
                return {"action": "skipped", "reason": "No MO found for source PO KAIN. Send PO KAIN first to create MO."}

            # Escalate MO to RELEASED (first PO LABEL to be sent)
            if mo.trigger_mode != "RELEASED":
                mo.trigger_mode = "RELEASED"
            mo.po_label_id = po.id  # last label wins (traceability)
            db.flush()

            # Use THIS PO LABEL's batch qty, NOT the total MO qty
            # Each PO LABEL = 1 delivery batch (e.g. 5000 EU, 2000 EA)
            batch_qty = int(po.article_qty or mo.qty_planned or 0)
            label_suffix = po.po_number  # unique per PO LABEL

            # Always create fresh WOs for this batch (no deduplication — different batches)
            new_wos = []
            route = [
                (Department.SEWING,    2, "SEW"),
                (Department.FINISHING, 3, "FIN"),
                (Department.PACKING,   4, "PCK"),
            ]
            for dept, seq, code in route:
                wo = WorkOrder(
                    mo_id=mo.id,
                    product_id=mo.product_id,
                    department=dept,
                    status=WorkOrderStatus.PENDING,
                    wo_number=f"WO-{code}-{label_suffix}",
                    sequence=seq,
                    input_qty=batch_qty,
                    target_qty=batch_qty,
                    notes=f"Batch: {po.week} / {po.destination} ({batch_qty} pcs) — from {label_suffix}",
                )
                db.add(wo)
                new_wos.append(f"{dept.value} ({batch_qty} pcs)")

            db.commit()
            print(f"✅ MO {mo.batch_number} | New batch WOs for {label_suffix}: {new_wos}")
            return {
                "mo_id": mo.id,
                "batch_number": mo.batch_number,
                "trigger_mode": "RELEASED",
                "batch_qty": batch_qty,
                "week": po.week,
                "destination": po.destination,
                "work_orders_created": new_wos,
                "action": "released",
            }

    except Exception as e:
        db.rollback()
        print(f"❌ Error in auto MO/WO trigger: {e}")
        return None

    return None


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



@router.patch("/purchase-orders/{po_id}/status")
def update_po_status(
    po_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.APPROVE))
):
    """Update PO status with validation.

    Allowed transitions:
    - Draft → Sent (send to supplier)
    - Draft → Cancelled
    - Sent → Received (goods arriving)
    - Received → Done
    """
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail=f"Purchase order {po_id} not found")

    current = po.status.value if po.status else None
    allowed = {
        "Draft": ["Sent", "Cancelled"],
        "Sent": ["Received", "Cancelled"],
        "Received": ["Done"],
        "Cancelled": [],
        "Done": [],
    }

    if current not in allowed or new_status not in allowed.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current} to {new_status}. Allowed: {allowed.get(current, [])}"
        )

    try:
        status_map = {
            "Draft": POStatus.DRAFT,
            "Sent": POStatus.SENT,
            "Received": POStatus.RECEIVED,
            "Done": POStatus.DONE,
            "Cancelled": POStatus.CANCELLED,
        }
        po.status = status_map[new_status]
        db.commit()
        db.refresh(po)

        # ── AUTO MO/WO TRIGGER ────────────────────────────────────────────
        mo_info = None
        stock_info = None
        if new_status == "Sent":
            mo_info = _auto_trigger_mo_wo(db, po, current_user.id)
        elif new_status == "Received":
            # Auto-update stock when PO is marked as received
            try:
                stock_info = _receive_po_stock(db, po, current_user.id)
                db.commit()
            except Exception as stock_err:
                print(f"⚠ Stock receive failed for {po.po_number}: {stock_err}")
        # ─────────────────────────────────────────────────────────────────

        print(f"✅ PO {po.po_number}: {current} → {new_status} (by user {current_user.id})")
        result = {
            "id": po.id,
            "po_number": po.po_number,
            "status": new_status,
            "message": f"PO status updated to {new_status}",
        }
        if mo_info:
            result["mo_created"] = mo_info
        if stock_info:
            result["stock_received"] = stock_info
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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


@router.post("/po", status_code=status.HTTP_201_CREATED)
def create_po_from_ui(
    request: CreatePOUIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.CREATE))
):
    """Frontend-friendly PO creation endpoint.

    Accepts the form data format from the UI modal:
    - po_date / expected_delivery_date instead of order_date / expected_date
    - primary_supplier_id at PO level
    - materials[] array with per-material supplier_id
    - Auto-generates po_number
    - Stores line items in extra_metadata (JSON)
    """
    try:
        # Map po_type string → POType enum
        try:
            po_type = POType[request.po_type.upper()]
        except KeyError:
            po_type = POType.ACCESSORIES

        # Validate supplier
        supplier = db.query(Partner).filter(
            Partner.id == request.primary_supplier_id,
            Partner.type == PartnerType.SUPPLIER,
        ).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supplier ID {request.primary_supplier_id} not found or is not a supplier",
            )

        # PO LABEL validations
        if po_type == POType.LABEL:
            if not request.source_po_kain_id:
                raise HTTPException(status_code=400, detail="PO LABEL must reference a PO KAIN")
            if not request.week:
                raise HTTPException(status_code=400, detail="PO LABEL requires week")
            if not request.destination:
                raise HTTPException(status_code=400, detail="PO LABEL requires destination")
            po_kain = db.query(PurchaseOrder).filter(
                PurchaseOrder.id == request.source_po_kain_id
            ).first()
            if not po_kain:
                raise HTTPException(status_code=404, detail=f"PO KAIN {request.source_po_kain_id} not found")
            # Auto-inherit article from PO KAIN
            if not request.article_id and po_kain.article_id:
                request.article_id = po_kain.article_id
                request.article_qty = po_kain.article_qty

            # ── QTY OVERFLOW CHECK ──────────────────────────────────────
            # Total allocated across all existing PO LABELs + this new one
            # must not exceed PO KAIN article_qty
            if po_kain.article_qty and request.article_qty:
                from sqlalchemy import func as sqlfunc
                already_allocated = db.query(
                    sqlfunc.coalesce(sqlfunc.sum(PurchaseOrder.article_qty), 0)
                ).filter(
                    PurchaseOrder.source_po_kain_id == request.source_po_kain_id,
                    PurchaseOrder.po_type == POType.LABEL,
                ).scalar() or 0
                total_after = int(already_allocated) + int(request.article_qty)
                if total_after > po_kain.article_qty:
                    remaining = po_kain.article_qty - int(already_allocated)
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Qty overflow: PO KAIN total {po_kain.article_qty} pcs, "
                            f"already allocated {int(already_allocated)} pcs, "
                            f"remaining {remaining} pcs, "
                            f"you requested {request.article_qty} pcs."
                        )
                    )

        # PO ACCESSORIES: validate referenced PO KAIN exists (any status allowed)
        if po_type == POType.ACCESSORIES and request.source_po_kain_id:
            acc_kain = db.query(PurchaseOrder).filter(
                PurchaseOrder.id == request.source_po_kain_id,
                PurchaseOrder.po_type == POType.KAIN,
            ).first()
            if not acc_kain:
                raise HTTPException(
                    status_code=404,
                    detail=f"PO KAIN with ID {request.source_po_kain_id} not found",
                )

        # PO KAIN requires article
        if po_type == POType.KAIN and not request.article_id:
            raise HTTPException(status_code=400, detail="PO KAIN requires article_id")

        # Validate article exists
        if request.article_id:
            article = db.query(Product).filter(Product.id == request.article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail=f"Article {request.article_id} not found")

        # Resolve product_ids, normalise material list, compute total
        # Batch-load products by code in one query (avoid N+1)
        codes_to_lookup = [mat.get("material_code", "") for mat in request.materials if not mat.get("product_id") and mat.get("material_code")]
        code_map = {p.code: p for p in db.query(Product).filter(Product.code.in_(codes_to_lookup)).all()} if codes_to_lookup else {}

        normalized_materials = []
        total_amount = 0.0
        for mat in request.materials:
            pid = mat.get("product_id")
            if not pid:
                code = mat.get("material_code", "")
                prod = code_map.get(code)
                pid = prod.id if prod else None

            qty = float(mat.get("quantity") or 0)
            price = float(mat.get("unit_price") or 0)
            total_amount += qty * price

            normalized_materials.append({
                "product_id": pid,
                "material_code": mat.get("material_code", ""),
                "material_name": mat.get("material_name", ""),
                "supplier_id": mat.get("supplier_id"),
                "quantity": qty,
                "uom": mat.get("uom", "PCS"),
                "unit_price": price,
                "total_price": qty * price,
                "description": mat.get("description", ""),
            })

        # Auto-generate unique po_number
        po_number = f"PO-{po_type.value}-{dt.now().strftime('%Y%m%d%H%M%S')}"

        # Create PO record
        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=request.primary_supplier_id,
            order_date=request.po_date,
            expected_date=request.expected_delivery_date,
            status=POStatus.DRAFT,
            po_type=po_type,
            source_po_kain_id=request.source_po_kain_id,
            article_id=request.article_id,
            article_qty=request.article_qty,
            week=request.week,
            destination=request.destination,
        )
        db.add(po)
        db.flush()  # get po.id before setting JSON columns

        po.total_amount = total_amount
        po.currency = "IDR"
        po.extra_metadata = {
            "items": normalized_materials,
            "notes": request.notes,
            "created_by": current_user.id,
            "created_at": dt.now().isoformat(),
        }

        db.commit()
        db.refresh(po)

        print(f"✅ Created PO (UI): {po.po_number} type={po_type.value} total={total_amount:,.0f} IDR")
        return {
            "id": po.id,
            "po_number": po.po_number,
            "status": po.status.value,
            "po_type": po_type.value,
            "total_amount": total_amount,
            "message": f"PO {po.po_number} created successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating PO from UI: {str(e)}")
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



# ══════════════════════════════════════════════════════════════════════════════
# PO DELETION / APPROVAL WORKFLOW
# ══════════════════════════════════════════════════════════════════════════════

from datetime import datetime as _dt
from app.core.models.po_requests import PODeleteRequest, PORequestStatus as _ReqStatus

ADMIN_ROLES = {"Developer", "Superadmin", "Admin", "Manager"}


class _DeletePOBody(BaseModel):
    reason: str = Field(..., min_length=5, description="Reason for deletion / cancellation")


class _RespondDeleteBody(BaseModel):
    note: str = ""


@router.delete("/purchase-orders/{po_id}")
def delete_purchase_order(
    po_id: int,
    body: _DeletePOBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.DELETE)),
):
    """Permanently delete or forcibly cancel a PO.

    - **System Admin** (Admin / Superadmin / Developer): direct action.
    - Others: must use POST …/request-delete instead.
    """
    if current_user.role.value not in ADMIN_ROLES:
        raise HTTPException(
            403,
            "You don't have permission to delete directly. "
            "Use POST /purchasing/purchase-orders/{id}/request-delete instead.",
        )
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, "Purchase Order not found")

    if po.status in (POStatus.RECEIVED, POStatus.DONE):
        raise HTTPException(
            400,
            f"Cannot delete PO in '{po.status.value}' status. "
            "Only Draft / Sent / Partial can be deleted.",
        )

    po_number = po.po_number
    # Hard delete; foreign-key cascades handle child POs and WOs
    db.delete(po)
    db.commit()
    return {"message": f"PO '{po_number}' deleted successfully."}


@router.post("/purchase-orders/{po_id}/request-delete", status_code=201)
def request_po_deletion(
    po_id: int,
    body: _DeletePOBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW)),
):
    """Non-admin users submit a deletion request for manager approval."""
    if current_user.role.value in ADMIN_ROLES:
        raise HTTPException(
            400,
            "Admins can delete directly. Use DELETE /purchasing/purchase-orders/{id}.",
        )
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, "Purchase Order not found")

    existing = (
        db.query(PODeleteRequest)
        .filter(
            PODeleteRequest.po_id == po_id,
            PODeleteRequest.status == _ReqStatus.PENDING,
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "A deletion request for this PO is already pending.")

    req = PODeleteRequest(
        po_id=po_id,
        po_number=po.po_number,
        request_reason=body.reason,
        requested_by=current_user.id,
    )
    db.add(req); db.commit(); db.refresh(req)
    return {
        "id": req.id,
        "po_number": req.po_number,
        "status": req.status.value,
        "message": "Deletion request submitted. Awaiting manager approval.",
    }


@router.post("/purchase-orders/{po_id}/generate-mo", status_code=200)
def generate_mo_for_po(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.UPDATE)),
):
    """Manually trigger MO + WO creation for a PO KAIN that has no linked MO.
    
    Used when PO was marked Done/Received without going through Sent (which auto-creates MO).
    """
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, "Purchase Order not found")
    if not po.po_type or po.po_type.value != "KAIN":
        raise HTTPException(400, "Only PO KAIN can generate Manufacturing Orders")
    if not po.article_id:
        raise HTTPException(400, "PO KAIN has no article_id — cannot generate MO")

    mo_info = _auto_trigger_mo_wo(db, po, current_user.id)
    if not mo_info:
        raise HTTPException(status_code=400, detail="MO generation failed — check server logs for details (article_id, BOM data, or DB constraint)")

    return {
        "message": f"Manufacturing Order generated for {po.po_number}",
        "mo_info": mo_info,
    }


@router.get("/purchase-orders/delete-requests")
def list_delete_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW)),
):
    """List pending PO deletion requests. Only accessible by Admin roles."""
    if current_user.role.value not in ADMIN_ROLES:
        raise HTTPException(403, "Only managers / admins can view deletion requests.")
    reqs = (
        db.query(PODeleteRequest)
        .options(
            joinedload(PODeleteRequest.requester),
            joinedload(PODeleteRequest.responder),
            joinedload(PODeleteRequest.purchase_order),
        )
        .order_by(PODeleteRequest.requested_at.desc())
        .all()
    )
    return [_fmt_delete_request(r) for r in reqs]


@router.post("/purchase-orders/delete-requests/{req_id}/approve")
def approve_delete_request(
    req_id: int,
    body: _RespondDeleteBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.DELETE)),
):
    """Approve a deletion request — deletes the PO."""
    if current_user.role.value not in ADMIN_ROLES:
        raise HTTPException(403, "Only admins can approve deletion requests.")
    req = db.query(PODeleteRequest).filter(PODeleteRequest.id == req_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    if req.status != _ReqStatus.PENDING:
        raise HTTPException(400, f"Request is already '{req.status.value}'")

    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == req.po_id).first()
    if po:
        db.delete(po)

    req.status = _ReqStatus.APPROVED
    req.responded_by = current_user.id
    req.responded_at = _dt.utcnow()
    req.response_note = body.note
    req.po_id = None  # detach before flush
    db.commit()
    return {"message": f"PO '{req.po_number}' deletion approved and executed."}


@router.post("/purchase-orders/delete-requests/{req_id}/reject")
def reject_delete_request(
    req_id: int,
    body: _RespondDeleteBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.DELETE)),
):
    """Reject a deletion request — PO stays intact."""
    if current_user.role.value not in ADMIN_ROLES:
        raise HTTPException(403, "Only admins can reject deletion requests.")
    req = db.query(PODeleteRequest).filter(PODeleteRequest.id == req_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    if req.status != _ReqStatus.PENDING:
        raise HTTPException(400, f"Request is already '{req.status.value}'")

    req.status = _ReqStatus.REJECTED
    req.responded_by = current_user.id
    req.responded_at = _dt.utcnow()
    req.response_note = body.note
    db.commit()
    return {"message": f"Deletion request for PO '{req.po_number}' rejected."}


def _fmt_delete_request(r: PODeleteRequest) -> dict:
    return {
        "id": r.id,
        "po_id": r.po_id,
        "po_number": r.po_number,
        "po_status": r.purchase_order.status.value if r.purchase_order else "deleted",
        "request_reason": r.request_reason,
        "status": r.status.value,
        "requested_by": r.requester.username if r.requester else None,
        "requested_at": r.requested_at.isoformat() if r.requested_at else None,
        "responded_by": r.responder.username if r.responder else None,
        "responded_at": r.responded_at.isoformat() if r.responded_at else None,
        "response_note": r.response_note,
    }


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
        return result  # flat list — frontend expects array, not wrapped object

    except Exception as e:
        print(f"❌ Error fetching available PO KAIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch available PO KAIN: {str(e)}"
        )


@router.get("/purchase-orders/{po_id}")
def get_purchase_order_detail(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.PURCHASING, Permission.VIEW))
):
    """Get single purchase order detail including materials list."""
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail=f"Purchase order {po_id} not found")

    supplier = db.query(Partner).filter(Partner.id == po.supplier_id).first()
    supplier_name = supplier.name if supplier else f"Supplier #{po.supplier_id}"

    article_name = None
    if po.article_id:
        article = db.query(Product).filter(Product.id == po.article_id).first()
        article_name = article.name if article else None

    source_po_number = None
    if po.source_po_kain_id:
        source_po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po.source_po_kain_id).first()
        source_po_number = source_po.po_number if source_po else None

    metadata = po.extra_metadata or {}
    items = metadata.get("items", [])

    # For PO KAIN: include all linked PO LABELs (delivery batches)
    linked_labels = []
    total_allocated = 0
    if po.po_type and po.po_type.value == "KAIN":
        label_pos = db.query(PurchaseOrder).filter(
            PurchaseOrder.source_po_kain_id == po.id,
            PurchaseOrder.po_type == POType.LABEL,
        ).order_by(PurchaseOrder.order_date).all()
        for lpo in label_pos:
            lqty = int(lpo.article_qty or 0)
            total_allocated += lqty
            linked_labels.append({
                "id": lpo.id,
                "po_number": lpo.po_number,
                "status": lpo.status.value if lpo.status else None,
                "week": lpo.week,
                "destination": lpo.destination,
                "article_qty": lqty,
                "order_date": lpo.order_date.isoformat() if lpo.order_date else None,
            })

    remaining_qty = max(0, (po.article_qty or 0) - total_allocated)

    # For PO KAIN: include linked PO ACCESSORIES
    linked_accessories = []
    if po.po_type and po.po_type.value == "KAIN":
        acc_pos = db.query(PurchaseOrder).filter(
            PurchaseOrder.source_po_kain_id == po.id,
            PurchaseOrder.po_type == POType.ACCESSORIES,
        ).order_by(PurchaseOrder.order_date).all()
        for apo in acc_pos:
            asp = db.query(Partner).filter(
                Partner.id == apo.supplier_id
            ).first()
            linked_accessories.append({
                "id": apo.id,
                "po_number": apo.po_number,
                "status": apo.status.value if apo.status else None,
                "supplier_name": asp.name if asp else f"Supplier #{apo.supplier_id}",
                "total_amount": float(apo.total_amount or 0),
                "order_date": apo.order_date.isoformat() if apo.order_date else None,
            })

    # ── Linked Manufacturing Order (KAIN direct / LABEL via source_po_kain_id)
    linked_mo_data = None
    po_type_val = po.po_type.value if po.po_type else None
    is_kain = po_type_val == "KAIN"
    # For LABEL/ACCESSORIES: look up MO of the parent PO KAIN
    is_child = po_type_val in ("LABEL", "ACCESSORIES") and po.source_po_kain_id
    if is_kain or is_child:
        lookup_po_id = po.id if is_kain else po.source_po_kain_id
        from sqlalchemy.orm import joinedload as _jl
        mo = None
        # 1. Try via direct FK (PO KAIN only)
        if is_kain and po.linked_mo_id:
            mo = db.query(ManufacturingOrder).filter(
                ManufacturingOrder.id == po.linked_mo_id
            ).options(_jl(ManufacturingOrder.work_orders)).first()
        # 2. Try by po_fabric_id (PRODUCTION MO preferred)
        if not mo:
            mo = db.query(ManufacturingOrder).filter(
                ManufacturingOrder.po_fabric_id == lookup_po_id,
                ManufacturingOrder.mo_type == MOType.PRODUCTION,
            ).options(_jl(ManufacturingOrder.work_orders)).first()
        # 3. Fallback: any MO linked to this PO
        if not mo:
            mo = db.query(ManufacturingOrder).filter(
                ManufacturingOrder.po_fabric_id == lookup_po_id
            ).options(_jl(ManufacturingOrder.work_orders)).first()

        if mo:
            linked_mo_data = {
                "id": mo.id,
                "batch_number": mo.batch_number,
                "state": mo.state.value if mo.state else None,
                "trigger_mode": mo.trigger_mode or "PARTIAL",
                "qty_planned": float(mo.qty_planned or 0),
                "qty_produced": float(mo.qty_produced or 0),
                "routing_type": mo.routing_type.value if mo.routing_type else None,
                "created_at": mo.created_at.isoformat() if mo.created_at else None,
                "work_orders": [
                    {
                        "id": wo.id,
                        "wo_number": wo.wo_number or f"WO-{wo.id}",
                        "department": wo.department.value if wo.department else None,
                        "status": wo.status.value if wo.status else None,
                        "target_qty": float(wo.target_qty or wo.input_qty or 0),
                        "output_qty": float(wo.output_qty or 0),
                        "sequence": wo.sequence,
                    }
                    for wo in sorted(mo.work_orders, key=lambda w: w.sequence or 99)
                ]
            }

    return {
        "id": po.id,
        "po_number": po.po_number,
        "po_type": po.po_type.value if po.po_type else None,
        "status": po.status.value if po.status else None,
        "supplier_id": po.supplier_id,
        "supplier_name": supplier_name,
        "order_date": po.order_date.isoformat() if po.order_date else None,
        "expected_date": po.expected_date.isoformat() if po.expected_date else None,
        "total_amount": float(po.total_amount) if po.total_amount else 0.0,
        "currency": po.currency or "IDR",
        "article_id": po.article_id,
        "article_name": article_name,
        "article_qty": po.article_qty,
        "week": po.week,
        "destination": po.destination,
        "source_po_kain_id": po.source_po_kain_id,
        "source_po_number": source_po_number,
        "notes": metadata.get("notes"),
        "created_at": po.created_at.isoformat() if po.created_at else None,
        "items": items,
        # Batch-split fields (only meaningful for PO KAIN)
        "linked_labels": linked_labels,
        "total_allocated": total_allocated,
        "remaining_qty": remaining_qty,
        # Manufacturing Order (PO KAIN direct / PO LABEL shows parent MO)
        "linked_mo": linked_mo_data,
        # PO ACCESSORIES linked to this PO KAIN (only meaningful for KAIN)
        "linked_accessories": linked_accessories,
    }


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
        
        # Get BOM Header - prefer consolidated purchasing BOM (PURCH-1.0) first,
        # then fall back to any active BOM
        bom_header = db.query(BOMHeader).filter(
            BOMHeader.product_id == article_id,
            BOMHeader.revision == "PURCH-1.0",
            BOMHeader.is_active == True
        ).first()
        
        if not bom_header:
            # Fall back to any active BOM that is not a department-stage one
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
        bom_details = (
            db.query(BOMDetail)
            .filter(BOMDetail.bom_header_id == bom_header.id)
            .options(joinedload(BOMDetail.component).joinedload(Product.category))
            .all()
        )
        
        materials = []
        for detail in bom_details:
            component = detail.component
            
            # Calculate total quantity needed
            qty_per_unit = float(detail.qty_needed)
            total_qty = qty_per_unit * quantity
            wastage_pct = float(detail.wastage_percent or 0)
            qty_with_wastage = total_qty * (1 + wastage_pct / 100)
            
            # Determine material category — use DB category name when available
            cat_name = component.category.name if component.category else ''
            material_category = _detect_material_category(component.code, component.name, cat_name)
            
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
                "material_type": component.type.value if hasattr(component.type, 'value') else 'RAW_MATERIAL',
                "material_category": material_category,
                "qty_per_unit": qty_per_unit,
                "total_qty_needed": round(qty_with_wastage, 4),
                "wastage_percent": wastage_pct,
                # Always return plain string so frontend doesn't see enum objects
                "uom": (
                    component.uom.value
                    if hasattr(component.uom, 'value')
                    else str(component.uom or 'Pcs')
                ),
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


def _detect_material_category(material_code: str, material_name: str, category_name: str = '') -> str:
    """Detect material category — uses DB category name first, then code/name fallback.

    PO filter mapping:
      FABRIC  → PO KAIN   (category starts with 'Fabric')
      LABEL   → PO LABEL  (category starts with 'Label')
      ACCESSORIES → PO ACCESSORIES  (Thread, Stuffing, Accessories, Packaging, Elastic, etc.)
    """
    cat = category_name.upper() if category_name else ''

    # ── DB-category-based detection (most reliable) ──────────────────────
    if cat.startswith('FABRIC'):
        return 'FABRIC'
    if cat.startswith('LABEL'):
        return 'LABEL'
    if cat.startswith('THREAD'):
        return 'THREAD'
    if cat.startswith('STUFFING'):
        return 'FILLING'
    if cat.startswith('ACCESSORIES'):
        return 'ACCESSORIES'
    if cat.startswith('PACKAGING'):
        return 'ACCESSORIES'
    if cat in ('ELASTIC', 'ELASTIC TAPE'):
        return 'ACCESSORIES'
    if cat.startswith('CHEMICAL'):      # Chemical / Lem
        return 'ACCESSORIES'
    if cat.startswith('ISOLASI'):       # Isolasi / Insulation
        return 'ACCESSORIES'
    if cat.startswith('JARUM'):         # Jarum / Needle
        return 'ACCESSORIES'
    if cat.startswith('WIP'):
        return 'WIP'

    # ── Fallback: code / name keyword detection ───────────────────────────
    code_upper = material_code.upper()
    name_upper = material_name.upper()

    fabric_kw = ['IKHR', 'IJBR', 'INYR', 'INYNR', 'IPPR', 'IPR', 'ISHR',
                 'IFLR', 'IKTR', 'IBTR', 'IKNR', 'ICOR',
                 'KOHAIR', 'BOA', 'NYLEX', 'FLANNEL', 'VELVET', 'VELBOA',
                 'MINKY', 'SHERPA', 'PLUMETTE', 'PLUCHE', 'CORAL',
                 'POLYESTER PRINT', 'GREY FABRIC', 'BATTING']
    if any(kw in code_upper or kw in name_upper for kw in fabric_kw):
        return 'FABRIC'

    label_kw = ['LABEL', 'HANG TAG', 'CARE LABEL', 'ULL STICKER', 'STICKER ULL',
                'RPI', 'BARCODE', 'SWING TAG', 'TAG GUNTING', 'WOVEN LABEL']
    if any(kw in name_upper for kw in label_kw):
        return 'LABEL'

    thread_kw = ['THREAD', 'BENANG', 'JAHIT']
    if any(kw in name_upper for kw in thread_kw):
        return 'THREAD'

    filling_kw = ['FILLING', 'KAPAS', 'DACRON', 'FIBER FILL', 'POLYESTER FILL']
    if any(kw in name_upper for kw in filling_kw):
        return 'FILLING'

    plastic_kw = ['PLASTIC', 'PE ', 'PET ', 'PVC', 'POLYETHYLENE', 'POLYPROPYLENE', 'POLYSTYRENE', 'EVA ', 'ABS ', 'IPP']
    if any(kw in name_upper or kw in code_upper for kw in plastic_kw):
        return 'ACCESSORIES'

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
                PurchaseOrder.status.in_([
                    POStatus.DRAFT, POStatus.SENT, POStatus.RECEIVED, POStatus.DONE
                ])
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
                "article_qty": po.article_qty,
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
        
        # Get BOM Header - prefer consolidated purchasing BOM (PURCH-1.0)
        bom_header = db.query(BOMHeader).filter(
            BOMHeader.product_id == article.id,
            BOMHeader.revision == "PURCH-1.0",
            BOMHeader.is_active == True
        ).first()
        
        if not bom_header:
            # Fall back to any active BOM
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
        
        # Get BOM Details — eagerly load component + its category
        bom_details = (
            db.query(BOMDetail)
            .filter(BOMDetail.bom_header_id == bom_header.id)
            .options(joinedload(BOMDetail.component).joinedload(Product.category))
            .all()
        )
        
        materials = []
        for detail in bom_details:
            component = detail.component
            
            # Calculate total quantity needed
            qty_per_unit = float(detail.qty_needed)
            total_qty = qty_per_unit * quantity
            wastage_pct = float(detail.wastage_percent or 0)
            qty_with_wastage = total_qty * (1 + wastage_pct / 100)
            
            # Determine material category — use DB category name when available
            cat_name = component.category.name if component.category else ''
            material_category = _detect_material_category(component.code, component.name, cat_name)
            
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
                "uom": (
                    component.uom.value
                    if hasattr(component.uom, 'value')
                    else str(component.uom or 'Pcs')
                ),
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
