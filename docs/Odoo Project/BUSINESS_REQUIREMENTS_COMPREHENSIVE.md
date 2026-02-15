# 🏭 DOKUMEN REQUIREMENTS & PAIN POINTS - PT QUTY KARUNIA
## Untuk Gap Analysis Consultation dengan ERP Vendor

**Perusahaan**: PT Quty Karunia  
**Industri**: Soft Toys Manufacturing (B2B Export - Supplier IKEA)  
**Jenis Dokumen**: Business Requirements & Pain Points untuk Gap Analysis Phase  
**Disusun Oleh**: IT Lead - Daniel Rizaldy  
**Tanggal**: 13 Februari 2026  
**Target**: ERP Vendor Project Director & Business Analyst  
**Status**: ✅ SIAP UNTUK EVALUASI  

---

## 📋 DAFTAR ISI

1. [Ringkasan Eksekutif](#executive-summary)
2. [Profil Perusahaan](#company-profile)
3. [Pain Points Saat Ini](#pain-points)
4. [Business Functions Yang Dibutuhkan](#requirements)
5. [Proses Bisnis Unik](#unique-processes)
6. [Kriteria Sukses](#success-criteria)
7. [Definisi Scope Project](#project-scope)
8. [Langkah Selanjutnya](#next-steps)

---

<a name="executive-summary"></a>
## 📊 1. RINGKASAN EKSEKUTIF

### Konteks Project

PT Quty Karunia adalah manufacturer soft toys dengan **customer utama IKEA** (80% revenue). Perusahaan menghadapi **inefficiency operasional** akibat sistem manual berbasis Excel dan kertas, serta **pengalaman implementasi ERP sebelumnya yang gagal** karena tidak sesuai dengan workflow bisnis yang kompleks, dan kemampuan user (admin) dalam pengerjaan menggunakan ERP.

### Tujuan Project

Implementasi **Integrated ERP System** yang **disesuaikan** dengan workflow Quty untuk:
- ✅ Menggantikan sistem manual dengan **single source of truth database**
- ✅ Mengintegrasikan **Purchasing, Production, Warehouse, dan QC** dalam satu platform
- ✅ Menyediakan **real-time visibility** untuk Management dan Department Heads
- ✅ Mengurangi **human error** dari 20% → <2%
- ✅ **Adopsi User tinggi** (pembelajaran mudah, tidak ada resistance dari team)

### Tantangan Utama

⚠️ **CRITICAL**: Soft toys manufacturing memiliki **karakteristik unik** yang berbeda dari manufacture standar:

1. **Dual Purchase Order System** - 2 jenis Purchase Order yang trigger produksi
2. **Complex Multi-Unit** - 30+ material per artikel dengan unit berbeda (YARD, GRAM, CM, PCS)
3. **2-Stage Internal Processing** - Internal conversion tanpa surat jalan formal
4. **Flexible Target System** - Department target dapat berbeda dari overall target (buffer management)
5. **Real-Time Work In Progress** - Parallel production dengan batch-based transfer
6. **Quality Control Loop** - Rework workflow dengan recovery tracking

---

<a name="company-profile"></a>
## 🏭 2. PROFIL PERUSAHAAN

### Informasi Umum

| Aspek | Detail |
|-------|--------|
| **Nama Perusahaan** | PT Quty Karunia |
| **Industri** | Soft Toys Manufacturing (Discrete Manufacturing) |
| **Tahun Berdiri** | 2010 (15+ tahun operational experience) |
| **Customer Utama** | IKEA (80% revenue), Others B2B Export (20%) |
| **Lokasi** | Indonesia |
| **Total Karyawan** | ~2000 |

### Skala Operasional

**Tipe Manufacturing**: Discrete Manufacturing dengan Complex Assembly

**Alur Produksi**: 6-Stage Sequential Process
```
Cutting → Embroidery* → Sewing → Finishing (2-stage) → Packing → Finished Goods
         (internal OR vendor)   (Stuffing + Closing)

*Embroidery: Opsional, bisa dikerjakan internal factory atau dikirim ke vendor eksternal
             Jika vendor, proses: Cutting → Kirim ke Vendor → Terima dari Vendor → Sewing
```

**Pola Order**: Weekly delivery schedule (W01-2026, W02-2026, dst.)

**Standar Kualitas**: IKEA Compliance (STRICT - 95%+ OTD required)

### Struktur Organisasi

**Departemen Utama**:
- **Purchasing** (3 specialists): Fabric, Label, Accessories (termasuk PO untuk vendor embroidery)
- **Warehouse** (3 types): Main, Finishing Internal, Finished Goods
- **Produksi** (5 departments): Cutting, Sewing, Finishing, Packing, QC
- **Embroidery**: Internal (jika ada) ATAU Vendor Eksternal (outsourced)
- **Data Entry**: Staff untuk input hasil produksi dan vendor embroidery (jika menggunakan vendor)
- **Management**: Director, GM, Managers

**Workflow Utama**: Purchasing → Warehouse → Production → Finished Good

**Total Staff**: ~40 office staff + ~1960 production workers

---

<a name="pain-points"></a>
## ❌ 3. PAIN POINTS SAAT INI

### 3.1 11 Critical Pain Points

| # | Pain Point | Business Impact |
|---|------------|-----------------|
| 1 | **Manual Data Entry** | Laporan lambat 3-5 hari |
| 2 | **Real-Time Material Unknown** | Produksi STOP tiba-tiba |
| 3 | **Work Order Tracking Manual** | Late delivery → penalty |
| 4 | **Finished Goods Verification Sulit** | Customer complaints |
| 5 | **No Clear Approval Process** | Fraud risk, no audit trail |
| 6 | **Monthly Closing Lambat** | Management decision delayed |
| 7 | **Warehouse Finishing Chaos** | Material waste |
| 8 | **Unit Conversion Errors** | Inventory discrepancy |
| 9 | **Production Target Rigid** | Shortage karena defect |
| 10 | **Defect Tidak Tertrack** | No root cause analysis |
| 11 | **Previous ERP Implementation Failure** | Admin trauma, resistance |

### 3.2 Root Cause Analysis

**Current State**: 7+ Fragmented Systems
```
┌──────────────────────────────────────────────────────────────┐
│  Purchasing → WhatsApp group + Excel tracker                 │
│    ↓                                                          │
│  Production → Paper forms + manual reporting                 │
│    ↓                                                          │
│  Warehouse → Manual logbook (3 different books!)             │
│    ↓                                                          │
│  QC → Paper checklist (lost after 3 months)                  │
│    ↓                                                          │
│  Finance → RE-ENTRY semua data manual (DOUBLE WORK!)         │
└──────────────────────────────────────────────────────────────┘
```

**Consequences**:
- ⚠️ Re-entry same data **3-4 kali** (Purchasing → Production → Warehouse → Finance)
- ⚠️ No single source of truth → **conflict data** antara departemen
- ⚠️ Laporan ke Management **always outdated** (data 3-5 hari yang lalu)
- ⚠️ Audit trail **tidak ada** (siapa approve? kapan? kenapa?)

### 3.3 Detail Pain Point #11: Previous ERP Implementation Failure

**Background**: PT Quty pernah implementasi ERP 2 tahun lalu dan **GAGAL TOTAL**

**Root Cause Kegagalan**:
- ❌ Vendor tidak memahami **complexity soft toys manufacturing**
- ❌ Sistema "force-fit" standard tanpa customization:
  - Tidak ada Dual Purchase Order feature
  - Tidak ada Flexible Target per department
  - Tidak ada customization untuk **Dual Trigger System**, **Flexible Target**, **2-Stage Finishing**
- ❌ Training tidak adequate (1 hari training untuk 40 staff - TIDAK CUKUP!)
- ❌ Support post-implementation buruk, banyak bug tidak terselesaikan
- ❌ Change management gagal, resistance tinggi dari admin

**Impact ke Tim**:
- 😰 Admin sekarang **trauma dengan ERP** (takut sistem baru akan sama gagalnya)
- 🤔 Management **sangat skeptis** dengan vendor ERP (takut buang uang lagi)
- 🚫 Strong resistance jika coba implement ERP baru tanpa **proof yang solid**

**Lesson Learned & Expectation ke Vendor Baru**:
- ✅ **Proper customization** untuk 7 unique features (bukan "nanti dibiasakan pakai cara standard")
- ✅ **Adequate training** dengan timeline realistic (minimum 2 minggu hands-on training)
- ✅ **Change management approach** yang proper (involve user dari awal, bukan surprise deployment)
- ✅ **Strong post-implementation support** dengan SLA clear (fast response, not abandon project)
- ✅ **Proof of concept** untuk critical features sebelum full implementation (mitigate risk)

**Dampak Operasional**:
- Lead time: 25 hari (target: 18 hari)
- On-time delivery: 75% (target: 95%)
- Inventory accuracy: 82% (target: 98%)
- Manual reporting time: 15 jam/minggu (target: 1 jam)

---

<a name="requirements"></a>
## 📋 4. BUSINESS FUNCTIONS YANG DIBUTUHKAN

### 4.1 Core Business Capabilities

| Kategori Function | Scope | Priority |
|-------------------|-------|----------|
| **1. Purchase Management** | 3 parallel streams (Fabric, Label, Accessories) | 🔴 CRITICAL |
| **2. Production Management** | Production order creation, Recipe/formula management, Routing workflow | 🔴 CRITICAL |
| **3. Inventory & Warehouse** | 3-warehouse types, Multi-unit conversions, Stock movements | 🔴 CRITICAL |
| **4. Quality Control** | 4-checkpoint inspection, Rework/Repair workflow | 🟠 HIGH |
| **5. Production Planning** | Weekly scheduling, Capacity planning (handled by Purchasing flow) | 🟠 HIGH |
| **6. Reporting & Dashboard** | Real-time KPI, Management dashboard | 🟠 HIGH |
| **7. User Access Control** | Role-based access, Approval workflow | 🟡 MEDIUM |
| **8. Product Tracking** | Finished Goods barcode/QR, Pallet system | 🟡 MEDIUM |
| **9. Mobile Application** | Production input, FG receiving via Android | 🟢 LOW (Nice-to-have) |

### 4.2 Key Functional Requirements

#### A. Purchase Management
- **Dual Purchase Order System**: PO Fabric (Trigger 1) dan PO Label (Trigger 2) unlock production stages
- **3 Specialist Workflow**: Parallel purchasing untuk Fabric, Label, & Accessories
- **Vendor Management**: Supplier database, Lead time tracking, PO history
- **Material Receiving**: Goods Receipt dengan unit conversion validation

#### B. Production Management
- **Product Recipe**: Multi-level Bahan (daftar material) dengan 30+ material per artikel
- **Production Order Workflow**: 2 modes (PARTIAL → RELEASED) based on PO Label status
- **Auto-Generate Work Orders**: 1 Production Order → 1 Work Order per department (auto-explode)
- **Flexible Target System**: Work Order target dapat berbeda dari Production Order target (buffer allocation)
- **Routing**: Optional embroidery step, 2-stage finishing
- **Workflow**: Purchasing is the main trigger for production (no separate production planning department)

#### C. Inventory & Warehouse
- **3 Main Warehouse Types**:
  - Main Warehouse (Raw materials)
  - Finishing Warehouse (Internal WIP: Skin → Stuffed Body)
  - Finished Goods Warehouse (Ready to ship - organized per pallet)
- **Department-Level Warehouses**: SETIAP departemen produksi punya warehouse/location sendiri:
  - Warehouse Cutting (WIP stock per cutting work order)
  - Warehouse Embroidery (WIP stock embroidery - internal atau return dari vendor)
  - Warehouse Sewing (WIP stock sewing - Body & Baju separate)
  - Warehouse Finishing (dijelaskan di atas - 2 stage)
  - Warehouse Packing (WIP ready-to-pack)
  - **Stock Opname**: Setiap departemen melakukan physical count regular untuk validasi inventory
- **Multi-Unit Handling**: YARD, GRAM, CM, PCS, BOX dengan auto-conversion
- **Real-Time WIP Tracking**: Inter-department stock movements
- **Material Debt System**: Negative stock allowed dengan alert & control

#### D. Quality Control
- **4-Checkpoint Inspection**: Cutting, Sewing, Finishing, Packing
- **Defect Recording**: Per work order, per admin, per defect type
- **Rework Workflow**: Defect → QC → Repair → Re-QC → Approve
- **Cost of Poor Quality Analysis**: COPQ tracking

#### E. Production Planning
- **Weekly Scheduling**: Week-based planning (W01-2026, W02-2026) managed by Purchasing
- **Multi-Destination Management**: Belgium, Sweden, USA, dll.
- **Capacity Planning**: Workload balancing per department
- **Material Availability Check**: Before production order validation
- **Note**: Production planning integrated dengan Purchasing workflow (Purchasing → Warehouse → Production → FG)

### 4.3 Kebutuhan Reporting & Analytics

**Real-Time Dashboards**:
- **Management Dashboard**: OTD%, Inventory value, WIP status, Defect rate
- **Production Dashboard**: Work order progress per department, Output vs Target
- **Purchasing Dashboard**: PO status, Vendor performance, Material availability
- **Quality Dashboard**: Defect trends, COPQ, Rework recovery rate

**Standard Reports**:
- Daily production report (output per department)
- Weekly shipment plan vs actual
- Monthly inventory aging
- Quarterly defect analysis & root cause

---

<a name="unique-processes"></a>
## 🔥 5. PROSES BISNIS UNIK

### 5.1 Dual Purchase Order System (CRITICAL!)

**Business Context**: 
- Customer IKEA butuh info **Week** (W01-2026) dan **Destination** (Belgium/Sweden/USA)
- Info ini ADA di **PO Label** (printed on label)
- Tapi PO Label **lead time lama** (7-10 hari) vs PO Fabric cepat (3-5 hari)
- Jika tunggu Label dulu baru produksi → **LATE 5 hari!**

**Business Solution**:

```
DUAL TRIGGER LOGIC:
═══════════════════════════════════════════════════════════════

TRIGGER 1: PO FABRIC arrives (Day 1)
───────────────────────────────────────────────────────────────
System Action:
├─ Create Production Order (PO-001)
├─ Status: PARTIAL (⚠️ Not fully released yet)
├─ Week: TBD (tunggu Label)
├─ Destination: TBD (tunggu Label)
└─ Departments Unlocked: Cutting, Embroidery

Business Rule:
├─ Cutting: CAN START ✅ (fabric ready)
├─ Embroidery: CAN START ✅ (can process cut body)
├─ Sewing: BLOCKED ❌ (need Label info first)
├─ Finishing: BLOCKED ❌
└─ Packing: BLOCKED ❌

Material Status:
├─ Fabric: RESERVED for PO-001
├─ Accessories: On-hold (belum kepakai)
└─ Label: Not yet ordered


TRIGGER 2: PO LABEL arrives (Day 5)
───────────────────────────────────────────────────────────────
System Action:
├─ Update Production Order PO-001
├─ Status: RELEASED ✅ (fully released!)
├─ Week: W05-2026 (from PO Label)
├─ Destination: Belgium (from PO Label)
└─ ALL Departments Unlocked

Business Rule:
├─ Cutting: Continue work ✅
├─ Embroidery: Continue work ✅
├─ Sewing: NOW UNLOCKED ✅
├─ Finishing: NOW UNLOCKED ✅
└─ Packing: NOW UNLOCKED ✅

Auto-Actions:
├─ Generate Work Orders for ALL departments
├─ Week & Destination auto-inherited (read-only)
├─ Material allocation finalized
└─ Label material RESERVED
```

**Business Impact**:
- ⚡ Time saved: **5 hari** per order (early start Cutting & Embroidery)
- 📦 On-time delivery improvement: **+15%**

**What System MUST Support**:
1. ✅ Track 2 different PO types (Fabric vs Label) yang trigger same Production Order
2. ✅ Production Order punya 2 states: PARTIAL (some dept allowed) dan RELEASED (all dept allowed)
3. ✅ Department lock/unlock mechanism based on PO status
4. ✅ Week & Destination fields auto-inherited dari PO Label (cannot be manually changed)
5. ✅ Alert/notification when PO Label arrived → Status change to RELEASED

**Questions for Vendor**:
- Q: Bagaimana system handle 2 PO yang trigger 1 production order?
- Q: Apakah bisa configure department-specific permissions berdasarkan status?
- Q: Bagaimana logic auto-inherit Week & Destination dari PO Label?
- Q: Apakah built-in atau perlu customization?

---

### 5.2 Flexible Target System (HIGH!)

**Business Context**:
- Customer minta **exact quantity** (contoh: 480 pcs, TIDAK BOLEH lebih/kurang)
- Tapi setiap department punya **defect rate berbeda** (Cutting 10%, Sewing 15%, dll)
- Jika target semua dept sama → **PASTI shortage** karena defect!
- Solusi: **Buffer per department** sesuai historical defect rate

**Business Solution**:

```
FLEXIBLE TARGET EXAMPLE:
═══════════════════════════════════════════════════════════════
Customer Order: 480 pcs Boneka IKEA (EXACT!)

Production Order (Overall):
├─ Target: 480 pcs (FIX - tidak boleh berubah)
└─ Auto-cascade ke departments dengan buffer:

Department Work Orders:
┌────────────────────────────────────────────────────────┐
│ 1. CUTTING                                             │
│    └─ Target: 528 pcs (+10% buffer)                    │
│       Logic: 480 × 1.10 = 528                          │
│       Reason: Historical waste 10%                     │
│                                                        │
│ 2. EMBROIDERY (Optional)                               │
│    └─ Target: 516 pcs (+7.5% buffer)                   │
│       Logic: 480 × 1.075 = 516                         │
│       Reason: Historical defect 7.5%                   │
│                                                        │
│ 3. SEWING (Body + Baju)                                │
│    └─ Target: 552 pcs (+15% buffer) ⚠️ HIGHEST!        │
│       Logic: 480 × 1.15 = 552                          │
│       Reason: Highest defect rate dept                 │
│                                                        │
│ 4. WAREHOUSE FINISHING                                 │
│    └─ Target: 504 pcs (+5% buffer)                     │
│       Logic: 480 × 1.05 = 504                          │
│       Reason: Low defect finishing process             │
│                                                        │
│ 5. PACKING                                             │
│    └─ Target: 480 pcs (NO BUFFER!) ✅                  │
│       Logic: EXACT match customer order                │
│       Reason: Final assembly, must be exact            │
└────────────────────────────────────────────────────────┘

Material Allocation Logic:
├─ Material consumption calculated based on WORK ORDER target (not Production Order)
├─ Example: Fabric for 528 pcs (not 480 pcs)
└─ Auto-adjust if Work Order target changed
```

**Business Impact**:
- 📉 Material waste: **-25%** (better planning, tidak excess)
- 📦 Shortage cases: **-40%** (buffer protect dari defect)

**What System MUST Support**:
1. ✅ Work Order target DAPAT BERBEDA dari Production Order target
2. ✅ Buffer % configurable per department type (admin dapat set sendiri)
3. ✅ Material auto-calculate based on Work Order target (bukan Production Order)
4. ✅ Alert if department output < minimum untuk next department
5. ✅ Tracking: Target vs Actual per department

**Questions for Vendor**:
- Q: Apakah Work Order bisa punya target berbeda dari Production Order?
- Q: Bagaimana material allocation logic jika target berbeda-beda?
- Q: Apakah bisa set buffer % per department type (configurable)?

---

### 5.3 Warehouse Finishing 2-Stage Process (MEDIUM!)

**Business Context**:
- Warehouse Finishing bukan hanya storage, tapi **processing center**
- Ada 2 stage internal: **Stuffing** (isi kapas) → **Closing** (pasang tag)
- Antara 2 stage ini **TIDAK ADA surat jalan** (internal conversion)
- Tapi inventory harus **terpisah track** (Skin stock vs Stuffed stock)

**Business Solution**:

```
2-STAGE INTERNAL WAREHOUSE CONVERSION:
═══════════════════════════════════════════════════════════════

STAGE 1: STUFFING PROCESS
───────────────────────────────────────────────────────────────
Location: Warehouse Finishing - Stuffing Area

Input Materials:
├─ Skin (from Sewing): 504 pcs
├─ Filling (kapas): 15,120 gram (30 gram/pcs × 504)
└─ Thread (closing thread): 504 meter

Process: Admin isi kapas ke dalam skin + jahit tutup

Output:
├─ Stuffed Body: 494 pcs (yield 98%)
└─ Defect/Scrap: 10 pcs (reject 2%)

Inventory Update:
├─ Skin Stock: -504 pcs (consumed)
├─ Filling Stock: -15,120 gram (consumed)
├─ Thread Stock: -504 meter (consumed)
└─ Stuffed Body Stock: +494 pcs (WIP inventory)

Note: Ini INTERNAL conversion, NO transfer document!


STAGE 2: CLOSING PROCESS
───────────────────────────────────────────────────────────────
Location: Warehouse Finishing - Closing Area

Input Materials:
├─ Stuffed Body (from Stage 1): 494 pcs
└─ Hang Tag: 494 pcs

Process: Admin pasang hang tag + QC final inspection

Output:
├─ Finished Doll: 489 pcs (yield 99%)
└─ Defect/Scrap: 5 pcs (reject 1%)

Inventory Update:
├─ Stuffed Body Stock: -494 pcs (consumed)
├─ Hang Tag Stock: -494 pcs (consumed)
└─ Finished Doll Stock: +489 pcs (ready for Packing)

Transfer: Finished Doll → Warehouse Main (formal transfer document)
```

**Business Impact**:
- 📊 Inventory visibility: Stuffing vs Closing stage jelas terpisah
- 🎯 Bottleneck identification: Tahu stage mana yang slow
- 📉 Material waste tracking: Monitor reject rate per stage

**What System MUST Support**:
1. ✅ 1 Warehouse bisa punya multiple internal "work centers" atau "sub-locations"
2. ✅ Track inventory per stage (Skin inventory vs Stuffed Body inventory)
3. ✅ Internal conversion TANPA formal transfer document (paperless)
4. ✅ Auto-calculate material consumption per stage
5. ✅ Yield tracking per stage (monitor reject rate)

**Questions for Vendor**:
- Q: Bagaimana implementation **internal warehouse conversion** tanpa formal transfer?
- Q: Apakah inventory bisa track per "work center" dalam 1 warehouse?
- Q: Bagaimana material consumption auto-calculated untuk internal conversion?

---

### 5.3.1 Department-Level Warehouse & Stock Opname (CRITICAL!)

**Business Context**:
- **SETIAP departemen produksi** punya warehouse/location sendiri (bukan hanya 3 main warehouses)
- **Stock opname regular** dilakukan per departemen untuk inventory accuracy
- System harus bisa track WIP inventory per department location

**Department Warehouse Structure**:

```
DEPARTMENT-LEVEL INVENTORY TRACKING:
═══════════════════════════════════════════════════════════════

1. WAREHOUSE CUTTING (WH-CUTTING)
   ├─ Input: Raw fabric dari WH-MAIN
   ├─ Output: Cut Body + Cut Baju (WIP)
   ├─ Stock Opname: Weekly (setiap Jumat sore)
   ├─ Tolerance: ±2% acceptable
   └─ Report: WIP Cutting inventory per SPK

2. WAREHOUSE EMBROIDERY (WH-EMBROIDERY)
   ├─ Input: Cut Body dari WH-CUTTING
   ├─ Output: Embroidered Body (WIP)
   ├─ Include: Outbound to vendor + Inbound from vendor
   ├─ Stock Opname: Weekly (setiap Sabtu pagi)
   ├─ Tolerance: ±2% (atau exact count jika <100 pcs)
   └─ Report: WIP Embroidery + In-transit vendor

3. WAREHOUSE SEWING (WH-SEWING)
   ├─ Input: Embroidered Body + Cut Baju + Thread
   ├─ Output: Skin + Baju Complete (tracked separately!)
   ├─ Stock Opname: Weekly (setiap Jumat sore)
   ├─ Tolerance: ±2%
   └─ Report: WIP Sewing - Body vs Baju separate

4. WAREHOUSE FINISHING (WH-FINISHING) - Already explained above
   ├─ 2 internal stages: Stuffing → Closing
   ├─ Stock Opname: Weekly per stage
   └─ Report: Skin vs Stuffed vs Finished Doll

5. WAREHOUSE PACKING (WH-PACKING)
   ├─ Input: Finished Doll + Baju + Carton + Label
   ├─ Output: Packed FG (Cartons)
   ├─ Stock Opname: DAILY (setiap akhir shift)
   ├─ Tolerance: 0% (must be exact - customer critical!)
   └─ Report: Ready-to-pack per SPK + Week/Destination
```

**Stock Opname Business Process**:

```
WEEKLY STOCK OPNAME WORKFLOW:
───────────────────────────────────────────────────────────────
Step 1: FREEZE TRANSACTIONS
├─ Department SPV freeze all stock movements (15 menit sebelum count)
├─ Finish all pending input transactions
└─ No new transfer allowed during count

Step 2: PHYSICAL COUNT
├─ 2 counters per department (cross-check)
├─ Count by SPK/Work Order (not bulk count)
├─ Record: SPK number, Item, Quantity, Location
└─ Time limit: 30-60 menit

Step 3: SYSTEM COMPARISON
├─ Input physical count to system
├─ System auto-compare: Physical vs System
├─ Variance calculation: (Physical - System) / System × 100%
└─ Flag: RED if variance > ±2%

Step 4: ADJUSTMENT (If needed)
├─ If variance ≤ ±2%: Auto-approve adjustment
├─ If variance > ±2%: Require SPV approval + justification
├─ Generate Adjustment Document (who, when, reason)
└─ Update system inventory

Step 5: REPORT & ANALYSIS
├─ Stock Opname Report per department
├─ Trend analysis: Apakah variance meningkat?
├─ Root cause: Department mana paling sering variance?
└─ Action: Training atau process improvement
```

**Business Impact**:
- 📊 Inventory accuracy: Target 98%+ (current manual 82%)
- 🎯 Early detection: Variance terdeteksi weekly (not monthly)
- 📉 Shrinkage control: Monitor department dengan highest variance
- ✅ Audit trail: All adjustments logged dengan justification

**What System MUST Support**:
1. ✅ Separate warehouse/location per department (5+ locations minimum)
2. ✅ Stock opname feature dengan physical count input
3. ✅ Auto-comparison physical vs system dengan variance %
4. ✅ Configurable tolerance per location (±2% default)
5. ✅ Adjustment workflow dengan approval logic
6. ✅ Audit trail all adjustments (who, when, before, after, reason)
7. ✅ Stock opname report & variance trend analysis

**Questions for Vendor**:
- Q: Apakah system support multi-location inventory per department?
- Q: Bagaimana stock opname workflow? Mobile-friendly?
- Q: Apakah ada automatic variance alert dengan threshold configurable?
- Q: Bagaimana ensure adjustment require approval jika variance besar?

---

### 5.4 Unit Conversion Validation (MEDIUM!)

**Business Context**:
- Soft toys pakai **banyak unit berbeda**: YARD (fabric), GRAM (filling), CM (ribbon), PCS (button), BOX (carton)
- Conversion manual → **error tinggi** (salah hitung, salah input)
- Error tidak terdetect sampai **1-2 minggu kemudian** (saat physical count)
- Dampak: Inventory chaos, shortage tidak terduga, excess waste

**Business Solution**:

```
VALIDATION CHECKPOINTS:
═══════════════════════════════════════════════════════════════

CHECKPOINT 1: CUTTING DEPARTMENT
───────────────────────────────────────────────────────────────
Scenario: Admin input material usage

Input Data:
├─ Material: KOHAIR Fabric
├─ Quantity Used: 70.38 YARD
├─ Work Order Target: 480 pcs
└─ Expected Usage (from recipe): 0.1005 YARD/pcs

System Calculation:
├─ Expected: 480 × 0.1005 = 48.24 YARD
├─ Actual: 70.38 YARD
├─ Variance: +45.7%
└─ Tolerance: ±10% (configurable)

System Action:
├─ Range Check: 48.24 ± 10% = 43.4 - 53.1 YARD
├─ Actual 70.38 YARD > 53.1 YARD → OUT OF RANGE!
└─ Alert: ⚠️ "Material usage abnormal (+45.7%). Verify input or check marker efficiency."

Options:
├─ Option 1: Correct input (re-enter)
├─ Option 2: Explain reason (input justification)
└─ Option 3: Supervisor approval (allow with alert)


CHECKPOINT 2: FINISHED GOODS RECEIVING
───────────────────────────────────────────────────────────────
Scenario: Warehouse Admin receive FG from Packing

Input Data:
├─ Cartons Received: 8 CTN
├─ Standard Packing: 60 pcs/CTN
├─ Expected: 8 × 60 = 480 pcs
└─ Physical Count: 465 pcs (manual count by admin)

System Calculation:
├─ Expected: 480 pcs
├─ Actual: 465 pcs
├─ Variance: -3.1%
└─ Tolerance: ±5% (configurable)

System Action:
├─ Range Check: 480 ± 5% = 456 - 504 pcs
├─ Actual 465 pcs within range → ACCEPTABLE
└─ Note: ⚠️ "Partial carton detected. CTN-008: 45 pcs (not standard 60)"

Auto-Actions:
├─ Inventory Update: 465 pcs (NOT 480 pcs)
├─ Carton Breakdown: Log partial carton detail
└─ Alert Packing Dept: "Non-standard carton created"
```

**Business Impact**:
- ✅ Inventory accuracy: 82% → **99%+**
- ⚡ Error detection: **Real-time** (vs 1-2 minggu manual)
- 🔍 Fraud prevention: Abnormal usage pattern terdeteksi

**What System MUST Support**:
1. ✅ Real-time validation saat input conversion
2. ✅ Configurable tolerance % per conversion type
3. ✅ Warning level (allow with note) vs Block level (require approval)
4. ✅ Log all variances untuk audit trail
5. ✅ Alert mechanism untuk abnormal patterns

**Questions for Vendor**:
- Q: Apakah system bisa auto-validate conversion dengan tolerance %?
- Q: Bagaimana configure warning vs blocking thresholds?
- Q: Apakah ada audit trail untuk semua variance?

---

### 5.5 Quality Control & Rework Workflow (MEDIUM!)

**Business Context**:
- Defect rate 10-15% normal untuk soft toys (karena manual sewing)
- Sebagian defect bisa di-**rework** (repair), tidak semua langsung scrap
- Tapi rework workflow **tidak tertrack** sekarang (manual paper-based)
- Dampak: COPQ (Cost of Poor Quality) tidak termonitor, root cause tidak teranalisa

**Business Solution**:

```
QUALITY CONTROL LOOP:
═══════════════════════════════════════════════════════════════

PHASE 1: DEFECT DETECTION
───────────────────────────────────────────────────────────────
QC Inspector (4 checkpoints: Cutting/Sewing/Finishing/Packing)

Defect Capture:
├─ Work Order: WO-SEWING-001
├─ Defect Qty: 15 pcs
├─ Defect Types:
│   ├─ Loose stitching: 8 pcs
│   ├─ Fabric hole: 4 pcs
│   └─ Wrong assembly: 3 pcs
├─ Root Cause:
│   ├─ Admin: Maria (ID-12345)
│   ├─ Machine: Sewing Machine #7
│   └─ Shift: Morning Shift
└─ Decision: ❓ REWORK atau SCRAP?

Decision Logic:
├─ Loose stitching → REWORK ✅ (can be fixed)
├─ Fabric hole → SCRAP ❌ (cannot be fixed)
└─ Wrong assembly → REWORK ✅ (can be re-assembled)

Result:
├─ To Rework: 11 pcs
└─ To Scrap: 4 pcs


PHASE 2: REWORK QUEUE ASSIGNMENT
───────────────────────────────────────────────────────────────
Rework Coordinator

Assignment:
├─ Priority: HIGH (customer urgent order)
├─ Assigned to: Rework Specialist - Team A
├─ SOP: "REWORK-SEWING-001: Loose Stitching Fix"
├─ Est. Time: 15 minutes/pcs × 11 pcs = 165 minutes
└─ Deadline: Within 4 hours

Material Tracking:
├─ Work In Progress: 11 pcs (in rework queue)
├─ Original WO: Still in progress
└─ COPQ Counter: Start tracking labor cost


PHASE 3: REWORK EXECUTION
───────────────────────────────────────────────────────────────
Rework Specialist

Process:
├─ Pick up 11 pcs from QC
├─ Follow SOP REWORK-SEWING-001
├─ Fix loose stitching
├─ Update status: "Rework completed"
└─ Send back to QC for RE-INSPECTION

Labor Tracking:
├─ Actual Time: 180 minutes (vs est. 165 min)
├─ Rework Cost: 180 min × $5/hour = $15
└─ COPQ Update: Add $15 to work order


PHASE 4: RE-INSPECTION
───────────────────────────────────────────────────────────────
Same QC Inspector (accountability)

Inspection Result:
├─ Pass: 10 pcs → Add back to GOOD OUTPUT ✅
├─ Fail: 1 pcs → Send to SCRAP ❌
└─ Recovery Rate: 10/11 = 90.9%

Inventory Update:
├─ Good Output: +10 pcs (recovered)
├─ Scrap: +1 pcs (permanent defect)
└─ Rework WIP: -11 pcs (cleared)


PHASE 5: REPORTING & ANALYSIS
───────────────────────────────────────────────────────────────
Management Dashboard

COPQ Summary (Work Order WO-SEWING-001):
├─ Scrap Cost: 5 pcs × $12/pcs = $60
├─ Rework Labor: $15
├─ Total COPQ: $75
└─ COPQ %: $75 / $1,200 revenue = 6.25%

Root Cause Analysis:
├─ Highest defect: Admin Maria (15 pcs)
├─ Highest defect machine: Machine #7
└─ Action: Training Maria + Maintenance Machine #7

Trend Analysis:
├─ Defect rate trend: ↓ 15% → 12% (improving!)
├─ Rework recovery rate: 90.9% (good!)
└─ COPQ trend: ↓ 8% → 6.25% (cost reduction!)
```

**Business Impact**:
- 📊 Defect visibility: 0% tracked → **100%** tracked
- 💰 COPQ reduction: **-30%** (better root cause action)
- 🎯 Targeted training: Data-driven admin improvement
- 📈 Recovery rate monitoring: Validate rework effectiveness

**What System MUST Support**:
1. ✅ Easy defect capture (preferably mobile-friendly)
2. ✅ Rework queue dengan priority management
3. ✅ Auto-calculate COPQ per work order (scrap + rework labor)
4. ✅ Re-inspection workflow (same inspector accountability)
5. ✅ Root cause analysis & reporting (admin, machine, shift trends)

**Questions for Vendor**:
- Q: Apakah ada Built-in quality control dengan rework workflow?
- Q: Bagaimana tracking COPQ (Cost of Poor Quality)?
- Q: Apakah mobile-friendly untuk production floor QC input?
- Q: Bagaimana ensure **admin tidak trauma lagi** dengan new ERP implementation?

---

<a name="success-criteria"></a>
## ✅ 6. KRITERIA SUKSES

### 6.1 Technical Success Criteria

**System Capabilities**:
✅ Handle 30+ materials per product (multi-level recipe)  
✅ Support 6+ unit types with auto-conversion (YARD, GRAM, CM, PCS, BOX, CARTON)  
✅ Real-time inventory visibility across 3 warehouses  
✅ Production tracking per department real-time  
✅ Mobile-friendly untuk production floor input (Android preferred)  

**Performance**:
✅ Page load time: <2 seconds  
✅ Report generation: <30 seconds untuk monthly reports  
✅ 99%+ uptime (system availability)  
✅ Support 40 concurrent users  

### 6.2 User Experience Success Criteria

**Ease of Use**:
✅ **SIMPLE & INTUITIVE** - Admin yang tidak tech-savvy bisa pakai dengan training minimal  
✅ **FAST INPUT** - Production team bisa input data <2 menit per work order  
✅ **CLEAR ALERTS** - Error messages jelas dalam **Bahasa Indonesia**  
✅ **MINIMAL CLICKS** - Reduce repetitive data entry (auto-fill where possible)  
✅ **MOBILE-FRIENDLY** - INPUT dari production floor tanpa perlu ke office  

**Training Success**:
✅ Admin bisa **comfortable** pakai system setelah 2 minggu training  
✅ 80%+ user satisfaction score (post-training survey)  
✅ <5% error rate setelah 1 bulan GoLive  

### 6.3 Business Outcome Success Criteria

**Operational KPIs** (Target: 6-12 bulan post-GoLive):

| Metric | Baseline | Target | Improvement |
|--------|----------|--------|-------------|
| **Lead Time** | 25 hari | 18 hari | **-28%** |
| **On-Time Delivery** | 75% | 95%+ | **+27%** |
| **Inventory Accuracy** | 82% | 98%+ | **+20%** |
| **Reporting Time** | 3-5 hari | Real-time | **-99%** |
| **Data Entry Time** | 15 jam/minggu | 1 jam/minggu | **-93%** |
| **Defect Tracking** | 0% tracked | 100% tracked | **+100%** |

**Operational Success**:
✅ Significant manual work reduction (eliminate manual inefficiencies)  
✅ Faster lead time enables taking more orders  
✅ **Expected payback within reasonable timeframe**  

**User Adoption**:
✅ **No resistance** dari admin (comfortable dengan system)  
✅ **No trauma** dari previous ERP failure (confidence restored)  
✅ Management **confidence** dalam ERP (continue investment)  

---

<a name="project-scope"></a>
## 📦 7. DEFINISI SCOPE PROJECT

### 7.1 IN SCOPE (Phase 1 - Core Implementation)

**Functional Areas**:
- ✅ Purchase Management (PO creation, Vendor management, Material receiving)
- ✅ Production Management (Production Order, Work Order, Recipe/Formula, Routing)
- ✅ Inventory Management (3 warehouses, Multi-unit, Stock movements, Real-time tracking)
- ✅ Quality Control (4 checkpoints, Defect recording, Rework workflow)
- ✅ Basic Reporting (Production reports, Inventory reports, Management dashboard)
- ✅ User Management (Role-based access, Approval workflow)

**Custom Features** (7 unique requirements):
- ✅ Dual Purchase Order System (PARTIAL/RELEASED status)
- ✅ Flexible Target System (Work Order target ≠ Production Order target)
- ✅ Warehouse Finishing 2-Stage (Internal conversion)
- ✅ Unit Conversion Validation (Tolerance checking)
- ✅ Real-Time WIP System (Batch-based transfers)
- ✅ Quality Control Loop (Rework/Repair tracking)
- ✅ Pull System Material (Auto-deduction logic)

**Data Migration**:
- ✅ Master data: Customer, Supplier, Material (SKU), Recipe/Formula
- ✅ Opening balance: Current inventory (as of cutoff date)
- ⚠️ Historical data: Last 3 bulan transactions (for reporting continuity)

**Training**:
- ✅ End-user training per role (Purchasing, Production, Warehouse, QC)
- ✅ Admin training (system configuration, user management)
- ✅ Super-user training (troubleshooting, support)

### 7.2 OUT OF SCOPE (Phase 2 - Future Enhancement)

- ❌ Finance module (AP/AR, General Ledger, Costing) → Use existing system for now
- ❌ HR & Payroll → Use existing system
- ❌ Sales Order management → Order masih via email dari IKEA
- ❌ Advanced planning (APS, MES) → Focus on core ERP first
- ❌ IoT integration → Future consideration
- ❌ AI/ML analytics → Future consideration

### 7.3 Estimasi Customization

Berdasarkan unique requirements, estimasi effort customization:

| Area Customization | Complexity | Estimasi Effort |
|-------------------|------------|-----------------|  
| **Dual Trigger Order Workflow** | 🔴 HIGH | Perlu diskusi GAP |
| **Flexible Target System** | 🔴 HIGH | Perlu diskusi GAP |
| **Warehouse Finishing 2-Stage** | 🟠 MEDIUM | Perlu diskusi GAP |
| **Unit Auto-Validation** | 🟠 MEDIUM | Perlu diskusi GAP |
| **Real-Time WIP System** | 🟠 MEDIUM | Perlu diskusi GAP |
| **Pull System Auto-Deduction** | 🟡 LOW | Perlu diskusi GAP |
| **Rework/Repair Workflow** | 🟠 MEDIUM | Perlu diskusi GAP |
| **Dashboard & Reports** | 🟡 LOW | Perlu diskusi GAP |
| **Integration & Testing** | - | Perlu diskusi GAP |

> 📋 **Note**: Exact effort akan ditentukan dalam **Gap Analysis Phase** setelah deep dive requirements dengan ERP Vendor Project Director & Business Analyst.

---

<a name="next-steps"></a>
## 🚀 8. LANGKAH SELANJUTNYA

### 8.1 Untuk Gap Analysis Consultation

**Yang PT Quty Harapkan dari Gap Analysis**:

1. **Deep Dive Requirements** (2-3 sesi workshop):
   - Vendor Project Director & Business Analyst understand **7 unique features** secara detail
   - Walk through **end-to-end workflow** dari Purchasing sampai Finished Goods
   - Discuss **pain point #11** (previous ERP failure) dan bagaimana mitigate

2. **Technical Feasibility Assessment**:
   - Demonstrate bagaimana system handle **Dual Purchase Order**
   - Show example **Flexible Target System** implementation
   - Explain approach untuk **Warehouse Finishing 2-Stage**
   - Validate **Unit Auto-Validation** mechanism
   - Prove **Real-Time WIP** capability dengan demo/proof-of-concept

3. **Reference Client Validation**:
   - Apakah ada client dengan **manufacturing complexity similar**?
   - Case study successful implementation di soft toys / garment industry
   - Reference contact yang bisa PT Quty hubungi untuk testimonial

4. **Training & Change Management Plan**:
   - Bagaimana approach untuk **admin yang trauma ERP**?
   - Training methodology (hands-on? classroom? on-the-job?)
   - Timeline training (berapa lama per role?)
   - Post-training support mechanism

5. **Support & Maintenance SLA**:
   - Post-GoLive support: Response time? Escalation path?
   - Bug fix commitment: Berapa lama resolve critical issue?
   - Enhancement request: Bagaimana process & pricing?
   - Upgrade policy: Version upgrade impact pada custom features?

### 8.2 Deliverables dari Gap Analysis (Yang PT Quty Butuhkan)

📋 **Gap Analysis Report** harus include:

**A. Technical Feasibility**:
- ✅ Detailed solution design untuk 7 unique features
- ✅ System architecture & data model
- ✅ Integration points & approach
- ✅ Customization scope & complexity assessment

**B. Implementation Plan**:
- ✅ Phased approach dengan milestone clear
- ✅ Timeline realistic (breakdown per phase)
- ✅ Resource requirement (vendor team + PT Quty team)
- ✅ Dependencies & risks identification

**C. Proof of Concept (Optional tapi Highly Recommended)**:
- ✅ Demo **Dual Trigger Order** workflow
- ✅ Show **Flexible Target** feature dengan sample data
- ✅ Validate **Unit conversion** logic dengan Quty recipe

**D. Training Plan**:
- ✅ Training modules per role (Purchasing, Production, Warehouse, Data Entry)
- ✅ Duration & methodology per module
- ✅ Success criteria per role (knowledge check, hands-on test)
- ✅ Special approach untuk **admin yang trauma ERP**

**E. Commercial Proposal**:
- ✅ License model & pricing
- ✅ Implementation cost breakdown
- ✅ Training cost
- ✅ Support & maintenance cost
- ✅ Payment terms & schedule

### 8.3 Decision Criteria untuk PT Quty

**We Will PROCEED if**:
✅ Semua 7 unique features **feasible** dengan customization reasonable  
✅ Vendor punya **proven track record** di manufacturing similar complexity  
✅ Commercial proposal **reasonable** dengan scope dan deliverables jelas  
✅ Timeline realistic **<6 bulan** untuk core implementation  
✅ Training & change management plan **solid & convincing**  
✅ Post-implementation support **commitment clear** dengan SLA  

**We Will REJECT if**:
❌ Vendor coba **force-fit** standard system tanpa proper customization  
❌ No experience di **manufacturing complexity level** PT Quty  
❌ Timeline unrealistic (too optimistic atau too long)  
❌ Commercial proposal tidak transparent  
❌ Training plan generic (tidak address previous ERP trauma)  
❌ Support SLA vague atau no commitment  

### 8.4 Questions untuk Vendor (Gap Analysis Discussion)

**General**:
1. Apakah pernah implement untuk **soft toys / garment / textile** industry?
2. Berapa project similar yang sudah successful?
3. Bisa share case study atau reference client?

**Technical**:
4. Bagaimana handle **Dual Purchase Order** trigger untuk production?
5. Bagaimana implement **Flexible Target** (Work Order target ≠ Production Order target)?
6. Bagaimana track **internal warehouse conversion** tanpa formal transfer?
7. Bagaimana **unit conversion validation** dengan tolerance %?
8. Apakah mobile-friendly untuk production floor input?

**Implementation**:
9. Berapa lama estimasi untuk Phase 1 (core implementation)?
10. Phased approach recommended? Atau Big Bang?
11. Minimal team PT Quty yang dibutuhkan (berapa orang, berapa % allocation)?

**Training & Support**:
12. Berapa lama training per role?
13. Training metodologi: Hands-on? Classroom? On-the-job coaching?
14. Post-GoLive support: Response time SLA? Dedicated support team?

**Commercial**:
15. License model: Perpetual atau subscription?
16. Customization cost: Fixed price atau Time & Material?
17. Payment terms: Percentage per milestone?

---

## 📚 APPENDIX

### A. Supporting Documents

**Yang sudah disiapkan PT Quty** (dapat diberikan saat Gap Analysis):
- Sample customer PO dari IKEA (redacted)
- Sample product recipe (30+ materials per SKU)
- Current manual forms (production reports, QC checklist)
- Historical data defect rate per department
- Organization chart & RACI matrix

**Yang belum disiapkan** (perlu discuss format dengan vendor):
- Detail data migration plan
- Test scenarios untuk UAT
- Cutover plan & rollback strategy

**Referensi dokumen tambahan** (jika vendor request):
- `ODOO_IMPLEMENTATION_BLUEPRINT.md` (1,200+ lines) - Detailed technical analysis (for internal reference - sangat technical)
- `Requirement Doc Odoo.md` + `Part 2.md` (2,000+ lines) - Comprehensive requirements (custom ERP prototype documentation)

> 📧 **Request**: Dokumen lengkap dapat dikirim via email setelah initial meeting confirmed untuk Gap Analysis schedule.

### B. Glossary

| Term | Definisi |
|------|----------|
| **Production Order** | Perintah produksi overall (triggered by Purchasing) |
| **Work Order** | Surat Perintah Kerja per departemen |
| **Recipe** | Daftar material (bahan) untuk 1 produk |
| **WIP** | Work In Progress - Barang setengah jadi |
| **FG** | Finished Goods - Barang jadi siap kirim |
| **GRN** | Goods Receipt Note - Penerimaan material |
| **COPQ** | Cost of Poor Quality - Biaya kualitas buruk (rework + scrap) |
| **OTD** | On-Time Delivery - Pengiriman tepat waktu |
| **PO** | Purchase Order - Pesanan pembelian |
| **Unit** | Unit of Measure - Satuan (YARD, PCS, GRAM, dll) |
| **QC** | Quality Control - Pengendalian kualitas |

---

**AKHIR DOKUMEN**

> 🎯 **Next Action**: Menunggu **Gap Analysis Consultation Quote** dari ERP vendor team, kemudian schedule workshop untuk deep dive requirements.

> ⚠️ **Important Reminder**: Ini adalah **last chance** untuk ERP di PT Quty. Previous implementation GAGAL. Management sangat skeptis. **HARUS BERHASIL** kali ini atau Quty akan permanent abandon ERP idea dan kembali ke manual system selamanya.

---

**Versi Dokumen**: 1.0  
**Last Updated**: 13 Februari 2026  
**Status**: ✅ Siap untuk ERP Vendor Review (Gap Analysis Phase)  
**Prepared By**: IT Lead PT Quty Karunia

**Document Version**: 1.0  
**Last Updated**: 13 Februari 2026  
**Status**: ✅ Ready for ERP Vendor Review
