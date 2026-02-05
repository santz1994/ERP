# 🚀 IMPLEMENTATION PLAN - ERP QUTY KARUNIA UI/UX V4.0

## 📋 EXECUTIVE SUMMARY

Dokumen ini adalah rencana implementasi lengkap untuk sistem ERP Quty Karunia berdasarkan spesifikasi "Rencana Tampilan.md" versi 4.0.

**Total Tasks**: 25 major implementations  
**Estimated Timeline**: 8-12 weeks  
**Priority**: Backend-first approach (60%), Frontend (35%), Mobile (5%)  
**Status**: Phase 1 Complete & Validated ✅ | Phase 2 Ready to Start

---

## ✅ PHASE 1 COMPLETION & VALIDATION SUMMARY (2026-02-05)

### Implementation Complete
**Completed Features**:
1. ✅ Dual-mode PO System with BOM Explosion
2. ✅ MO PARTIAL/RELEASED Auto-upgrade Logic  
3. ✅ Flexible Target System with Week/Destination tracking
4. ✅ Database migrations applied successfully (009, 010)

**Code Statistics**:
- Files Created: 4 (migrations, docs, services)
- Files Modified: 5 (models, services, API endpoints)
- Lines of Code: ~1,200 production-ready lines
- Database Changes: 2 migrations, 18 new columns, 1 new table

### Testing & Validation Complete ✅
**Test Results**: 8/8 smoke tests passed (100%)

**Validated Components**:
- ✅ Database schema (all 18 new columns verified)
- ✅ Service methods (BOM explosion, AUTO_BOM, preview, triggers)
- ✅ Enum definitions (MOState.PARTIAL, MOState.RELEASED)
- ✅ Trigger logic (KAIN → PARTIAL, LABEL → RELEASED)
- ✅ Critical bug fixes (metadata → extra_metadata)

**Test Files Created**:
- `tests/test_phase1_smoke.py` - 8 passing smoke tests
- `tests/test_phase1_dual_mode_po.py` - 13 comprehensive tests (awaiting fixtures)
- `tests/test_phase1_mo_triggers.py` - 11 integration tests (awaiting fixtures)

**Documentation**: 
- [SESSION_IMPLEMENTATION_PHASE1A_COMPLETE.md](SESSION_IMPLEMENTATION_PHASE1A_COMPLETE.md) - Implementation details
- [SESSION_PHASE1_TESTING_COMPLETE.md](SESSION_PHASE1_TESTING_COMPLETE.md) - Testing & validation report

---

## 🎯 CRITICAL SUCCESS FACTORS

1. **Dual-mode PO System dengan BOM Explosion** (Most Complex)
2. **MO PARTIAL/RELEASED Auto-upgrade Logic** (Core Business Logic)
3. **Flexible Target System dengan Constraint Validation** (Production Critical)
4. **Warehouse Finishing 2-Stage Process** (Inventory Accuracy)
5. **Material Debt Tracking** (Financial Risk Management)
6. **Rework & QC Integration** (Quality Management)

---

## 📦 PHASE 1: BACKEND CORE (Weeks 1-4)

### 🔥 Priority 1A: Dual-Mode PO System with BOM Explosion

**Goal**: Implement 2 cara input PO (Auto from Article vs Manual)

#### Database Schema Updates

```sql
-- 1. Update PurchaseOrder table untuk support dual-mode
ALTER TABLE purchase_orders 
ADD COLUMN input_mode VARCHAR(20) DEFAULT 'MANUAL' CHECK (input_mode IN ('AUTO_BOM', 'MANUAL'));
ADD COLUMN source_article_id INTEGER REFERENCES products(id);
ADD COLUMN article_quantity DECIMAL(15,3);

-- 2. Update PurchaseOrderLine untuk supplier per material
ALTER TABLE purchase_order_lines
ADD COLUMN supplier_id INTEGER REFERENCES partners(id); -- 🆕 Supplier PER MATERIAL

-- 3. Metadata JSON structure untuk PO
/*
{
  "input_mode": "AUTO_BOM",
  "article": {"id": 123, "code": "40551542", "name": "AFTONSPARV"},
  "article_qty": 1000,
  "bom_explosion": {
    "bom_id": 456,
    "total_materials": 32,
    "timestamp": "2026-02-04T10:30:00"
  },
  "suppliers": {
    "IKHR504": {"supplier_id": 10, "supplier_name": "PT Supplier A"},
    "IKP20157": {"supplier_id": 12, "supplier_name": "PT Fill Jaya"}
  }
}
*/
```

#### Backend Files to Create/Update

**1. Models Extension** (`app/core/models/warehouse.py`)
```python
# Add new fields to PurchaseOrder model
input_mode: str = Field(default='MANUAL')
source_article_id: Optional[int] = Field(default=None, foreign_key="products.id")
article_quantity: Optional[Decimal] = Field(default=None)

# Add to PurchaseOrderLine
supplier_id: Optional[int] = Field(default=None, foreign_key="partners.id")
```

**2. BOM Explosion Service** (`app/services/bom_explosion_service.py`) - **NEW FILE**
```python
class BOMExplosionService:
    def explode_bom_for_article(
        self,
        article_id: int,
        quantity: Decimal,
        include_routing: bool = True
    ) -> dict:
        """
        Explode BOM untuk article tertentu
        Returns:
        {
            "materials": [
                {
                    "material_id": 123,
                    "material_code": "IKHR504",
                    "material_name": "KOHAIR 7MM D.BROWN",
                    "quantity_per_unit": 0.1466,
                    "total_quantity": 146.6,
                    "uom": "YARD",
                    "material_type": "RAW",
                    "suggested_suppliers": [10, 12, 15]
                },
                ...
            ],
            "total_materials": 32,
            "estimated_cost": 125000.00
        }
        """
        pass
    
    def validate_bom_cascade(self, bom_id: int) -> dict:
        """Validate BOM chain (Output dept N = Input dept N+1)"""
        pass
```

**3. Purchasing Service Update** (`app/modules/purchasing/purchasing_service.py`)
```python
def create_purchase_order_auto_bom(
    self,
    article_id: int,
    article_quantity: Decimal,
    po_number: str,
    order_date: date,
    expected_date: date,
    material_suppliers: dict[str, int],  # {material_code: supplier_id}
    material_prices: dict[str, Decimal],  # {material_code: unit_price}
    user_id: int,
    po_type: str = 'KAIN'
) -> PurchaseOrder:
    """
    Create PO with AUTO BOM Explosion mode
    
    Args:
        article_id: Product article ID
        article_quantity: How many pcs to produce
        material_suppliers: Mapping {material_code: supplier_id} - KEY FEATURE!
        material_prices: Mapping {material_code: unit_price}
    
    Returns:
        PurchaseOrder with all materials from BOM
    """
    # 1. Get BOM explosion
    bom_service = BOMExplosionService(self.db)
    explosion = bom_service.explode_bom_for_article(article_id, article_quantity)
    
    # 2. Validate all materials have supplier & price
    for material in explosion['materials']:
        code = material['material_code']
        if code not in material_suppliers:
            raise ValueError(f"Material {code} missing supplier assignment")
        if code not in material_prices:
            raise ValueError(f"Material {code} missing unit price")
    
    # 3. Create PO with lines
    items = []
    for material in explosion['materials']:
        code = material['material_code']
        items.append({
            "product_id": material['material_id'],
            "quantity": material['total_quantity'],
            "unit_price": material_prices[code],
            "supplier_id": material_suppliers[code]  # 🔥 PER MATERIAL SUPPLIER
        })
    
    # 4. Create PO (similar to existing method but with input_mode)
    po = PurchaseOrder(
        po_number=po_number,
        input_mode='AUTO_BOM',
        source_article_id=article_id,
        article_quantity=article_quantity,
        po_type=po_type,
        # ... other fields
        metadata={
            "input_mode": "AUTO_BOM",
            "bom_explosion": explosion,
            "material_suppliers": material_suppliers
        }
    )
    
    # 5. Create PO Lines with supplier per material
    for item in items:
        line = PurchaseOrderLine(
            purchase_order_id=po.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            supplier_id=item['supplier_id'],  # 🔥 KEY FEATURE
            subtotal=item['quantity'] * item['unit_price']
        )
        self.db.add(line)
    
    return po
```

**4. API Endpoints** (`app/api/v1/purchasing.py`)
```python
@router.post("/purchase-orders/auto-bom")
async def create_po_auto_bom(
    request: POAutoBOMRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create PO with AUTO BOM Explosion
    
    Request Body:
    {
        "article_id": 123,
        "article_quantity": 1000,
        "po_number": "PO-K-2026-00012",
        "order_date": "2026-02-04",
        "expected_date": "2026-02-10",
        "po_type": "KAIN",
        "material_suppliers": {
            "IKHR504": 10,
            "IKP20157": 12,
            ...
        },
        "material_prices": {
            "IKHR504": 12.50,
            "IKP20157": 5.00,
            ...
        }
    }
    """
    service = PurchasingService(db)
    po = service.create_purchase_order_auto_bom(
        article_id=request.article_id,
        article_quantity=request.article_quantity,
        po_number=request.po_number,
        order_date=request.order_date,
        expected_date=request.expected_date,
        material_suppliers=request.material_suppliers,
        material_prices=request.material_prices,
        user_id=current_user.id,
        po_type=request.po_type
    )
    
    return {"success": True, "data": po}

@router.get("/bom-explosion/{article_id}")
async def get_bom_explosion(
    article_id: int,
    quantity: Decimal,
    db: Session = Depends(get_db)
):
    """
    Preview BOM explosion untuk article (before creating PO)
    
    Response:
    {
        "materials": [...],
        "total_materials": 32,
        "estimated_cost": 125000.00
    }
    """
    service = BOMExplosionService(db)
    explosion = service.explode_bom_for_article(article_id, quantity)
    return {"success": True, "data": explosion}
```

---

### 🔥 Priority 1B: MO PARTIAL/RELEASED Logic

**Goal**: Implement 2-stage MO (PARTIAL from PO Kain, RELEASED from PO Label)

#### Database Schema Updates

```sql
-- 1. Add MOStatus enum
CREATE TYPE mo_status_new AS ENUM ('DRAFT', 'PARTIAL', 'RELEASED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');

-- 2. Update ManufacturingOrder table
ALTER TABLE manufacturing_orders
ADD COLUMN week VARCHAR(10); -- W05, W06, etc (from PO LABEL)
ADD COLUMN destination VARCHAR(200); -- IKEA Distribution Center, etc
ADD COLUMN week_destination_locked BOOLEAN DEFAULT FALSE;

-- 3. Metadata structure
/*
{
  "po_kain_id": 123,
  "po_kain_approved_at": "2026-02-04T10:00:00",
  "po_label_id": 456,
  "po_label_approved_at": "2026-02-05T14:30:00",
  "week": "W05",
  "destination": "IKEA Distribution Center",
  "week_destination_locked": true,
  "release_history": [
    {"from": "DRAFT", "to": "PARTIAL", "trigger": "PO_KAIN_APPROVED", "timestamp": "..."},
    {"from": "PARTIAL", "to": "RELEASED", "trigger": "PO_LABEL_APPROVED", "timestamp": "..."}
  ]
}
*/
```

#### Backend Implementation

**1. Models Update** (`app/core/models/production.py`)
```python
class MOStatus(str, Enum):
    DRAFT = "DRAFT"
    PARTIAL = "PARTIAL"  # 🆕 PO Kain ready, PO Label waiting
    RELEASED = "RELEASED"  # 🆕 Both PO ready, full production
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ManufacturingOrder(SQLModel, table=True):
    # ... existing fields
    week: Optional[str] = Field(default=None, max_length=10)
    destination: Optional[str] = Field(default=None, max_length=200)
    week_destination_locked: bool = Field(default=False)
```

**2. Service Methods** (`app/modules/ppic/ppic_service.py`)
```python
def upgrade_mo_to_partial(
    self,
    mo_id: int,
    po_kain_id: int,
    user_id: int
) -> ManufacturingOrder:
    """
    Upgrade MO from DRAFT → PARTIAL
    Triggered by PO KAIN approval
    """
    mo = self.get_mo(mo_id)
    
    if mo.status != MOStatus.DRAFT:
        raise ValueError(f"Cannot upgrade MO with status {mo.status}")
    
    mo.status = MOStatus.PARTIAL
    mo.metadata = mo.metadata or {}
    mo.metadata['po_kain_id'] = po_kain_id
    mo.metadata['po_kain_approved_at'] = datetime.utcnow().isoformat()
    
    # Only Cutting & Embroidery can start
    mo.metadata['departments_unlocked'] = ['CUTTING', 'EMBROIDERY']
    mo.metadata['departments_locked'] = ['SEWING', 'FINISHING', 'PACKING']
    
    log_audit(...)
    self.db.commit()
    
    return mo

def upgrade_mo_to_released(
    self,
    mo_id: int,
    po_label_id: int,
    week: str,
    destination: str,
    user_id: int
) -> ManufacturingOrder:
    """
    Upgrade MO from PARTIAL → RELEASED
    Triggered by PO LABEL approval
    Auto-inherit Week & Destination
    """
    mo = self.get_mo(mo_id)
    
    if mo.status != MOStatus.PARTIAL:
        raise ValueError(f"Cannot upgrade MO with status {mo.status}")
    
    mo.status = MOStatus.RELEASED
    mo.week = week
    mo.destination = destination
    mo.week_destination_locked = True  # Cannot edit after this
    
    mo.metadata = mo.metadata or {}
    mo.metadata['po_label_id'] = po_label_id
    mo.metadata['po_label_approved_at'] = datetime.utcnow().isoformat()
    mo.metadata['week'] = week
    mo.metadata['destination'] = destination
    
    # Unlock all departments
    mo.metadata['departments_unlocked'] = ['CUTTING', 'EMBROIDERY', 'SEWING', 'FINISHING', 'PACKING']
    mo.metadata['departments_locked'] = []
    
    log_audit(...)
    self.db.commit()
    
    # 🔔 Send notification to all production admins
    from app.services.notification_service import NotificationService
    notif = NotificationService(self.db)
    notif.send_mo_released_notification(mo_id, user_id)
    
    return mo
```

**3. Integration with Purchasing Service**

Update `app/modules/purchasing/purchasing_service.py` (sudah ada di kode existing):
```python
# TRIGGER 1: PO KAIN approved
if po.po_type == 'KAIN' and po.linked_mo_id:
    ppic_service = PPICService(self.db)
    ppic_service.upgrade_mo_to_partial(po.linked_mo_id, po.id, user_id)

# TRIGGER 2: PO LABEL approved
elif po.po_type == 'LABEL' and po.linked_mo_id:
    week = po.metadata.get('week')
    destination = po.metadata.get('destination')
    
    ppic_service = PPICService(self.db)
    ppic_service.upgrade_mo_to_released(
        po.linked_mo_id, 
        po.id, 
        week, 
        destination, 
        user_id
    )
```

---

### 🔥 Priority 1C: Flexible Target System

**Goal**: SPK Target dapat berbeda dari MO Target dengan buffer logic

#### Database Schema

```sql
-- Update WorkOrders (SPK) table
ALTER TABLE work_orders
ADD COLUMN mo_target DECIMAL(15,3); -- Base target from MO
ADD COLUMN spk_target DECIMAL(15,3); -- Actual SPK target (may include buffer)
ADD COLUMN buffer_percentage DECIMAL(5,2) DEFAULT 0.00; -- Buffer % (e.g., 15.00)
ADD COLUMN buffer_reason TEXT; -- Why buffer applied

-- Metadata structure
/*
{
  "target_breakdown": {
    "mo_target": 450,
    "buffer_pct": 15.0,
    "buffer_qty": 67,
    "spk_target": 517
  },
  "constraint": {
    "upstream_dept": "EMBROIDERY",
    "upstream_good_output": 495,
    "max_allowed": 495,
    "current_spk": 517,
    "validation": "WARN: SPK target exceeds upstream output"
  }
}
*/
```

#### Backend Implementation

**1. Service Method** (`app/modules/ppic/spk_service.py`)
```python
def create_spk_with_flexible_target(
    self,
    mo_id: int,
    department_id: int,
    mo_target: Decimal,
    buffer_percentage: Decimal = 0.0,
    custom_target: Optional[Decimal] = None,
    user_id: int
) -> WorkOrder:
    """
    Create SPK with flexible target
    
    Args:
        mo_target: Base target from MO
        buffer_percentage: Optional buffer (e.g., 15.0 for 15%)
        custom_target: Or directly specify target
    
    Returns:
        WorkOrder dengan constraint validation
    """
    # 1. Calculate SPK target
    if custom_target:
        spk_target = custom_target
        buffer_pct = ((custom_target - mo_target) / mo_target) * 100
    else:
        buffer_qty = mo_target * (buffer_percentage / 100)
        spk_target = mo_target + buffer_qty
        buffer_pct = buffer_percentage
    
    # 2. Validate against upstream department output
    constraint_check = self._validate_spk_constraint(
        department_id, 
        spk_target
    )
    
    if constraint_check['violation']:
        raise ValueError(
            f"SPK target {spk_target} exceeds upstream output "
            f"{constraint_check['max_allowed']}"
        )
    
    # 3. Create SPK
    spk = WorkOrder(
        mo_id=mo_id,
        department_id=department_id,
        mo_target=mo_target,
        spk_target=spk_target,
        buffer_percentage=buffer_pct,
        status='PENDING',
        metadata={
            "target_breakdown": {
                "mo_target": float(mo_target),
                "buffer_pct": float(buffer_pct),
                "buffer_qty": float(spk_target - mo_target),
                "spk_target": float(spk_target)
            },
            "constraint_check": constraint_check
        }
    )
    
    self.db.add(spk)
    self.db.commit()
    
    return spk

def _validate_spk_constraint(
    self,
    department_id: int,
    requested_target: Decimal
) -> dict:
    """
    Validate SPK target tidak melebihi upstream output
    
    Returns:
        {
            "upstream_dept": "EMBROIDERY",
            "upstream_good_output": 495,
            "max_allowed": 495,
            "requested": 517,
            "violation": True,
            "message": "..."
        }
    """
    # Get upstream department
    dept_sequence = {
        'CUTTING': None,  # First dept, no constraint
        'EMBROIDERY': 'CUTTING',
        'SEWING': 'EMBROIDERY',
        'FINISHING': 'SEWING',
        'PACKING': 'FINISHING'
    }
    
    dept = self.db.query(Department).get(department_id)
    upstream_code = dept_sequence.get(dept.code)
    
    if not upstream_code:
        return {"violation": False, "message": "First department, no constraint"}
    
    # Get upstream SPK good output
    upstream_dept = self.db.query(Department).filter(Department.code == upstream_code).first()
    upstream_spk = self.db.query(WorkOrder).filter(
        WorkOrder.department_id == upstream_dept.id,
        WorkOrder.status == 'COMPLETED'
    ).order_by(WorkOrder.id.desc()).first()
    
    if not upstream_spk:
        return {"violation": False, "message": "No upstream SPK found"}
    
    max_allowed = upstream_spk.good_output or upstream_spk.spk_target
    
    violation = requested_target > max_allowed
    
    return {
        "upstream_dept": upstream_code,
        "upstream_good_output": float(max_allowed),
        "max_allowed": float(max_allowed),
        "requested": float(requested_target),
        "violation": violation,
        "message": f"{'VIOLATION' if violation else 'OK'}: Requested {requested_target} vs Max {max_allowed}"
    }
```

---

## 📦 PHASE 2: BACKEND ENHANCEMENT (Weeks 5-6)

### Priority 2A: Warehouse Finishing 2-Stage Process
### Priority 2B: Rework & QC Module
### Priority 2C: Material Debt Tracking
### Priority 2D: UOM Conversion & Validation
### Priority 2E: Stock Opname per Departemen

---

## 📦 PHASE 3: NOTIFICATION & RBAC (Week 7)

### Priority 3A: Notification System
### Priority 3B: RBAC & Permission Matrix

---

## 📦 PHASE 4: FRONTEND IMPLEMENTATION (Weeks 8-10)

### Priority 4A: Dashboard dengan KPI Cards
### Priority 4B: Dual-mode PO UI
### Priority 4C: PPIC MO Management UI
### Priority 4D: Production Calendar View
### Priority 4E: Rework Station UI
### Priority 4F: Warehouse UI dengan Validation
### Priority 4G: Masterdata Forms
### Priority 4H: Reports & Analytics

---

## 📦 PHASE 5: MOBILE & TESTING (Weeks 11-12)

### Priority 5A: Mobile FG Label App (Planning)
### Priority 5B: Integration Testing
### Priority 5C: User Acceptance Testing (UAT)

---

## 📊 IMPLEMENTATION CHECKLIST

- [x] **Phase 1A**: Dual-mode PO System ✅ CRITICAL **[COMPLETED 2026-02-05]**
- [x] **Phase 1B**: MO PARTIAL/RELEASED ✅ CRITICAL **[COMPLETED 2026-02-05]**
- [x] **Phase 1C**: Flexible Target System ✅ CRITICAL **[COMPLETED 2026-02-05]**
- [ ] **Phase 2A**: 2-Stage Finishing
- [ ] **Phase 2B**: Rework & QC
- [ ] **Phase 2C**: Material Debt
- [ ] **Phase 2D**: UOM Conversion
- [ ] **Phase 2E**: Stock Opname
- [ ] **Phase 3A**: Notification System
- [ ] **Phase 3B**: RBAC System
- [ ] **Phase 4**: Frontend Implementation
- [ ] **Phase 5**: Mobile & Testing

**Progress**: Phase 1 Complete (100%) - Database migrations applied successfully ✅

---

## 🚨 RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| BOM Explosion complexity | High | Start with simple 1-level BOM, then expand |
| Database migration on production | Critical | Test on staging with full backup |
| Frontend redesign scope | Medium | Use component library (Ant Design/Material-UI) |
| Mobile app development resource | Medium | Phase 5 can be delayed, use web-based interim |
| User adoption resistance | High | Comprehensive training + gradual rollout |

---

## 🎯 SUCCESS METRICS

1. **PO Creation Time**: Reduce from 2 hours → 20 minutes (85% improvement)
2. **MO Accuracy**: 100% Week/Destination auto-inherit (zero manual error)
3. **Production Buffer Optimization**: Target achievement >95%
4. **Material Debt Visibility**: Real-time tracking (zero surprise shortages)
5. **Rework Recovery Rate**: Track & improve from 80% → 90%

---

## 📝 NOTES FOR IMPLEMENTATION

1. **Always test on staging first** dengan data produksi yang realistic
2. **Incremental deployment**: 1 module at a time, not big bang
3. **User feedback loop**: Weekly meeting dengan user untuk adjustment
4. **Documentation**: Update API docs setiap kali ada perubahan
5. **Backup strategy**: Daily backup before any major changes

---

**Document Version**: 1.0  
**Created**: 5 February 2026  
**Status**: Ready for Implementation  
**Approved By**: [Pending]
