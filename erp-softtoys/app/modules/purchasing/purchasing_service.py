"""Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved.

Purchasing Service - Raw Material Procurement Business Logic
Handles PO creation, approval, receiving, and stock updates
"""

from datetime import date, datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.base_production_service import BaseProductionService
from app.core.models.products import Product, ProductType
from app.core.models.warehouse import POStatus, PurchaseOrder, StockLot, StockMove, StockQuant
from app.shared.audit import log_audit


class PurchasingService:
    """Business logic for Purchasing operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_purchase_orders(
        self,
        status: str | None = None,
        supplier_id: int | None = None
    ) -> list[PurchaseOrder]:
        """Get all purchase orders with filters."""
        query = self.db.query(PurchaseOrder)

        if status:
            query = query.filter(PurchaseOrder.status == status)

        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)

        return query.order_by(PurchaseOrder.order_date.desc()).all()

    def create_purchase_order(
        self,
        po_number: str,
        supplier_id: int,
        order_date: date,
        expected_date: date,
        items: list[dict],
        user_id: int,
        # 🆕 PO REFERENCE SYSTEM FIELDS (Feb 6, 2026)
        po_type=None,
        source_po_kain_id: int | None = None,
        article_id: int | None = None,
        article_qty: int | None = None,
        week: str | None = None,
        destination: str | None = None,
        linked_mo_id: int | None = None
    ) -> PurchaseOrder:
        """Create new purchase order with PO Reference System support.
        
        🆕 PO Reference System (Feb 6, 2026):
        - PO KAIN (Fabric) - TRIGGER 1: Enables Cutting/Embroidery
        - PO LABEL - TRIGGER 2: Full MO Release + Week/Destination inheritance
        - PO ACCESSORIES - Optional reference to PO KAIN

        items format: [{"product_id": 1, "quantity": 100, "unit_price": 50000}]
        """
        # Import POType here to avoid circular import
        from app.core.models.warehouse import POType
        
        # Validate supplier exists
        from app.core.models.sales import Partner, PartnerType
        supplier = self.db.query(Partner).filter(
            and_(
                Partner.id == supplier_id,
                Partner.type == PartnerType.SUPPLIER
            )
        ).first()

        if not supplier:
            raise ValueError("Supplier not found")

        # Validate all products are raw materials
        product_ids = [item["product_id"] for item in items]
        products = self.db.query(Product).filter(Product.id.in_(product_ids)).all()

        for product in products:
            if product.type != ProductType.RAW_MATERIAL:
                raise ValueError(f"Product {product.code} is not a raw material")

        # Calculate total amount
        total_amount = sum(item["quantity"] * item["unit_price"] for item in items)

        # Create PO with PO Reference System fields
        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=supplier_id,
            order_date=order_date,
            expected_date=expected_date,
            status=POStatus.DRAFT,
            total_amount=total_amount,
            currency="IDR",
            # 🆕 PO Reference System fields
            po_type=po_type or POType.ACCESSORIES,
            source_po_kain_id=source_po_kain_id,
            article_id=article_id,
            article_qty=article_qty,
            week=week,
            destination=destination,
            linked_mo_id=linked_mo_id,
            metadata={
                "items": items,
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
        )

        self.db.add(po)

        # Audit log with PO Reference System info
        audit_changes = {
            "po_number": po_number, 
            "supplier": supplier.name, 
            "amount": total_amount,
            "po_type": po_type.value if po_type else "ACCESSORIES"
        }
        
        if source_po_kain_id:
            audit_changes["source_po_kain_id"] = source_po_kain_id
        if article_id:
            audit_changes["article_id"] = article_id
        if week:
            audit_changes["week"] = week
        if destination:
            audit_changes["destination"] = destination
        
        log_audit(
            self.db,
            user_id=user_id,
            action="CREATE_PURCHASE_ORDER",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes=audit_changes
        )

        self.db.commit()
        self.db.refresh(po)

        return po

    def approve_purchase_order(self, po_id: int, user_id: int) -> PurchaseOrder:
        """Approve purchase order (Manager approval)."""
        po = BaseProductionService.get_purchase_order_optional(self.db, po_id)

        if not po:
            raise ValueError("Purchase Order not found")

        if po.status != POStatus.DRAFT:
            raise ValueError(f"Cannot approve PO with status {po.status.value}")

        po.status = POStatus.SENT
        po.approved_by = user_id
        po.approved_at = datetime.utcnow()

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="APPROVE_PURCHASE_ORDER",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes={"status": "SENT", "approved_by": user_id}
        )

        self.db.commit()
        self.db.refresh(po)

        return po

    def receive_purchase_order(
        self,
        po_id: int,
        received_items: list[dict],
        user_id: int,
        location_id: int = 1  # Default warehouse location (to)
    ) -> PurchaseOrder:
        """Receive materials from PO — creates StockLot, StockMove, StockQuant.

        received_items format: [{"product_id": 1, "quantity": 95, "lot_number": "LOT-001", "uom": "PCS"}]
        """
        from app.core.models.warehouse import Location, LocationType, StockMoveStatus

        po = BaseProductionService.get_purchase_order_optional(self.db, po_id)

        if not po:
            raise ValueError("Purchase Order not found")

        if po.status not in (POStatus.SENT, POStatus.DRAFT):
            raise ValueError(f"Cannot receive PO with status {po.status.value}")

        # Ensure a "Virtual/Supplier" (from) location exists
        supplier_loc = self.db.query(Location).filter(
            Location.name == "Virtual/Supplier"
        ).first()
        if not supplier_loc:
            supplier_loc = Location(
                name="Virtual/Supplier",
                type=LocationType.SUPPLIER,
                is_active=True,
            )
            self.db.add(supplier_loc)
            self.db.flush()

        # Ensure the destination (to) location exists — fallback by id
        wh_loc = self.db.query(Location).filter(Location.id == location_id).first()
        if not wh_loc:
            wh_loc = self.db.query(Location).filter(
                Location.type == LocationType.INTERNAL
            ).first()
        if not wh_loc:
            wh_loc = Location(
                name="Warehouse/Stock",
                type=LocationType.INTERNAL,
                is_active=True,
            )
            self.db.add(wh_loc)
            self.db.flush()

        now = datetime.utcnow()

        # Process each received item
        for item in received_items:
            product_id = item["product_id"]
            quantity = float(item.get("quantity") or 0)
            uom = str(item.get("uom") or "PCS")
            lot_number = item.get("lot_number") or f"LOT-{po.po_number}-{product_id}-{now.strftime('%Y%m%d%H%M%S')}"

            if quantity <= 0:
                continue

            # Create stock lot for traceability
            stock_lot = StockLot(
                lot_number=lot_number,
                product_id=product_id,
                qty_initial=quantity,
                qty_remaining=quantity,
                supplier_id=po.supplier_id,
                purchase_order_id=po.id,
                received_date=now,
            )
            self.db.add(stock_lot)
            self.db.flush()  # Need lot.id for StockMove FK

            # Create stock move (Supplier → Warehouse incoming)
            stock_move = StockMove(
                product_id=product_id,
                qty=quantity,
                uom=uom,
                location_id_from=supplier_loc.id,
                location_id_to=wh_loc.id,
                reference_doc=f"PO/{po.po_number}",
                state=StockMoveStatus.DONE,
                lot_id=stock_lot.id,
            )
            self.db.add(stock_move)

            # Update or create stock quant (aggregate per product+location)
            stock_quant = self.db.query(StockQuant).filter(
                and_(
                    StockQuant.product_id == product_id,
                    StockQuant.location_id == wh_loc.id,
                )
            ).first()

            if stock_quant:
                stock_quant.qty_on_hand += quantity
            else:
                stock_quant = StockQuant(
                    product_id=product_id,
                    location_id=wh_loc.id,
                    lot_id=stock_lot.id,
                    qty_on_hand=quantity,
                    qty_reserved=0,
                )
                self.db.add(stock_quant)

        # Update PO status
        po.status = POStatus.RECEIVED
        po.received_by = user_id
        po.received_at = datetime.utcnow()

        if not po.metadata:
            po.metadata = {}
        po.metadata["received_items"] = received_items

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="RECEIVE_PURCHASE_ORDER",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes={"status": "RECEIVED", "received_by": user_id}
        )

        self.db.commit()
        self.db.refresh(po)

        return po

    def cancel_purchase_order(self, po_id: int, reason: str, user_id: int) -> PurchaseOrder:
        """Cancel purchase order."""
        po = BaseProductionService.get_purchase_order_optional(self.db, po_id)

        if not po:
            raise ValueError("Purchase Order not found")

        if po.status in [POStatus.RECEIVED, POStatus.DONE]:
            raise ValueError(f"Cannot cancel PO with status {po.status.value}")

        po.status = POStatus.CANCELLED

        if not po.metadata:
            po.metadata = {}
        po.metadata["cancellation"] = {
            "reason": reason,
            "cancelled_by": user_id,
            "cancelled_at": datetime.utcnow().isoformat()
        }

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="CANCEL_PURCHASE_ORDER",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes={"status": "CANCELLED", "reason": reason}
        )

        self.db.commit()
        self.db.refresh(po)

        return po

    def get_supplier_performance(self, supplier_id: int) -> dict:
        """Get supplier performance metrics."""
        # Note: This uses .filter() for filtering, handled separately from simple get_*() helpers
        pos = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.supplier_id == supplier_id
        ).all()

        total_pos = len(pos)
        completed = len([po for po in pos if po.status == POStatus.DONE])
        on_time = len([po for po in pos if po.received_at and po.received_at <= po.expected_date])

        return {
            "supplier_id": supplier_id,
            "total_purchase_orders": total_pos,
            "completed_orders": completed,
            "on_time_delivery": on_time,
            "on_time_rate": (on_time / total_pos * 100) if total_pos > 0 else 0,
            "completion_rate": (completed / total_pos * 100) if total_pos > 0 else 0
        }
