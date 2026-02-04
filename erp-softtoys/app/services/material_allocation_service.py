"""
Material Allocation Service - Week 3 Implementation
Auto-allocate materials when Work Order is generated
Auto-deduct stock when WO starts
Material shortage alerts

Author: IT Developer Expert
Date: 4 Februari 2026
Motto: "Kegagalan adalah kesuksesan yang tertunda!"
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.models.manufacturing import WorkOrder, WorkOrderStatus, SPKMaterialAllocation
from app.core.models.bom import BOMDetail
from app.core.models.warehouse import StockQuant, Location, StockMove, StockMoveStatus
from app.core.models.products import Product


class MaterialShortageAlert:
    """Material shortage alert data structure"""
    
    def __init__(
        self,
        material_id: int,
        material_code: str,
        material_name: str,
        required_qty: Decimal,
        available_qty: Decimal,
        shortage_qty: Decimal,
        wo_id: int,
        department: str
    ):
        self.material_id = material_id
        self.material_code = material_code
        self.material_name = material_name
        self.required_qty = required_qty
        self.available_qty = available_qty
        self.shortage_qty = shortage_qty
        self.wo_id = wo_id
        self.department = department
        self.severity = self._calculate_severity()
    
    def _calculate_severity(self) -> str:
        """Calculate alert severity based on shortage percentage"""
        shortage_pct = (self.shortage_qty / self.required_qty) * 100
        
        if shortage_pct >= 50:
            return "CRITICAL"  # Missing 50%+ of required material
        elif shortage_pct >= 20:
            return "HIGH"      # Missing 20-50%
        elif shortage_pct >= 5:
            return "MEDIUM"    # Missing 5-20%
        else:
            return "LOW"       # Missing <5%
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "material_id": self.material_id,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "required_qty": float(self.required_qty),
            "available_qty": float(self.available_qty),
            "shortage_qty": float(self.shortage_qty),
            "shortage_pct": float((self.shortage_qty / self.required_qty) * 100),
            "wo_id": self.wo_id,
            "department": self.department,
            "severity": self.severity
        }


class MaterialAllocationService:
    """
    Service for material allocation and warehouse integration
    
    Features:
    1. Auto-allocate materials when WO is generated
    2. Reserve stock for WO (soft reservation)
    3. Deduct stock when WO starts (hard deduction)
    4. Material shortage alerts
    5. FIFO stock allocation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.warehouse_main_location = self._get_warehouse_main_location()
    
    def _get_warehouse_main_location(self) -> Optional[Location]:
        """Get Warehouse Main location"""
        return self.db.query(Location).filter(
            and_(
                Location.name.like('%Warehouse Main%'),
                Location.type == 'INTERNAL'
            )
        ).first()
    
    def allocate_materials_for_wo(
        self,
        wo: WorkOrder,
        bom_details: List[BOMDetail],
        check_availability: bool = True
    ) -> Tuple[List[SPKMaterialAllocation], List[MaterialShortageAlert]]:
        """
        Allocate materials for a Work Order based on BOM
        
        Args:
            wo: Work Order object
            bom_details: List of BOM details (materials needed)
            check_availability: Whether to check stock availability
        
        Returns:
            Tuple of (allocations, shortage_alerts)
        """
        
        print(f"\n🔄 Allocating materials for WO {wo.id} - {wo.department.value}...")
        
        allocations = []
        shortage_alerts = []
        
        for bom_detail in bom_details:
            # Calculate required quantity based on WO target
            required_qty = bom_detail.quantity * wo.target_qty
            
            # Get available stock
            available_qty = self._get_available_stock(bom_detail.material_id)
            
            # Check if shortage
            if check_availability and available_qty < required_qty:
                shortage_qty = required_qty - available_qty
                
                material = self.db.query(Product).filter_by(id=bom_detail.material_id).first()
                
                alert = MaterialShortageAlert(
                    material_id=bom_detail.material_id,
                    material_code=material.code if material else "UNKNOWN",
                    material_name=material.name if material else "Unknown Material",
                    required_qty=required_qty,
                    available_qty=available_qty,
                    shortage_qty=shortage_qty,
                    wo_id=wo.id,
                    department=wo.department.value
                )
                
                shortage_alerts.append(alert)
                
                print(f"   ⚠️ SHORTAGE: {alert.material_code} - Need {required_qty}, Have {available_qty}")
            
            # Create allocation record (reservation)
            allocation = SPKMaterialAllocation(
                wo_id=wo.id,
                material_id=bom_detail.material_id,
                qty_allocated=required_qty,
                qty_consumed=Decimal('0'),
                uom_id=bom_detail.uom_id,
                is_reserved=True,
                is_consumed=False,
                allocated_at=datetime.utcnow()
            )
            
            self.db.add(allocation)
            allocations.append(allocation)
            
            material = self.db.query(Product).filter_by(id=bom_detail.material_id).first()
            print(f"   ✅ Allocated: {material.code if material else 'N/A'} - {required_qty} {bom_detail.uom.name if bom_detail.uom else 'pcs'}")
        
        self.db.flush()
        
        print(f"\n   📊 Total: {len(allocations)} materials allocated")
        if shortage_alerts:
            print(f"   ⚠️ {len(shortage_alerts)} materials in shortage!")
        
        return allocations, shortage_alerts
    
    def _get_available_stock(self, material_id: int) -> Decimal:
        """
        Get available stock for a material (FIFO-based)
        
        Args:
            material_id: Material product ID
        
        Returns:
            Total available quantity
        """
        
        if not self.warehouse_main_location:
            return Decimal('0')
        
        # Sum all stock quants for this material at Warehouse Main
        total = self.db.query(func.sum(StockQuant.quantity)).filter(
            and_(
                StockQuant.product_id == material_id,
                StockQuant.location_id == self.warehouse_main_location.id,
                StockQuant.quantity > 0
            )
        ).scalar()
        
        return total or Decimal('0')
    
    def deduct_stock_on_wo_start(
        self,
        wo: WorkOrder,
        force: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Deduct stock from warehouse when WO starts (hard deduction)
        
        Args:
            wo: Work Order object
            force: Force deduction even if shortage exists (debt system)
        
        Returns:
            Tuple of (success, error_messages)
        """
        
        print(f"\n💰 Deducting stock for WO {wo.id} - {wo.department.value}...")
        
        errors = []
        
        # Get all allocated materials
        allocations = self.db.query(SPKMaterialAllocation).filter_by(
            wo_id=wo.id,
            is_consumed=False
        ).all()
        
        if not allocations:
            return False, ["No material allocations found for this WO"]
        
        for allocation in allocations:
            # Check stock availability
            available = self._get_available_stock(allocation.material_id)
            
            if available < allocation.qty_allocated and not force:
                material = self.db.query(Product).filter_by(id=allocation.material_id).first()
                error_msg = f"Insufficient stock for {material.code if material else 'N/A'}: need {allocation.qty_allocated}, have {available}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                continue
            
            # Perform FIFO deduction
            success, deduction_errors = self._deduct_stock_fifo(
                material_id=allocation.material_id,
                qty_to_deduct=allocation.qty_allocated,
                wo_id=wo.id,
                force=force
            )
            
            if not success:
                errors.extend(deduction_errors)
                continue
            
            # Mark allocation as consumed
            allocation.is_consumed = True
            allocation.qty_consumed = allocation.qty_allocated
            allocation.consumed_at = datetime.utcnow()
            
            material = self.db.query(Product).filter_by(id=allocation.material_id).first()
            print(f"   ✅ Deducted: {material.code if material else 'N/A'} - {allocation.qty_allocated}")
        
        if errors:
            print(f"\n   ⚠️ {len(errors)} deduction errors occurred")
            return False, errors
        
        self.db.flush()
        print(f"\n   🎉 All materials successfully deducted!")
        
        return True, []
    
    def _deduct_stock_fifo(
        self,
        material_id: int,
        qty_to_deduct: Decimal,
        wo_id: int,
        force: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Deduct stock using FIFO (First In, First Out) method
        
        Args:
            material_id: Material product ID
            qty_to_deduct: Quantity to deduct
            wo_id: Work Order ID (for traceability)
            force: Allow negative stock (debt system)
        
        Returns:
            Tuple of (success, error_messages)
        """
        
        if not self.warehouse_main_location:
            return False, ["Warehouse Main location not found"]
        
        # Get stock quants ordered by creation date (FIFO)
        from sqlalchemy import func
        stock_quants = self.db.query(StockQuant).filter(
            and_(
                StockQuant.product_id == material_id,
                StockQuant.location_id == self.warehouse_main_location.id,
                StockQuant.quantity > 0
            )
        ).order_by(StockQuant.created_at.asc()).all()
        
        remaining_to_deduct = qty_to_deduct
        deducted_lots = []
        
        # Deduct from oldest lots first (FIFO)
        for quant in stock_quants:
            if remaining_to_deduct <= 0:
                break
            
            # Deduct from this lot
            deduct_from_lot = min(quant.quantity, remaining_to_deduct)
            
            quant.quantity -= deduct_from_lot
            remaining_to_deduct -= deduct_from_lot
            
            deducted_lots.append({
                'lot_id': quant.lot_id,
                'qty': deduct_from_lot
            })
            
            # Create stock move record for traceability
            self._create_stock_move(
                product_id=material_id,
                qty=deduct_from_lot,
                from_location=self.warehouse_main_location,
                to_location=None,  # Consumed by production
                lot_id=quant.lot_id,
                reference=f"WO-{wo_id}"
            )
        
        # If still remaining and force=True, create debt
        if remaining_to_deduct > 0:
            if force:
                # Create negative stock entry (debt)
                print(f"      ⚠️ Creating debt: {remaining_to_deduct}")
                
                # Create negative quant
                debt_quant = StockQuant(
                    product_id=material_id,
                    location_id=self.warehouse_main_location.id,
                    quantity=-remaining_to_deduct,
                    lot_id=None
                )
                self.db.add(debt_quant)
                
                # Create stock move for debt
                self._create_stock_move(
                    product_id=material_id,
                    qty=remaining_to_deduct,
                    from_location=self.warehouse_main_location,
                    to_location=None,
                    lot_id=None,
                    reference=f"WO-{wo_id}-DEBT"
                )
                
            else:
                return False, [f"Insufficient stock: still need {remaining_to_deduct} more"]
        
        return True, []
    
    def _create_stock_move(
        self,
        product_id: int,
        qty: Decimal,
        from_location: Optional[Location],
        to_location: Optional[Location],
        lot_id: Optional[int],
        reference: str
    ):
        """Create stock move record for traceability"""
        
        move = StockMove(
            product_id=product_id,
            quantity=qty,
            source_location_id=from_location.id if from_location else None,
            destination_location_id=to_location.id if to_location else None,
            lot_id=lot_id,
            reference=reference,
            status=StockMoveStatus.DONE,
            move_date=datetime.utcnow()
        )
        
        self.db.add(move)
    
    def get_material_shortage_alerts(
        self,
        mo_id: Optional[int] = None,
        department: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[MaterialShortageAlert]:
        """
        Get material shortage alerts with filtering
        
        Args:
            mo_id: Filter by Manufacturing Order
            department: Filter by department
            severity: Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)
        
        Returns:
            List of MaterialShortageAlert objects
        """
        
        from app.core.models.manufacturing import ManufacturingOrder
        
        # Get all WOs
        query = self.db.query(WorkOrder)
        
        if mo_id:
            query = query.filter_by(mo_id=mo_id)
        
        if department:
            query = query.filter_by(department=department)
        
        work_orders = query.all()
        
        all_alerts = []
        
        for wo in work_orders:
            # Get allocations
            allocations = self.db.query(SPKMaterialAllocation).filter_by(
                wo_id=wo.id,
                is_consumed=False
            ).all()
            
            for allocation in allocations:
                available = self._get_available_stock(allocation.material_id)
                
                if available < allocation.qty_allocated:
                    material = self.db.query(Product).filter_by(id=allocation.material_id).first()
                    
                    alert = MaterialShortageAlert(
                        material_id=allocation.material_id,
                        material_code=material.code if material else "UNKNOWN",
                        material_name=material.name if material else "Unknown",
                        required_qty=allocation.qty_allocated,
                        available_qty=available,
                        shortage_qty=allocation.qty_allocated - available,
                        wo_id=wo.id,
                        department=wo.department.value
                    )
                    
                    # Filter by severity
                    if severity is None or alert.severity == severity:
                        all_alerts.append(alert)
        
        # Sort by severity (CRITICAL first)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_alerts.sort(key=lambda x: severity_order.get(x.severity, 99))
        
        return all_alerts
    
    def check_wo_can_start(self, wo: WorkOrder) -> Tuple[bool, List[str]]:
        """
        Check if Work Order can start (all materials available)
        
        Args:
            wo: Work Order object
        
        Returns:
            Tuple of (can_start, blocking_reasons)
        """
        
        blocking_reasons = []
        
        # Check material allocations
        allocations = self.db.query(SPKMaterialAllocation).filter_by(
            wo_id=wo.id
        ).all()
        
        if not allocations:
            blocking_reasons.append("No materials allocated")
            return False, blocking_reasons
        
        # Check each material availability
        for allocation in allocations:
            available = self._get_available_stock(allocation.material_id)
            
            if available < allocation.qty_allocated:
                material = self.db.query(Product).filter_by(id=allocation.material_id).first()
                shortage = allocation.qty_allocated - available
                blocking_reasons.append(
                    f"{material.code if material else 'Material'}: shortage {shortage} (need {allocation.qty_allocated}, have {available})"
                )
        
        can_start = len(blocking_reasons) == 0
        
        return can_start, blocking_reasons


# Helper functions for API endpoints

def allocate_materials_for_mo(db: Session, mo_id: int) -> Dict:
    """
    Allocate materials for all Work Orders in a Manufacturing Order
    
    Returns summary with shortage alerts
    """
    
    from app.core.models.manufacturing import ManufacturingOrder
    
    service = MaterialAllocationService(db)
    
    mo = db.query(ManufacturingOrder).filter_by(id=mo_id).first()
    if not mo:
        raise ValueError(f"Manufacturing Order {mo_id} not found")
    
    work_orders = mo.work_orders
    
    total_allocations = 0
    all_shortage_alerts = []
    
    for wo in work_orders:
        # Get BOM details for this WO
        # This assumes BOM explosion already happened
        allocations, shortage_alerts = service.allocate_materials_for_wo(
            wo=wo,
            bom_details=[],  # Would be populated from BOM explosion
            check_availability=True
        )
        
        total_allocations += len(allocations)
        all_shortage_alerts.extend(shortage_alerts)
    
    db.commit()
    
    return {
        "success": True,
        "mo_id": mo_id,
        "total_work_orders": len(work_orders),
        "total_allocations": total_allocations,
        "shortage_alerts": [alert.to_dict() for alert in all_shortage_alerts],
        "has_shortages": len(all_shortage_alerts) > 0
    }
