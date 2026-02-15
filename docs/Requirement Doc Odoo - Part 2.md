# 🏭 ODOO 18 IMPLEMENTATION - REQUIREMENTS DOCUMENT (PART 2)
## PT Quty Karunia - Continued from Part 1

---

<a name="section-7"></a>
## 7️⃣ BOM & MANUFACTURING LOGIC

### Current BOM Structure Overview

PT Quty Karunia has **2 types of BOM** for each product:

1. **BOM Production** (Process-Oriented): For PPIC & Production Departments
2**BOM Purchasing** (Material-Oriented): For Purchasing Department

### BOM Statistics

| Metric | Value |
|--------|-------|
| **Total Articles** | 478 SKU |
| **Total BOM Production Lines** | 5,845 lines |
| **Total BOM Purchasing Lines** | 2,891 lines (RAW materials only) |
| **Average BOM Lines per Article** | ~12 lines (Production), ~6 lines (Purchasing) |
| **Total Unique Materials** | 1,254 SKU |
| **Material Categories** | Fabric (378), Thread (89), Filling (24), Label (156), Accessories (245), Carton (45), Other (317) |

### Example: AFTONSPARV Bear (40551542)

#### BOM Production (Step-by-Step per Department)

```
Article: AFTONSPARV Bear - Sitting Doll 38cm
Code: 40551542
Output: 1 PCS Finished Goods

┌─────────────────────────────────────────────────────────────┐
│  DEPARTMENT 1: CUTTING                                       │
├─────────────────────────────────────────────────────────────┤
│  INPUT Materials:                                           │
│   ├─ [IKHR504] KOHAIR Fabric D.BROWN: 0.1466 YARD          │
│   ├─ [IJBR105] JS BOA Fabric: 0.0015 YARD                  │
│   ├─ [INYR002] NYLEX Fabric: 0.001 YARD                    │
│   ├─ [IPR301] POLYESTER Grey: 0.1893 YARD                  │
│   └─ ... (9 more fabric types)                             │
│                                                             │
│  OUTPUT: 2 WIP Products                                     │
│   ├─ WIP_AFTONSPARV_CUT_BODY: 1 PCS (Body pieces cut)     │
│   └─ WIP_AFTONSPARV_CUT_BAJU: 1 PCS (Clothing pieces cut) │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  DEPARTMENT 2: EMBROIDERY (Optional - Route 1 only)        │
├─────────────────────────────────────────────────────────────┤
│  INPUT:                                                     │
│   └─ WIP_AFTONSPARV_CUT_BODY: 1 PCS                        │
│                                                             │
│  Materials:                                                 │
│   └─ [ATR20155] Thread Embroidery: 50 CM                   │
│                                                             │
│  OUTPUT:                                                    │
│   └─ WIP_AFTONSPARV_EMBR_BODY: 1 PCS (with logo)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  DEPARTMENT 3: SEWING (2 Parallel Streams)                 │
├─────────────────────────────────────────────────────────────┤
│  STREAM A - Body Sewing:                                    │
│  INPUT:                                                     │
│   └─ WIP_AFTONSPARV_EMBR_BODY (or CUT_BODY): 1 PCS        │
│                                                             │
│  Materials:                                                 │
│   ├─ [IKB10204] Thread Black: 2496 CM                      │
│   ├─ [IKB10208] Thread Brown: 1200 CM                      │
│   ├─ [IAC10115] Button Eyes: 2 PCS                         │
│   ├─ [IAC10220] Nose Plastic: 1 PCS                        │
│   └─ ... (5 more accessories)                              │
│                                                             │
│  OUTPUT:                                                    │
│   └─ WIP_AFTONSPARV_SKIN: 1 PCS (sewn, no filling)        │
│                                                             │
│  STREAM B - Clothing Sewing:                                │
│  INPUT:                                                     │
│   └─ WIP_AFTONSPARV_CUT_BAJU: 1 PCS                        │
│                                                             │
│  Materials:                                                 │
│   ├─ [IKB10204] Thread Black: 800 CM                       │
│   └─ [IAC30145] Button Shirt: 4 PCS                        │
│                                                             │
│  OUTPUT:                                                    │
│   └─ WIP_AFTONSPARV_BAJU: 1 PCS (clothing complete)       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  DEPARTMENT 4: FINISHING - Stage 1 (Stuffing)              │
├─────────────────────────────────────────────────────────────┤
│  INPUT:                                                     │
│   └─ WIP_AFTONSPARV_SKIN: 1 PCS                            │
│                                                             │
│  Materials:                                                 │
│   ├─ [IKP20157] Filling Dacron: 54 GRAM                    │
│   └─ [IKB10208] Thread Brown: 100 CM                       │
│                                                             │
│  OUTPUT:                                                    │
│   └─ WIP_AFTONSPARV_STUFFED: 1 PCS (body with filling)    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  DEPARTMENT 4: FINISHING - Stage 2 (Closing)               │
├─────────────────────────────────────────────────────────────┤
│  INPUT:                                                     │
│   └─ WIP_AFTONSPARV_STUFFED: 1 PCS                         │
│                                                             │
│  Materials:                                                 │
│   ├─ [IKB10208] Thread Brown: 50 CM                        │
│   └─ [ALB40011] Hang Tag IKEA: 1 PCS                       │
│                                                             │
│  OUTPUT:                                                    │
│   └─ WIP_AFTONSPARV_BONEKA: 1 PCS (finished doll)         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  DEPARTMENT 5: PACKING                                      │
├─────────────────────────────────────────────────────────────┤
│  INPUT: (Assembly of 2 components)                          │
│   ├─ WIP_AFTONSPARV_BONEKA: 1 PCS                          │
│   └─ WIP_AFTONSPARV_BAJU: 1 PCS                            │
│                                                             │
│  Materials:                                                 │
│   ├─ [ALB40301] Label EU: 1 PCS                            │
│   ├─ [ALB40305] Info Sticker: 2 PCS (front + back)        │
│   ├─ [IAC50112] Polybag: 1 PCS                             │
│   └─ [ACB30104] Carton 570x375: 0.0167 PCS (60pcs/ctn)    │
│                                                             │
│  OUTPUT:                                                    │
│   └─ [40551542] AFTONSPARV Bear: 1 PCS (Finished Goods)   │
└─────────────────────────────────────────────────────────────┘
```

**Total Unique Materials for 1 pcs AFTONSPARV**: 38 SKU (30 RAW + 8 WIP)

#### BOM Purchasing (Aggregated RAW Materials Only)

```
Article: AFTONSPARV Bear (40551542)
Purpose: Material Procurement Planning
For: Purchasing Department

┌─────────────────────────────────────────────────────────────┐
│  TOTAL RAW MATERIALS (per 1 PCS finished)                   │
├─────────────────────────────────────────────────────────────┤
│  FABRIC (9 types):                                          │
│   ├─ [IKHR504] KOHAIR D.BROWN: 0.1466 YARD                 │
│   ├─ [IJBR105] JS BOA: 0.0015 YARD                         │
│   ├─ [INYR002] NYLEX: 0.001 YARD                           │
│   ├─ [IPR301] POLYESTER Grey: 0.1893 YARD                  │
│   └─ ... (5 more fabric types)                             │
│                                                             │
│  THREAD (4 types):                                          │
│   ├─ [IKB10204] Thread Black: 3296 CM (3.296 METER)        │
│   ├─ [IKB10208] Thread Brown: 1350 CM (1.35 METER)         │
│   ├─ [ATR20155] Thread Embroidery: 50 CM                   │
│   └─ [IKB10202] Thread White: 200 CM                       │
│                                                             │
│  FILLING & STUFFING:                                        │
│   └─ [IKP20157] Filling Dacron: 54 GRAM (0.054 KG)         │
│                                                             │
│  ACCESSORIES (12 types):                                    │
│   ├─ [IAC10115] Button Eyes: 2 PCS                         │
│   ├─ [IAC10220] Nose Plastic: 1 PCS                        │
│   ├─ [IAC30145] Button Shirt: 4 PCS                        │
│   └─ ... (9 more accessories)                              │
│                                                             │
│  LABEL & PACKAGING (4 types):                               │
│   ├─ [ALB40011] Hang Tag IKEA: 1 PCS                       │
│   ├─ [ALB40301] Label EU: 1 PCS                            │
│   ├─ [ALB40305] Info Sticker: 2 PCS                        │
│   ├─ [IAC50112] Polybag: 1 PCS                             │
│   └─ [ACB30104] Carton 570x375: 0.0167 PCS (60pcs/ctn)    │
└─────────────────────────────────────────────────────────────┘

Total Unique RAW Materials: 30 SKU (NO WIP components!)
```

### Routing Configuration

PT Quty Karunia has **2 routing options** per artikel:

| Route | Description | Departments | When to Use |
|-------|-------------|-------------|-------------|
| **Route 1** | With Embroidery | Cutting → **Embroidery** → Sewing → Finishing → Packing | Artikel dengan logo/text (e.g., AFTONSPARV, KRAMIG) |
| **Route 2** | Without Embroidery | Cutting → ~~Embroidery~~ → Sewing → Finishing → Packing | Artikel simple/plain (e.g., BLÅHAJ, GOSIG) |

**Odoo Requirement**: Flexible routing configuration yang bisa pilih skip Embroidery stage based on artikel properties.

### Multi-UOM System Configuration

| Material Type | Primary UOM | Secondary UOM | Conversion Factor | Used In | Validation Required |
|---------------|-------------|---------------|-------------------|---------|---------------------|
| **Fabric** | YARD | METER | 1 YARD = 0.9144 METER | Purchasing (YARD), Cutting (YARD→PCS) | ✅ YES (Cutting output validation) |
| **Thread** | CM (Centimeter) | METER | 100 CM = 1 METER | Purchasing (METER), Production (CM) | ⚠️ WARNING only |
| **Filling** | GRAM | KG | 1000 GRAM = 1 KG | Purchasing (KG), Production (GRAM) | ✅ YES (Filling consumption validation) |
| **Finished Goods** | PCS (Pieces) | CTN (Carton) | 60 PCS = 1 CTN (default, varies by artikel) | Production (PCS), Shipping (CTN) | ✅ YES (FG receiving validation) |
| **Label** | PCS | - | - | Purchasing & Production | No validation |
| **Accessories** | PCS | - | - | Purchasing & Production | No validation |

**Critical Odoo Customization**:
```python
# Auto-validation pada UOM conversion
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _validate_uom_conversion(self):
        """Validate UOM conversion against BOM expected value"""
        # Example: Cutting YARD → PCS
        if self.workorder_id and self.workorder_id.workcenter_id.code == 'CUTTING':
            bom_marker = self._get_bom_marker()  # e.g., 0.1466 YARD per 1 PCS
            expected_pcs = self.product_uom_qty / bom_marker
            actual_pcs = self.workorder_id.qty_produced
            
            variance = abs((actual_pcs - expected_pcs) / expected_pcs) * 100
            
            if variance > 15:
                raise ValidationError(f"Conversion error! Variance {variance:.1f}% > 15%")
            elif variance > 10:
                return {'warning': f"Variance {variance:.1f}% > 10%, please verify"}
```

---

<a name="section-8"></a>
## 8️⃣ INVENTORY & WAREHOUSE MANAGEMENT

### Warehouse Structure

```
┌─────────────────────────────────────────────────────────────┐
│             PT QUTY KARUNIA - WAREHOUSE LAYOUT              │
└─────────────────────────────────────────────────────────────┘

WAREHOUSE MAIN (Central Storage)
│
├─ LOCATION: RAW MATERIALS
│  ├─ Zone A: Fabric (378 SKU)
│  │  ├─ Sub-zone A1: KOHAIR (45 SKU)
│  │  ├─ Sub-zone A2: BOA (32 SKU)
│  │  ├─ Sub-zone A3: POLYESTER (89 SKU)
│  │  └─ ... (more fabric types)
│  │
│  ├─ Zone B: Thread & Yarn (89 SKU)
│  │  ├─ Sub-zone B1: Black Thread (15 SKU)
│  │  ├─ Sub-zone B2: White Thread (12 SKU)
│  │  └─ ... (more colors)
│  │
│  ├─ Zone C: Filling & Stuffing (24 SKU)
│  │  ├─ Sub-zone C1: Dacron (8 SKU)
│  │  ├─ Sub-zone C2: Polyester Fiber (10 SKU)
│  │  └─ Sub-zone C3: Other filling (6 SKU)
│  │
│  ├─ Zone D: Label & Packaging (201 SKU)
│  │  ├─ Sub-zone D1: Hang Tags (45 SKU)
│  │  ├─ Sub-zone D2: EU Labels (67 SKU)
│  │  ├─ Sub-zone D3: Stickers (44 SKU)
│  │  └─ Sub-zone D4: Carton/Box (45 SKU)
│  │
│  └─ Zone E: Accessories (245 SKU)
│     ├─ Sub-zone E1: Button/Eyes (89 SKU)
│     ├─ Sub-zone E2: Plastic Parts (67 SKU)
│     └─ ... (more accessories)
│
├─ LOCATION: WIP STORAGE (Work In Progress)
│  ├─ WIP_CUTTING: Cut pieces (Body + Baju)
│  ├─ WIP_EMBROIDERY: Embroidered pieces
│  ├─ WIP_SEWING: Sewn pieces (Skin + Baju)
│  └─ WIP_HOLD: Baju waiting for final assembly
│
├─ LOCATION: WAREHOUSE FINISHING (Special - 2 Stage)
│  ├─ Stage 1 Storage: Skin (before stuffing)
│  ├─ Stage 2 Storage: Stuffed Body (before closing)
│  └─ Output Storage: Finished Doll (ready for packing)
│
└─ LOCATION: FINISHED GOODS
   ├─ FG_READY: Ready for shipment (per Week + Destination)
   ├─ FG_QC_HOLD: Quality check hold
   └─ FG_QUARANTINE: Customer complaint/return
```

### Stock Movement Rules (Odoo Routes Configuration)

#### Route 1: Raw Material Receiving

```
PO Confirmed → Vendor → Receiving Area → QC Inspection → Warehouse Main

Odoo Configuration:
- Push Rule: Receiving → Main Storage
- Pull Rule: Production Request → Main Storage
- Reorder Point: Auto-generate PO when stock < minimum
```

#### Route 2: Production Material Request

```
MO/WO Created → Material Request → Pick from Main → Deliver to Department

Odoo Configuration:
- Pull Rule: Each department has dedicated picking location
- Barcode Scan: Required for material issue
- Batch Picking: Group multiple WO material requests
```

#### Route 3: WIP Internal Transfer

```
Dept A Complete → QC Check → Internal Transfer → Dept B Input

Example: Cutting → Sewing
1. Cutting WO Complete → Output: WIP_CUT_BODY (500 pcs)
2. QC Inspection → Good: 490 pcs, Defect: 10 pcs
3. Internal Transfer: 490 pcs → WIP_SEWING location
4. Sewing WO Auto-receive: 490 pcs available to process

Odoo Configuration:
- Auto-transfer on WO completion
- QC checkpoint before transfer
- Defect auto-routed to Rework location
```

#### Route 4: Finishing 2-Stage (Special Internal Conversion)

```
Stage 1: Sewing Output → Warehouse Finishing → Stuffing → Stage 1 Storage
Stage 2: Stage 1 Output → Closing → Finished Doll → Main WIP

Odoo Custom Logic:
class FinishingInternalMove(models.Model):
    def process_stage1_stuffing(self):
        # Input: Skin from Sewing
        # Consume: Filling material
        # Output: Stuffed Body → Stage 2 location
        # NO delivery order generated (internal only)
        
    def process_stage2_closing(self):
        # Input: Stuffed Body from Stage 1
        # Consume: Thread
        # Output: Finished Doll → WIP main
        # NO delivery order generated (internal only)
```

#### Route 5: Finished Goods Receiving

```
Packing Complete → FG Barcode Labeling → FG Receiving → FG Ready

Process:
1. Packing WO output: 480 pcs AFTONSPARV
2. Pack into cartons: 8 CTN × 60 pcs = 480 pcs
3. Generate barcode label per carton: FG-2026-00089-CTN001 to CTN008
4. Scan each carton → Auto validation (UOM conversion PCS→CTN)
5. Move to FG Ready location (grouped by Week + Destination)

Odoo Configuration:
- Auto-generate lot/serial number per carton
- UOM conversion validation (PCS → CTN)
- Auto-group by Week & Destination for easier picking
```

### Stock Valuation Method

| Product Type | Valuation Method | Costing Method | Update Frequency |
|--------------|------------------|----------------|------------------|
| **Raw Materials** | Automated | Average Cost | Per PO receipt |
| **WIP (Work In Progress)** | Automated | Standard Cost + Actual Labor | Per WO completion |
| **Finished Goods** | Automated | Standard Cost (BOM) + Actual Production Cost | Real-time |
| **Consumables (Rags, Tools)** | Manual | - | Monthly adjustment |

**Odoo Configuration Required**:
```python
# Standard Cost + Actual Cost tracking per MO
class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'
    
    # Standard cost from BOM
    standard_material_cost = fields.Float(compute='_compute_standard_cost')
    standard_labor_cost = fields.Float(compute='_compute_standard_labor')
    standard_overhead_cost = fields.Float(compute='_compute_standard_overhead')
    
    # Actual cost from production
    actual_material_cost = fields.Float(compute='_compute_actual_material')
    actual_labor_cost = fields.Float(compute='_compute_actual_labor')
    actual_overhead_cost = fields.Float(compute='_compute_actual_overhead')
    
    # Variance
    cost_variance = fields.Float(compute='_compute_cost_variance')
    cost_variance_pct = fields.Float(compute='_compute_cost_variance_pct')
    
    def _compute_cost_variance(self):
        for mo in self:
            standard_total = mo.standard_material_cost + mo.standard_labor_cost + mo.standard_overhead_cost
            actual_total = mo.actual_material_cost + mo.actual_labor_cost + mo.actual_overhead_cost
            mo.cost_variance = actual_total - standard_total
            
            if standard_total:
                mo.cost_variance_pct = (mo.cost_variance / standard_total) * 100
```

### Inventory Accuracy Target & Cycle Count

| Location | Target Accuracy | Cycle Count Frequency | Method |
|----------|-----------------|----------------------|--------|
| RAW - Fabric | 98% | Weekly (by zone) | Barcode scan + physical count |
| RAW - Thread | 95% | Bi-weekly | Weight verification |
| RAW - Filling | 98% | Weekly | Weight scale + batch verification |
| RAW - Label | 99% | Monthly | Full count (critical for production trigger) |
| WIP | 92% | Daily (auto from WO) | System auto-track per WO |
| Finished Goods | 99.5% | Per shipment | Barcode scan (100% verification) |

**Odoo Cycle Count Configuration**:
- Automated cycle count schedule by location/zone
- ABC Analysis: A-items (critical) → weekly, B-items → bi-weekly, C-items → monthly
- Mobile barcode scanning for count input
- Auto-generate adjustment journal entry with approval workflow

---

<a name="section-9"></a>
## 9️⃣ ARCHITECTURE & TECHNOLOGY STACK

### Current Prototype Architecture (For Reference)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python 3.11 + FastAPI | REST API, Business Logic |
| **Database** | PostgreSQL 15 | Data persistence, 12GB estimated |
| **Frontend** | React 18 + TypeScript | Web UI (Desktop & Tablet) |
| **Mobile** | Kotlin + Jetpack Compose | Android app untuk barcode scanning |
| **Authentication** | JWT + OAuth2 | Secure authentication & authorization |
| **File Storage** | MinIO (S3-compatible) | Document & image storage |

### Odoo 18 Target Architecture

| Component | Odoo Module/Technology | Notes |
|-----------|------------------------|-------|
| **ERP Core** | Odoo 18 (Community or Enterprise?) | TBD - need Sales recommendation |
| **Database** | PostgreSQL 14+ | Existing data migration required |
| **Web Framework** | Odoo Web Framework | Built-in, responsive UI |
| **Mobile App** | Odoo Mobile + Custom Native App | Hybrid: Odoo mobile for basic, Custom for barcode heavy usage |
| **Reporting** | Odoo Studio + Custom Reports | QWeb for standard, Custom for complex analytics |
| **API Integration** | Odoo XML-RPC / JSON-RPC | For external system integration (future) |
| **Authentication** | Odoo Users Module | RBAC built-in |
| **Hosting** | On-Premise or Cloud? | TBD - need recommendation |

### Odoo Modules Required (Estimation)

#### Standard Odoo Modules (Out-of-the-box)

| Module | Purpose | Customization Level |
|--------|---------|---------------------|
| `mrp` | Manufacturing / MRP | 🔴 HEAVY (Dual Trigger, Flexible Target, etc.) |
| `purchase` | Purchase Management | 🟠 MEDIUM (3 PO types, Dual Trigger) |
| `stock` | Inventory & Warehouse | 🟠 MEDIUM (Multi-UOM validation, 2-stage Finishing) |
| `quality_control` | Quality Management | 🟠 MEDIUM (Rework module integration) |
| `sale` | Sales Management | 🟡 LIGHT (Standard, minor customization) |
| `account` | Accounting | 🟡 LIGHT (Standard, WIP valuation custom) |
| `barcodes` | Barcode Scanning | 🟠 MEDIUM (Custom workflows for FG & Finishing) |
| `hr` | Human Resources | 🟢 NONE (Standard usage) |
| `project` | Project Management | 🟢 NONE or SKIP (may not be needed) |

#### Custom Modules Required (New Development)

| Custom Module Name | Purpose | Estimated LOC | Priority |
|--------------------|---------|---------------|----------|
| `quty_dual_trigger` | Dual Trigger Production System | 1,500 lines | 🔴 CRITICAL |
| `quty_flexible_target` | Flexible Target per Department | 800 lines | 🔴 CRITICAL |
| `quty_dual_bom` | Dual-BOM System (Production + Purchasing) | 1,200 lines | 🔴 CRITICAL |
| `quty_finishing_2stage` | Warehouse Finishing 2-Stage Internal Conversion | 900 lines | 🔴 MUST-HAVE |
| `quty_uom_validation` | UOM Conversion Auto-Validation | 500 lines | 🔴 MUST-HAVE |
| `quty_rework_qc` | Rework/Repair Module + QC Integration | 1,000 lines | 🟠 HIGH |
| `quty_week_destination` | Week/Destination Auto-Inheritance & Lock | 300 lines | 🔴 MUST-HAVE |
| `quty_material_debt` | Material Debt (Negative Stock) with Approval | 700 lines | 🟠 HIGH |
| `quty_mobile_barcode` | Custom Mobile Barcode Workflows | 1,200 lines | 🟠 HIGH |
| `quty_dashboard` | Real-Time Dashboard & Analytics | 600 lines | 🟠 MEDIUM |

**Total Custom Development Estimate**: ~8,700 lines of Python code + XML views

### Infrastructure Requirements

#### On-Premise Deployment (If chosen)

| Component | Specification | Quantity | Purpose |
|-----------|---------------|----------|---------|
| **Application Server** | CPU: 8 cores, RAM: 32GB, SSD: 500GB | 2 units | Odoo app server (load balanced) |
| **Database Server** | CPU: 16 cores, RAM: 64GB, SSD: 1TB (NVMe) | 1 unit | PostgreSQL primary + standby replication |
| **File Storage** | NAS: 2TB | 1 unit | Documents, attachments, backups |
| **Backup Server** | HDD: 4TB | 1 unit | Daily backup retention (30 days) |
| **Network** | 100 Mbps dedicated internet | - | For cloud backup & remote access |

#### Cloud Deployment (If chosen - Recommended for scalability)

| Service | Provider | Specification | Purpose |
|---------|----------|---------------|---------|
| **Compute** | AWS EC2 / Azure VM / GCP Compute | c5.2xlarge (8 vCPU, 16GB RAM) | Odoo application |
| **, **Database** | AWS RDS / Azure Database / GCP Cloud SQL | PostgreSQL 14, db.m5.xlarge (4 vCPU, 16GB RAM, 500GB SSD) | Managed PostgreSQL |
| **Storage** | AWS S3 / Azure Blob / GCP Storage | 500GB | File attachments |
| **Backup** | AWS Backup / Azure Backup | Automated daily | Disaster recovery |
| **Load Balancer** | AWS ELB / Azure LB | Standard | High availability |

**Monthly Cost Estimate (Cloud)**:
- Compute: $350-450/month
- Database: $400-500/month
- Storage: $25-50/month
- Backup: $50-80/month
- Network: $100-150/month
- **Total**: ~$1,000-1,300/month

---

<a name="section-10"></a>
## 🗄️ DATABASE SCHEMA OVERVIEW

### Current Prototype Schema (For Reference & Migration)

**Total Tables**: 45 tables  
**Total Estimated Rows** (after 1 year): ~180,000 transactions  
**Database Size**: ~8GB (with indexes ~12GB)

#### Core Tables (High Priority for Migration to Odoo)

| Table Name | Purpose | Row Count (est.) | Odoo Equivalent | Migration Complexity |
|------------|---------|------------------|-----------------|----------------------|
| `products` | Master data products (Materials + Articles) | 1,732 rows | `product.product`, `product.template` | 🟡 MEDIUM |
| `bom_production_headers` | BOM Production headers | 478 rows | `mrp.bom` | 🟠 HIGH (custom type field) |
| `bom_production_details` | BOM Production lines | 5,845 rows | `mrp.bom.line` | 🟠 HIGH (dept routing) |
| `bom_purchasing_headers` | BOM Purchasing headers | 478 rows | Custom table or `mrp.bom` with type | 🔴 CRITICAL |
| `bom_purchasing_details` | BOM Purchasing lines | 2,891 rows | Custom table or `mrp.bom.line` | 🔴 CRITICAL |
| `purchase_orders` | Purchase Orders | ~1,200/year | `purchase.order` | 🟡 MEDIUM (custom PO type field) |
| `purchase_order_lines` | PO Lines | ~3,600/year | `purchase.order.line` | 🟡 MEDIUM |
| `manufacturing_orders` | Manufacturing Orders (MO) | ~800/year | `mrp.production` | 🔴 CRITICAL (custom states: PARTIAL/RELEASED) |
| `work_orders` (SPK) | Work Orders per department | ~4,800/year | `mrp.workorder` | 🔴 CRITICAL (flexible target field) |
| `daily_productions` | Daily production input per SPK | ~24,000/year | Custom table or `mrp.workorder` history | 🟠 HIGH |
| `finishing_conversions` | Finishing 2-stage conversions | ~1,600/year | Custom table `finishing.conversion` | 🔴 NEW MODULE |
| `rework_requests` | Rework/QC tracking | ~600/year | Custom table `quality.rework.request` | 🔴 NEW MODULE |
| `material_debts` | Material debt (negative stock approved) | ~120/year | Custom table `material.debt` | 🔴 NEW MODULE |
| `stock_moves` | Inventory movements | ~35,000/year | `stock.move` | 🟡 MEDIUM (UOM validation field) |
| `users` | System users | 111 users | `res.users` | 🟢 EASY |
| `audit_logs` | Audit trail (5W1H) | ~150,000/year | `auditlog.log` (Odoo module) or custom | 🟡 MEDIUM |

### Key Custom Fields Required in Odoo Models

#### 1. `mrp.production` (Manufacturing Order)

```python
class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    # Dual Trigger fields
    po_fabric_id = fields.Many2one('purchase.order', 'PO Fabric (Trigger 1)')
    po_label_id = fields.Many2one('purchase.order', 'PO Label (Trigger 2)')
    
    # Custom states
    state = fields.Selection(selection_add=[
        ('partial', 'Partial (Fabric Ready)'),
        ('released', 'Released (Label Ready)'),
    ])
    
    # Week & Destination (from PO Label - LOCKED)
    production_week = fields.Char('Production Week', readonly=True)
    destination_country = fields.Char('Destination Country', readonly=True)
    week_destination_locked = fields.Boolean('Week/Dest Locked', default=False)
    
    # Routing type
    routing_type = fields.Selection([
        ('route1', 'Route 1 (With Embroidery)'),
        ('route2', 'Route 2 (Without Embroidery)'),
    ], 'Routing Type', required=True)
```

#### 2. `mrp.workorder` (Work Order / SPK)

```python
class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    # Flexible Target System
    target_qty = fields.Float('Target Quantity')  # Can differ from MO qty
    buffer_percentage = fields.Float('Buffer %', related='workcenter_id.default_buffer_pct')
    
    # Production tracking (Good vs Defect)
    good_qty = fields.Float('Good Output', compute='_compute_good_qty')
    defect_qty = fields.Float('Defect Quantity')
    yield_rate = fields.Float('Yield %', compute='_compute_yield_rate')
    
    # Rework integration
    rework_request_ids = fields.One2many('quality.rework.request', 'workorder_id', 'Rework Requests')
```

#### 3. `purchase.order` (Purchase Order)

```python
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    # Custom PO Type
    po_type_custom = fields.Selection([
        ('fabric', 'PO Fabric'),
        ('label', 'PO Label'),
        ('accessories', 'PO Accessories'),
    ], 'PO Type')
    
    # For PO Label only
    production_week = fields.Char('Production Week')  # Format: W05-2026
    destination_country = fields.Char('Destination Country')
    
    # Link to MO (for Dual Trigger)
    manufacturing_order_id = fields.Many2one('mrp.production', 'Related MO')
```

#### 4. `mrp.bom` (Bill of Materials)

```python
class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    # Dual-BOM type
    bom_type_custom = fields.Selection([
        ('production', 'BOM Production'),
        ('purchasing', 'BOM Purchasing'),
    ], 'BOM Type (Custom)', required=True)
    
    # Auto-sync
    source_production_bom_id = fields.Many2one('mrp.bom', 'Source Production BOM')
    
    # Routing info per line (for Production BOM)
    # (handled in mrp.bom.line below)
```

#### 5. `mrp.bom.line` (BOM Line)

```python
class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    # Department routing (for Production BOM)
    department_id = fields.Many2one('hr.department', 'Department')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center')
    
    # Operation sequence (which stage in production)
    operation_sequence = fields.Integer('Operation Sequence')
    
    # Material type classification
    material_type = fields.Selection([
        ('raw', 'RAW Material'),
        ('wip', 'WIP Component'),
    ], 'Material Type', compute='_compute_material_type')
```

#### 6. `stock.move` (Stock Move)

```python
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    # UOM Conversion Validation
    uom_conversion_validation = fields.Boolean('Enable UOM Validation', default=True)
    expected_conversion_qty = fields.Float('Expected Qty (from BOM)')
    actual_input_qty = fields.Float('Actual Input Qty')
    conversion_variance_pct = fields.Float('Variance %', compute='_compute_conversion_variance')
    
    # Material debt tracking
    material_debt_id = fields.Many2one('material.debt', 'Related Material Debt')
```

### Data Migration Strategy

#### Phase 1: Master Data (Week 1-2)

| Data Type | Source | Destination | Method | Validation |
|-----------|--------|-------------|--------|------------|
| **Products** (Materials) | `products` table (type='material') | `product.product` | CSV export → Odoo import | SKU code uniqueness |
| **Products** (Articles/FG) | `products` table (type='article') | `product.product` | CSV export → Odoo import | Article code uniqueness |
| **Suppliers** | `suppliers` table | `res.partner` (supplier=True) | CSV export → Odoo import | Tax ID uniqueness |
| **BOM Production** | `bom_production_*` tables | `mrp.bom` (custom type) | Custom Python script | BOM explosion verification |
| **BOM Purchasing** | `bom_purchasing_*` tables | Custom `mrp.bom` or separate table | Custom Python script | Material aggregation check |
| **Users** | `users` table | `res.users` | Manual creation + CSV | Role mapping verification |

#### Phase 2: Transactional Data (Week 3-4)

| Data Type | Source | Destination | Method | Notes |
|-----------|--------|-------------|--------|-------|
| **Open PO** | `purchase_orders` (state!='done') | `purchase.order` | CSV import | Only open/pending PO |
| **Open MO** | `manufacturing_orders` (state!='done') | `mrp.production` | Custom script (due to custom states) | PARTIAL/RELEASED state mapping |
| **Stock on Hand** | `stock_quants` | `stock.quant` | Inventory adjustment | Physical count verification |
| **WIP Stock** | `finishing_stocks`, WIP locations | Custom locations in Odoo | Manual entry + adjustment | Critical for production continuity |

####Phase 3: Historical Data (Week 5-6) - Optional

| Data Type | Retention Period | Migration Priority | Method |
|-----------|------------------|-------------------|--------|
| **Completed MO** (last 6 months) | 6 months | 🟡 MEDIUM (for reporting) | Archived import (read-only) |
| **Completed PO** (last 12 months) | 12 months | 🟢 LOW (for vendor analysis) | Archived import |
| **Audit Logs** (last 3 months) | 3 months | 🟢 LOW (compliance) | Separate archive database |

**Migration Tools**:
- Odoo built-in import (CSV for simple data)
- Custom Python scripts using `odoorpc` library (for complex data with validations)
- PostgreSQL direct connection (for bulk data, with caution)

---

<a name="section-11"></a>
## 🔗 INTEGRATION REQUIREMENTS

### Current External Systems (None - Standalone)

PT Quty Karunia currently does **NOT** have external system integrations. However, future integration possibilities should be considered:

### Future Integration Possibilities (Post Go-Live)

| System | Purpose | Integration Method | Priority | Timeline |
|--------|---------|-------------------|----------|----------|
| **IKEA EDI System** | Customer PO auto-import, Shipment notification | EDI (XML/JSON via API) | 🟠 MEDIUM | 6-12 months after go-live |
| **Accounting Software** (if different from Odoo Accounting) | Financial data sync | Odoo XML-RPC API | 🟡 LOW | TBD |
| **Payroll System** | Employee attendance → payroll | CSV export/import or API | 🟡 LOW | TBD |
| **Shipping/Logistics** (Forwarder system) | Shipment tracking | API or manual entry | 🟡 LOW | 12+ months |
| **E-Procurement Platform** (Supplier portal) | Auto-PO to suppliers | B2B portal or email | 🟢 FUTURE | 18+ months |

**Current Recommendation**: Focus on **standalone Odoo implementation** first. Plan integration architecture untuk future extensibility.

### Internal Integration (Within Odoo)

| Integration Point | Modules Involved | Trigger | Auto-Action |
|-------------------|------------------|---------|-------------|
| **PO → MO (Dual Trigger)** | `purchase`, `mrp` | PO Fabric validated | Create MO (state='partial') |
| **PO Label → MO Upgrade** | `purchase`, `mrp` | PO Label validated | Upgrade MO to 'released', inherit Week/Destination |
| **MO → SPK Generation** | `mrp` | MO state='released' | Auto-generate Work Orders per department |
| **SPK Complete → Next SPK** | `mrp` | Work Order done | Auto-trigger next department WO |
| **Defect → Rework** | `quality`, `mrp` | Defect registered | Create Rework Request |
| **Rework Approved → WO** | `quality`, `mrp` | QC approve rework | Create Rework Work Order |
| **Material Low Stock → PO** | `stock`, `purchase` | Stock < reorder point | Auto-generate PO draft (PPIC approve) |
| **FG Complete → Accounting** | `mrp`, `account` | MO done | Auto-post WIP → FG journal entry |

---

<a name="section-12"></a>
## 📱 MOBILE APPLICATIONS

### Use Cases for Mobile/Tablet

| User Role | Device | Primary Use Case | Features Required |
|-----------|--------|------------------|-------------------|
| **Warehouse Staff** | Android Tablet (10") | Material receiving, Internal transfer, Stock adjustment | Barcode scanning, Camera, Offline mode |
| **Production Operator** | Android Tablet (8") | Daily production input, Defect reporting | Simplified UI, Barcode scan (optional), Offline mode |
| **QC Inspector** | Android Tablet (10") | Quality inspection, Rework approval | Camera (defect photos), Signature capture, Online required |
| **PPIC** | Windows Laptop/Tablet | MO monitoring, SPK tracking | Full web UI (Odoo standard) |
| **Manager/Director** | Smartphone (iOS/Android) | Dashboard view, Approval | Mobile-responsive Odoo web UI |

### Mobile App Strategy

#### Option A: Odoo Mobile App (Built-in)

**Pros**:
- Free (included in Odoo)
- Automatic sync with Odoo backend
- Support most standard modules

**Cons**:
- Limited customization for complex workflows
- Barcode scanning less robust than native
- Offline mode limited

**Recommendation**: Use for **PPIC, Manager, Director** (dashboard & approval only)

#### Option B: Custom Native Android App

**Pros**:
- Full control over UI/UX
- Robust barcode scanning (Zebra SDK, Honeywell SDK)
- Better offline mode with local SQLite cache
- Optimized for factory floor (large buttons, simple flow)

**Cons**:
- Additional development cost ($15,000 - $25,000)
- Maintenance overhead
- Need separate Odoo API integration

**Recommendation**: Develop for **Warehouse Staff & Production Operator** (heavy barcode usage)

#### Option C: Hybrid Approach (RECOMMENDED)

**Warehouse & Production**: Custom Native Android App
- Barcode scanning for material issue
- FG receiving with UOM validation
- Daily production input (simplified form)
- Offline capability (sync when online)

**PPIC, QC, Manager**: Odoo Mobile Web (Responsive)
- MO/SPK monitoring dashboard
- Approval workflows
- QC inspection (with photo upload)

**Estimated Cost**:
- Custom Android App development: $18,000 - $22,000
- Odoo Mobile web responsive customization: $3,000 - $5,000
- **Total**: $21,000 - $27,000

### Mobile Key Features

#### Custom Android App for Warehouse

**Screens**:
1. **Login** (fingerprint/PIN)
2. **Home Dashboard**
   - Pending tasks count
   - Recent scans history
3. **Material Receiving** (from PO)
   - Scan barcode (material code)
   - Input quantity received
   - Select location (zone/bin)
   - Photo (optional, for quality check)
   - Submit → Create stock move in Odoo
4. **Internal Transfer** (Dept to Dept)
   - Scan barcode (material/WIP)
   - Select source location
   - Select destination location
   - Input quantity
   - Submit → Create internal transfer in Odoo
5. **FG Receiving** (from Packing)
   - Scan barcode (FG carton)
   - Auto-validate UOM (60 pcs/carton)
   - Display: Article, Week, Destination
   - Confirm → Move to FG location
6. **Stock Adjustment**
   - Select location
   - Scan barcode
   - Input actual count
   - Reason (dropdown)
   - Submit → Create adjustment journal

#### Custom Android App for Production Operator

**Screens**:
1. **Login** (simplified, PIN only)
2. **My SPK Today**
   - List of assigned SPK
   - Status: Not Started / In Progress / Done
3. **SPK Detail**
   - SPK info (artikel, target, date)
   - View BOM materials (list)
4. **Daily Production Input**
   - Date picker
   - Input good qty
   - Input defect qty (if any)
   - Select defect category (dropdown)
   - Add note (optional)
   - Submit → Create daily_production record
5. **Report Defect**
   - Photo defect (camera)
   - Select defect category
   - Input defect count
   - Submit → Create defect record

**Technical Stack** (Custom Android App):
- Language: Kotlin
- UI Framework: Jetpack Compose
- Barcode: ZXing library atau Zebra SDK (if using Zebra devices)
- Offline Storage: Room (SQLite)
- API: Retrofit (to Odoo JSON-RPC API)
- Photo: CameraX library

---

<a name="section-13"></a>
## 📊 REPORTING & ANALYTICS

### Required Reports (Standard + Custom)

#### Production Reports

| Report Name | Frequency | Audience | Output Format | Odoo Module | Customization Level |
|-------------|-----------|----------|---------------|-------------|---------------------|
| **Daily Production Summary** | Daily (auto 8 AM) | PPIC, Manager | PDF, Email | `mrp` | 🟠 MEDIUM (custom template) |
| **Weekly Production Plan** | Weekly (Monday) | PPIC, Production SPV | PDF, Excel | `mrp` | 🟡 LIGHT |
| **MO Completion Report** | Per MO done | PPIC, Accounting | PDF | `mrp` | 🟡 LIGHT |
| **SPK Progress Tracking** | Real-time dashboard | PPIC, Manager | Web dashboard | `mrp` | 🟠 MEDIUM (custom dashboard) |
| **Department Efficiency** | Weekly | Manager, Production SPV | Excel, Chart | `mrp`, custom | 🟠 MEDIUM |
| **Defect Analysis (by Dept)** | Weekly | QC, Manager | Excel, Chart | `quality`, custom | 🟠 MEDIUM |
| **Rework Cost (COPQ)** | Monthly | Manager, Finance | PDF, Excel | `quality`, custom | 🔴 HIGH (custom calculation) |
| **Yield Rate Analysis** | Weekly | PPIC, Manager | Excel, Chart | `mrp`, custom | 🟠 MEDIUM |

#### Inventory Reports

| Report Name | Frequency | Audience | Output Format | Odoo Module | Customization Level |
|-------------|-----------|----------|---------------|-------------|---------------------|
| **Stock on Hand (by Location)** | Daily | Warehouse, PPIC | PDF, Excel | `stock` | 🟢 NONE (standard) |
| **Material Consumption Report** | Per MO | PPIC, Accounting | PDF | `mrp`, `stock` | 🟡 LIGHT |
| **Low Stock Alert** | Daily (auto notification) | Purchasing | Email, Dashboard | `stock` | 🟢 NONE (standard reorder point) |
| **Stock Valuation** | Monthly | Accounting, Manager | PDF, Excel | `stock`, `account` | 🟡 LIGHT |
| **WIP Valuation (by Stage)** | Monthly | Accounting | PDF, Excel | Custom | 🔴 HIGH (custom WIP tracking) |
| **Cycle Count Variance** | Per cycle count | Warehouse SPV, Manager | PDF | `stock` | 🟡 LIGHT |
| **Material Debt Report** | Weekly | Manager, PPIC | PDF, Excel | Custom | 🟠 MEDIUM (custom module) |
| **Fabric Yield Report** | Per MO | PPIC, Purchasing | Excel, Chart | Custom | 🔴 HIGH (Yard→Pcs variance analysis) |

#### Purchasing Reports

| Report Name | Frequency | Audience | Output Format | Odoo Module | Customization Level |
|-------------|-----------|----------|---------------|-------------|---------------------|
| **PO Summary (by Type)** | Weekly | Purchasing Manager | PDF, Excel | `purchase` | 🟡 LIGHT (group by PO type) |
| **Vendor Performance** | Monthly | Purchasing Manager | PDF, Chart | `purchase` | 🟠 MEDIUM |
| **PO vs Receipt Variance** | Per PO received | Purchasing, Warehouse | PDF | `purchase`, `stock` | 🟡 LIGHT |
| **Lead Time Analysis (by Vendor)** | Monthly | Purchasing Manager | Excel, Chart | `purchase` | 🟠 MEDIUM |
| **Material Forecast (MRP)** | Weekly | Purchasing, PPIC | Excel | `mrp`, `purchase` | 🟡 LIGHT (standard MRP report) |

#### Financial Reports

| Report Name | Frequency | Audience | Output Format | Odoo Module | Customization Level |
|-------------|-----------|----------|---------------|-------------|---------------------|
| **COGS per Article** | Monthly | Finance, Manager | Excel | `account`, `mrp` | 🟠 MEDIUM |
| **Production Cost Variance** | Per MO | Finance, PPIC | PDF | Custom | 🔴 HIGH (Standard vs Actual) |
| **WIP Valuation** | Month-end | Finance | PDF | Custom | 🔴 HIGH (per stage valuation) |
| **Inventory Valuation** | Month-end | Finance | PDF, Excel | `stock`, `account` | 🟢 NONE (standard) |
| **P&L by Product Line** | Monthly | Finance, Director | PDF | `account` | 🟡 LIGHT |

#### Management Dashboard (Real-Time)

**PPIC Dashboard**:
```
┌────────────────────────────────────────────────────┐
│  PPIC DASHBOARD - Real-Time                        │
├────────────────────────────────────────────────────┤
│  📊 SPK Today: 15 total                           │
│      ✅ Completed: 8 (53%)                        │
│      🔄 In Progress: 5 (33%)                      │
│      ⚠️ Delayed: 2 (13%)                          │
│                                                    │
│  📦 Material Stock (Critical):                    │
│      🔴 [IKHR504] KOHAIR: 125 YD (Low: 62%)      │
│      ✅ [IKP20157] Filling: 45 KG (OK)           │
│      ⚠️ [ACB30104] Carton: 18 PCE (Critical!)    │
│                                                    │
│  🏭 Production Today (AFTONSPARV):                │
│      Target: 480 pcs │ Actual: 465 pcs (96.9%)   │
│      - Boneka: 465 pcs ✅                         │
│      - Baju: 470 pcs ✅                           │
│                                                    │
│  [VIEW DETAILS] [EXPORT PDF]                      │
└────────────────────────────────────────────────────┘
```

**Manager Dashboard**:
```
┌────────────────────────────────────────────────────┐
│  DIRECTOR/MANAGER DASHBOARD                        │
├────────────────────────────────────────────────────┤
│  🎯 KPI This Month:                                │
│  ├─ OTD (On-Time Delivery): 94.2% (▲ 2.1%)       │
│  ├─ Fabric Yield: 91.5% (▼ 0.8%)                 │
│  ├─ Defect Rate: 2.8% (▼ 0.5%)                   │
│  └─ COPQ (Cost of Poor Quality): $2,850 (▼ 12%)  │
│                                                    │
│  💰 Financial Snapshot:                            │
│  ├─ WIP Value: $125,000                           │
│  ├─ FG Value: $180,000                            │
│  └─ Raw Material Value: $220,000                  │
│                                                    │
│  📈 Production Volume (MTD):                       │
│  ├─ Target: 65,000 pcs                            │
│  ├─ Actual: 62,300 pcs (95.8%)                    │
│  └─ Forecast: 68,500 pcs (105.4%) ✅             │
│                                                    │
│  ⚠️ Alerts & Actions Required:                     │
│  ├─ 3 PO pending approval (>$10,000)              │
│  ├─ 5 Material Debt requests awaiting approval    │
│  └─ 2 Customer PO at risk (Week 6 delivery)       │
│                                                    │
│  [VIEW DETAILS] [EXPORT REPORT]                   │
└────────────────────────────────────────────────────┘
```

### Custom Dashboard Development

**Technology**: Odoo Dashboard / Board module + Custom JavaScript widgets

**Widgets Required**:
1. **KPI Cards** (OTD, Yield, Defect Rate, COPQ)
2. **Production Progress Bar** (per SPK, per Department)
3. **Material Stock Gauge** (color-coded: Green/Yellow/Red)
4. **Line Chart** (Production trend 7 days)
5. **Bar Chart** (Defect by category)
6. **Table** (Top 10 delayed SPK, Critical stock items)

**Estimated Development**: 5-7 days for custom dashboards

---

<a name="section-14"></a>
## 🧩 ODOO MODULES MAPPING

### Must-Have Odoo Modules (Cannot skip)

| Odoo Module | Purpose | License | Cost (if Enterprise) | Priority |
|-------------|---------|---------|----------------------|----------|
| **Manufacturing (`mrp`)** | Core MRP, MO, BOM, Work Orders | Community/Enterprise | Included in Enterprise | 🔴 CRITICAL |
| **Inventory (`stock`)** | Warehouse, Stock moves, Locations | Community/Enterprise | Included | 🔴 CRITICAL |
| **Purchase (`purchase`)** | Purchase Orders, Vendor management | Community/Enterprise | Included | 🔴 CRITICAL |
| **Sales (`sale`)** | Sales Orders (for customer orders) | Community/Enterprise | Included | 🔴 REQUIRED |
| **Accounting (`account`)** | Financial records, COGS, WIP valuation | Community/Enterprise | Included | 🔴 REQUIRED |
| **Barcodes (`barcodes`)** | Barcode scanning operations | Enterprise only | Part of Enterprise | 🟠 HIGH (or custom) |
| **Quality (`quality_control`)** | Quality checkpoints, QC workflow | Enterprise only | Part of Enterprise | 🟠 HIGH |

### Recommended Odoo Modules (For better functionality)

| Odoo Module | Purpose | License | Benefit | Priority |
|-------------|---------|---------|---------|----------|
| **MRP Workorder (`mrp_workorder`)** | Work Order management with tablet view | Enterprise | Operator tablet interface | 🟠 HIGH |
| **MRP Subcontracting** | (NOT needed for Quty) | Enterprise | N/A | ❌ SKIP |
| **Product Lifecycle Management (`plm`)** | BOM versioning, Engineering changes | Enterprise | Version control for BOM | 🟡 MEDIUM |
| **MRP Maintenance** | Equipment maintenance | Enterprise | Machine downtime tracking | 🟡 OPTIONAL |
| **HR (`hr`)** | Employee database | Community | Basic | 🟢 NICE-TO-HAVE |
| **Audit Trail (`auditlog`)** | Track all changes (5W1H) | Community (OCA) | Compliance, forensic analysis | 🟠 HIGH |
| **Dashboard Ninja** | Custom dashboard builder | Community (Third-party) | Visual dashboard without coding | 🟡 OPTIONAL |

### Odoo Edition Recommendation: Community vs Enterprise?

| Factor | Community | Enterprise | Recommendation |
|--------|-----------|------------|----------------|
| **Cost** | Free (self-hosted) | ~$30-50/user/month | Community saves $40,000-60,000/year for 111 users |
| **Barcode Module** | ❌ Not included (need custom or third-party) | ✅ Included | **Enterprise** if heavy barcode usage |
| **Quality Module** | ⚠️ Limited (OCA alternative) | ✅ Full-featured | **Enterprise** for QC workflow |
| **Mobile App** | ⚠️ Web-responsive only | ✅ Native mobile app | **Enterprise** atau develop custom |
| **Support** | Community forum | Official Odoo support | Community + Partner support OK |
| **Hosting** | Self-hosted or Cloud | Odoo SaaS or self-hosted | Either OK |
| **Customization** | ✅ Full access to source | ✅ Full access | Tie |

**💡 RECOMMENDATION for PT Quty Karunia**: **Odoo 18 ENTERPRISE Edition**

**Justification**:
1. **Barcode Module** essential untuk Warehouse & Production (avoid custom development cost)
2. **Quality Module** needed untuk Rework/QC workflow
3. **Better Mobile App** untuk operator (atau combine dengan custom Android app)
4. **Official Support** penting untuk production-critical system
5. **Cost**: ~$5,000-6,000/month ($60,000-72,000/year) **vs** Community + Heavy Customization (~$50,000-80,000 one-time untuk replicate Enterprise features)

**ROI Calculation**:
- Enterprise cost: $72,000/year
- Community + Custom Dev: $70,000 first year + $15,000/year maintenance
- **Winner**: Enterprise (better long-term value + official support)

---

<a name="section-15"></a>
## 🛠️ CUSTOMIZATION REQUIREMENTS SUMMARY

### Customization Effort Breakdown

| Customization Area | Complexity | Estimated Days | Priority | Module Affected |
|--------------------|------------|----------------|----------|-----------------|
| **Dual Trigger Production System** | 🔴 CRITICAL | 15-20 days | 🔴 MUST-HAVE | `mrp`, `purchase` |
| **Flexible Target per Department** | 🔴 HIGH | 10-12 days | 🔴 MUST-HAVE | `mrp` (Work Orders) |
| **Dual-BOM System** | 🔴 CRITICAL | 12-15 days | 🔴 MUST-HAVE | `mrp` (BOM) |
| **Warehouse Finishing 2-Stage** | 🟠 HIGH | 8-10 days | 🔴 MUST-HAVE | `stock`, `mrp` |
| **UOM Conversion Auto-Validation** | 🟠 MEDIUM | 5-7 days | 🔴 MUST-HAVE | `stock`, `mrp` |
| **Rework/Repair Module** | 🟠 MEDIUM | 8-10 days | 🟠 HIGH | `quality`, `mrp` |
| **Week/Destination Auto-Inheritance** | 🟡 MEDIUM | 5-7 days | 🔴 MUST-HAVE | `purchase`, `mrp` |
| **Material Debt System** | 🟠 HIGH | 7-9 days | 🟠 HIGH | `stock`, approval workflow |
| **Custom Mobile Barcode App** | 🔴 HIGH | 15-20 days | 🟠 HIGH | Android app + Odoo API |
| **Real-Time Dashboard** | 🟡 MEDIUM | 5-7 days | 🟠 MEDIUM | `board`, custom reports |
| **Custom Reports (10+)** | 🟡 MEDIUM | 8-10 days | 🟠 MEDIUM | Various modules |
| **Data Migration Scripts** | 🟠 MEDIUM | 8-10 days | 🔴 REQUIRED | All modules |
| **Integration Testing** | 🟠 HIGH | 10-15 days | 🔴 REQUIRED | QA |
| **User Training Material** | 🟡 LIGHT | 5-7 days | 🔴 REQUIRED | Documentation |

**Total Development Effort**: **116-159 days** (~5-7 months for 2 developers working full-time)

**🔴 CRITICAL PATH**: Dual Trigger + Dual-BOM + Flexible Target = 37-47 days (2 months minimum for core features)

###Risk Mitigation Strategy

| Risk | Probability | Impact | Mitigation | Contingency Plan |
|------|-------------|--------|------------|------------------|
| **Customization too complex for Odoo** | 🟡 MEDIUM | 🔴 HIGH | Proof-of-concept for critical features in Week 1-2 | Consider full custom development atau Odoo + external microservices |
| **Data migration issues** | 🟠 HIGH | 🟠 MEDIUM | Parallel run (old + new system) for 1 month | Extend cutover timeline |
| **User adoption resistance** | 🟠 HIGH | 🟠 MEDIUM | Intensive training + change management | Gradual rollout (dept by dept) |
| **Performance issues (large BOM)** | 🟡 MEDIUM | 🟠 MEDIUM | Load testing with real data | Database optimization, caching, indexing |
| **Mobile app compatibility** | 🟡 MEDIUM | 🟡 LOW | Device testing (Zebra, Honeywell, generic Android) | Fallback to web-based scanning |
| **Budget overrun** | 🟠 HIGH | 🟠 MEDIUM | Phased implementation (MVP first) | Reduce scope (defer nice-to-have features) |

---

<a name="section-16"></a>
## ⚖️ GAP ANALYSIS: ODOO STANDARD vs REQUIREMENTS

### Major Gaps (Require Heavy Customization)

| Feature Required | Odoo Standard | Gap | Customization Effort |
|------------------|---------------|-----|----------------------|
| **Dual Trigger MO from 2 PO** | ❌ MO from Sales Order only | 🔴 CRITICAL GAP | 15-20 days |
| **MO State: PARTIAL/RELEASED** | ❌ Standard states: draft/confirmed/progress/done | 🔴 CRITICAL GAP | Part of Dual Trigger |
| **Flexible SPK Target ≠ MO Target** | ❌ WO qty = MO qty (rigid) | 🔴 CRITICAL GAP | 10-12 days |
| **Dual-BOM (Production + Purchasing)** | ❌ 1 BOM per product | 🔴 CRITICAL GAP | 12-15 days |
| **Warehouse Finishing 2-Stage Internal Conversion** | ❌ Standard internal transfer needs DO | 🟠 HIGH GAP | 8-10 days |
| **UOM Conversion Auto-Validation** | ⚠️ Manual validation only | 🟠 MEDIUM GAP | 5-7 days |
| **Rework/Repair Module + QC Integration** | ⚠️ Basic quality check, no rework tracking | 🟠 HIGH GAP | 8-10 days |
| **Week & Destination LOCKED from PO Label** | ❌ No concept of locked fields from PO | 🟠 MEDIUM GAP | 5-7 days |
| **Material Debt (Negative Stock with Approval)** | ⚠️ Can allow negative, but no approval workflow | 🟠 MEDIUM GAP | 7-9 days |
| *Custom Android Barcode App** | ⚠️ Has barcode module, but limited customization | 🟠 MEDIUM GAP | 15-20 days (if custom) |
| **Real-Time Dashboard with Custom KPI** | ⚠️ Has dashboard, but limited customization | 🟡 LOW GAP | 5-7 days |

### Minor Gaps (Can Use Standard with Light Customization)

| Feature Required | Odoo Standard | Gap | Customization Effort |
|------------------|---------------|-----|----------------------|
| **Multi-UOM per Product** | ✅ Supported | ✅ NONE | 0 days (config only) |
| **Multi-Location Warehouse** | ✅ Supported | ✅ NONE | 0 days (config only) |
| **Routing (with/without Embroidery)** | ✅ Supported (routing optional steps) | ✅ NONE | 0 days (config only) |
| **Barcode Scanning (Web)** | ✅ Supported (Enterprise) | ✅ NONE | 0 days (if using Enterprise) |
| **Lot/Serial Tracking** | ✅ Supported | ✅ NONE | 0 days (config only) |
| **Approval Workflow** | ⚠️ Basic approval (Studio), full via custom | 🟡 LOW GAP | 2-3 days (config Studio) |
| **Reorder Point & Auto-PO** | ✅ Supported | ✅ NONE | 0 days (config only) |
| **Work Order Tablet View** | ✅ Supported (Enterprise MRP Workorder) | ✅ NONE | 0 days (if using Enterprise) |
| **COGS & WIP Valuation** | ✅ Supported | ⚠️ MINOR GAP (2-stage Finishing custom valuation) | 3-5 days |

### Verdict: Can Odoo 18 Handle PT Quty Karunia Requirements?

**✅ YES**, but with **SIGNIFICANT CUSTOMIZATION** (3-5 months development)

**Pros of Odoo 18**:
- Solid foundation for MRP, Inventory, Purchasing
- Flexible architecture untuk customization (Python + XML)
- Large community & partner ecosystem
- Good performance with proper config
- Mobile-responsive UI out-of-the-box

**Cons/Challenges**:
- Dual Trigger system NOT standard (major customization)
- Dual-BOM NOT standard (major customization)
- Flexible Target per SPK NOT standard (major customization)
- Warehouse Finishing 2-stage special logic (medium customization)
- Cost: Enterprise edition + customization + implementation **~$150,000-200,000** total project

**Alternative Consideration**:
If budget is very tight, consider:
- **Option A**: Start with Odoo Community + Heavy Customization (save $60k/year license fee, but higher dev cost)
- **Option B**: Full Custom ERP (current prototype) + Polish & Deployment (total control, but higher long-term maintenance)

**Recommendation**: **Proceed with Odoo 18 Enterprise** if budget allows ($150k-200k project budget). Benefits of ecosystem, support, and scalability outweigh customization cost.

---

<a name="section-17"></a>
## 📅 IMPLEMENTATION ROADMAP

### Phase 0: Blueprint & Planning (4 weeks)

| Week | Activities | Deliverables | Responsible |
|------|------------|--------------|-------------|
| **Week 1-2** | - Gap Analysis Workshop<br>- Technical Deep Dive<br>- Odoo Partner Selection | - Gap Analysis Report<br>- Technical Specification<br>- Partner Selection | Quty IT Lead + Odoo Partner |
| **Week 3** | - Project Kickoff<br>- Team Formation<br>- Environment Setup | - Project Charter<br>- Team Roster<br>- Dev/UAT/Prod environments | Odoo Partner PM |
| **Week 4** | - Proof-of-Concept (Dual Trigger)<br>- Database Design Review<br>- Migration Strategy | - PoC Demo<br>- Database Schema Design<br>- Migration Plan | Odoo Developer + Quty IT |

### Phase 1: Foundation & Core Modules (8 weeks)

| Week | Module | Activities | Milestone |
|------|--------|------------|-----------|
| **Week 5-6** | Master Data & Base Config | - Odoo base installation<br>- User & role setup<br>- Warehouse locations config<br>- UOM setup | ✅ Odoo configured & accessible |
| **Week 7-8** | Product & BOM | - Import Products (Materials + Articles)<br>- Create BOM Production (manual)<br>- Develop Dual-BOM logic | ✅ BOM system ready |
| **Week 9-10** | Purchasing Module | - Configure PO workflow<br>- Develop Dual Trigger (Trigger 1: PO Fabric) | ✅ PO Fabric → MO PARTIAL working |
| **Week 11-12** | Manufacturing Module (Part 1) | - Develop Dual Trigger (Trigger 2: PO Label)<br>- Week/Destination auto-inheritance<br>- TEST: PO Label → MO RELEASED | ✅ Dual Trigger complete |

**Phase 1 Checkpoint**: Demo Dual Trigger System to stakeholders

### Phase 2: Production & Advanced Features (10 weeks)

| Week | Module | Activities | Milestone |
|------|--------|------------|-----------|
| **Week 13-15** | Manufacturing Module (Part 2) | - Develop Flexible Target System<br>- SPK auto-generation from MO<br>- TEST: MO → SPK split by dept | ✅ Flexible Target working |
| **Week 16-17** | Inventory & Stock Moves | - Configure internal transfer routes<br>- Develop UOM conversion validation<br>- TEST: Cutting YARD→PCS validation | ✅ UOM validation working |
| **Week 18-20** | Warehouse Finishing 2-Stage | - Develop Finishing Stage 1 (Stuffing)<br>- Develop Finishing Stage 2 (Closing)<br>- Internal conversion logic<br>- TEST: Material consumption tracking | ✅ Finishing 2-stage working |
| **Week 21-22** | Quality & Rework Module | - Develop Rework Request workflow<br>- QC approval integration<br>- COPQ calculation<br>- TEST: Defect → Rework → Recover | ✅ Rework module working |

**Phase 2 Checkpoint**: End-to-end production test (PO → MO → SPK → FG)

### Phase 3: Mobile, Reports, & Integrations (6 weeks)

| Week | Module | Activities | Milestone |
|------|--------|------------|-----------|
| **Week 23-25** | Mobile Applications | - Develop Custom Android App (Warehouse)<br>- Develop Custom Android App (Production Operator)<br>- Odoo API integration<br>- TEST: Barcode scanning working | ✅ Mobile apps ready |
| **Week 26-27** | Reports & Dashboard | - Develop Custom Reports (10+ reports)<br>- Develop Real-Time Dashboards (PPIC, Manager)<br>- TEST: All reports generating correctly | ✅ Reporting complete |
| **Week 28** | Material Debt & Approval | - Develop Material Debt module<br>- Approval workflow integration<br>- TEST: Negative stock with approval | ✅ Material Debt working |

**Phase 3 Checkpoint**: Full system demo with mobile app

### Phase 4: Data Migration & Testing (6 weeks)

| Week | Activities | Deliverables | Milestone |
|------|------------|--------------|-----------|
| **Week 29-30** | Data Migration (Master Data) | - Migrate Products, BOM, Suppliers<br>- Migrate Users & Roles<br>- Verify data integrity | ✅ Master data migrated |
| **Week 31** | Data Migration (Transactional) | - Migrate Open PO, Open MO<br>- Stock on hand adjustment<br>- WIP stock setup | ✅ Transactional data migrated |
| **Week 32-33** | Integration Testing | - End-to-end testing (all modules)<br>- Performance testing (1000+ BOM lines)<br>- Security testing (RBAC) | ✅ System tested & stable |
| **Week 34** | User Acceptance Testing (UAT) | - Department-by-department UAT<br>- Bug fixing<br>- UAT Sign-off | ✅ UAT approved |

### Phase 5: Training & Go-Live (4 weeks)

| Week | Activities | Deliverables | Milestone |
|------|------------|--------------|-----------|
| **Week 35-36** | User Training | - PPIC training (2 days)<br>- Purchasing training (1 day)<br>- Production SPV training (2 days)<br>- Warehouse training (2 days)<br>- Management training (0.5 day) | ✅ All users trained |
| **Week 37** | Parallel Run | - Run old system + new system simultaneously<br>- Data reconciliation daily<br>- Issue escalation & resolution | ✅ Parallel run successful |
| **Week 38** | Go-Live & Cutover | - Final data cutover<br>- Switch to Odoo (production)<br>- 24/7 support standby<br>- Hypercare for 2 weeks | ✅ GO-LIVE! |

### Phase 6: Hypercare & Stabilization (4 weeks post go-live)

| Week | Activities | Support Level |
|------|------------|---------------|
| **Week 39-40** | Hypercare | - 24/7 support standby<br>- Immediate bug fixing<br>- Daily check-in with users | 🔴 CRITICAL support |
| **Week 41-42** | Stabilization | - 12/7 support (office hours + on-call)<br>- Performance optimization<br>- Fine-tuning | 🟠 HIGH support |

**Post Go-Live**: 
- Months 3-6: Regular support (office hours)
- Months 7-12: Standard support (SLA-based)
- Year 2+: Maintenance & enhancements

---

### Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| **Phase 0** | 4 weeks | Blueprint & PoC |
| **Phase 1** | 8 weeks | Dual Trigger & Base Modules |
| **Phase 2** | 10 weeks | Advanced Production Features |
| **Phase 3** | 6 weeks | Mobile & Reporting |
| **Phase 4** | 6 weeks | Migration & Testing |
| **Phase 5** | 4 weeks | Training & Go-Live |
| **Phase 6** | 4 weeks | Hypercare (post go-live) |
| **TOTAL** | **38 weeks (~9 months)** | Fully operational Odoo ERP |

**Critical Path**: Dual Trigger (Week 9-12) → Flexible Target (Week 13-15) → Dual-BOM (Week 7-8 + ongoing)

---

<a name="section-18"></a>
## 🎯 SUCCESS METRICS & KPI

### Project Success Criteria

| Metric | Target | Measurement Method | Timeframe |
|--------|--------|-------------------|-----------|
| **On-Time Go-Live** | Week 38 (± 2 weeks) | Project milestone completion | End of project |
| **Budget Adherence** | ≤ 110% of approved budget | Actual cost vs budget | End of project |
| **User Adoption Rate** | ≥ 95% of users actively using system | Login frequency + transaction volume | 3 months post go-live |
| **Data Accuracy** | ≥ 98% match between old system & Odoo | Data reconciliation report | Cutover week |
| **System Uptime** | ≥ 99.5% (excluding planned maintenance) | Server monitoring logs | First 3 months post go-live |
| **Critical Bugs** (P1) | < 5 bugs in first month | Bug tracking system | First month post go-live |
| **User Satisfaction** | ≥ 4.0/5.0 average score | Survey (post-training & post-go-live) | 1 month & 3 months post go-live |

### Business KPI Improvement Targets

#### Operational KPI (Measured 6 months post go-live)

| KPI | Baseline (Before ERP) | Target (6 months after) | Improvement | Measurement |
|-----|----------------------|------------------------|-------------|-------------|
| **Lead Time** | 25 days | 18 days | -28% | Days from PO to shipment |
| **On-Time Delivery (OTD)** | 75% | ≥ 95% | +27% | % orders delivered on target week |
| **Inventory Accuracy** | 82% | ≥ 98% | +20% | Physical count vs system (cycle count) |
| **Fabric Yield** | 85% (15% waste) | 92% (8% waste) | +8% (+47% waste reduction) | Good output vs material consumed |
| **Material Shortage Frequency** | 8-12 times/month | < 3 times/month | -72% | Production stop incidents |
| **Manual Data Entry Time** | 15 hours/week | < 2 hours/week | -87% | Admin timesheet |
| **Reporting Time (Monthly Report)** | 3-5 days | < 1 hour | -98% | Time to generate monthly production report |

#### Financial KPI (Measured 12 months post go-live)

| KPI | Baseline (Before ERP) | Target (12 months after) | Improvement | Annual Savings |
|-----|----------------------|-------------------------|-------------|----------------|
| **Material Waste Loss** | $120,000/year | $72,000/year | -40% | **$48,000/year** |
| **Delay Penalty (IKEA)** | $80,000/year | $16,000/year | -80% | **$64,000/year** |
| **Inventory Discrepancy Loss** | $35,000/year | $8,000/year | -77% | **$27,000/year** |
| **COPQ (Cost of Poor Quality)** | $60,000/year | $20,000/year | -66% | **$40,000/year** |
| **Manual Work Opportunity Cost** | $45,000/year | $6,000/year | -87% | **$39,000/year** |
| **TOTAL ANNUAL SAVINGS** | - | - | - | **$218,000/year** |

#### ROI Calculation

| Item | Amount |
|------|--------|
| **Total Project Cost** | $180,000 (estimated) |
| **Annual Savings** | $218,000/year |
| **Payback Period** | 9.9 months (~10 months) |
| **3-Year ROI** | 263% (($218k × 3 - $180k) / $180k) |
| **5-Year ROI** | 506% (($218k × 5 - $180k) / $180k) |

**Verdict**: **HIGHLY POSITIVE ROI**. Project pays for itself in **< 1 year**, then generates $218k/year savings.

---

<a name="glossary"></a>
## 📚 GLOSSARY

### Manufacturing Terms

| Term | Full Name | Definition | Example |
|------|-----------|------------|---------|
| **BOM** | Bill of Materials | Daftar material untuk membuat 1 unit produk ("resep masakan" produksi) | 1 pcs AFTONSPARV butuh 0.1466 YARD kain KOHAIR + 54 gram filling + 2496 CM benang |
| **MO** | Manufacturing Order | Perintah produksi dari PPIC (auto-generate dari PO Purchasing). 1 MO bisa jadi 5-10 SPK untuk berbagai departemen. | MO-2026-00089 untuk 480 pcs AFTONSPARV |
| **SPK** | Surat Perintah Kerja | Task detail untuk 1 departemen (Cutting, Sewing, Finishing, dll). Equivalent to "Work Order" (WO) in Odoo. | SPK-CUT-2026-00120 untuk Cutting 480 pcs |
| **WO** | Work Order | Same as SPK. Term used in Odoo standard | WO-00156 Sewing Body |
| **WIP** | Work in Progress | Barang setengah jadi yang masih di produksi (belum packing) | Cutting result, Sewing result (Skin), Stuffed Body |
| **FG** | Finished Goods | Barang jadi siap kirim ke customer | AFTONSPARV Bear packed in carton |
| **PO** | Purchase Order | Pesanan pembelian dari Purchasing ke Supplier. Ada 3 jenis: PO Kain (Fabric), PO Label, PO Accessories | PO-FAB-2026-0456 untuk 125 YARD KOHAIR |
| **SO** | Sales Order | Pesanan dari customer (IKEA) | SO-2026-00089 untuk 450 pcs AFTONSPARV, Week W05, Belgium |
| **UOM** | Unit of Measure | Satuan ukuran material/produk | YARD (kain), GRAM (filling), CM (benang), PCS (produk), CTN (carton) |
| **PPIC** | Production Planning & Inventory Control | Departemen yang mengatur jadwal produksi & kontrol material | PPIC review MO, monitor SPK progress |
| **QC** | Quality Control | Inspeksi kualitas produk di setiap tahap produksi | QC checkpoint setelah Sewing, sebelum Finishing |
| **COPQ** | Cost of Poor Quality | Biaya yang dikeluarkan akibat produk defect (rework + scrap cost) | Rework cost $5,000 + Scrap cost $3,000 = COPQ $8,000 |
| **OTD** | On-Time Delivery | Persentase order yang dikirim tepat waktu sesuai target week | 95% OTD = 19 dari 20 orders delivered on time |

### Soft Toys Manufacturing Specific Terms

| Term | Definition | Example |
|------|------------|---------|
| **Skin** | Boneka yang sudah dijahit tapi belum diisi (no filling) | AFTONSPARV Skin (sewn, empty) |
| **Stuffed Body** | Boneka yang sudah diisi kapas/filling tapi belum ditutup | AFTONSPARV Stuffed (with filling, not closed yet) |
| **Finished Doll** | Boneka yang sudah closing (lengkap dengan hang tag) | AFTONSPARV Finished Doll (ready to pack) |
| **Baju** | Pakaian boneka (diproduksi terpisah dari body) | AFTONSPARV clothing (shirt + pants) |
| **Marker** | Ukuran pola kain untuk 1 unit produk (dalam YARD atau METER) | Marker 0.1466 YARD = fabric needed for 1 pcs AFTONSPARV body |
| **Filling** | Material pengisi boneka (dacron, polyester fiber, kapas) | 54 gram Dacron filling per 1 pcs AFTONSPARV |
| **Hang Tag** | Label gantung berisi brand info (IKEA) | Hang Tag with IKEA logo, article code, safety info |
| **EU Label** | Label kain yang dijahit di boneka berisi Week & Destination | EU Label: W05-2026, Belgium, Made in Indonesia |
| **Carton** | Kotak karton untuk packing Finished Goods | Carton 570x375mm, capacity 60 pcs AFTONSPARV |

### Odoo Specific Terms

| Term | Definition | Odoo Module |
|------|------------|-------------|
| **Reorder Point** | Batas minimum stok yang trigger auto-PO | `stock` - Inventory |
| **Push Rule** | Aturan otomatis untuk move stock dari location A ke B | `stock` - Routes |
| **Pull Rule** | Aturan otomatis untuk request stock dari location (on-demand) | `stock` - Routes |
| **BoM Explosion** | Proses breakdown BOM parent menjadi semua material & sub-assembly | `mrp` - Manufacturing |
| **Routing** | Urutan proses produksi (sequence of work centers) | `mrp` - Manufacturing |
| **Work Center** | Lokasi/mesin dimana proses produksi dilakukan (Cutting, Sewing, dll) | `mrp` - Manufacturing |
| **Smart Button** | Button di form Odoo yang membuka related records (e.g., "10 Work Orders" button in MO form) | Core Odoo UI |
| **Kanban View** | Tampilan card-based untuk visual tracking (e.g., SPK by status: To Do / In Progress / Done) | Core Odoo UI |
| **Odoo Studio** | Drag-and-drop builder untuk custom forms, reports, automations (Enterprise only) | `web_studio` (Enterprise) |
| **OCA** | Odoo Community Association - Komunitas yang develop free Odoo modules | - |

---

<a name="references"></a>
## 📚 REFERENCES

### Internal Documents (PT Quty Karunia)

1. **PRESENTASI_MANAGEMENT_ERP_QUTY_KARUNIA.md** - Overview sistem untuk Management (Bahasa Indonesia)
2. **TECHNICAL_SPECIFICATION.md** - Spesifikasi teknis lengkap dengan code examples (Python, TypeScript, Kotlin, SQL)
3. **ANALYSIS_BOM_MO_SPK_FLOW.md** - Deep analysis alur BOM → MO → SPK
4. **ILUSTRASI_WORKFLOW_LENGKAP.md** - End-to-end process flow dari Purchasing sampai Finished Goods
5. **ODOO_IMPLEMENTATION_BLUEPRINT.md** - Blueprint implementasi Odoo (draft awal)
6. **DUAL_BOM_SYSTEM_IMPLEMENTATION.md** - Design document untuk Dual-BOM feature
7. **PHASE2A_FINISHING_2STAGE_IMPLEMENTATION_GUIDE.md** - Design document untuk Warehouse Finishing 2-Stage
8. **PHASE2B_REWORK_QC_IMPLEMENTATION_GUIDE.md** - Design document untuk Rework/QC Module

### Odoo Official Documentation

- [Odoo 18 Official Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo Manufacturing Module Documentation](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/manufacturing.html)
- [Odoo Inventory Module Documentation](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory.html)
- [Odoo Purchase Module Documentation](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/purchase.html)
- [Odoo Quality Module Documentation](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/quality.html)
- [Odoo Developer Documentation](https://www.odoo.com/documentation/18.0/developer.html)

### External References

- **IKEA Quality Requirements for Suppliers** (Internal document - confidential)
- **Soft Toys Manufacturing Best Practices** (Industry knowledge - informal)

---

<a name="contact"></a>
## 📞 CONTACT INFORMATION

### Project Stakeholders

| Role | Name | Email | Phone | Availability |
|------|------|-------|-------|--------------|
| **IT Lead (Project Owner)** | Daniel Rizaldy S.W. | daniel.rizaldy@qutykarunia.com | +62-XXX-XXXX-XXXX | Mon-Sat, 8AM-6PM WIB |
| **Director** | [TBD] | director@qutykarunia.com | +62-XXX-XXXX-XXXX | By appointment |
| **Manager (Production)** | [TBD] | manager.prod@qutykarunia.com | +62-XXX-XXXX-XXXX | Mon-Sat, 8AM-5PM WIB |
| **PPIC Manager** | [TBD] | ppic@qutykarunia.com | +62-XXX-XXXX-XXXX | Mon-Sat, 8AM-5PM WIB |
| **Purchasing Manager** | [TBD] | purchasing@qutykarunia.com | +62-XXX-XXXX-XXXX | Mon-Fri, 8AM-5PM WIB |

### Company Information

**PT Quty Karunia**  
Address: [Company Address - TBD]  
Industry: Soft Toys Manufacturing (Discrete Manufacturing)  
Main Customer: IKEA (80% revenue)  
Production Capacity: 50,000 - 80,000 pcs/month  
Employees: ~111 users (operators + staff + management)  

---

## 🎁 DELIVERABLES EXPECTED FROM ODOO PARTNER (Before Contract)

Before moving forward with contract signing, PT Quty Karunia requires the following deliverables from Odoo Sales/Partner:

### 1. Gap Analysis Report (1-2 weeks)

**Content**:
- Review of this requirement document
- Line-by-line assessment: "Can Odoo handle this?" (YES / PARTIAL / NO)
- For "PARTIAL" and "NO": Proposed solution approach
- Estimated customization effort (man-days) per feature
- Risk assessment for each critical feature
- Alternative approaches (if standard Odoo solution not feasible)

**Format**: PDF report (20-30 pages)

### 2. Proof-of-Concept (PoC) for Critical Features (2-3 weeks)

**Scope**:
Develop mini PoC for **3 most critical features**:
1. **Dual Trigger Production System** (PO Fabric → MO PARTIAL → PO Label → MO RELEASED)
2. **Flexible Target System** (SPK Target ≠ MO Target with buffer)
3. **Dual-BOM System** (Production BOM + Purchasing BOM auto-sync)

**Deliverable**:
- Working Odoo 18 demo environment (dev server)
- Screen recording demo (15-20 minutes)
- Technical explanation document (how it's implemented)
- Code samples (if custom development)

### 3. Implementation Proposal (1 week)

**Content**:
- Detailed project plan (week-by-week breakdown)
- Resource allocation (# of developers, consultants, etc.)
- Cost breakdown (licensing, development, training, support)
- Timeline (realistic estimate with buffer)
- Assumptions & dependencies
- Payment terms & milestones
- Warranty & support terms (post go-live)

**Format**: Formal proposal document (PDF, 15-20 pages)

### 4. Technical Architecture Design (1 week)

**Content**:
- Odoo modules deployment diagram
- Custom modules architecture
- Database schema extensions
- Integration points (internal & potential external)
- Infrastructure recommendation (on-prem vs cloud)
- Performance optimization strategy
- Security & access control design
- Backup & disaster recovery plan

**Format**: Technical design document (PDF, 10-15 pages) + diagrams

### 5. Cost Quotation (Detailed Breakdown)

**Expected Format**:

| Item | Description | Unit | Qty | Unit Price | Total |
|------|-------------|------|-----|------------|-------|
| **Licensing** | Odoo 18 Enterprise (111 users, annual) | User/year | 111 | $XX | $XX,XXX |
| **Implementation** | Consulting, configuration, development | Man-day | XXX | $XXX | $XX,XXX |
| • Core Setup | User, warehouse, product setup | Man-day | XX | $XXX | $X,XXX |
| • Custom Development | Dual Trigger, Dual-BOM, etc. | Man-day | XXX | $XXX | $XX,XXX |
| • Mobile App Development | Custom Android app | Man-day | XX | $XXX | $X,XXX |
| • Data Migration | Script development & execution | Man-day | XX | $XXX | $X,XXX |
| • Testing & QA | Integration, UAT, performance testing | Man-day | XX | $XXX | $X,XXX |
| • Training | User training (all departments) | Man-day | XX | $XXX | $X,XXX |
| • Documentation | User manual, admin guide | Man-day | X | $XXX | $XXX |
| **Infrastructure** | Server, database, backup (if on-prem) | - | - | - | $X,XXX |
| **Support** | Post go-live support (3 months) | Month | 3 | $X,XXX | $X,XXX |
| **Contingency** | 10-15% for unforeseen issues | - | - | - | $X,XXX |
| **TOTAL PROJECT COST** | | | | | **$XXX,XXX** |

### 6. Reference Customers (Similar Projects)

**Request**:
- List of 2-3 customers with similar complexity projects (manufacturing with heavy customization)
- Contact information (for reference check)
- Project summary (industry, scope, timeline, outcome)

### Timeline for Deliverables

| Deliverable | Estimated Time | Responsible |
|-------------|----------------|-------------|
| Gap Analysis Report | 1-2 weeks | Odoo Partner (Functional Consultant) |
| PoC for Critical Features | 2-3 weeks | Odoo Partner (Developer) |
| Implementation Proposal | 1 week | Odoo Partner (Project Manager) |
| Technical Architecture | 1 week | Odoo Partner (Solution Architect) |
| Cost Quotation | 1 week | Odoo Partner (Sales) |
| Reference Customers | Immediate | Odoo Partner (Sales) |
| **TOTAL (Sequential)** | 6-8 weeks | |
| **TOTAL (Parallel Work)** | 3-4 weeks (realistic) | |

---

## 📊 DECISION CRITERIA (For Odoo Partner Selection)

PT Quty Karunia will evaluate Odoo Partners based on:

| Criteria | Weight | Evaluation Method |
|----------|--------|-------------------|
| **Technical Capability** | 30% | PoC demo quality, Architecture design |
| **Experience (Similar Projects)** | 25% | Reference customers, Case studies |
| **Cost Competitiveness** | 20% | Quotation vs market rate vs budget |
| **Project Management** | 15% | Proposal quality, Timeline realism, Risk mitigation plan |
| **Post-Implementation Support** | 10% | Support SLA, Response time, Warranty terms |

**Minimum Qualification**:
- PPoC must demonstrate at least **2 out of 3 critical features** successfully
- Total project cost must be within **±20% of internal budget estimate ($150k-220k)**
- Implementation timeline must be **≤ 10 months** (from kickoff to go-live)
- Must have at least **2 reference customers in manufacturing industry** with successful Odoo implementation

---

## 🚀 NEXT STEPS

### For Odoo Sales Indonesia:

1. **Review this document thoroughly** (est. 3-4 hours reading time)
2. **Schedule Deep Dive Session** with PT Quty Karunia IT Lead (4-6 hours meeting)
   - Topics: Clarify requirements, Discuss feasibility, Explore alternatives
3. **Assemble Technical Team** untuk Gap Analysis & PoC
   - Functional Consultant (1 person)
   - Solution Architect (1 person)
   - Senior Developer (1-2 persons for PoC)
4. **Prepare & Deliver Deliverables** (6-8 weeks as outlined above)
5. **Present Proposal** to PT Quty Karunia Management & Board
6. **Contract Negotiation** (if proposal accepted)
7. **Project Kickoff** (Week 1 of Phase 0)

### For PT Quty Karunia IT Team:

1. **Finalize Internal Budget** (confirm $150k-220k range)
2. **Prepare PoC Test Scenarios** untuk validate Odoo Partner's solution
3. **Coordinate with Department Heads** untuk UAT participation planning
4. **Backup Current System** (prepare for potential parallel run)
5. **Standby for Questions** dari Odoo Partner during Gap Analysis

---

## 🎯 FINAL NOTES

This document represents **9 months of analysis, prototyping, and business process deep dive** by PT Quty Karunia IT team. It contains:

- ✅ **Real production workflows** (not theoretical, but based on actual factory operations)
- ✅ **Proven business logic** (currently running in FastAPI/React prototype with 90% functionality complete)
- ✅ **Quantified pain points** with financial impact ($218k/year potential savings)
- ✅ **Realistic expectations** (we know Odoo cannot do everything out-of-the-box, heavy customization expected)
- ✅ **Technical depth** (code samples, database schema, API examples included)

**What we expect from Odoo Partner**:

- **Honesty**: Tell us upfront if something is not feasible in Odoo (we'll find alternatives together)
- **Expertise**: Deep Odoo knowledge + manufacturing domain knowledge
- **Commitment**: This is a complex project, we need a partner who will stay with us long-term
- **Transparency**: Clear communication on cost, timeline, risks

**What Odoo Partner can expect from PT Quty Karunia**:

- **Prepared Client**: We've done our homework, requirements are clear & detailed
- **Realistic Budget**: $150k-220k project budget approved (pending final proposal)
- **Decision-Making Authority**: IT Lead has mandate to make technical decisions, Management trusts our recommendation
- **Long-Term Partnership**: This is not a one-time project. We plan to use Odoo for 5+ years with continuous enhancements.

**Looking forward to your proposal!**

---

**Document Version**: 1.0  
**Last Updated**: 13 Februari 2026  
**Total Pages**: 60+ pages  
**Word Count**: ~25,000 words  

**Prepared by**:  
Daniel Rizaldy S.W.  
IT Lead - PT Quty Karunia  
Email: daniel.rizaldy@qutykarunia.com  

---

*End of Requirement Document Part 2*

