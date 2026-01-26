# ⚙️ SESSION 31 - EDITABLE SPK & NEGATIVE INVENTORY WITH APPROVAL WORKFLOW

**Feature**: Production SPK Editing + Negative Inventory Management  
**Status**: Specification Complete | **Implementation**: Ready  

---

## 📋 OVERVIEW

This feature enables:
1. **Editable SPK** - PPIC/Manager can modify production quantities after creation
2. **Negative Inventory** - Allow production to start even without materials (defer fulfillment)
3. **Approval Workflow** - Multi-level approval for negative stock scenarios
4. **Debt Tracking** - Track material shortfall and reconciliation
5. **Audit Logging** - Complete traceability of all changes

---

## 🏗️ ARCHITECTURE

### Database Schema

#### 1. Enhanced SPK Model
```sql
ALTER TABLE spks ADD COLUMN (
    original_qty INT,                    -- Original target qty
    modified_qty INT,                    -- Modified target qty (if edited)
    modification_reason VARCHAR(255),    -- Why was it modified?
    modified_by_id INT FOREIGN KEY,      -- Who modified it
    modified_at TIMESTAMP,               -- When was it modified?
    allow_negative_inventory BOOLEAN DEFAULT FALSE,
    negative_approval_status VARCHAR(50),  -- PENDING, APPROVED, REJECTED
    negative_approved_by_id INT FOREIGN KEY,
    negative_approved_at TIMESTAMP
);

-- Create audit trail for SPK changes
CREATE TABLE spk_modifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    spk_id INT FOREIGN KEY REFERENCES spks(id),
    field_name VARCHAR(50),          -- 'qty', 'allow_negative', etc.
    old_value VARCHAR(255),
    new_value VARCHAR(255),
    modified_by_id INT FOREIGN KEY REFERENCES users(id),
    modification_reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_spk_id (spk_id),
    INDEX idx_modified_at (created_at)
);
```

#### 2. Material Debt Model
```sql
CREATE TABLE material_debts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    spk_id INT FOREIGN KEY REFERENCES spks(id),
    material_id INT FOREIGN KEY REFERENCES materials(id),
    qty_owed DECIMAL(10, 2),             -- Negative inventory amount
    qty_settled DECIMAL(10, 2) DEFAULT 0,
    qty_pending DECIMAL(10, 2),          -- (qty_owed - qty_settled)
    status VARCHAR(50),                  -- PENDING, PARTIAL, SETTLED, OVERDUE
    approval_status VARCHAR(50),         -- PENDING_APPROVAL, APPROVED, REJECTED
    created_at TIMESTAMP DEFAULT NOW(),
    created_by_id INT FOREIGN KEY REFERENCES users(id),
    approved_by_id INT FOREIGN KEY REFERENCES users(id),
    approved_at TIMESTAMP,
    approval_reason VARCHAR(255),
    override_reason VARCHAR(255),        -- Emergency reason if override used
    is_override BOOLEAN DEFAULT FALSE,
    settled_at TIMESTAMP,
    INDEX idx_spk_id (spk_id),
    INDEX idx_status (status),
    INDEX idx_approval_status (approval_status)
);

CREATE TABLE material_debt_settlements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    debt_id INT FOREIGN KEY REFERENCES material_debts(id),
    qty_received DECIMAL(10, 2),
    received_at TIMESTAMP,
    recorded_by_id INT FOREIGN KEY REFERENCES users(id),
    notes VARCHAR(255),
    INDEX idx_debt_id (debt_id)
);
```

---

## 🎯 WORKFLOW FLOWS

### Flow 1: Editing SPK Quantity

```
┌────────────────────────────────┐
│ PPIC Manager Views SPK         │
│ (e.g., qty=500)                │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Click "Edit SPK"               │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Form shows:                    │
│  - Original qty: 500           │
│  - New qty: [input field]      │
│  - Reason: [textarea]          │
│  - Checkbox: "Allow Negative"  │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ User enters new qty: 600       │
│ Reason: "Customer order upsell"│
│ Allow Negative: ☑ YES          │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Click "Submit for Approval"    │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Check: SPK already started?    │
│ - YES: Show warning            │
│ - NO: Proceed                  │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Save modification to DB        │
│ Create audit log entry         │
│ Create material debt if needed  │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ If allow_negative = true:      │
│ → Send for approval            │
│ Else:                          │
│ → Approval auto-granted        │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Notify approver (SPV/Manager)  │
│ Create approval request        │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Awaiting Approval              │
│ (Status: PENDING_APPROVAL)     │
└────────────────────────────────┘
```

### Flow 2: Approval Process

```
┌─────────────────────────────────┐
│ SPV/Manager receives notice     │
│ "SPK #123 needs approval"       │
└────────────┬─────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ View approval request:          │
│ ├─ Original SPK qty: 500        │
│ ├─ New SPK qty: 600             │
│ ├─ Material debt: 100 units     │
│ ├─ Material needed: Material X  │
│ ├─ Reason: Customer upsell      │
│ └─ Requested by: PPIC Manager   │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────┬──────────────┐
│   Approve    │    Reject    │
└──────┬───────┴──────┬───────┘
       │              │
       ▼              ▼
  ┌─────────┐  ┌─────────────┐
  │ Approval│  │ Reject      │
  │ Dialog  │  │ Dialog      │
  └────┬────┘  └──────┬──────┘
       │              │
       ▼              ▼
  ┌─────────────────────────┐
  │ Confirm & Add Reason    │
  │ e.g., "Approved - mat'l │
  │ delivery scheduled      │
  │ for Jan 27"             │
  └────────┬────────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ Save approval        │
  │ Update debt status   │
  │ Create audit entry   │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ Notify requester     │
  │ Update SPK status    │
  └──────────────────────┘
```

### Flow 3: Production with Negative Inventory

```
SPK created: qty_required = 600 (with 100 units negative)
Material in warehouse: 500 units
Negative approval: APPROVED

Action 1: Reduce material stock by 600
  └─ Result: Stock = 500 - 600 = -100 units
  └─ Create debt record: qty_owed = 100

Action 2: Production can start immediately
  ├─ Use available 500 units
  └─ Remaining 100 marked as "provisional deduction"

Action 3: Material received later (50 units)
  └─ Settlement: qty_owed reduces to 50
  └─ Debt status: PARTIAL

Action 4: More material received (60 units)
  └─ Settles remaining 50 + surplus 10
  └─ Debt status: SETTLED
  └─ Surplus 10 units added back to stock
```

---

## 🔧 BACKEND IMPLEMENTATION

### Python/FastAPI Endpoints

#### 1. Edit SPK Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(prefix="/ppic", tags=["PPIC"])

class UpdateSPKRequest(BaseModel):
    target_qty: int = Field(gt=0)
    reason: str
    allow_negative_inventory: bool = False

class UpdateSPKResponse(BaseModel):
    spk_id: int
    original_qty: int
    new_qty: int
    modification_reason: str
    allow_negative: bool
    status: str
    created_at: datetime
    modified_at: datetime

@router.put(
    "/spk/{spk_id}",
    response_model=UpdateSPKResponse,
    dependencies=[Depends(require_permission("ppic.update"))]
)
async def update_spk(
    spk_id: int,
    request: UpdateSPKRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit SPK quantity and optionally allow negative inventory"""
    
    # Fetch SPK
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")
    
    # Check if already started (warning but allow)
    if spk.status in ["IN_PROGRESS", "COMPLETED"]:
        # Optional: block edit or allow with confirmation
        pass
    
    # Get old values
    old_qty = spk.target_qty
    old_allow_negative = spk.allow_negative_inventory
    
    # Update SPK
    spk.original_qty = old_qty
    spk.modified_qty = request.target_qty
    spk.modification_reason = request.reason
    spk.modified_by_id = current_user.id
    spk.modified_at = datetime.utcnow()
    spk.allow_negative_inventory = request.allow_negative_inventory
    
    if request.allow_negative_inventory:
        spk.negative_approval_status = "PENDING_APPROVAL"
    else:
        spk.negative_approval_status = "N/A"
        spk.allow_negative_inventory = False
    
    # Calculate material requirement change
    qty_delta = request.target_qty - old_qty
    
    if qty_delta != 0 and request.allow_negative_inventory:
        # Create material debt if needed
        mo = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.id == spk.mo_id
        ).first()
        
        # Get BOM for product
        bom_items = db.query(BOMItem).filter(
            BOMItem.product_id == mo.product_id
        ).all()
        
        for bom_item in bom_items:
            material_qty_needed = qty_delta * bom_item.qty_per_unit
            current_stock = db.query(func.sum(WarehouseStock.qty)).filter(
                WarehouseStock.material_id == bom_item.material_id
            ).scalar() or 0
            
            if current_stock < material_qty_needed:
                # Create debt record
                debt = MaterialDebt(
                    spk_id=spk_id,
                    material_id=bom_item.material_id,
                    qty_owed=material_qty_needed - current_stock,
                    qty_settled=0,
                    qty_pending=material_qty_needed - current_stock,
                    status="PENDING",
                    approval_status="PENDING_APPROVAL",
                    created_by_id=current_user.id,
                    created_at=datetime.utcnow()
                )
                db.add(debt)
                
                # Create audit log
                audit_log(
                    user_id=current_user.id,
                    action="MATERIAL_DEBT_CREATED",
                    entity_type="MaterialDebt",
                    entity_id=debt.id,
                    details={
                        "spk_id": spk_id,
                        "material_id": bom_item.material_id,
                        "qty_owed": material_qty_needed - current_stock
                    }
                )
    
    # Record modification in history
    modification = SPKModification(
        spk_id=spk_id,
        field_name="target_qty",
        old_value=str(old_qty),
        new_value=str(request.target_qty),
        modified_by_id=current_user.id,
        modification_reason=request.reason,
        created_at=datetime.utcnow()
    )
    db.add(modification)
    db.commit()
    
    # Audit log
    audit_log(
        user_id=current_user.id,
        action="SPK_MODIFIED",
        entity_type="SPK",
        entity_id=spk_id,
        details={
            "old_qty": old_qty,
            "new_qty": request.target_qty,
            "reason": request.reason,
            "allow_negative": request.allow_negative_inventory
        }
    )
    
    return UpdateSPKResponse(
        spk_id=spk.id,
        original_qty=spk.original_qty,
        new_qty=spk.modified_qty or spk.target_qty,
        modification_reason=spk.modification_reason,
        allow_negative=spk.allow_negative_inventory,
        status=spk.negative_approval_status,
        created_at=spk.created_at,
        modified_at=spk.modified_at
    )
```

#### 2. Approve Negative Inventory Endpoint
```python
class ApproveDriftRequest(BaseModel):
    debt_id: int
    action: str = Field(pattern="^(APPROVE|REJECT)$")
    reason: str
    override_reason: str = None

@router.post(
    "/material-debt/{debt_id}/approve",
    response_model=dict,
    dependencies=[Depends(require_permission("warehouse.approve_negative"))]
)
async def approve_material_debt(
    debt_id: int,
    request: ApproveDriftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject negative inventory for material debt"""
    
    debt = db.query(MaterialDebt).filter(
        MaterialDebt.id == debt_id
    ).first()
    
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    if request.action == "APPROVE":
        debt.approval_status = "APPROVED"
        debt.approved_by_id = current_user.id
        debt.approved_at = datetime.utcnow()
        debt.approval_reason = request.reason
        
        if request.override_reason:
            debt.is_override = True
            debt.override_reason = request.override_reason
        
        # Deduct stock immediately (go negative if needed)
        warehouse_stock = db.query(WarehouseStock).filter(
            WarehouseStock.material_id == debt.material_id
        ).first()
        
        if warehouse_stock:
            warehouse_stock.qty -= debt.qty_owed
        else:
            warehouse_stock = WarehouseStock(
                material_id=debt.material_id,
                qty=-debt.qty_owed,
                warehouse_location_id=1
            )
            db.add(warehouse_stock)
        
        # Production can now start
        spk = db.query(SPK).filter(SPK.id == debt.spk_id).first()
        if spk:
            spk.negative_approval_status = "APPROVED"
        
        action_text = "APPROVED"
        
    else:  # REJECT
        debt.approval_status = "REJECTED"
        debt.approved_by_id = current_user.id
        debt.approved_at = datetime.utcnow()
        debt.approval_reason = request.reason
        
        # Block production
        spk = db.query(SPK).filter(SPK.id == debt.spk_id).first()
        if spk:
            spk.negative_approval_status = "REJECTED"
            spk.allow_negative_inventory = False
        
        action_text = "REJECTED"
    
    db.commit()
    
    # Audit log
    audit_log(
        user_id=current_user.id,
        action=f"MATERIAL_DEBT_{action_text}",
        entity_type="MaterialDebt",
        entity_id=debt_id,
        details={
            "spk_id": debt.spk_id,
            "material_id": debt.material_id,
            "qty_owed": debt.qty_owed,
            "reason": request.reason
        }
    )
    
    return {
        "status": action_text,
        "debt_id": debt_id,
        "spk_id": debt.spk_id,
        "can_start_production": request.action == "APPROVE"
    }
```

#### 3. Settle Material Debt Endpoint
```python
class SettleDebtRequest(BaseModel):
    qty_received: Decimal = Field(gt=0)
    reason: str = "Material delivery received"

@router.post(
    "/material-debt/{debt_id}/settle",
    response_model=dict
)
async def settle_material_debt(
    debt_id: int,
    request: SettleDebtRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record partial or full settlement of material debt"""
    
    debt = db.query(MaterialDebt).filter(
        MaterialDebt.id == debt_id
    ).first()
    
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    # Calculate new values
    new_settled = debt.qty_settled + request.qty_received
    new_pending = debt.qty_owed - new_settled
    
    if new_pending < 0:
        # Overage: add back to stock
        warehouse_stock = db.query(WarehouseStock).filter(
            WarehouseStock.material_id == debt.material_id
        ).first()
        
        if warehouse_stock:
            warehouse_stock.qty += abs(new_pending)
    
    # Update debt
    debt.qty_settled = new_settled
    debt.qty_pending = max(0, new_pending)
    debt.status = "SETTLED" if new_pending <= 0 else "PARTIAL"
    debt.settled_at = datetime.utcnow() if new_pending <= 0 else None
    
    # Record settlement
    settlement = MaterialDebtSettlement(
        debt_id=debt_id,
        qty_received=request.qty_received,
        received_at=datetime.utcnow(),
        recorded_by_id=current_user.id,
        notes=request.reason
    )
    db.add(settlement)
    db.commit()
    
    # Audit log
    audit_log(
        user_id=current_user.id,
        action="MATERIAL_DEBT_SETTLED",
        entity_type="MaterialDebt",
        entity_id=debt_id,
        details={
            "qty_received": request.qty_received,
            "total_settled": new_settled,
            "remaining": new_pending
        }
    )
    
    return {
        "debt_id": debt_id,
        "qty_settled": new_settled,
        "qty_pending": new_pending,
        "status": debt.status,
        "fully_settled": new_pending <= 0
    }
```

---

## 🎨 FRONTEND IMPLEMENTATION (React/TypeScript)

### Component 1: SPK Edit Form
```typescript
import React, { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'

interface EditSPKFormProps {
  spkId: number
  onSuccess: () => void
}

export const EditSPKForm: React.FC<EditSPKFormProps> = ({ spkId, onSuccess }) => {
  const [newQty, setNewQty] = useState('')
  const [reason, setReason] = useState('')
  const [allowNegative, setAllowNegative] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const { data: spk, isLoading: spkLoading } = useQuery({
    queryKey: ['spk', spkId],
    queryFn: () => apiClient.getSPK(spkId)
  })

  const editMutation = useMutation({
    mutationFn: (data: any) => apiClient.updateSPK(spkId, data),
    onSuccess: () => {
      onSuccess()
      setNewQty('')
      setReason('')
      setAllowNegative(false)
    }
  })

  const handleSubmit = () => {
    editMutation.mutate({
      target_qty: parseInt(newQty),
      reason,
      allow_negative_inventory: allowNegative
    })
  }

  if (spkLoading) return <div>Loading...</div>

  return (
    <div className="spk-edit-form">
      <h2>Edit SPK #{spkId}</h2>
      
      <div className="form-group">
        <label>Current Quantity: {spk?.target_qty}</label>
        <input
          type="number"
          value={newQty}
          onChange={(e) => setNewQty(e.target.value)}
          placeholder="Enter new quantity"
          min="1"
        />
      </div>

      <div className="form-group">
        <label>Modification Reason *</label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Why are you modifying this SPK?"
          rows={3}
        />
      </div>

      <div className="form-group checkbox">
        <label>
          <input
            type="checkbox"
            checked={allowNegative}
            onChange={(e) => setAllowNegative(e.target.checked)}
          />
          Allow Negative Inventory (start production without materials)
        </label>
      </div>

      {allowNegative && (
        <div className="alert alert-warning">
          ⚠️ This requires approval from SPV/Manager before production can start
        </div>
      )}

      <button
        onClick={() => setShowConfirm(true)}
        disabled={!newQty || !reason || editMutation.isPending}
      >
        {editMutation.isPending ? 'Submitting...' : 'Submit for Approval'}
      </button>

      {showConfirm && (
        <ConfirmDialog
          title="Confirm SPK Edit"
          message={`Update SPK qty from ${spk?.target_qty} to ${newQty}?`}
          onConfirm={() => {
            handleSubmit()
            setShowConfirm(false)
          }}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  )
}
```

### Component 2: Negative Inventory Approval
```typescript
interface MaterialDebt {
  id: number
  spk_id: number
  material_id: number
  qty_owed: number
  status: string
  approval_status: string
}

export const MaterialDebtApprovalPanel: React.FC<{ debt: MaterialDebt }> = ({ debt }) => {
  const [approvalReason, setApprovalReason] = useState('')
  const [overrideReason, setOverrideReason] = useState('')
  const [isOverride, setIsOverride] = useState(false)

  const approveMutation = useMutation({
    mutationFn: (data: any) =>
      apiClient.approveMaterialDebt(debt.id, data),
    onSuccess: () => {
      // Refresh or notify success
    }
  })

  return (
    <div className="debt-approval-panel">
      <h3>Material Debt Approval</h3>
      
      <div className="debt-info">
        <p>SPK #{debt.spk_id}</p>
        <p>Material: Product X</p>
        <p>Amount Owed: {debt.qty_owed} units</p>
      </div>

      <div className="form-group">
        <label>Approval Reason *</label>
        <textarea
          value={approvalReason}
          onChange={(e) => setApprovalReason(e.target.value)}
          placeholder="e.g., 'Material in transit, ETA Jan 27'"
        />
      </div>

      {isOverride && (
        <div className="form-group">
          <label>Override Reason (Emergency) *</label>
          <textarea
            value={overrideReason}
            onChange={(e) => setOverrideReason(e.target.value)}
            placeholder="Why is this an emergency?"
          />
        </div>
      )}

      <div className="form-group checkbox">
        <label>
          <input
            type="checkbox"
            checked={isOverride}
            onChange={(e) => setIsOverride(e.target.checked)}
          />
          This is an emergency override
        </label>
      </div>

      <div className="button-group">
        <button
          onClick={() => approveMutation.mutate({
            debt_id: debt.id,
            action: 'APPROVE',
            reason: approvalReason,
            override_reason: isOverride ? overrideReason : undefined
          })}
          className="btn-primary"
          disabled={!approvalReason}
        >
          ✓ Approve
        </button>
        
        <button
          onClick={() => approveMutation.mutate({
            debt_id: debt.id,
            action: 'REJECT',
            reason: approvalReason
          })}
          className="btn-danger"
          disabled={!approvalReason}
        >
          ✗ Reject
        </button>
      </div>
    </div>
  )
}
```

---

## 📊 PERMISSION MATRIX

| Role | Can Edit SPK | Can Approve Negative | Can Settle Debt |
|------|------|------|------|
| OPERATOR | ❌ | ❌ | ❌ |
| SUPERVISOR | ❌ | ✅ (dept only) | ✅ (dept only) |
| PPIC_MANAGER | ✅ | ❌ | ❌ |
| WAREHOUSE_SPV | ❌ | ✅ (warehouse) | ✅ |
| MANAGER | ✅ | ✅ | ✅ |
| SUPERADMIN | ✅ | ✅ | ✅ |

---

## 🔍 AUDIT TRAIL EXAMPLE

```json
{
  "action": "SPK_MODIFIED",
  "timestamp": "2026-01-26T14:30:00Z",
  "user_id": 5,
  "username": "ppic_manager@quty.co.id",
  "entity_type": "SPK",
  "entity_id": 123,
  "details": {
    "old_qty": 500,
    "new_qty": 600,
    "reason": "Customer order increased",
    "allow_negative": true,
    "material_debt_created": {
      "material_id": 10,
      "qty_owed": 100,
      "approval_status": "PENDING_APPROVAL"
    }
  }
}

{
  "action": "MATERIAL_DEBT_APPROVED",
  "timestamp": "2026-01-26T15:15:00Z",
  "user_id": 8,
  "username": "spv@quty.co.id",
  "entity_type": "MaterialDebt",
  "entity_id": 45,
  "details": {
    "spk_id": 123,
    "qty_owed": 100,
    "approval_reason": "Material in transit, ETA Jan 27"
  }
}

{
  "action": "MATERIAL_DEBT_SETTLED",
  "timestamp": "2026-01-27T10:00:00Z",
  "user_id": 12,
  "username": "warehouse@quty.co.id",
  "entity_type": "MaterialDebt",
  "entity_id": 45,
  "details": {
    "qty_received": 100,
    "qty_settled": 100,
    "qty_pending": 0,
    "status": "SETTLED"
  }
}
```

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Database schema created (SPK modifications, material debts)
- [ ] Backend endpoints implemented (update SPK, approve debt, settle debt)
- [ ] Permission model updated (approval matrix)
- [ ] Frontend form created (Edit SPK, Negative Inventory)
- [ ] Approval workflow UI implemented
- [ ] Audit logging added
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Error handling implemented
- [ ] Documentation complete
- [ ] User training materials created
- [ ] Deployed to staging
- [ ] QA tested
- [ ] Deployed to production

---

## 6️⃣ DAILY PRODUCTION INPUT TRACKING

### Overview
Admin/Operator inputs actual daily production quantities against SPK target, using calendar-like date columns. Each day shows progress, with final confirmation button when SPK target is reached.

### Database Schema - Daily Production Tracking

```sql
-- Track daily production input per SPK
CREATE TABLE spk_daily_production (
    id INT PRIMARY KEY AUTO_INCREMENT,
    spk_id INT FOREIGN KEY REFERENCES spks(id),
    production_date DATE NOT NULL,
    input_qty INT DEFAULT 0,
    cumulative_qty INT,              -- Running total
    input_by_id INT FOREIGN KEY REFERENCES users(id),
    status VARCHAR(50),              -- DRAFT, CONFIRMED, COMPLETED
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_spk_id (spk_id),
    INDEX idx_production_date (production_date),
    UNIQUE KEY uk_spk_date (spk_id, production_date)
);

-- Track SPK completion milestone
CREATE TABLE spk_production_completion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    spk_id INT FOREIGN KEY REFERENCES spks(id),
    target_qty INT,
    actual_qty INT,
    completed_date DATE,
    confirmed_by_id INT FOREIGN KEY REFERENCES users(id),
    confirmation_notes VARCHAR(255),
    confirmed_at TIMESTAMP,
    is_completed BOOLEAN DEFAULT FALSE,
    INDEX idx_spk_id (spk_id),
    INDEX idx_completed_date (completed_date)
);

-- Status tracking per SPK
ALTER TABLE spks ADD COLUMN (
    production_status VARCHAR(50) DEFAULT 'NOT_STARTED',  -- NOT_STARTED, IN_PROGRESS, COMPLETED
    completion_date DATE,
    daily_progress_start_date DATE
);
```

### UI Structure - Calendar-Like Production Dashboard

**Daily Production Input Grid**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ SPK-2026-001: Teddy Bear Production                    Status: IN_PROGRESS │
├─────────────────────────────────────────────────────────────────────────┤
│ Target: 500 units | Current Progress: 320 units (64%)                   │
├─────────────────────────────────────────────────────────────────────────┤
│ 📅 Week of Jan 26 - Feb 01, 2026                                        │
├─────────────────────────────────────────────────────────────────────────┤
│
│  Date      | Mon 26 | Tue 27 | Wed 28 | Thu 29 | Fri 30 | Sat 31 | Sun 1
│ ───────────┼────────┼────────┼────────┼────────┼────────┼────────┼──────
│ Daily Qty  |   50   |   60   |   75   |   70   |        |        |
│  Input     |  ✅    |   ✅   |   ✅   |   ✅   | [ ]    | [ ]    | [ ]
│ ───────────┼────────┼────────┼────────┼────────┼────────┼────────┼──────
│ Cumulative | 50     | 110    | 185    | 255    | 255    | 255    | 255
│ ───────────┼────────┼────────┼────────┼────────┼────────┼────────┼──────
│ Notes      | Good   | Good   | Good   | Good   |        |        |
│            | quality| quality| speed  | Temp   |        |        |
│            |        |        | up     | issue  |        |        |
│
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Need to reach: 500 units | Remaining: 245 units | Est. completion: 02-02 │
│                                                                           │
│  [Enter Today's Qty: ____]  [Confirm]  [Complete SPK ✓]                 │
│                                                                           │
│  📊 Progress Chart:  ████████████░░░░░░░░░░░░░░░░░ 64%                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Frontend Component - DailyProductionInput

**React/TypeScript Component Structure**:

```typescript
interface DailyProduction {
  spk_id: number;
  production_date: string;
  input_qty: number;
  cumulative_qty: number;
  status: 'DRAFT' | 'CONFIRMED' | 'COMPLETED';
  notes: string;
}

interface SPKProductionState {
  spk_id: number;
  target_qty: number;
  actual_qty: number;
  daily_entries: DailyProduction[];
  completion_percentage: number;
  is_completed: boolean;
}

const DailyProductionInput: React.FC<{spkId: number}> = ({spkId}) => {
  const [productionData, setProductionData] = useState<SPKProductionState>({
    spk_id: spkId,
    target_qty: 500,
    actual_qty: 320,
    daily_entries: [],
    completion_percentage: 64,
    is_completed: false
  });

  const [todayQty, setTodayQty] = useState<number>(0);
  const [todayNotes, setTodayNotes] = useState<string>('');

  // Input daily production
  const handleDailyInput = async (qty: number) => {
    const response = await fetch(`/api/v1/ppic/spk/${spkId}/daily-production`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        production_date: new Date().toISOString().split('T')[0],
        input_qty: qty,
        notes: todayNotes,
        status: 'CONFIRMED'
      })
    });

    if (response.ok) {
      const data = await response.json();
      setProductionData(data);
      setTodayQty(0);
      setTodayNotes('');
    }
  };

  // Complete SPK when target reached
  const handleCompleteSPK = async () => {
    if (productionData.actual_qty < productionData.target_qty) {
      alert(`Cannot complete. Still need ${
        productionData.target_qty - productionData.actual_qty
      } units.`);
      return;
    }

    const response = await fetch(`/api/v1/ppic/spk/${spkId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        confirmation_notes: 'Daily production target reached',
        confirmed_by_id: getCurrentUserId()
      })
    });

    if (response.ok) {
      setProductionData({...productionData, is_completed: true});
      alert('✅ SPK marked as COMPLETED!');
    }
  };

  return (
    <div className="daily-production-panel">
      <div className="spk-header">
        <h2>SPK-{spkId}: Daily Production Tracking</h2>
        <div className="progress-info">
          <span>Target: {productionData.target_qty} units</span>
          <span>Progress: {productionData.actual_qty} units ({productionData.completion_percentage}%)</span>
          <span>Remaining: {productionData.target_qty - productionData.actual_qty} units</span>
        </div>
      </div>

      {/* Daily Grid */}
      <div className="daily-grid">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              {productionData.daily_entries.map((entry, idx) => (
                <th key={idx}>{formatDate(entry.production_date)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Daily Qty</td>
              {productionData.daily_entries.map((entry, idx) => (
                <td key={idx} className={entry.status === 'CONFIRMED' ? 'confirmed' : ''}>
                  {entry.input_qty} {entry.status === 'CONFIRMED' ? '✅' : ''}
                </td>
              ))}
            </tr>
            <tr>
              <td>Cumulative</td>
              {productionData.daily_entries.map((entry, idx) => (
                <td key={idx}>{entry.cumulative_qty}</td>
              ))}
            </tr>
            <tr>
              <td>Notes</td>
              {productionData.daily_entries.map((entry, idx) => (
                <td key={idx} className="notes-cell">{entry.notes}</td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Today's Input */}
      {!productionData.is_completed && (
        <div className="daily-input-form">
          <div className="input-group">
            <label>Today's Production Qty:</label>
            <input 
              type="number" 
              value={todayQty} 
              onChange={(e) => setTodayQty(Number(e.target.value))}
              placeholder="Enter quantity"
            />
            <span className="helper-text">
              Current: {productionData.actual_qty} + {todayQty} = {productionData.actual_qty + todayQty}
            </span>
          </div>

          <div className="input-group">
            <label>Notes (Quality, Issues, etc.):</label>
            <textarea 
              value={todayNotes} 
              onChange={(e) => setTodayNotes(e.target.value)}
              placeholder="Any notes for today's production"
              rows={3}
            />
          </div>

          <button 
            className="btn-confirm"
            onClick={() => handleDailyInput(todayQty)}
            disabled={todayQty === 0}
          >
            ✅ Confirm Today's Input
          </button>
        </div>
      )}

      {/* Progress Bar */}
      <div className="progress-bar-container">
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{width: `${productionData.completion_percentage}%`}}
          >
            {productionData.completion_percentage}%
          </div>
        </div>
      </div>

      {/* Completion Button */}
      <div className="completion-section">
        {productionData.actual_qty >= productionData.target_qty ? (
          <button 
            className="btn-complete btn-primary"
            onClick={handleCompleteSPK}
            disabled={productionData.is_completed}
          >
            ✅ Mark SPK as COMPLETED
          </button>
        ) : (
          <div className="completion-info">
            ℹ️ Need {productionData.target_qty - productionData.actual_qty} more units to complete
          </div>
        )}
      </div>

      {productionData.is_completed && (
        <div className="completion-badge">
          ✅ SPK COMPLETED on {productionData.daily_entries[productionData.daily_entries.length - 1].production_date}
        </div>
      )}
    </div>
  );
};
```

### Backend Endpoints - Daily Production API

**1. Record Daily Production**:
```python
@router.post("/ppic/spk/{spk_id}/daily-production")
async def record_daily_production(
    spk_id: int,
    request: RecordDailyProductionRequest,  # {production_date, input_qty, notes}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record daily production quantity for SPK
    Permission: PPIC_MANAGER, SUPERVISOR, OPERATOR
    """
    # Verify SPK exists
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")

    # Calculate cumulative quantity
    last_entry = db.query(SPKDailyProduction)\
        .filter(SPKDailyProduction.spk_id == spk_id)\
        .order_by(SPKDailyProduction.production_date.desc())\
        .first()
    
    cumulative = (last_entry.cumulative_qty if last_entry else 0) + request.input_qty

    # Create daily entry
    daily_entry = SPKDailyProduction(
        spk_id=spk_id,
        production_date=request.production_date,
        input_qty=request.input_qty,
        cumulative_qty=cumulative,
        input_by_id=current_user.id,
        status='CONFIRMED',
        notes=request.notes
    )
    db.add(daily_entry)

    # Update SPK production status
    spk.actual_qty = cumulative
    spk.production_status = 'IN_PROGRESS' if cumulative > 0 else 'NOT_STARTED'

    # Audit log
    audit_log = AuditLog(
        action='DAILY_PRODUCTION_INPUT',
        resource_type='SPK',
        resource_id=spk_id,
        user_id=current_user.id,
        details={'date': request.production_date, 'qty': request.input_qty},
        timestamp=datetime.now()
    )
    db.add(audit_log)
    db.commit()

    return {
        'data': {
            'spk_id': spk_id,
            'daily_entry': daily_entry,
            'cumulative_qty': cumulative,
            'target_qty': spk.target_qty,
            'completion_percentage': (cumulative / spk.target_qty) * 100
        },
        'message': 'Daily production recorded successfully',
        'timestamp': datetime.now()
    }
```

**2. Get Daily Production Report**:
```python
@router.get("/ppic/spk/{spk_id}/daily-production")
async def get_daily_production(
    spk_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily production entries for SPK
    Returns calendar-style data with all dates
    """
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")

    # Get all daily entries
    entries = db.query(SPKDailyProduction)\
        .filter(SPKDailyProduction.spk_id == spk_id)\
        .order_by(SPKDailyProduction.production_date.asc())\
        .all()

    # Format calendar response
    calendar_data = {
        'spk_id': spk_id,
        'target_qty': spk.target_qty,
        'actual_qty': spk.actual_qty,
        'daily_entries': [
            {
                'date': entry.production_date,
                'qty': entry.input_qty,
                'cumulative': entry.cumulative_qty,
                'notes': entry.notes,
                'status': entry.status
            }
            for entry in entries
        ],
        'completion_percentage': (spk.actual_qty / spk.target_qty) * 100,
        'is_completed': spk.production_status == 'COMPLETED'
    }

    return {'data': calendar_data, 'timestamp': datetime.now()}
```

**3. Complete SPK Production**:
```python
@router.post("/ppic/spk/{spk_id}/complete")
async def complete_spk_production(
    spk_id: int,
    request: CompleteSPKRequest,  # {confirmation_notes}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark SPK as completed when target quantity reached
    Permission: PPIC_MANAGER, MANAGER, SUPERADMIN
    """
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")

    # Verify quantity reached target
    if spk.actual_qty < spk.target_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete. Need {spk.target_qty - spk.actual_qty} more units"
        )

    # Mark as completed
    spk.production_status = 'COMPLETED'
    spk.completion_date = datetime.now().date()

    # Create completion record
    completion = SPKProductionCompletion(
        spk_id=spk_id,
        target_qty=spk.target_qty,
        actual_qty=spk.actual_qty,
        completed_date=spk.completion_date,
        confirmed_by_id=current_user.id,
        confirmation_notes=request.confirmation_notes,
        confirmed_at=datetime.now(),
        is_completed=True
    )
    db.add(completion)

    # Audit log
    audit_log = AuditLog(
        action='SPK_COMPLETED',
        resource_type='SPK',
        resource_id=spk_id,
        user_id=current_user.id,
        details={
            'target_qty': spk.target_qty,
            'actual_qty': spk.actual_qty,
            'completion_date': spk.completion_date.isoformat()
        },
        timestamp=datetime.now()
    )
    db.add(audit_log)
    db.commit()

    return {
        'data': {
            'spk_id': spk_id,
            'production_status': 'COMPLETED',
            'target_qty': spk.target_qty,
            'actual_qty': spk.actual_qty,
            'completion_date': spk.completion_date
        },
        'message': f'✅ SPK {spk_id} marked as COMPLETED',
        'timestamp': datetime.now()
    }
```

### Permission Matrix - Daily Production

| Role | View Daily | Input Daily | Confirm Input | Complete SPK |
|------|-----------|-------------|---------------|-------------|
| OPERATOR | ✅ | ✅ | ❌ | ❌ |
| SUPERVISOR | ✅ | ✅ | ✅ | ❌ |
| PPIC_MANAGER | ✅ | ✅ | ✅ | ✅ |
| WAREHOUSE_SPV | ✅ | ❌ | ❌ | ❌ |
| MANAGER | ✅ | ✅ | ✅ | ✅ |
| SUPERADMIN | ✅ | ✅ | ✅ | ✅ |

### Workflow - Daily Production Input

```
┌─────────────────────────────────────────────────────┐
│  Day 1: Admin inputs 50 units                       │
│         Cumulative: 50 / 500 (10%)                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Day 2: Admin inputs 60 units                       │
│         Cumulative: 110 / 500 (22%)                 │
│         Status: IN_PROGRESS                         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Day 3-10: Continue daily input                     │
│            Monitor progress vs target               │
│            Add notes (quality, issues, speed)       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Target Reached: 500 / 500 (100%)                   │
│                                                     │
│  ✅ [Confirm Completion Button]                     │
│     Status changes to: COMPLETED                    │
│     Locked from further edits                       │
└─────────────────────────────────────────────────────┘
```

### Features & Behavior

**Calendar-Like Grid**:
- Shows week view (Mon-Sun) with date columns
- Each cell shows daily input, cumulative, and notes
- Locked days (past) show as read-only ✅
- Today editable with input fields
- Future days placeholder [ ]

**Real-Time Progress**:
- Progress bar updates after each input
- Percentage calculated (actual_qty / target_qty)
- Estimated completion date shown
- Visual indicator when target reached

**Completion Confirmation**:
- Button only enabled when actual_qty ≥ target_qty
- Confirmation creates completion record in database
- SPK locked (no more daily inputs accepted)
- Audit trail tracks who confirmed and when

**Error Handling**:
- Cannot input negative quantities
- Cannot complete if target not reached
- Cannot modify past entries (past dates locked)
- Duplicate date entries prevented (unique constraint)

---

**Status**: Specification Complete | Ready for Implementation  
**Owner**: Daniel Rizaldy  
**Created**: January 26, 2026

