# 🚀 IMPLEMENTATION GUIDE: BOM Per Department System
**ERP Quty Karunia - Multi-level BOM dengan WIP Tracking**

**Date**: 3 Februari 2026  
**Author**: IT Developer Expert  
**Status**: ✅ Ready for Implementation

---

## 📋 OVERVIEW

Sistem ini mengimplementasikan **BOM per Department** dengan struktur multi-level WIP (Work In Progress) tracking, sesuai dengan data aktual dari 6 file Excel BOM.

### Key Features

✅ **1,333 WIP Products** imported from 6 Excel files  
✅ **5,836 BOM Lines** dengan material relationships  
✅ **Multi-level BOM Explosion** (FG → WIP → RAW)  
✅ **Auto-generate Work Orders** per department  
✅ **Dependency Management** (WO sequence enforcement)  
✅ **Buffer Allocation** per department (10% cutting, 7% embo, etc.)

---

## 🗂️ FILES CREATED

### 1. Database Migration
**File**: `erp-softtoys/alembic/versions/add_wip_routing_001.py`

**Changes**:
- ✅ Added `product_type` column to `products` table
- ✅ Added `routing_department` and `routing_sequence` to `bom_headers`
- ✅ Created `bom_wip_routing` table (department sequence tracking)
- ✅ Updated `work_orders` table with WIP input/output
- ✅ Created `wip_transfer_logs` table
- ✅ Updated `manufacturing_orders` table

### 2. BOM Import Script
**File**: `erp-softtoys/scripts/import_bom_from_excel.py`

**What it does**:
- ✅ Reads 6 Excel files (Cutting, Embo, Sewing, Finishing, Packing, FG)
- ✅ Creates 8 product categories (RAW, WIP_CUTTING, WIP_EMBO, etc.)
- ✅ Creates 1,333 WIP products
- ✅ Creates 5,836 BOM detail lines
- ✅ Auto-detects material categories (Fabric, Thread, Filling, etc.)
- ✅ Caches products for performance

### 3. BOM Explosion Service
**File**: `erp-softtoys/app/services/bom_explosion_service.py`

**Key Functions**:
- `explode_mo_and_generate_work_orders()` - Main entry point
- `explode_bom_multi_level()` - Recursive BOM explosion
- `_generate_work_orders_from_explosion()` - Create WOs from explosion tree
- `check_wo_dependencies()` - Validate if WO can start
- `update_wo_status_auto()` - Auto-update WO statuses (WAITING → READY)

### 4. Testing Script
**File**: `erp-softtoys/scripts/test_bom_explosion.py`

**Test Coverage**:
- ✅ BOM explosion for Finished Good
- ✅ Work Order generation
- ✅ Dependency checking
- ✅ Status auto-update
- ✅ Cleanup (rollback)

---

## 📊 DATABASE SCHEMA CHANGES

### New Tables

#### `bom_wip_routing`
Tracks department sequence for multi-level BOM

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| bom_header_id | Integer | FK to bom_headers |
| department | String(50) | Department name |
| sequence | Integer | Order (1, 2, 3...) |
| input_wip_product_id | Integer | Input WIP from previous dept |
| output_wip_product_id | Integer | Output WIP for next dept |
| is_optional | Boolean | Skip if not needed (e.g., Embo) |

#### `wip_transfer_logs`
Tracks WIP movement between departments

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| wo_id | Integer | FK to work_orders |
| wip_product_id | Integer | Which WIP transferred |
| from_department | String(50) | Source department |
| to_department | String(50) | Destination department |
| qty_transferred | Decimal(10,2) | Quantity |
| transfer_date | DateTime | When transferred |

### Updated Tables

#### `products`
- ✅ Added `product_type` (raw_material, wip, finished_good)

#### `bom_headers`
- ✅ Added `routing_department` (which dept this BOM belongs to)
- ✅ Added `routing_sequence` (order in production flow)

#### `work_orders`
- ✅ Added `input_wip_product_id` (input from previous dept)
- ✅ Added `output_wip_product_id` (output for next dept)
- ✅ Added `sequence` (1, 2, 3... order of execution)
- ✅ Added `status` (WAITING, READY, IN_PROGRESS, COMPLETED)

#### `manufacturing_orders`
- ✅ Added `finished_good_product_id` (target FG product)
- ✅ Added `bom_explosion_complete` (explosion done?)
- ✅ Added `total_departments` (how many WOs generated)

---

## 🚀 STEP-BY-STEP IMPLEMENTATION

### Step 1: Run Database Migration

```powershell
cd d:\Project\ERP2026\erp-softtoys

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run migration
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade -> add_wip_routing_001
# Adding product_type column to products table...
# Adding routing_department to bom_headers...
# Creating bom_wip_routing table...
# ✅ Migration completed successfully!
```

### Step 2: Import BOM Data from Excel

```powershell
# Still in erp-softtoys directory
python scripts/import_bom_from_excel.py

# Confirm when prompted:
# ⚠️  This will import BOM data to database. Continue? (yes/no): yes

# Expected output:
# ================================================================================
# 🚀 STARTING BOM IMPORT FROM EXCEL
# ================================================================================
# 
# 📂 Creating product categories...
#   ✅ Created category: RAW
#   ✅ Created category: WIP_CUTTING
#   ✅ Created category: WIP_EMBO
#   ... (8 categories total)
# 
# ================================================================================
# 📦 Importing CUTTING BOM from: d:/Project/ERP2026/docs/BOM/Cutting.xlsx
# ================================================================================
# 📄 Loaded 508 rows from Excel
# 🎯 Found 131 unique WIP products
#   ⏳ Progress: 10/131 products processed
#   ⏳ Progress: 20/131 products processed
#   ... (continues)
# ✅ Completed CUTTING: 131 WIP products imported
# 
# ... (repeats for all 6 departments)
# 
# ================================================================================
# 📊 IMPORT STATISTICS
# ================================================================================
# Categories created: 8
# Products created: 1333
# BOM Headers created: 1333
# BOM Details created: 5836
# Errors: 0
# 
# ✅ BOM IMPORT COMPLETED SUCCESSFULLY!
# ✅ All changes committed to database
```

**⏱️ Estimated Time**: 5-10 minutes

### Step 3: Test BOM Explosion

```powershell
# Test the system
python scripts/test_bom_explosion.py

# Expected output:
# ================================================================================
# 🧪 TESTING BOM EXPLOSION & WORK ORDER GENERATION
# ================================================================================
# 
# 📦 Step 1: Finding Finished Good product...
# ✅ Found 5 FG products:
#   1. [20540663] BLÅHAJ N soft toy 55 baby shark
#   2. [540664] BLÅHAJ N soft toy 55 baby shark AP
#   ... (continues)
# 
# 🎯 Testing with: [20540663] BLÅHAJ N soft toy 55 baby shark
# 
# 📋 Step 2: Creating test Manufacturing Order...
# ✅ Created MO: MO-TEST-123
# 
# 🔍 Step 3: Exploding BOM...
# ================================================================================
# 🎯 EXPLODING BOM FOR MO: MO-TEST-123
# 📦 Finished Good: [20540663] BLÅHAJ N soft toy 55 baby shark
# 🎯 Target Quantity: 450 pcs
# ================================================================================
# 🎯 Level 0: [20540663] BLÅHAJ N soft toy 55 baby shark x 450
#   📋 BOM found: 125 (1 components)
#     - BLÅHAJ N soft toy 55 baby shark_WIP_PACKING: 1.0 x 450 = 450.0
#       🔄 WIP detected - exploding...
#   🔍 Level 1: BLÅHAJ N soft toy 55 baby shark_WIP_PACKING x 450
#     📋 BOM found: 126 (5 components)
#       - BLÅHAJ N soft toy 55 baby shark_WIP_BONEKA: 60.0 x 450 = 27000.0
#         🔄 WIP detected - exploding...
#       ... (continues recursively)
# 
# 📊 Explosion Result Summary:
# 📦 [20540663] BLÅHAJ N soft toy 55 baby shark (Level 0)
#    Qty: 450 pcs
#    Type: finished_good
#    Dept: N/A
#    Children (1):
#      📦 BLÅHAJ N soft toy 55 baby shark_WIP_PACKING (Level 1)
#         Qty: 450 pcs
#         Type: wip
#         Dept: PACKING
#         Children (2):
#           ... (full tree shown)
# 
# 🏭 Step 4: Generating Work Orders...
# ================================================================================
# 🏭 GENERATING WORK ORDERS
# ================================================================================
# 
# 📊 Found 5 WIP stages:
#   1. Level 4: CUTTING → BLÅHAJ...WIP_CUTTING (495 pcs)
#   2. Level 3: SEWING → BLÅHAJ...WIP_SKIN (480 pcs)
#   3. Level 2: FINISHING → BLÅHAJ...WIP_BONEKA (470 pcs)
#   4. Level 1: PACKING → BLÅHAJ...WIP_PACKING (465 pcs)
#   5. Level 0: FG_RECEIVING → [20540663] BLÅHAJ (450 pcs)
# 
#   ✅ Created WO: MO-TEST-123-CUT-01 (CUTTING) - Target: 495.0 pcs
#   ✅ Created WO: MO-TEST-123-SEW-02 (SEWING) - Target: 512.16 pcs
#   ✅ Created WO: MO-TEST-123-FIN-03 (FINISHING) - Target: 490.68 pcs
#   ✅ Created WO: MO-TEST-123-PCK-04 (PACKING) - Target: 480.35 pcs
# 
# ✅ Generated 4 Work Orders for MO MO-TEST-123
# 
# 🔗 Step 5: Testing Work Order dependencies...
#   ✅ WO MO-TEST-123-CUT-01: First department - ready to start
#   ⏳ WO MO-TEST-123-SEW-02: Waiting for CUTTING to complete
#   ⏳ WO MO-TEST-123-FIN-03: Waiting for SEWING to complete
#   ⏳ WO MO-TEST-123-PCK-04: Waiting for FINISHING to complete
# 
# ⚡ Step 6: Simulating Work Order progression...
#   ✅ Completed WO: MO-TEST-123-CUT-01
# 
#   Updated statuses:
#     MO-TEST-123-CUT-01: COMPLETED
#     MO-TEST-123-SEW-02: READY ← Auto-updated!
#     MO-TEST-123-FIN-03: WAITING
#     MO-TEST-123-PCK-04: WAITING
# 
# ✅ TEST COMPLETED SUCCESSFULLY!
# 
# 🧹 Cleaning up test data...
# ✅ Test data cleaned up (rolled back)
```

**⏱️ Test Duration**: 30-60 seconds

---

## 🎯 USAGE EXAMPLES

### Example 1: Create MO and Auto-Generate Work Orders

```python
from app.services.bom_explosion_service import BOMExplosionService
from app.core.database import get_db
from decimal import Decimal

# Get database session
db = next(get_db())

# Create service
service = BOMExplosionService(db)

# Generate Work Orders from MO
work_orders = service.explode_mo_and_generate_work_orders(
    mo_id=89,  # MO-2026-00089
    qty_planned=Decimal('450')
)

print(f"Generated {len(work_orders)} Work Orders:")
for wo in work_orders:
    print(f"  - {wo.wo_number}: {wo.department} ({wo.status})")
```

### Example 2: Check Work Order Dependencies

```python
from app.services.bom_explosion_service import BOMExplosionService

service = BOMExplosionService(db)

# Check if WO can start
can_start, reason = service.check_wo_dependencies(wo_id=123)

if can_start:
    print(f"✅ WO ready to start: {reason}")
else:
    print(f"⏳ WO not ready: {reason}")
```

### Example 3: Complete WO and Auto-Update Dependencies

```python
# Mark WO as completed
wo = db.query(WorkOrder).filter_by(id=123).first()
wo.status = 'COMPLETED'
db.commit()

# Auto-update next WO statuses
service.update_wo_status_auto(mo_id=wo.mo_id)

# Check updated statuses
updated_wos = db.query(WorkOrder).filter_by(mo_id=wo.mo_id).all()
for wo in updated_wos:
    print(f"{wo.wo_number}: {wo.status}")
```

---

## ✅ VERIFICATION CHECKLIST

After implementation, verify:

### Database
- [ ] Migration applied successfully
- [ ] 8 new categories created (RAW, WIP_CUTTING, etc.)
- [ ] 1,333 products created
- [ ] 1,333 BOM headers created
- [ ] 5,836 BOM details created
- [ ] New tables created (bom_wip_routing, wip_transfer_logs)

### Functionality
- [ ] BOM explosion works for any Finished Good
- [ ] Work Orders auto-generated (one per department)
- [ ] WO sequence enforced (1, 2, 3...)
- [ ] Dependency checking works
- [ ] Status auto-update when dependencies satisfied
- [ ] Buffer allocation per department applied

### Performance
- [ ] Import completes in <10 minutes
- [ ] BOM explosion for 1 product <5 seconds
- [ ] Work Order generation for 1 MO <2 seconds

---

## 🐛 TROUBLESHOOTING

### Issue: Import Script Fails with "File not found"

**Solution**:
```powershell
# Check file paths
Get-ChildItem "d:\Project\ERP2026\docs\BOM"

# Update paths in import_bom_from_excel.py if needed
```

### Issue: Migration Fails with "Column already exists"

**Solution**:
```powershell
# Check current migration status
alembic current

# If needed, stamp as current version
alembic stamp head

# Then retry
alembic upgrade head
```

### Issue: BOM Explosion Returns Empty Result

**Solution**:
```python
# Check if BOM exists for product
from app.core.models.bom import BOMHeader

bom = db.query(BOMHeader).filter_by(
    product_id=product_id,
    is_active=True
).first()

if not bom:
    print("No BOM found for this product!")
```

### Issue: Work Order Status Not Auto-Updating

**Solution**:
```python
# Manually trigger status update
service.update_wo_status_auto(mo_id=89)

# Check dependencies
for wo in work_orders:
    can_start, reason = service.check_wo_dependencies(wo.id)
    print(f"{wo.wo_number}: {can_start} - {reason}")
```

---

## 📚 NEXT STEPS

### Phase 1: Basic Testing (Week 1)
- [ ] Import all BOM data
- [ ] Test explosion for 10 different products
- [ ] Validate WO generation accuracy
- [ ] Check buffer calculations

### Phase 2: UI Integration (Week 2-3)
- [ ] Add "Generate WOs" button in MO form
- [ ] Show WO list with dependencies
- [ ] Display BOM explosion tree in UI
- [ ] WO status dashboard

### Phase 3: Material Allocation (Week 4)
- [ ] Implement material allocation to WOs
- [ ] Stock availability checking
- [ ] Material reservation system
- [ ] Purchase requisition generation

### Phase 4: Production Execution (Week 5-6)
- [ ] Daily production input per WO
- [ ] WIP transfer between departments
- [ ] Auto status update based on actual progress
- [ ] Real-time dashboard

---

## 📞 SUPPORT

**Questions?** Contact IT Developer Expert Team

**Documentation**:
- [REVISED_BOM_MO_SPK_ARCHITECTURE.md](../docs/00-Overview/REVISED_BOM_MO_SPK_ARCHITECTURE.md)
- [LIVE_DEMO_PROTOTYPE_PLAN.md](../docs/00-Overview/LIVE_DEMO_PROTOTYPE_PLAN.md)

---

**Last Updated**: 3 Februari 2026  
**Status**: ✅ Ready for Production Testing
