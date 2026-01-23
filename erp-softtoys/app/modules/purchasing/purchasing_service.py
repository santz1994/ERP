"""Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved

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
    """Business logic for Purchasing operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_purchase_orders(
        self,
        status: str | None = None,
        supplier_id: int | None = None
    ) -> list[PurchaseOrder]:
        """Get all purchase orders with filters"""
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
        user_id: int
    ) -> PurchaseOrder:
        """Create new purchase order

        items format: [{"product_id": 1, "quantity": 100, "unit_price": 50000}]
        """
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

        # Create PO
        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=supplier_id,
            order_date=order_date,
            expected_date=expected_date,
            status=POStatus.DRAFT,
            total_amount=total_amount,
            currency="IDR",
            metadata={
                "items": items,
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
        )

        self.db.add(po)

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="CREATE_PURCHASE_ORDER",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes={"po_number": po_number, "supplier": supplier.name, "amount": total_amount}
        )

        self.db.commit()
        self.db.refresh(po)

        return po

    def approve_purchase_order(self, po_id: int, user_id: int) -> PurchaseOrder:
        """Approve purchase order (Manager approval)"""
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
        location_id: int = 1  # Default warehouse location
    ) -> PurchaseOrder:
        """Receive materials from PO

        received_items format: [{"product_id": 1, "quantity": 95, "lot_number": "LOT-001"}]
        """
        po = BaseProductionService.get_purchase_order_optional(self.db, po_id)

        if not po:
            raise ValueError("Purchase Order not found")

        if po.status != POStatus.SENT:
            raise ValueError(f"Cannot receive PO with status {po.status.value}")

        # Process each received item
        for item in received_items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            lot_number = item.get("lot_number", f"LOT-{po.po_number}-{product_id}")

            # Create stock lot for traceability
            stock_lot = StockLot(
                lot_number=lot_number,
                product_id=product_id,
                quantity=quantity,
                purchase_order_id=po.id,
                expiry_date=None,  # Set if applicable
                status="Active"
            )
            self.db.add(stock_lot)

            # Create stock move (incoming)
            stock_move = StockMove(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity,
                move_type="IN",
                reference=f"PO/{po.po_number}",
                move_date=datetime.utcnow(),
                user_id=user_id
            )
            self.db.add(stock_move)

            # Update or create stock quant
            stock_quant = self.db.query(StockQuant).filter(
                and_(
                    StockQuant.product_id == product_id,
                    StockQuant.location_id == location_id,
                    StockQuant.lot_id == stock_lot.id
                )
            ).first()

            if stock_quant:
                stock_quant.quantity_on_hand += quantity
            else:
                stock_quant = StockQuant(
                    product_id=product_id,
                    location_id=location_id,
                    lot_id=stock_lot.id,
                    quantity_on_hand=quantity,
                    quantity_reserved=0
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
        """Cancel purchase order"""
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
        """Get supplier performance metrics"""
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
