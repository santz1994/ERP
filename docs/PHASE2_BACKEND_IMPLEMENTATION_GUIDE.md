# 🚀 PHASE 2: BACKEND IMPLEMENTATION GUIDE

**Status**: Starting Phase 2 (Backend) | **Timeline**: 2-3 days  
**Scope**: 11 new API endpoints + 5 critical fixes + Database tables  
**Language**: Python 3.11 + FastAPI 0.95  
**Database**: PostgreSQL 15 + SQLAlchemy ORM

---

## 📋 IMPLEMENTATION CHECKLIST (11 Tasks)

### TASK 1: Daily Production Input Endpoints (4 endpoints)
**Status**: 🟡 QUEUED | **Time**: 4 hours

**Endpoints to Create**:
```python
1. POST /production/spk/{spk_id}/daily-input
   Input:  {"date": "2026-01-28", "qty": 150, "notes": "..."}
   Output: {"status": "ok", "cumulative": 150, "progress": 30%}
   
2. GET /production/spk/{spk_id}/progress
   Output: {"target": 500, "cumulative": 450, "remaining": 50, "daily": [...]}
   
3. GET /production/my-spks
   Output: [{"id": "SPK-001", "stage": "CUTTING", "progress": 30}]
   
4. POST /production/mobile/daily-input
   Mobile variant of endpoint 1 with offline sync
```

**Database Table to Create**:
```sql
CREATE TABLE spk_daily_production (
    id INT PRIMARY KEY,
    spk_id INT NOT NULL,
    date DATE NOT NULL,
    quantity_input INT NOT NULL,
    notes TEXT,
    created_by INT NOT NULL,
    created_at TIMESTAMP,
    FOREIGN KEY (spk_id) REFERENCES spk(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

**File to Create**:
- `/erp-softtoys/app/api/v1/production/daily_input.py`

**Implementation Steps**:
1. Create DailyProductionService (business logic)
2. Create daily_input.py endpoints
3. Add cumulative calculation logic
4. Add permission checks (PRODUCTION_STAFF role)
5. Add error handling

---

### TASK 2: PPIC Dashboard Endpoints (4 endpoints)
**Status**: 🟡 QUEUED | **Time**: 4 hours

**Endpoints to Create**:
```python
1. GET /ppic/dashboard
   Output: {
     "total_spks": 12,
     "completed": 5,
     "in_progress": 6,
     "delayed": 1,
     "by_stage": {...},
     "alerts": [...]
   }
   
2. GET /ppic/reports/daily-summary
   Output: {
     "date": "2026-01-29",
     "target": 2000,
     "actual": 1850,
     "variance": -150,
     "by_stage": [...]
   }
   
3. GET /ppic/reports/on-track-status
   Output: {
     "on_track": 11,
     "at_risk": 1,
     "off_track": 0,
     "details": [...]
   }
   
4. GET /ppic/alerts
   Output: {
     "critical": [...],
     "warning": [...]
   }
```

**File to Create**:
- `/erp-softtoys/app/api/v1/ppic/dashboard.py`

**Implementation Steps**:
1. Create PPICService (aggregation logic)
2. Create dashboard.py endpoints
3. Add real-time status calculation
4. Add alert detection logic
5. Add permission checks (PPIC_MANAGER role)

---

### TASK 3: Approval Workflow Endpoints (3 endpoints)
**Status**: 🟡 QUEUED | **Time**: 3 hours

**Endpoints to Create**:
```python
1. POST /production/spk/{spk_id}/modify-qty
   Input:  {"new_qty": 450, "reason": "Customer request"}
   Output: {"mod_id": "MOD-001", "status": "pending"}
   
2. GET /production/approvals/pending
   Output: [{"id": "MOD-001", "change": "500→450", "requester": "SPV1"}]
   
3. POST /production/approvals/{mod_id}/approve
   Input:  {"approved": true, "notes": "OK"}
   Output: {"status": "approved", "spk_updated": true}
```

**Database Tables to Create**:
```sql
CREATE TABLE spk_modifications (
    id INT PRIMARY KEY,
    spk_id INT NOT NULL,
    old_qty INT NOT NULL,
    new_qty INT NOT NULL,
    change_reason TEXT,
    requested_by INT NOT NULL,
    requested_at TIMESTAMP,
    approved_by INT,
    approved_at TIMESTAMP,
    approval_status VARCHAR(20),
    FOREIGN KEY (spk_id) REFERENCES spk(id)
);

CREATE TABLE material_debt (
    id INT PRIMARY KEY,
    spk_id INT NOT NULL,
    material_id INT NOT NULL,
    debt_qty INT NOT NULL,
    approval_status VARCHAR(20),
    approved_by INT,
    settled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (spk_id) REFERENCES spk(id),
    FOREIGN KEY (material_id) REFERENCES material(id)
);
```

**File to Create**:
- `/erp-softtoys/app/api/v1/production/approval.py`
- `/erp-softtoys/app/services/approval_service.py`

**Implementation Steps**:
1. Create ApprovalService
2. Create approval endpoints
3. Add multi-level approval workflow
4. Add material debt tracking
5. Add audit trail logging

---

### TASK 4: Fix 5 Critical API Issues (14 hours)

**ISSUE 1: Missing FinishGood Endpoints (4 endpoints) - 4-6 hours**
```python
1. POST /warehouse/finishgood/receive
   Input: {"carton_id": "CARTON-125", "barcode": "QR-DATA"}
   
2. POST /warehouse/finishgood/verify
   Input: {"carton_id": "CARTON-125", "article": "IKEA-P01"}
   
3. POST /warehouse/finishgood/confirm
   Input: {"carton_id": "CARTON-125", "qty": 20}
   
4. POST /warehouse/finishgood/{id}/shipment
   Input: {"destination": "CUSTOMER", "method": "TRUCK"}
```

**ISSUE 2: Missing BOM Endpoints (5 endpoints) - 6-8 hours**
```python
1. POST /bom/create
   Input: {"article_id": "IKEA-P01", "materials": [...]}
   
2. GET /bom/list
3. GET /bom/{id}
4. PUT /bom/{id}
5. DELETE /bom/{id}
```

**ISSUE 3: CORS Production Config - 15 minutes**
```python
# From:
CORS_ORIGINS = ["*"]

# To:
CORS_ORIGINS = [
    "https://erp.quty-karunia.com",
    "https://www.quty-karunia.com",
    "https://mobile.quty-karunia.com"
]
```

**ISSUE 4: PPIC Lifecycle Incomplete (3-4 endpoints) - 4-6 hours**

**ISSUE 5: Response Format Inconsistency - 2-3 hours**

---

### TASK 5: Create Database Tables (ORM Models)
**Status**: 🟡 QUEUED | **Time**: 2 hours

**Files to Create/Update**:
- `/erp-softtoys/app/core/models.py` (add 5 new tables)
- `/erp-softtoys/app/core/schemas.py` (add 5 new Pydantic schemas)

**Tables**:
1. `spk_daily_production`
2. `spk_modifications`
3. `material_debt`
4. `material_debt_settlement`
5. `finish_goods_movement`

---

## 🎯 EXECUTION PLAN (Phase 2)

### Day 1: Core Endpoints
- [ ] Task 1: Daily Production Input endpoints (4)
- [ ] Task 2: PPIC Dashboard endpoints (4)
- [ ] Task 3: Approval Workflow endpoints (3)
- [ ] Create all database tables
- **Output**: 11 endpoints + 5 tables ready

### Day 2: Critical Fixes
- [ ] Fix Issue 1: FinishGood endpoints (4)
- [ ] Fix Issue 2: BOM endpoints (5)
- [ ] Fix Issue 3: CORS config
- **Output**: 9 missing endpoints created

### Day 3: Quality & Testing
- [ ] Fix Issues 4-5: Lifecycle + Response format
- [ ] API endpoint testing (Postman/curl)
- [ ] Database validation
- [ ] Error handling review
- **Output**: All endpoints tested & working

---

## 📝 IMPLEMENTATION TEMPLATE

### Example: Daily Production Input Endpoint

**File**: `/erp-softtoys/app/api/v1/production/daily_input.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models import SPK, SPKDailyProduction, User
from app.core.schemas import DailyInputRequest, DailyInputResponse
from app.core.security import get_current_user
from app.services.daily_production_service import DailyProductionService

router = APIRouter(prefix="/production", tags=["production"])
service = DailyProductionService()

@router.post("/spk/{spk_id}/daily-input", response_model=DailyInputResponse)
async def record_daily_input(
    spk_id: int,
    request: DailyInputRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record daily production input for SPK
    
    - **spk_id**: SPK ID
    - **request.qty**: Daily quantity produced
    - **request.date**: Date of production
    """
    
    # Permission check
    if not current_user.has_permission("PRODUCTION_INPUT"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Get SPK
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")
    
    # Create daily input record
    daily_input = SPKDailyProduction(
        spk_id=spk_id,
        date=request.date,
        quantity_input=request.qty,
        notes=request.notes,
        created_by=current_user.id
    )
    db.add(daily_input)
    
    # Calculate cumulative
    cumulative = service.calculate_cumulative(db, spk_id, include_today=True)
    progress = (cumulative / spk.modified_qty or spk.original_qty) * 100
    
    # Update SPK status
    if cumulative >= (spk.modified_qty or spk.original_qty):
        spk.status = "COMPLETED"
    else:
        spk.status = "IN_PROGRESS"
    
    spk.cumulative_output = cumulative
    
    db.commit()
    
    return DailyInputResponse(
        status="ok",
        cumulative=cumulative,
        progress=progress,
        message="Daily input recorded successfully"
    )

@router.get("/spk/{spk_id}/progress", response_model=SPKProgressResponse)
async def get_spk_progress(
    spk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SPK production progress"""
    
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")
    
    target = spk.modified_qty or spk.original_qty
    cumulative = service.calculate_cumulative(db, spk_id)
    
    return SPKProgressResponse(
        target=target,
        cumulative=cumulative,
        remaining=target - cumulative,
        progress=(cumulative / target * 100),
        daily_entries=service.get_daily_entries(db, spk_id)
    )

@router.get("/my-spks", response_model=List[MySPKResponse])
async def get_my_spks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SPKs for current user's department"""
    
    spks = db.query(SPK).filter(
        SPK.department_id == current_user.department_id,
        SPK.status.in_(["NOT_STARTED", "IN_PROGRESS"])
    ).all()
    
    return [
        MySPKResponse(
            id=spk.id,
            stage=spk.stage,
            progress=(spk.cumulative_output / (spk.modified_qty or spk.original_qty) * 100),
            status=spk.status
        )
        for spk in spks
    ]
```

**File**: `/erp-softtoys/app/services/daily_production_service.py`

```python
from sqlalchemy.orm import Session
from app.core.models import SPKDailyProduction, SPK
from datetime import datetime

class DailyProductionService:
    
    def calculate_cumulative(self, db: Session, spk_id: int, include_today: bool = False):
        """Calculate cumulative production quantity"""
        query = db.query(SPKDailyProduction).filter(
            SPKDailyProduction.spk_id == spk_id
        )
        
        entries = query.all()
        cumulative = sum(entry.quantity_input for entry in entries)
        
        return cumulative
    
    def get_daily_entries(self, db: Session, spk_id: int):
        """Get all daily entries for SPK"""
        entries = db.query(SPKDailyProduction).filter(
            SPKDailyProduction.spk_id == spk_id
        ).order_by(SPKDailyProduction.date).all()
        
        return [
            {
                "date": entry.date.isoformat(),
                "qty": entry.quantity_input,
                "cumulative": self.calculate_cumulative(db, spk_id)
            }
            for entry in entries
        ]
    
    def get_progress_summary(self, db: Session, spk_id: int):
        """Get production progress summary"""
        spk = db.query(SPK).filter(SPK.id == spk_id).first()
        if not spk:
            return None
        
        cumulative = self.calculate_cumulative(db, spk_id)
        target = spk.modified_qty or spk.original_qty
        
        return {
            "target": target,
            "cumulative": cumulative,
            "remaining": target - cumulative,
            "progress_pct": (cumulative / target * 100),
            "status": spk.status
        }
```

---

## ✅ COMPLETION CHECKLIST

**Backend Implementation**:
- [ ] 11 new API endpoints created
- [ ] 5 database tables created + migrations run
- [ ] 5 critical API issues fixed (9 endpoints)
- [ ] ORM models updated
- [ ] Pydantic schemas created
- [ ] Permission checks added
- [ ] Error handling implemented
- [ ] API tested with Postman (all endpoints green ✅)
- [ ] Database validation (all queries working)
- [ ] Audit trails logging

**Expected Output**:
- ✅ 20 total API endpoints working (11 new + 9 fixes)
- ✅ 5 new database tables
- ✅ All CORS issues resolved
- ✅ Response format standardized
- ✅ Backend ready for frontend integration

---

## 📊 SUCCESS CRITERIA

| Metric | Target | Acceptance |
|--------|--------|-----------|
| **Endpoints Working** | 20/20 | All endpoints return 200 status |
| **Database** | 5 tables | All migrations successful |
| **Error Handling** | 100% | All endpoints handle errors gracefully |
| **Performance** | <500ms | API response time acceptable |
| **Security** | Verified | Permission checks working |
| **Audit Trail** | 100% | All changes logged |

---

**Status**: 🟡 PHASE 2 READY TO BEGIN  
**Timeline**: 2-3 days  
**Next**: Proceed to implementation

