# 🚀 QUTY KARUNIA ERP - WEEK 1 SETUP GUIDE
**Status: ACTIVE DEVELOPMENT | Week 1 Foundation Setup**

---

## ✅ WHAT WE'VE COMPLETED THIS WEEK

### **Database Models Created (All Gap Fixes Applied)**
1. ✅ **Products Model** - Parent-child article hierarchy (Gap Fix #1)
2. ✅ **BOM Models** - With revision audit trail (Gap Fix #4)
3. ✅ **Manufacturing Orders & Work Orders** - Full production tracking
4. ✅ **Transfer Models** - Line occupancy tracking (Gap Fix #2)
5. ✅ **Warehouse Models** - Stock moves & FIFO logic
6. ✅ **Quality Models** - QC tests with NUMERIC precision (Gap Fix #5)
7. ✅ **Exception Models** - Alert logs & segregasi acknowledgement (NEW)
8. ✅ **User Models** - Role-based access control

### **Database Schema Features**
- ✅ All tables from Database Scheme.csv implemented
- ✅ 5 Gap Fixes integrated
- ✅ Relationships configured (Foreign Keys)
- ✅ Indices for performance optimization
- ✅ Enum types for data integrity

---

## 📋 SETUP STEPS (Do This Now)

### **Step 1: Create .env File**
```bash
cd D:\Project\ERP2026\erp-softtoys
cat > .env << EOF
# Database
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/erp_quty_karunia

# JWT Security
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# App
ENVIRONMENT=development
DEBUG=True
EOF
```

### **Step 2: Install Updated Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 3: Create PostgreSQL Database**
```bash
# Using psql (if PostgreSQL installed locally)
psql -U postgres
CREATE DATABASE erp_quty_karunia;
\q

# Or using command line:
createdb -U postgres erp_quty_karunia
```

### **Step 4: Initialize Alembic (Database Migrations)**
```bash
alembic init migrations

# Edit migrations/alembic.ini
# Change: sqlalchemy.url = postgresql://user:password@localhost/erp_quty_karunia

# Generate first migration
alembic revision --autogenerate -m "Initial schema with all models"

# Apply migration to database
alembic upgrade head
```

### **Step 5: Verify Database Created**
```bash
# Connect to database
psql -U postgres -d erp_quty_karunia

# List tables
\dt

# Should see:
# - products, categories
# - bom_headers, bom_details
# - manufacturing_orders, work_orders, mo_material_consumption
# - transfer_logs, line_occupancy
# - locations, stock_moves, stock_quants
# - qc_lab_tests, qc_inspections
# - alert_logs, segregasi_acknowledgement
# - users
```

### **Step 6: Run Application in Development**
```bash
cd D:\Project\ERP2026\erp-softtoys
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Step 7: Access Swagger Documentation**
```
http://localhost:8000/docs
```

---

## 📊 DATABASE SCHEMA CREATED

### **Master Data Tables**
```
products
├── id (PK)
├── code (Unique)
├── name
├── type (Raw Material, WIP, Finish Good, Service)
├── uom (Pcs, Meter, Yard, Kg, Roll)
├── parent_article_id (NEW - Gap Fix #1)
└── min_stock

categories
├── id (PK)
├── name (Unique)
└── products (relationship)

bom_headers
├── id (PK)
├── product_id (FK)
├── bom_type
├── qty_output
├── is_active
├── revision
├── revision_date (NEW - Gap Fix #4)
├── revised_by (NEW)
└── revision_reason (NEW)

bom_details
├── id (PK)
├── bom_header_id (FK)
├── component_id (FK)
├── qty_needed
└── wastage_percent
```

### **Production Execution Tables**
```
manufacturing_orders (SPK Induk)
├── id (PK)
├── so_line_id (FK - Sales Order)
├── product_id (FK)
├── qty_planned
├── qty_produced
├── routing_type (Route 1, 2, 3)
├── batch_number (Traceability)
└── state (Draft, In Progress, Done)

work_orders (SPK per Department)
├── id (PK)
├── mo_id (FK)
├── product_id (FK)
├── department
├── status
├── start_time, end_time
├── input_qty
├── output_qty (Can be surplus/shortage!)
├── reject_qty
└── worker_id (FK - User)

mo_material_consumption
├── id (PK)
├── work_order_id (FK)
├── product_id (FK - Material used)
├── qty_planned
├── qty_actual
└── lot_id (FK - Batch/Roll)
```

### **Transfer & Line Management Tables (QT-09)**
```
transfer_logs (Handshake Digital)
├── id (PK)
├── mo_id (FK)
├── from_dept (Cutting, Embroidery, Sewing, Finishing, Packing) ← Gap Fix #3
├── to_dept (Same enum) ← Gap Fix #3
├── article_code
├── batch_id
├── qty_sent
├── qty_received
├── is_line_clear (Line Clearance validation)
├── status (Initiated, Blocked, Locked, Accepted, Completed)
└── timestamp_* (start, accept, end)

line_occupancy (NEW - Gap Fix #2)
├── id (PK)
├── dept_name
├── line_number
├── current_article_id (FK)
├── current_batch_id
├── current_destination
├── occupancy_status (Clear, Occupied, Paused)
├── locked_at
├── locked_by (FK - User)
└── expected_clear_time (ETA)
```

### **Quality Control Tables**
```
qc_lab_tests
├── id (PK)
├── batch_number
├── test_type (Drop Test, Stability 10/27, Seam Strength)
├── test_result (Pass, Fail)
├── measured_value (NUMERIC - Gap Fix #5, was FLOAT)
├── measured_unit (Newton, %, cm, etc.)
├── iso_standard (ISO 8124, etc.)
├── inspector_id (FK)
└── evidence_photo_url (If Fail)

qc_inspections
├── id (PK)
├── work_order_id (FK)
├── type (Incoming, Inline Sewing, Final Metal Detector)
├── status (Pass, Fail)
├── defect_reason
├── defect_location
├── defect_qty
└── inspected_by (FK - User)
```

### **Exceptions & Alerts Tables (NEW)**
```
alert_logs (Gap Fix #2)
├── id (PK)
├── alert_type (Line Clearance Block, Segregasi Alarm, QC Fail, etc.)
├── severity (Info, Warning, Critical)
├── triggered_at
├── triggered_by (FK - User/System)
├── escalated_to (FK - User)
├── escalation_level (1=First, 2=Manager, 3=Director)
├── status (Pending, Acknowledged, Resolved, Overridden)
└── notes

segregasi_acknowledgement (Gap Fix #2)
├── id (PK)
├── transfer_log_id (FK)
├── acknowledged_at
├── acknowledged_by (FK - User)
├── clearance_method (Physical Gap, Line Stop, Manual Inspection)
├── proof_photo_url
└── clearance_notes
```

### **Warehouse Tables**
```
locations
├── id (PK)
├── name (Unique)
├── type (Warehouse, Production, Supplier, etc.)
└── capacity

stock_moves
├── id (PK)
├── product_id (FK)
├── qty, uom
├── location_id_from (FK)
├── location_id_to (FK)
├── reference_doc (SPK, PO, etc.)
├── state (Draft, Done)
└── lot_id (FK - For FIFO)

stock_quants
├── id (PK)
├── product_id (FK)
├── location_id (FK)
├── lot_id (FK - For FIFO)
├── qty_on_hand
└── qty_reserved

stock_lots
├── id (PK)
├── product_id (FK)
├── lot_number (Unique - Roll ID)
├── qty_initial, qty_remaining
└── received_date, expiry_date
```

### **User & Security Tables**
```
users
├── id (PK)
├── username (Unique)
├── email (Unique)
├── hashed_password
├── full_name
├── role (Admin, PPIC Manager, SPV Cutting, Operator, QC, Warehouse, etc.)
├── department
└── is_active
```

---

## 🔑 DATA VALIDATION RULES

### **Product Types (Enum)**
- `Raw Material` - Bahan baku (Kain, Benang, etc.)
- `WIP` - Work In Progress (WIP CUT, WIP EMB, WIP SEW)
- `Finish Good` - Barang jadi (Final product from IKEA)
- `Service` - Services

### **Unit of Measurement (UOM)**
- `Pcs` - Pieces
- `Meter` - Length
- `Yard` - Yard
- `Kg` - Weight
- `Roll` - Roll of fabric

### **Routing Types (3 Production Routes)**
- `Route 1` - Full Process: Cutting → Embroidery → Sewing → Finishing → Packing
- `Route 2` - Direct Sewing: Cutting → Sewing → Finishing → Packing
- `Route 3` - Subcon: Cutting → Vendor → Finishing → Packing

### **Work Order Status**
- `Pending` - Waiting to start
- `Running` - Currently executing
- `Finished` - Work completed

### **Transfer Status (Handshake Protocol)**
- `Initiated` - Transfer created, checking line clearance
- `Blocked` - Line not ready (ID 292 or 382)
- `Locked` - Stock locked, waiting for ACCEPT scan
- `Accepted` - Receiving dept scanned ACCEPT
- `Completed` - Stock quantity transferred
- `Cancelled` - Transfer cancelled

### **Line Status**
- `Clear` - Line ready for new article
- `Occupied` - Currently processing
- `Paused` - Temporarily stopped for clearance

### **User Roles (RBAC)**
- `Admin` - System administrator
- `PPIC Manager` - Production planning manager
- `SPV Cutting` - Cutting supervisor (Escalation point for ID 292)
- `SPV Sewing` - Sewing supervisor
- `SPV Finishing` - Finishing supervisor
- `Operator_*` - Machine operators
- `QC Inspector` - Quality control
- `QC Lab` - Lab technician
- `Warehouse Admin` - Warehouse administrator
- `Purchasing` - Procurement team
- `Security` - Security gate

---

## ⚙️ NEXT STEPS (Week 2)

### **Phase 0 Completion (Week 2)**
1. Implement FastAPI authentication (JWT)
2. Create RBAC middleware
3. Implement PPIC API endpoints (BOM, MO creation)
4. Implement Warehouse API endpoints (Stock moves)
5. Create error handling middleware
6. Seed test data

### **What Will Be Ready After Week 2**
- ✅ Complete authentication system
- ✅ 7 API endpoints (PPIC + Warehouse)
- ✅ Role-based access control
- ✅ Test data seeded
- ✅ Swagger API documentation

---

## 🐛 TROUBLESHOOTING

### **Issue: ImportError for models**
```python
# Solution: Ensure models are imported in database.py
from app.core.models import (User, Product, ... all models)
```

### **Issue: Alembic can't find SQLAlchemy models**
```bash
# Solution: Check alembic.ini and env.py in migrations/
# In migrations/env.py, ensure:
from app.core.database import Base
from app.core.models import *

target_metadata = Base.metadata
```

### **Issue: Foreign key constraint errors**
```sql
# Check relationships are defined correctly
SELECT * FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY';
```

### **Issue: Port 8000 already in use**
```bash
# Use different port
python -m uvicorn app.main:app --reload --port 8001
```

---

## 📞 CONTACTS & REFERENCES

- **Database Schema Documentation**: [Database Scheme.csv](../Database%20Scheme.csv)
- **Flowchart**: [Flowchart ERP.csv](../Flowchart%20ERP.csv)
- **SOP Documentation**: [Flow Production.md](../Flow%20Production.md)
- **Implementation Roadmap**: [IMPLEMENTATION_ROADMAP.md](../IMPLEMENTATION_ROADMAP.md)

---

**Created by: Daniel Rizaldy | Week 1 Status: ✅ COMPLETE**
