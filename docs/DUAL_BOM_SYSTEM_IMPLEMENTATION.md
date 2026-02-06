# 🔄 DUAL-BOM SYSTEM IMPLEMENTATION GUIDE

**Project**: ERP Quty Karunia - Manufacturing Soft Toys  
**Version**: 1.0  
**Date**: February 6, 2026  
**Status**: Implementation Ready  
**Impact**: HIGH - Changes core BOM structure and all dependent modules

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Business Problem](#business-problem)
3. [Solution: Dual-BOM System](#solution)
4. [System Architecture](#architecture)
5. [Database Schema](#database-schema)
6. [Data Migration](#data-migration)
7. [API Changes](#api-changes)
8. [Frontend Changes](#frontend-changes)
9. [Business Logic](#business-logic)
10. [Implementation Plan](#implementation-plan)
11. [Testing Strategy](#testing-strategy)

---

<a name="executive-summary"></a>
## 🎯 EXECUTIVE SUMMARY

### Current Problem
PT Quty Karunia currently has **ONE BOM system** that tries to serve **TWO different purposes**:
1. **Purchasing Department** needs to know: *"What RAW materials to buy from suppliers?"*
2. **PPIC/Production** needs to know: *"How to transform materials step-by-step through each department?"*

Using a single BOM creates confusion:
- Purchasing sees WIP components (not their concern)
- PPIC doesn't see department-specific routing clearly
- Material aggregation requires complex filtering
- Changes in one department affect other modules unexpectedly

### Solution: Dual-BOM System

**BOM PRODUCTION** (Process-Oriented):
- Split by department: Cutting → Embroidery → Sewing → Finishing → Packing
- Shows step-by-step transformation (SKIN → STUFFED BODY → FINISHED DOLL)
- Includes WIP components, material consumption per stage
- Used by: PPIC for MO/SPK explosion, Production departments for material requests

**BOM PURCHASING** (Material-Oriented):
- Consolidated view of **RAW materials ONLY**
- Aggregates all material needs across all departments
- Excludes WIP/internal components
- Used by: Purchasing for PO calculation, Inventory planning

### Key Benefits
- ✅ **Clear Separation of Concerns**: Each department sees only relevant BOM
- ✅ **Accurate Material Planning**: Purchasing sees aggregated raw materials
- ✅ **Better Production Tracking**: Each stage has explicit input/output
- ✅ **Easier Maintenance**: Changes in production process don't affect purchasing
- ✅ **Auto-Sync**: BOM Purchasing auto-generated from BOM Production

---

<a name="business-problem"></a>
## ❌ BUSINESS PROBLEM: Why We Need Dual-BOM

### Scenario: AFTONSPARV Bear Production

**Current Single BOM Problem**:
```
Article: AFTONSPARV Bear (40551542)
BOM (Mixed Production + Purchasing):
├─ [IKHR504] KOHAIR Fabric 0.15 YARD (RAW - needs purchasing)
├─ [IKP20157] Filling 54 GRAM (RAW - needs purchasing)
├─ [ATR10400] Thread 60 CM (RAW - needs purchasing)
├─ [ALL40030] Label 1 PCE (RAW - needs purchasing)
├─ AFTONSPARV_WIP_CUTTING 1 PCE (WIP - internal, confuses purchasing)
├─ AFTONSPARV_WIP_SKIN 1 PCE (WIP - internal, confuses purchasing)
├─ AFTONSPARV_WIP_STUFFED 1 PCE (WIP - internal, confuses purchasing)
└─ [ACB30104] Carton 0.0167 PCE (RAW - needs purchasing)
```

**Problem**:
- Purchasing Officer sees: *"Do I need to buy WIP_CUTTING? What is that?"*
- PPIC cannot see: *"Which materials go to Cutting vs Sewing?"*
- Material aggregation requires: *"Filter WHERE material_type = 'RAW_MATERIAL'"* (error-prone)

### Solution with Dual-BOM

**BOM PRODUCTION** (Department-Specific):

```
CUTTING DEPARTMENT:
Input: 
  - [IKHR504] KOHAIR Fabric 0.15 YARD
  - [IJBR105] BOA Fabric 0.0015 YARD
  - [INYR002] NYLEX 0.001 YARD
Output:
  - AFTONSPARV_WIP_CUTTING (Skin pieces cut)

SEWING DEPARTMENT:
Input:
  - AFTONSPARV_WIP_CUTTING 1 PCE
  - [ATR10400] Thread 60 CM
  - [ALL40030] Label 1 PCE
Output:
  - AFTONSPARV_WIP_SKIN (Sewn skin, no filling)

FINISHING STAGE 1 (Stuffing):
Input:
  - AFTONSPARV_WIP_SKIN 1 PCE
  - [IKP20157] Filling 54 GRAM
Output:
  - AFTONSPARV_WIP_STUFFED (Body with filling)

FINISHING STAGE 2 (Closing):
Input:
  - AFTONSPARV_WIP_STUFFED 1 PCE
  - [ALB40011] Hang Tag 1 PCE
Output:
  - AFTONSPARV_WIP_BONEKA (Finished doll)

PACKING DEPARTMENT:
Input:
  - AFTONSPARV_WIP_BONEKA 60 PCE
  - [ACB30104] Carton 1 PCE
Output:
  - [40551542] AFTONSPARV Bear (Finished Goods)
```

**BOM PURCHASING** (Auto-Generated Aggregation):

```
Article: AFTONSPARV Bear (40551542)
Total RAW Materials to Purchase (per 1 PCE finished):
├─ [IKHR504] KOHAIR Fabric: 0.15 YARD
├─ [IJBR105] BOA Fabric: 0.0015 YARD
├─ [INYR002] NYLEX: 0.001 YARD
├─ [IKP20157] Filling: 54 GRAM
├─ [ATR10400] Thread: 60 CM
├─ [ALL40030] Label: 1 PCE
├─ [ALB40011] Hang Tag: 1 PCE
└─ [ACB30104] Carton: 0.0167 PCE (60 pcs/carton)

Total: 7 raw materials (NO WIP components)
```

**Benefits**:
- ✅ Purchasing sees: "I need to buy 7 materials" (clear!)
- ✅ PPIC sees: "Production has 5 stages with specific inputs/outputs"
- ✅ Each department sees: "These are MY materials"
- ✅ Warehouse tracks: WIP inventory at each stage
- ✅ Costing calculates: Cost per department (labor + material)

---

<a name="solution"></a>
## 🌟 SOLUTION: DUAL-BOM SYSTEM

### Core Concept

```
┌─────────────────────────────────────────────────────────────┐
│                     MASTERDATA                               │
│  ┌──────────────┐        ┌──────────────────┐               │
│  │   ARTICLE    │        │    MATERIALS     │               │
│  │  (Products)  │        │ (RAW + WIP + FG) │               │
│  └──────┬───────┘        └────────┬─────────┘               │
│         │                         │                          │
└─────────┼─────────────────────────┼──────────────────────────┘
          │                         │
          ├─────────────────────────┴───────────┐
          │                                     │
┌─────────▼──────────────┐         ┌───────────▼──────────────┐
│   BOM PRODUCTION       │         │   BOM PURCHASING         │
│  (Process-Oriented)    │         │  (Material-Oriented)     │
├────────────────────────┤         ├──────────────────────────┤
│ - Split by Department  │◄────────│ - RAW Materials Only     │
│ - Shows WIP Flow       │ AUTO-GEN│ - Aggregated from        │
│ - Routing Specific     │         │   Production BOMs        │
│ - Detail: Input/Output │         │ - Used for PO Calc       │
├────────────────────────┤         ├──────────────────────────┤
│ Used By:               │         │ Used By:                 │
│ - PPIC (MO/SPK)        │         │ - Purchasing (PO)        │
│ - Production (Routing) │         │ - Inventory Planning     │
│ - Warehouse (WIP Track)│         │ - Material Requirement   │
│ - Costing (per stage)  │         │   Planning (MRP)         │
└────────────────────────┘         └──────────────────────────┘
```

### Data Flow

```
1. IMPORT PHASE:
   [BOM Production Excel Files] 
          ↓
   [Bulk Import Service]
          ↓
   [bom_production_headers + bom_production_details]
          ↓
   [Auto-Calculate BOM Purchasing]
          ↓
   [bom_purchasing_headers + bom_purchasing_details]

2. PURCHASING WORKFLOW:
   [Sales Order Received]
          ↓
   [Check BOM Purchasing] → Which RAW materials needed?
          ↓
   [Generate Purchase Orders]
          ↓
   [Receive Materials to Warehouse]

3. PRODUCTION WORKFLOW:
   [PO Kain + PO Label Received]
          ↓
   [PPIC Creates MO] → Uses BOM Production
          ↓
   [Explode to SPK/WO per Department]
          ↓
   [Each Department] → Uses BOM Production for their stage
          ↓
   [Material Request] → Warehouse issues materials per BOM Production
          ↓
          [Track WIP] → WIP inventory at each stage
          ↓
   [Finished Goods] → Ready to pack and ship
```

---

<a name="architecture"></a>
## 🏗️ SYSTEM ARCHITECTURE

### Module Dependencies

```
┌──────────────────────────────────────────────────────────┐
│                    MASTERDATA LAYER                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │ Products   │  │ Materials  │  │ BOM Dual System    │  │
│  │ (Articles) │  │ (RAW/WIP)  │  │ - Production       │  │
│  │            │  │            │  │ - Purchasing       │  │
│  └────────────┘  └────────────┘  └────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼───────────────┐    ┌───────────▼────────────────┐
│  PURCHASING MODULE    │    │  PPIC MODULE               │
├───────────────────────┤    ├────────────────────────────┤
│ Uses:                 │    │ Uses:                      │
│ - BOM PURCHASING      │    │ - BOM PRODUCTION           │
│                       │    │                            │
│ Functions:            │    │ Functions:                 │
│ - Material Need Calc  │    │ - MO Creation              │
│ - PO Generation       │    │ - SPK/WO Explosion         │
│ - Supplier Selection  │    │ - Material Allocation      │
│ - Lead Time Planning  │    │ - Routing Assignment       │
└───────┬───────────────┘    └───────────┬────────────────┘
        │                                │
        └────────────────┬───────────────┘
                         │
        ┌────────────────▼────────────────┐
        │     PRODUCTION EXECUTION        │
        ├─────────────────────────────────┤
        │ - Cutting   (BOM Prod: Stage 1) │
        │ - Embo      (BOM Prod: Stage 2) │
        │ - Sewing    (BOM Prod: Stage 3) │
        │ - Finishing (BOM Prod: Stage 4) │
        │ - Packing   (BOM Prod: Stage 5) │
        └─────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │       WAREHOUSE MODULE          │
        ├─────────────────────────────────┤
        │ - RAW Material Stock            │
        │ - WIP Stock (per stage)         │
        │ - Finished Goods Stock          │
        │ - Material Request Processing   │
        └─────────────────────────────────┘
```

---

<a name="database-schema"></a>
## 💾 DATABASE SCHEMA

### New Table Structure

```sql
-- ============================================
-- BOM PRODUCTION TABLES (Process-Oriented)
-- ============================================

CREATE TABLE bom_production_headers (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES products(id), -- Finished Good
    department_id INTEGER NOT NULL REFERENCES departments(id), -- Cutting, Sewing, etc.
    bom_production_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., "BOM-PROD-AFTON-CUT-001"
    version VARCHAR(20) DEFAULT '1.0',
    routing_type VARCHAR(50), -- ROUTE1, ROUTE2, ROUTE3
    routing_sequence INTEGER, -- 1, 2, 3, 4, 5 (order of departments)
    output_product_id INTEGER REFERENCES products(id), -- WIP output (e.g., AFTONSPARV_WIP_SKIN)
    output_quantity DECIMAL(10, 4) DEFAULT 1.0,
    output_uom VARCHAR(20),
    waste_percentage DECIMAL(5, 2) DEFAULT 0,
    standard_time_minutes DECIMAL(10, 2), -- SMV per unit
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bom_production_details (
    id SERIAL PRIMARY KEY,
    bom_production_header_id INTEGER NOT NULL REFERENCES bom_production_headers(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES products(id), -- Can be RAW or WIP
    material_type VARCHAR(20) CHECK (material_type IN ('RAW_MATERIAL', 'WIP', 'BAHAN_PENOLONG')),
    quantity_required DECIMAL(10, 4) NOT NULL,
    uom VARCHAR(20) NOT NULL,
    sequence INTEGER DEFAULT 1, -- Order in BOM
    is_subcontracted BOOLEAN DEFAULT FALSE,
    subcontractor_id INTEGER REFERENCES partners(id),
    cost_per_unit DECIMAL(15, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- BOM PURCHASING TABLES (Material-Oriented)
-- ============================================

CREATE TABLE bom_purchasing_headers (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES products(id), -- Finished Good
    bom_purchasing_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., "BOM-PUR-AFTON-001"
    version VARCHAR(20) DEFAULT '1.0',
    total_raw_materials INTEGER, -- Count of unique raw materials
    auto_generated BOOLEAN DEFAULT TRUE, -- TRUE if generated from BOM Production
    last_sync_date TIMESTAMP, -- Last time synced with BOM Production
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bom_purchasing_details (
    id SERIAL PRIMARY KEY,
    bom_purchasing_header_id INTEGER NOT NULL REFERENCES bom_purchasing_headers(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES products(id), -- RAW MATERIAL only
    material_type VARCHAR(20) CHECK (material_type = 'RAW_MATERIAL'),
    quantity_required DECIMAL(10, 4) NOT NULL, -- Aggregated from all production stages
    uom VARCHAR(20) NOT NULL,
    preferred_supplier_id INTEGER REFERENCES partners(id),
    lead_time_days INTEGER DEFAULT 7,
    minimum_order_qty DECIMAL(10, 2),
    cost_per_unit DECIMAL(15, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES for Performance
-- ============================================

CREATE INDEX idx_bom_prod_article ON bom_production_headers(article_id);
CREATE INDEX idx_bom_prod_dept ON bom_production_headers(department_id);
CREATE INDEX idx_bom_prod_details_header ON bom_production_details(bom_production_header_id);
CREATE INDEX idx_bom_prod_details_material ON bom_production_details(material_id);

CREATE INDEX idx_bom_pur_article ON bom_purchasing_headers(article_id);
CREATE INDEX idx_bom_pur_details_header ON bom_purchasing_details(bom_purchasing_header_id);
CREATE INDEX idx_bom_pur_details_material ON bom_purchasing_details(material_id);
```

### Relationship Diagram

```
products (articles)
    │
    ├──► bom_production_headers (1 article - many dept BOMs)
    │        │
    │        └──► bom_production_details (many materials per stage)
    │                   │
    │                   └──► products (materials: RAW + WIP)
    │
    └──► bom_purchasing_headers (1 article - 1 purchasing BOM)
             │
             └──► bom_purchasing_details (many RAW materials aggregated)
                        │
                        └──► products (materials: RAW only)
```

---

<a name="data-migration"></a>
## 🔄 DATA MIGRATION STRATEGY

### Phase 1: Create New Tables (NON-BREAKING)

```sql
-- Run migration: Add new tables without touching existing bom_headers/bom_details
-- This allows backward compatibility during migration period

-- File: erp-softtoys/alembic/versions/2026_02_06_dual_bom_system.py

def upgrade():
    # Create BOM Production tables
    op.create_table('bom_production_headers', ...)
    op.create_table('bom_production_details', ...)
    
    # Create BOM Purchasing tables
    op.create_table('bom_purchasing_headers', ...)
    op.create_table('bom_purchasing_details', ...)
    
    # Add indexes
    op.create_index(...)

def downgrade():
    # Drop tables if migration fails
    op.drop_table('bom_purchasing_details')
    op.drop_table('bom_purchasing_headers')
    op.drop_table('bom_production_details')
    op.drop_table('bom_production_headers')
```

### Phase 2: Bulk Import Data

```python
# Import BOM Production from Excel files
POST /api/v1/imports/bom-production
Files:
- docs/Masterdata/BOM Production/Cutting.xlsx
- docs/Masterdata/BOM Production/Embo.xlsx
- docs/Masterdata/BOM Production/Sewing.xlsx
- docs/Masterdata/BOM Production/Finishing.xlsx
- docs/Masterdata/BOM Production/Finishing Goods.xlsx
- docs/Masterdata/BOM Production/Packing.xlsx

# Auto-generate BOM Purchasing
POST /api/v1/bom-purchasing/generate-from-production
- Reads all bom_production_details
- Filters material_type = 'RAW_MATERIAL'
- Aggregates quantities per article
- Creates bom_purchasing_headers + bom_purchasing_details
```

### Phase 3: Update API Routes (Gradual)

```
OLD ROUTES (Deprecated, keep for backward compatibility):
GET /api/v1/bom → Redirect to /api/v1/bom-purchasing

NEW ROUTES:
GET /api/v1/bom-production?article_id=X&department=cutting
POST /api/v1/bom-production
PUT /api/v1/bom-production/{id}
DELETE /api/v1/bom-production/{id}

GET /api/v1/bom-purchasing?article_id=X
POST /api/v1/bom-purchasing/generate-from-production
PUT /api/v1/bom-purchasing/{id}
DELETE /api/v1/bom-purchasing/{id}
```

### Phase 4: Deprecate Old Tables (After 3 Months)

```sql
-- After full migration and testing:
-- 1. Rename old tables for backup
ALTER TABLE bom_headers RENAME TO bom_headers_legacy;
ALTER TABLE bom_details RENAME TO bom_details_legacy;

-- 2. Keep for 6 months, then drop
-- DROP TABLE bom_headers_legacy;
-- DROP TABLE bom_details_legacy;
```

---

<a name="api-changes"></a>
## 🔌 API CHANGES

### New Endpoints

```python
# ============================================
# BOM PRODUCTION APIs
# ============================================

@router.get("/bom-production/")
def get_bom_production(
    article_id: Optional[int] = None,
    department_id: Optional[int] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get BOM Production (Process-Oriented)
    Query Params:
    - article_id: Filter by article
    - department_id: Filter by department (Cutting, Sewing, etc.)
    - is_active: Show only active BOMs
    """
    pass

@router.post("/bom-production/")
def create_bom_production(
    bom_data: BOMProductionCreate,
    db: Session = Depends(get_db)
):
    """
    Create new BOM Production for a department stage
    Body:
    {
      "article_id": 1,
      "department_id": 2,
      "routing_type": "ROUTE1",
      "routing_sequence": 1,
      "output_product_id": 150, // WIP_CUTTING
      "materials": [
        {"material_id": 10, "quantity": 0.15, "uom": "YARD"},
        {"material_id": 11, "quantity": 0.001, "uom": "YARD"}
      ]
    }
    """
    pass

@router.get("/bom-production/explode/{article_id}")
def explode_bom_production(
    article_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    """
    Explode BOM Production for all departments
    Returns material requirements per department
    Used by: PPIC for SPK/WO explosion
    """
    pass

# ============================================
# BOM PURCHASING APIs
# ============================================

@router.get("/bom-purchasing/")
def get_bom_purchasing(
    article_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get BOM Purchasing (Material-Oriented)
    Shows RAW materials only (no WIP)
    """
    pass

@router.post("/bom-purchasing/generate-from-production")
def generate_bom_purchasing_from_production(
    article_id: Optional[int] = None,  # If None, generate for all
    db: Session = Depends(get_db)
):
    """
    AUTO-GENERATE BOM Purchasing from BOM Production
    Logic:
    1. Get all bom_production_details for article
    2. Filter material_type = 'RAW_MATERIAL'
    3. Aggregate quantities (sum across all departments)
    4. Create bom_purchasing_headers + bom_purchasing_details
    """
    pass

@router.get("/bom-purchasing/calculate-needs/{article_id}")
def calculate_material_needs(
    article_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    """
    Calculate total RAW material needs for X units
    Returns: List of materials with quantities
    Used by: Purchasing for PO generation
    """
    pass

# ============================================
# BULK IMPORT APIs
# ============================================

@router.post("/imports/bom-production")
async def import_bom_production(
    file: UploadFile,
    department: str,  # cutting, embo, sewing, finishing, packing
    db: Session = Depends(get_db)
):
    """
    Bulk import BOM Production from Excel
    Validates:
    - Article codes exist in products table
    - Material codes exist in products table
    - Department exists
    - Quantities are positive
    """
    pass
```

---

<a name="frontend-changes"></a>
## 🖼️ FRONTEND CHANGES

### New Pages/Components

```
erp-ui/frontend/src/pages/
├── bom/
│   ├── BOMProductionPage.tsx        // List all BOM Production by department
│   ├── BOMProductionDetailPage.tsx  // Create/Edit BOM Production
│   ├── BOMPurchasingPage.tsx        // List all BOM Purchasing
│   ├── BOMPurchasingDetailPage.tsx  // View/Edit BOM Purchasing
│   └── BOMComparisonPage.tsx        // Compare Production vs Purchasing BOM
│
├── ppic/
│   └── MOCreationPage.tsx           // Updated to use BOM Production
│
└── purchasing/
    └── POCreationPage.tsx           // Updated to use BOM Purchasing
```

### UI Mockup: BOM Production Page

```
┌────────────────────────────────────────────────────────────────┐
│  BOM PRODUCTION - Process-Oriented View                        │
├────────────────────────────────────────────────────────────────┤
│  Article: [AFTONSPARV Bear 40551542] ▼                         │
│  Department: [All] ▼  [Cutting] [Embo] [Sewing] ...           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STAGE 1: CUTTING DEPARTMENT                              │  │
│  │ Routing: ROUTE1 | Sequence: 1                            │  │
│  │                                                           │  │
│  │ Input Materials:                                         │  │
│  │ ✓ [IKHR504] KOHAIR Fabric 0.15 YARD                      │  │
│  │ ✓ [IJBR105] BOA Fabric 0.0015 YARD                       │  │
│  │ ✓ [INYR002] NYLEX 0.001 YARD                             │  │
│  │                                                           │  │
│  │ Output:                                                   │  │
│  │ → AFTONSPARV_WIP_CUTTING 1 PCE                           │  │
│  │                                                           │  │
│  │ [Edit] [View History]                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STAGE 2: SEWING DEPARTMENT                               │  │
│  │ ...                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [+ Add New Stage] [Export Excel] [Generate Purchasing BOM]   │
└────────────────────────────────────────────────────────────────┘
```

### UI Mockup: BOM Purchasing Page

```
┌────────────────────────────────────────────────────────────────┐
│  BOM PURCHASING - Material-Oriented View                       │
├────────────────────────────────────────────────────────────────┤
│  Article: [AFTONSPARV Bear 40551542] ▼                         │
│  Status: ✅ Auto-Generated from BOM Production                 │
│  Last Sync: 2026-02-06 10:30 AM                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ RAW MATERIALS TO PURCHASE (per 1 PCE)                    │  │
│  │                                                           │  │
│  │ No. | Material Code | Material Name       | Qty   | UoM │  │
│  │ 1   | IKHR504       | KOHAIR Fabric       | 0.15  | YARD│  │
│  │ 2   | IJBR105       | BOA Fabric          | 0.0015| YARD│  │
│  │ 3   | INYR002       | NYLEX               | 0.001 | YARD│  │
│  │ 4   | IKP20157      | Filling HCS         | 54    | GRAM│  │
│  │ 5   | ATR10400      | Thread Nilon        | 60    | CM  │  │
│  │ 6   | ALL40030      | Label RPI           | 1     | PCE │  │
│  │ 7   | ALB40011      | Hang Tag            | 1     | PCE │  │
│  │ 8   | ACB30104      | Carton              | 0.0167| PCE │  │
│  │                                                           │  │
│  │ Total: 8 materials                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ CALCULATE MATERIAL NEEDS FOR PRODUCTION                   │  │
│  │ Quantity to Produce: [500] PCE                            │  │
│  │ [Calculate] → Show total material requirements            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [Regenerate from Production BOM] [Export Excel] [Create PO]  │
└────────────────────────────────────────────────────────────────┘
```

---

<a name="business-logic"></a>
## 🧠 BUSINESS LOGIC

### Use Case 1: PPIC Creates MO

```python
# PPIC flow: Create Manufacturing Order
# Uses: BOM PRODUCTION

def create_manufacturing_order(article_id, quantity):
    # 1. Get BOM Production for all departments
    bom_stages = db.query(BOMProductionHeader)\
        .filter(BOMProductionHeader.article_id == article_id)\
        .order_by(BOMProductionHeader.routing_sequence)\
        .all()
    
    # 2. Create MO
    mo = ManufacturingOrder(
        article_id=article_id,
        quantity_target=quantity,
        status="DRAFT"
    )
    db.add(mo)
    db.flush()
    
    # 3. Explode to Work Orders (SPK) per department
    for stage in bom_stages:
        wo = WorkOrder(
            mo_id=mo.id,
            department_id=stage.department_id,
            routing_sequence=stage.routing_sequence,
            status="PENDING"
        )
        db.add(wo)
        
        # 4. Allocate materials for this department
        for material in stage.bom_production_details:
            required_qty = material.quantity_required * quantity
            
            allocation = MaterialAllocation(
                wo_id=wo.id,
                material_id=material.material_id,
                quantity_required=required_qty,
                uom=material.uom
            )
            db.add(allocation)
    
    db.commit()
    return mo
```

### Use Case 2: Purchasing Calculates Material Needs

```python
# Purchasing flow: Calculate total materials needed for Sales Order
# Uses: BOM PURCHASING

def calculate_material_needs_for_sales_order(so_lines):
    """
    so_lines = [
        {"article_id": 1, "quantity": 500},
        {"article_id": 2, "quantity": 300}
    ]
    """
    material_needs = {}
    
    for line in so_lines:
        # Get BOM Purchasing for this article
        bom_pur = db.query(BOMPurchasingHeader)\
            .filter(BOMPurchasingHeader.article_id == line['article_id'])\
            .first()
        
        if not bom_pur:
            # Auto-generate if not exists
            generate_bom_purchasing(line['article_id'])
            bom_pur = db.query(BOMPurchasingHeader)\
                .filter(BOMPurchasingHeader.article_id == line['article_id'])\
                .first()
        
        # Calculate material needs
        for detail in bom_pur.bom_purchasing_details:
            material_code = detail.material.product_code
            required_qty = detail.quantity_required * line['quantity']
            
            if material_code in material_needs:
                material_needs[material_code]['quantity'] += required_qty
            else:
                material_needs[material_code] = {
                    'material_id': detail.material_id,
                    'material_name': detail.material.product_name,
                    'quantity': required_qty,
                    'uom': detail.uom,
                    'preferred_supplier_id': detail.preferred_supplier_id
                }
    
    return material_needs
```

### Use Case 3: Auto-Generate BOM Purchasing

```python
# Service: Auto-generate BOM Purchasing from BOM Production
# Triggered: When BOM Production is updated OR manually by user

def generate_bom_purchasing_from_production(article_id):
    """
    Aggregate all RAW materials from all production stages
    """
    # 1. Get all BOM Production stages for this article
    production_stages = db.query(BOMProductionHeader)\
        .filter(BOMProductionHeader.article_id == article_id)\
        .all()
    
    # 2. Aggregate RAW materials
    raw_materials = {}
    
    for stage in production_stages:
        for detail in stage.bom_production_details:
            # Filter: Only RAW_MATERIAL (exclude WIP)
            if detail.material_type == 'RAW_MATERIAL':
                material_code = detail.material.product_code
                
                if material_code in raw_materials:
                    # Aggregate quantity
                    raw_materials[material_code]['quantity'] += detail.quantity_required
                else:
                    raw_materials[material_code] = {
                        'material_id': detail.material_id,
                        'quantity': detail.quantity_required,
                        'uom': detail.uom
                    }
    
    # 3. Check if BOM Purchasing already exists
    bom_pur_header = db.query(BOMPurchasingHeader)\
        .filter(BOMPurchasingHeader.article_id == article_id)\
        .first()
    
    if bom_pur_header:
        # Update existing
        # Delete old details
        db.query(BOMPurchasingDetail)\
            .filter(BOMPurchasingDetail.bom_purchasing_header_id == bom_pur_header.id)\
            .delete()
    else:
        # Create new header
        bom_pur_header = BOMPurchasingHeader(
            article_id=article_id,
            bom_purchasing_code=f"BOM-PUR-{article_id}",
            auto_generated=True
        )
        db.add(bom_pur_header)
        db.flush()
    
    # 4. Create details
    for material_data in raw_materials.values():
        detail = BOMPurchasingDetail(
            bom_purchasing_header_id=bom_pur_header.id,
            material_id=material_data['material_id'],
            material_type='RAW_MATERIAL',
            quantity_required=material_data['quantity'],
            uom=material_data['uom']
        )
        db.add(detail)
    
    bom_pur_header.total_raw_materials = len(raw_materials)
    bom_pur_header.last_sync_date = datetime.now()
    
    db.commit()
    return bom_pur_header
```

---

<a name="implementation-plan"></a>
## 📅 IMPLEMENTATION PLAN

### Phase 1: Database & Backend (2-3 Days)

**Day 1: Database Schema**
- [ ] Create Alembic migration script
- [ ] Add new tables: bom_production_headers, bom_production_details
- [ ] Add new tables: bom_purchasing_headers, bom_purchasing_details
- [ ] Add indexes for performance
- [ ] Run migration on dev database
- [ ] Verify tables created successfully

**Day 2: Backend Services**
- [ ] Create BOM Production Service (CRUD operations)
- [ ] Create BOM Purchasing Service (CRUD + auto-generation)
- [ ] Create BOM Import Service (bulk import from Excel)
- [ ] Add API routers for both BOM types
- [ ] Add auto-generation logic (Production → Purchasing)
- [ ] Write unit tests for services

**Day 3: Integration & Testing**
- [ ] Update PPIC module to use BOM Production
- [ ] Update Purchasing module to use BOM Purchasing
- [ ] Update Material Allocation logic
- [ ] Test end-to-end workflow (MO → SPK → Material Request)
- [ ] Test PO generation with BOM Purchasing

### Phase 2: Bulk Import (1-2 Days)

**Day 4: Import Implementation**
- [ ] Create Excel template parser for BOM Production
- [ ] Add validation logic (article exists, material exists, etc.)
- [ ] Implement transaction rollback on error
- [ ] Add audit logging for imports
- [ ] Test import with sample data (10 articles)

**Day 5: Full Data Import**
- [ ] Import Cutting.xlsx (508 lines)
- [ ] Import Embo.xlsx (306 lines)
- [ ] Import Sewing.xlsx (2,450 lines)
- [ ] Import Finishing.xlsx (835 lines)
- [ ] Import Finishing Goods.xlsx (518 lines)
- [ ] Import Packing.xlsx (1,228 lines)
- [ ] Auto-generate BOM Purchasing for all articles
- [ ] Verify data integrity (total 5,845 BOM lines)

### Phase 3: Frontend (2-3 Days)

**Day 6-7: UI Components**
- [ ] Create BOMProductionPage (list view)
- [ ] Create BOMProductionDetailPage (create/edit)
- [ ] Create BOMPurchasingPage (list view)
- [ ] Create BOMComparisonPage (side-by-side view)
- [ ] Update MOCreationPage (use BOM Production)
- [ ] Update POCreationPage (use BOM Purchasing)

**Day 8: Testing & Polish**
- [ ] Integration testing (frontend ↔ backend)
- [ ] User acceptance testing with Purchasing team
- [ ] User acceptance testing with PPIC team
- [ ] Fix bugs and polish UI
- [ ] Update user documentation

### Phase 4: Documentation (1 Day)

**Day 9: Update Documentation**
- [ ] Update prompt.md with dual-BOM concept
- [ ] Update Rencana Tampilan.md (UI specs)
- [ ] Update PRESENTASI_MANAGEMENT.md (benefits)
- [ ] Create training materials for users
- [ ] Record video tutorial (10 minutes)

### Phase 5: Deployment (1 Day)

**Day 10: Production Deployment**
- [ ] Run database migration on production
- [ ] Deploy backend updates
- [ ] Deploy frontend updates
- [ ] Import production data (5,845 BOM lines)
- [ ] Monitor error logs for 24 hours
- [ ] Provide on-site support to users

**Total Estimated Time: 10 Working Days (2 Weeks)**

---

<a name="testing-strategy"></a>
## ✅ TESTING STRATEGY

### Unit Tests

```python
# tests/test_bom_production_service.py

def test_create_bom_production():
    """Test creating BOM Production for Cutting department"""
    bom_data = {
        'article_id': 1,
        'department_id': 1,  # Cutting
        'routing_sequence': 1,
        'materials': [
            {'material_id': 10, 'quantity': 0.15, 'uom': 'YARD'},
            {'material_id': 11, 'quantity': 0.001, 'uom': 'YARD'}
        ]
    }
    bom = bom_production_service.create(bom_data)
    assert bom.id is not None
    assert len(bom.bom_production_details) == 2

def test_explode_bom_production():
    """Test exploding BOM Production for 500 units"""
    materials = bom_production_service.explode(article_id=1, quantity=500)
    assert len(materials) > 0
    assert materials[0]['quantity'] == 75.0  # 0.15 * 500

# tests/test_bom_purchasing_service.py

def test_generate_bom_purchasing():
    """Test auto-generation of BOM Purchasing from Production"""
    bom_pur = bom_purchasing_service.generate_from_production(article_id=1)
    assert bom_pur.auto_generated == True
    assert bom_pur.total_raw_materials > 0

def test_calculate_material_needs():
    """Test calculating material needs for 500 units"""
    needs = bom_purchasing_service.calculate_needs(article_id=1, quantity=500)
    assert 'IKHR504' in needs  # Material code
    assert needs['IKHR504']['quantity'] == 75.0  # 0.15 * 500
```

### Integration Tests

```python
# tests/test_bom_integration.py

def test_ppic_creates_mo_with_bom_production():
    """Test PPIC workflow: Create MO → Explode SPK → Allocate materials"""
    # 1. Create MO
    mo = ppic_service.create_mo(article_id=1, quantity=500)
    assert mo.id is not None
    
    # 2. Check SPK/WO explosion
    work_orders = db.query(WorkOrder).filter(WorkOrder.mo_id == mo.id).all()
    assert len(work_orders) == 5  # 5 departments
    
    # 3. Check material allocation per SPK
    for wo in work_orders:
        allocations = db.query(MaterialAllocation)\
            .filter(MaterialAllocation.wo_id == wo.id)\
            .all()
        assert len(allocations) > 0

def test_purchasing_generates_po_with_bom_purchasing():
    """Test Purchasing workflow: Sales Order → Material Needs → PO"""
    # 1. Calculate material needs
    so_lines = [{"article_id": 1, "quantity": 500}]
    material_needs = purchasing_service.calculate_material_needs(so_lines)
    assert len(material_needs) > 0
    
    # 2. Generate PO
    po = purchasing_service.create_po_from_material_needs(material_needs)
    assert po.id is not None
    assert len(po.po_lines) == len(material_needs)
```

### User Acceptance Testing

```
Test Case 1: PPIC User Creates MO
1. Login as ppic_admin
2. Navigate to PPIC → Manufacturing Orders
3. Click [+ Create MO]
4. Select Article: AFTONSPARV Bear
5. Enter Quantity: 500
6. Click [Preview BOM Production]
   → Should show 5 stages (Cutting, Embo, Sewing, Finishing, Packing)
7. Click [Create MO]
8. Verify: 5 SPK/WO created (one per department)
9. Verify: Material allocations match BOM Production

Test Case 2: Purchasing User Creates PO
1. Login as purchasing
2. Navigate to Purchasing → Sales Orders
3. Open SO-2026-001 (AFTONSPARV Bear - 500 pcs)
4. Click [Calculate Material Needs]
   → Should use BOM Purchasing (RAW materials only, no WIP)
5. Verify: Material list shows 8 raw materials
6. Click [Generate PO]
7. Verify: PO created with correct quantities
8. Submit PO to supplier
```

### Performance Testing

```
Scenario: Import 5,845 BOM lines
Expected: < 30 seconds for all 6 files
Actual: [TO BE MEASURED]

Scenario: Generate BOM Purchasing for 100 articles
Expected: < 10 seconds
Actual: [TO BE MEASURED]

Scenario: Explode BOM Production for MO (500 units)
Expected: < 2 seconds
Actual: [TO BE MEASURED]
```

---

## 📊 SUCCESS METRICS

### Technical Metrics
- ✅ 5,845 BOM lines imported successfully
- ✅ Zero data integrity errors
- ✅ API response time < 2 seconds for BOM explosion
- ✅ 100% test coverage for BOM services

### Business Metrics
- ✅ Purchasing sees only RAW materials (no WIP confusion)
- ✅ PPIC explosion time reduced by 50% (clear department routing)
- ✅ Material calculation accuracy: 99%+
- ✅ User satisfaction: 4.5/5 stars (post-training survey)

### Adoption Metrics
- ✅ 100% of PPIC staff using BOM Production (Week 2)
- ✅ 100% of Purchasing staff using BOM Purchasing (Week 2)
- ✅ Zero rollback to old BOM system (Week 4)

---

## 🆘 SUPPORT & TROUBLESHOOTING

### Common Issues

**Issue 1: BOM Purchasing not showing materials**
- Cause: BOM Production not imported yet OR no RAW materials in production stages
- Solution: Import BOM Production first, then regenerate BOM Purchasing

**Issue 2: Material allocation fails during MO creation**
- Cause: BOM Production missing for a department
- Solution: Check bom_production_headers, ensure all 5-6 departments have BOM entries

**Issue 3: Duplicate materials in BOM Purchasing**
- Cause: Same material used in multiple departments (expected behavior)
- Solution: This is correct! BOM Purchasing aggregates quantities

### Contact

**Technical Support**: [developer@qutykarunia.com]  
**Business Questions**: [ppic@qutykarunia.com]  
**Training**: [training@qutykarunia.com]

---

## 📝 CHANGELOG

### Version 1.0 (2026-02-06)
- Initial document creation
- Defined dual-BOM concept (Production vs Purchasing)
- Designed database schema
- Created implementation plan (10-day roadmap)
- Prepared testing strategy

---

**Document Owner**: Daniel Rizaldy (IT Fullstack)  
**Last Updated**: February 6, 2026  
**Status**: ✅ Ready for Implementation  
**Next Review**: February 16, 2026 (After Phase 1 completion)
