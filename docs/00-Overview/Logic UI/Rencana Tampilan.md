🏭 RENCANA TAMPILAN SISTEM ERP QUTY KARUNIA
============================================

Dokumen ini menjelaskan secara detail tampilan, navigasi, dan fitur-fitur UI/UX untuk Sistem ERP Manufaktur Soft Toys PT Quty Karunia.

**Versi**: 4.2  
**Tanggal Update**: 5 Februari 2026  
**Status**: Production Ready - Complete with Visual Diagrams  
**Update Notes**: Added comprehensive workflow visualizations:
- Three Purchasing Specialists diagram dengan detail PO tracking
- PPIC complete workflow (MO auto-generation from PO, WO/SPK review & explosion, BOM calculation)
- **TERMINOLOGY**: WO (Work Order) = SPK (Surat Perintah Kerja) - used interchangeably
- Production Flow 6-Stages end-to-end dengan Real-Time WIP Dashboard
- Warehouse 3-Types structure dengan 2-Stage Finishing detail
- QC 4-Checkpoint visualization dengan Rework Module workflow
- Material Flow Tracking dan Timeline/Gantt Chart lengkap

---

## DAFTAR ISI
1. [Dashboard Utama](#dashboard-utama)
2. [Menu Navigasi](#menu-navigasi)
3. [Purchasing Module](#purchasing-module)
4. [PPIC Module](#ppic-module)
5. [Production Module](#production-module)
6. [Warehouse & Inventory](#warehouse-inventory)
7. [Rework & Quality Control](#rework-qc)
8. [Masterdata](#masterdata)
9. [Reporting](#reporting)
10. [User Management](#user-management)
11. [Mobile Application](#mobile-app)
12. [Notification System](#notification)
13. [Material Flow Tracking](#material-flow-tracking)
14. [Timeline & Gantt Chart](#timeline-gantt)
15. [Barcode & Label System](#barcode-label)
16. [Security & Fraud Prevention](#security)

---

<a name="dashboard-utama"></a>
## 1. DASHBOARD UTAMA

### 1.0 Login Screen - Entry Point

#### 🔐 Login Page Design

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│              🏭 ERP QUTY KARUNIA                            │
│         Manufacturing Management System                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │  👤 Username / Email                                │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ [Input text]                                  │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  🔒 Password                                        │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ [Input password] 👁️                          │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  ☐ Remember me for 30 days                         │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         [LOGIN] 🚀                           │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  Forgot password? | Need help?                     │    │
│  │                                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  📱 Mobile App Available: Android | iOS                    │
│  🌐 Language: 🇮🇩 Indonesia | 🇬🇧 English                   │
│                                                              │
│  © 2026 PT Quty Karunia. All rights reserved.              │
│  Version 4.2 | Status: ✅ All Systems Operational          │
└─────────────────────────────────────────────────────────────┘
```

**Features**:
- ✅ Responsive design (Desktop, Tablet, Mobile)
- ✅ Password visibility toggle
- ✅ Remember me functionality
- ✅ Multi-language support
- ✅ SSO integration ready
- ✅ Biometric login (Mobile app)

**Security**:
- 🔒 SSL/TLS encryption
- 🔒 2FA optional untuk Superadmin
- 🔒 IP whitelist untuk production access
- 🔒 Session timeout: 30 minutes idle
- 🔒 Auto-logout pada browser close

---

### 1.1 Dashboard Overview
Dashboard utama menampilkan **real-time monitoring** dari seluruh operasional pabrik:

#### A. KPI Cards (Top Row)
```
┌────────────────────────────────────────────────────────────┐
│  📊 DASHBOARD PPIC - PT QUTY KARUNIA                       │
├────────────────────────────────────────────────────────────┤
│  [Total SPK Aktif]  [Material Critical]  [MO Terlambat]   │
│      15 SPK              3 Items           2 Orders        │
│  ────────────────────────────────────────────────────────  │
│  [Produksi Hari Ini]  [QC Pending]  [FG Ready Ship]       │
│      1,250 pcs           45 pcs         8 Cartons          │
└────────────────────────────────────────────────────────────┘
```

#### B. Production Progress Chart
- **Bar Chart**: Perbandingan target vs actual per departemen (harian)
- **Line Chart**: Trend produksi 7 hari terakhir
- **Pie Chart**: Distribution produksi per artikel

#### C. Material Stock Alert
Real-time monitoring material dengan **color coding**:
- 🟢 **Green** (>50% dari minimum stock): Stock aman
- 🟡 **Yellow** (15-50% dari minimum): Warning - perlu reorder
- 🔴 **Red** (<15% dari minimum): Critical - urgent action
- ⚫ **Black** (Negative stock): Material Debt - produksi berjalan dengan hutang

**Contoh Display**:
```
📦 Material Stock Critical (Top 5):
┌──────────────────────────────────────────────┐
│ [IKHR504] KOHAIR D.BROWN                     │
│ Stock: 125 YD | Min: 200 YD                  │
│ Status: 🟡 Low (62.5%) - Reorder 100 YD      │
├──────────────────────────────────────────────┤
│ [ACB30104] CARTON 570x375                    │
│ Stock: 18 PCE | Min: 50 PCE                  │
│ Status: 🔴 Critical! - Urgent Purchase        │
├──────────────────────────────────────────────┤
│ [IKP20157] Filling Dacron                   │
│ Stock: -12 KG | Min: 20 KG                   │
│ Status: ⚫ DEBT! - Production at risk         │
└──────────────────────────────────────────────┘
```

#### D. SPK Status Overview
```
📊 Total SPK Hari Ini: 15
   ✅ Selesai: 8 (53%)
   🔄 Proses: 5 (33%)
   ⚠️ Terlambat: 2 (13%)
   
⏱️ SPK Terlambat:
   • SEW-2026-00034 - AFTONSPARV (Delay: 2 hari)
   • FIN-2026-00012 - KRAMIG (Delay: 1 hari)
```

#### E. Quick Actions (Floating Buttons)
- ➕ **Create New SPK**
- 📥 **Material Receipt**
- 📤 **FG Shipment**
- 🔍 **Search SPK**

### 1.2 Dashboard by Role

#### PPIC Dashboard
- Focus: MO management, SPK tracking, material allocation
- Widget khusus: **MO Release Status** (PARTIAL vs RELEASED)
- Alert: Material shortage, Delayed SPK

#### Manager Dashboard
- Focus: High-level overview, performance metrics
- Widget khusus: **Production Efficiency**, **OEE**, **COPQ**
- Export: PDF reports untuk management meeting

#### Director Dashboard
- Focus: Strategic metrics, cost analysis
- Widget khusus: **Revenue per artikel**, **Material debt cost**
- Comparison: Month-over-month performance

#### Warehouse Dashboard
- Focus: Stock levels, material in/out, FG ready
- Widget khusus: **Stock movement heatmap**
- Alert: Low stock, Expired materials

---

<a name="menu-navigasi"></a>
## 2. MENU NAVIGASI

### Struktur Menu (Sidebar Navigation)

```
📱 ERP QUTY KARUNIA
├─ 🏠 Dashboard
│  ├─ Dashboard PPIC
│  ├─ Dashboard Manager
│  ├─ Dashboard Director
│  └─ Dashboard Warehouse
│
├─ 🏭 Operation
│  ├─ PPIC
│  │  ├─ Manufacturing Order (MO)
│  │  │  ├─ List MO (Auto-generated from PO)
│  │  │  ├─ Review MO (Edit/Accept/Reject)
│  │  │  ├─ Release MO (PARTIAL → RELEASED)
│  │  │  └─ Track MO Status
│  │  ├─ WO/SPK Management (Work Order = Surat Perintah Kerja)
│  │  │  ├─ Generate WO/SPK (Auto-explode from MO)
│  │  │  ├─ Flexible Target Setup per Department
│  │  │  ├─ Multi-WO/SPK per MO (parallel streams)
│  │  │  └─ WO/SPK Timeline View
│  │  └─ Material Allocation
│  │     ├─ BOM Explosion
│  │     ├─ Material Reservation
│  │     └─ Debt Material Tracking
│  │
│  ├─ Production
│  │  ├─ Cutting
│  │  │  ├─ List WO/SPK (Work Orders)
│  │  │  │  ├─ Daily Progress (Calendar View)
│  │  │  │  ├─ Cumulative Tracking
│  │  │  │  └─ Material Consumption
│  │  │  ├─ Input Hasil Produksi
│  │  │  │  ├─ Date Selection
│  │  │  │  ├─ Actual Output (pcs)
│  │  │  │  ├─ Good Output vs Defect
│  │  │  │  └─ UOM Conversion (YARD → PCS)
│  │  │  └─ Daily Report
│  │  │     ├─ Performance Report
│  │  │     ├─ Efficiency Tracking
│  │  │     └─ Yield Analysis
│  │  │
│  │  ├─ Embroidery
│  │  │  ├─ Subcontract Management
│  │  │  │  ├─ Send to Subcon
│  │  │  │  ├─ Receive from Subcon
│  │  │  │  └─ Subcon Performance
│  │  │  ├─ List SPK
│  │  │  │  ├─ Daily Progress
│  │  │  │  └─ Cumulative Tracking
│  │  │  ├─ Input Hasil Produksi
│  │  │  └─ Daily Report
│  │  │
│  │  ├─ Sewing
│  │  │  ├─ List WO/SPK (Body & Baju Parallel)
│  │  │  │  ├─ Daily Progress per Stream
│  │  │  │  ├─ Target vs Actual
│  │  │  │  └─ Constraint Validation
│  │  │  ├─ Input Hasil Produksi
│  │  │  │  ├─ Good Output
│  │  │  │  ├─ Defect → Send to Rework
│  │  │  │  └─ Thread Consumption
│  │  │  └─ Daily Report
│  │  │     ├─ Operator Performance
│  │  │     ├─ Line Efficiency
│  │  │     └─ Quality Metrics
│  │  │
│  │  ├─ Finishing (🆕 2-Stage Process)
│  │  │  ├─ Warehouse Finishing Dashboard
│  │  │  │  ├─ Stock Skin (from Sewing)
│  │  │  │  ├─ Stock Stuffed Body (Stage 1 output)
│  │  │  │  └─ Finished Doll (Stage 2 output)
│  │  │  ├─ Stage 1 - Stuffing (Isi Kapas)
│  │  │  │  ├─ Input: Skin + Filling
│  │  │  │  ├─ Process: Stuffing + Close stitch
│  │  │  │  ├─ Output: Stuffed Body
│  │  │  │  ├─ Material Tracking (Filling gram/pcs)
│  │  │  │  └─ Yield Monitoring
│  │  │  ├─ Stage 2 - Closing (Final Touch)
│  │  │  │  ├─ Input: Stuffed Body
│  │  │  │  ├─ Process: Hang Tag attachment
│  │  │  │  ├─ Output: Finished Doll
│  │  │  │  └─ Final QC
│  │  │  └─ Daily Report (per Stage)
│  │  │
│  │  ├─ Packing
│  │  │  ├─ List WO/SPK (Urgency-Based Target)
│  │  │  │  ├─ Constraint Check (Doll + Baju)
│  │  │  │  ├─ Week/Destination Assignment
│  │  │  │  └─ Packing Plan
│  │  │  ├─ Input Hasil Produksi
│  │  │  │  ├─ Packed Sets (Doll + Baju)
│  │  │  │  ├─ Carton Packing
│  │  │  │  ├─ Barcode Generation
│  │  │  │  └─ Pallet Assignment
│  │  │  └─ FG Label Printing
│  │  │     ├─ Barcode Label
│  │  │     ├─ Carton Label
│  │  │     └─ Pallet Label
│  │  │
│  │  └─ Production Calendar
│  │     ├─ View by Department
│  │     ├─ View by Week
│  │     └─ View by Article
│  │
│  ├─ Rework Station (🆕 QC Integration)
│  │  ├─ Dashboard Rework
│  │  │  ├─ Total Defects (by dept)
│  │  │  ├─ In Rework Queue
│  │  │  ├─ Completed Rework
│  │  │  └─ Recovery Rate
│  │  ├─ List Rework Orders
│  │  │  ├─ Filter by Dept/Article
│  │  │  ├─ Priority (Urgent/Normal)
│  │  │  └─ Aging Analysis
│  │  ├─ Input Hasil Rework
│  │  │  ├─ Rework Process
│  │  │  ├─ Success vs Scrap
│  │  │  ├─ Root Cause Analysis
│  │  │  └─ Cost Tracking (COPQ)
│  │  └─ Rework Report
│  │     ├─ Recovery Analysis
│  │     ├─ Defect Pareto Chart
│  │     └─ Continuous Improvement
│  │
│  └─ Quality Control
│     ├─ QC Checkpoint
│     │  ├─ Receiving Inspection (Material)
│     │  ├─ In-Process QC (per Dept)
│     │  ├─ Final Inspection (FG)
│     │  └─ Subcon QC
│     ├─ Input Hasil QC
│     │  ├─ Pass/Fail Decision
│     │  ├─ Defect Classification
│     │  ├─ Send to Rework (if fixable)
│     │  └─ Scrap (if beyond repair)
│     └─ QC Report
│        ├─ Quality Dashboard
│        ├─ Defect Analysis
│        └─ Yield Report per Dept
│
├─ 💰 Purchasing
│  ├─ Purchase Order Management
│  │  ├─ PO Kain (Fabric Specialist)
│  │  │  ├─ Create PO Kain
│  │  │  │  ├─ 🔑 TRIGGER 1: Start Cutting/Embroidery
│  │  │  │  ├─ Auto Material List from BOM
│  │  │  │  ├─ Supplier Selection
│  │  │  │  └─ Delivery Schedule
│  │  │  ├─ PO Status (Draft/Sent/Partial/Complete)
│  │  │  └─ PO Tracking
│  │  │
│  │  ├─ PO Label (Label Specialist)
│  │  │  ├─ Create PO Label
│  │  │  │  ├─ 🔑 TRIGGER 2: Full Release MO
│  │  │  │  ├─ Week Assignment (inherited to MO)
│  │  │  │  ├─ Destination (inherited to MO)
│  │  │  │  └─ Label Types (Hang Tag, EU Label, etc)
│  │  │  ├─ Critical Fields (Auto-Inherit):
│  │  │  │  ├─ Week Number
│  │  │  │  ├─ Destination
│  │  │  │  └─ Delivery Date
│  │  │  └─ PO Tracking
│  │  │
│  │  ├─ PO Accessories (Accessories Specialist)
│  │  │  ├─ Create PO Aksesoris
│  │  │  │  ├─ Thread, Filling, Box, Pallet
│  │  │  │  ├─ Multi-supplier management
│  │  │  │  └─ Price comparison
│  │  │  └─ PO Tracking
│  │  │
│  │  └─ PO List & Search
│  │     ├─ Filter by Type (Kain/Label/Accessories)
│  │     ├─ Filter by Status
│  │     ├─ Filter by Supplier
│  │     └─ Search by Article/PO Number
│  │
│  ├─ Supplier Management
│  │  ├─ Supplier Database
│  │  ├─ Supplier Performance
│  │  ├─ Supplier Evaluation
│  │  └─ Supplier Contact
│  │
│  └─ Material Receipt
│     ├─ GRN (Good Receipt Note)
│     ├─ Quality Inspection
│     ├─ Put Away to Warehouse
│     └─ Update PO Status
│
├─ 📦 Inventory & Warehouse
│  ├─ Warehouse Main (Material)
│  │  ├─ Stock Material
│  │  │  ├─ Real-time Stock Level
│  │  │  ├─ Material Location
│  │  │  ├─ Material Aging
│  │  │  └─ Reorder Point Alert
│  │  ├─ Material In (GRN)
│  │  │  ├─ Receipt from Supplier
│  │  │  ├─ Quality Check
│  │  │  ├─ Barcode Scanning
│  │  │  └─ Bin Allocation
│  │  ├─ Material Out (Issue to Production)
│  │  │  ├─ SPK-based Issue
│  │  │  ├─ BOM Validation
│  │  │  ├─ Batch/Lot Tracking
│  │  │  └─ Negative Stock (Debt) Alert
│  │  └─ Stock Adjustment
│  │     ├─ Physical Count
│  │     ├─ Variance Analysis
│  │     └─ Approval Workflow
│  │
│  ├─ Warehouse Production (WIP)
│  │  ├─ Stock Cutting Output
│  │  ├─ Stock Embroidery Output
│  │  ├─ Stock Sewing Output (Body & Baju)
│  │  └─ Transfer between Dept
│  │
│  ├─ Warehouse Finishing (🆕 2-Stage)
│  │  ├─ Stock Skin (from Sewing)
│  │  │  ├─ SKU Management
│  │  │  ├─ Queue to Stage 1
│  │  │  └─ Aging Alert
│  │  ├─ Stock Stuffed Body (Stage 1 output)
│  │  │  ├─ SKU Management
│  │  │  ├─ Queue to Stage 2
│  │  │  └─ Quality Hold
│  │  ├─ Stock Finished Doll (Stage 2 output)
│  │  │  ├─ Ready for Packing
│  │  │  ├─ QC Passed
│  │  │  └─ Transfer to Packing
│  │  └─ Material Tracking
│  │     ├─ Filling Consumption per pcs
│  │     ├─ Thread Usage
│  │     └─ Yield per Stage
│  │
│  ├─ Warehouse Finished Goods
│  │  ├─ Stock Finished Goods
│  │  │  ├─ Real-time FG Level (qty from MO)
│  │  │  ├─ Auto-display: Cartons, Pcs, Boxes (UOM conversion)
│  │  │  ├─ By Article/Week/Destination
│  │  │  ├─ Carton Tracking
│  │  │  └─ Pallet Management
│  │  ├─ Finished Goods In
│  │  │  ├─ Receipt from Packing (qty sesuai MO)
│  │  │  ├─ Barcode Scanning (🆕 Mobile)
│  │  │  ├─ Auto-display: Pcs, Cartons, Boxes (multi-UOM)
│  │  │  ├─ Auto-validation (<10% variance vs MO target)
│  │  │  └─ Pallet Stacking
│  │  ├─ Finished Goods Out
│  │  │  ├─ Pick List by DO
│  │  │  ├─ FIFO/FEFO Logic
│  │  │  ├─ Loading List
│  │  │  └─ Shipment Confirmation
│  │  └─ FG Label System (🆕 Mobile Scanning)
│  │     ├─ Label Printing
│  │     ├─ Barcode Scanning
│  │     ├─ Verification System
│  │     └─ Shipment Tracking
│  │
│  └─ Stock Opname
│     ├─ Schedule SO (Monthly/Quarterly)
│     ├─ Cycle Count (Daily)
│     ├─ Physical Count Input
│     ├─ Variance Report
│     └─ Adjustment Approval
│
├─ 📊 Report & Analytics
│  ├─ Production Reports
│  │  ├─ Daily Production Report
│  │  │  ├─ Output per Department
│  │  │  ├─ Yield Analysis
│  │  │  └─ Efficiency Metrics
│  │  ├─ Weekly Production Summary
│  │  ├─ Monthly Production Analysis
│  │  ├─ SPK Completion Report
│  │  └─ OEE (Overall Equipment Effectiveness)
│  │
│  ├─ Purchasing Reports
│  │  ├─ PO Summary (by Type/Supplier)
│  │  ├─ Delivery Performance
│  │  ├─ Price Trend Analysis
│  │  └─ Vendor Performance Scorecard
│  │
│  ├─ Inventory Reports
│  │  ├─ Stock Movement Report
│  │  ├─ Material Consumption Analysis
│  │  ├─ Slow Moving/Dead Stock
│  │  ├─ Stock Aging Report
│  │  └─ ABC Analysis
│  │
│  ├─ 🆕 Material Debt Report
│  │  ├─ Current Debt Status
│  │  ├─ Debt by Material/Supplier
│  │  ├─ Production Risk Analysis
│  │  ├─ Debt Settlement Tracking
│  │  └─ Cost Impact (Interest/Rush Order)
│  │
│  ├─ 🆕 Rework & Quality Reports
│  │  ├─ Defect Analysis Report
│  │  │  ├─ By Department
│  │  │  ├─ By Article
│  │  │  ├─ By Defect Type
│  │  │  └─ Root Cause Pareto
│  │  ├─ Rework Performance
│  │  │  ├─ Recovery Rate
│  │  │  ├─ Rework Cost (COPQ)
│  │  │  └─ Process Time Analysis
│  │  ├─ Yield Report (per Department)
│  │  └─ First Pass Yield (FPY)
│  │
│  ├─ 🆕 Flexible Target Analysis
│  │  ├─ Target vs Actual Comparison
│  │  ├─ Buffer Utilization Report
│  │  ├─ Shortage Prevention Metrics
│  │  └─ Excess Stock Analysis
│  │
│  └─ Executive Dashboard
│     ├─ KPI Dashboard (Director)
│     ├─ Financial Summary
│     ├─ Cost Analysis (COGS)
│     └─ Export to Excel/PDF
│
├─ 🗂️ Masterdata
│  ├─ Material Master
│  │  ├─ Material List
│  │  │  ├─ Fabric (Kain)
│  │  │  ├─ Thread (Benang)
│  │  │  ├─ Filling (Isi)
│  │  │  ├─ Accessories (Label, Tag, Sticker)
│  │  │  ├─ Packaging (Carton, Pallet)
│  │  │  └─ WIP (intermediate products)
│  │  ├─ Material Details
│  │  │  ├─ Material Code (Auto-generate)
│  │  │  ├─ Material Name
│  │  │  ├─ Material Type
│  │  │  ├─ UOM (Primary & Secondary)
│  │  │  ├─ Minimum Stock
│  │  │  ├─ Lead Time
│  │  │  ├─ Standard Cost
│  │  │  └─ Material Image
│  │  └─ Import/Export Material
│  │
│  ├─ Supplier Master
│  │  ├─ Supplier List
│  │  ├─ Supplier Details
│  │  │  ├─ Supplier Code
│  │  │  ├─ Supplier Name
│  │  │  ├─ Supplier Type (Fabric/Label/Accessories)
│  │  │  ├─ Address & Contact
│  │  │  ├─ Payment Terms
│  │  │  ├─ Lead Time
│  │  │  └─ Performance Rating
│  │  └─ Supplier-Material Mapping
│  │
│  ├─ BOM Master (Bill of Materials)
│  │  ├─ 🆕 2 Jenis BOM:
│  │  │  ├─ BOM Manufacturing (for Production)
│  │  │  └─ BOM Purchasing (for Buying)
│  │  ├─ BOM Header
│  │  │  ├─ BOM Code (Auto-generate)
│  │  │  ├─ Article Reference
│  │  │  ├─ Department
│  │  │  ├─ BOM Type (Finished Goods/WIP)
│  │  │  ├─ Output Product
│  │  │  ├─ Output Qty & UOM
│  │  │  ├─ Subcontract (Yes/No)
│  │  │  ├─ Routing (Process Flow)
│  │  │  └─ Effective Date
│  │  ├─ BOM Lines (Material List)
│  │  │  ├─ Material Code & Name
│  │  │  ├─ Material Type
│  │  │  ├─ Qty per Unit
│  │  │  ├─ UOM
│  │  │  ├─ Scrap %
│  │  │  ├─ 🆕 UOM Conversion Factor
│  │  │  └─ Notes
│  │  ├─ 🆕 BOM Cascade Validation
│  │  │  ├─ Cutting → Embroidery chain
│  │  │  ├─ Embroidery → Sewing chain
│  │  │  ├─ Sewing → Finishing chain
│  │  │  └─ Finishing → Packing chain
│  │  └─ BOM Version Control
│  │
│  ├─ Article Master
│  │  ├─ Article List
│  │  ├─ Article Details
│  │  │  ├─ Article Code (IKEA/Internal)
│  │  │  ├─ Article Name
│  │  │  ├─ Description
│  │  │  ├─ Buyer
│  │  │  ├─ Category (Soft Toys type)
│  │  │  ├─ Standard Packing (pcs/carton)
│  │  │  ├─ 🆕 UOM Conversion (Box → Pcs)
│  │  │  ├─ Article Image
│  │  │  └─ Active Status
│  │  └─ Article-BOM Linking
│  │
│  ├─ Department Master
│  │  ├─ Department List
│  │  ├─ Department Details
│  │  │  ├─ Department Code
│  │  │  ├─ Department Name
│  │  │  ├─ Department Type
│  │  │  ├─ Cost Center
│  │  │  └─ Capacity (pcs/day)
│  │  └─ Department Routing
│  │
│  └─ Subcontractor Master
│     ├─ Subcon List
│     ├─ Subcon Details
│     │  ├─ Subcon Code
│     │  ├─ Subcon Name
│     │  ├─ Service Type (Embroidery/Sewing)
│     │  ├─ Contact & Address
│     │  ├─ Payment Terms
│     │  └─ Performance Rating
│     └─ Subcon-Process Mapping
│
├─ 👤 User Management & System
│  ├─ User Management
│  │  ├─ User List
│  │  ├─ Create/Edit User
│  │  │  ├─ Username & Password
│  │  │  ├─ Full Name
│  │  │  ├─ Email & Phone
│  │  │  ├─ Department Assignment
│  │  │  ├─ Role Assignment
│  │  │  └─ Active Status
│  │  └─ User Activity Log
│  │
│  ├─ Role & Permission
│  │  ├─ Predefined Roles:
│  │  │  ├─ Superadmin (full access)
│  │  │  ├─ Director (all read, approve MO)
│  │  │  ├─ Manager (dept read, dept approve)
│  │  │  ├─ PPIC (MO review/edit/approve, WO/SPK auto-explode)
│  │  │  ├─ Purchasing (PO create/edit)
│  │  │  ├─ Warehouse (stock manage, GRN, issue)
│  │  │  ├─ Admin Produksi (input production per dept)
│  │  │  ├─ QC (quality inspection)
│  │  │  ├─ Supervisor (approve SPK, view report)
│  │  │  ├─ Subcontractor (view assigned work only)
│  │  │  └─ Developer (FullAccess system config)
│  │  └─ Custom Permission Matrix
│  │
│  ├─ Approval Workflow
│  │  ├─ MO Approval
│  │  │  ├─ Draft (System auto-generate from PO)
│  │  │  ├─ Review (PPIC review & edit)
│  │  │  ├─ Approve (Manager approve)
│  │  │  └─ Released (Director final approve, trigger WO/SPK explosion)
│  │  ├─ PO Approval
│  │  │  ├─ Draft (Purchasing create)
│  │  │  ├─ Review (Purchasing Manager)
│  │  │  └─ Approve (Director for >$10K)
│  │  └─ Stock Adjustment Approval
│  │     ├─ Request (Warehouse)
│  │     ├─ Review (Warehouse Manager)
│  │     └─ Approve (Director)
│  │
│  ├─ Audit Trail
│  │  ├─ User Activity Log
│  │  ├─ Data Change History
│  │  ├─ Login/Logout History
│  │  └─ Critical Action Log
│  │
│  └─ System Configuration
│     ├─ Company Profile
│     ├─ System Parameters
│     ├─ Email/Notification Settings
│     ├─ Barcode Configuration
│     ├─ Report Templates
│     └─ Database Backup/Restore
│
└─ 🔔 Notification Center
   ├─ Real-time Alerts
   │  ├─ Material Low Stock
   │  ├─ SPK Delay Warning
   │  ├─ PO Delivery Reminder
   │  └─ Quality Alert (high defect rate)
   ├─ Approval Pending
   │  ├─ MO Awaiting Approval
   │  ├─ PO Awaiting Approval
   │  └─ Stock Adjustment Pending
   ├─ Task Assignment
   │  ├─ New SPK Assigned
   │  ├─ Rework Task
   │  └─ QC Inspection Due
   └─ System Notifications
      ├─ Backup Success/Fail
      ├─ User Login Alert
      └─ System Maintenance Schedule
```
---

<a name="purchasing-module"></a>
## 3. PURCHASING MODULE

### 3.1 Purchasing Department Structure & Workflow

#### 🏢 Three Purchasing Specialists - Parallel Workflow

PT Quty Karunia memiliki **3 Purchasing Specialist** yang bekerja secara **parallel** dengan spesialisasi berbeda:

- **PURCHASING A** - Fabric Specialist (🔑 TRIGGER 1) - **MASTER PO REFERENCE**
- **PURCHASING B** - Label Specialist (🔑 TRIGGER 2) - **MUST REFERENCE PO-FAB**
- **PURCHASING C** - Accessories Specialist - **MUST REFERENCE PO-FAB**

#### 🔗 PO Reference Chain (Parent-Child Relationship)

**CRITICAL RULE**: Purchasing B dan C **WAJIB mencantumkan NO PO Purchasing A** sebagai reference untuk:
- ✅ **Traceability**: Mudah tracking semua material terkait 1 artikel
- ✅ **BOM Compliance**: Memastikan material sesuai dengan BOM yang sama
- ✅ **Audit Trail**: Full 5W1H tracking dari fabric ke finished goods
- ✅ **Cost Allocation**: Akumulasi cost per artikel lebih akurat

**Contoh PO Reference**:
```
PO-FAB-2026-0456 (MASTER - Purchasing A)
   ├─ PO-LBL-2026-0789 (Ref: PO-FAB-2026-0456)
   └─ PO-ACC-2026-0890 (Ref: PO-FAB-2026-0456)
```

**Implementation di Form PO**:
- Field "Reference PO" (mandatory untuk PO Label & Accessories)
- Dropdown otomatis filter PO Fabric yang aktif
- Validation: Tidak bisa submit PO-LBL/PO-ACC tanpa Reference PO-FAB
- Auto-inherit: Article Code, BOM Version dari PO Master

**Workflow Visualization** (Complete Process Flow):

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PURCHASING DEPARTMENT - 3 PARALLEL STREAMS                             │
└─────────────────────────────────────────────────────────────────────────┘

CUSTOMER ORDER: 450 pcs AFTONSPARV for Week 05
    │
    ├─────────────────────────────────────────────────────────────────────┐
    │                                                                      │
    ▼                            ▼                         ▼              │
┌──────────────┐        ┌──────────────┐        ┌──────────────┐        │
│ PURCHASING A │        │ PURCHASING B │        │ PURCHASING C │        │
│   (FABRIC)   │        │   (LABEL)    │        │ (ACCESSORIES)│        │
└──────────────┘        └──────────────┘        └──────────────┘        │
        │                       │                       │                │
        ▼                       ▼                       ▼                │
┌──────────────┐        ┌──────────────┐        ┌──────────────┐        │
│ PO-FAB-2026  │        │ PO-LBL-2026  │        │ PO-ACC-2026  │        │
│   -0456      │        │   -0789      │        │   -0890      │        │
│              │        │              │        │              │        │
│ • KOHAIR     │        │ • Hang Tag   │        │ • Thread     │        │
│   70.4 YD    │        │   450 pcs    │        │   2500 CM    │        │
│ • JS BOA     │        │ • Label EU   │        │ • Filling    │        │
│   4.7 YD     │        │   450 pcs    │        │   24.3 kg    │        │
│ • NYLEX      │        │ • Sticker    │        │ • Carton     │        │
│   2.5 YD     │        │   900 pcs    │        │   8 pcs      │        │
│ • Polyester  │        │              │        │              │        │
│   85.3 YD    │        │              │        │              │        │
│              │        │              │        │              │        │
│ Lead Time:   │        │ Lead Time:   │        │ Lead Time:   │        │
│ 3-5 days     │        │ 7-10 days ⚠️ │        │ 2-3 days     │        │
│              │        │              │        │              │        │
│ Status: ✅   │        │ Status: ⏳   │        │ Status: ✅   │        │
│ Received     │        │ Waiting      │        │ Received     │        │
└──────────────┘        └──────────────┘        └──────────────┘        │
        │                       │                       │                │
        │                       │                       │                │
        ▼                       ▼                       ▼                │
┌─────────────────────────────────────────────────────────────────────┐  │
│  WAREHOUSE MAIN - MATERIAL RECEIVING                                │  │
│                                                                     │  │
│  ✅ Fabric Stock:                                                   │  │
│     ├─ [IKHR504] KOHAIR: 125 YD (⚠️ Low stock)                     │  │
│     ├─ [IJBR105] JS BOA: 15 YD (✅ OK)                             │  │
│     └─ [IPR301] POLYESTER: 450 YD (✅ OK)                          │  │
│                                                                     │  │
│  ⏳ Label Stock:                                                    │  │
│     └─ [ALB40011] Hang Tag: 0 pcs (🔴 OUT OF STOCK)               │  │
│                                                                     │  │
│  ✅ Accessories Stock:                                              │  │
│     ├─ [IKP20157] Filling: 45 kg (✅ OK)                           │  │
│     ├─ Thread assorted: 5,000 CM (✅ OK)                           │  │
│     └─ [ACB30104] Carton: 18 pcs (⚠️ Low stock)                    │  │
└─────────────────────────────────────────────────────────────────────┘  │
                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 🔑 Dual Trigger System Visualization

```
🔑 TRIGGER 1: PO KAIN RECEIVED ✅
    │
    ├─→ System Action:
    │   ├─ Material Kain available di Warehouse Main
    │   ├─ Notify PPIC: "Fabric ready for cutting"
    │   └─ MO Status: Can upgrade to PARTIAL
    │
    └─→ PPIC Decision:
        ├─ Create MO with MODE: PARTIAL
        ├─ Cutting & Embroidery dapat start
        └─ Sewing, Finishing, Packing: BLOCKED (tunggu PO Label)

⏳ TRIGGER 2: PO LABEL RECEIVED (3-7 days later)
    │
    ├─→ System Action:
    │   ├─ Label available di Warehouse Main
    │   ├─ Auto-inherit: Week & Destination dari PO Label
    │   └─ MO Status: Auto-upgrade to RELEASED
    │
    └─→ Production Impact:
        ├─ Sewing dapat start (batch dari Embroidery sudah ready)
        ├─ Finishing dapat start
        ├─ Packing dapat start
        └─ 🎯 FULL PRODUCTION MODE ACTIVE

⚡ BENEFIT: Lead Time Reduction -3 to -5 days
```

### 3.2 🔥 DUAL-MODE SYSTEM - Purchase Order (PO)

Purchasing memiliki **2 mode input** untuk membuat PO dengan fleksibilitas maksimal:

#### 🆕 MODE 1: AUTO TRIGGER FROM ARTICLE (🤖 BOM Explosion)

**Konsep**: Purchasing pilih Article → Sistem otomatis generate material list dari BOM.

**UI Flow**:

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE PURCHASE ORDER - AUTO MODE                          │
├─────────────────────────────────────────────────────────────┤
│  📋 HEADER INFORMATION                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • No PO IKEA (ECIS): [          ] (Optional)         │  │
│  │ • No PO Purchasing: [AUTO-GENERATE]                  │  │
│  │ • PO Type: [Dropdown: KAIN/LABEL/ACCESSORIES]        │  │
│  │ • Tanggal PO: [Date Picker]                          │  │
│  │ • Expected Delivery: [Date Picker]                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  🤖 INPUT MODE SELECTION                                    │
│  ┌───────────────────┬──────────────────────────────────┐  │
│  │ 🤖 AUTO from      │  ✍️ MANUAL INPUT                 │  │
│  │    ARTICLE        │                                   │  │
│  │                   │  Tambah material satu per satu   │  │
│  │ [SELECTED]        │  [Click to switch]               │  │
│  └───────────────────┴──────────────────────────────────┘  │
│                                                              │
│  📦 ARTICLE SELECTION (BOM Explosion Trigger)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • No/Kode Article: [Dropdown: Select Article]        │  │
│  │   Options: 40551542, 40499469, 50551703...           │  │
│  │                                                        │  │
│  │ • Nama Article: [Auto-filled from selection]          │  │
│  │   Display: AFTONSPARV soft toy w astronaut suit...   │  │
│  │                                                        │  │
│  │ • Qty Article (pcs): [Input Number, min: 1]           │  │
│  │   Example: 1000 pcs                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ⏳ BOM Explosion Status:                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ✅ BOM Explosion berhasil! 32 materials generated     │  │
│  │ Silakan cek dan update harga/supplier per material.   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  📋 MATERIAL LIST (Auto-Generated from BOM)                 │
│                                                              │
│  ╔════════════════════════════════════════════════════════╗ │
│  ║ MATERIAL #1 (🤖 Auto-generated from BOM)              ║ │
│  ╠════════════════════════════════════════════════════════╣ │
│  ║ • Material Name: [IKHR504] KOHAIR 7MM D.BROWN         ║ │
│  ║   [Read-only - from BOM]                              ║ │
│  ║                                                         ║ │
│  ║ • Material Type: RAW [Read-only]                       ║ │
│  ║ • Material Code: IKHR504 [Auto from BOM]              ║ │
│  ║                                                         ║ │
│  ║ • 🏭 Supplier (per material): [Dropdown] *REQUIRED    ║ │
│  ║   Options: PT Supplier A, CV Supplier B...            ║ │
│  ║   ℹ️ Setiap material bisa dari supplier berbeda       ║ │
│  ║                                                         ║ │
│  ║ • Description: [Optional text]                         ║ │
│  ║                                                         ║ │
│  ║ • Quantity: 146.6 [From BOM calc, editable]           ║ │
│  ║ • Unit: YARD [From BOM]                               ║ │
│  ║ • Unit Price: [Input Number] *REQUIRED                ║ │
│  ║ • Total Price: [Auto-calculate: Qty × Unit Price]     ║ │
│  ╚════════════════════════════════════════════════════════╝ │
│                                                              │
│  ╔════════════════════════════════════════════════════════╗ │
│  ║ MATERIAL #2 (🤖 Auto-generated from BOM)              ║ │
│  ╠════════════════════════════════════════════════════════╣ │
│  ║ • Material Name: [IKP20157] RECYCLE HCS Filling       ║ │
│  ║ • Material Type: RAW                                   ║ │
│  ║ • Material Code: IKP20157                             ║ │
│  ║ • 🏭 Supplier: [Dropdown] *REQUIRED                   ║ │
│  ║ • Quantity: 54.0 KG                                   ║ │
│  ║ • Unit Price: [Input]                                 ║ │
│  ║ • Total Price: [Auto-calc]                            ║ │
│  ╚════════════════════════════════════════════════════════╝ │
│                                                              │
│  ... (30 more materials auto-generated)                     │
│                                                              │
│  ⚠️ NOTE:                                                   │
│  - Material names & codes CANNOT be edited (from BOM)       │
│  - You MUST fill: Supplier & Unit Price for each material  │
│  - Quantities are calculated from BOM × Article Qty         │
│  - Each material can have DIFFERENT supplier                │
│                                                              │
│  💰 TOTAL PO VALUE: Rp [Auto-sum all materials]             │
│                                                              │
│  [SAVE DRAFT]  [SUBMIT PO] ←── Validate supplier+price     │
└─────────────────────────────────────────────────────────────┘
```

**Key Features MODE 1**:
1. **BOM Explosion**: Pilih article → 30+ materials auto-populated
2. **Supplier per Material**: Setiap material bisa dari supplier berbeda (FLEXIBILITY!)
3. **Auto-calculation**: Quantity dihitung otomatis (Article Qty × BOM ratio)
4. **Read-only Material Info**: Material name/code tidak bisa diubah (integrity)
5. **User Input Focus**: User hanya isi Supplier & Price (save time 80%!)
6. **Visual Badge**: Purple card dengan badge "🤖 Auto-generated from BOM"

**Validation Rules**:
- ✅ Article MUST be selected
- ✅ Article Quantity MUST > 0
- ✅ EVERY material MUST have Supplier selected
- ✅ EVERY material MUST have Unit Price > 0
- ✅ Material list cannot be empty

---

#### MODE 2: MANUAL INPUT (✍️ Traditional Entry)

**Konsep**: Purchasing tambah material satu per satu (untuk non-standard orders).

**UI Flow**:

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE PURCHASE ORDER - MANUAL MODE                        │
├─────────────────────────────────────────────────────────────┤
│  📋 HEADER INFORMATION (same as Mode 1)                     │
│                                                              │
│  ✍️ INPUT MODE SELECTION                                    │
│  ┌───────────────────┬──────────────────────────────────┐  │
│  │ 🤖 AUTO from      │  ✍️ MANUAL INPUT                 │  │
│  │    ARTICLE        │                                   │  │
│  │                   │  Tambah material satu per satu   │  │
│  │ [Click to switch] │  [SELECTED]                      │  │
│  └───────────────────┴──────────────────────────────────┘  │
│                                                              │
│  📋 MATERIAL LIST (Manual Entry)                            │
│                                                              │
│  ╔════════════════════════════════════════════════════════╗ │
│  ║ MATERIAL #1                                            ║ │
│  ╠════════════════════════════════════════════════════════╣ │
│  ║ 🔄 Input Mode: [🔽 BOM Dropdown | ✍️ Manual Input]     ║ │
│  ║                                                         ║ │
│  ║ IF Dropdown Mode:                                      ║ │
│  ║ • Material Name: [Dropdown from Masterdata BOM]        ║ │
│  ║   → Auto-fill: Type, Code, Unit from BOM              ║ │
│  ║                                                         ║ │
│  ║ IF Manual Mode:                                        ║ │
│  ║ • Material Name: [Free text input]                     ║ │
│  ║ • Material Type: [Dropdown: RAW/BAHAN PENOLONG/WIP]   ║ │
│  ║ • Material Code: [Manual input]                        ║ │
│  ║                                                         ║ │
│  ║ • 🏭 Supplier: [Dropdown] *REQUIRED                   ║ │
│  ║ • Description: [Optional]                              ║ │
│  ║ • Quantity: [Input Number]                            ║ │
│  ║ • Unit: [Dropdown: YD/KG/PCS/METER/CM/GRAM]           ║ │
│  ║ • Unit Price: [Input Number]                          ║ │
│  ║ • Total Price: [Auto-calculate]                        ║ │
│  ║                                                         ║ │
│  ║ [🗑️ Remove Material]                                  ║ │
│  ╚════════════════════════════════════════════════════════╝ │
│                                                              │
│  [➕ ADD MATERIAL] ←── Only in Manual Mode                  │
│                                                              │
│  💰 TOTAL PO VALUE: Rp [Auto-sum]                           │
│                                                              │
│  [SAVE DRAFT]  [SUBMIT PO]                                  │
└─────────────────────────────────────────────────────────────┘
```

**Key Features MODE 2**:
1. **Hybrid Input**: Per material bisa pilih BOM dropdown ATAU manual input
2. **Toggle Switch**: User dapat switch antara dropdown/manual per material
3. **Full Flexibility**: User kontrol penuh atas nama, code, type, qty
4. **Add/Remove**: User dapat tambah/hapus material sesuka hati
5. **Same Supplier Logic**: Supplier per material (consistency with Mode 1)
6. **Visual Difference**: Blue card (vs purple for auto-generated)

**Use Cases Manual Mode**:
- One-off purchases (special orders)
- BOM tidak tersedia untuk article
- Mixed materials (some from BOM, some custom)
- Quick purchase tanpa MO

---

### 3.2 PO Display & Management

#### PO List View (Table)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PURCHASE ORDERS - FILTER: [All Types ▾] [All Status ▾] [Search...]   │
├─────────────────────────────────────────────────────────────────────────┤
│ PO Number  │ Type  │ Article │ Supplier │ Status │ Total │ Date    │ ⚙️│
├────────────┼───────┼─────────┼──────────┼────────┼───────┼─────────┼───┤
│ PO-K-2026  │ KAIN  │ 40551542│ Multiple │ DRAFT  │ 45M   │ 3/2/26  │ ⋮ │
│ -00012     │       │ AFTONSPA│ (15 sups)│        │       │         │   │
│ [AUTO]     │       │         │          │        │       │         │   │
├────────────┼───────┼─────────┼──────────┼────────┼───────┼─────────┼───┤
│ PO-L-2026  │ LABEL │ Manual  │ PT Label │RECEIVED│ 12M   │ 1/2/26  │ ⋮ │
│ -00089     │       │ Entry   │ Indo     │        │       │         │   │
│ [MANUAL]   │       │         │          │        │       │         │   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Badge System**:
- 🤖 **[AUTO]**: PO created with Article BOM explosion
- ✍️ **[MANUAL]**: PO created with manual entry
- 🟢 **Multiple Suppliers**: PO dengan beberapa supplier (hover untuk detail)

#### PO Detail View

Display lengkap dengan 2 sections:

**Section 1: Header**
- PO Number, Type, Date
- Article Info (if AUTO mode)
- Expected Delivery Date
- Status & Approval chain

**Section 2: Material List**
- Table dengan kolom: Material Name, Code, Type, Supplier, Qty, Unit, Price, Total
- Group by Supplier (collapsible)
- Export to Excel/PDF
### 3.3 🆕 Supplier Management

**Features**:
- Master database supplier dengan history PO
- Rating & Performance tracking per supplier
- Material specialization (Fabric, Label, Accessories)
- Auto-suggest supplier based on material type
- Contact person & payment terms

---

<a name="ppic-module"></a>
## 4. PPIC MODULE

### 4.1 PPIC Workflow Visualization - Complete Process

#### 📋 Manufacturing Order Creation & SPK Generation Flow

```
┌───────────────────────────────────────────────────────────────────────┐
│  PPIC DASHBOARD - MANUFACTURING ORDER CREATION                        │
└───────────────────────────────────────────────────────────────────────┘

INPUT:
├─ Customer Order: 450 pcs AFTONSPARV
├─ Delivery: Week 05-2026
├─ Destination: IKEA DC Belgium
└─ Deadline: 10 Feb 2026

SYSTEM AUTO-GENERATE MO (from PO Purchasing):
┌──────────────────────────────────────┐
│ MO-2026-00089 (AUTO-CREATED)        │
│ Artikel: [40551542] AFTONSPARV       │
│ Target: 450 pcs                      │
│ Week: W05-2026 (auto from PO Label) │
│ Destination: Belgium                 │
│                                      │
│ Status: PARTIAL ⚠️                   │
│ (Auto-upgrade to RELEASED when PO Label received)  │
│                                      │
│ ⏳ PPIC REVIEW STATUS:               │
│ [ ] Review Material Availability     │
│ [ ] Edit if needed (target/date)     │
│ [ ] ACCEPT → Trigger WO/SPK explosion│
│                                      │
│ BOM Manufacturing:                   │
│ ├─ Fabric: 30+ SKU                  │
│ ├─ Thread: 9 types                  │
│ ├─ Filling: 24.3 kg                 │
│ ├─ Label: 450 pcs (WAITING)         │
│ └─ Carton: 8 pcs                    │
│                                      │
│ Material Availability:               │
│ ├─ Fabric: ✅ 95% ready             │
│ ├─ Thread: ✅ 100% ready            │
│ ├─ Filling: ✅ 100% ready           │
│ ├─ Label: 🔴 0% (PO-LBL pending)    │
│ └─ Carton: ⚠️ 50% (need reorder)    │
└──────────────────────────────────────┘
        │
        ▼ (After PPIC ACCEPT)
┌──────────────────────────────────────┐
│ AUTO WO/SPK EXPLOSION                │
│ (Broadcast to Admin Dashboard)      │
│ 📝 WO = Work Order = SPK = Surat Perintah Kerja │
├──────────────────────────────────────┤
│                                      │
│ ✅ RELEASED (Active):                │
│ ├─ WO/SPK-CUT-BODY-2026-00120       │
│ │  Target: 495 pcs (450 + 10%)     │
│ │  Access: ✅ GRANTED               │
│ │                                   │
│ └─ WO/SPK-CUT-BAJU-2026-00121       │
│    Target: 495 pcs                  │
│    Access: ✅ GRANTED                │
│                                      │
│ 🔒 LOCKED (Pending PO Label):       │
│ ├─ WO/SPK-SEW-BODY-2026-00156       │
│ ├─ WO/SPK-SEW-BAJU-2026-00157       │
│ ├─ WO/SPK-FIN-STUFFING-2026-00089   │
│ ├─ WO/SPK-FIN-CLOSING-2026-00090    │
│ └─ WO/SPK-PCK-2026-00045            │
│                                      │
│ 📅 Auto-unlock when:                │
│    PO-LBL-2026-0789 received        │
└──────────────────────────────────────┘
```

#### 📊 Material Allocation Logic (BOM Calculation)

```
┌─────────────────────────────────────────────────────────────────┐
│  BOM CALCULATION & MATERIAL ALLOCATION                          │
└─────────────────────────────────────────────────────────────────┘

MO Target: 450 pcs
SPK Strategy: Flexible buffer per department

CALCULATION CASCADE:

[CUTTING] Buffer +10%
├─ SPK Target: 495 pcs (450 × 1.10)
├─ Material Allocated:
│  ├─ KOHAIR: 49.75 YD (495 × 0.1005 YD/pcs)
│  ├─ JS BOA: 4.65 YD (495 × 0.0094)
│  ├─ NYLEX BLACK: 0.50 YD (495 × 0.0010)
│  ├─ NYLEX WHITE: 2.18 YD (495 × 0.0044)
│  ├─ POLYESTER Prints: 20.66 YD
│  └─ POLYESTER Solid: 74.74 YD
│
└─ System Check:
   ├─ Available: KOHAIR 125 YD ✅ (enough)
   ├─ Available: POLYESTER 450 YD ✅
   └─ Action: CREATE RESERVATION in Warehouse

[SEWING] Buffer +15%
├─ SPK Target: 517 pcs (450 × 1.15)
├─ Constraint: ≤ Cutting Output
├─ Material Allocated:
│  ├─ Thread: 2,900 CM (variable per stitch)
│  └─ Wait for: Cut pieces from Cutting dept
│
└─ System Note: Target > MO untuk antisipasi defect

[FINISHING] Demand-Driven
├─ SPK Target: 480 pcs (not rigid to MO)
├─ Based on: Packing urgent need 465 pcs
├─ Material Allocated:
│  ├─ Filling: 25.92 kg (480 × 54 gram)
│  ├─ Thread Closing: 288 meter
│  └─ Hang Tag: 480 pcs (from PO Label)
│
└─ Flexibility: Adjust real-time to demand

[PACKING] Exact Match
├─ SPK Target: 465 pcs (urgent shipping)
├─ Material Allocated:
│  ├─ Carton: 8 pcs (60 pcs/CTN)
│  ├─ Pallet: 1 pc (shared 8 CTN)
│  └─ Pad: 1 pc
│
└─ Assembly: 1 Boneka + 1 Baju per set
```

### 4.2 Manufacturing Order (MO) Management

#### 🔥 DUAL TRIGGER PRODUCTION SYSTEM

**Konsep Revolutionary**: MO dapat dimulai dengan **2 stages** untuk reduce lead time.

##### STAGE 1: MO PARTIAL (PO Kain only)

**Workflow**:
```
[PO KAIN Created] → [System Auto-Generate MO PARTIAL] → [PPIC Review/Edit/Accept] → [Auto-Explode WO/SPK]
   ↓
[Cutting dapat start (WO/SPK-CUT)]
   ↓
[Embroidery dapat start (WO/SPK-EMB)]
   ↓
[Sewing, Finishing, Packing: HOLD - Waiting PO Label]
```

**UI Display**:
```
┌─────────────────────────────────────────────────────────────┐
│  MO-2026-00089 - [40551542] AFTONSPARV                      │
│  Status: 🟡 PARTIAL (PO Kain Ready)                        │
├─────────────────────────────────────────────────────────────┤
│  📋 Basic Info:                                             │
│  • MO Target: 450 pcs                                       │
│  • PO Reference:                                            │
│    - PO Kain: PO-K-2026-00012 ✅                           │
│    - PO Label: ⏳ Waiting...                               │
│  • Week: [Empty - Waiting PO Label]                        │
│  • Destination: [Empty - Waiting PO Label]                 │
│                                                              │
│  🚦 Department Release Status:                              │
│  • Cutting: ✅ RELEASED (can start)                        │
│  • Embroidery: ✅ RELEASED (can start)                     │
│  • Sewing: 🔒 HOLD (PO Label required)                     │
│  • Finishing: 🔒 HOLD (PO Label required)                  │
│  • Packing: 🔒 HOLD (PO Label required)                    │
│                                                              │
│  [WAIT FOR PO LABEL] [CANCEL MO]                            │
└─────────────────────────────────────────────────────────────┘
```

**Benefit**: 
- Cutting & Embroidery dapat start **3-5 hari lebih cepat**
- Reduce overall lead time significantly
- Material fabric (paling lama) sudah diproses duluan

##### STAGE 2: MO RELEASED (PO Label ready)

**Auto-upgrade ketika PO Label dibuat**:

```
[PO LABEL Created] → [System Auto-detect MO PARTIAL dengan same Article]
   ↓
[Auto-upgrade MO to RELEASED]
   ↓
[Auto-inherit Week & Destination dari PO Label]
   ↓
[Unlock ALL departments]
```

**UI Display After Upgrade**:
```
┌─────────────────────────────────────────────────────────────┐
│  MO-2026-00089 - [40551542] AFTONSPARV                      │
│  Status: 🟢 RELEASED (Full Production Ready)               │
├─────────────────────────────────────────────────────────────┤
│  📋 Complete Info:                                          │
│  • MO Target: 450 pcs                                       │
│  • PO References:                                           │
│    - PO Kain: PO-K-2026-00012 ✅                           │
│    - PO Label: PO-L-2026-00089 ✅                          │
│  • Week: W05 2026 [Auto from PO Label] 🔒                  │
│  • Destination: IKEA Distribution Center [Auto] 🔒         │
│                                                              │
│  🚦 Department Status (ALL RELEASED):                       │
│  • Cutting: ✅ SPK Active (520/517 pcs)                    │
│  • Embroidery: ✅ In Progress (495/495 pcs)                │
│  • Sewing: ✅ RELEASED (can start now)                     │
│  • Finishing: ✅ RELEASED (can start now)                  │
│  • Packing: ✅ RELEASED (can start now)                    │
│                                                              │
│  [VIEW SPK LIST] [MONITOR PROGRESS] [GENERATE REPORT]       │
└─────────────────────────────────────────────────────────────┘
```

**Key Features**:
- ✅ Week & Destination **auto-inherited** (zero manual entry error!)
- ✅ All departments unlocked instantly
- ✅ Audit trail: System log kapan upgrade dari PARTIAL → RELEASED
- ✅ Email notification ke PPIC & Production Admin

---

### 4.2 PPIC Dashboard - MO Overview

```
┌───────────────────────────────────────────────────────────────────┐
│  PPIC DASHBOARD - MANUFACTURING ORDERS                            │
├───────────────────────────────────────────────────────────────────┤
│  📊 Summary:                                                      │
│  • Total MO Active: 12                                           │
│    - PARTIAL (PO Kain only): 3 MOs 🟡                           │
│    - RELEASED (Full production): 7 MOs 🟢                       │
│    - COMPLETED: 2 MOs ✅                                         │
│                                                                   │
│  🔴 Critical Alerts:                                             │
│  • MO-2026-00056 - Delay 3 days (Sewing bottleneck)             │
│  • MO-2026-00078 - Material shortage (KOHAIR -45 YD)            │
│                                                                   │
│  📋 MO List (Sortable):                                          │
│  ┌───────────┬────────┬────────┬─────────┬──────────┬─────────┐ │
│  │ MO Number │ Status │ Target │ Actual  │ Week/Dest│ Days    │ │
│  ├───────────┼────────┼────────┼─────────┼──────────┼─────────┤ │
│  │ MO-00089  │ 🟢 REL │ 450 pcs│ 465/450 │ W05/IKEA │ 2 days  │ │
│  │ AFTONSP..│        │        │ (103%)  │          │ left ✅ │ │
│  ├───────────┼────────┼────────┼─────────┼──────────┼─────────┤ │
│  │ MO-00078  │ 🟡 PAR │ 600 pcs│ 320/600 │ Waiting  │ -       │ │
│  │ KRAMIG   │ (Kain) │        │ (53%)   │ PO Label │         │ │
│  └───────────┴────────┴────────┴─────────┴──────────┴─────────┘ │
│                                                                   │
│  [CREATE NEW MO] [FILTER] [EXPORT]                               │
└───────────────────────────────────────────────────────────────────┘
```

---

### 4.3 Schedule Production (SPK/WO Generation)

**Workflow**:
```
[MO RELEASED] → [PPIC Create SPK per Department]
   ↓
[BOM Explosion untuk material allocation]
   ↓
[SPK Active - Department can start production]
```

#### 🔥 FLEXIBLE TARGET SYSTEM

**Konsep Game-Changer**: SPK Target **dapat berbeda** dari MO Target!

**Formula Universal**: `Actual/Target pcs (Percentage%)`

**Example**:
```
MO Target: 450 pcs
SPK Target: 517 pcs (450 + 15% buffer)
Actual Production: 520 pcs

Display: 520/517 (100.6%) ✅ Exceed target!
```

**Buffer Strategy by Department**:
- **Cutting**: +10% (antisipasi fabric defect/waste)
- **Embroidery**: +5% (minimal loss, precision work)
- **Sewing**: +15% (highest defect rate, manual intensive)
- **Finishing**: +10% (stuffing may fail)
- **Packing**: 0% (exact match urgency)

**Constraint Logic**:
```
SPK Target Department N ≤ Good Output Department (N-1)

Example:
- Cutting Good Output: 495 pcs
- Sewing SPK Target MAX: 495 pcs (tidak boleh >495)
- Actual Sewing Target: 517 pcs (tapi input ≤495)
```

**UI Display**:
```
┌─────────────────────────────────────────────────────────────┐
│  CREATE SPK - SEWING BODY                                    │
├─────────────────────────────────────────────────────────────┤
│  📋 Reference:                                              │
│  • MO: MO-2026-00089 (Target: 450 pcs)                     │
│  • Previous Dept: EMBROIDERY (Good Output: 495 pcs)        │
│                                                              │
│  🎯 TARGET SETTING:                                         │
│  • MO Target: 450 pcs [Reference only]                     │
│  • Recommended Buffer: 15% (Sewing historical average)      │
│  • SPK Target: [Input: 517] pcs                            │
│    ⚠️ Max allowed: 495 pcs (Embroidery output)             │
│    ✅ Suggested: 517 pcs (450 × 1.15)                      │
│                                                              │
│  ℹ️ Why Buffer?                                             │
│  - Anticipated defect rate: ~12-15 pcs                     │
│  - Rework recovery: ~80%                                    │
│  - Final good output target: ≥450 pcs                      │
│                                                              │
│  [SAVE SPK] [CANCEL]                                         │
└─────────────────────────────────────────────────────────────┘
```

**Benefits**:
1. **Zero Shortage Risk**: Buffer ensures MO target always met
2. **Realistic Planning**: Account for real defect rates
3. **Optimal Material Usage**: Smart allocation based on buffer
4. **Fast Response**: Urgent orders dapat increase buffer instantly

---

### 4.4 🔥 REAL-TIME WIP (Work In Progress) SYSTEM

**Konsep Revolutionary**: Hasil produksi hari ini = Stok bahan baku dept berikutnya **instant** (tanpa tunggu SPK selesai semua).

#### 4.4.1 Parsialitas & Incremental Production

**Traditional System Problem**:
```
Cutting harus selesai 10,000 pcs dulu
    ↓ (tunggu 5 hari)
Baru Sewing bisa mulai
    ↓
Lead time panjang, WIP menumpuk
```

**ERP Quty Solution**:
```
Cutting Day 1: 500 pcs selesai
    ↓ (instant transfer)
Sewing Day 1: Langsung bisa mulai 500 pcs
    ↓
Cutting Day 2: 500 pcs lagi
    ↓ (instant transfer)
Sewing Day 2: Lanjut 500 pcs lagi
    ↓
Parallel production → Lead time -40%
```

#### 4.4.2 Admin Input Focus & Backend Process

**Admin Dept A (Cutting) Daily Input**:
```
┌────────────────────────────────────────┐
│  INPUT PRODUKSI HARIAN                 │
│  SPK-CUT-2026-00120                    │
│  Tanggal: 02 Feb 2026                  │
├────────────────────────────────────────┤
│  Qty Output Hari Ini: 500 pcs ✅       │
│  Material Used:                        │
│  ├─ KOHAIR: 50.25 YD                   │
│  └─ JS BOA: 0.75 YD                    │
│                                        │
│  Status SPK: ONGOING (500/495 pcs)     │
│  Status Batch: READY TO TRANSFER ✅    │
│                                        │
│  [SUBMIT & TRANSFER]                   │
└────────────────────────────────────────┘
```

**System Behavior Behind the Scene (Invisible to Admin)**:
```
1. Admin klik [SUBMIT & TRANSFER]
2. Backend Process:
   ├─ Update SPK-CUT: Progress 500/495 (101%)
   ├─ Generate DN-CUT-2026-00089:
   │  └─ From: Warehouse Main (Cutting)
   │      To: WIP Buffer (Embroidery/Sewing)
   │      Qty: 500 pcs Cut Body
   │      Status: AUTO-APPROVED (no manual signature)
   ├─ Update Inventory:
   │  ├─ WIP Cutting: -500 pcs
   │  └─ WIP Embroidery: +500 pcs ✅
   └─ Broadcast notification:
      └─ Dashboard Embroidery/Sewing: "Material Baru: 500 pcs"
```

**Admin Dept B (Sewing) Dashboard Instantly Updated**:
```
┌────────────────────────────────────────┐
│  BAHAN SIAP OLAH - REAL-TIME           │
│  SPK-SEW-BODY-2026-00120               │
├────────────────────────────────────────┤
│  🔔 NEW: +500 pcs Cut Body Available   │
│      (dari Cutting 02-Feb 14:30)      │
│                                        │
│  Total Stock Ready: 500 pcs            │
│  SPK Target: 517 pcs                   │
│                                        │
│  ✅ CAN START PRODUCTION NOW           │
│  [MULAI KERJA]                         │
└────────────────────────────────────────┘
```

#### 4.4.3 Dinamika Over-Production & Saldo Minus

**Case Study: Normal Flow**
```
Day 1:
├─ Cutting output: 500 pcs → WIP Buffer +500
└─ Sewing input: 200 pcs → WIP Buffer 300 (saldo)

Day 2:
├─ Cutting output: 500 pcs → WIP Buffer +500 (total 800)
└─ Sewing input: 300 pcs → WIP Buffer 500 (saldo)

Benefit: Sewing tidak pernah kehabisan material
```

**Case Study: Abnormal Flow (Minus)**
```
Day 1:
├─ Cutting output: 0 pcs (machine breakdown)
└─ Sewing input: 200 pcs → WIP Buffer -200 ⚠️

System Alert Dashboard Supervisor:
┌────────────────────────────────────────┐
│  🚨 SALDO MATERIAL MINUS DETECTED      │
├────────────────────────────────────────┤
│  Dept: Sewing Body                      │
│  Material: Cut Body AFTONSPARV         │
│  Current Saldo: -200 pcs               │
│                                        │
│  Possible Causes:                      │
│  ├─ Cutting belum input produksi      │
│  ├─ Material "melompat" tanpa DN      │
│  └─ Admin salah input qty              │
│                                        │
│  Action Required:                      │
│  ├─ Verifikasi fisik stock di lantai  │
│  ├─ Cek dengan Cutting apakah ada DN   │
│  └─ Reconcile di akhir shift           │
│                                        │
│  [RECONCILE NOW] [REMIND CUTTING]      │
└────────────────────────────────────────┘
```

**Reconciliation Process**:
```
Supervisor klik [RECONCILE NOW]:
1. System pause production input Sewing
2. Admin Cutting & Sewing physical count together
3. Find discrepancy:
   └─ Actual: Cutting ada output 150 pcs tapi lupa input
4. Admin Cutting input 150 pcs retrospective (with approval)
5. System adjust:
   ├─ WIP Buffer: -200 + 150 = -50 (masih minus)
   └─ Need 50 pcs lagi dari Cutting Day 2
6. Production resume
```

#### 4.4.4 Status Differentiation

**Status SPK vs Status Batch Produksi**:

| Aspek | Status SPK | Status Batch Produksi |
|-------|------------|----------------------|
| **Scope** | Keseluruhan SPK (target total) | Per hari / per input |
| **States** | PENDING, ONGOING, FINISHED | READY TO TRANSFER, TRANSFERRED, RECEIVED |
| **Update** | Kumulatif (500+500+...=total) | Incremental (hari ini berapa) |
| **Purpose** | Track completion vs target | Track material flow |

**Contoh Real**:
```
SPK-CUT-BODY-2026-00120 (Target: 495 pcs)

Status SPK: ONGOING
├─ Day 1: 500 pcs (101%) → Status SPK tetap ONGOING
└─ Progress: 500/495 pcs

Batch Production Day 1:
├─ Batch-001: 500 pcs
│  └─ Status: TRANSFERRED ✅
└─ Available for Next Dept: 500 pcs instant

Admin Cutting masih bisa lanjut input Day 2 jika ada over-production
(spare material tersedia)
```

#### 4.4.5 Keuntungan Business

| Benefit | Impact | Value |
|---------|--------|-------|
| **Parallel Production** | Lead time -40% | Faster delivery |
| **Zero Waiting Time** | Dept B start instant | Higher throughput |
| **Real-Time Visibility** | Manager lihat WIP live | Better decision |
| **Auto Material Flow** | No manual DN approval | Reduce admin time -60% |
| **Early Problem Detection** | Minus alert instant | Prevent stock-out |
| **Flexible Over-Production** | Use spare material optimal | Material efficiency +15% |

---

### 4.5 🔥 PULL SYSTEM & AUTO MATERIAL DEDUCTION

**Konsep**: Saat Admin Dept B submit production, sistem **otomatis menarik (pull)** material dari WIP Buffer Dept A.

#### 4.5.1 Pull Mechanism

**Traditional System** (Manual Push):
```
Admin A: Selesai 500 pcs → Bikin DN manual → Kirim ke Warehouse
Warehouse: Terima DN → Input ke system → Update stock
Admin B: Cek stock → Ada 500 pcs → Ambil material → Bikin dokumen tarik
Warehouse: Approve dokumen → Update stock lagi
    ↓
Total: 4 steps, 2-3 jam delay
```

**ERP Quty System** (Auto Pull):
```
Admin A: Submit 500 pcs ✅
    ↓ (instant, backend process)
System: Auto DN + Transfer + Update stock Dept A & B
    ↓ (0 delay)
Admin B: Lihat dashboard → 500 pcs available ✅
Admin B: Submit production 200 pcs
    ↓ (instant, backend auto-pull)
System: Potong stock WIP Buffer: 500 - 200 = 300 pcs
    ↓
Total: 2 steps, 0 delay, 0 manual paperwork
```

#### 4.5.2 Backend Process Detail

**Admin Sewing Submit Production**:
```
Input Form:
├─ SPK: SPK-SEW-LINE05-2026-00120
├─ Qty Output: 200 pcs
├─ Material Used:
│  ├─ Cut Body: 200 pcs (auto-calculated from BOM)
│  ├─ Thread: 5000 CM (auto-calculated)
│  └─ Label EU: 200 pcs (auto-calculated)
└─ [SUBMIT]

Backend Process (Invisible to Admin):
1. Validate Material Availability:
   ├─ WIP Buffer Cut Body: 500 pcs ≥ 200 pcs ✅
   ├─ Warehouse Thread: 15,000 CM ≥ 5,000 CM ✅
   └─ Warehouse Label: 350 pcs ≥ 200 pcs ✅

2. Auto Material Deduction:
   ├─ WIP Buffer Cut Body: 500 → 300 pcs
   ├─ Warehouse Thread: 15,000 → 10,000 CM
   └─ Warehouse Label: 350 → 150 pcs

3. Generate Internal Transaction Log:
   ├─ Trans-ID: TRX-SEW-2026-00345
   ├─ Type: MATERIAL PULL
   ├─ From: WIP Buffer (Cutting)
   ├─ To: Production Floor (Sewing Body)
   ├─ Qty: 200 pcs Cut Body
   ├─ Timestamp: 02-Feb-2026 14:35:22
   ├─ By User: admin_sewing_line05
   └─ Status: COMPLETED ✅

4. Update SPK Progress:
   ├─ SPK-SEW-LINE05: Progress 200/200 pcs (100%)
   └─ Status: COMPLETED ✅

5. Generate Output to WIP Next Dept:
   ├─ WIP Buffer Finishing: +195 pcs (200 - 5 defect)
   └─ Notification: Dashboard Finishing gets alert
```

#### 4.5.3 Traceability & Audit Trail

**Full Transparency** - Every transaction is logged dengan 5W1H:

**Audit Log Structure**:
```
┌─────────────────────────────────────────────────────────┐
│  AUDIT LOG - MATERIAL MOVEMENT TRACKING                 │
├─────────────────────────────────────────────────────────┤
│  Transaction ID: TRX-SEW-2026-00345                     │
│                                                         │
│  WHO:   admin_sewing (ID: USR-0089)                  │
│  WHAT:  Material Pull - Cut Body AFTONSPARV            │
│  WHEN:  02-Feb-2026 14:35:22 WIB                       │
│  WHERE: From WIP Buffer (Cutting) → Sewing           │
│  WHY:   Production SPK-SEW-BODY-2026-00120             │
│  HOW:   Auto-deduction via system (backend process)    │
│                                                         │
│  Detail Movement:                                       │
│  ├─ Material: [AFTONSPARV_CUT_BODY]                    │
│  ├─ Qty: -200 pcs (deduction)                          │
│  ├─ Before: 500 pcs                                    │
│  ├─ After: 300 pcs                                     │
│  └─ Variance: 0 pcs (match BOM)                        │
│                                                         │
│  Related Transactions:                                  │
│  ├─ Previous: TRX-CUT-2026-00289 (Cutting output)      │
│  └─ Next: TRX-SEW-2026-00346 (Sewing output to FIN)    │
│                                                         │
│  Approval Status: AUTO-APPROVED ✅                      │
│  (No manual approval needed for normal flow)            │
└─────────────────────────────────────────────────────────┘
```

**Manager View - Transaction Chain**:
```
┌─────────────────────────────────────────────────────────┐
│  MATERIAL FLOW TRACE: Cut Body AFTONSPARV              │
│  Date Range: 01-Feb to 03-Feb 2026                     │
├─────────────────────────────────────────────────────────┤
│  
│  [CUTTING] 01-Feb 10:00
│  ├─ TRX-CUT-2026-00289
│  ├─ Input: KOHAIR 50.25 YD
│  └─ Output: 500 pcs Cut Body → WIP Buffer
│      
│  [SEWING BODY] 01-Feb 14:35
│  ├─ TRX-SEW-2026-00345 ⬅️ YOU ARE HERE
│  ├─ Pull: 200 pcs Cut Body ← WIP Buffer
│  └─ Output: 195 pcs Skin → WIP Finishing
│      
│  [SEWING BODY] 02-Feb 08:15
│  ├─ TRX-SEW-2026-00351
│  ├─ Pull: 100 pcs Cut Body ← WIP Buffer
│  └─ Output: 98 pcs Skin → WIP Finishing
│      
│  [WIP BUFFER STATUS]
│  └─ Remaining: 200 pcs Cut Body (available)
│
└─────────────────────────────────────────────────────────┘
```

#### 4.5.4 Discrepancy Detection & Alert

**Real-Time Monitoring**:

**Case 1: Material Shortage**
```
Sewing tries to pull 200 pcs, but WIP Buffer only has 150 pcs:

System Response:
├─ BLOCK submission
├─ Show alert:
│  "⚠️ Material Insufficient!
│   Required: 200 pcs Cut Body
│   Available: 150 pcs
│   Shortage: 50 pcs
│   
│   Action:
│   ├─ Wait for Cutting to complete
│   └─ OR reduce qty to 150 pcs"
└─ Notify Supervisor & PPIC via WhatsApp
```

**Case 2: Material "Melompat" (Untracked Movement)**
```
Physical count shows 300 pcs di Sewing, but system shows 500 pcs:

System Detect (Daily Reconciliation):
├─ Expected (system): 500 pcs
├─ Actual (physical): 300 pcs
├─ Discrepancy: -200 pcs (missing)
└─ Alert Supervisor:
   "🚨 Material Discrepancy Detected!
    Possible causes:
    ├─ Material moved without system input
    ├─ Theft/loss (investigate)
    └─ Admin forgot to input production
    
    Please reconcile before end of day."
```

#### 4.5.5 End-of-Month Reconciliation

**Auto vs Manual Reconciliation**:

| Frequency | Trigger | Action |
|-----------|---------|--------|
| **Daily** | Auto at 23:00 | Soft warning if variance <5% |
| **Weekly** | Auto every Friday | Email to SPV if variance >2% |
| **Monthly** | Manual by Manager | Hard reconciliation + physical count |

**Monthly Reconciliation Workflow**:
```
1. System generate report:
   ├─ All negative balances
   ├─ High variance locations (>10%)
   └─ Suspicious transaction patterns

2. Manager assign reconciliation team:
   ├─ Admin Dept A + Admin Dept B
   └─ Supervisor witness

3. Physical count & adjust:
   ├─ Count actual stock di lantai
   ├─ Compare dengan system
   └─ Input adjustment with approval

4. System record:
   ├─ Adjustment transaction
   ├─ Reason for discrepancy
   └─ Corrective action taken

5. Lock period:
   └─ No retroactive input allowed after lock
```

#### 4.5.6 Benefit Summary

| Feature | Traditional | ERP Quty Pull System |
|---------|-------------|----------------------|
| **Material Request** | Manual form, 2-3 jam | Auto-pull, instant |
| **Paperwork** | DN manual, sign, scan | Zero paperwork |
| **Stock Update** | Manual input, delay | Real-time auto |
| **Traceability** | Susah lacak | Full audit log 5W1H |
| **Discrepancy** | Found at month-end | Alert instant |
| **Reconciliation** | Manual, 2-3 hari | Semi-auto, 2-3 jam |

---

### 4.6 🔥 VALIDATION & TOLERANCE RULES

**Konsep**: Sistem harus fleksibel untuk over-production (spare material), tapi tetap ada **kontrol ketat** untuk mencegah manipulasi data.

#### 4.6.1 Over-Production Tolerance

**Business Rule**: Produksi boleh melebihi SPK Target, tetapi harus dalam batas wajar (3-5%).

**Tolerance Levels**:

| Variance | Action | Approval Required |
|----------|--------|-------------------|
| **0-3%** | ✅ AUTO-APPROVE | No (normal operation) |
| **3-5%** | ⚠️ WARNING | SPV review (soft) |
| **5-10%** | ⚠️ REQUIRE REASON | SPV approval (mandatory) |
| **>10%** | ❌ BLOCK | Manager approval (investigation) |

**Example Flow**:

**Case 1: Normal (2% over)**
```
SPK Target: 495 pcs
Admin Input: 505 pcs (102%)
Variance: +2%

System Response:
├─ Status: ✅ AUTO-APPROVED
├─ Message: "Production completed successfully"
└─ No additional action needed
```

**Case 2: Warning (4% over)**
```
SPK Target: 495 pcs
Admin Input: 515 pcs (104%)
Variance: +4%

System Response:
├─ Status: ⚠️ WARNING - Need SPV Review
├─ Message: "Production exceeds target by 4%
│           Please confirm with Supervisor"
├─ Auto-notify: SPV via dashboard notification
└─ SPV Action:
   ├─ Review: Check if spare material memang ada
   ├─ Decision: Approve / Adjust qty
   └─ Submit with notes
```

**Case 3: Require Reason (7% over)**
```
SPK Target: 495 pcs
Admin Input: 530 pcs (107%)
Variance: +7%

System Response:
├─ Status: ⚠️ BLOCKED - Need Justification
├─ Form Popup:
│  ┌────────────────────────────────────┐
│  │  OVER-PRODUCTION JUSTIFICATION     │
│  ├────────────────────────────────────┤
│  │  SPK: SPK-CUT-2026-00120           │
│  │  Target: 495 pcs                   │
│  │  Actual: 530 pcs (107%)            │
│  │  Variance: +35 pcs (7%)            │
│  │                                    │
│  │  Reason (Required): ______________ │
│  │  Contoh:                           │
│  │  "Ada spare kain 3.5 YD sisa PO    │
│  │   sebelumnya, daripada waste."     │
│  │                                    │
│  │  [SUBMIT FOR APPROVAL]             │
│  └────────────────────────────────────┘
└─ Workflow:
   1. Admin submit reason
   2. SPV review & approve
   3. System record justification in audit log
   4. Production accepted
```

**Case 4: Critical (12% over)**
```
SPK Target: 495 pcs
Admin Input: 555 pcs (112%)
Variance: +12%

System Response:
├─ Status: ❌ BLOCKED - Manager Approval Required
├─ Alert Chain:
│  ├─ Admin: "Cannot submit, variance too high"
│  ├─ SPV: "High variance detected, investigate"
│  └─ Manager: "Approval needed for SPK-CUT-2026-00120"
├─ Investigation Required:
│  ├─ Verify physical stock
│  ├─ Check material source (PO mana)
│  ├─ Interview admin & operator
│  └─ Potential issue: Manipulasi data / material theft
└─ Manager Decision:
   ├─ APPROVE: If legitimate (with strong justification)
   ├─ ADJUST: Reduce qty to actual verified amount
   └─ REJECT: If cannot verify, start audit process
```

#### 4.6.2 Material Variance Tolerance

**BOM vs Actual Usage**:

| Variance | Material Type | Action |
|----------|---------------|--------|
| **0-5%** | Fabric, Thread | ✅ Normal (waste tolerance) |
| **5-10%** | Fabric | ⚠️ Review (possible cutting error) |
| **>10%** | Fabric | ❌ Block (investigate) |
| **>2%** | Filling, Accessories | ⚠️ Review (count error likely) |

**Example - Fabric Usage**:
```
BOM Standard: 0.1005 YD/pcs × 500 pcs = 50.25 YD
Admin Input: 53.00 YD
Variance: +5.5%

System Response:
├─ Status: ⚠️ WARNING - Above Normal Waste
├─ Alert SPV: "Fabric usage variance 5.5%
│              Normal waste: 3-5%
│              Possible causes:
│              ├─ Marker tidak optimal
│              ├─ Kain cacat (must cut more)
│              └─ Salah hitung input"
└─ SPV Action:
   ├─ Verify cutting layout
   ├─ Check fabric quality report
   └─ Approve with notes or adjust qty
```

#### 4.6.3 Minus Stock Tolerance

**WIP Buffer Negative Balance**:

| Minus Level | Action | Timeline |
|-------------|--------|----------|
| **-1 to -5%** | ⚠️ Soft alert | Reconcile within 24 hours |
| **-5 to -10%** | ⚠️ Hard alert | Reconcile within 4 hours |
| **>-10%** | ❌ Block next input | Reconcile immediately |

**Example - Minor Minus**:
```
WIP Buffer Cut Body: 500 pcs
Sewing pulls: 520 pcs (over-consumption)
Balance: -20 pcs (-4%)

System Response:
├─ Status: ⚠️ Soft Alert
├─ Allow: Sewing can continue (trust first)
├─ Notify: SPV + PPIC via dashboard
├─ Message: "WIP Buffer minus -20 pcs (-4%)
│           Expected reconciliation:
│           Cutting will input 520+ pcs today"
└─ Timeline: Must reconcile within 24 hours
            (likely Cutting forgot to input)
```

**Example - Critical Minus**:
```
WIP Buffer Cut Body: 500 pcs
Sewing pulls: 600 pcs (massive over-consumption)
Balance: -100 pcs (-20%)

System Response:
├─ Status: ❌ CRITICAL - Block Next Input
├─ Block: Sewing cannot submit more production
├─ Alert Chain:
│  ├─ Sewing SPV: Production blocked
│  ├─ Cutting SPV: Verify output urgently
│  ├─ PPIC: Material flow disrupted
│  └─ Manager: Investigation required
├─ Mandatory Action:
│  1. STOP all related production
│  2. Physical count Cutting + Sewing
│  3. Find 100 pcs discrepancy
│  4. Submit incident report
│  5. Manager approve reconciliation
│  6. System unlock after verified
└─ Timeline: Must reconcile immediately (max 2 hours)
```

#### 4.6.4 Time-Based Tolerance (Late Input)

**Retroactive Input Rules**:

| Time Gap | Action | Approval |
|----------|--------|----------|
| **Same day** | ✅ Allow | No approval |
| **1-2 days** | ⚠️ Allow with reason | SPV approval |
| **3-7 days** | ⚠️ Allow with reason | Manager approval |
| **>7 days** | ❌ Block | Director approval only |

**Example - Late Input**:
```
Today: 10-Feb-2026
Admin tries to input production for: 03-Feb-2026
Time Gap: 7 days

System Response:
├─ Status: ⚠️ LATE INPUT - Manager Approval Required
├─ Form:
│  ┌────────────────────────────────────┐
│  │  RETROACTIVE INPUT REQUEST         │
│  ├────────────────────────────────────┤
│  │  Production Date: 03-Feb-2026      │
│  │  Input Date: 10-Feb-2026           │
│  │  Gap: 7 days ⚠️                    │
│  │                                    │
│  │  Reason (Mandatory): ____________  │
│  │  "Admin sakit, baru masuk hari ini"│
│  │                                    │
│  │  Verified By: ________________     │
│  │  (SPV signature)                   │
│  │                                    │
│  │  [SUBMIT FOR MANAGER APPROVAL]     │
│  └────────────────────────────────────┘
└─ Impact:
   ├─ All subsequent calculations affected
   ├─ WIP balance may show incorrect history
   └─ Manager must verify cascade impact
```

#### 4.6.5 Fraud Prevention Patterns

**System Auto-Detect Suspicious Patterns**:

**Pattern 1: Frequent High Variance**
```
Admin A input history (last 7 days):
├─ Day 1: +4% over target
├─ Day 2: +6% over target
├─ Day 3: +5% over target
├─ Day 4: +7% over target
└─ Pattern: Consistently high variance

System Alert Manager:
"⚠️ Suspicious Pattern Detected
 Admin: admin_cutting_01
 Pattern: Consistent over-production 4-7%
 Possible issues:
 ├─ Material hoarding untuk bonus
 ├─ Manipulasi data
 └─ Poor target setting (SPV review needed)
 
 Recommended Action:
 └─ Audit last week's production + material usage"
```

**Pattern 2: Minus-Plus Cycle**
```
WIP Buffer history:
├─ Day 1: -50 pcs (Dept B over-pull)
├─ Day 2: +60 pcs (Dept A over-produce)
├─ Day 3: -50 pcs (Dept B over-pull again)
├─ Day 4: +60 pcs (Dept A over-produce again)
└─ Pattern: Coordinated manipulation?

System Alert:
"🚨 Coordinated Pattern Detected
 Possible collusion between Dept A & B
 └─ Director investigation required"
```

#### 4.6.6 Implementation Checklist

**System Configuration**:
```
[ ] Set tolerance levels per dept (customizable)
[ ] Configure approval workflow (SPV → Manager → Director)
[ ] Setup alert thresholds & notification channels
[ ] Define reconciliation frequency (daily/weekly/monthly)
[ ] Create fraud detection rules & ML patterns
[ ] Train all users on tolerance policies
[ ] Document all validation rules in SOP
```

**Benefit Summary**:

| Aspect | Without Tolerance | With Smart Tolerance |
|--------|-------------------|----------------------|
| **Flexibility** | Rigid, cannot use spare | Flexible 3-5% auto-approved |
| **Control** | No control, easy manipulate | Multi-level approval >5% |
| **Efficiency** | Everything needs approval | 95% auto-approved (normal) |
| **Fraud Risk** | High (no detection) | Low (pattern detection) |
| **Audit Trail** | Manual investigation | Auto-flagged suspicious |

---

### 4.7 PPIC - Multi-SPK Monitoring untuk 1 MO

**Scenario**: 1 MO → Multiple parallel SPKs (Body & Baju)

```
┌─────────────────────────────────────────────────────────────────┐
│  MO-2026-00089 - AFTONSPARV (Target: 450 pcs)                  │
│  Progress Aggregate: 998/450 pcs (221% coverage) ✅            │
├─────────────────────────────────────────────────────────────────┤
│  📊 SPK Breakdown:                                              │
│                                                                  │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║ SPK-SEW-BODY-2026-00120                                   ║ │
│  ║ Target: 517 pcs | Actual: 520/517 (100.6%) ✅            ║ │
│  ║ Good Output: 508 pcs | Defect: 12 pcs (2.3%)             ║ │
│  ║ Rework: 10 pcs recovered → Final: 518 pcs                ║ │
│  ║ Status: COMPLETED                                         ║ │
│  ║                                                            ║ │
│  ║ Daily Progress (Calendar View):                           ║ │
│  ║ [2] [3: 105] [4: 110] [5: 108] [6: 97] = 520 total       ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
│                                                                  │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║ SPK-SEW-BAJU-2026-00121                                   ║ │
│  ║ Target: 495 pcs | Actual: 500/495 (101%) ✅              ║ │
│  ║ Good Output: 495 pcs | Defect: 5 pcs (1.0%)              ║ │
│  ║ After Rework: 500 pcs (all recovered)                     ║ │
│  ║ Status: COMPLETED                                         ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
│                                                                  │
│  🎯 MO Fulfillment Analysis:                                   │
│  • Min(Body: 518, Baju: 500) = 500 complete sets possible     │
│  • MO Target: 450 pcs                                          │
│  • Achievement: 500/450 (111%) ✅ SURPLUS 50 pcs              │
│  • Extra Stock: Body +18, Baju +50 (for future orders)        │
│                                                                  │
│  [GENERATE MO COMPLETION REPORT] [CLOSE MO]                     │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features**:
- ✅ Aggregate monitoring: Total dari semua SPK vs MO Target
- ✅ Constraint validation: Packing tidak bisa exceed MIN(Body, Baju)
- ✅ Surplus tracking: Extra stock automatically added to inventory
- ✅ Completion gate: MO hanya bisa closed jika ≥ Target

---
<a name="production-module"></a>
## 5. PRODUCTION MODULE

### 5.1 Complete Production Flow - 6 Stages Visualization

#### 🏭 End-to-End Production Stages (from Material to Finished Goods)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  PRODUCTION FLOW - 6 STAGES (Parallel & Sequential)                       │
└────────────────────────────────────────────────────────────────────────────┘

DAY 1-2: CUTTING (2 Parallel Streams)
═══════════════════════════════════════════════════════════════════════════

    WAREHOUSE MAIN
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
    [MATERIAL ISSUE]   [MATERIAL ISSUE]   [MATERIAL ISSUE]
    Fabric for Body    Fabric for Baju   Thread & Acc
         │                  │
         ▼                  ▼
    ┌─────────────┐    ┌─────────────┐
    │  CUTTING A  │    │  CUTTING B  │
    │   (BODY)    │    │   (BAJU)    │
    │             │    │             │
    │ SPK Target: │    │ SPK Target: │
    │  495 pcs    │    │  495 pcs    │
    │             │    │             │
    │ Input Day 1:│    │ Input Day 1:│
    │  250 pcs ✅ │    │  250 pcs ✅ │
    │ Input Day 2:│    │ Input Day 2:│
    │  250 pcs ✅ │    │  245 pcs ✅ │
    │             │    │             │
    │ Total: 500  │    │ Total: 495  │
    │ Good: 495   │    │ Good: 495   │
    │ Defect: 5→Q │    │ Defect: 0   │
    └─────────────┘    └─────────────┘
         │                  │
         │ AUTO TRANSFER    │ HOLD FOR PACKING
         ▼                  ▼
    🔄 WIP BUFFER      📦 WAREHOUSE MAIN
    (Cut Body 495)     (Cut Baju 495)


DAY 3: EMBROIDERY (Optional, Body Only)
═══════════════════════════════════════════════════════════════════════════

    🔄 WIP BUFFER (Cut Body 495 pcs)
         │
         ▼
    ┌──────────────────┐
    │   EMBROIDERY     │
    │                  │
    │ SPK Target:      │
    │  495 pcs         │
    │                  │
    │ Process:         │
    │ ├─ Logo IKEA     │
    │ ├─ Text detail   │
    │ └─ QC check      │
    │                  │
    │ Input Day 3:     │
    │  495 pcs ✅      │
    │                  │
    │ Good Output:     │
    │  495 pcs (100%)  │
    └──────────────────┘
         │
         │ AUTO TRANSFER
         ▼
    🔄 WIP BUFFER
    (Embroidered Body 495)


DAY 4-5: SEWING (2 Parallel Streams)
═══════════════════════════════════════════════════════════════════════════

    🔄 WIP BUFFER           📦 WAREHOUSE MAIN
    (Embroidered 495)       (Cut Baju 495)
         │                        │
         ▼                        ▼
    ┌─────────────┐         ┌─────────────┐
    │  SEWING A   │         │  SEWING B   │
    │   (BODY)    │         │   (BAJU)    │
    │             │         │             │
    │ 🔒 WAIT PO  │         │ 🔒 WAIT PO  │
    │    LABEL    │         │    LABEL    │
    │             │         │             │
    │ Status:     │         │ Status:     │
    │ RELEASED ✅ │         │ RELEASED ✅ │
    │ (Day 4)     │         │ (Day 4)     │
    │             │         │             │
    │ SPK Target: │         │ SPK Target: │
    │  517 pcs    │         │  495 pcs    │
    │             │         │             │
    │ Day 4: 260  │         │ Day 4: 250  │
    │ Day 5: 260  │         │ Day 5: 250  │
    │             │         │             │
    │ Total: 520  │         │ Total: 500  │
    │ Good: 508   │         │ Good: 495   │
    │ Defect: 12→Q│         │ Defect: 5→Q │
    │ Rework: +10 │         │ Rework: +5  │
    │ Final: 518  │         │ Final: 500  │
    └─────────────┘         └─────────────┘
         │                        │
         │ AUTO TRANSFER          │ HOLD
         ▼                        ▼
    📦 WAREHOUSE            📦 WAREHOUSE
       FINISHING               MAIN
    (Skin 518 pcs)         (Baju 500 pcs)


DAY 6-7: WAREHOUSE FINISHING (2-Stage Process)
═══════════════════════════════════════════════════════════════════════════

STAGE 1: STUFFING (Internal Process)
────────────────────────────────────────

    📦 WAREHOUSE FINISHING
       (Skin 518 pcs available)
         │
         ▼
    ┌──────────────────────────┐
    │  STAGE 1: STUFFING       │
    │                          │
    │  SPK Target: 480 pcs     │
    │  (Demand-driven)         │
    │                          │
    │  Material Consume:       │
    │  ├─ Skin: 480 pcs        │
    │  ├─ Filling: 25.92 kg    │
    │  │  (480 × 54 gram)      │
    │  └─ Thread: 288 meter    │
    │                          │
    │  Day 6: 240 pcs ✅       │
    │  Day 7: 243 pcs ✅       │
    │                          │
    │  Total: 483 pcs          │
    │  Good: 473 pcs (97.9%)   │
    │  Defect: 10 pcs → QC     │
    │  Rework: +8 pcs          │
    │  Final: 481 pcs          │
    │                          │
    │  Inventory Update:       │
    │  ├─ Skin: 518→38 pcs    │
    │  └─ Stuffed: 0→481 pcs  │
    └──────────────────────────┘
         │
         ▼
    📦 WAREHOUSE FINISHING
       (Stuffed Body 481 pcs)


STAGE 2: CLOSING (Final Touch)
────────────────────────────────────────

    📦 WAREHOUSE FINISHING
       (Stuffed Body 481 pcs)
         │
         ▼
    ┌──────────────────────────┐
    │  STAGE 2: CLOSING        │
    │                          │
    │  SPK Target: 470 pcs     │
    │  (Match packing need)    │
    │                          │
    │  Material Consume:       │
    │  ├─ Stuffed: 470 pcs     │
    │  └─ Hang Tag: 470 pcs    │
    │                          │
    │  Day 7: 235 pcs ✅       │
    │  Day 8: 237 pcs ✅       │
    │                          │
    │  Total: 472 pcs          │
    │  Good: 468 pcs (99.2%)   │
    │  Defect: 4 pcs → QC      │
    │  Rework: +3 pcs          │
    │  Final: 471 pcs          │
    │                          │
    │  Inventory Update:       │
    │  ├─ Stuffed: 481→11 pcs │
    │  └─ Finished: 0→471 pcs │
    └──────────────────────────┘
         │
         │ TRANSFER TO PACKING
         ▼
    📦 WAREHOUSE MAIN
       (Finished Doll 471 pcs)


DAY 8-9: PACKING (Assembly)
═══════════════════════════════════════════════════════════════════════════

    📦 WAREHOUSE MAIN
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    Finished Doll   Cut Baju      Carton
    471 pcs         500 pcs       8 pcs
         │              │              │
         └──────────────┴──────────────┘
                     │
                     ▼
    ┌─────────────────────────────────┐
    │  PACKING DEPARTMENT             │
    │                                 │
    │  SPK Target: 465 pcs            │
    │  (Urgent shipping Week 05)      │
    │                                 │
    │  Assembly:                      │
    │  ├─ 1 Finished Doll             │
    │  ├─ 1 Baju                      │
    │  ├─ 1 Carton (60 pcs/CTN)       │
    │  └─ Label Week + Destination    │
    │                                 │
    │  Packing Schedule:              │
    │  Day 8: 300 pcs (5 CTN) ✅      │
    │  Day 9: 165 pcs (3 CTN) ✅      │
    │                                 │
    │  Total Packed: 465 pcs          │
    │  ├─ CTN 001-007: 60 pcs each    │
    │  └─ CTN 008: 45 pcs (partial)   │
    │                                 │
    │  Label Info:                    │
    │  ├─ Week: W05-2026              │
    │  ├─ Destination: Belgium        │
    │  ├─ PO: PO-LBL-2026-0789        │
    │  └─ Artikel: AFTONSPARV         │
    │                                 │
    │  Stock Remaining:               │
    │  ├─ Finished Doll: 6 pcs        │
    │  └─ Baju: 35 pcs                │
    └─────────────────────────────────┘
         │
         │ TRANSFER TO FG
         ▼
    📦 WAREHOUSE FG
       8 CTN (465 pcs)
       READY TO SHIP ✅
```

#### 📊 Real-Time WIP Dashboard (Live Inventory Tracking)

```
┌────────────────────────────────────────────────────────────────────┐
│  REAL-TIME WIP DASHBOARD - LIVE INVENTORY TRACKING                │
└────────────────────────────────────────────────────────────────────┘

ARTIKEL: [40551542] AFTONSPARV - MO-2026-00089
Status: PRODUCTION ONGOING (Day 7 of 9)

┌──────────────────┬──────────┬──────────┬──────────┬──────────────┐
│ LOCATION         │ TYPE     │ QTY      │ STATUS   │ NEXT ACTION  │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ Warehouse Main   │ Fabric   │ 25.5 YD  │ Reserved │ Hold buffer  │
│ Warehouse Main   │ Thread   │ 1200 CM  │ Reserved │ Hold buffer  │
│ Warehouse Main   │ Filling  │ 19.1 kg  │ Reserved │ For next MO  │
│ Warehouse Main   │ Baju     │ 500 pcs  │ Ready    │ Wait Packing │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ WIP Cutting      │ Cut Body │ 0 pcs    │ Complete │ -            │
│ WIP Embroidery   │ Emb Body │ 0 pcs    │ Complete │ -            │
│ WIP Sewing       │ Skin     │ 0 pcs    │ Complete │ -            │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ WH Finishing     │ Skin     │ 38 pcs   │ Buffer   │ For next MO  │
│ WH Finishing     │ Stuffed  │ 11 pcs   │ Buffer   │ Continue Day8│
│ WH Finishing     │ Finished │ 471 pcs  │ Ready ✅ │ To Packing   │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ Packing Line     │ Sets     │ 465 pcs  │ Packed ✅│ To FG        │
│ Warehouse FG     │ Cartons  │ 8 CTN    │ Ready ✅ │ Ship Day 10  │
└──────────────────┴──────────┴──────────┴──────────┴──────────────┘

📊 PRODUCTION SUMMARY:
├─ MO Target: 450 pcs
├─ Actual Output: 465 pcs (103.3% ✅)
├─ Overall Yield: 94.1%
├─ Total Defects: 41 pcs (4.0%)
├─ Rework Success: 34 pcs (82.9% recovery ✅)
├─ Scrap Loss: 7 pcs (0.7%)
└─ Status: ON-TIME for Week 05 deadline ✅
```

---

### 5.2 Production Flow Overview

```
CUTTING → EMBROIDERY* → SEWING → FINISHING (2-stage) → PACKING → FG
(*optional)
```

### 5.3 Universal UI Template untuk Semua Departemen

Setiap departemen memiliki **3 halaman utama** dengan struktur sama:

#### A. List SPK/WO (Active & Completed)

```
┌─────────────────────────────────────────────────────────────────┐
│  SEWING - ACTIVE SPK LIST                                       │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [All Status ▾] [All Articles ▾] [Week: All ▾]        │
│                                                                  │
│  ┌──────────┬────────┬─────────┬──────────┬─────────┬────────┐ │
│  │ SPK No   │ Article│ Target  │ Actual   │ Week    │ Status │ │
│  ├──────────┼────────┼─────────┼──────────┼─────────┼────────┤ │
│  │ SEW-00120│ AFTON..│ 517 pcs │ 520/517  │ W05     │ ✅ DONE│ │
│  │          │        │ +15%buf │ (100.6%) │ IKEA    │        │ │
│  │          │        │         │ Good:508 │         │        │ │
│  │          │        │         │ Def:12   │         │        │ │
│  ├──────────┼────────┼─────────┼──────────┼─────────┼────────┤ │
│  │ SEW-00121│ KRAMIG │ 600 pcs │ 450/600  │ W06     │🔄 PROG│ │
│  │          │        │ +20%buf │ (75%)    │ Target  │        │ │
│  │          │        │         │ Days: 2  │         │        │ │
│  └──────────┴────────┴─────────┴──────────┴─────────┴────────┘ │
│                                                                  │
│  [VIEW DETAILS] per SPK untuk daily progress & calendar view    │
└─────────────────────────────────────────────────────────────────┘
```

#### B. Daily Progress (Kalender View)

**Konsep**: Input produksi harian dengan tampilan kalender intuitif.

```
┌─────────────────────────────────────────────────────────────────┐
│  SPK-SEW-BODY-2026-00120 - AFTONSPARV                          │
│  Target: 517 pcs (MO: 450 + Buffer 15%) | Periode: 5 hari kerja│
├─────────────────────────────────────────────────────────────────┤
│  📅 JANUARI 2026                                                │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐                  │
│  │ Sen  │ Sel  │ Rab  │ Kam  │ Jum  │ Sab  │                  │
│  ├──────┼──────┼──────┼──────┼──────┼──────┤                  │
│  │  1   │  2   │  3   │  4   │  5   │  6   │                  │
│  │ ---  │ ---  │[105]✅│[110]✅│[108]✅│[97]✅│                 │
│  │      │      │      │      │      │      │                  │
│  └──────┴──────┴──────┴──────┴──────┴──────┘                  │
│                                                                  │
│  📊 Progress Summary:                                           │
│  • Total Production: 520/517 pcs (100.6%) ✅                   │
│  • Good Output: 508 pcs (Yield: 97.7%)                         │
│  • Defect: 12 pcs (2.3%)                                       │
│    └─ To Rework: 12 pcs → Recovery: 10 pcs ✅                 │
│  • Daily Average: 104 pcs/day ✅ (vs target: 103 pcs/day)     │
│                                                                  │
│  📝 INPUT HARIAN (Click tanggal untuk input):                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Tanggal: 3 Januari 2026                                  │  │
│  │                                                            │  │
│  │ • Production Quantity: [105] pcs                          │  │
│  │ • Good Output: [103] pcs (Quality passed)                │  │
│  │ • Defect Found: [2] pcs                                   │  │
│  │   └─ Reason: [Dropdown: Jahitan putus/Salah ukuran/...]  │  │
│  │                                                            │  │
│  │ • Notes: [Optional: Mesin #3 maintenance 1 jam]          │  │
│  │                                                            │  │
│  │ [SAVE] [CANCEL]                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [COMPLETE SPK] ← Available when Progress ≥100%                 │
└─────────────────────────────────────────────────────────────────┘
```

**Features**:
- ✅ Visual calendar dengan color coding (gray: holiday, green: completed, yellow: partial)
- ✅ Click tanggal untuk input harian (modal popup)
- ✅ Auto-calculate kumulatif progress
- ✅ Defect tracking langsung saat input
- ✅ Notes untuk mencatat kendala harian
- ✅ SPK completion gate: Hanya bisa complete jika ≥Target

---

### 4.2 PPIC Dashboard untuk Multi-SPK Monitoring

**Purpose**: Monitor aggregate progress dari semua SPK untuk 1 MO.

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 PPIC DASHBOARD - MO MONITORING                              │
│  MO-2026-00089 | AFTONSPARV | Target: 450 pcs                 │
├─────────────────────────────────────────────────────────────────┤
│  📦 SPK Breakdown for this MO:                                  │
│                                                                  │
│  🔹 Cutting Department (2 Parallel Streams):                    │
│  ├─ CUT-BODY-2026-00120 (Body Parts)                           │
│  │  ├─ Target: 495 pcs (with +10% buffer)                      │
│  │  ├─ Actual: 500/495 (101%) ✅ COMPLETED                    │
│  │  ├─ Good Output: 495 pcs (99% yield)                        │
│  │  └─ Transfer to Embroidery: ✅ Done                         │
│  │                                                              │
│  └─ CUT-BAJU-2026-00121 (Baju/Clothes)                         │
│     ├─ Target: 495 pcs (with +10% buffer)                       │
│     ├─ Actual: 500/495 (101%) ✅ COMPLETED                     │
│     ├─ Good Output: 495 pcs (99% yield)                         │
│     └─ Transfer to Sewing Baju: ✅ Done                         │
│                                                                  │
│  🔹 Embroidery Department (Body only - Optional):               │
│  └─ EMB-2026-00089 (Body Embroidery)                           │
│     ├─ Target: 495 pcs (all Body parts)                         │
│     ├─ Actual: 495/495 (100%) ✅ COMPLETED                     │
│     ├─ Good Output: 495 pcs (100% yield)                        │
│     └─ Transfer to Sewing Body: ✅ Done                         │
│                                                                  │
│  🔹 Sewing Department (2 Parallel Streams):                     │
│  ├─ SEW-BODY-2026-00120 (Boneka Body Assembly)                 │
│  │  ├─ Target: 517 pcs (with +15% buffer)                      │
│  │  ├─ Actual: 520/517 (100.6%) ✅ COMPLETED                  │
│  │  ├─ Good Output: 508 pcs (yield: 97.7%)                     │
│  │  ├─ Defect: 12 pcs → Rework: 10 pcs recovered ✅           │
│  │  ├─ Final Good Output: 518 pcs (508+10)                     │
│  │  └─ Transfer to Finishing (Skin): ✅ Done                   │
│  │                                                              │
│  └─ SEW-BAJU-2026-00121 (Baju Assembly)                        │
│     ├─ Target: 495 pcs (with +10% buffer)                       │
│     ├─ Actual: 500/495 (101%) ✅ COMPLETED                     │
│     ├─ Good Output: 495 pcs (99% yield)                         │
│     ├─ After Minor Rework: 500 pcs                              │
│     └─ Transfer to Hold (wait Packing): ✅ Done                 │
│                                                                  │
│  🔹 Finishing Department (2-Stage Process):                     │
│  ├─ FIN-STG1-2026-00045 (Stuffing - Stage 1)                   │
│  │  ├─ Target: 480 pcs (demand-driven)                         │
│  │  ├─ Actual: 483/480 (100.6%) ✅ COMPLETED                  │
│  │  ├─ Good Output: 473 pcs (97.9% yield)                      │
│  │  ├─ After Rework: 481 pcs Stuffed Body                      │
│  │  └─ Transfer to Stage 2: ✅ Done                            │
│  │                                                              │
│  └─ FIN-STG2-2026-00046 (Closing - Stage 2)                    │
│     ├─ Target: 470 pcs                                          │
│     ├─ Actual: 472/470 (100.4%) ✅ COMPLETED                   │
│     ├─ Good Output: 468 pcs (99.2% yield)                       │
│     ├─ After Rework: 471 pcs Finished Doll                      │
│     └─ Transfer to Packing: ✅ Done                             │
│                                                                  │
│  🔹 Packing Department (Final Assembly):                        │
│  └─ PACK-2026-00089 (Final Packing)                            │
│     ├─ Target: 465 pcs (urgency-based, exact)                   │
│     ├─ Constraint: MIN(Doll: 471, Baju: 500) = 471 pcs max     │
│     ├─ Actual: 466/465 (100.2%) ✅ COMPLETED                   │
│     ├─ Packed Sets: 465 pcs (1 boneka + 1 baju each)           │
│     ├─ Output: 8 CTN (7×60 + 1×45 pcs)                         │
│     ├─ Surplus: Doll +6 pcs, Baju +35 pcs (future stock)       │
│     └─ Transfer to FG Warehouse: ✅ Done                        │
│                                                                  │
│  🎯 MO Fulfillment Analysis:                                    │
│  • Min(Body: 518, Baju: 500) = 500 complete sets possible      │
│  • MO Target: 450 pcs                                           │
│  • Achievement: 465/450 (103.3%) ✅ SURPLUS 15 pcs             │
│  • Extra Stock: Body +6, Baju +35 (for future orders)          │
│  • Overall Yield: 94.1% (465 from 495 initial cut)             │
│                                                                  │
│  💡 Performance Insights:                                       │
│  ├─ Total SPKs: 10 SPKs (all departments)                      │
│  ├─ All Completed: ✅ 100% completion rate                     │
│  ├─ Total Production: 1,018 pcs across all depts               │
│  ├─ Total Defects: 41 pcs (4.0%)                               │
│  ├─ Rework Recovery: 34 pcs (82.9% success) ✅                 │
│  ├─ Net Waste: 7 pcs (0.7% scrap) ✅ Excellent                 │
│  └─ On-Time Delivery: Week 05 ✅ ACHIEVED                      │
│                                                                  │
│  [GENERATE MO REPORT] [CLOSE MO] [EXPORT ANALYSIS]             │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features**:
- ✅ Aggregate monitoring: Total dari semua SPK vs MO Target
- ✅ Cascade visualization: Lihat flow dari Cutting sampai Packing
- ✅ Constraint validation: Packing tidak bisa exceed MIN(Body, Baju)
- ✅ Surplus tracking: Extra stock automatically recorded
- ✅ Completion gate: MO hanya bisa closed jika ≥ Target
- ✅ Performance insights: Overall yield, defect rate, recovery rate

---

### 4.3 Data pada Schedule Setiap Departemen Production

**Detail fields untuk setiap SPK**:

```
┌─────────────────────────────────────────────────────────────┐
│  SPK DETAIL VIEW                                            │
├─────────────────────────────────────────────────────────────┤
│  🆔 SPK Identity                                            │
│  ├─ No SPK: SEW-2026-00120 (Auto-generate per dept)        │
│  ├─ Kode Work Order (WO): WO-SEW-2026-00120                │
│  ├─ No MO: MO-2026-00089 (Trigger dari MO)                 │
│  └─ Status: 🔄 In Progress / ✅ Completed                  │
│                                                             │
│  🎯 Article Information                                     │
│  ├─ No/Kode Article: 40551542 (Trigger dari Masterdata)    │
│  ├─ Nama Article: AFTONSPARV soft toy with suit            │
│  └─ Buyer: IKEA                                             │
│                                                             │
│  🏭 Department Information                                  │
│  ├─ Kode Departemen: SEW                                    │
│  ├─ Nama Departemen: Sewing Body                           │
│  └─ Line/Team: Line 1 & Line 2                             │
│                                                             │
│  📊 Production Target & Progress                            │
│  ├─ 🆕 MO Target: 450 pcs (Base requirement)               │
│  ├─ 🆕 SPK Target: 517 pcs (with +15% buffer)              │
│  ├─ Actual Production: 520 pcs (100.6%) ✅                 │
│  ├─ Good Output: 508 pcs (97.7% yield)                     │
│  ├─ Defect: 12 pcs (2.3%)                                  │
│  ├─ Rework: 10 pcs recovered (83.3% recovery) ✅           │
│  ├─ Scrap: 2 pcs (0.4%)                                    │
│  ├─ Final Output: 518 pcs (Good + Rework)                  │
│  └─ UoM Article: PCS                                        │
│                                                             │
│  📦 Material Requirements (Trigger dari BOM)                │
│  ├─ Material 1: [IKHR504] KOHAIR D.BROWN                   │
│  │  ├─ Qty Required: 52.04 YARD (517 × 0.1005)            │
│  │  ├─ Qty Actual Used: 52.26 YARD                         │
│  │  ├─ Variance: +0.22 YD (+0.4%) ✅ OK                    │
│  │  └─ UoM Material: YARD                                   │
│  │                                                          │
│  ├─ Material 2: Thread Brown                               │
│  │  ├─ Qty Required: 280 CM/pcs × 517 = 144,760 CM        │
│  │  ├─ Actual Used: 145,600 CM                             │
│  │  └─ UoM: CM                                              │
│  │                                                          │
│  └─ ... (other materials from BOM)                          │
│                                                             │
│  📅 Timeline                                                │
│  ├─ Tanggal Schedule Production: 2 Jan 2026                │
│  ├─ Tanggal Mulai Produksi: 3 Jan 2026                     │
│  ├─ Tanggal Target Selesai: 7 Jan 2026 (5 hari kerja)     │
│  ├─ Tanggal Aktual Selesai: 6 Jan 2026 ✅ EARLY           │
│  └─ Lead Time: 4 hari (target: 5 hari)                     │
│                                                             │
│  🔄 Status Produksi                                         │
│  └─ Status: [Dropdown]                                      │
│     ├─ ⚪ Belum Mulai (Scheduled)                          │
│     ├─ 🔵 Sedang Produksi (In Progress)                    │
│     └─ ✅ Selesai Produksi (Completed) ← Current           │
│                                                             │
│  📝 Daily Progress Log (Auto-recap dari input harian)      │
│  ├─ 3 Jan: 105 pcs (Good: 103, Defect: 2)                  │
│  ├─ 4 Jan: 110 pcs (Good: 108, Defect: 2)                  │
│  ├─ 5 Jan: 108 pcs (Good: 105, Defect: 3)                  │
│  └─ 6 Jan: 197 pcs (Good: 192, Defect: 5)                  │
│     └─ Total: 520 pcs, Good: 508 pcs (97.7% yield)         │
│                                                             │
│  [VIEW DETAILED REPORT] [EDIT SPK] [COMPLETE & CLOSE]      │
└─────────────────────────────────────────────────────────────┘
```

---

### 4.4 Kalender Produksi Per Departemen

**Purpose**: Visualisasi jadwal produksi dalam bentuk kalender untuk monitoring.

```
┌─────────────────────────────────────────────────────────────┐
│  📅 KALENDER PRODUKSI - SEWING DEPARTMENT                   │
│  Januari 2026                                               │
├─────────────────────────────────────────────────────────────┤
│  Week 1:                                                    │
│  ┌────┬────┬────┬────┬────┬────┬────┐                      │
│  │ S  │ M  │ T  │ W  │ T  │ F  │ S  │                      │
│  ├────┼────┼────┼────┼────┼────┼────┤                      │
│  │    │    │    │ 1  │ 2  │ 3  │ 4  │                      │
│  │    │    │    │🟢  │🟢  │🟢  │🟡  │                      │
│  │    │    │    │SEW │SEW │SEW │SEW │                      │
│  │    │    │    │120 │120 │120 │120 │                      │
│  │    │    │    │105 │110 │108 │97  │ pcs/day              │
│  └────┴────┴────┴────┴────┴────┴────┘                      │
│                                                             │
│  Week 2:                                                    │
│  ┌────┬────┬────┬────┬────┬────┬────┐                      │
│  │ 5  │ 6  │ 7  │ 8  │ 9  │ 10 │ 11 │                      │
│  │🟢  │🟢  │⚪  │🟢  │🟢  │🟢  │⚪  │                      │
│  │SEW │    │    │SEW │SEW │SEW │    │                      │
│  │120 │    │    │121 │121 │121 │    │                      │
│  │100 │    │    │95  │105 │110 │    │ pcs/day              │
│  └────┴────┴────┴────┴────┴────┴────┘                      │
│                                                             │
│  Legend:                                                    │
│  • 🟢 Completed (100% daily target achieved)               │
│  • 🟡 Partial (50-99% achieved)                            │
│  • 🔴 Delayed (target not met, behind schedule)            │
│  • ⚪ Scheduled (future/not started)                       │
│  • ⚫ Holiday/No production                                │
│                                                             │
│  Quick Stats untuk Januari:                                │
│  ├─ Total Production Days: 22 days                          │
│  ├─ Completed SPK: 8 SPK ✅                                │
│  ├─ In Progress: 3 SPK 🔄                                  │
│  ├─ Scheduled: 5 SPK ⚪                                     │
│  ├─ Average Daily Output: 102 pcs/day                       │
│  └─ Efficiency: 97.5% ✅ Excellent                         │
│                                                             │
│  [VIEW LIST] [FILTER BY ARTICLE] [EXPORT CALENDAR]         │
└─────────────────────────────────────────────────────────────┘
```

**Interactive Features**:
- Click tanggal untuk lihat detail produksi hari itu
- Hover untuk preview (SPK number, target, actual)
- Color coding untuk quick status identification
- Filter by article, line, atau status
- Export ke PDF untuk management meeting

---

## 5. MASTERDATA - DETAIL SPESIFIKASI

### 5.1 Masterdata Material

**Purpose**: Central database untuk semua material (30+ unique SKU per artikel).

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE/EDIT MATERIAL MASTER                                │
├─────────────────────────────────────────────────────────────┤
│  🆔 Material Identity                                       │
│  ├─ Kode Material: [Auto-gen] IKHR504                      │
│  │  └─ Format: [Type][Category][Seq]                       │
│  │     I=IKEA, K=Kain, HR=Haar/Kohair, 504=sequence        │
│  ├─ Nama Material: [Text] *Required                         │
│  │  KOHAIR 7MM RECYCLE D.BROWN                              │
│  └─ Alias/Short Name: [Text] KOHAIR D.BROWN                 │
│                                                             │
│  📝 Material Description                                    │
│  └─ Deskripsi: [Textarea]                                   │
│     Kain kohair 7mm pile, recycled material, dark brown     │
│     color. Soft texture untuk boneka body.                  │
│                                                             │
│  📦 Material Classification                                 │
│  ├─ Jenis Material: [Dropdown] *Required                    │
│  │  ├─ Raw Material (Fabric, Thread, Filling)              │
│  │  ├─ Bahan Penolong (Label, Tag, Sticker)                │
│  │  ├─ Setengah Jadi (WIP from production dept)            │
│  │  ├─ Barang Jadi (Finished Goods)                        │
│  │  ├─ Packaging (Carton, Pallet, Pad)                     │
│  │  └─ Consumables (Thread, Glue, etc)                     │
│  │                                                          │
│  ├─ Category: [Dropdown]                                    │
│  │  Fabric → Kohair                                         │
│  │                                                          │
│  └─ Sub-Category: [Text]                                    │
│     Recycled Material                                        │
│                                                             │
│  📏 UOM (Unit of Measure)                                   │
│  ├─ Primary UOM: [Dropdown] YARD *Required                  │
│  │  └─ Options: PCS, YARD, METER, KG, GRAM, CTN, etc       │
│  │                                                          │
│  ├─ Secondary UOM: [Dropdown] Optional                      │
│  │  └─ For conversion (e.g., Carton → Pcs)                 │
│  │                                                          │
│  └─ 🆕 UOM Conversion Factor: [Number]                      │
│     0.1005 YARD/pcs (for production calculation)            │
│                                                             │
│  📊 Stock Management                                        │
│  ├─ Minimum Stock: [Number] 200 YARD *Required              │
│  │  └─ Alert trigger when below this level                 │
│  ├─ Maximum Stock: [Number] 1000 YARD (Optional)            │
│  ├─ Reorder Point: [Number] 250 YARD                        │
│  │  └─ Auto-suggest PO when reach this level               │
│  └─ Safety Stock: [Number] 50 YARD (Buffer)                 │
│                                                             │
│  ⏱️ Lead Time & Cost                                        │
│  ├─ Lead Time: [Number] 14 days (from order to delivery)   │
│  ├─ Standard Cost: [Currency] $12.50 /YARD                  │
│  │  └─ For COGS calculation                                │
│  └─ Last Purchase Price: [Auto-update] $12.50 (4 Jan 26)   │
│                                                             │
│  🏢 Supplier Association                                    │
│  ├─ Primary Supplier: [Dropdown] PT Kain Sejahtera ⭐      │
│  ├─ Alternative Supplier 1: CV Textile Indo                 │
│  └─ Alternative Supplier 2: UD Kain Murah                   │
│                                                             │
│  📸 Material Image                                          │
│  └─ [Upload Image] (Max 2MB, JPG/PNG)                       │
│     [Preview thumbnail of fabric swatch]                    │
│                                                             │
│  ✅ Status                                                  │
│  └─ Active Status: [Toggle] ● Active ○ Inactive             │
│                                                             │
│  [SAVE] [SAVE & NEW] [CANCEL]                              │
└─────────────────────────────────────────────────────────────┘
```

**Material Type Explanation**:

| Jenis Material | Contoh | Karakteristik |
|----------------|--------|---------------|
| **Raw Material** | Fabric, Thread, Filling | Bahan dasar produksi, from supplier |
| **Bahan Penolong** | Label, Tag, Sticker, Hangtag | Aksesoris untuk FG, from supplier |
| **Setengah Jadi (WIP)** | Skin (from Sewing), Stuffed Body | Intermediate product, from production |
| **Barang Jadi** | Finished Doll, Complete Set | Final product, to warehouse FG |
| **Packaging** | Carton, Pallet, Pad, Plastic | For packing & shipping |
| **Consumables** | Jarum jahit, Oli mesin, Lem | Indirect material, tidak ke BOM |

---

### 5.2 Masterdata Supplier

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE/EDIT SUPPLIER MASTER                                │
├─────────────────────────────────────────────────────────────┤
│  🆔 Supplier Identity                                       │
│  ├─ Kode Supplier: [Auto-gen] SUP-2026-0001                │
│  ├─ Nama Supplier: [Text] *Required                         │
│  │  PT KAIN SEJAHTERA                                       │
│  └─ Short Name: [Text] Kain Sejahtera                       │
│                                                             │
│  📍 Address & Contact                                       │
│  ├─ Alamat Lengkap: [Textarea] *Required                    │
│  │  Jl. Industri Raya No. 45, Tangerang 15100              │
│  ├─ Kota: [Text] Tangerang                                  │
│  ├─ Provinsi: [Dropdown] Banten                             │
│  ├─ Kode Pos: [Text] 15100                                  │
│  │                                                          │
│  ├─ Contact Person: [Text] Pak Hendro (Sales Manager)       │
│  ├─ No Telp/HP: [Text] +62 21 5555 1234                     │
│  ├─ No Fax: [Text] Optional                                 │
│  └─ Email: [Email] hendro@kainsejahtera.com                 │
│                                                             │
│  🏷️ Supplier Classification                                │
│  ├─ Supplier Type: [Multi-select] *Required                 │
│  │  ☑️ Fabric (Kain)                                       │
│  │  ☐ Label & Tag                                          │
│  │  ☐ Accessories (Thread, Filling)                        │
│  │  ☐ Packaging (Carton, Pallet)                           │
│  │  ☐ Subcontractor (Embroidery, Sewing)                   │
│  │                                                          │
│  └─ Specialization: [Text]                                  │
│     Kohair, Plush, Boa fabrics - Soft toys specialist       │
│                                                             │
│  💰 Payment & Terms                                         │
│  ├─ Payment Terms: [Dropdown]                               │
│  │  ├─ COD (Cash on Delivery)                              │
│  │  ├─ Net 30 (30 days after invoice) ☑️ Selected          │
│  │  ├─ Net 60                                               │
│  │  └─ Custom: [Text field]                                 │
│  │                                                          │
│  ├─ Currency: [Dropdown] IDR (Rupiah)                       │
│  ├─ Credit Limit: [Currency] IDR 500,000,000                │
│  └─ Tax ID (NPWP): [Text] 01.234.567.8-901.000              │
│                                                             │
│  ⏱️ Lead Time & Performance                                 │
│  ├─ Standard Lead Time: [Number] 14 days                    │
│  ├─ Minimum Order Qty (MOQ): [Number] 100 YARD              │
│  │                                                          │
│  └─ 📊 Performance Rating (Auto-calculated):                │
│     ├─ Delivery On-Time: 92% ✅                             │
│     ├─ Quality Pass Rate: 97% ✅                            │
│     ├─ Price Competitiveness: 4.2/5.0 ⭐⭐⭐⭐             │
│     └─ Overall Score: 4.5/5.0 ⭐⭐⭐⭐⭐ (Excellent)        │
│                                                             │
│  📋 Notes & History                                         │
│  ├─ Internal Notes: [Textarea]                              │
│  │  Supplier andalan untuk kohair. Kualitas konsisten.     │
│  │  Harga negotiable untuk order >500 YD.                  │
│  │                                                          │
│  └─ Last Transaction: [Auto] PO-2026-00045 (4 Jan 2026)    │
│     Value: $2,450.00                                        │
│                                                             │
│  ✅ Status                                                  │
│  └─ Active Status: [Toggle] ● Active ○ Inactive             │
│                                                             │
│  [SAVE] [VIEW TRANSACTIONS] [PERFORMANCE REPORT] [CANCEL]  │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.3 Masterdata BOM - CASCADE VALIDATION

**Purpose**: BOM chain validation untuk memastikan WIP flow correct.

**BOM Cascade Example** (AFTONSPARV):

```
[CUTTING BOM]
Input: 9 Fabrics (Raw Material)
Output: Body Parts (WIP)
    ↓
    ↓ [Cascade Rule: Cutting Output = Embroidery Input]
    ↓
[EMBROIDERY BOM]
Input: Body Parts (WIP from Cutting)
Output: Embroidered Body (WIP)
    ↓
    ↓ [Cascade Rule: Embroidery Output = Sewing Input]
    ↓
[SEWING BOM]
Input: Embroidered Body (WIP from Embroidery) + 9 Threads
Output: Skin Body (WIP)
    ↓
    ↓ [Cascade Rule: Sewing Output = Finishing Input]
    ↓
[FINISHING BOM - Stage 1]
Input: Skin Body (WIP from Sewing) + Filling + Thread
Output: Stuffed Body (WIP)
    ↓
    ↓ [Cascade Rule: Stage 1 Output = Stage 2 Input]
    ↓
[FINISHING BOM - Stage 2]
Input: Stuffed Body (WIP from Stage 1) + Hang Tag
Output: Finished Doll (WIP)
    ↓
    ↓ [Cascade Rule: Finishing Output = Packing Input]
    ↓
[PACKING BOM]
Input: Finished Doll (WIP from Finishing) + Baju + Carton
Output: Complete Set (Finished Goods) ✅
```

**System Validation Rules**:

1. **Input Material Type Check**:
   - Cutting: Must use Raw Material (Fabric)
   - Mid-process: Must use WIP from previous dept
   - Final: Output must be Finished Goods

2. **Qty Consistency**:
   - Output qty dari Dept A = Input qty untuk Dept B
   - UOM must match atau ada conversion factor

3. **Routing Sequence**:
   - BOM routing harus sesuai dengan actual dept sequence
   - Cannot skip department (e.g., Cutting → Packing directly)

4. **Circular Reference Prevention**:
   - Cannot have BOM that references itself
   - Cannot have loop (A → B → A)

**Validation Alert**:

```
⚠️ BOM VALIDATION ERROR
─────────────────────────────────────────────────────
BOM: SEWING-BODY-2026-00089
Issue: Input material "Body Parts" not found in
       previous dept (Embroidery) output.

Expected: Embroidery BOM output = "Embroidered Body"
Actual: Sewing BOM input = "Body Parts"

❌ MISMATCH - Cannot save BOM

Action Required:
1. Update Sewing BOM input to match Embroidery output, OR
2. Update Embroidery BOM output to match Sewing input

[FIX NOW] [VIEW CASCADE] [CANCEL]
```

---

### 5.4 Masterdata Article

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE/EDIT ARTICLE MASTER                                 │
├─────────────────────────────────────────────────────────────┤
│  🆔 Article Identity                                        │
│  ├─ No/Kode Article: [Text] *Required                      │
│  │  40551542 (IKEA Article Number)                          │
│  ├─ Internal Code: [Auto-gen] ART-2026-00089                │
│  └─ Nama Article: [Text] *Required                          │
│     AFTONSPARV soft toy with astronaut suit, 28cm, bear     │
│                                                             │
│  📝 Description                                             │
│  └─ Deskripsi Article: [Textarea]                           │
│     Soft toy boneka beruang dengan baju astronaut.          │
│     Warna coklat tua (dark brown), tinggi 28cm.             │
│     Material kohair recycled, filling dacron.                │
│     Untuk anak usia 3+ tahun.                                │
│                                                             │
│  🏢 Buyer Information                                       │
│  ├─ Buyer: [Dropdown] IKEA                                  │
│  ├─ Buyer PO Number: [Text] Optional                        │
│  │  (untuk referensi, link ke PO Label)                    │
│  └─ Buyer Contact: [Text] buyer@ikea.com                    │
│                                                             │
│  🎨 Product Classification                                  │
│  ├─ Category: [Dropdown] Soft Toys                          │
│  ├─ Sub-Category: [Dropdown] Bear                           │
│  ├─ Size: [Dropdown] Medium (20-30cm)                       │
│  └─ Color: [Text] Dark Brown                                │
│                                                             │
│  📦 Packing Information                                     │
│  ├─ Standard Packing: [Number] 60 pcs/carton                │
│  │  └─ Carton Size: 570×375×450 mm                         │
│  │                                                          │
│  ├─ 🆕 UOM Conversion (Box → Pcs):                          │
│  │  ├─ Conversion Factor: [Number] 60 pcs/CTN *Required    │
│  │  ├─ Tolerance: [Number] ±2% (variance allowed)          │
│  │  └─ Validation Rule: Auto-check saat FG receiving       │
│  │                                                          │
│  ├─ Pallet Configuration:                                   │
│  │  ├─ Cartons per Pallet: 8 CTN                           │
│  │  └─ Pcs per Pallet: 480 pcs (8 × 60)                    │
│  │                                                          │
│  └─ Gross Weight: [Number] 0.25 KG/pcs (with packaging)     │
│                                                             │
│  💰 Costing                                                 │
│  ├─ Standard Cost: [Currency] $10.00 /pcs (COGS)            │
│  ├─ Selling Price: [Currency] $25.00 /pcs                   │
│  └─ Margin: [Auto-calc] $15.00 (60%) ✅ Healthy            │
│                                                             │
│  🔗 BOM Association                                         │
│  ├─ BOM Manufacturing: [Multi-select]                       │
│  │  ├─ ☑️ BOM-CUT-AFTON-2026-001 (Cutting)                │
│  │  ├─ ☑️ BOM-EMB-AFTON-2026-001 (Embroidery)             │
│  │  ├─ ☑️ BOM-SEW-AFTON-2026-001 (Sewing)                 │
│  │  ├─ ☑️ BOM-FIN-AFTON-2026-001 (Finishing)              │
│  │  └─ ☑️ BOM-PCK-AFTON-2026-001 (Packing)                │
│  │                                                          │
│  └─ BOM Purchasing: [Select]                                │
│     BOM-PUR-AFTON-2026-001 (For material ordering)          │
│                                                             │
│  📸 Product Images                                          │
│  ├─ Main Image: [Upload] (Product photo)                    │
│  ├─ Gallery: [Upload Multiple] (Max 5 images)               │
│  └─ Technical Drawing: [Upload PDF] (Optional)              │
│                                                             │
│  ✅ Status                                                  │
│  ├─ Active: [Toggle] ● Active ○ Inactive                    │
│  └─ Production Status:                                      │
│     ├─ ○ New (Not yet produced)                            │
│     ├─ ● Active (Currently producing) ☑️                   │
│     └─ ○ Discontinued (Phased out)                         │
│                                                             │
│  [SAVE] [VIEW BOM DETAIL] [PRODUCTION HISTORY] [CANCEL]    │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.5 Masterdata Department

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE/EDIT DEPARTMENT MASTER                              │
├─────────────────────────────────────────────────────────────┤
│  🆔 Department Identity                                     │
│  ├─ Kode Departemen: [Text] SEW (max 5 char) *Required     │
│  ├─ Nama Departemen: [Text] *Required                       │
│  │  Sewing Department                                        │
│  └─ Short Name: [Text] Sewing                                │
│                                                             │
│  🏭 Department Classification                               │
│  ├─ Department Type: [Dropdown] *Required                   │
│  │  ├─ Production (Cutting, Sewing, Finishing, etc)        │
│  │  ├─ Support (Warehouse, QC, Maintenance)                │
│  │  ├─ Planning (PPIC)                                      │
│  │  └─ Management                                           │
│  │                                                          │
│  ├─ Cost Center: [Text] CC-SEW-001                          │
│  │  └─ For financial reporting & cost allocation           │
│  │                                                          │
│  └─ Location: [Dropdown]                                    │
│     ├─ Building: Gedung Produksi A                          │
│     ├─ Floor: Lantai 2                                      │
│     └─ Area: Area Sewing (300m²)                            │
│                                                             │
│  👥 Capacity & Resources                                    │
│  ├─ Capacity (Normal): [Number] 500 pcs/day                 │
│  ├─ Capacity (Max): [Number] 650 pcs/day (with OT)          │
│  ├─ Number of Lines: [Number] 3 lines                       │
│  │  ├─ Line 1: Body Assembly (15 operators)                │
│  │  ├─ Line 2: Baju Assembly (10 operators)                │
│  │  └─ Line 3: Mixed (12 operators)                        │
│  │                                                          │
│  ├─ Total Operators: [Number] 37 orang                      │
│  ├─ Supervisor: [Number] 3 orang                            │
│  └─ Shift Pattern: [Dropdown] 2 Shift (Pagi & Sore)         │
│                                                             │
│  🔄 Routing & Process Flow                                  │
│  ├─ Upstream Department (Input from):                       │
│  │  └─ [Multi-select] Cutting, Embroidery                  │
│  │                                                          │
│  ├─ Downstream Department (Output to):                      │
│  │  └─ [Multi-select] Finishing, Packing                   │
│  │                                                          │
│  └─ Process Time (Average):                                 │
│     ├─ Setup Time: 30 minutes/SPK                           │
│     ├─ Process Time: 8 minutes/pcs                          │
│     └─ Total: ~65 pcs/hour/line                             │
│                                                             │
│  💰 Cost Structure                                          │
│  ├─ Labor Cost: [Currency] $5.00 /hour                      │
│  ├─ Overhead Rate: [%] 15% of labor cost                    │
│  └─ Standard Rate: [Auto-calc] $0.67 /pcs                   │
│                                                             │
│  👤 Department Head                                         │
│  ├─ Nama: [Dropdown] Pak Agung (Supervisor Sewing)          │
│  ├─ Contact: [Text] +62 812 3456 7890                       │
│  └─ Email: [Email] agung.sewing@quty.com                    │
│                                                             │
│  ✅ Status                                                  │
│  └─ Active: [Toggle] ● Active ○ Inactive                    │
│                                                             │
│  [SAVE] [VIEW PERFORMANCE] [CANCEL]                         │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.6 Masterdata Subcontractor

```
┌─────────────────────────────────────────────────────────────┐
│  CREATE/EDIT SUBCONTRACTOR MASTER                           │
├─────────────────────────────────────────────────────────────┤
│  🆔 Subcon Identity                                         │
│  ├─ Kode Subcon: [Auto-gen] SUB-EMB-001                    │
│  ├─ Nama Subcon: [Text] *Required                           │
│  │  CV EMBROIDERY JAYA                                       │
│  └─ Short Name: Embroidery Jaya                              │
│                                                             │
│  🏷️ Service Type                                            │
│  └─ Service: [Multi-select] *Required                       │
│     ├─ ☑️ Embroidery (Bordir)                              │
│     ├─ ☐ Sewing (Jahit)                                    │
│     ├─ ☐ Cutting                                           │
│     └─ ☐ Finishing                                         │
│                                                             │
│  📍 Address & Contact

#### C. Daily Report (Auto-generated)

```
┌─────────────────────────────────────────────────────────────────┐
│  SEWING DEPARTMENT - DAILY REPORT                               │
│  Date: 3 Januari 2026                                           │
├─────────────────────────────────────────────────────────────────┤
│  📊 Production Summary:                                         │
│  • Total Units Produced: 215 pcs (across 2 active SPKs)        │
│  • Good Output: 210 pcs (97.7% yield)                          │
│  • Defects: 5 pcs (2.3%)                                       │
│                                                                  │
│  📋 SPK Breakdown:                                              │
│  ┌────────────┬────────┬──────────┬───────────┬─────────────┐  │
│  │ SPK        │ Article│ Today    │ Cumulative│ Status      │  │
│  ├────────────┼────────┼──────────┼───────────┼─────────────┤  │
│  │ SEW-00120  │ AFTON..│ 105 pcs  │ 520/517   │ ✅ Complete │  │
│  │            │        │ Good:103 │ (100.6%)  │             │  │
│  ├────────────┼────────┼──────────┼───────────┼─────────────┤  │
│  │ SEW-00121  │ KRAMIG │ 110 pcs  │ 450/600   │ 🔄 Progress │  │
│  │            │        │ Good:107 │ (75%)     │             │  │
│  └────────────┴────────┴──────────┴───────────┴─────────────┘  │
│                                                                  │
│  🔴 Issues & Actions:                                           │
│  • Mesin #3 maintenance (1 jam) - Resolved                     │
│  • Material IKHR504 running low (2 days stock) - Reorder req   │
│                                                                  │
│  [EXPORT PDF] [SEND TO MANAGER]                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Auto-generated Elements**:
- Total production per SPK
- Cumulative progress tracking
- Defect rate & yield percentage
- Issues logged (from daily notes)
- Email to Manager & PPIC

---

### 5.3 Department-Specific Features

#### CUTTING
- **UOM Conversion**: Yard (input) → Pcs (output)
- **BOM Marker**: Auto-calculate pcs dari yards (validation)
- **Parallel Streams**: Body & Baju tracked separately
- **Fabric Roll Tracking**: Which roll used for which pattern

#### EMBROIDERY (Optional)
- **Subcontract Management**: Track subcon orders
- **Quality Check**: Incoming inspection dari subcon
- **Delivery Note Integration**: Surat jalan in/out

#### SEWING
- **Highest Buffer**: +15% (manual intensive, high defect risk)
- **Line Balancing**: Multiple lines tracked separately
- **Operator Assignment**: Track performance per operator

#### 🔥 FINISHING (2-Stage Process)

**Unique Feature**: Warehouse Finishing dengan 2 internal stages.

##### Stage 1: Stuffing (Isi Kapas)

```
┌─────────────────────────────────────────────────────────────────┐
│  WAREHOUSE FINISHING - STUFFING PROCESS                         │
│  SPK-FIN-STUFF-2026-00045                                       │
├─────────────────────────────────────────────────────────────────┤
│  📦 INPUT MATERIAL:                                             │
│  • Skin (from Sewing): 518 pcs available                        │
│  • Filling (Dacron): 30 kg stock                                │
│  • Thread Closing: 500 meter stock                              │
│                                                                  │
│  🎯 TARGET (Demand-Driven):                                     │
│  • Packing Need: 465 pcs (urgent - Week 05)                    │
│  • SPK Target: 480 pcs (465 + 3% buffer)                       │
│  • Constraint: ≤ 518 pcs (Skin available)                      │
│                                                                  │
│  📊 DAILY PROGRESS:                                             │
│  [Calendar View similar to other depts]                         │
│  • Actual: 483/480 pcs (100.6%) ✅                             │
│  • Good Output: 473 pcs (97.9% yield)                          │
│  • Defect: 10 pcs (stuffing error - irregular shape)           │
│    └─ Rework: 8 pcs recovered                                  │
│  • Final: 481 pcs Stuffed Body                                 │
│                                                                  │
│  📋 MATERIAL CONSUMPTION:                                       │
│  • Skin Used: 483 pcs (from 518 available)                     │
│  • Filling Used: 26.08 kg (483 × 54g per pcs)                  │
│  • Thread Used: 290 meter (483 × 60cm per pcs)                 │
│                                                                  │
│  💾 OUTPUT STOCK:                                               │
│  • Stuffed Body: 481 pcs → Transfer to Stage 2                 │
│  • Remaining Skin: 35 pcs (518 - 483) → Hold in warehouse      │
│                                                                  │
│  [COMPLETE STUFFING] → Trigger Stage 2                          │
└─────────────────────────────────────────────────────────────────┘
```

##### Stage 2: Closing (Final Touch)

```
┌─────────────────────────────────────────────────────────────────┐
│  WAREHOUSE FINISHING - CLOSING PROCESS                          │
│  SPK-FIN-CLOSE-2026-00046                                       │
├─────────────────────────────────────────────────────────────────┤
│  📦 INPUT MATERIAL:                                             │
│  • Stuffed Body (from Stage 1): 481 pcs available               │
│  • Hang Tag: 500 pcs stock                                      │
│                                                                  │
│  🎯 TARGET:                                                     │
│  • Packing Need: 465 pcs (match urgency)                       │
│  • SPK Target: 470 pcs                                          │
│  • Constraint: ≤ 481 pcs (Stuffed Body available)              │
│                                                                  │
│  📊 DAILY PROGRESS:                                             │
│  • Actual: 472/470 pcs (100.4%) ✅                             │
│  • Good Output: 468 pcs (99.2% yield)                          │
│  • Defect: 4 pcs (minor - hangtag position error)              │
│    └─ Rework: 3 pcs fixed instantly                            │
│  • Final: 471 pcs Finished Doll                                │
│                                                                  │
│  💾 OUTPUT:                                                     │
│  • Finished Doll: 471 pcs → Transfer to PACKING                │
│  • Extra Stuffed Body: 9 pcs (481 - 472) → Hold for next order │
│                                                                  │
│  [COMPLETE CLOSING] → Release to Packing                        │
└─────────────────────────────────────────────────────────────────┘
```

**Key Benefits 2-Stage Finishing**:
- ✅ **Separate Stock Tracking**: Skin vs Stuffed Body inventory clear
- ✅ **Material Consumption Accurate**: Track filling/kapas usage precisely
- ✅ **Demand-Driven**: Adjust target based on Packing urgency (not rigid MO)
- ✅ **Quality Gate**: Each stage has own QC checkpoint
- ✅ **Buffer Stock**: Extra output creates safety stock for future

#### PACKING
- **Urgency-Based Target**: Exact match shipping requirement (no buffer)
- **Set Completion Logic**: MIN(Finished Doll, Baju) = Max packed sets
- **Barcode Integration**: Scan-to-pack verification
- **Carton Configuration**: Auto-calculate 60pcs/ctn standard

---

### 5.4 🔥 REWORK/REPAIR MODULE

**Integration**: Connected ke setiap departemen untuk defect recovery.

#### A. Defect Capture (During Daily Input)

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT PRODUKSI HARIAN - SEWING                                 │
│  SPK-SEW-00120 | Tanggal: 3 Jan 2026                           │
├─────────────────────────────────────────────────────────────────┤
│  • Production Quantity: 105 pcs                                 │
│  • Good Output (QC Pass): 103 pcs ✅                           │
│  • Defect Found: 2 pcs ⚠️                                      │
│                                                                  │
│  🔴 DEFECT DETAILS (Per Unit):                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Defect #1:                                                │  │
│  │ • Type: [Dropdown: Jahitan putus / Salah ukuran / ...]   │  │
│  │ • Severity: [Dropdown: Minor / Major / Critical]         │  │
│  │ • Location: [Text: Lengan kiri bawah]                    │  │
│  │ • Photo: [Upload optional]                                │  │
│  │ • Action: [Radio: Rework ● / Scrap ○]                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  → Defect auto-sent to REWORK MODULE                            │
│                                                                  │
│  [SAVE & SEND TO REWORK]                                        │
└─────────────────────────────────────────────────────────────────┘
```

#### B. Rework Station - List Rework

```
┌─────────────────────────────────────────────────────────────────┐
│  REWORK STATION - PENDING REPAIRS                               │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [All Dept ▾] [All Severity ▾] [Urgent first ▾]      │
│                                                                  │
│  ┌──────┬─────────┬────────┬──────────┬─────────┬──────────┐  │
│  │ ID   │ From    │ Article│ Defect   │ Severity│ Status   │  │
│  ├──────┼─────────┼────────┼──────────┼─────────┼──────────┤  │
│  │ RW001│ SEWING  │ AFTON..│ Jahitan  │ Minor   │🔄 Repair │  │
│  │      │ SEW-120 │        │ putus    │         │ ing      │  │
│  ├──────┼─────────┼────────┼──────────┼─────────┼──────────┤  │
│  │ RW002│ SEWING  │ AFTON..│ Salah    │ Major   │⏳ Queue  │  │
│  │      │ SEW-120 │        │ ukuran   │         │          │  │
│  ├──────┼─────────┼────────┼──────────┼─────────┼──────────┤  │
│  │ RW003│ FINISH. │ KRAMIG │ Stuffing │ Critical│🔴 URGENT │  │
│  │      │ FIN-045 │        │ irregular│         │          │  │
│  └──────┴─────────┴────────┴──────────┴─────────┴──────────┘  │
│                                                                  │
│  [ASSIGN TO OPERATOR] [MARK COMPLETED]                          │
└─────────────────────────────────────────────────────────────────┘
```

#### C. Input Hasil Rework

```
┌─────────────────────────────────────────────────────────────────┐
│  REWORK RESULT - RW001                                          │
│  Original: SEWING - SEW-00120 - Jahitan putus                  │
├─────────────────────────────────────────────────────────────────┤
│  👷 Operator: [Dropdown: Select operator]                      │
│  • Start Time: [Auto: 09:15]                                    │
│  • End Time: [Input: 09:35]                                     │
│  • Duration: 20 minutes                                         │
│                                                                  │
│  🔧 REWORK ACTION:                                              │
│  • Action Taken: [Text: Jahit ulang dengan benang reinforced]  │
│  • Material Used:                                               │
│    - Thread: 50 cm                                              │
│  • Cost Estimate: [Auto-calc labor + material]                 │
│                                                                  │
│  ✅ RE-QC INSPECTION:                                           │
│  • QC Result: [Radio: Pass ● / Fail ○ / Scrap ○]             │
│  • QC Inspector: [Dropdown]                                     │
│  • Notes: [Text: Quality OK after repair]                      │
│                                                                  │
│  [SAVE & RETURN TO STOCK] ← If Pass                            │
│  [SEND TO SCRAP] ← If unrepairable                             │
└─────────────────────────────────────────────────────────────────┘
```

**Workflow Complete**:
```
Defect Found → Rework Queue → Assign Operator → Repair → Re-QC
                                                            ↓
                                                   Pass: Add to Good Output
                                                   Fail: Send to Scrap
```

**Benefits**:
- ✅ **Recovery Tracking**: Monitor % defect yang bisa diperbaiki
- ✅ **Cost Analysis**: COPQ (Cost of Poor Quality) per department
- ✅ **Root Cause**: Identify pattern (operator/machine/material issue)
- ✅ **Prevent Waste**: Minimize unnecessary scrap
- ✅ **Performance Metric**: Rework rate by dept → continuous improvement

---

### 5.5 Quality Control Integration

#### QC Checkpoints (Throughout Production)

```
┌─────────────────────────────────────────────────────────────────┐
│  QC INSPECTION - CHECKPOINT: SEWING OUTPUT                      │
│  SPK: SEW-00120 | Date: 3 Jan 2026                             │
├─────────────────────────────────────────────────────────────────┤
│  📦 Batch to Inspect: 105 pcs                                   │
│  • Sampling Method: [Random 10% = 11 pcs]                      │
│                                                                  │
│  🔍 INSPECTION RESULT:                                          │
│  • Pass: 103 pcs (98.1%) ✅                                    │
│  • Defect: 2 pcs (1.9%)                                        │
│    └─ RW001: Jahitan putus (Minor) → Rework                    │
│    └─ RW002: Salah ukuran (Major) → Rework                     │
│                                                                  │
│  📊 Quality Metrics:                                            │
│  • AQL Level: Pass ✅ (<2.5% defect)                           │
│  • Critical Defects: 0                                          │
│  • Major Defects: 1                                             │
│  • Minor Defects: 1                                             │
│                                                                  │
│  [APPROVE BATCH] [HOLD FOR REVIEW]                              │
└─────────────────────────────────────────────────────────────────┘
```

**Integration Points**:
- QC auto-triggered setelah department complete daily input
- Defect langsung create rework ticket
- AQL validation sebelum transfer ke department berikutnya
- Manager notification jika critical defect found

---
<a name="warehouse-inventory"></a>
## 6. WAREHOUSE & INVENTORY MODULE

### 6.1 Warehouse Structure - Complete Visualization

#### 🏢 Three Warehouse Types - End-to-End Flow

```
┌────────────────────────────────────────────────────────────────────┐
│  WAREHOUSE SYSTEM - 3 TYPES                                        │
└────────────────────────────────────────────────────────────────────┘

WAREHOUSE MAIN (Material & Components)
════════════════════════════════════════════════════════════════════

Function: Store raw materials + Cut components
Location: Building A, Floor 1

Inventory Types:
├─ RAW MATERIAL - FABRIC
│  ├─ [IKHR504] KOHAIR: 125 YD
│  ├─ [IJBR105] JS BOA: 15 YD
│  ├─ [INYR002] NYLEX BLACK: 2.5 YD
│  └─ [IPR301] POLYESTER: 450 YD
│
├─ RAW MATERIAL - THREAD
│  ├─ Thread Brown: 1,200 CM
│  ├─ Thread White: 800 CM
│  └─ Thread Black: 500 CM
│
├─ RAW MATERIAL - ACCESSORIES
│  ├─ [IKP20157] Filling: 45 kg
│  ├─ [ALB40011] Hang Tag: 0 pcs 🔴
│  ├─ [ALL40030] Label EU: 450 pcs
│  └─ [ACB30104] Carton: 18 pcs ⚠️
│
└─ SEMI-FINISHED (Cut Components)
   ├─ Cut Baju (various designs): 1,250 pcs
   └─ Cut Accessories: 850 pcs

Material Issue Process:
1. SPK-CUT requests material
2. Warehouse staff scan barcode
3. System deduct stock automatically
4. Material delivered to Cutting dept
5. Cutting input production daily


WAREHOUSE FINISHING (2-Stage Internal Conversion)
════════════════════════════════════════════════════════════════════

Function: Special warehouse for Finishing process
Location: Building A, Floor 2

Inventory Types (2 Stages):
├─ STAGE 1 INVENTORY: SKIN
│  ├─ [AFTONSPARV_WIP_SKIN]: 38 pcs
│  ├─ [VANDRING_WIP_SKIN]: 125 pcs
│  └─ [GOSIG_WIP_SKIN]: 89 pcs
│
└─ STAGE 2 INVENTORY: STUFFED BODY
   ├─ [AFTONSPARV_WIP_STUFFED]: 11 pcs
   ├─ [VANDRING_WIP_STUFFED]: 67 pcs
   └─ [GOSIG_WIP_STUFFED]: 34 pcs

Internal Process Flow:
┌─────────────────────────────────────┐
│ RECEIVE from Sewing                 │
│ ├─ Type: SKIN (sewing body, unstuff) │
│ ├─ Scan barcode                     │
│ └─ Update Stage 1 Inventory         │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ STAGE 1: STUFFING                   │
│ ├─ Issue: Skin + Filling + Thread  │
│ ├─ Process: Stuff & close           │
│ ├─ Duration: ~3 min/pcs             │
│ └─ Output: Stuffed Body             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ INTERNAL TRANSFER (No paperwork)    │
│ ├─ Deduct: Stage 1 (Skin)          │
│ ├─ Add: Stage 2 (Stuffed Body)     │
│ └─ System auto-update inventory     │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ STAGE 2: CLOSING                    │
│ ├─ Issue: Stuffed + Hang Tag       │
│ ├─ Process: Attach tag + final QC  │
│ ├─ Duration: ~2 min/pcs             │
│ └─ Output: Finished Doll            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ TRANSFER to Packing                 │
│ ├─ Deduct: Stage 2 (Stuffed)       │
│ ├─ Add: Warehouse Main (FG ready)  │
│ └─ Generate delivery note           │
└─────────────────────────────────────┘

Unique Features:
✅ Dual inventory tracking (Skin vs Stuffed)
✅ No manual paperwork for internal transfer
✅ Real-time stock validation per stage
✅ Material consumption auto-tracked
✅ Demand-driven production (not rigid MO)


WAREHOUSE FINISHED GOODS (Ready to Ship)
════════════════════════════════════════════════════════════════════

Function: Store packed finished goods
Location: Building B, Floor 1 (near loading dock)

Inventory Types:
├─ PACKED SETS (Ready to ship)
│  ├─ [40551542] AFTONSPARV: 8 CTN (465 pcs)
│  │  Week: W05-2026, Dest: Belgium
│  ├─ [00511543] VANDRING: 12 CTN (720 pcs)
│  │  Week: W06-2026, Dest: Germany
│  └─ [70401234] GOSIG: 5 CTN (300 pcs)
│     Week: W07-2026, Dest: France
│
└─ PACKING MATERIALS
   ├─ Carton 570×375: 150 pcs
   ├─ Pallet: 8 pcs
   └─ Plastic wrap: 20 rolls

Shipping Process:
1. Customer order confirmed
2. FG Warehouse pull stock by Week + Dest
3. Generate shipping document
4. Load to truck with barcode scan
5. Update stock real-time
6. Customer notified (auto email)

Storage Rules:
├─ FIFO (First In First Out)
├─ Segregate by Week & Destination
├─ Max storage: 30 days
└─ Temperature controlled: 20-25°C
```

---

### 6.2 Traditional Warehouse View

```
WAREHOUSE MAIN (Material Raw)
    ↓
WAREHOUSE PRODUCTION (WIP per Dept)
    ├─ Cutting Stock
    ├─ Embroidery Stock
    ├─ Sewing Stock
    ├─ Finishing Stock (2-stage: Skin & Stuffed Body)
    └─ Packing Stock
    ↓
WAREHOUSE FINISHED GOODS (FG Ready to Ship)
```

### 6.3 Material Warehouse - Stock Management

```
┌─────────────────────────────────────────────────────────────────┐
│  WAREHOUSE MAIN - MATERIAL STOCK                                │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [All Type ▾] [All Supplier ▾] [Critical first ▾]     │
│                                                                  │
│  ┌──────────┬────────┬───────┬────────┬─────────┬───────────┐  │
│  │ Material │ Type   │ Stock │ Min    │ Status  │ Last In   │  │
│  ├──────────┼────────┼───────┼────────┼─────────┼───────────┤  │
│  │ IKHR504  │ Fabric │ 125 YD│ 200 YD │🟡 Low   │ 2/1/26    │  │
│  │ KOHAIR.. │        │       │ (62.5%)│ Reorder │ 80 YD     │  │
│  ├──────────┼────────┼───────┼────────┼─────────┼───────────┤  │
│  │ ACB30104 │ Pack   │ 18 PCE│ 50 PCE │🔴 CRIT! │ 29/12/25  │  │
│  │ CARTON.. │        │       │ (36%)  │ Urgent  │ 25 PCE    │  │
│  ├──────────┼────────┼───────┼────────┼─────────┼───────────┤  │
│  │ IKP20157 │ Fill   │-12 KG │ 20 KG  │⚫ DEBT! │ Produksi  │  │
│  │ Filling..│        │       │        │ Risk    │ running   │  │
│  └──────────┴────────┴───────┴────────┴─────────┴───────────┘  │
│                                                                  │
│  🔴 MATERIAL DEBT ALERT:                                        │
│  • IKP20157 Filling: -12 KG                                     │
│  • Produksi tetap jalan (PO-K-2026-00012 approved with debt)   │
│  • Expected delivery: 5 Jan 2026 (2 days)                      │
│  • Action: Create urgent PO to clear debt                       │
│                                                                  │
│  [CREATE PURCHASE REQUEST] [MATERIAL IN] [MATERIAL OUT]         │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features**:
- ✅ **Color-coded Alert**: Green/Yellow/Red/Black status
- ✅ **Material Debt Tracking**: Negative stock dengan visibility
- ✅ **Reorder Point**: Auto-suggest purchase when low
- ✅ **Last Transaction**: Track material in/out history

### 6.3 Material IN (Receiving)

```
┌─────────────────────────────────────────────────────────────────┐
│  MATERIAL RECEIVING - FROM PO                                   │
├─────────────────────────────────────────────────────────────────┤
│  PO Reference: [Dropdown: Select PO]                            │
│  Selected: PO-K-2026-00012 (KAIN - AFTONSPARV)                 │
│                                                                  │
│  📦 DELIVERY INFO:                                              │
│  • Delivery Date: [Date picker]                                 │
│  • Supplier: [Auto from PO: PT Supplier A]                     │
│  • DO Number: [Input: DO-SUP-0012]                             │
│  • Received By: [Dropdown: Warehouse staff]                     │
│                                                                  │
│  📋 MATERIAL LIST (from PO):                                    │
│  ┌──────────┬────────┬─────────┬──────────┬────────────────┐  │
│  │ Material │ Code   │ PO Qty  │ Received │ Status         │  │
│  ├──────────┼────────┼─────────┼──────────┼────────────────┤  │
│  │ IKHR504  │ Fabric │ 150 YD  │[150] YD  │✅ Complete     │  │
│  │ KOHAIR..│        │         │          │                │  │
│  ├──────────┼────────┼─────────┼──────────┼────────────────┤  │
│  │ IKP20157 │ Fill   │ 60 KG   │[55] KG   │⚠️ Short 5KG   │  │
│  │ Filling..│        │         │          │ (Accept/Reject)│  │
│  └──────────┴────────┴─────────┴──────────┴────────────────┘  │
│                                                                  │
│  ⚠️ DISCREPANCY HANDLING:                                       │
│  • IKP20157: Short delivery 5 KG                                │
│  • Action: [Radio: Accept short ● / Reject partial ○]         │
│  • If Accept: Update PO status to "Partial Received"           │
│  • Notes: [Text: Supplier akan kirim sisa 5KG besok]          │
│                                                                  │
│  [CONFIRM RECEIVING] → Stock updated automatically              │
└─────────────────────────────────────────────────────────────────┘
```

**Auto Effects**:
- Stock updated in real-time
- Material debt cleared (if negative stock)
- PO status updated (Partial/Complete)
- PPIC notified (material ready for MO)

#### 🖥️ Material Receipt - Step-by-Step UI

**Step 1: Scan Barcode (Mobile/Desktop)**
```
┌─────────────────────────────────────────────────────────────┐
│  📦 MATERIAL RECEIVING - SCAN BARCODE                       │
├─────────────────────────────────────────────────────────────┤
│  📱 Scan PO Barcode atau Input Manual:                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  [PO-K-2026-00012]  🔍 SCAN                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ✅ PO Found!                                               │
│  • Supplier: PT Kain Jaya                                   │
│  • Expected: 3 Feb 2026                                     │
│  • Status: SENT (Awaiting delivery)                         │
│  • Total Items: 15 materials                                │
│                                                              │
│  [PROCEED TO RECEIVE] [CANCEL]                              │
└─────────────────────────────────────────────────────────────┘
```

**Step 2: Input Received Quantity**
```
┌─────────────────────────────────────────────────────────────┐
│  📦 RECEIVING - PO-K-2026-00012                             │
├─────────────────────────────────────────────────────────────┤
│  Progress: Material 3 of 15                                 │
│  [████████░░░░░░░░░░] 20%                                   │
│                                                              │
│  📋 Current Material:                                       │
│  • Material: [IKHR504] KOHAIR 7MM D.BROWN                  │
│  • PO Qty: 150 YARD                                         │
│                                                              │
│  ✍️ Received Quantity:                                      │
│  ┌──────────────────────────────────────────────────┐      │
│  │  [150.0] YARD                                     │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ✅ Status: EXACT MATCH (0% variance)                      │
│                                                              │
│  📸 Photo Documentation (Optional):                         │
│  [Upload Photo] 📷                                          │
│                                                              │
│  📝 Notes:                                                  │
│  ┌──────────────────────────────────────────────────┐      │
│  │ Quality checked OK, stored at Rack A3            │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  [NEXT MATERIAL →] [SKIP] [SAVE & EXIT]                    │
└─────────────────────────────────────────────────────────────┘
```

**Validation Rules**:
- ⚠️ Variance 0-5%: AUTO ACCEPT (log warning)
- ⚠️ Variance 5-10%: REQUIRE SUPERVISOR APPROVAL
- 🔴 Variance >10%: BLOCK + REQUIRE MANAGER APPROVAL + REASON
- 🔴 Short delivery: Create backorder automatically
- ✅ Over delivery: Accept + adjust PO quantity

**Step 3: Confirmation & Stock Update**
```
┌─────────────────────────────────────────────────────────────┐
│  ✅ RECEIVING COMPLETE - PO-K-2026-00012                   │
├─────────────────────────────────────────────────────────────┤
│  📊 Summary:                                                │
│  • Total Materials: 15 items                                │
│  • Exact Match: 13 items (86.7%) ✅                        │
│  • Variance: 2 items (13.3%)                                │
│    - IKHR504: +2 YD (1.3% over) ✅ Accepted               │
│    - IKP20157: -5 KG (8.3% short) ⚠️ Backorder created   │
│                                                              │
│  💰 Total Value: $5,850.00                                 │
│  📦 Storage Locations Assigned: 8 racks                    │
│                                                              │
│  🔄 System Actions (Auto):                                 │
│  ✅ Stock updated in Warehouse Main                        │
│  ✅ Material debt cleared: -12 KG → 0 KG                   │
│  ✅ PO Status: SENT → PARTIAL RECEIVED                     │
│  ✅ PPIC notified: Materials ready for MO-2026-00089       │
│  ✅ Email sent to: Purchasing A, PPIC, Manager             │
│                                                              │
│  📄 Documents Generated:                                    │
│  • GRN (Good Receipt Note): GRN-2026-00234                 │
│  • Backorder: BO-2026-00045 (5 KG Filling)                │
│                                                              │
│  [PRINT GRN] [EMAIL TO SUPPLIER] [CLOSE]                   │
└─────────────────────────────────────────────────────────────┘
```

### 6.4 Warehouse Production (WIP Tracking)

#### 🔥 Special Case: Warehouse Finishing (2-Stage Stock)

```
┌─────────────────────────────────────────────────────────────────┐
│  WAREHOUSE FINISHING - DUAL STOCK TRACKING                      │
├─────────────────────────────────────────────────────────────────┤
│  📊 STAGE 1 STOCK (Skin - After Sewing):                       │
│  ┌────────────┬──────────┬──────────┬─────────┬────────────┐  │
│  │ Article    │ From SPK │ Qty      │ Quality │ Next Stage │  │
│  ├────────────┼──────────┼──────────┼─────────┼────────────┤  │
│  │ AFTONSPARV │ SEW-00120│ 518 pcs  │ QC Pass │⏳ Pending  │  │
│  │ (Skin)     │ 3 Jan 26 │          │         │ Stuffing   │  │
│  ├────────────┼──────────┼──────────┼─────────┼────────────┤  │
│  │ KRAMIG     │ SEW-00115│ 245 pcs  │ QC Pass │⏳ Pending  │  │
│  │ (Skin)     │ 2 Jan 26 │          │         │ Stuffing   │  │
│  └────────────┴──────────┴──────────┴─────────┴────────────┘  │
│                                                                  │
│  📊 STAGE 2 STOCK (Stuffed Body - After Stuffing):             │
│  ┌────────────┬──────────┬──────────┬─────────┬────────────┐  │
│  │ Article    │ From SPK │ Qty      │ Quality │ Next Stage │  │
│  ├────────────┼──────────┼──────────┼─────────┼────────────┤  │
│  │ AFTONSPARV │ FIN-00045│ 481 pcs  │ QC Pass │⏳ Closing  │  │
│  │ (Stuffed)  │ 3 Jan 26 │          │         │            │  │
│  └────────────┴──────────┴──────────┴─────────┴────────────┘  │
│                                                                  │
│  📊 FINAL STOCK (Finished Doll - Ready to Pack):               │
│  ┌────────────┬──────────┬──────────┬─────────┬────────────┐  │
│  │ Article    │ From SPK │ Qty      │ Quality │ Status     │  │
│  ├────────────┼──────────┼──────────┼─────────┼────────────┤  │
│  │ AFTONSPARV │ FIN-00046│ 471 pcs  │ QC Pass │✅ Ready    │  │
│  │ (Finished) │ 3 Jan 26 │          │         │ to Pack    │  │
│  └────────────┴──────────┴──────────┴─────────┴────────────┘  │
│                                                                  │
│  ℹ️ Traceability: Full tracking dari Skin → Stuffed → Finished │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Clear separation: 3 distinct inventory (Skin, Stuffed, Finished)
- ✅ Demand-driven: Stage 1 target based on Packing urgency
- ✅ Material control: Track filling/kapas consumption accurately
- ✅ Traceability: From which SPK each finished doll came from

### 6.5 Warehouse Finished Goods

#### 🎯 FG Data Recording Logic

**KEY CONCEPT**: 
- **Input**: Qty sesuai dengan **MO final quantity** (dalam pcs)
- **Display**: Auto-convert ke **multiple UOMs** untuk kemudahan:
  - **Pcs** (unit dasar)
  - **Cartons** (untuk packing/shipping)
  - **Boxes** (jika applicable)
  - **Pallets** (untuk logistics)

**Example**:
```
MO-2026-00089 Final Qty: 465 pcs
└─ System Auto-Display:
   ├─ 465 pcs (primary UOM)
   ├─ 8 Cartons (7 full + 1 partial of 45 pcs)
   ├─ 0.5 Pallet (assuming 16 cartons per pallet)
   └─ Weight: 186 kg (assuming 0.4 kg per pcs)
```

#### FG Stock Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  WAREHOUSE FINISHED GOODS - READY TO SHIP                       │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [All Article ▾] [All Week ▾] [All Destination ▾]     │
│                                                                  │
│  ┌────────────┬──────────────┬────────┬────────────┬──────────┐ │
│  │ Article    │ Qty (Multi-UOM Display) │ Week/Dest  │ Status   │ │
│  ├────────────┼──────────────┼────────┼────────────┼──────────┤ │
│  │ AFTONSPARV │ 465 pcs      │ 8 CTN  │ W05 / IKEA │✅ Ready  │ │
│  │ 40551542   │ (from MO)    │7×60+45 │ Dist Ctr   │   Ship   │ │
│  │            │ = 186 kg     │0.5 PLT │            │          │ │
│  ├────────────┼──────────────┼────────┼────────────┼──────────┤ │
│  │ KRAMIG     │ 380 pcs      │ 7 CTN  │ W06 / TGT  │🔄 Partial│ │
│  │ 40499469   │ (from MO)    │6×60+20 │ Stockholm  │(Target:  │ │
│  │            │ = 152 kg     │0.4 PLT │            │600 pcs)  │ │
│  └────────────┴──────────────┴────────┴────────────┴──────────┘ │
│                                                                  │
│  [SCAN BARCODE] [SHIPMENT OUT] [PRINT LABEL]                    │
└─────────────────────────────────────────────────────────────────┘
```

#### 🔥 UOM Conversion - FG Receiving Validation

**Problem**: Box → Pcs conversion sering salah (human error).

**Solution**: Auto-validation dengan conversion factor + **record qty match MO**.

```
┌─────────────────────────────────────────────────────────────────┐
│  FG RECEIVING - FROM PACKING                                    │
│  WO/SPK: PACK-2026-00078 | Article: AFTONSPARV                 │
│  🎯 MO Target: 465 pcs (REFERENCE)                             │
├─────────────────────────────────────────────────────────────────┤
│  📦 CARTON CONFIGURATION (from BOM):                            │
│  • Standard: 60 pcs per carton                                  │
│  • Last carton can be partial (any quantity)                    │
│                                                                  │
│  📝 INPUT (Physical Count):                                     │
│  • Full Cartons: [7] CTN                                        │
│  • Partial Carton: [45] pcs                                     │
│                                                                  │
│  🔄 AUTO-CALCULATION:                                           │
│  • Calculated Total: (7 × 60) + 45 = 465 pcs ✅                │
│  • MO Final Qty: 465 pcs                                        │
│  • Match: ✅ Perfect match!                                     │
│                                                                  │
│  💾 SYSTEM RECORDS:                                             │
│  • Primary: 465 pcs (match MO)                                  │
│  • Auto-display: 8 Cartons (7 full + 1 partial)                │
│  • Auto-display: 0.5 Pallet                                     │
│  • Auto-display: 186 kg weight                                  │
│                                                                  │
│  ⚠️ VALIDATION RULES (vs MO Target):                            │
│  • If variance ≤ 10%: Yellow warning (allow with note)         │
│  • If variance > 10% AND ≤ 15%: Orange alert (SPV approval)    │
│  • If variance > 15%: 🔴 Block (recount required)              │
│                                                                  │
│  [CONFIRM RECEIVING] → FG Stock updated                         │
└─────────────────────────────────────────────────────────────────┘
```

**Example Scenarios**:

**Scenario 1: Perfect Match** ✅
- Input: 7 CTN + 45 pcs
- Calc: 465 pcs
- SPK: 465 pcs
- Result: Auto-approve

**Scenario 2: Small Variance** 🟡
- Input: 7 CTN + 40 pcs (460 pcs)
- SPK: 465 pcs
- Variance: -5 pcs (1.1%)
- Result: Warning → Require note → Approve with adjustment

**Scenario 3: Large Variance** 🔴
- Input: 6 CTN + 50 pcs (410 pcs)
- SPK: 465 pcs
- Variance: -55 pcs (11.8%)
- Result: **BLOCK** → Recount required → SPV investigation

**Benefits**:
- ✅ Prevent inventory chaos sejak awal
- ✅ Auto-detect counting error
- ✅ Audit trail untuk discrepancy
- ✅ Reduce customer complaint (wrong quantity)

---

<a name="rework-qc"></a>
## 7. REWORK & QUALITY CONTROL MODULE

### 7.1 Quality Control - 4 Critical Checkpoints

PT Quty Karunia menerapkan **4 QC Checkpoint** strategis untuk memastikan kualitas produk dari hulu ke hilir.

#### 📋 QC 4-Checkpoint Complete Visualization

```
┌────────────────────────────────────────────────────────────────────┐
│  QUALITY CONTROL - 4 CRITICAL CHECKPOINTS                          │
└────────────────────────────────────────────────────────────────────┘

CHECKPOINT 1: AFTER CUTTING
════════════════════════════════════════════════════════════════════
Location: Cutting Department Exit
Inspector: QC Staff A (Random sampling 10%)

Check Items:
├─ Size accuracy (±2mm tolerance)
├─ Edge cutting quality (no fray)
├─ Pattern alignment (matching marks)
└─ Quantity verification

Input: 500 pcs Cut Body
Sample: 50 pcs (10%)
Result:
├─ PASS: 48 pcs (96%) ✅
├─ MINOR: 2 pcs (4%) → Mark for careful sewing
└─ REJECT: 0 pcs

Action: Release to Embroidery


CHECKPOINT 2: AFTER SEWING
════════════════════════════════════════════════════════════════════
Location: Sewing Department Exit
Inspector: QC Staff B (100% inline inspection)

Check Items:
├─ Stitch quality (no loose thread)
├─ Stitch per inch (SPI) standard
├─ Seam strength (pull test)
├─ Assembly accuracy (all parts attached)
└─ Appearance (no wrinkle)

Input: 520 pcs Sewn Body
Inspection Result:
├─ PASS: 508 pcs (97.7%) ✅ → To Finishing
├─ MINOR DEFECT: 10 pcs (1.9%) → Rework queue
│  └─ Issues: Loose thread, misaligned stitch
├─ MAJOR DEFECT: 2 pcs (0.4%) → Scrap
│  └─ Issues: Broken seam, wrong assembly
└─ REWORK SUCCESS: 10 → 10 recovered (100%) ✅

Final Output: 518 pcs Good


CHECKPOINT 3: AFTER FINISHING
════════════════════════════════════════════════════════════════════
Location: Warehouse Finishing Exit (Stage 2)
Inspector: QC Staff C (100% inspection)

Check Items:
├─ Stuffing quality (firmness check)
├─ Shape consistency (no deform)
├─ Closing quality (hidden stitches)
├─ Hang tag attachment (secure)
├─ Cleanliness (no dust/stain)
└─ Safety check (no sharp edges)

Input: 472 pcs Finished Doll
Inspection Result:
├─ PASS: 468 pcs (99.2%) ✅ → To Packing
├─ MINOR DEFECT: 4 pcs (0.8%) → Quick fix
│  └─ Issues: Hang tag loose, minor stain
├─ MAJOR DEFECT: 0 pcs
└─ REWORK SUCCESS: 4 → 3 recovered (75%)

Final Output: 471 pcs Good


CHECKPOINT 4: PRE-PACKING FINAL
════════════════════════════════════════════════════════════════════
Location: Packing Department Entry
Inspector: QC Staff D (Random + 100% visual)

Check Items:
├─ Final appearance (overall quality)
├─ Baju fit test (boneka + baju assembly)
├─ Label check (correct Week + Destination)
├─ Compliance check (EU safety standards)
└─ Metal detector test (no needle)

Input: 471 Finished Doll + 500 Baju
Inspection Result:
├─ Finished Doll: 471 pcs PASS ✅
├─ Baju: 500 pcs PASS ✅
├─ Assembly Test: 20 samples - All OK ✅
└─ Metal Detector: All PASS ✅

Action: Release for Packing

───────────────────────────────────────────────────────────────────

📊 OVERALL QC PERFORMANCE:

Total Inspection Points: 4 checkpoints
Total Units Inspected: 1,963 pcs (sum of all stages)
Overall Defect Rate: 4.0%
Recovery Rate: 82.9% ✅ (Target: >80%)
Scrap Rate: 0.7% (Target: <2%)

Status: QUALITY STANDARD MET ✅
```

#### 🖥️ QC Checkpoint UI - Input Form

```
┌─────────────────────────────────────────────────────────────────┐
│  QC INSPECTION - CHECKPOINT 2 (AFTER SEWING)                    │
│  SPK: SEW-BODY-2026-00120 | Artikel: AFTONSPARV                │
├─────────────────────────────────────────────────────────────────┤
│  👤 Inspector: [Dropdown] QC Staff B (Ibu Siti)                 │
│  📅 Inspection Date: [Date] 5 Feb 2026                          │
│  ⏰ Time: [Time] 14:30 WIB                                      │
│                                                                  │
│  📦 Batch Information:                                          │
│  • Batch Date: 5 Feb 2026                                       │
│  • Quantity to Inspect: [Input] 520 pcs                         │
│  • Sampling Method: [Radio] ● 100% Inline ○ Random 10%         │
│                                                                  │
│  ✅ INSPECTION RESULT:                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ✅ PASS (Good Quality):                                   │  │
│  │    Quantity: [Input] 508 pcs                              │  │
│  │    Action: → Transfer to Finishing                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ ⚠️ MINOR DEFECT (Repairable):                            │  │
│  │    Quantity: [Input] 10 pcs                               │  │
│  │    Defect Type: [Multi-select]                            │  │
│  │    ☑️ Loose thread                                        │  │
│  │    ☑️ Misaligned stitch                                   │  │
│  │    ☐ Puckering                                            │  │
│  │    Action: → Send to Rework Station                       │  │
│  │                                                            │  │
│  │    Photos: [Upload] 📷 (3 photos attached)               │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 🔴 MAJOR DEFECT (Scrap):                                 │  │
│  │    Quantity: [Input] 2 pcs                                │  │
│  │    Defect Type: [Multi-select]                            │  │
│  │    ☑️ Broken seam                                         │  │
│  │    ☑️ Wrong assembly                                      │  │
│  │    ☐ Fabric tear                                          │  │
│  │    Action: → Scrap (cannot repair)                        │  │
│  │                                                            │  │
│  │    Root Cause: [Dropdown] Operator error                  │  │
│  │    Operator ID: [Select] OP-SEW-023                       │  │
│  │    Machine ID: [Select] SEW-LINE-02                       │  │
│  │    Notes: [Text] Operator baru, perlu training            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📊 Summary:                                                    │
│  • Total Inspected: 520 pcs (100%)                              │
│  • Pass Rate: 97.7% ✅ (Target: >95%)                          │
│  • Defect Rate: 2.3% (Target: <5%)                             │
│  • To Rework: 10 pcs (1.9%)                                     │
│  • To Scrap: 2 pcs (0.4%)                                       │
│                                                                  │
│  [SUBMIT INSPECTION] → Auto-create Rework Order for 10 pcs     │
│  [SAVE DRAFT] [CANCEL]                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

### 7.2 Rework/Repair Module - Complete Workflow

#### 📋 Rework Module Visualization

```
┌────────────────────────────────────────────────────────────────────┐
│  REWORK/REPAIR MODULE - DEFECT MANAGEMENT SYSTEM                   │
└────────────────────────────────────────────────────────────────────┘

DEFECT DETECTED → QC INSPECTION → REWORK QUEUE → RE-QC → PASS/SCRAP

Example: Sewing Defects (12 pcs)

Step 1: DEFECT CAPTURE (Auto by QC)
────────────────────────────────────────
┌──────────────────────────────────────┐
│ DEFECT RECORD #D-2026-0156-001       │
│                                      │
│ SPK: SPK-SEW-BODY-2026-00156         │
│ Batch Date: 05-Feb-2026              │
│ QC Inspector: Staff B                │
│                                      │
│ Defect Details:                      │
│ ├─ Qty: 12 pcs                      │
│ ├─ Type: MINOR (10 pcs)             │
│ │  └─ Issue: Loose thread, gap      │
│ └─ Type: MAJOR (2 pcs)              │
│    └─ Issue: Broken seam             │
│                                      │
│ Root Cause (Operator Input):        │
│ ├─ Machine tension issue            │
│ ├─ Operator: OP-SEW-023             │
│ └─ Machine: SEW-LINE-02              │
│                                      │
│ Decision:                            │
│ ├─ REWORK: 10 pcs → Queue #RW-001   │
│ └─ SCRAP: 2 pcs → Waste bin         │
└──────────────────────────────────────┘

Step 2: REWORK QUEUE ASSIGNMENT
────────────────────────────────────────
┌──────────────────────────────────────┐
│ REWORK QUEUE #RW-001                 │
│                                      │
│ Priority: HIGH (urgent MO)           │
│ Assigned to: Rework Specialist A    │
│ Est. Time: 2 hours (10 pcs)         │
│                                      │
│ Rework SOP:                          │
│ ├─ 1. Unstitch defect area          │
│ ├─ 2. Re-stitch dengan mesin khusus │
│ ├─ 3. Trim loose threads             │
│ └─ 4. Submit to Re-QC                │
│                                      │
│ Status: IN PROGRESS ⏳               │
└──────────────────────────────────────┘

Step 3: RE-QC INSPECTION
────────────────────────────────────────
┌──────────────────────────────────────┐
│ RE-QC INSPECTION                     │
│                                      │
│ Rework Batch: #RW-001 (10 pcs)      │
│ Inspector: QC Staff B                │
│                                      │
│ Re-inspection Result:                │
│ ├─ PASS: 10 pcs (100%) ✅           │
│ ├─ FAIL: 0 pcs                      │
│ └─ Recovery Rate: 100%               │
│                                      │
│ Cost Analysis:                       │
│ ├─ Rework Cost: $100 (10 × $10)    │
│ ├─ vs Scrap Cost: $400 (10 × $40)  │
│ └─ Savings: $300 💰                 │
│                                      │
│ Action: Add back to Good Output     │
└──────────────────────────────────────┘

Step 4: SYSTEM UPDATE (Auto)
────────────────────────────────────────
SPK-SEW-BODY-2026-00156 Updated:

├─ Total Production: 520 pcs
├─ Initial Good: 508 pcs
├─ Defect: 12 pcs
│  ├─ Rework Success: +10 pcs ✅
│  └─ Scrap: -2 pcs
└─ Final Good Output: 518 pcs (508 + 10)

───────────────────────────────────────────────────────────────────

📊 REWORK MODULE DASHBOARD (Monthly):

Total Defects: 127 pcs
├─ Reworked: 98 pcs
├─ Recovery Success: 87 pcs (88.8%) ✅
├─ Recovery Fail: 11 pcs → Scrap
└─ Direct Scrap: 29 pcs

COPQ (Cost of Poor Quality):
├─ Rework Cost: $980
├─ Scrap Cost: $1,600 (40 × $40)
├─ Total COPQ: $2,580
└─ Savings from Rework: $2,480 💰

Top Defect Types:
1. Loose thread (45 cases)
2. Stitch misalignment (32 cases)
3. Stuffing uneven (21 cases)

Action Plan:
├─ Retrain operators with high defect rate
├─ Maintenance schedule for problematic machines
└─ Update SOP for critical processes
```

#### 🖥️ Rework Station UI

```
┌─────────────────────────────────────────────────────────────────┐
│  REWORK STATION - DASHBOARD                                     │
├─────────────────────────────────────────────────────────────────┤
│  📊 Today's Rework Queue: 15 items                              │
│  • HIGH Priority: 5 items (urgent MO) 🔴                        │
│  • NORMAL Priority: 10 items                                     │
│                                                                  │
│  ┌──────────┬─────────┬────────┬──────────┬────────┬────────┐  │
│  │ Rework # │ SPK     │ Defect │ Qty      │ Assign │ Status │  │
│  ├──────────┼─────────┼────────┼──────────┼────────┼────────┤  │
│  │ RW-001   │SEW-00120│ Loose  │ 10 pcs   │ Spec-A │🔄 PROG│  │
│  │          │         │ thread │          │        │ 6/10   │  │
│  ├──────────┼─────────┼────────┼──────────┼────────┼────────┤  │
│  │ RW-002   │FIN-00089│ Uneven │ 4 pcs    │ Spec-B │⏳ WAIT│  │
│  │          │         │ stuff  │          │        │        │  │
│  └──────────┴─────────┴────────┴──────────┴────────┴────────┘  │
│                                                                  │
│  [INPUT REWORK RESULT] [VIEW HISTORY] [COPQ REPORT]            │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT REWORK RESULT - RW-001                                   │
│  SPK: SEW-BODY-00120 | Defect: Loose thread | Qty: 10 pcs     │
├─────────────────────────────────────────────────────────────────┤
│  👤 Rework By: [Dropdown] Rework Specialist A                   │
│  📅 Rework Date: [Date] 5 Feb 2026                              │
│  ⏱️ Time Spent: [Number] 2.5 hours                             │
│                                                                  │
│  📝 Rework Process:                                             │
│  [Checklist]                                                    │
│  ☑️ Unstitch defect area                                        │
│  ☑️ Re-stitch dengan mesin khusus                               │
│  ☑️ Trim loose threads                                          │
│  ☑️ Quality check before Re-QC                                  │
│                                                                  │
│  ✅ REWORK RESULT:                                              │
│  • Success (Pass Re-QC): [Input] 10 pcs ✅                     │
│  • Failed (Still defect): [Input] 0 pcs                         │
│  • Recovery Rate: 100% (Target: >80%)                           │
│                                                                  │
│  💰 Cost Tracking:                                              │
│  • Labor Cost: $10/pcs × 10 = $100                              │
│  • Material Cost: $5 (thread, supplies)                         │
│  • Total Rework Cost: $105                                      │
│  • Avoided Scrap Cost: $400 (10 × $40)                          │
│  • Net Savings: $295 💰                                         │
│                                                                  │
│  📸 Photos: [Upload] Before/After (Optional)                    │
│  📝 Notes: [Text] All defects successfully repaired             │
│                                                                  │
│  [SUBMIT FOR RE-QC] → Auto-notify QC Staff                     │
│  [SAVE DRAFT] [CANCEL]                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

<a name="masterdata"></a>


<a name="bom-dual-system"></a>
## 🔄 SISTEM DUAL-BOM (BOM Produksi + BOM Purchasing)

### Konsep Baru (February 6, 2026)

PT Quty Karunia menggunakan **2 jenis BOM yang terpisah** untuk 2 keperluan berbeda:

```
┌─────────────────────────────────────────────────────────┐
│  ARTIKEL (Finished Good - IKEA Soft Toys)               │
│  Contoh: AFTONSPARV Bear (40551542)                     │
└──────┬───────────────────────┬──────────────────────────┘
       │                       │
       ▼                       ▼
┌──────────────────┐    ┌─────────────────────┐
│ BOM PRODUKSI     │    │ BOM PURCHASING      │
│ (Proses)         │    │ (Material)          │
├──────────────────┤    ├─────────────────────┤
│ Per Departemen:  │    │ Total Material RAW: │
│ - Cutting        │    │ - KOHAIR 0.15 YD    │
│ - Embo           │    │ - BOA 0.0015 YD     │
│ - Sewing         │    │ - Filling 54 GRAM   │
│ - Finishing      │    │ - Thread 60 CM      │
│ - Packing        │    │ - Label 1 PCE       │
│                  │    │ - Carton 0.0167 PCE │
│ Termasuk WIP     │    │                     │
│ (internal flow)  │    │ TANPA WIP!          │
└──────────────────┘    └─────────────────────┘
       │                       │
       ▼                       ▼
   PPIC/PRODUKSI           PURCHASING
   - Edit MO/SPK            - Create PO
   - Alokasi Material       - Calculate Needs
   - Tracking WIP           - Supplier Sourcing
```

### BOM PRODUKSI (Process-Oriented)

**Tujuan**: Menunjukkan alur manufaktur step-by-step per departemen

**Contoh Flow AFTONSPARV Bear**:

```
STAGE 1 - CUTTING:
Input:  [IKHR504] KOHAIR 0.15 YARD
        [IJBR105] BOA 0.0015 YARD
Output: AFTONSPARV_WIP_CUTTING (potongan kain)

↓

STAGE 2 - SEWING:
Input:  AFTONSPARV_WIP_CUTTING (dari stage 1)
        [ATR10400] Thread 60 CM
        [ALL40030] Label 1 PCE
Output: AFTONSPARV_WIP_SKIN (kulit jahit, belum isi)

↓

STAGE 3 - FINISHING (Stuffing):
Input:  AFTONSPARV_WIP_SKIN (dari stage 2)
        [IKP20157] Filling 54 GRAM
Output: AFTONSPARV_WIP_BONEKA (boneka isi kapas)

↓

STAGE 4 - PACKING:
Input:  AFTONSPARV_WIP_BONEKA 60 PCS
        [ACB30104] Carton 1 PCE
Output: [40551542] AFTONSPARV Bear FINISHED GOODS
```

**Digunakan oleh**:
- **PPIC**: Explosion MO ke SPK per departemen
- **Departemen Produksi**: Material request sesuai stage mereka
- **Warehouse**: Tracking WIP antar departemen
- **Costing**: Hitung biaya per departemen

**Database**: `bom_production_headers` + `bom_production_details`

**Data**: 5,845 baris BOM dari 6 file Excel (Cutting, Embo, Sewing, Finishing, FG, Packing)

---

### BOM PURCHASING (Material-Oriented)

**Tujuan**: Menunjukkan HANYA material RAW yang perlu dibeli (tanpa WIP internal)

**Contoh untuk AFTONSPARV Bear** (per 1 PCE):

```
Material RAW yang harus dibeli:
├─ [IKHR504] KOHAIR Fabric: 0.15 YARD
├─ [IJBR105] BOA Fabric: 0.0015 YARD
├─ [IKP20157] Filling HCS: 54 GRAM
├─ [ATR10400] Thread Nilon: 60 CM
├─ [ALL40030] Label RPI: 1 PCE
├─ [ALB40011] Hang Tag: 1 PCE
└─ [ACB30104] Carton: 0.0167 PCE

Total: 7 material RAW (TIDAK ada WIP_CUTTING, WIP_SKIN, dll)
```

**Digunakan oleh**:
- **Purchasing**: Kalkulasi kebutuhan material untuk PO
- **Inventory Planning**: Material Requirement Planning (MRP)
- **Procurement**: Sourcing supplier, lead time planning

**Database**: `bom_purchasing_headers` + `bom_purchasing_details`

**Data**: AUTO-GENERATED dari BOM Produksi (filter `material_type = 'RAW_MATERIAL'`)

---

### Navigasi & UI

**PPIC Module** - Tambahkan menu baru:
```
PPIC Dashboard
├─ Manufacturing Orders
├─ ⭐ BOM Produksi (BARU) ← View by department
│  ├─ Filter by Article
│  ├─ Filter by Department
│  └─ Explode untuk generate SPK
├─ Work Orders (SPK)
└─ Material Allocation
```

**Purchasing Module** - Tambahkan menu baru:
```
Purchasing Dashboard
├─ Purchase Orders
├─ ⭐ BOM Purchasing (BARU) ← Material view only
│  ├─ Filter by Article
│  ├─ Calculate Material Needs (qty × BOM)
│  └─ Generate PO from calculation
├─ Supplier Management
└─ Material Request
```

**Masterdata Module** - Update:
```
Masterdata
├─ Products & Materials
├─ BOM Management
│  ├─ BOM Produksi (by dept) ← Can edit
│  ├─ BOM Purchasing (aggregated) ← Auto-generated, read-only
│  └─ Sync BOM (trigger re-generation)
└─ Bulk Import
   └─ Upload BOM Production Excel (6 files)
```

---

### API Endpoints

**BOM Production**:
```
GET  /api/v1/bom-production?article_id=X&department_id=Y
POST /api/v1/bom-production
PUT  /api/v1/bom-production/{id}
GET  /api/v1/bom-production/explode/{article_id}

POST /api/v1/imports/bom-production?department=cutting
```

**BOM Purchasing**:
```
GET  /api/v1/bom-purchasing?article_id=X
POST /api/v1/bom-purchasing/generate-from-production
GET  /api/v1/bom-purchasing/calculate-needs/{article_id}?qty=500
```

---

### Keuntungan Sistem Dual-BOM

| Aspek | Sebelum (Single BOM) | Sesudah (Dual-BOM) |
|-------|----------------------|---------------------|
| **Purchasing View** | Lihat WIP components (bingung) | Hanya RAW materials (jelas!) |
| **PPIC Explosion** | Susah filter per dept | Otomatis per dept |
| **Material Calculation** | Manual filter RAW | Auto-aggregated |
| **Akurasi** | 80-85% (human error) | 99%+ (system-calculated) |
| **Waktu Explosion** | 15-20 menit | 5 menit (-70%) |

**Referensi Lengkap**: [DUAL_BOM_SYSTEM_IMPLEMENTATION.md](../DUAL_BOM_SYSTEM_IMPLEMENTATION.md)

---


## 8. MASTERDATA MODULE

### 7.1 Material Master

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTERDATA MATERIAL                                            │
│  (Superadmin, Supervisor, Direktur, Developer Only)             │
├─────────────────────────────────────────────────────────────────┤
│  [CREATE NEW MATERIAL] [IMPORT FROM EXCEL] [EXPORT]            │
│                                                                  │
│  Filter: [All Type ▾] [Active only ✓] [Search...]             │
│                                                                  │
│  ┌─────────┬───────────┬──────┬──────┬─────────┬──────────┬──┐│
│  │ Code    │ Name      │ Type │ UoM  │ Min Stk │ Supplier │⚙️││
│  ├─────────┼───────────┼──────┼──────┼─────────┼──────────┼──┤│
│  │ IKHR504 │KOHAIR 7MM │ RAW  │ YARD │ 200     │ Multi    │⋮ ││
│  │         │D.BROWN    │      │      │         │ (3 sups) │  ││
│  ├─────────┼───────────┼──────┼──────┼─────────┼──────────┼──┤│
│  │ IKP20157│RECYCLE HCS│ RAW  │ KG   │ 20      │ PT Fill  │⋮ ││
│  │         │Filling    │      │      │         │ Jaya     │  ││
│  └─────────┴───────────┴──────┴──────┴─────────┴──────────┴──┘│
│                                                                  │
│  [BULK EDIT] [ARCHIVE UNUSED]                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Fields**:
- Kode Material (Primary Key, Auto-generate or Manual)
- Nama Material (Full description)
- Deskripsi Material (Optional notes)
- UoM (Unit of Measure: YARD, KG, PCS, METER, CM, GRAM)
- Jenis Material (RAW, BAHAN PENOLONG, WIP, FINISHED GOODS)
- Min Stock (Reorder point)
- Default Suppliers (Multi-select for flexibility)
- Last Purchase Price (Reference)
- Active Status (for archiving obsolete materials)

### 7.2 Supplier Master

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTERDATA SUPPLIER                                            │
├─────────────────────────────────────────────────────────────────┤
│  [CREATE NEW SUPPLIER] [IMPORT] [EXPORT]                        │
│                                                                  │
│  ┌─────────┬──────────────┬────────────┬──────────┬──────────┐ │
│  │ Code    │ Name         │ Type       │ Rating   │ Contact  │ │
│  ├─────────┼──────────────┼────────────┼──────────┼──────────┤ │
│  │ SUP-001 │PT Supplier A │ Fabric     │⭐⭐⭐⭐⭐│ John Doe │ │
│  │         │              │ Specialist │ (4.8/5)  │ 08123... │ │
│  ├─────────┼──────────────┼────────────┼──────────┼──────────┤ │
│  │ SUP-012 │CV Label Indo │ Label      │⭐⭐⭐⭐  │ Jane Sm..│ │
│  │         │              │ Specialist │ (4.2/5)  │ 08234... │ │
│  └─────────┴──────────────┴────────────┴──────────┴──────────┘ │
│                                                                  │
│  [PERFORMANCE REPORT] [PAYMENT TERMS]                           │
└─────────────────────────────────────────────────────────────────┘
```

**Fields**:
- Kode Supplier (Auto-generate: SUP-001, SUP-002...)
- Nama Supplier
- Alamat Supplier (Full address with province/city)
- Kontak Person (PIC name)
- No Telp/Fax
- Email Supplier
- **Specialization**: Fabric/Label/Accessories/Filling/Packing
- **Rating** (1-5 stars, based on delivery time, quality, price)
- Payment Terms (Net 30, Net 45, COD, etc.)
- Bank Account Info

### 7.3 🔥 BOM (Bill of Material) Master

**Most Complex Masterdata** - Multi-level dengan chain antar departemen.

#### BOM Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTERDATA BOM                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [All Department ▾] [All Article ▾] [Active ✓]        │
│                                                                  │
│  ┌──────────┬────────────┬──────────┬─────────┬──────────────┐ │
│  │ BOM Code │ Article    │ Dept     │ Type    │ Materials    │ │
│  ├──────────┼────────────┼──────────┼─────────┼──────────────┤ │
│  │ BOM-CUT  │ AFTONSPARV │ CUTTING  │ WIP     │ 9 Fabrics    │ │
│  │ -00089   │ 40551542   │          │ Output  │ 9 Threads    │ │
│  ├──────────┼────────────┼──────────┼─────────┼──────────────┤ │
│  │ BOM-SEW  │ AFTONSPARV │ SEWING   │ WIP     │ Cut pieces   │ │
│  │ -00089   │ 40551542   │          │ (Skin)  │ + Threads    │ │
│  ├──────────┼────────────┼──────────┼─────────┼──────────────┤ │
│  │ BOM-FIN  │ AFTONSPARV │ FINISH   │ FG      │ Skin+Filling │ │
│  │ -00089   │ 40551542   │ (Stage1) │ (Stuff) │ +Thread      │ │
│  └──────────┴────────────┴──────────┴─────────┴──────────────┘ │
│                                                                  │
│  [CREATE NEW BOM] [CLONE FROM EXISTING] [CASCADE VIEW]          │
└─────────────────────────────────────────────────────────────────┘
```

#### BOM Detail - Example: CUTTING BOM

```
┌─────────────────────────────────────────────────────────────────┐
│  BOM DETAIL - CUTTING (AFTONSPARV Body)                         │
├─────────────────────────────────────────────────────────────────┤
│  📋 HEADER:                                                     │
│  • BOM Code: BOM-CUT-00089-BODY [Auto-generate]                │
│  • Article: [Dropdown] 40551542 - AFTONSPARV                   │
│  • Department: CUTTING                                          │
│  • BOM Name: AFTONSPARV Body Cut [Auto from article]           │
│                                                                  │
│  🎯 OUTPUT:                                                     │
│  • Output Product: AFTONSPARV Body (Skin) [WIP]                │
│  • BOM Type: WIP (Work In Progress)                             │
│  • Subcontract: No ● / Yes ○                                   │
│  • Output Quantity: 1 pcs (per unit article)                   │
│  • Output UoM: PCS                                              │
│                                                                  │
│  🔀 ROUTING (Process Sequence):                                 │
│  CUTTING → EMBROIDERY → SEWING → FINISHING → PACKING           │
│                                                                  │
│  📦 MATERIAL LIST (Input):                                      │
│  ┌──────┬─────────┬──────────────┬──────────┬──────┬────────┐ │
│  │ #    │ Type    │ Material     │ Code     │ Qty  │ UoM    │ │
│  ├──────┼─────────┼──────────────┼──────────┼──────┼────────┤ │
│  │ 1    │ RAW     │ KOHAIR 7MM   │ IKHR504  │0.1466│ YARD   │ │
│  │      │         │ D.BROWN      │          │      │        │ │
│  ├──────┼─────────┼──────────────┼──────────┼──────┼────────┤ │
│  │ 2    │ RAW     │ JS BOA       │ IJBR105  │0.0094│ YARD   │ │
│  │      │         │ RECYCLE BROWN│          │      │        │ │
│  ├──────┼─────────┼──────────────┼──────────┼──────┼────────┤ │
│  │ 3    │ RAW     │ NYLEX BLACK  │ INYR002  │0.0010│ YARD   │ │
│  ├──────┼─────────┼──────────────┼──────────┼──────┼────────┤ │
│  │ ...  │ (6 more fabrics)                                   │ │
│  ├──────┼─────────┼──────────────┼──────────┼──────┼────────┤ │
│  │ 10   │ RAW     │ BENANG COATS │ THR-001  │ 250  │ CM     │ │
│  │      │         │ BROWN        │          │      │        │ │
│  │ ...  │ (8 more threads)                                   │ │
│  └──────┴─────────┴──────────────┴──────────┴──────┴────────┘ │
│                                                                  │
│  🔄 MARKER EFFICIENCY (for UoM conversion):                     │
│  • Fabric Width: 60 inch                                        │
│  • Pattern Pieces: 12 pieces per body                           │
│  • Marker Length: 3.5 yards (for 24 bodies = 2 rows)           │
│  • Efficiency: 0.1458 yard per pcs (3.5 ÷ 24)                  │
│  • Actual BOM: 0.1466 yard (with 0.5% waste buffer)            │
│                                                                  │
│  ℹ️ This marker info used for Cutting UoM conversion validation│
│                                                                  │
│  [SAVE BOM] [TEST CALCULATION] [DUPLICATE FOR BAJU]             │
└─────────────────────────────────────────────────────────────────┘
```

#### 🔥 BOM Cascade/Chain Example

**Concept**: Output dari 1 BOM menjadi Input untuk BOM berikutnya.

```
ARTICLE: AFTONSPARV (40551542)

[BOM-CUTTING-BODY]
Input: 9 Fabrics + 9 Threads (RAW materials)
Output: 1 pcs "AFTONSPARV Body (Skin)" [WIP]
    ↓
[BOM-EMBROIDERY-BODY] (Optional)
Input: 1 pcs "AFTONSPARV Body (Skin)" [WIP] + Benang bordir
Output: 1 pcs "AFTONSPARV Body Embroidered" [WIP]
    ↓
[BOM-SEWING-BODY]
Input: 1 pcs "AFTONSPARV Body Embroidered" [WIP] + Benang jahit
Output: 1 pcs "AFTONSPARV Skin (Body complete)" [WIP]
    ↓
[BOM-FINISHING-STAGE1] (Stuffing)
Input: 1 pcs "AFTONSPARV Skin" [WIP] + 54g Filling + 60cm Thread
Output: 1 pcs "AFTONSPARV Stuffed Body" [WIP]
    ↓
[BOM-FINISHING-STAGE2] (Closing)
Input: 1 pcs "AFTONSPARV Stuffed Body" [WIP] + 1 Hang Tag
Output: 1 pcs "AFTONSPARV Finished Doll" [SEMI-FG]
    ↓
[BOM-PACKING]
Input: 1 pcs "Finished Doll" + 1 pcs "Baju" + 1/60 Carton + Labels
Output: 1 pcs "AFTONSPARV Complete Set" [FINISHED GOODS]

---

PARALLEL STREAM: BAJU (Pakaian)

[BOM-CUTTING-BAJU]
Input: 5 Fabrics + 5 Threads (different from body)
Output: 1 pcs "AFTONSPARV Baju (Cut pieces)" [WIP]
    ↓
[BOM-SEWING-BAJU]
Input: 1 pcs "Baju Cut pieces" + Threads
Output: 1 pcs "AFTONSPARV Baju (Complete)" [WIP]
    ↓
→ Join with Body at PACKING stage
```

**Validation Rules**:
- ✅ Output dari BOM(n) MUST exist sebagai material di masterdata
- ✅ Output BOM(n) jenis WIP MUST menjadi input BOM(n+1)
- ✅ Final BOM output type MUST be FINISHED GOODS
- ✅ Quantity cascade: 1 article = 1:1:1:1:1 ratio (unless specified)

### 7.4 Article Master

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTERDATA ARTICLE                                             │
├─────────────────────────────────────────────────────────────────┤
│  [CREATE NEW ARTICLE] [IMPORT] [EXPORT]                         │
│                                                                  │
│  ┌──────────┬───────────────────┬──────────┬────────┬────────┐ │
│  │ Code     │ Name              │ Buyer    │ BOMs   │ Status │ │
│  ├──────────┼───────────────────┼──────────┼────────┼────────┤ │
│  │ 40551542 │ AFTONSPARV soft   │ IKEA     │ 7 BOMs │✅ Active││
│  │          │ toy w astronaut.. │          │ (5dpts)│        │ │
│  ├──────────┼───────────────────┼──────────┼────────┼────────┤ │
│  │ 40499469 │ KRAMIG soft toy..│ IKEA     │ 5 BOMs │✅ Active││
│  └──────────┴───────────────────┴──────────┴────────┴────────┘ │
│                                                                  │
│  [VIEW CASCADE BOM] [CLONE ARTICLE]                             │
└─────────────────────────────────────────────────────────────────┘
```

**Fields**:
- No/Kode Article (Primary Key, usually from buyer)
- Nama Article (Full product name)
- Deskripsi Article (Technical specs)
- Buyer/Customer (IKEA, Target, etc.)
- Category (Soft Toys, Accessories, etc.)
- SKU (Stock Keeping Unit)
- Standard Carton Config (60 pcs per carton)
- Active Status

### 7.5 Department Master

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTERDATA DEPARTMENT                                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┬────────────┬──────────┬──────────┬─────────────┐ │
│  │ Code     │ Name       │ Type     │ SPK Pref │ Buffer Avg  │ │
│  ├──────────┼────────────┼──────────┼──────────┼─────────────┤ │
│  │ DEPT-CUT │ CUTTING    │ PROD     │ CUT-     │ +10%        │ │
│  ├──────────┼────────────┼──────────┼──────────┼─────────────┤ │
│  │ DEPT-EMB │ EMBROIDERY │ PROD     │ EMB-     │ +5%         │ │
│  ├──────────┼────────────┼──────────┼──────────┼─────────────┤ │
│  │ DEPT-SEW │ SEWING     │ PROD     │ SEW-     │ +15%        │ │
│  ├──────────┼────────────┼──────────┼──────────┼─────────────┤ │
│  │ DEPT-FIN │ FINISHING  │ PROD     │ FIN-     │ +10%        │ │
│  ├──────────┼────────────┼──────────┼──────────┼─────────────┤ │
│  │ DEPT-PCK │ PACKING    │ PROD     │ PACK-    │ 0%          │ │
│  ├──────────┼────────────┼──────────┼──────────┼─────────────┤ │
│  │ DEPT-QC  │ QC         │ SUPPORT  │ QC-      │ N/A         │ │
│  ├──────────┼────────────┼──────────┼──────────┼─────────────┤ │
│  │ DEPT-RWK │ REWORK     │ SUPPORT  │ RW-      │ N/A         │ │
│  └──────────┴────────────┴──────────┴──────────┴─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 7.6 Subcontractor Master

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTERDATA SUBCONTRACTOR                                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┬──────────────┬────────────┬──────────┬─────────┐  │
│  │ Code    │ Name         │ Service    │ Rating   │ Active  │  │
│  ├─────────┼──────────────┼────────────┼──────────┼─────────┤  │
│  │ SUB-001 │ CV Bordir    │ Embroidery │⭐⭐⭐⭐ │ ✅ Yes  │  │
│  │         │ Jaya         │ Specialist │ (4.5/5)  │         │  │
│  └─────────┴──────────────┴────────────┴──────────┴─────────┘  │
│                                                                  │
│  [PERFORMANCE TRACKING] [DELIVERY MONITORING]                   │
└─────────────────────────────────────────────────────────────────┘
```

---

<a name="reporting"></a>
## 8. REPORTING & ANALYTICS

### 8.1 Production Reports

```
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION REPORT - WEEKLY SUMMARY                             │
│  Week: W05 2026 (Jan 27 - Feb 2)                               │
├─────────────────────────────────────────────────────────────────┤
│  📊 Achievement Summary:                                        │
│  • Total SPK Completed: 23                                      │
│  • Total Units Produced: 5,420 pcs                             │
│  • Overall Yield: 97.2% (Good Output / Total Production)       │
│  • Defect Rate: 2.8% (148 pcs defect)                         │
│    └─ Rework Recovery: 82.4% (122 pcs recovered)              │
│  • Final Scrap: 26 pcs (0.48%)                                 │
│                                                                  │
│  📋 By Department:                                              │
│  ┌────────────┬─────────┬────────┬─────────┬──────────────┐   │
│  │ Department │ Target  │ Actual │ Yield   │ Defect Rate  │   │
│  ├────────────┼─────────┼────────┼─────────┼──────────────┤   │
│  │ CUTTING    │ 2,800   │ 2,850  │ 99.1%   │ 0.9%         │   │
│  │ EMBROIDERY │ 1,200   │ 1,215  │ 99.5%   │ 0.5%         │   │
│  │ SEWING     │ 2,650   │ 2,680  │ 97.3%   │ 2.7%         │   │
│  │ FINISHING  │ 2,100   │ 2,140  │ 97.8%   │ 2.2%         │   │
│  │ PACKING    │ 1,850   │ 1,850  │ 100%    │ 0%           │   │
│  └────────────┴─────────┴────────┴─────────┴──────────────┘   │
│                                                                  │
│  🏆 Top Performers:                                             │
│  • Best Yield: PACKING (100%)                                   │
│  • Highest Recovery: FINISHING (85% rework success)            │
│  • On-time Completion: CUTTING (100% SPK on schedule)          │
│                                                                  │
│  [EXPORT PDF] [SEND TO MANAGEMENT] [DRILL DOWN]                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Material Debt Report

```
┌─────────────────────────────────────────────────────────────────┐
│  MATERIAL DEBT REPORT - CRITICAL                                │
│  As of: 4 February 2026                                         │
├─────────────────────────────────────────────────────────────────┤
│  🔴 Active Material Debts:                                      │
│  ┌──────────┬────────┬────────┬─────────┬──────────────────┐   │
│  │ Material │ Code   │ Debt   │ Value   │ Expected Clear   │   │
│  ├──────────┼────────┼────────┼─────────┼──────────────────┤   │
│  │ Filling  │IKP20157│ -12 KG │ Rp 1.2M │ 5 Feb (PO-00034) │   │
│  │ Dacron   │        │        │         │                  │   │
│  ├──────────┼────────┼────────┼─────────┼──────────────────┤   │
│  │ KOHAIR   │IKHR504 │ -8 YD  │ Rp 800K │ 6 Feb (PO-00035) │   │
│  │ D.BROWN  │        │        │         │                  │   │
│  └──────────┴────────┴────────┴─────────┴──────────────────┘   │
│                                                                  │
│  💰 Total Debt Value: Rp 2,000,000                              │
│  ⚠️ Production at Risk: 2 MOs (900 pcs total)                  │
│                                                                  │
│  📝 Actions Taken:                                              │
│  • PO-00034 expedited (urgent delivery requested)               │
│  • PO-00035 confirmed by supplier (2 days max)                 │
│  • PPIC notified to prioritize other MOs temporarily            │
│                                                                  │
│  [CREATE URGENT PO] [NOTIFY PURCHASING] [ESCALATE]              │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 COPQ (Cost of Poor Quality) Report

```
┌─────────────────────────────────────────────────────────────────┐
│  COPQ ANALYSIS - JANUARY 2026                                   │
├─────────────────────────────────────────────────────────────────┤
│  📊 Total Defects: 245 pcs                                      │
│  • Rework Successful: 198 pcs (80.8%)                          │
│  • Scrap: 47 pcs (19.2%)                                        │
│                                                                  │
│  💰 Cost Breakdown:                                             │
│  • Rework Labor Cost: Rp 5,940,000                             │
│    (198 pcs × 25 min avg × Rp 1,200/min labor rate)           │
│  • Rework Material Cost: Rp 1,250,000                          │
│  • Scrap Cost: Rp 8,225,000                                     │
│    (47 pcs × Rp 175,000 per unit avg material value)          │
│  ─────────────────────────────                                  │
│  • TOTAL COPQ: Rp 15,415,000                                    │
│                                                                  │
│  📋 By Department (Defect Source):                              │
│  • CUTTING: 12 pcs (4.9%) - Fabric cutting error               │
│  • SEWING: 145 pcs (59.2%) - Jahitan putus, salah ukuran       │
│  • FINISHING: 88 pcs (35.9%) - Stuffing irregular              │
│                                                                  │
│  🎯 Improvement Opportunities:                                  │
│  1. SEWING: Train operators on tension control (145 defects)    │
│  2. FINISHING: Improve stuffing SOP (88 defects)               │
│  3. Target: Reduce defect rate from 2.8% to 2.0% (save 28%)   │
│     Potential Savings: Rp 4,316,000 per month                  │
│                                                                  │
│  [ROOT CAUSE ANALYSIS] [EXPORT] [ACTION PLAN]                   │
└─────────────────────────────────────────────────────────────────┘
```

---

<a name="user-management"></a>
## 9. USER MANAGEMENT & PERMISSIONS

### 9.1 User Roles

```
┌────────────────┬────────────────────────────────────────────────┐
│ Role           │ Access & Permissions                           │
├────────────────┼────────────────────────────────────────────────┤
│ SUPERADMIN     │ • Full system access                           │
│                │ • Create/Edit/Delete ALL data                  │
│                │ • User management                              │
│                │ • System configuration                         │
├────────────────┼────────────────────────────────────────────────┤
│ DEVELOPER      │ • Same as Superadmin                           │
│                │ • Database direct access                       │
│                │ • Debug mode enabled                           │
├────────────────┼────────────────────────────────────────────────┤
│ DIRECTOR       │ • View ALL modules (read-only for most)        │
│                │ • Approve critical PO (>Rp 100M)               │
│                │ • Final approval untuk material debt           │
│                │ • Export ALL reports                           │
│                │ • Dashboard: Strategic metrics                 │
├────────────────┼────────────────────────────────────────────────┤
│ MANAGER        │ • View production, inventory, purchasing       │
│                │ • Approve MO, PO (mid-level)                   │
│                │ • Cannot edit masterdata                       │
│                │ • Dashboard: Operational metrics               │
├────────────────┼────────────────────────────────────────────────┤
│ SUPERVISOR     │ • View/Edit masterdata (BOM, Material, etc.)   │
│                │ • Approve SPK                                  │
│                │ • Approve rework decisions                     │
│                │ • QC checkpoint approval                       │
├────────────────┼────────────────────────────────────────────────┤
│ PURCHASING     │ • Create/Edit PO (both Auto & Manual mode)     │
│                │ • Supplier management                          │
│                │ • Material receiving approval                  │
│                │ • Cannot view costing details                  │
├────────────────┼────────────────────────────────────────────────┤
│ PPIC           │ • Create/Edit MO (PARTIAL & RELEASED)          │
│                │ • Create SPK per department                    │
│                │ • Material allocation                          │
│                │ • Production scheduling                        │
│                │ • View material stock (cannot edit)            │
├────────────────┼────────────────────────────────────────────────┤
│ WAREHOUSE      │ • Material IN/OUT                              │
│                │ • Stock opname                                 │
│                │ • FG receiving & shipment                      │
│                │ • Barcode scanning                             │
│                │ • Cannot approve PO/MO                         │
├────────────────┼────────────────────────────────────────────────┤
│ ADMIN PRODUKSI │ • Input daily production (assigned dept)       │
│ (per Dept)     │ • View own dept SPK only                       │
│                │ • Record defects → auto-create rework          │
│                │ • Cannot edit SPK target                       │
│                │ • Cannot view other departments                │
├────────────────┼────────────────────────────────────────────────┤
│ QC INSPECTOR   │ • QC checkpoint inspection                     │
│                │ • Approve/Reject batches                       │
│                │ • Create rework tickets                        │
│                │ • View quality metrics                         │
├────────────────┼────────────────────────────────────────────────┤
│ REWORK         │ • View rework queue                            │
│ OPERATOR       │ • Input rework results                         │
│                │ • Cannot approve QC pass/fail                  │
├────────────────┼────────────────────────────────────────────────┤
│ SUBCONTRACTOR  │ • View assigned embroidery orders              │
│                │ • Update progress only                         │
│                │ • Cannot view costing/pricing                  │
│                │ • Limited to own orders                        │
└────────────────┴────────────────────────────────────────────────┘
```

### 9.2 Permission Matrix

| Module/Feature | Superadmin | Developer | Director | Manager | PPIC | Purchasing | Warehouse | Admin Prod |
|----------------|------------|-----------|----------|---------|------|------------|-----------|------------|
| **Dashboard**  | ✅ All     | ✅ All    | ✅ All   | ✅ Ops  | ✅ PPIC | ✅ Purchase | ✅ Stock | ✅ Dept |
| **Create PO**  | ✅         | ✅        | ❌       | ❌      | ❌   | ✅         | ❌        | ❌         |
| **Approve PO** | ✅         | ✅        | ✅ >100M | ✅ <100M | ❌  | ❌         | ❌        | ❌         |
| **Create MO**  | ✅         | ✅        | ❌       | ❌      | ✅   | ❌         | ❌        | ❌         |
| **Create SPK** | ✅         | ✅        | ❌       | ❌      | ✅   | ❌         | ❌        | ❌         |
| **Input Daily Prod** | ✅   | ✅        | ❌       | ❌      | ❌   | ❌         | ❌        | ✅ Own Dept |
| **Material IN/OUT** | ✅    | ✅        | ❌       | ❌      | ❌   | ✅ Approve | ✅        | ❌         |
| **Edit Masterdata** | ✅    | ✅        | ❌       | ❌      | ❌   | ❌         | ❌        | ❌         |
| **View Reports** | ✅ All   | ✅ All    | ✅ All   | ✅ Most | ✅ Prod | ✅ Purchase | ✅ Stock | ✅ Dept |
| **QC Approval** | ✅        | ✅        | ❌       | ✅      | ❌   | ❌         | ❌        | ❌         |

---

<a name="mobile-app"></a>
## 10. 📱 MOBILE APPLICATION (Android)

### 10.1 FinishGood Label System (Mobile)

**Platform**: Android (Tablet preferred, smartphone compatible)

**Main Features**:
1. Barcode Scanner Integration
2. Label Printing (Bluetooth thermal printer)
3. Box Verification
4. FG Receiving Confirmation

#### Mobile UI - Main Screen

```
┌─────────────────────────────────────────────────────────────────┐
│  📱 FG LABEL SYSTEM - QUTY KARUNIA                              │
│  User: John Doe (Warehouse) | 4 Feb 2026 10:23                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [📊 SCAN BARCODE]                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │            [CAMERA VIEWFINDER]                             │  │
│  │                                                            │  │
│  │        Align barcode within frame                          │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ─────────── OR ───────────                                     │
│                                                                  │
│  [🔢 MANUAL ENTRY]                                              │
│  SPK Number: [Input: PACK-2026-00078]                          │
│  [SEARCH]                                                       │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  📦 ACTIVE PACKING ORDERS (Today):                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PACK-2026-00078 - AFTONSPARV                              │  │
│  │ Target: 465 pcs (8 CTN) | Status: 🔄 In Progress         │  │
│  │ [TAP TO OPEN]                                              │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ PACK-2026-00075 - KRAMIG                                  │  │
│  │ Target: 600 pcs (10 CTN) | Status: ⏳ Ready              │  │
│  │ [TAP TO OPEN]                                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [⚙️ SETTINGS] [📊 HISTORY] [🔄 SYNC]                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Mobile UI - Box Labeling Process

```
┌─────────────────────────────────────────────────────────────────┐
│  📦 LABELING: PACK-2026-00078                                   │
│  Article: AFTONSPARV (40551542)                                │
│  Week: W05 | Destination: IKEA Distribution Center             │
├─────────────────────────────────────────────────────────────────┤
│  🎯 TARGET:                                                     │
│  • Total: 465 pcs (8 cartons)                                   │
│  • Standard: 60 pcs/carton × 7 = 420 pcs                       │
│  • Last carton: 45 pcs                                          │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  📋 PROGRESS:                                                   │
│  ┌──────────┬────────────┬─────────┬──────────┬─────────────┐ │
│  │ Box No   │ Qty        │ Labeled │ Scanned  │ Status      │ │
│  ├──────────┼────────────┼─────────┼──────────┼─────────────┤ │
│  │ 1/8      │ 60 pcs     │ ✅      │ ✅       │ Complete    │ │
│  │ 2/8      │ 60 pcs     │ ✅      │ ✅       │ Complete    │ │
│  │ 3/8      │ 60 pcs     │ ✅      │ ⏳       │ Pending Scan│ │
│  │ 4/8      │ 60 pcs     │ ⏳      │ ⏳       │ Ready Label │ │
│  │ ...      │            │         │          │             │ │
│  └──────────┴────────────┴─────────┴──────────┴─────────────┘ │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  🏷️ CURRENT BOX: 4/8                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Box Number: 4                                            │  │
│  │ • Quantity: 60 pcs (standard)                              │  │
│  │ • Barcode: [Auto-generated]                                │  │
│  │   AFTON-W05-004-20260204                                   │  │
│  │                                                            │  │
│  │ [🖨️ PRINT LABEL] ← Connect to thermal printer             │  │
│  │                                                            │  │
│  │ After label attached:                                      │  │
│  │ [📷 SCAN TO VERIFY] ← Verify label correct                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [◀️ PREV BOX] [NEXT BOX ▶️] [🏠 HOME]                          │
└─────────────────────────────────────────────────────────────────┘
```

**Workflow**:
1. Operator pilih SPK dari list
2. Untuk setiap carton:
   - Input qty (default 60 untuk standard, manual untuk last box)
   - System generate barcode
   - Print label via Bluetooth printer
   - Attach label to box
   - Scan barcode to verify
   - Mark complete → Next box
3. Setelah semua boxes labeled → Submit to FG warehouse
4. Warehouse receive dengan scan barcode → Auto-update FG stock

**Benefit**:
- ✅ Paperless process
- ✅ Real-time FG inventory update
- ✅ Traceability per carton
- ✅ Reduce counting error
- ✅ Fast shipment verification

---

<a name="notification"></a>
## 11. 🔔 NOTIFICATION SYSTEM

### 11.1 Notification Types & Triggers

```
┌─────────────────────────────────────────────────────────────────┐
│  NOTIFICATION CENTER                                            │
│  User: PPIC Team | 12 unread notifications                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 🔴 URGENT - Material Debt Alert                          │  │
│  │ IKP20157 Filling: -12 KG (Affects MO-00089)              │  │
│  │ Action required: Expedite PO-00034                        │  │
│  │ 10 minutes ago | [VIEW DETAILS] [MARK READ]               │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 🟠 WARNING - SPK Delayed                                 │  │
│  │ SEW-2026-00034 (AFTONSPARV) - 2 days behind schedule     │  │
│  │ Reason: Machine breakdown (resolved)                      │  │
│  │ 1 hour ago | [VIEW SPK] [MARK READ]                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 🟢 SUCCESS - PO Received                                 │  │
│  │ PO-L-2026-00089 (Label) fully received                   │  │
│  │ MO-2026-00089 auto-upgraded to RELEASED                  │  │
│  │ 2 hours ago | [VIEW MO] [MARK READ]                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 🔵 INFO - New PO Created                                 │  │
│  │ PO-K-2026-00045 (KRAMIG - Fabric) by Purchasing A        │  │
│  │ Awaiting PPIC review for MO creation                      │  │
│  │ 3 hours ago | [REVIEW PO] [MARK READ]                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Filter: [All ▾] | Sort: [Most Recent ▾] | [MARK ALL READ]    │
└─────────────────────────────────────────────────────────────────┘
```

### 11.2 Notification Rules (Auto-trigger)

| Event | Notify To | Priority | Channel |
|-------|-----------|----------|---------|
| PO Created | PPIC | 🔵 INFO | Email + In-app |
| PO Received (Fabric) | PPIC | 🟢 SUCCESS | Email + In-app |
| PO Received (Label) | PPIC, Production Admins | 🟢 SUCCESS | Email + In-app + SMS |
| MO Upgraded (PARTIAL → RELEASED) | All Production Admins | 🟢 SUCCESS | In-app + SMS |
| Material Stock Low (<15%) | Purchasing, Manager | 🟠 WARNING | Email + In-app |
| Material Debt (Negative) | Purchasing, PPIC, Manager, Director | 🔴 URGENT | Email + In-app + SMS |
| SPK Delayed (>1 day) | PPIC, Manager | 🟠 WARNING | Email + In-app |
| SPK Completed | PPIC | 🟢 SUCCESS | In-app |
| Defect Rate High (>5%) | QC, Supervisor, Manager | 🔴 URGENT | Email + In-app |
| Rework Completed | PPIC, QC | 🔵 INFO | In-app |
| FG Ready to Ship | Warehouse, Manager | 🟢 SUCCESS | Email + In-app |

### 11.3 Email Notification Template Example

```
Subject: 🔴 URGENT - Material Debt Alert (IKP20157 Filling -12 KG)

Dear PPIC Team,

This is an automated alert from ERP Quty Karunia system.

Material Debt Detected:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Material: [IKP20157] RECYCLE HCS Filling
Current Stock: -12 KG (DEBT)
Minimum Stock: 20 KG
Debt Value: Rp 1,200,000

Impact:
• MO-2026-00089 (AFTONSPARV) at risk
• Production may stop if not resolved within 2 days

Actions Required:
1. Expedite PO-00034 delivery (Expected: 5 Feb 2026)
2. Contact supplier for urgent shipment
3. Consider alternative filling source if delay continues

Expected Delivery: 5 Feb 2026 (2 days from now)

[VIEW DETAILS IN SYSTEM] [CONTACT PURCHASING]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ERP Quty Karunia | Automated Alert System
Generated: 4 Feb 2026, 10:45 WIB
```

---

## 12. 📝 SUMMARY - KEY UI/UX IMPROVEMENTS

### What Makes This ERP Special?

#### 1. 🔥 DUAL-MODE PURCHASING
- **Article BOM Explosion**: 80% time savings
- **Supplier per Material**: Maximum flexibility
- **Hybrid Input**: Best of both worlds

#### 2. 🔥 FLEXIBLE PRODUCTION START
- **PARTIAL MO**: Start cutting 3-5 days earlier
- **Auto-upgrade to RELEASED**: Zero manual error
- **Week/Destination auto-inherit**: From PO Label

#### 3. 🔥 FLEXIBLE TARGET SYSTEM
- **Buffer per Department**: Realistic planning
- **Actual/Target format**: Universal clarity
- **Constraint validation**: Prevent overproduction

#### 4. 🔥 WAREHOUSE FINISHING 2-STAGE
- **Separate Stock**: Skin vs Stuffed Body
- **Demand-driven**: Adjust to Packing urgency
- **Material control**: Accurate filling tracking

#### 5. 🔥 UOM CONVERSION VALIDATION
- **Auto-calculate**: From BOM marker
- **Real-time Alert**: Variance detection
- **Block logic**: >15% variance prevented

#### 6. 🔥 REWORK MODULE
- **Defect capture**: Integrated with daily input
- **Recovery tracking**: Monitor % success
- **COPQ analysis**: Cost visibility for improvement

#### 7. 🔥 MOBILE FG LABELING
- **Barcode integration**: Paperless process
- **Real-time update**: FG stock instant
- **Traceability**: Per carton tracking

---

## 13. 🚀 NEXT DEVELOPMENT PRIORITIES

│  └─ Service: [Multi-select] *Required                       │
│     ├─ ☑️ Embroidery (Bordir)                              │
│     ├─ ☐ Sewing (Jahit)                                    │
│     ├─ ☐ Cutting                                           │
│     └─ ☐ Finishing                                         │
│                                                             │
│  📍 Address & Contact                                       │
│  ├─ Alamat: [Textarea] *Required                            │
│  │  Jl. Bordir Indah No. 12, Cibitung, Bekasi              │
│  ├─ Contact Person: [Text] Ibu Rina (Owner)                 │
│  ├─ No Telp: [Text] +62 21 8888 9999                        │
│  └─ Email: [Email] rina@embjaya.com                         │
│                                                             │
│  💰 Pricing & Terms                                         │
│  ├─ Service Rate: [Currency]                                │
│  │  ├─ Standard Embroidery: $0.50 /pcs                     │
│  │  ├─ Complex Pattern: $0.75 /pcs                         │
│  │  └─ Rush Order: +20% premium                            │
│  │                                                          │
│  ├─ Payment Terms: [Dropdown] Net 14 days                   │
│  └─ Minimum Order: [Number] 100 pcs                         │
│                                                             │
│  ⏱️ Capacity & Lead Time                                    │
│  ├─ Daily Capacity: [Number] 800 pcs/day                    │
│  ├─ Standard Lead Time: [Number] 3 days                     │
│  ├─ Rush Lead Time: [Number] 1 day (with premium)           │
│  └─ Current Utilization: [Auto-calc] 60% ✅ Available       │
│                                                             │
│  📊 Performance Rating                                      │
│  ├─ Quality Score: 4.3/5.0 ⭐⭐⭐⭐                        │
│  ├─ On-Time Delivery: 88% ⚠️ (Need improvement)            │
│  ├─ Defect Rate: 2.5% ✅ Acceptable                        │
│  └─ Overall Score: 4.0/5.0 ⭐⭐⭐⭐                         │
│                                                             │
│  🔐 User Account (For Subcon Portal Access)                 │
│  ├─ Username: [Text] emb_jaya                               │
│  ├─ Password: [Password] ******** (Auto-generated)          │
│  ├─ Role: Subcontractor (Limited access)                    │
│  └─ Access Rights:                                          │
│     ├─ View assigned SPK only                               │
│     ├─ Input production progress                            │
│     ├─ View material allocation                             │
│     └─ Cannot view other MO/SPK                             │
│                                                             │
│  ✅ Status                                                  │
│  └─ Active: [Toggle] ● Active ○ Inactive                    │
│                                                             │
│  [SAVE] [VIEW WORK ORDERS] [PERFORMANCE REPORT] [CANCEL]   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. STOCK OPNAME PER DEPARTEMEN

### 6.1 Konsep Stock Opname

**Purpose**: Physical count untuk memastikan system stock = actual stock di lapangan.

**Key Rules**:
1. Setiap departemen input stock opname sendiri
2. Tidak dapat diubah oleh departemen lain (strict permission)
3. Tidak perlu approval (trust-based, karena physical count)
4. Variance otomatis adjust system stock

**Frequency**:
- **Monthly SO**: End of month (mandatory)
- **Cycle Count**: Daily/weekly untuk fast-moving items
- **Annual Audit**: Full inventory count (End of year)

---

### 6.2 Form Stock Opname

```
┌─────────────────────────────────────────────────────────────┐
│  STOCK OPNAME - SEWING DEPARTMENT                           │
│  Period: Januari 2026 | Count Date: 31 Jan 2026            │
├─────────────────────────────────────────────────────────────┤
│  📦 Material Category: WIP (Work in Progress)               │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Item 1: [WIP-SEW-AFTON-BODY] Skin Body AFTONSPARV      ││
│  │ ├─ System Stock: 125 pcs                                ││
│  │ ├─ Physical Count: [  118  ] pcs *Input Required       ││
│  │ ├─ Variance: -7 pcs (-5.6%) ⚠️ Investigate             ││
│  │ ├─ Reason: [Dropdown]                                   ││
│  │ │  ├─ Normal consumption                                ││
│  │ │  ├─ Defect/Scrap (not recorded) ☑️ Selected          ││
│  │ │  ├─ Theft/Loss                                        ││
│  │ │  └─ Data entry error                                  ││
│  │ └─ Notes: [Text] Found 7 pcs reject di corner, lupa    ││
│  │    input ke rework module                               ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ Item 2: [WIP-SEW-AFTON-BAJU] Baju AFTONSPARV           ││
│  │ ├─ System Stock: 85 pcs                                 ││
│  │ ├─ Physical Count: [  85  ] pcs ✅ MATCH               ││
│  │ ├─ Variance: 0 pcs (0.0%) ✅ Perfect                   ││
│  │ └─ Notes: [Text] Stock sesuai                           ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ Item 3: Thread - Brown                                  ││
│  │ ├─ System Stock: 5,000 CM                               ││
│  │ ├─ Physical Count: [  4,850  ] CM                      ││
│  │ ├─ Variance: -150 CM (-3.0%) ✅ Within tolerance       ││
│  │ └─ Reason: Normal usage variance                        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  [+ ADD MORE ITEMS] [IMPORT FROM TEMPLATE]                  │
│                                                             │
│  📊 Summary                                                 │
│  ├─ Total Items Counted: 12 items                           │
│  ├─ Exact Match: 8 items (66.7%) ✅                        │
│  ├─ Within Tolerance (<5%): 3 items (25.0%) ✅             │
│  ├─ Need Investigation (>5%): 1 item (8.3%) ⚠️            │
│  └─ Total Value Variance: -$85.00 (-2.1%)                   │
│                                                             │
│  👤 Approval (Dept Level Only)                              │
│  ├─ Counted By: [Dropdown] Admin Sewing (Ibu Ani)           │
│  ├─ Verified By: [Dropdown] Supervisor Sewing (Pak Agung)   │
│  └─ Count Date/Time: 31 Jan 2026 15:30 WIB                  │
│                                                             │
│  [SAVE DRAFT] [SUBMIT & ADJUST STOCK] [CANCEL]             │
│                                                             │
│  ⚡ Actions After Submit:                                   │
│  1. System stock auto-adjust ke physical count              │
│  2. Variance report auto-generated                          │
│  3. Finance team notified (for value variance >5%)          │
│  4. Investigation task created (for items >5% variance)     │
└─────────────────────────────────────────────────────────────┘
```

---

### 6.3 Stock Opname Types by Location

| Location | Stock Type | Frequency | Responsibility |
|----------|-----------|-----------|----------------|
| **Warehouse Main** | Raw Material | Monthly | Warehouse Team |
| **Cutting Dept** | Fabric scraps, WIP parts | Weekly | Admin Cutting |
| **Embroidery** | WIP embroidered parts | Monthly | Admin Embroidery |
| **Sewing Dept** | WIP Skin, Thread | Weekly | Admin Sewing |
| **Warehouse Finishing** | Skin, Stuffed Body, Finished Doll | Weekly | Warehouse Team |
| **Packing Dept** | Complete Sets, Cartons | Daily | Admin Packing |
| **Warehouse FG** | Finished Goods ready ship | Daily | Warehouse Team |

---

## 7. LAPORAN DAN DASHBOARD - COMPREHENSIVE ANALYTICS

### 7.1 Laporan PO Purchasing

```
┌─────────────────────────────────────────────────────────────┐
│  📊 PURCHASE ORDER REPORT                                   │
│  Period: Januari 2026                                       │
├─────────────────────────────────────────────────────────────┤
│  🔍 Filters                                                 │
│  ├─ PO Type: [Dropdown] All / PO Kain / PO Label / PO Acc  │
│  ├─ Status: [Multi-select] All / Draft / Sent / Partial /  │
│  │          Complete                                        │
│  ├─ Supplier: [Dropdown] All Suppliers                      │
│  ├─ Date Range: [Date] 1 Jan - 31 Jan 2026                 │
│  └─ Article: [Dropdown] All Articles                        │
│                                                             │
│  📑 PO Summary Table                                        │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ PO No    │ Type  │ Supplier       │ Value    │Status │ │
│  ├──────────┼───────┼────────────────┼──────────┼───────┤ │
│  │POK-00001 │Kain   │Kain Sejahtera  │$2,450 ✅│Complete││
│  │POL-00002 │Label  │Label Indonesia │$158   ✅│Complete││
│  │POA-00003 │Access │Thread Supply   │$420   🔄│Partial││
│  │POK-00004 │Kain   │Textile Indo    │$3,200 📤│Sent   ││
│  │... (45 more POs)                                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  💰 Financial Summary                                       │
│  ├─ Total PO Value: $125,450.00                             │
│  │  ├─ PO Kain: $78,200 (62.3%)                            │
│  │  ├─ PO Label: $12,500 (10.0%)                           │
│  │  └─ PO Accessories: $34,750 (27.7%)                     │
│  │                                                          │
│  ├─ Status Breakdown:                                       │
│  │  ├─ Complete: $85,000 (67.8%) ✅                        │
│  │  ├─ Partial: $25,450 (20.3%) 🔄                         │
│  │  └─ Sent (Waiting): $15,000 (11.9%) ⏳                  │
│  │                                                          │
│  └─ Payment Status:                                         │
│     ├─ Paid: $60,000 (70.6% of complete)                    │
│     ├─ Due: $15,000 (17.6%)                                 │
│     └─ Overdue: $10,000 (11.8%) ⚠️ Action needed           │
│                                                             │
│  📊 Supplier Performance                                    │
│  ├─ Top Suppliers (by value):                               │
│  │  1. PT Kain Sejahtera: $45,000 (35.9%)                  │
│  │  2. CV Textile Indo: $32,000 (25.5%)                    │
│  │  3. Thread Supply Co: $18,500 (14.7%)                   │
│  │                                                          │
│  └─ On-Time Delivery Rate:                                  │
│     ├─ PT Kain Sejahtera: 92% ✅                           │
│     ├─ CV Textile Indo: 85% ⚠️                             │
│     └─ Thread Supply Co: 78% 🔴 Need improvement           │
│                                                             │
│  [EXPORT EXCEL] [EXPORT PDF] [EMAIL REPORT] [PRINT]        │
└─────────────────────────────────────────────────────────────┘
```

---

### 7.2 Laporan MO (Manufacturing Order)

```
┌─────────────────────────────────────────────────────────────┐
│  📊 MANUFACTURING ORDER REPORT                              │
│  Period: Januari 2026 | Article: All                       │
├─────────────────────────────────────────────────────────────┤
│  🎯 MO Performance Overview                                 │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ MO No      │ Article      │ Target │ Actual │ Status │  │
│  ├────────────┼──────────────┼────────┼────────┼────────┤  │
│  │MO-2026-089 │AFTONSPARV    │450 pcs │465 pcs │✅ 103%│  │
│  │MO-2026-090 │KRAMIG        │600 pcs │598 pcs │✅ 99% │  │
│  │MO-2026-091 │GOSIG GOLDEN  │800 pcs │-       │🔄 60% │  │
│  │... (24 more MOs this month)                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  📈 Achievement Metrics                                     │
│  ├─ Total MO: 27 orders                                     │
│  ├─ Completed: 22 MO (81.5%) ✅                            │
│  ├─ In Progress: 4 MO (14.8%) 🔄                           │
│  ├─ Delayed: 1 MO (3.7%) ⚠️                                │
│  │                                                          │
│  ├─ Target vs Actual:                                       │
│  │  ├─ Total Target: 12,500 pcs                            │
│  │  ├─ Total Actual: 12,680 pcs                            │
│  │  └─ Achievement: 101.4% ✅ EXCEED                       │
│  │                                                          │
│  └─ On-Time Delivery Rate: 95.7% ✅ Excellent              │
│                                                             │
│  🏭 Production Efficiency by Department                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Dept      │Target │Actual │Yield  │OEE   │Grade    │  │
│  ├───────────┼───────┼───────┼───────┼──────┼─────────┤  │
│  │Cutting    │13,125 │13,250 │99.2%  │94.5% │✅ A     │  │
│  │Embroidery │12,375 │12,375 │100.0% │92.0% │✅ A     │  │
│  │Sewing     │13,922 │13,985 │97.8%  │89.5% │✅ B+    │  │
│  │Finishing  │12,960 │12,980 │98.5%  │91.2% │✅ A-    │  │
│  │Packing    │12,550 │12,680 │99.8%  │96.3% │✅ A+    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  💰 Cost Analysis                                           │
│  ├─ Material Cost: $115,000                                 │
│  ├─ Labor Cost: $38,500                                     │
│  ├─ Overhead: $12,200                                       │
│  ├─ COPQ (Defects): $1,680                                  │
│  ├─ Total COGS: $167,380                                    │
│  └─ Cost per Unit: $13.20 /pcs ✅ Within budget ($14.00)   │
│                                                             │
│  [EXPORT EXCEL] [VIEW DETAILS] [SEND TO DIRECTOR]          │
└─────────────────────────────────────────────────────────────┘
```

---

### 7.3 Dashboard Monitoring Schedule Production

**Real-time Gantt Chart View**:

```
┌─────────────────────────────────────────────────────────────┐
│  📊 PRODUCTION SCHEDULE DASHBOARD - GANTT VIEW              │
│  Week: 1-7 Feb 2026                                         │
├─────────────────────────────────────────────────────────────┤
│  🏭 Department: Sewing (Filter: All / Select Dept)          │
│                                                             │
│  Timeline: [◀ Previous Week] [This Week] [Next Week ▶]     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SPK          │ Mon │ Tue │ Wed │ Thu │ Fri │ Sat │   │   │
│  ├──────────────┼─────┼─────┼─────┼─────┼─────┼─────┤   │   │
│  │SEW-00120     │█████│█████│█████│█████│█████│     │   │   │
│  │AFTONSPARV    │ ✅ 100% Completed                  │   │   │
│  ├──────────────┼─────┼─────┼─────┼─────┼─────┼─────┤   │   │
│  │SEW-00121     │     │█████│█████│█████│█████│█████│   │   │
│  │KRAMIG        │     │ 🔄 Progress: 85% (On track)   │   │   │
│  ├──────────────┼─────┼─────┼─────┼─────┼─────┼─────┤   │   │
│  │SEW-00122     │     │     │     │█████│█████│█████│   │   │
│  │GOSIG         │     │     │     │ ⏳ Scheduled      │   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Legend:                                                    │
│  █████ Planned duration                                     │
│  ✅ Completed ahead/on-time                                │
│  🔄 In progress (on track)                                  │
│  ⚠️ Delayed (action needed)                                │
│  ⏳ Scheduled (not started)                                │
│                                                             │
│  📊 Weekly Statistics                                       │
│  ├─ Total SPK This Week: 8 SPK                              │
│  ├─ Completed: 3 SPK (37.5%) ✅                            │
│  ├─ In Progress: 4 SPK (50.0%) 🔄                          │
│  ├─ Not Started: 1 SPK (12.5%) ⏳                          │
│  └─ On-Time Rate: 92.3% ✅                                 │
│                                                             │
│  [REFRESH] [PRINT] [EXPORT TO PDF] [MEETING MODE]          │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. USER ROLE AND PERMISSION - RBAC SYSTEM

### 8.1 Role-Based Access Control Matrix

| Module / Feature | Superadmin | Director | Manager | PPIC | Purchasing | Warehouse | Admin Prod | QC | Supervisor | Subcon | Dev |
|------------------|:----------:|:--------:|:-------:|:----:|:----------:|:---------:|:----------:|:--:|:----------:|:------:|:---:|
| **Dashboard** |
| View All Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| View Cost Data | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Purchasing** |
| Create PO | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Approve PO | ✅ | ✅ (>$10K) | ✅ (<$10K) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Edit PO | ✅ | ❌ | ❌ | ❌ | ✅ (Own) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **PPIC** |
| Create MO | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Release MO | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Generate SPK | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Edit SPK Target | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Production** |
| View SPK (All) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| View SPK (Own Dept) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Input Production | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Own) | ❌ | ✅ | ✅ (Assigned) | ✅ |
| Edit Production | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ (Own, <24h) | ❌ | ✅ | ❌ | ✅ |
| Complete SPK | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Rework & QC** |
| Create Rework | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Input Rework Result | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ |
| QC Inspection | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| Approve QC | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Warehouse** |
| GRN (Material In) | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ (QC) | ✅ | ❌ | ✅ |
| Material Issue | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| FG Receiving | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| FG Shipment | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Stock Adjustment | ✅ | ✅ (Approve) | ✅ (Approve) | ❌ | ❌ | ✅ (Request) | ❌ | ❌ | ✅ | ❌ | ✅ |
| Stock Opname | ✅ | ✅ (View) | ✅ (View) | ✅ (Input) | ❌ | ✅ (Input) | ✅ (Input) | ❌ | ✅ | ❌ | ✅ |
| **Masterdata** |
| Material Master | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ (View) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Supplier Master | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| BOM Master | ✅ | ❌ | ❌ | ✅ | ✅ (View) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Article Master | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Department Master | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Subcon Master | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Reports** |
| Production Report | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ (Own) | ✅ | ✅ | ❌ | ✅ |
| Purchasing Report | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Inventory Report | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Material Debt Report | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| COPQ Report | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| Financial Report | ✅ | ✅ | ✅ (Dept) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **System Admin** |
| User Management | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Role & Permission | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| System Config | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Audit Trail | ✅ | ✅ (View) | ✅ (View) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Database Backup | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Legend**:
- ✅ Full Access (Create, Read, Update, Delete)
- ✅ (Own) Can only access own department/data
- ✅ (View) Read-only access
- ✅ (Approve) Approval rights only
- ❌ No Access

---

## 9. NOTIFIKASI DAN REMINDER - COMPREHENSIVE SYSTEM

### 9.1 Notification Rules & Triggers

```
┌─────────────────────────────────────────────────────────────┐
│  🔔 NOTIFICATION SYSTEM CONFIGURATION                       │
├─────────────────────────────────────────────────────────────┤
│  📤 PURCHASING MODULE                                       │
│  ├─ PO Created (Draft)                                      │
│  │  ├─ To: Purchasing Manager                               │
│  │  ├─ Channel: In-App + Email                              │
│  │  └─ Message: "New PO draft created - Review required"    │
│  │                                                          │
│  ├─ PO Sent to Supplier                                     │
│  │  ├─ To: PPIC, Warehouse, Manager                         │
│  │  ├─ Channel: In-App + Email                              │
│  │  ├─ Message: "PO-XXX sent to supplier [Name]"            │
│  │  └─ Special: If PO Kain → Notify "Cutting can start"    │
│  │            If PO Label → Notify "MO Released to all"     │
│  │                                                          │
│  ├─ PO Delivery Reminder (3 days before)                    │
│  │  ├─ To: Purchasing, Warehouse                            │
│  │  ├─ Channel: In-App + Email + WhatsApp                   │
│  │  └─ Message: "PO-XXX expected delivery: [Date]"          │
│  │                                                          │
│  └─ PO Overdue (Delivery date passed)                       │
│     ├─ To: Purchasing, Manager, Director                    │
│     ├─ Channel: In-App + Email + SMS (Director)             │
│     ├─ Priority: 🔴 HIGH                                    │
│     └─ Message: "URGENT: PO-XXX overdue! Follow up now"     │
│                                                             │
│  🏭 PPIC MODULE                                             │
│  ├─ MO Auto-Created (from PO Kain)                          │
│  │  ├─ To: PPIC Team                                        │
│  │  ├─ Channel: In-App + Email                              │
│  │  └─ Message: "New MO-XXX created (MODE: PARTIAL)"        │
│  │                                                          │
│  ├─ MO Released (from PO Label)                             │
│  │  ├─ To: PPIC, All Production Admin, Manager              │
│  │  ├─ Channel: In-App + Email + WhatsApp (Production)      │
│  │  ├─ Priority: ⚡ URGENT                                  │
│  │  └─ Message: "MO-XXX RELEASED! Week [X], Dest: [Y]"     │
│  │                                                          │
│  ├─ MO Approval Request                                     │
│  │  ├─ Workflow: PPIC → Supervisor → Manager → Director    │
│  │  ├─ Channel: In-App + Email                              │
│  │  └─ Auto-escalate: If not approved in 24h              │
│  │                                                          │
│  └─ SPK Generated                                           │
│     ├─ To: Admin Production (assigned dept)                 │
│     ├─ Channel: In-App + WhatsApp                           │
│     └─ Message: "New SPK-XXX assigned to [Dept]"            │
│                                                             │
│  🏭 PRODUCTION MODULE                                       │
│  ├─ SPK Delayed (Behind schedule)                           │
│  │  ├─ To: Admin Prod, Supervisor, PPIC, Manager            │
│  │  ├─ Channel: In-App + Email + WhatsApp                   │
│  │  ├─ Priority: ⚠️ HIGH                                    │
│  │  └─ Message: "SPK-XXX delayed by [X] days"               │
│  │                                                          │
│  ├─ Daily Production Input Reminder (15:00 WIB)             │
│  │  ├─ To: Admin Prod (if not input today)                  │
│  │  ├─ Channel: In-App + WhatsApp                           │
│  │  └─ Message: "Reminder: Input produksi hari ini"         │
│  │                                                          │
│  ├─ SPK Near Completion (90% progress)                      │
│  │  ├─ To: PPIC, Next Department Admin                      │
│  │  ├─ Channel: In-App                                      │
│  │  └─ Message: "SPK-XXX 90% done. Prepare next stage"      │
│  │                                                          │
│  └─ SPK Completed                                           │
│     ├─ To: PPIC, Manager, Next Department                   │
│     ├─ Channel: In-App + Email                              │
│     └─ Message: "✅ SPK-XXX completed. [X] pcs ready"      │
│                                                             │
│  🔧 REWORK & QC MODULE                                      │
│  ├─ High Defect Rate Alert (>5%)                            │
│  │  ├─ To: Admin Prod, Supervisor, QC, Manager              │
│  │  ├─ Channel: In-App + Email + WhatsApp (Manager)         │
│  │  ├─ Priority: 🔴 CRITICAL                                │
│  │  └─ Message: "[Dept] defect rate [X]%! Investigate!"    │
│  │                                                          │
│  ├─ Rework Task Assigned                                    │
│  │  ├─ To: Rework Operator, Supervisor                      │
│  │  ├─ Channel: In-App + WhatsApp                           │
│  │  └─ Message: "Rework task RW-XXX assigned"               │
│  │                                                          │
│  ├─ Rework Overdue (>24 hours in queue)                     │
│  │  ├─ To: Supervisor, Manager                              │
│  │  ├─ Channel: In-App + Email                              │
│  │  ├─ Priority: ⚠️ HIGH                                    │
│  │  └─ Message: "Rework RW-XXX aging >24h"                  │
│  │                                                          │
│  └─ QC Inspection Required                                  │
│     ├─ To: QC Inspector                                     │
│     ├─ Channel: In-App + WhatsApp                           │
│     └─ Message: "QC inspection needed for [Item]"           │
│                                                             │
│  📦 WAREHOUSE MODULE                                        │
│  ├─ Material Low Stock (<Min Stock)                         │
│  │  ├─ To: Purchasing, Warehouse Manager, PPIC              │
│  │  ├─ Channel: In-App + Email                              │
│  │  └─ Message: "[Material] below minimum stock"            │
│  │                                                          │
│  ├─ Material Critical Stock (<15% of Min)                   │
│  │  ├─ To: Purchasing, Manager, Director                    │
│  │  ├─ Channel: In-App + Email + SMS (Director)             │
│  │  ├─ Priority: 🔴 CRITICAL                                │
│  │  └─ Message: "CRITICAL: [Material] only [X] left!"       │
│  │                                                          │
│  ├─ Material Negative (Debt)                                │
│  │  ├─ To: Purchasing, Warehouse, PPIC, Manager, Director   │
│  │  ├─ Channel: All channels + SMS                          │
│  │  ├─ Priority: ⚫ EMERGENCY                               │
│  │  └─ Message: "DEBT: [Material] negative [X] units!"      │
│  │                                                          │
│  ├─ GRN Pending QC (>24 hours)                              │
│  │  ├─ To: QC Team, Warehouse Manager                       │
│  │  ├─ Channel: In-App + Email                              │
│  │  └─ Message: "GRN-XXX awaiting QC inspection"            │
│  │                                                          │
│  ├─ FG Ready for Shipment                                   │
│  │  ├─ To: Warehouse, Logistics, Manager                    │
│  │  ├─ Channel: In-App + Email                              │
│  │  └─ Message: "[X] CTN ready for Week [Y]"                │
│  │                                                          │
│  └─ Stock Opname Reminder (Monthly)                         │
│     ├─ To: All Dept Admin, Warehouse                        │
│     ├─ Channel: In-App + Email + WhatsApp                   │
│     ├─ Timing: 3 days before end of month                   │
│     └─ Message: "Reminder: Monthly SO due [Date]"           │
│                                                             │
│  ⚙️ SYSTEM MODULE                                           │
│  ├─ Backup Success                                          │
│  │  ├─ To: Developer, IT Admin                              │
│  │  ├─ Channel: In-App + Email                              │
│  │  └─ Message: "Database backup completed"                 │
│  │                                                          │
│  ├─ Backup Failed                                           │
│  │  ├─ To: Developer, IT Admin, Director                    │
│  │  ├─ Channel: All channels + SMS                          │
│  │  ├─ Priority: 🔴 CRITICAL                                │
│  │  └─ Message: "FAILED: Database backup error!"            │
│  │                                                          │
│  ├─ User Login from New Device                              │
│  │  ├─ To: User (own account)                               │
│  │  ├─ Channel: Email + SMS                                 │
│  │  └─ Message: "New login from [Device] at [Time]"         │
│  │                                                          │
│  └─ System Maintenance Schedule                             │
│     ├─ To: All Users                                        │
│     ├─ Channel: In-App + Email                              │
│     ├─ Timing: 24 hours before maintenance                  │
│     └─ Message: "System maintenance scheduled [DateTime]"   │
└─────────────────────────────────────────────────────────────┘
```

---

### 9.2 Notification Preference Settings (User-Configurable)

```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ NOTIFICATION PREFERENCES - USER SETTINGS                │
│  User: Pak Agung (Supervisor Sewing)                        │
├─────────────────────────────────────────────────────────────┤
│  📱 Delivery Channels                                       │
│  ├─ In-App Notification: [Toggle] ● ON ○ OFF                │
│  ├─ Email: [Toggle] ● ON ○ OFF                              │
│  │  └─ Email Address: agung@quty.com                        │
│  ├─ WhatsApp: [Toggle] ● ON ○ OFF                           │
│  │  └─ Phone: +62 812 3456 7890                             │
│  └─ SMS: [Toggle] ○ ON ● OFF (Cost: Rp 500/SMS)            │
│                                                             │
│  🔔 Notification Types (Enable/Disable by Category)         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Category         │ In-App │ Email │ WhatsApp │ SMS │   │
│  ├──────────────────┼────────┼───────┼──────────┼─────┤   │
│  │ SPK Assigned     │   ☑️   │  ☑️   │    ☑️    │  ☐  │   │
│  │ SPK Delayed      │   ☑️   │  ☑️   │    ☑️    │  ☐  │   │
│  │ SPK Completed    │   ☑️   │  ☐    │    ☐     │  ☐  │   │
│  │ High Defect Rate │   ☑️   │  ☑️   │    ☑️    │  ☑️ │   │
│  │ Rework Task      │   ☑️   │  ☐    │    ☑️    │  ☐  │   │
│  │ QC Inspection    │   ☑️   │  ☑️   │    ☐     │  ☐  │   │
│  │ Material Low     │   ☑️   │  ☑️   │    ☐     │  ☐  │   │
│  │ Approval Request │   ☑️   │  ☑️   │    ☑️    │  ☐  │   │
│  │ System Alert     │   ☑️   │  ☑️   │    ☐     │  ☐  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ⏰ Quiet Hours (Do Not Disturb)                            │
│  ├─ Enable DND: [Toggle] ● ON ○ OFF                         │
│  ├─ From: [Time] 22:00 WIB                                  │
│  ├─ To: [Time] 06:00 WIB                                    │
│  └─ Exception: [Checkboxes]                                 │
│     ├─ ☑️ Critical Alerts (Defect >10%, Material Debt)     │
│     ├─ ☑️ Emergency System Alerts                          │
│     └─ ☐ All Other Notifications                           │
│                                                             │
│  📊 Notification Digest (Summary Report)                    │
│  ├─ Daily Digest: [Toggle] ● ON ○ OFF                       │
│  │  ├─ Time: [Dropdown] 17:00 WIB (End of workday)         │
│  │  └─ Channel: Email only                                  │
│  │                                                          │
│  └─ Weekly Digest: [Toggle] ● ON ○ OFF                      │
│     ├─ Day: [Dropdown] Friday                               │
│     ├─ Time: 16:00 WIB                                      │
│     └─ Channel: Email + WhatsApp                            │
│                                                             │
│  [SAVE PREFERENCES] [RESET TO DEFAULT] [CANCEL]             │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. ADDITIONAL FEATURES - ENHANCEMENTS

### 10.1 Export & Import Functions

**Supported Formats**:
- **Excel (.xlsx)**: For data manipulation & analysis
- **PDF**: For formal reports & documentation
- **CSV**: For data exchange with external systems
- **JSON**: For API integration

**Export Examples**:

1. **Production Report Export**:
   - Daily production detail (per SPK, per operator)
   - Summary by department
   - Charts & graphs included in PDF
   - Raw data in Excel for pivot analysis

2. **Material BOM Export**:
   - Complete BOM structure
   - Material requirements per article
   - Cost breakdown
   - Supplier information

3. **Inventory Export**:
   - Stock levels by location
   - Stock movement history
   - Aging analysis
   - ABC classification

**Import Examples**:

1. **Material Master Bulk Upload** (Excel Template):
   ```
   Column A: Material Code
   Column B: Material Name
   Column C: Type
   Column D: UOM
   Column E: Min Stock
   Column F: Lead Time
   ... (20 columns total)
   ```

2. **BOM Import** (Structured Excel):
   ```
   Sheet 1: BOM Header
   Sheet 2: BOM Lines (Material List)
   Validation: Auto-check for duplicate/missing materials
   ```

---

### 10.2 Audit Trail & Data History

**Every transaction logged**:
- User who created/edited
- Timestamp (date & time)
- Old value vs New value
- IP Address & Device
- Reason for change (optional comment)

**Audit Log Example**:

```
┌─────────────────────────────────────────────────────────────┐
│  📜 AUDIT TRAIL - SPK-2026-00120                            │
├─────────────────────────────────────────────────────────────┤
│  Event History (Most Recent First)                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ [2026-01-06 16:45:23] COMPLETED                       │  │
│  │ User: Pak Agung (Supervisor Sewing)                   │  │
│  │ Action: Mark SPK as Completed                         │  │
│  │ Old Status: In Progress → New Status: Completed       │  │
│  │ Comment: "All targets achieved"                       │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ [2026-01-06 14:20:15] UPDATED                         │  │
│  │ User: Ibu Ani (Admin Sewing)                          │  │
│  │ Action: Input Daily Production (6 Jan)                │  │
│  │ Old Total: 420 pcs → New Total: 520 pcs               │  │
│  │ Daily: +100 pcs (Good: 97, Defect: 3)                 │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ [2026-01-04 11:30:40] EDITED                          │  │
│  │ User: Pak Budi (PPIC)                                 │  │
│  │ Action: Adjust SPK Target                             │  │
│  │ Old Target: 500 pcs → New Target: 517 pcs             │  │
│  │ Reason: "Increase buffer for anticipated defects"     │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ [2026-01-02 08:15:30] CREATED                         │  │
│  │ User: Pak Budi (PPIC)                                 │  │
│  │ Action: SPK Generated from MO-2026-00089              │  │
│  │ Target: 500 pcs | Article: AFTONSPARV                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  [EXPORT AUDIT LOG] [FILTER BY USER] [FILTER BY ACTION]    │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. INTEGRATION & API

### 11.1 External System Integration Points

```
ERP QUTY KARUNIA
      ↕️ API Integration
      ├─ 📧 Email Service (SMTP)
      │  └─ Notification emails, Reports
      │
      ├─ 📱 WhatsApp Business API
      │  └─ Real-time alerts to mobile
      │
      ├─ 📊 Power BI / Tableau
      │  └─ Advanced analytics dashboard
      │
      ├─ 🏦 Accounting System (Future)
      │  └─ COGS, Inventory value, PO payment
      │
      ├─ 🚛 Logistics System (Future)
      │  └─ Shipment tracking, Delivery order
      │
      └─ 🏢 IKEA ECIS (Future)
         └─ Order sync, Delivery confirmation
```

---

## 12. TRAINING & USER ADOPTION

### 12.1 Training Modules by Role

| Role | Training Duration | Topics Covered |
|------|-------------------|----------------|
| **Superadmin** | 2 days | Full system, User management, System config |
| **Director** | 0.5 day | Dashboard, Reports, Approval workflow |
| **Manager** | 1 day | Dashboard, Dept monitoring, Reports, Approval |
| **PPIC** | 2 days | MO creation, SPK generation, BOM, Material allocation |
| **Purchasing** | 1.5 days | PO creation (3 types), Supplier mgmt, GRN |
| **Warehouse** | 1.5 days | Material In/Out, FG receiving, Stock opname, Mobile scanner |
| **Admin Produksi** | 1 day | SPK view, Daily input production, Defect tracking |
| **QC** | 1 day | QC inspection, Rework module, Quality reports |
| **Supervisor** | 1 day | SPK monitoring, Approval, Team performance |

---

## 13. ROADMAP & FUTURE ENHANCEMENTS

### Phase 1: Core Completion (Current - Feb 2026)
- ✅ Dual-mode PO (Article BOM explosion) - **DONE**
- ✅ Flexible target system - **DONE**
- ✅ Rework module - **DONE**
- 🔄 Backend BOM explosion endpoint - **IN PROGRESS**
- 🔄 Supplier per material backend schema - **IN PROGRESS**

### Phase 2: Mobile & Integration (Mar 2026)
- 📱 Android FG Label app development
- 🔗 Bluetooth printer integration
- 📊 Advanced analytics dashboard
- 📧 Email notification system

### Phase 3: AI & Automation (Apr-May 2026)
- 🤖 Predictive material requirement
- 📈 Auto-reorder point adjustment
- 🎯 Defect pattern recognition
- 💰 Cost optimization suggestions

---

## 14. ✅ VALIDATION CHECKLIST

**Before Go-Live**:
- [ ] All user roles tested with correct permissions
- [ ] BOM cascade validation working (Output → Next Input)
- [ ] UOM conversion tested (Cutting Yard→Pcs, FG Box→Pcs)
- [ ] Material debt tracking accurate
- [ ] Rework workflow complete (Defect → Rework → Re-QC → Stock)
- [ ] Notification system tested (Email, In-app, SMS)
- [ ] Mobile app tested with Bluetooth printer
- [ ] Reports export correct (PDF, Excel)
- [ ] Data backup & restore procedure ready
- [ ] User training completed for all departments

---

<a name="material-flow-tracking"></a>
## 13. 📦 MATERIAL FLOW TRACKING - END-TO-END VISIBILITY

### 13.1 Complete Material Journey Visualization

**Purpose**: Track setiap material dari PO → Production → Finished Goods dengan full traceability.

#### Real-Time Material Flow Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 MATERIAL FLOW TRACKER - ARTICLE: AFTONSPARV (40551542)      │
│  MO: MO-2026-00089 | Target: 450 pcs | Week: W05               │
├─────────────────────────────────────────────────────────────────┤
│  🔄 FLOW VISUALIZATION (Left to Right Timeline)                 │
│                                                                  │
│  [PO] → [WH Main] → [Cutting] → [Emb] → [Sewing] → [Fin] → [FG]│
│   ✅      ✅         ✅        ✅      🔄        ⏳       ⏳    │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  📦 STAGE 1: PURCHASING (Material Procurement)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • PO Kain (PO-K-2026-00012): ✅ Received 2 Jan 2026       │  │
│  │   ├─ KOHAIR 70.4 YD → Stock: 125 YD (Surplus: +54.6 YD) │  │
│  │   ├─ JS BOA 4.7 YD → Stock: 15 YD (Surplus: +10.3 YD)   │  │
│  │   └─ POLYESTER 85.3 YD → Stock: 450 YD (✅ OK)           │  │
│  │                                                            │  │
│  │ • PO Label (PO-L-2026-00089): ✅ Received 3 Jan 2026      │  │
│  │   ├─ Hang Tag: 450 pcs (🔑 TRIGGER 2 - MO RELEASED)      │  │
│  │   ├─ Label EU: 450 pcs                                    │  │
│  │   └─ Sticker: 900 pcs                                     │  │
│  │                                                            │  │
│  │ • PO Accessories (PO-A-2026-00090): ✅ Partial            │  │
│  │   ├─ Thread: 2,500 CM (✅ OK)                             │  │
│  │   ├─ Filling: 24.3 kg (✅ OK)                             │  │
│  │   └─ Carton: 8 pcs (⚠️ Short 2 pcs - reorder)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📦 STAGE 2: WAREHOUSE MAIN (Material Stock)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Material Reserved for MO-00089:                            │  │
│  │ ├─ KOHAIR: 70.4 YD (Reserved from 125 YD stock)           │  │
│  │ ├─ Filling: 24.3 kg (Reserved from 45 kg stock)           │  │
│  │ ├─ Thread: 2,500 CM (Reserved from 5,000 CM stock)        │  │
│  │ └─ Status: ✅ All materials reserved                      │  │
│  │                                                            │  │
│  │ Material Issued to Production:                             │  │
│  │ • To Cutting: 70.4 YD fabrics (3 Jan 2026)                │  │
│  │ • To Sewing: 2,500 CM thread (4 Jan 2026)                 │  │
│  │ • To Finishing: 24.3 kg filling (5 Jan 2026)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🏭 STAGE 3: PRODUCTION (WIP Tracking)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [CUTTING] SPK-CUT-00120 (3 Jan - COMPLETED)               │  │
│  │ • Input: 70.4 YD fabrics                                   │  │
│  │ • Output: 500 pcs Body Parts (Target: 495) ✅             │  │
│  │ • Conversion: 70.4 YD → 500 pcs (0.1408 YD/pcs)           │  │
│  │ • Variance: +5 pcs buffer (1.0%) ✅ Within tolerance      │  │
│  │ • Waste: 0.8 YD fabric scrap (1.1%)                       │  │
│  │ • Transfer to: Embroidery (500 pcs sent)                  │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ [EMBROIDERY] SPK-EMB-00089 (4 Jan - COMPLETED)            │  │
│  │ • Input: 500 pcs Body Parts from Cutting                  │  │
│  │ • Process: Embroidery pattern applied                     │  │
│  │ • Output: 495 pcs Embroidered Body (Target: 495) ✅       │  │
│  │ • Defect: 5 pcs pattern error → Scrap                     │  │
│  │ • Transfer to: Sewing (495 pcs sent)                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ [SEWING] SPK-SEW-00120 (5-6 Jan - COMPLETED)              │  │
│  │ • Input: 495 pcs Embroidered Body from Embroidery         │  │
│  │ • Additional Material: 2,500 CM thread consumed           │  │
│  │ • Output: 520 pcs Sewn Body (Target: 517) ✅              │  │
│  │ • Good Output: 508 pcs (Yield: 97.7%)                     │  │
│  │ • Defect: 12 pcs → Rework: 10 recovered ✅                │  │
│  │ • Final Output: 518 pcs Skin Body                          │  │
│  │ • Transfer to: Finishing (518 pcs sent)                    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ [FINISHING - STAGE 1] SPK-FIN-STUFF-00045 (6 Jan - DONE)  │  │
│  │ • Input: 518 pcs Skin from Sewing                          │  │
│  │ • Additional Material:                                     │  │
│  │   ├─ Filling: 26.08 kg consumed (483 × 54g)               │  │
│  │   └─ Thread: 290 meter (483 × 60cm)                       │  │
│  │ • Target: 480 pcs (demand-driven)                          │  │
│  │ • Actual: 483 pcs stuffed                                  │  │
│  │ • Good Output: 473 pcs (97.9% yield)                      │  │
│  │ • Defect: 10 pcs → Rework: 8 recovered                    │  │
│  │ • Final: 481 pcs Stuffed Body                              │  │
│  │ • Stock: Remaining 35 pcs Skin (hold for next MO)         │  │
│  │ • Transfer to: Finishing Stage 2 (481 pcs)                │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ [FINISHING - STAGE 2] SPK-FIN-CLOSE-00046 (7 Jan - DONE)  │  │
│  │ • Input: 481 pcs Stuffed Body from Stage 1                │  │
│  │ • Additional Material: 480 pcs Hang Tag                    │  │
│  │ • Target: 470 pcs                                          │  │
│  │ • Actual: 472 pcs closed                                   │  │
│  │ • Good Output: 468 pcs (99.2% yield)                      │  │
│  │ • Defect: 4 pcs → Rework: 3 recovered                     │  │
│  │ • Final: 471 pcs Finished Doll                             │  │
│  │ • Transfer to: Packing (471 pcs ready)                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ [PACKING] SPK-PACK-00089 (7-8 Jan - IN PROGRESS 🔄)       │  │
│  │ • Input Available:                                         │  │
│  │   ├─ Finished Doll: 471 pcs (from Finishing)              │  │
│  │   └─ Baju: 500 pcs (from Sewing Baju stream)              │  │
│  │ • Constraint: MIN(471, 500) = 471 max sets                │  │
│  │ • Target: 465 pcs (urgency-based, exact)                  │  │
│  │ • Progress: 380/465 pcs (81.7%) 🔄                        │  │
│  │ • Packed: 6 CTN + partial 20 pcs                          │  │
│  │ • Expected completion: 8 Jan 2026                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📦 STAGE 4: WAREHOUSE FG (Final Stock)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Status: ⏳ Awaiting final completion from Packing          │  │
│  │                                                            │  │
│  │ Expected FG Stock:                                         │  │
│  │ • Complete Sets: 465 pcs                                   │  │
│  │ • Carton Configuration: 8 CTN (7×60 + 1×45 pcs)           │  │
│  │ • Pallet: 1 pallet (8 CTN)                                │  │
│  │ • Week: W05                                                │  │
│  │ • Destination: IKEA Distribution Center                   │  │
│  │ • Shipment Ready: 10 Feb 2026                              │  │
│  │                                                            │  │
│  │ Surplus Stock (Buffer):                                    │  │
│  │ ├─ Finished Doll: +6 pcs (471 - 465)                      │  │
│  │ └─ Baju: +35 pcs (500 - 465)                              │  │
│  │    → Will be used for future orders/replacement           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📊 MATERIAL EFFICIENCY SUMMARY                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Starting Material:                                         │  │
│  │ • Fabric: 70.4 YD purchased → 500 pcs cut                 │  │
│  │ • Filling: 24.3 kg purchased → 26.08 kg used              │  │
│  │ • Thread: 2,500 CM purchased → 2,790 CM used              │  │
│  │                                                            │  │
│  │ Final Achievement:                                         │  │
│  │ • MO Target: 450 pcs → Actual: 465 pcs ✅ (103.3%)        │  │
│  │ • Overall Yield: 93.0% (465 from 500 initial)             │  │
│  │ • Material Utilization:                                    │  │
│  │   ├─ Fabric: 99.1% (waste: 0.9%)                          │  │
│  │   ├─ Filling: 107% (variance due to manual stuffing)      │  │
│  │   └─ Thread: 111.6% (higher usage from rework)            │  │
│  │                                                            │  │
│  │ Quality Metrics:                                           │  │
│  │ • Total Defects Found: 41 pcs (4.0% of 1,018 total)       │  │
│  │ • Rework Success: 34 pcs recovered (82.9%) ✅             │  │
│  │ • Final Scrap: 7 pcs (0.7%) ✅ Excellent                  │  │
│  │ • COPQ (Cost of Poor Quality): Rp 385,000 (0.3% of COGS) │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🔍 TRACEABILITY ACTIONS                                        │
│  [TRACE SPECIFIC BATCH] [VIEW MATERIAL DEBT] [PRINT REPORT]    │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features**:
- ✅ **End-to-End Visibility**: Dari PO sampai FG dalam satu view
- ✅ **Real-Time Status**: Update otomatis setiap stage complete
- ✅ **Material Balance**: Track input vs output per stage
- ✅ **Variance Analysis**: Detect discrepancies immediately
- ✅ **Traceability**: Link dari carton FG balik ke PO original

---

### 13.2 QC 4-CHECKPOINT DETAILED WORKFLOW

**Complete Quality Control Flow** - As described in ILUSTRASI_WORKFLOW_LENGKAP.md:

```
┌─────────────────────────────────────────────────────────────────┐
│  ✅ QUALITY CONTROL - 4 CRITICAL CHECKPOINTS                    │
│  Article: AFTONSPARV | MO: MO-2026-00089                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔍 CHECKPOINT 1: AFTER CUTTING                                 │
│  Location: Cutting Department Exit                              │
│  Inspector: QC Staff A (Random Sampling 10%)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Check Items:                                               │  │
│  │ ├─ ☑️ Size accuracy (±2mm tolerance)                      │  │
│  │ ├─ ☑️ Edge cutting quality (no fray)                      │  │
│  │ ├─ ☑️ Pattern alignment (matching marks)                  │  │
│  │ └─ ☑️ Quantity verification                               │  │
│  │                                                            │  │
│  │ Inspection Result: 3 Jan 2026                              │  │
│  │ • Input Batch: 500 pcs Cut Body                            │  │
│  │ • Sample Size: 50 pcs (10%)                                │  │
│  │ • PASS: 48 pcs (96%) ✅                                    │  │
│  │ • MINOR: 2 pcs (4%) → Mark for careful sewing             │  │
│  │ • REJECT: 0 pcs                                            │  │
│  │ • Action: ✅ Release to Embroidery                         │  │
│  │ • QC Inspector Signature: _____________________            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🔍 CHECKPOINT 2: AFTER SEWING                                  │
│  Location: Sewing Department Exit                               │
│  Inspector: QC Staff B (100% Inline Inspection)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Check Items:                                               │  │
│  │ ├─ ☑️ Stitch quality (no loose thread)                    │  │
│  │ ├─ ☑️ Stitch per inch (SPI) standard                      │  │
│  │ ├─ ☑️ Seam strength (pull test)                           │  │
│  │ ├─ ☑️ Assembly accuracy (all parts attached)              │  │
│  │ └─ ☑️ Appearance (no wrinkle)                             │  │
│  │                                                            │  │
│  │ Inspection Result: 6 Jan 2026                              │  │
│  │ • Input Batch: 520 pcs Sewn Body                           │  │
│  │ • Inspection: 100% checked (inline during sewing)          │  │
│  │                                                            │  │
│  │ • PASS: 508 pcs (97.7%) ✅ → To Finishing                 │  │
│  │                                                            │  │
│  │ • MINOR DEFECT: 10 pcs (1.9%) → Rework Queue              │  │
│  │   └─ Issues: Loose thread (6), Misaligned stitch (4)      │  │
│  │                                                            │  │
│  │ • MAJOR DEFECT: 2 pcs (0.4%) → Scrap                      │  │
│  │   └─ Issues: Broken seam (1), Wrong assembly (1)          │  │
│  │                                                            │  │
│  │ • REWORK RESULT: 10 → 10 recovered (100%) ✅              │  │
│  │   └─ All minor defects successfully repaired              │  │
│  │                                                            │  │
│  │ • Final Good Output: 518 pcs (508 + 10 rework)            │  │
│  │ • Action: ✅ Release 518 pcs to Finishing                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🔍 CHECKPOINT 3: AFTER FINISHING (Stage 2)                     │
│  Location: Warehouse Finishing Exit                             │
│  Inspector: QC Staff C (100% Final Inspection)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Check Items:                                               │  │
│  │ ├─ ☑️ Stuffing quality (firmness check)                   │  │
│  │ ├─ ☑️ Shape consistency (no deform)                       │  │
│  │ ├─ ☑️ Closing quality (hidden stitches)                   │  │
│  │ ├─ ☑️ Hang tag attachment (secure)                        │  │
│  │ ├─ ☑️ Cleanliness (no dust/stain)                         │  │
│  │ └─ ☑️ Safety check (no sharp edges)                       │  │
│  │                                                            │  │
│  │ Inspection Result: 7 Jan 2026                              │  │
│  │ • Input Batch: 472 pcs Finished Doll                       │  │
│  │ • Inspection: 100% checked (mandatory final QC)            │  │
│  │                                                            │  │
│  │ • PASS: 468 pcs (99.2%) ✅ → To Packing                   │  │
│  │                                                            │  │
│  │ • MINOR DEFECT: 4 pcs (0.8%) → Quick Fix                  │  │
│  │   └─ Issues: Hang tag loose (3), Minor stain (1)          │  │
│  │                                                            │  │
│  │ • MAJOR DEFECT: 0 pcs ✅                                   │  │
│  │                                                            │  │
│  │ • REWORK RESULT: 4 → 3 recovered (75%)                    │  │
│  │   └─ 1 pcs stain tidak bisa dibersihkan → Scrap           │  │
│  │                                                            │  │
│  │ • Final Good Output: 471 pcs (468 + 3 rework)             │  │
│  │ • Action: ✅ Release 471 pcs to Packing                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🔍 CHECKPOINT 4: PRE-PACKING FINAL                             │
│  Location: Packing Department Entry                             │
│  Inspector: QC Staff D (Random + 100% Visual)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Check Items:                                               │  │
│  │ ├─ ☑️ Final appearance (overall quality)                  │  │
│  │ ├─ ☑️ Baju fit test (boneka + baju assembly)              │  │
│  │ ├─ ☑️ Label check (correct Week + Destination)            │  │
│  │ ├─ ☑️ Compliance check (EU safety standards)              │  │
│  │ └─ ☑️ Metal detector test (no needle left)                │  │
│  │                                                            │  │
│  │ Inspection Result: 7-8 Jan 2026                            │  │
│  │ • Finished Doll Available: 471 pcs ✅                      │  │
│  │ • Baju Available: 500 pcs ✅                               │  │
│  │                                                            │  │
│  │ • Assembly Test Sample: 20 sets (random)                   │  │
│  │   └─ Result: All 20 PASS ✅ (Fit perfect, labels correct) │  │
│  │                                                            │  │
│  │ • Metal Detector Test: 471 pcs tested                      │  │
│  │   └─ Result: All PASS ✅ (No metal detected)              │  │
│  │                                                            │  │
│  │ • EU Compliance Check:                                     │  │
│  │   ├─ CE marking: ✅ Present                                │  │
│  │   ├─ Age warning label: ✅ Correct (3+ years)             │  │
│  │   └─ Material safety cert: ✅ Valid                        │  │
│  │                                                            │  │
│  │ • Action: ✅ RELEASE FOR PACKING                           │  │
│  │   └─ Max sets to pack: 465 pcs (as per target)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  📊 OVERALL QC PERFORMANCE SUMMARY                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Total Inspection Points: 4 mandatory checkpoints           │  │
│  │ Total Items Inspected: 1,963 pcs (cumulative)             │  │
│  │                                                            │  │
│  │ Defect Summary by Checkpoint:                              │  │
│  │ ├─ CP1 (Cutting): 2 pcs minor (0.4% of 500)               │  │
│  │ ├─ CP2 (Sewing): 12 pcs defect (2.3% of 520)              │  │
│  │ ├─ CP3 (Finishing): 4 pcs defect (0.8% of 472)            │  │
│  │ └─ CP4 (Packing): 0 pcs defect (0.0%) ✅                  │  │
│  │                                                            │  │
│  │ Total Defects: 18 pcs                                      │  │
│  │ Defect Rate: 0.9% ✅ Excellent (target: <2%)              │  │
│  │                                                            │  │
│  │ Rework Performance:                                        │  │
│  │ ├─ Total Sent to Rework: 14 pcs                           │  │
│  │ ├─ Successfully Recovered: 13 pcs (92.9%) ✅              │  │
│  │ └─ Final Scrap: 4 pcs (0.2% of total production)          │  │
│  │                                                            │  │
│  │ Compliance Status:                                         │  │
│  │ • All checkpoints PASSED ✅                                │  │
│  │ • Safety standards MET ✅                                  │  │
│  │ • Ready for customer delivery ✅                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [EXPORT QC REPORT] [PRINT CERTIFICATES] [SEND TO CUSTOMER]    │
└─────────────────────────────────────────────────────────────────┘
```

**Integration Notes**:
- QC checkpoints auto-triggered saat department complete daily input
- Defect auto-create rework ticket dengan full traceability
- Failed items dapat di-track dari customer complaint balik ke specific batch
- Metal detector integration untuk needle detection (safety critical)

---

<a name="timeline-gantt"></a>
## 14. 📅 TIMELINE & GANTT CHART - PROJECT VIEW

### 14.1 MO Timeline Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 PRODUCTION TIMELINE - MO-2026-00089 (AFTONSPARV)            │
│  Target: 450 pcs | Period: 1-10 Feb 2026                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📅 GANTT CHART VIEW (Interactive)                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          │ 1│ 2│ 3│ 4│ 5│ 6│ 7│ 8│ 9│10│               │  │
│  │ Process  │Mo│Tu│We│Th│Fr│Sa│Su│Mo│Tu│We│ Progress      │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │PO Kain   │██│  │  │  │  │  │  │  │  │  │ ✅ RECEIVED   │  │
│  │          │✅│  │  │  │  │  │  │  │  │  │ (2 Jan)       │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │PO Label  │  │██│  │  │  │  │  │  │  │  │ ✅ RECEIVED   │  │
│  │🔑TRIGGER │  │✅│  │  │  │  │  │  │  │  │ (3 Jan)       │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │Cutting   │  │  │██│██│  │  │  │  │  │  │ ✅ DONE       │  │
│  │(Body)    │  │  │✅│✅│  │  │  │  │  │  │ 500/495 pcs   │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │Embroider │  │  │  │██│██│  │  │  │  │  │ ✅ DONE       │  │
│  │          │  │  │  │✅│✅│  │  │  │  │  │ 495/495 pcs   │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │Sewing    │  │  │  │  │██│██│  │  │  │  │ ✅ DONE       │  │
│  │(Body)    │  │  │  │  │✅│✅│  │  │  │  │ 518/517 pcs   │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │Finishing │  │  │  │  │  │██│██│  │  │  │ ✅ DONE       │  │
│  │(2-Stage) │  │  │  │  │  │✅│✅│  │  │  │ 471/470 pcs   │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │Packing   │  │  │  │  │  │  │██│██│  │  │ 🔄 PROGRESS   │  │
│  │          │  │  │  │  │  │  │🔄│🔄│  │  │ 380/465 (82%) │  │
│  ├──────────┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼───────────────┤  │
│  │FG Ready  │  │  │  │  │  │  │  │  │██│  │ ⏳ SCHEDULED  │  │
│  │          │  │  │  │  │  │  │  │  │⏳│  │ (Expected 9th)│  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🎯 Critical Path: PO Label → Release ALL depts (bottleneck)    │
│  ⚡ Lead Time Saved: 3 days (Early cutting start with PO Kain)  │
│                                                                  │
│  📊 Progress Metrics:                                           │
│  • Total Days: 10 days (Plan) vs 8.5 days (Actual) ✅          │
│  • On-Time Delivery: 96% probability (1.5 days buffer)          │
│  • Current Status: Day 8 of 10 (80% timeline elapsed)           │
│  • Remaining Work: 85 pcs packing (1 day) + FG (0.5 day)        │
│                                                                  │
│  [ZOOM IN] [EXPORT GANTT] [PRINT] [SHARE WITH TEAM]            │
└─────────────────────────────────────────────────────────────────┘
```

### 14.2 Multi-MO Dashboard Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 PRODUCTION MASTER TIMELINE - ALL ACTIVE MOs                 │
│  Week: W05 2026 (27 Jan - 2 Feb)                               │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [All Articles ▾] [All Depts ▾] [Show: Active ●]      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MO-00089 (AFTONSPARV - 450 pcs)                           │  │
│  │ ████████████████████████████████░░ 80% ✅ On Track        │  │
│  │ Start: 2 Jan | End: 10 Feb | Days Remaining: 2            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ MO-00090 (KRAMIG - 600 pcs)                               │  │
│  │ ██████████████████░░░░░░░░░░░░░░ 60% 🔄 In Progress       │  │
│  │ Start: 4 Jan | End: 14 Feb | Days Remaining: 6            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ MO-00091 (GOSIG GOLDEN - 800 pcs)                         │  │
│  │ ████████░░░░░░░░░░░░░░░░░░░░░░░░ 25% ⚠️ Risk of Delay   │  │
│  │ Start: 5 Jan | End: 18 Feb | Delayed by: 2 days          │  │
│  │ Issue: Material shortage (KOHAIR -45 YD)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🎯 Weekly Overview:                                            │
│  • Total Active MOs: 12                                         │
│  • On Track: 8 MOs (66.7%) ✅                                  │
│  • At Risk: 3 MOs (25.0%) ⚠️                                   │
│  • Delayed: 1 MO (8.3%) 🔴                                     │
│  • Average Completion: 68.5%                                    │
│                                                                  │
│  📅 Upcoming Deadlines (Next 7 Days):                           │
│  • 8 Feb: MO-00089 (AFTONSPARV) - FG Ready ✅                  │
│  • 10 Feb: MO-00087 (DJUNGELSKOG) - 350 pcs                    │
│  • 12 Feb: MO-00088 (BLAHAJ) - 200 pcs                         │
│                                                                  │
│  [REFRESH] [EXPORT] [SEND REPORT TO MANAGEMENT]                │
└─────────────────────────────────────────────────────────────────┘
```

---

<a name="barcode-label"></a>
## 15. 📱 BARCODE & LABEL SYSTEM - COMPREHENSIVE

### 15.1 Barcode Standards & Format

**Used Throughout System**:
- **Material**: MAT-{Type}-{Code}-{BatchID}
  - Example: MAT-RAW-IKHR504-20260102-001
- **WIP**: WIP-{Dept}-{Article}-{SPKDate}-{SeqNo}
  - Example: WIP-SEW-40551542-20260105-001
- **Finished Goods**: FG-{Article}-{Week}-{BoxNo}-{Date}
  - Example: FG-40551542-W05-001-20260208
- **Carton Label**: CTN-{Article}-{Week}-{BoxNo}-{TotalBoxes}
  - Example: CTN-40551542-W05-003-008 (Box 3 of 8)

### 15.2 Mobile Barcode Scanner Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  📱 MOBILE BARCODE SCANNER APP                                  │
│  User: Warehouse Staff | Location: Packing Area                │
├─────────────────────────────────────────────────────────────────┤
│  🔍 SCAN MODE SELECTION                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [📥 Material IN]  [📤 Material OUT]  [📦 FG Receiving]   │  │
│  │                                                            │  │
│  │ [🏷️ Label Print]  [✅ QC Check]  [📊 Stock Count]       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🎯 ACTIVE SCAN: FG Receiving Mode                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [CAMERA VIEWFINDER - ACTIVE]                               │  │
│  │                                                            │  │
│  │         ┌─────────────────┐                                │  │
│  │         │  ▐║║║║║║║║║║║  │  ← Align barcode                 │  │
│  │         │  ▐║║║║║║║║║║║  │                                  │  │
│  │         └─────────────────┘                                │  │
│  │                                                            │  │
│  │  [TAP TO SCAN] or Auto-scan when detected                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📋 SCANNED HISTORY (Last 5):                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ✅ FG-40551542-W05-007-20260208 (Box 7 - 60 pcs)          │  │
│  │ ✅ FG-40551542-W05-006-20260208 (Box 6 - 60 pcs)          │  │
│  │ ✅ FG-40551542-W05-005-20260208 (Box 5 - 60 pcs)          │  │
│  │ ✅ FG-40551542-W05-004-20260208 (Box 4 - 60 pcs)          │  │
│  │ ✅ FG-40551542-W05-003-20260208 (Box 3 - 60 pcs)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📊 SESSION SUMMARY:                                            │
│  • Total Boxes Scanned: 7 boxes                                 │
│  • Total Pcs: 420 pcs (7 × 60)                                  │
│  • SPK: PACK-2026-00089                                         │
│  • Expected Total: 465 pcs (8 boxes)                            │
│  • Remaining: 1 box (45 pcs)                                    │
│                                                                  │
│  [🔄 SYNC TO SERVER] [📝 ADD NOTE] [✅ COMPLETE BATCH]         │
└─────────────────────────────────────────────────────────────────┘
```

**Auto-Actions After Scan**:
1. FG stock updated real-time
2. Carton location recorded (bin assignment)
3. Shipment readiness calculated
4. Notification sent to logistics when complete

---

<a name="security"></a>
## 16. 🔒 SECURITY & FRAUD PREVENTION

### 16.1 Critical Security Features

**Multi-Layer Authentication**:
```
┌─────────────────────────────────────────────────────────────────┐
│  🔐 LOGIN SECURITY - MULTI-FACTOR AUTHENTICATION                │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: Username & Password                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Username: [agung_sewing]                                   │  │
│  │ Password: [••••••••••]                                     │  │
│  │ [LOGIN]                                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Step 2: OTP Verification (for sensitive roles)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ OTP Code sent to: +62 812-XXXX-7890                        │  │
│  │ Enter 6-digit code: [______]                               │  │
│  │ [VERIFY]                                                    │  │
│  │ Code expires in: 2:45                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Step 3: Device Fingerprint (Auto-captured)                     │
│  • Browser: Chrome 120.0 on Windows 11                          │
│  • IP Address: 192.168.1.45 (Internal Network)                  │
│  • Location: Tangerang, Indonesia                               │
│  • Device ID: WIN-PROD-SRV-012                                  │
│                                                                  │
│  ✅ Login Successful - Session Active                           │
└─────────────────────────────────────────────────────────────────┘
```

### 16.2 Fraud Detection & Prevention

**Automated Anomaly Detection**:

```
┌─────────────────────────────────────────────────────────────────┐
│  🚨 FRAUD DETECTION ALERT                                       │
│  Severity: ⚠️ MEDIUM - Requires Review                         │
├─────────────────────────────────────────────────────────────────┤
│  Anomaly Detected: Unusual Stock Adjustment                     │
│                                                                  │
│  Details:                                                        │
│  • User: warehouse_staff_3                                      │
│  • Action: Stock Adjustment (Manual)                            │
│  • Material: [IKHR504] KOHAIR D.BROWN                           │
│  • Adjustment: -85 YD (Large quantity)                           │
│  • Reason Given: "Physical count discrepancy"                   │
│  • Timestamp: 5 Feb 2026 18:45 (After working hours) ⚠️        │
│  • Approver: None (pending) ⚠️                                  │
│                                                                  │
│  🔍 System Analysis:                                            │
│  ├─ Average Adjustment: 5-10 YD (This: 85 YD) 🚨 17x higher    │
│  ├─ Time Pattern: 93% adjustments during work hours 🚨         │
│  ├─ User History: 2 similar large adjustments in last month    │
│  └─ Material Value: Rp 1,062,500 (~$85) 🚨 High value          │
│                                                                  │
│  ⚡ Recommended Actions:                                         │
│  1. Require Manager approval (mandatory)                        │
│  2. Request supporting documentation (photo of physical count)  │
│  3. Schedule follow-up physical audit                           │
│  4. Escalate to Director if >Rp 1M                              │
│                                                                  │
│  [APPROVE WITH REVIEW] [REJECT & INVESTIGATE] [ESCALATE]        │
└─────────────────────────────────────────────────────────────────┘
```

**Key Security Controls**:
1. **Segregation of Duties**: No single user can create & approve critical transactions
2. **Approval Limits**: Tiered approval based on value (Supervisor < Manager < Director)
3. **Dual Custody**: Material debt must be approved by 2 people (PPIC + Purchasing)
4. **Time-Based Lock**: Cannot edit production data older than 48 hours without SPV approval
5. **IP Whitelist**: Critical functions only accessible from factory network
6. **Audit Log**: Every action logged with user, timestamp, IP, device, old/new value

---

**END OF DOCUMENT**

Dokumen ini memberikan gambaran **lengkap dan detail** tentang tampilan, fitur, dan workflow UI/UX sistem ERP Quty Karunia. Setiap section dirancang dengan fokus pada:
- ✅ **User-friendly**: Intuitif dan mudah dipahami
- ✅ **Efficient**: Minimalisir manual input
- ✅ **Accurate**: Validasi otomatis mencegah error
- ✅ **Flexible**: Adapt to real production scenarios
- ✅ **Traceable**: Full audit trail untuk accountability

**Version**: 4.0 | **Last Updated**: 4 Februari 2026