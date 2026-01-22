"""
Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved

Finishgoods Service - Finished Goods Warehouse Management
Handles FG receiving from packing, storage, inventory monitoring, and shipping preparation
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.core.models.transfer import TransferLog
from app.core.models.warehouse import StockMove, StockQuant, Location
from app.core.models.products import Product, ProductType
from app.core.models.manufacturing import ManufacturingOrder
from app.core.schemas import MOStatus
from app.shared.audit import log_audit
from app.core.base_production_service import BaseProductionService


class FinishgoodsService:
    """Business logic for Finishgoods Warehouse operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_finished_goods_inventory(
        self,
        product_code: Optional[str] = None,
        low_stock_only: bool = False
    ) -> List[dict]:
        """Get finished goods inventory with stock levels"""
        query = self.db.query(
            Product,
            func.sum(StockQuant.qty_on_hand).label('total_quantity')
        ).join(
            StockQuant, StockQuant.product_id == Product.id
        ).join(
            Location, Location.id == StockQuant.location_id
        ).filter(
            and_(
                Product.type == ProductType.FINISH_GOOD,
                Location.name.like('%Finish%')  # FG Warehouse locations
            )
        ).group_by(Product.id)
        
        if product_code:
            query = query.filter(Product.code.like(f'%{product_code}%'))
        
        results = query.all()
        
        inventory = []
        for product, total_qty in results:
            if low_stock_only and total_qty >= product.min_stock:
                continue
            
            inventory.append({
                "product_id": product.id,
                "product_code": product.code,
                "product_name": product.name,
                "qty_on_hand": total_qty,
                "min_stock": product.min_stock,
                "stock_status": "Low Stock" if total_qty < product.min_stock else "Adequate",
                "uom": product.uom
            })
        
        return inventory

    def receive_from_packing(
        self,
        transfer_id: int,
        user_id: int,
        fg_location_id: int = 2  # Default FG warehouse location
    ) -> TransferLog:
        """
        Receive finished goods from Packing department
        
        - Validates transfer from Packing
        - Creates stock movement
        - Updates FG inventory
        - Marks transfer as completed
        """
        transfer = self.db.query(TransferLog).filter(
            TransferLog.id == transfer_id
        ).first()
        
        if not transfer:
            raise ValueError("Transfer not found")
        
        if transfer.from_department != "Packing":
            raise ValueError("Can only receive transfers from Packing department")
        
        if transfer.status == "Completed":
            raise ValueError("Transfer already completed")
        
        # Create stock move for FG receipt
        stock_move = StockMove(
            product_id=transfer.product_id,
            location_id=fg_location_id,
            quantity=transfer.transfer_qty,
            move_type="IN",
            reference=f"Transfer/{transfer.id}/Packing-to-FG",
            move_date=datetime.utcnow(),
            user_id=user_id
        )
        self.db.add(stock_move)
        
        # Update or create stock quant
        stock_quant = self.db.query(StockQuant).filter(
            and_(
                StockQuant.product_id == transfer.product_id,
                StockQuant.location_id == fg_location_id
            )
        ).first()
        
        if stock_quant:
            stock_quant.qty_on_hand += transfer.transfer_qty
        else:
            stock_quant = StockQuant(
                product_id=transfer.product_id,
                location_id=fg_location_id,
                qty_on_hand=transfer.transfer_qty,
                quantity_reserved=0
            )
            self.db.add(stock_quant)
        
        # Mark transfer as completed
        transfer.status = "Completed"
        transfer.acknowledged_by = user_id
        transfer.acknowledged_at = datetime.utcnow()
        
        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="RECEIVE_FINISHGOODS",
            entity_type="TransferLog",
            entity_id=transfer.id,
            changes={
                "from": "Packing",
                "to": "FinishGoods",
                "qty": transfer.transfer_qty,
                "status": "Completed"
            }
        )
        
        self.db.commit()
        self.db.refresh(transfer)
        
        return transfer

    def prepare_shipment(
        self,
        product_id: int,
        quantity: int,
        destination: str,
        shipping_marks: List[str],
        user_id: int
    ) -> dict:
        """
        Prepare finished goods for shipment
        
        - Validates stock availability
        - Reserves stock for shipment
        - Creates shipping preparation record
        """
        # Check stock availability
        fg_location = self.db.query(Location).filter(
            Location.name.like('%Finish%')
        ).first()
        
        if not fg_location:
            raise ValueError("Finished Goods location not found")
        
        stock_quant = self.db.query(StockQuant).filter(
            and_(
                StockQuant.product_id == product_id,
                StockQuant.location_id == fg_location.id
            )
        ).first()
        
        if not stock_quant:
            raise ValueError("Product not found in Finished Goods warehouse")
        
        available_qty = stock_quant.qty_on_hand - stock_quant.quantity_reserved
        
        if available_qty < quantity:
            raise ValueError(
                f"Insufficient stock. Available: {available_qty}, Requested: {quantity}"
            )
        
        # Reserve stock
        stock_quant.quantity_reserved += quantity
        
        # Create shipment preparation record
        shipment = {
            "product_id": product_id,
            "quantity": quantity,
            "destination": destination,
            "shipping_marks": shipping_marks,
            "prepared_by": user_id,
            "prepared_at": datetime.utcnow().isoformat(),
            "status": "Ready for Shipment"
        }
        
        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="PREPARE_SHIPMENT",
            entity_type="FinishGoods",
            entity_id=product_id,
            changes=shipment
        )
        
        self.db.commit()
        
        return shipment

    def ship_finishgoods(
        self,
        product_id: int,
        quantity: int,
        user_id: int,
        fg_location_id: int = 2
    ) -> dict:
        """
        Ship finished goods (reduce FG inventory)
        
        - Creates outbound stock movement
        - Updates FG inventory
        - Releases reserved stock
        """
        stock_quant = self.db.query(StockQuant).filter(
            and_(
                StockQuant.product_id == product_id,
                StockQuant.location_id == fg_location_id
            )
        ).first()
        
        if not stock_quant:
            raise ValueError("Product not found in Finished Goods warehouse")
        
        if stock_quant.qty_on_hand < quantity:
            raise ValueError("Insufficient stock for shipment")
        
        # Create outbound stock move
        stock_move = StockMove(
            product_id=product_id,
            location_id=fg_location_id,
            quantity=-quantity,  # Negative for outbound
            move_type="OUT",
            reference=f"Shipment/FG/{product_id}",
            move_date=datetime.utcnow(),
            user_id=user_id
        )
        self.db.add(stock_move)
        
        # Update stock quant
        stock_quant.qty_on_hand -= quantity
        if stock_quant.quantity_reserved >= quantity:
            stock_quant.quantity_reserved -= quantity
        
        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="SHIP_FINISHGOODS",
            entity_type="StockMove",
            entity_id=stock_move.id,
            changes={
                "product_id": product_id,
                "quantity": quantity,
                "type": "Shipment"
            }
        )
        
        self.db.commit()
        
        return {
            "product_id": product_id,
            "shipped_quantity": quantity,
            "remaining_stock": stock_quant.qty_on_hand,
            "shipped_at": datetime.utcnow().isoformat()
        }

    def get_shipment_ready_products(self) -> List[dict]:
        """Get list of products ready for shipment"""
        # Get completed MOs
        completed_mos = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.state == MOStatus.DONE
        ).all()
        
        ready_products = []
        for mo in completed_mos:
            product = BaseProductionService.get_product_optional(self.db, mo.product_id)
            if product:
                stock = self.db.query(StockQuant).filter(
                    StockQuant.product_id == product.id
                ).first()
                
                if stock and stock.qty_on_hand > 0:
                    ready_products.append({
                        "mo_id": mo.id,
                        "product_code": product.code,
                        "product_name": product.name,
                        "quantity_available": stock.qty_on_hand,
                        "quantity_reserved": stock.quantity_reserved,
                        "destination": mo.metadata.get("destination", "Unknown") if mo.metadata else "Unknown"
                    })
        
        return ready_products

    def get_stock_aging(self) -> List[dict]:
        """Get finished goods stock aging analysis"""
        stock_moves = self.db.query(StockMove).filter(
            and_(
                StockMove.move_type == "IN",
                StockMove.reference.like('%Packing%')
            )
        ).order_by(StockMove.move_date.desc()).all()
        
        aging_data = []
        for move in stock_moves:
            days_in_stock = (datetime.utcnow() - move.move_date).days
            product = BaseProductionService.get_product_optional(self.db, move.product_id)
            
            if product:
                aging_data.append({
                    "product_code": product.code,
                    "product_name": product.name,
                    "received_date": move.move_date.isoformat(),
                    "days_in_stock": days_in_stock,
                    "aging_category": (
                        "Fresh" if days_in_stock < 7 else
                        "Normal" if days_in_stock < 14 else
                        "Aging" if days_in_stock < 30 else
                        "Old Stock"
                    )
                })
        
        return aging_data

