"""
Service Layer for Daily Production, SPK Modifications & Material Debt
Created: January 26, 2026
Location: app/services/daily_production_service.py

Services:
- DailyProductionService - Daily input recording & progress tracking
- SPKModificationService - SPK edits & audit trail
- MaterialDebtService - Negative inventory & settlement workflow
"""

from datetime import datetime, date
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.core.models import (
    SPK, SPKDailyProduction, SPKProductionCompletion,
    SPKModification, MaterialDebt, MaterialDebtSettlement,
    AuditLog, User, Material
)


class DailyProductionService:
    """Service for daily production tracking and progress calculation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_daily_input(
        self,
        spk_id: int,
        production_date: date,
        input_qty: int,
        user_id: int,
        notes: Optional[str] = None,
        status: str = "CONFIRMED"
    ) -> Dict:
        """
        Record daily production for SPK
        
        Args:
            spk_id: SPK identifier
            production_date: Date of production
            input_qty: Quantity produced today
            user_id: User recording the input
            notes: Optional notes
            status: CONFIRMED, PENDING, REJECTED
        
        Returns:
            Dict with daily_entry and calculated metrics
        """
        # Verify SPK exists
        spk = self.db.query(SPK).filter(SPK.id == spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        # Check for duplicate entry
        existing = self.db.query(SPKDailyProduction).filter(
            SPKDailyProduction.spk_id == spk_id,
            SPKDailyProduction.production_date == production_date
        ).first()
        
        if existing:
            raise ValueError(
                f"Daily production for {production_date} already exists for SPK {spk_id}"
            )
        
        # Calculate cumulative quantity
        cumulative = self._calculate_cumulative(spk_id, input_qty)
        
        # Create daily entry
        daily_entry = SPKDailyProduction(
            spk_id=spk_id,
            production_date=production_date,
            input_qty=input_qty,
            cumulative_qty=cumulative,
            input_by_id=user_id,
            status=status,
            notes=notes
        )
        self.db.add(daily_entry)
        
        # Update SPK
        spk.actual_qty = cumulative
        spk.production_status = "IN_PROGRESS" if cumulative > 0 else "NOT_STARTED"
        
        self.db.commit()
        
        return {
            "daily_entry_id": daily_entry.id,
            "input_qty": input_qty,
            "cumulative_qty": cumulative,
            "target_qty": spk.target_qty,
            "completion_pct": (cumulative / spk.target_qty * 100) if spk.target_qty > 0 else 0
        }
    
    def get_calendar_data(self, spk_id: int) -> Dict:
        """
        Get calendar-style view of daily production
        
        Returns: Dict with all daily entries and progress metrics
        """
        spk = self.db.query(SPK).filter(SPK.id == spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        entries = self.db.query(SPKDailyProduction)\
            .filter(SPKDailyProduction.spk_id == spk_id)\
            .order_by(SPKDailyProduction.production_date.asc())\
            .all()
        
        total_days = len(entries)
        confirmed_qty = sum(e.input_qty for e in entries if e.status == "CONFIRMED")
        pending_qty = sum(e.input_qty for e in entries if e.status == "PENDING")
        
        return {
            "spk_id": spk_id,
            "target_qty": spk.target_qty,
            "actual_qty": spk.actual_qty or 0,
            "daily_entries": [
                {
                    "date": e.production_date.isoformat(),
                    "qty": e.input_qty,
                    "cumulative": e.cumulative_qty,
                    "status": e.status,
                    "notes": e.notes
                }
                for e in entries
            ],
            "summary": {
                "total_days": total_days,
                "confirmed_qty": confirmed_qty,
                "pending_qty": pending_qty,
                "completion_pct": (spk.actual_qty / spk.target_qty * 100) if spk.target_qty > 0 else 0
            }
        }
    
    def get_production_progress(self, spk_id: int) -> Dict:
        """Get production progress details"""
        spk = self.db.query(SPK).filter(SPK.id == spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        entries = self.db.query(SPKDailyProduction)\
            .filter(SPKDailyProduction.spk_id == spk_id).all()
        
        daily_avg = (spk.actual_qty or 0) / len(entries) if entries else 0
        
        return {
            "spk_id": spk_id,
            "target_qty": spk.target_qty,
            "actual_qty": spk.actual_qty or 0,
            "progress_pct": (spk.actual_qty / spk.target_qty * 100) if spk.target_qty > 0 else 0,
            "remaining_qty": max(0, spk.target_qty - (spk.actual_qty or 0)),
            "days_tracked": len(entries),
            "daily_average": daily_avg,
            "estimated_days_remaining": max(0,
                int((spk.target_qty - (spk.actual_qty or 0)) / daily_avg) if daily_avg > 0 else 0
            )
        }
    
    def complete_production(
        self,
        spk_id: int,
        user_id: int,
        confirmation_notes: Optional[str] = None
    ) -> Dict:
        """Mark SPK production as completed"""
        spk = self.db.query(SPK).filter(SPK.id == spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        # Verify target reached
        if (spk.actual_qty or 0) < spk.target_qty:
            raise ValueError(
                f"Cannot complete. Need {spk.target_qty - (spk.actual_qty or 0)} more units"
            )
        
        # Mark as completed
        spk.production_status = "COMPLETED"
        spk.completion_date = date.today()
        
        # Create completion record
        completion = SPKProductionCompletion(
            spk_id=spk_id,
            target_qty=spk.target_qty,
            actual_qty=spk.actual_qty or 0,
            completed_date=spk.completion_date,
            confirmed_by_id=user_id,
            confirmation_notes=confirmation_notes,
            confirmed_at=datetime.utcnow(),
            is_completed=True
        )
        self.db.add(completion)
        self.db.commit()
        
        return {
            "spk_id": spk_id,
            "status": "COMPLETED",
            "completion_date": spk.completion_date.isoformat(),
            "target_qty": spk.target_qty,
            "actual_qty": spk.actual_qty or 0
        }
    
    def _calculate_cumulative(self, spk_id: int, new_qty: int) -> int:
        """Calculate cumulative quantity including new input"""
        last_entry = self.db.query(SPKDailyProduction)\
            .filter(SPKDailyProduction.spk_id == spk_id)\
            .order_by(SPKDailyProduction.production_date.desc())\
            .first()
        
        return (last_entry.cumulative_qty if last_entry else 0) + new_qty


class SPKModificationService:
    """Service for tracking SPK modifications and edits"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def modify_spk_quantity(
        self,
        spk_id: int,
        modified_qty: int,
        modification_reason: str,
        user_id: int,
        allow_negative_inventory: bool = False
    ) -> Dict:
        """
        Modify SPK target quantity
        
        Args:
            spk_id: SPK identifier
            modified_qty: New target quantity
            modification_reason: Reason for modification
            user_id: User making modification
            allow_negative_inventory: Flag for negative inventory workflow
        
        Returns:
            Dict with modification details and status
        """
        spk = self.db.query(SPK).filter(SPK.id == spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        original_qty = spk.target_qty
        
        # Store modification info on SPK
        spk.original_qty = original_qty
        spk.modified_qty = modified_qty
        spk.modification_reason = modification_reason
        spk.modified_by_id = user_id
        spk.modified_at = datetime.utcnow()
        spk.allow_negative_inventory = allow_negative_inventory
        
        # Create audit record
        modification = SPKModification(
            spk_id=spk_id,
            field_name="target_qty",
            old_value=str(original_qty),
            new_value=str(modified_qty),
            modified_by_id=user_id,
            modification_reason=modification_reason
        )
        self.db.add(modification)
        
        # Check if negative inventory approval needed
        qty_increase = modified_qty - original_qty
        material_debt_id = None
        
        if qty_increase > 0 and allow_negative_inventory:
            # Will need warehouse approval
            spk.negative_approval_status = "PENDING"
            # Material debt creation would happen in MaterialDebtService
        
        self.db.commit()
        
        return {
            "spk_id": spk_id,
            "original_qty": original_qty,
            "modified_qty": modified_qty,
            "modification_reason": modification_reason,
            "qty_change": qty_increase,
            "allow_negative_inventory": allow_negative_inventory,
            "negative_approval_status": spk.negative_approval_status
        }
    
    def get_modification_history(self, spk_id: int) -> List[Dict]:
        """Get complete modification history for SPK"""
        modifications = self.db.query(SPKModification)\
            .filter(SPKModification.spk_id == spk_id)\
            .order_by(SPKModification.created_at.desc())\
            .all()
        
        return [
            {
                "field": m.field_name,
                "old_value": m.old_value,
                "new_value": m.new_value,
                "reason": m.modification_reason,
                "modified_by": m.modified_by.username if m.modified_by else None,
                "modified_at": m.created_at.isoformat()
            }
            for m in modifications
        ]
    
    def undo_modification(self, modification_id: int, user_id: int) -> Dict:
        """Undo a specific modification"""
        modification = self.db.query(SPKModification)\
            .filter(SPKModification.id == modification_id).first()
        
        if not modification:
            raise ValueError(f"Modification {modification_id} not found")
        
        # Restore original value
        spk = modification.spk
        if modification.field_name == "target_qty":
            spk.modified_qty = int(modification.old_value)
            spk.modification_reason = f"Undo: {modification.modification_reason}"
            spk.modified_by_id = user_id
            spk.modified_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "message": "Modification undone",
            "spk_id": spk.id,
            "restored_value": modification.old_value
        }


class MaterialDebtService:
    """Service for managing material debt and negative inventory"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_material_debt(
        self,
        spk_id: int,
        material_id: int,
        qty_owed: int,
        reason: str,
        user_id: int
    ) -> Dict:
        """
        Create material debt record for negative inventory
        
        Args:
            spk_id: Associated SPK
            material_id: Material with insufficient stock
            qty_owed: Quantity owed
            reason: Reason for debt (e.g., "SPK qty increased")
            user_id: User creating debt
        
        Returns:
            Dict with debt creation details
        """
        material_debt = MaterialDebt(
            spk_id=spk_id,
            material_id=material_id,
            qty_owed=qty_owed,
            qty_settled=0,
            reason=reason,
            created_by_id=user_id,
            approval_status="PENDING"
        )
        self.db.add(material_debt)
        self.db.commit()
        
        return {
            "debt_id": material_debt.id,
            "spk_id": spk_id,
            "material_id": material_id,
            "qty_owed": qty_owed,
            "approval_status": "PENDING"
        }
    
    def approve_material_debt(
        self,
        debt_id: int,
        approval_decision: str,
        user_id: int,
        approval_reason: Optional[str] = None
    ) -> Dict:
        """
        Approve or reject material debt
        
        Args:
            debt_id: Material debt ID
            approval_decision: "APPROVE" or "REJECT"
            user_id: Approving user
            approval_reason: Reason for decision
        
        Returns:
            Dict with approval status
        """
        debt = self.db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
        if not debt:
            raise ValueError(f"Debt {debt_id} not found")
        
        if approval_decision not in ["APPROVE", "REJECT"]:
            raise ValueError("approval_decision must be APPROVE or REJECT")
        
        debt.approval_status = approval_decision
        debt.approved_by_id = user_id
        debt.approved_at = datetime.utcnow()
        debt.approval_reason = approval_reason
        
        self.db.commit()
        
        return {
            "debt_id": debt_id,
            "approval_status": debt.approval_status,
            "approved_by": self.db.query(User).filter(User.id == user_id).first().username,
            "approved_at": debt.approved_at.isoformat()
        }
    
    def settle_material_debt(
        self,
        debt_id: int,
        qty_settled: int,
        settlement_date: date,
        user_id: int,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Settle material debt (record material arrival)
        
        Args:
            debt_id: Material debt ID
            qty_settled: Quantity settled
            settlement_date: Date material arrived
            user_id: User receiving material
            notes: Settlement notes
        
        Returns:
            Dict with settlement status
        """
        debt = self.db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
        if not debt:
            raise ValueError(f"Debt {debt_id} not found")
        
        # Verify settlement amount
        remaining = debt.qty_owed - debt.qty_settled
        if qty_settled > remaining:
            raise ValueError(f"Cannot settle {qty_settled}. Only {remaining} owed")
        
        # Create settlement record
        settlement = MaterialDebtSettlement(
            material_debt_id=debt_id,
            qty_settled=qty_settled,
            settlement_date=settlement_date,
            received_by_id=user_id,
            settled_by_id=user_id,
            settlement_notes=notes
        )
        self.db.add(settlement)
        
        # Update debt
        debt.qty_settled += qty_settled
        if debt.qty_settled >= debt.qty_owed:
            debt.approval_status = "SETTLED"
        
        self.db.commit()
        
        return {
            "debt_id": debt_id,
            "qty_settled": qty_settled,
            "total_settled": debt.qty_settled,
            "remaining": max(0, debt.qty_owed - debt.qty_settled),
            "approval_status": debt.approval_status,
            "settlement_id": settlement.id
        }
    
    def get_debt_status(self, debt_id: int) -> Dict:
        """Get current debt status and progress"""
        debt = self.db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
        if not debt:
            raise ValueError(f"Debt {debt_id} not found")
        
        settlements = self.db.query(MaterialDebtSettlement)\
            .filter(MaterialDebtSettlement.material_debt_id == debt_id).all()
        
        return {
            "debt_id": debt_id,
            "spk_id": debt.spk_id,
            "qty_owed": debt.qty_owed,
            "qty_settled": debt.qty_settled,
            "approval_status": debt.approval_status,
            "reason": debt.reason,
            "settlements": [
                {
                    "settlement_date": s.settlement_date.isoformat(),
                    "qty_settled": s.qty_settled,
                    "notes": s.settlement_notes
                }
                for s in settlements
            ],
            "approved_by": debt.approved_by.username if debt.approved_by else None,
            "approved_at": debt.approved_at.isoformat() if debt.approved_at else None
        }
    
    def get_pending_approvals(self) -> List[Dict]:
        """Get all pending material debt approvals"""
        debts = self.db.query(MaterialDebt)\
            .filter(MaterialDebt.approval_status == "PENDING")\
            .order_by(MaterialDebt.created_at.asc())\
            .all()
        
        return [
            {
                "debt_id": d.id,
                "spk_id": d.spk_id,
                "qty_owed": d.qty_owed,
                "reason": d.reason,
                "created_by": d.created_by.username if d.created_by else None,
                "created_at": d.created_at.isoformat()
            }
            for d in debts
        ]
