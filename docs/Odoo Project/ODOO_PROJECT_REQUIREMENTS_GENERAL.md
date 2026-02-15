# 🏭 DOKUMEN REQUIREMENTS & PAIN POINTS - PT QUTY KARUNIA
## Untuk Gap Analysis Consultation dengan Odoo Partner

**Perusahaan**: PT Quty Karunia  
**Industri**: Soft Toys Manufacturing (B2B Export - Supplier IKEA)  
**Jenis Dokumen**: Requirements & Pain Points untuk Gap Analysis Phase  
**Disusun Oleh**: IT Lead - Daniel Rizaldy  
**Tanggal**: 13 Februari 2026  
**Target**: Odoo Project Director & Business Analyst  
**Status**: ✅ SIAP UNTUK EVALUASI  

---

## 📋 DAFTAR ISI

1. [Ringkasan Eksekutif](#executive-summary)
2. [Profil Perusahaan](#company-profile)
3. [Pain Points Saat Ini](#pain-points)
4. [Requirements Umum](#requirements)
5. [Proses Bisnis Unik](#unique-processes)
6. [Kriteria Sukses](#success-criteria)
7. [Definisi Scope Project](#project-scope)
8. [Langkah Selanjutnya](#next-steps)

---

<a name="executive-summary"></a>
## 📊 1. RINGKASAN EKSEKUTIF

### Konteks Project

PT Quty Karunia adalah manufacturer soft toys dengan **customer utama IKEA** (80% revenue). Perusahaan menghadapi **inefficiency operasional** akibat sistem manual berbasis Excel dan kertas, serta **pengalaman implementasi Odoo sebelumnya yang gagal** karena tidak sesuai dengan workflow bisnis yang kompleks, dan kemampuan user (admin) dalam pengerjaan menggunakan ERP Odoo

### Tujuan Project

Implementasi **Odoo 18 ERP System** yang **disesuaikan** dengan workflow Quty untuk:
- ✅ Menggantikan sistem manual dengan **single source of truth database**
- ✅ Mengintegrasikan **Purchasing, Production, Warehouse, dan QC** dalam satu platform
- ✅ Menyediakan **real-time visibility** untuk Management dan Department Heads
- ✅ Mengurangi **human error** dari 20% → <2%
- ✅ **Adopsi User tinggi** (pembelajaran mudah, tidak ada resistance dari team)

### Tantangan Utama

⚠️ **CRITICAL**: Soft toys manufacturing memiliki **karakteristik unik** yang berbeda dari manufacture standar:

1. **Dual Trigger Production System** - 2 jenis Purchase Order yang trigger produksi
2. **Complex Multi-UOM** - 30+ material per artikel dengan unit berbeda (YARD, GRAM, CM, PCS)
3. **2-Stage Finishing Process** - Internal conversion tanpa surat jalan formal
4. **Flexible Target System** - SPK target dapat berbeda dari MO target (buffer management)
5. **Parallel Production Streams** - 1 artikel = 2 komponen paralel (Body + Clothing)
6. **User Competency & Training** - Tingkat kemampuan user bervariasi, perlu pelatihan intensif
7. **Previous Odoo Failure** - Team admin trauma dengan Odoo karena implementasi sebelumnya gagal

> 🎯 **Kriteria Sukses**: Sistem harus dapat handle **unique workflows** ini tanpa memaksakan proses "generic manufacturing" yang tidak sesuai dengan business reality Quty. Team admin harus **nyaman menggunakan** sistem baru (user-friendly, well-trained).

---

<a name="PROFIL PERUSAHAAN

### Gambaran Bisnis
### Business Overview

| Aspek | Detail |
|--------|---------|
| **Nama Perusahaan** | PT Quty Karunia |
| **Industri** | Soft Toys Manufacturing (Discrete Manufacturing) |
| **Model Bisnis** | B2B Export - Make-to-Order (MTO) |
| **Customer Utama** | IKEA Sweden (80% revenue) |
| **Volume Produksi** | 50,000 - 80,000 pcs/bulan |
| **Range Produk** | 478 SKU (Boneka, Bantal, Soft Toys) |
| **Jumlah Karyawan** | ~250 total (40 staff + 210 workers) |

### Karakteristik Produksi

**Tipe Manufacturing**: Discrete Manufacturing dengan Complex Assembly

**Alur Produksi**: 6-Stage Sequential Process
```
Cutting → Embroidery* → Sewing → Finishing (2-stage) → Packing → Finished Goods
         (internal OR vendor)   (Stuffing + Closing)

*Embroidery: Opsional, bisa dikerjakan internal factory atau dikirim ke vendor eksternal
             Jika vendor, proses: Cutting → Kirim ke Vendor → Terima dari Vendor → Sewing
```

**Lead Time**: 15-25 hari (dari PO sampai Shipment)

**Pola Order**: Weekly delivery schedule (W01-2026, W02-2026, dst.)

**Standar Kualitas**: IKEA Compliance (STRICT - 95%+ OTD required)

### Struktur Organisasi

**Departemen Utama**:
- **Purchasing** (3 specialists): Fabric, Label, Accessories (termasuk PO untuk vendor embroidery)
- **Warehouse** (3 types): Main, Finishing Internal, Finished Goods
- **Produksi** (5 departments): Cutting, Sewing, Finishing, Packing, QC
- **Embroidery**: Internal (jika ada) ATAU Vendor Eksternal (outsorced)
- **Data Entry**: Staff untuk input hasil produksi dan vendor embroidery (jika menggunakan vendor)
- **Management**: Director, GM, Managers

**Workflow Utama**: Purchasing → Warehouse → Production → Finished Good

**Total Staff**: ~40 office staff

---

<a name="pain-points"></a>
## ❌ 3. PAIN POINTS SAAT INI

### 3.1 Ringkasan Masalah Kritis

PT Quty Karunia menghadapi **11 masalah kritis** yang menghambat operasional:

| No | Pain Point | Dampak Bisnis | Severity |
|----|------------|---------------|----------|
| 1 | **Data Produksi Manual** (Excel/Kertas) | Laporan lambat 3-5 hari, error prone, data tidak real-time | 🔴 CRITICAL |
| 2 | **Material Tidak Terdata Real-Time** | Tiba-tiba material habis → produksi STOP, pembelian dadakan | 🔴 CRITICAL |
| 3 | **SPK Tidak Terpantau** | Delay baru ketahuan saat deadline, koordinasi sulit | 🔴 CRITICAL |
| 4 | **Finished Good Sulit Verifikasi** | Salah hitung → customer complaint, rework packing | 🟠 HIGH |
| 5 | **Approval Tidak Jelas** | No audit trail, fraud potential, accountability hilang | 🟠 HIGH |
| 6 | **Laporan Bulanan Lambat** | Decision making terlambat, missed opportunities | 🟡 MEDIUM |
| 7 | **Finishing Process Chaos** | Stuffing & Closing tidak terstruktur, waste tinggi | 🔴 CRITICAL |
| 8 | **UOM Conversion Error** | Yard→Pcs, Box→Pcs salah hitung → inventory kacau | 🔴 CRITICAL |
| 9 | **Target Produksi Rigid** | Shortage karena defect tidak diantisipasi, delay shipping | 🔴 CRITICAL |
| 10 | **Defect Tidak Tertrack** | Waste tinggi, no root cause analysis, biaya rework besar | 🟠 HIGH |
| 11 | **Previous Odoo Implementation Failure** | Admin trauma, tidak terbiasa dengan Odoo, resistance to change | 🔴 CRITICAL |

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

PROBLEMS:
├─ No single source of truth
├─ Data duplication (setiap dept punya catatan sendiri)
├─ No real-time visibility (laporan delay 3-5 hari)
├─ Error prone (manual calculation & typing)
├─ No audit trail (sulit trace siapa ubah apa, kapan)
└─ Coordination nightmare (banyak meeting & follow-up)
```

### 3.3 Detail Pain Point #11: Previous Odoo Implementation Failure

⚠️ **CRITICAL CONTEXT** - WAJIB DIPAHAMI!

**Sejarah**:
- PT Quty pernah mencoba implementasi Odoo **sebelum IT Lead saat ini bergabung**
- Implementasi **GAGAL** karena:
  - Workflow Odoo standard tidak match dengan proses bisnis Quty yang kompleks
  - Vendor Odoo sebelumnya tidak deep dive requirements, force-fit Odoo standard
  - Tidak ada customization untuk **Dual Trigger System**, **Flexible Target**, **2-Stage Finishing**
  - Training tidak memadai, admin kebingungan dengan interface Odoo
  - Support post-implementation buruk, banyak bug tidak terselesaikan
  
**Dampak Sekarang**:
- ❌ **Admin trauma dengan Odoo** - "Odoo itu ribet, tidak sesuai cara kerja kita"
- ❌ **Resistance to change** - "Lebih baik Excel yang sudah biasa daripada Odoo yang susah"
- ❌ **Management skeptis** - "Sudah pernah coba Odoo, hasilnya gagal, kenapa harus coba lagi?"
- ❌ **Budget terbuang** - Investasi sebelumnya tidak memberikan hasil

**Yang Dibutuhkan Kali Ini**:
- ✅ **Deep understanding** dari Odoo team tentang **unique workflow** Quty (bukan force-fit!)
- ✅ **Proper customization** untuk 7 unique features (bukan "nanti dibiasakan pakai cara Odoo")
- ✅ **User-friendly interface** yang intuitif untuk admin (minimal training time)
- ✅ **Comprehensive training** dengan hands-on practice (bukan teori doang)
- ✅ **Strong post-implementation support** dengan SLA clear (fast response, not abandon project)
- ✅ **Proof of concept** untuk critical features sebelum full implementation (mitigate risk)

> 🚨 **PERINGATAN**: Jika implementasi kali ini gagal lagi, kemungkinan besar Management akan **permanently abandon** ide ERP dan kembali ke manual system selamanya. **This is the LAST CHANCE** untuk Odoo di Quty!

**Ekspektasi dari Gap Analysis**:
- 📋 Odoo team **HARUS** demonstrate bagaimana handle 7 unique features
- 📋 Odoo team **HARUS** show examples dari client lain dengan complexity similar
- 📋 Odoo team **HARUS** provide clear training plan untuk admin yang "trauma Odoo"
- 📋 Odoo team **HARUS** commit strong support SLA (bukan lepas tangan after GoLive)

### 3.4 Dampak Operasional

**Operational Impact**:
- ⏱️ **Lead Time**: 25 hari (target: 18 hari) → **-28% needed**
- 📦 **OTD (On-Time Delivery)**: 75% (target: 95%) → **+20% needed**
- 📊 **Inventory Accuracy**: 82% (target: 98%) → **+16% needed**
- 📋 **Reporting Time**: 3-5 hari (target: real-time) → **-100% needed**
- 💰 **Material Shortage Incidents**: 8-12/bulan (target: <3) → **-75% needed**

---

<a name="requirements"></a>
## 📋 4. REQUIREMENTS UMUM

### 4.1 Core Modules yang Dibutuhkan

| Kategori Module | Scope | Priority |
|----------------|-------|----------|
| **1. Purchasing Management** | 3 parallel streams (Fabric, Label, Accessories) | 🔴 CRITICAL |
| **2. Manufacturing (MRP)** | MO → SPK generation, BOM explosion, Routing | 🔴 CRITICAL |
| **3. Inventory & Warehouse** | 3-warehouse types, Multi-UOM, Stock movements | 🔴 CRITICAL |
| **4. Quality Control** | 4-checkpoint inspection, Rework/Repair workflow | 🟠 HIGH |
| **5. Production Planning** | Weekly scheduling, Capacity planning (handled by Purchasing flow) | 🟠 HIGH |
| **6. Reporting & Dashboard** | Real-time KPI, Management dashboard | 🟠 HIGH |
| **7. User Management (RBAC)** | Role-based access, Approval workflow | 🟡 MEDIUM |
| **8. Barcode & Labeling** | Finished Goods tracking, Pallet system | 🟡 MEDIUM |
| **9. Mobile App (Android)** | Production input, FG receiving | 🟢 LOW (Nice-to-have) |

### 4.2 Key Functional Requirements

#### A. Purchasing Management
- **Dual Trigger System**: PO Kain (Trigger 1) dan PO Label (Trigger 2) unlock production stages
- **3 Specialist Workflow**: Parallel purchasing untuk Fabric, Label, & Accessories
- **Vendor Management**: Supplier database, Lead time tracking, PO history
- **Material Receiving**: GRN dengan UOM conversion validation

#### B. Manufacturing (MRP)
- **BOM Structure**: Multi-level BOM dengan 30+ material per artikel
- **MO Workflow**: 2 modes (PARTIAL → RELEASED) based on PO Label status
- **MO Auto-Generate**: 1 PO -> 1-3 MO (auto-generated)
- **SPK Auto-Generation**: 1 MO → 1 SPK per department (auto-explode)
- **Flexible Target System**: SPK target dapat berbeda dari MO target (buffer allocation)
- **Routing**: Optional embroidery step, 2-stage finishing
- **Workflow**: Purchasing is the main trigger for production (no separate PPIC department)

#### C. Inventory & Warehouse
- **3 Main Warehouse Types**:
  - Main Warehouse (Raw materials)
  - Finishing Warehouse (Internal WIP: Skin → Stuffed Body)
  - Finished Goods Warehouse (Ready to ship - organized per pallet)
- **Department-Level Warehouses**: SETIAP departemen produksi punya warehouse/location sendiri:
  - Warehouse Cutting (WIP per cutting SPK)
  - Warehouse Embroidery (WIP embroidery - internal atau return dari vendor)
  - Warehouse Sewing (WIP sewing - Body & Baju separate tracking)
  - Warehouse Finishing (2-stage: Stuffing → Closing)
  - Warehouse Packing (WIP ready-to-pack)
  - **Stock Opname Regular**: Setiap departemen melakukan physical count untuk validasi inventory accuracy
- **Multi-UOM Handling**: YARD, GRAM, CM, PCS, BOX dengan auto-conversion
- **Real-Time WIP Tracking**: Inter-department stock movements
- **Material Debt System**: Negative stock allowed dengan alert & control

#### D. Quality Control
- **4-Checkpoint Inspection**: Cutting, Sewing, Finishing, Packing
- **Defect Recording**: Per SPK, per admin, per defect type
- **Rework Workflow**: Defect → QC → Repair → Re-QC → Approve
- **COPQ Analysis**: Cost of Poor Quality tracking

#### E. Production Planning
- **Weekly Scheduling**: Week-based planning (W01-2026, W02-2026) managed by Purchasing
- **Multi-Destination Management**: Belgium, Sweden, USA, dll.
- **Capacity Planning**: Workload balancing per department
- **Material Availability Check**: Before MO validation
- **Note**: Production planning integrated dengan Purchasing workflow (Purchasing → Warehouse → Production → FG)

### 4.3 Kebutuhan Reporting & Analytics

**Real-Time Dashboards**:
- Production progress per SPK (Actual vs Target)
- Material stock level (dengan min/max alert)
- Finished Goods inventory (ready to ship)
- Quality metrics (defect rate, yield rate)
- Delivery performance (OTD by week)

**Management Reports**:
- Monthly production summary
- Material consumption analysis
- COPQ report (rework cost vs scrap cost)
- Vendor performance scorecard

---

<a name="unique-processes"></a>
## 🔥 5. PROSES BISNIS UNIK (CRITICAL!)

### 5.1 Dual Trigger Production System

**⚠️ MOST UNIQUE FEATURE - TIDAK ADA DI ODOO STANDARD**

**Business Logic**:

```
TRIGGER 1: PO KAIN (Fabric) RECEIVED
├─ Status MO: PARTIAL
├─ Departments Unlocked: Cutting, Embroidery
└─ Other departments: BLOCKED (Sewing, Finishing, Packing)

    ↓ (3-7 days later)

TRIGGER 2: PO LABEL RECEIVED
├─ Status MO: RELEASED (auto-upgrade from PARTIAL)
├─ Week & Destination: AUTO-INHERIT from PO Label (tidak boleh manual edit!)
└─ All Departments: UNLOCKED (full production start)
```

**Why This Matters** (Kenapa Ini Penting):
- Lead time reduction **-30 to -40%** (cutting dapat start lebih awal)
- Label adalah material kritis karena contain Week & Destination info
- Week & Destination **TIDAK BOLEH** salah (akan kacaukan shipping schedule)

**Impact on Odoo**: MO workflow harus support **2-stage unlocking** dengan constraint per department.

---

### 5.2 Flexible Target System per Departemen

**⚠️ REVOLUTIONARY CONCEPT - TIDAK ADA DI STANDARD MRP**

**Business Logic**:

```
Manufacturing Order: 450 pcs AFTONSPARV
    │
    ├─ [CUTTING]
    │   MO Target: 450 pcs
    │   SPK Target: 495 pcs (+10% buffer) ← DIFFERENT FROM MO!
    │   Good Output: 485 pcs (98% yield)
    │   → 35 pcs surplus jadi stock buffer
    │
    ├─ [SEWING]
    │   Input: 485 pcs (from Cutting output)
    │   SPK Target: 480 pcs (adjusted to actual input)
    │   Good Output: 475 pcs
    │
    └─ [PACKING]
        Input: MIN(Body: 475 pcs, Clothing: 490 pcs) = 475 pcs
        SPK Target: 465 pcs (urgent shipping need)
        Final Output: 465 pcs ✅
```

**Format Universal**: `Actual/Target (Percentage%)`
- Contoh: `250/200 pcs (125%)` = exceed target 25%

**Smart Constraints**:
- SPK Target ≤ Good Output from previous dept
- Validation tolerance: 0-3% auto-approve, 5-10% warning, >10% block

**Why This Matters** (Kenapa Ini Penting):
- Zero shortage risk (buffer mengantisipasi defect)
- Material efficiency (production only what's needed + safety margin)
- Fast response to urgent orders (Packing dapat adjust target)

**Impact on Odoo**: SPK entity harus separate dari MO dengan flexible target field.

---

### 5.3 Warehouse Finishing 2-Stage Internal Conversion

**⚠️ UNIQUE PROCESS - TIDAK ADA DI STANDARD WAREHOUSE MODULE**

**Business Logic**:

```
Warehouse Finishing (Internal Conversion - No Surat Jalan)
│
├─ Stage 1: STUFFING
│   Input: WIP_SKIN (from Sewing) - 485 pcs
│   Material: Filling (25 kg dacron)
│   Process: Isi kapas ke dalam skin
│   Output: WIP_STUFFED_BODY - 475 pcs
│   Location: WH_FINISHING/STUFFED
│   → 2 Stok Terpisah: SKIN vs STUFFED BODY
│
└─ Stage 2: CLOSING
    Input: WIP_STUFFED_BODY - 475 pcs
    Material: Thread (100 CM), Hang Tag (1 pcs)
    Process: Jahit closing + pasang label
    Output: FINISHED_DOLL - 470 pcs
    Location: WH_FG/READY_TO_PACK
```

**Key Points**:
- **2 jenis stok berbeda**: Skin (belum isi) vs Stuffed Body (sudah isi)
- **Internal conversion**: Tanpa surat jalan (bukan antar-warehouse transfer formal)
- **Demand-driven**: Target adjust to Packing need (bukan rigid dari MO)
- **Material tracking**: Konsumsi filling/kapas per stage jelas

**Why This Matters** (Kenapa Ini Penting):
- Kontrol filling consumption akurat (material cost 15-20% dari total)
- Yield per stage dapat dimonitor (stuffing 98%, closing 99%)
- Visibility stok per stage untuk planning

**Impact on Odoo**: Warehouse Finishing butuh **dual inventory tracking** dengan conversion logic.

---

### 5.4 UOM Auto-Validation with Tolerance Checking

**⚠️ CRITICAL FEATURE - PREVENT INVENTORY CHAOS**

**Business Logic**:

```
CUTTING: Fabric YARD → Pieces
├─ BOM: 1 pcs = 0.1466 YARD (marker calculation)
├─ Input: 70.4 YARD fabric consumed
├─ Expected output: 70.4 / 0.1466 = 480.2 pcs
├─ Actual input: 485 pcs
├─ Variance: (485 - 480.2) / 480.2 = +1.0% ✅ AUTO-APPROVE
└─ Alert level: 0-10% Warning, >15% BLOCK entry

FG RECEIVING: Box → Pieces
├─ Standard: 1 BOX = 54 PCS (conversion factor)
├─ Input: 8.5 BOX received
├─ Expected: 8.5 × 54 = 459 pcs
├─ Actual count: 465 pcs
├─ Variance: +6 pcs (+1.3%) ⚠️ WARNING (proceed with manager approval)
└─ Update: Adjust conversion factor OR flag for investigation
```

**Validation Rules**:
- **0-10% variance**: Warning only (proceed allowed)
- **10-15% variance**: Require supervisor approval
- **>15% variance**: BLOCK entry (force recount)

**Why This Matters** (Kenapa Ini Penting):
- Prevent inventory kacau sejak awal (data entry error detection)
- Real-time alert saat variance mencurigakan
- Audit trail lengkap untuk investigation

**Impact on Odoo**: Custom validation logic pada stock move dengan tolerance matrix.

---

### 5.5 Real-Time WIP System (Work In Progress)

**⚠️ GAME CHANGER - PARALLEL PRODUCTION**

**Traditional System Problem**:
```
Dept A: Selesai 100% → baru transfer ke Dept B → Dept B baru mulai
Lead time: 5 hari + 5 hari = 10 hari total ❌
```

**Quty System Solution**:
```
Dept A: Selesai batch 1 (20%) → Dept B START segera dengan batch 1
Dept A: Selesai batch 2 (40%) → Dept B lanjut batch 2 (sambil A kerja batch 3)
Lead time: 5 hari + 1 hari overlap = 6 hari total ✅ (-40%!)
```

**Key Features**:
- **Parsialitas**: Production submit per batch (20, 50, 100 pcs) bukan tunggu semua selesai
- **Instant transfer**: Output Dept A = Input available Dept B (real-time)
- **Minus balance alert**: Jika Dept B tarik material lebih dari available (early warning)

**Why This Matters** (Kenapa Ini Penting):
- Production throughput +30%
- Faster delivery (critical untuk IKEA deadline)
- Bottleneck detection real-time

**Impact on Odoo**: Stock location dan transfer harus support **partial batch movement** dengan real-time update.

---

### 5.6 Pull System & Auto Material Deduction

**⚠️ ZERO PAPERWORK - FULL AUTOMATION**

**Traditional System**:
```
1. Production request material → Form manual
2. Warehouse prepare → 1-2 hour
3. Delivery → Manual logbook
4. System update → Next day (manual entry)
Total time: 2-3 hours + 1 day delay ❌
```

**Quty System**:
```
1. Admin submit production (actual output)
2. Backend auto-calculate material consumed (via BOM)
3. Auto-deduct from warehouse stock
4. Auto-transfer to production location
5. Full audit trail (5W1H) recorded
Total time: 5 seconds, instant update ✅
```

**5W1H Audit Trail**:
- **WHO**: User ID, Department, Role
- **WHAT**: Material SKU, Quantity, UOM
- **WHEN**: Timestamp exact
- **WHERE**: Source location → Destination location
- **WHY**: SPK reference, MO reference
- **HOW**: Manual entry / Auto-deduction / Transfer

**Why This Matters** (Kenapa Ini Penting):
- Material movement efficiency +90%
- Zero paperwork (production tidak buat form manual)
- Audit ready (ISO compliance)
- Discrepancy detection real-time

**Impact on Odoo**: Stock move harus **auto-triggered** dari production confirmation dengan full traceability.

---

### 5.7 Rework/Repair Module Integration with QC

**⚠️ QUALITY EXCELLENCE - MINIMIZE WASTE**

**Workflow**:
```
Production Submit → Input: Good Output + Defect qty
    │
    ├─ Good Output: Direct transfer to next dept
    │
    └─ Defect: Send to REWORK queue
        │
        ├─ QC Inspection: Classify defect type
        │   ├─ Repairable → Send to Repair dept
        │   └─ Scrap → Write-off (calculate COPQ)
        │
        ├─ Repair Process: Fix defect
        │   └─ Re-submit to QC for re-inspection
        │
        └─ Re-QC: Approve atau Reject
            ├─ Approved → Add back to Good Output pool
            └─ Rejected → Final scrap (calculate loss)
```

**Key Metrics Tracked**:
- **Defect Rate**: By department, by admin, by defect type
- **Recovery Rate**: % defect yang berhasil diperbaiki (target >80%)
- **COPQ**: Cost of rework + scrap value
- **Root Cause**: Pareto analysis untuk continuous improvement

**Why This Matters** (Kenapa Ini Penting):
- Waste cost reduction signifikan
- Quality visibility 100% (tidak ada "hidden defect")
- Continuous improvement via root cause analysis

**Impact on Odoo**: QC module harus integrate dengan production untuk **defect loop management**.

---

<a name="success-criteria"></a>
## 📊 6. KRITERIA SUKSES

### 6.1 Quantitative Metrics (KPI)

| No | Metric | Current (Baseline) | Target (After Odoo) | Improvement | Timeline |
|----|--------|-------------------|---------------------|-------------|----------|
| 1 | **Lead Time** | 25 hari | 18 hari | -28% | 6 bulan post-GoLive |
| 2 | **On-Time Delivery (OTD)** | 75% | 95%+ | +27% | 6 bulan post-GoLive |
| 3 | **Inventory Accuracy** | 82% | 98%+ | +20% | 3 bulan post-GoLive |
| 4 | **Fabric Yield** | 85% (15% waste) | 92% (8% waste) | +8% | 12 bulan post-GoLive |
| 5 | **Reporting Time** | 3-5 hari | <1 jam | -99% | 1 bulan post-GoLive |
| 6 | **Material Shortage Incidents** | 8-12 kali/bulan | <3 kali/bulan | -75% | 3 bulan post-GoLive |
| 7 | **Manual Data Entry Time** | 15 jam/minggu | 2 jam/minggu | -87% | 1 bulan post-GoLive |
| 8 | **Decision Making Speed** | 3-5 hari | Real-time | -100% | 1 bulan post-GoLive |

### 6.2 Qualitative Success Factors

✅ **User Adoption**: >80% daily active users dalam 3 bulan (terutama admin yang "trauma Odoo")  
✅ **System Stability**: Uptime >99.5% (max 4 hours downtime/bulan)  
✅ **Data Integrity**: Zero double-entry, single source of truth  
✅ **Audit Trail**: 100% traceability untuk material movement  
✅ **Approval Workflow**: Clear authorization chain dengan timestamp  
✅ **Mobile Accessibility**: Production & FG receiving via Android app  
✅ **Training Effectiveness**: <2 minggu untuk user menjadi proficient  
✅ **Admin Confidence**: Admin yang previous trauma dengan Odoo sekarang **comfortable** menggunakan sistem

---

<a name="project-scope"></a>
## 🎯 7. DEFINISI SCOPE PROJECT

### 7.1 IN SCOPE (Phase 1 - Core Implementation)

✅ **Modules to Implement**:
1. **Purchasing Management**
   - 3-stream purchasing (Fabric, Label, Accessories)
   - Vendor management
   - PO tracking
   - GRN with UOM validation

2. **Manufacturing (MRP)**
   - BOM structure (multi-level, multi-UOM)
   - MO workflow (2-mode: PARTIAL/RELEASED)
   - SPK auto-generation per department
   - Routing (optional embroidery, 2-stage finishing)
   - Flexible target system (buffer allocation)

3. **Inventory & Warehouse**
   - 3-warehouse setup (Main, Finishing, FG)
   - Multi-UOM handling
   - Stock movement tracking
   - Real-time WIP system
   - Material debt management

4. **Quality Control**
   - 4-checkpoint inspection
   - Defect recording
   - Rework workflow (basic)

5. **Reporting & Dashboard**
   - Production progress dashboard
   - Material stock level
   - Management KPI dashboard
   - Basic reports (monthly production, material consumption)

6. **User Management**
   - Role-based access control (RBAC)
   - Multi-level approval workflow
   - Audit trail

### 7.2 OUT OF SCOPE (Phase 1)

❌ **Deferred to Phase 2 atau Future**:
- Accounting & Finance integration (gunakan sistem existing)
- HR & Payroll module
- Sales & CRM module
- E-commerce integration
- Advanced analytics & BI tools
- IoT integration (machine sensors)
- AI/ML predictive analytics

### 7.3 Estimasi Customization

Berdasarkan unique requirements, estimasi effort customization:

| Area Customization | Complexity | Estimasi Effort |
|-------------------|------------|-----------------|  
| **Dual Trigger MO Workflow** | 🔴 HIGH | Perlu diskusi GAP |
| **Flexible Target System** | 🔴 HIGH | Perlu diskusi GAP |
| **Warehouse Finishing 2-Stage** | 🟠 MEDIUM | Perlu diskusi GAP |
| **UOM Auto-Validation** | 🟠 MEDIUM | Perlu diskusi GAP |
| **Real-Time WIP System** | 🟠 MEDIUM | Perlu diskusi GAP |
| **Pull System Auto-Deduction** | 🟡 LOW | Perlu diskusi GAP |
| **Rework/Repair Module** | 🟠 MEDIUM | Perlu diskusi GAP |
| **Dashboard & Reports** | 🟡 LOW | Perlu diskusi GAP |
| **Integration & Testing** | - | Perlu diskusi GAP |

> 📋 **Note**: Exact effort akan ditentukan dalam **Gap Analysis Phase** setelah deep dive requirements dengan Odoo Project Director & Business Analyst.

---

<a name="next-steps"></a>
## 🚀 8. LANGKAH SELANJUTNYA

### 8.1 Untuk Gap Analysis Consultation

**Yang PT Quty Harapkan dari Gap Analysis**:

1. **Deep Dive Requirements** (2-3 sesi workshop):
   - Odoo Project Director & Business Analyst understand **7 unique features** secara detail
   - Walk through **end-to-end workflow** dari Purchasing sampai Finished Goods
   - Discuss **pain point #11** (previous Odoo failure) dan bagaimana mitigate

2. **Technical Feasibility Assessment**:
   - Demonstrate bagaimana Odoo handle **Dual Trigger MO**
   - Show example **Flexible Target System** implementation
   - Explain approach untuk **Warehouse Finishing 2-Stage**
   - Validate **UOM Auto-Validation** mechanism
   - Prove **Real-Time WIP** capability dengan demo/proof-of-concept

3. **Reference Client Validation**:
   - Apakah ada Odoo client dengan **manufacturing complexity similar**?
   - Case study successful implementation di soft toys / garment industry
   - Reference contact yang bisa PT Quty hubungi untuk testimonial

4. **Training & Change Management Plan**:
   - Bagaimana approach untuk **admin yang trauma Odoo**?
   - Training methodology (hands-on? classroom? on-the-job?)
   - Timeline training (berapa lama per role?)
   - Post-training support mechanism

5. **Support & Maintenance SLA**:
   - Post-GoLive support: Response time? Escalation path?
   - Bug fix commitment: Berapa lama resolve critical issue?
   - Enhancement request: Bagaimana process & pricing?
   - Upgrade policy: Odoo v19, v20 impact pada custom code?

### 8.2 Deliverables dari Gap Analysis (Yang PT Quty Butuhkan)

📋 **Gap Analysis Report** harus include:

**A. Technical Feasibility**:
- ✅ Detailed solution design untuk 7 unique features
- ✅ Odoo modules mapping (standard vs custom)
- ✅ Architecture diagram (data flow, integration points)
- ✅ Risk assessment & mitigation plan

**B. Project Plan**:
- ✅ Implementation phases dengan milestone clear
- ✅ Resource allocation (team size, roles, duration)
- ✅ Timeline realistic (tidak over-promise!)
- ✅ Dependency & critical path analysis

**C. Proof of Concept (Optional tapi Highly Recommended)**:
- ✅ Demo **Dual Trigger MO** workflow di Odoo environment
- ✅ Show **Flexible Target** feature dengan sample data
- ✅ Validate **UOM conversion** logic dengan Quty BOM

**D. Training Plan**:
- ✅ Training modules per role (Purchasing, Production, Warehouse, Data Entry)
- ✅ Duration & methodology per module
- ✅ Success criteria per role (knowledge check, hands-on test)
- ✅ Special approach untuk **admin yang trauma Odoo**

**E. Commercial Proposal**:
- ✅ License model & pricing
- ✅ Implementation cost breakdown
- ✅ Training cost
- ✅ Support & maintenance cost
- ✅ Payment terms & schedule

### 8.3 Decision Criteria untuk PT Quty

**GO Decision jika**:
✅ Semua 7 unique features **feasible** dengan customization reasonable  
✅ Odoo team demonstrate **deep understanding** workflow Quty (bukan surface level)  
✅ Reference client proven dengan **manufacturing complexity similar**  
✅ Training plan solid untuk **admin yang trauma Odoo** (bukan generic training)  
✅ Post-GoLive support SLA **clear & strong** (bukan lepas tangan after GoLive)  
✅ Timeline realistic **<6 bulan** untuk core implementation  
✅ Proof of concept untuk **critical features** berhasil demonstrated  

**NO-GO jika**:
❌ Major unique features **TIDAK feasible** di Odoo platform  
❌ Odoo team coba **force-fit** standard Odoo tanpa proper customization  
❌ No clear answer untuk **previous Odoo failure** issue (kenapa kali ini beda?)  
❌ Training plan **generic** tanpa consider admin trauma  
❌ Support SLA **vague** atau tidak committed  
❌ Timeline **unrealistic** (<3 bulan atau >9 bulan)

---

### 8.4 Pertanyaan Kritis untuk Odoo Team (WAJIB DIJAWAB!)

**Technical Questions**:

1. **Dual Trigger MO System**:
   - Q: Bagaimana Odoo MRP module handle **2-stage MO unlocking** (PARTIAL → RELEASED)?
   - Q: Apakah Odoo support **department-level constraint** (Dept A unlock, Dept B block)?
   - Q: Bagaimana PO Label status auto-trigger MO upgrade ke RELEASED?

2. **Flexible Target System**:
   - Q: Apakah Odoo support **SPK target berbeda dari MO target**?
   - Q: Bagaimana implement **smart buffer allocation** (Cutting +10%, Sewing +15%)?
   - Q: Apakah Odoo punya **validation tolerance** (0-3% auto, 5-10% warning, >10% block)?

3. **Warehouse Finishing 2-Stage**:
   - Q: Bagaimana implementation **internal warehouse conversion** tanpa formal transfer?
   - Q: Apakah Odoo support **dual inventory tracking** (Skin stock vs Stuffed Body stock)?
   - Q: Bagaimana track **material consumption per stage** (filling di Stage 1, thread di Stage 2)?

4. **UOM Validation**:
   - Q: Apakah Odoo punya **native UOM validation** dengan tolerance checking?
   - Q: Bagaimana prevent inventory kacau saat **Yard→Pcs conversion error**?
   - Q: Apakah ada **real-time alert** saat variance >10%?

5. **Real-Time WIP**:
   - Q: Apakah stock movement dapat **auto-triggered** dari production confirmation?
   - Q: Bagaimana Odoo handle **partial batch transfer** (20 pcs, 50 pcs, 100 pcs)?
   - Q: Apakah support **minus balance alert** untuk early warning?

6. **Pull System**:
   - Q: Bagaimana Odoo auto-deduct material saat production submit?
   - Q: Apakah ada **full 5W1H audit trail** untuk every transaction?
   - Q: Bagaimana handle **discrepancy detection** real-time?

7. **Rework Module**:
   - Q: Bagaimana Odoo QC module integrate dengan **rework loop workflow**?
   - Q: Apakah support **defect tracking per admin, per defect type**?
   - Q: Bagaimana calculate **COPQ** (Cost of Poor Quality)?

**Change Management Questions**:

8. **Previous Odoo Failure**:
   - Q: Kenapa implementasi Odoo sebelumnya **GAGAL** di Quty? (jika Odoo tahu history)
   - Q: Apa yang akan Odoo team lakukan **BERBEDA** kali ini?
   - Q: Bagaimana ensure **admin tidak trauma lagi** dengan new Odoo implementation?

9. **Training Approach**:
   - Q: Apa training methodology untuk **admin yang tidak terbiasa dengan Odoo**?
   - Q: Berapa lama training per role? Hands-on practice berapa %?
   - Q: Apakah ada **post-training support** untuk Q&A ongoing?

10. **User Adoption Strategy**:
    - Q: Bagaimana ensure **>80% daily active users** dalam 3 bulan?
    - Q: Apa strategy untuk handle **resistance to change**?
    - Q: Bagaimana measure user adoption success?

---

## 📞 CONTACT INFORMATION

**PT Quty Karunia - IT Project Lead**  
Nama: Daniel Rizaldy  
Role: IT Lead & System Designer  
Email: [TBD]  
Phone: [TBD]  

**Project Sponsor**  
Role: General Manager / Director  
Contact: [TBD]

---

## 📄 APPENDIX

### A. Referensi Dokumen

Detail lengkap (technical specification, workflow illustration, dll) tersedia di:
- `PRESENTASI_MANAGEMENT_ERP_QUTY_KARUNIA.md` (4,600+ lines) - Business context & features
- `TECHNICAL_SPECIFICATION.md` (4,200+ lines) - Complete technical spec dengan code examples
- `ILUSTRASI_WORKFLOW_LENGKAP.md` (1,500+ lines) - End-to-end workflow visualization
- `ODOO_IMPLEMENTATION_BLUEPRINT.md` (1,200+ lines) - Detailed Odoo gap analysis
- `Requirement Doc Odoo.md` + `Part 2.md` (2,000+ lines) - Comprehensive requirements

> 📧 **Request**: Dokumen lengkap dapat dikirim via email setelah initial meeting confirmed untuk Gap Analysis schedule.

### B. Glossary

| Term | Definisi |
|------|----------|
| **MO** | Manufacturing Order - Perintah produksi (triggered by Purchasing) |
| **SPK** | Surat Perintah Kerja - Work Order per departemen |
| **BOM** | Bill of Materials - Daftar material untuk 1 produk |
| **WIP** | Work In Progress - Barang setengah jadi |
| **FG** | Finished Goods - Barang jadi siap kirim |
| **GRN** | Goods Receipt Note - Penerimaan material |
| **COPQ** | Cost of Poor Quality - Biaya kualitas buruk (rework + scrap) |
| **OTD** | On-Time Delivery - Pengiriman tepat waktu |
| **PO** | Purchase Order - Pesanan pembelian |
| **UOM** | Unit of Measure - Satuan unit (YARD, PCS, GRAM, dll) |
| **QC** | Quality Control - Pengendalian kualitas |

---

**AKHIR DOKUMEN**

> 🎯 **Next Action**: Menunggu **Gap Analysis Consultation Quote** dari Odoo team, kemudian schedule workshop untuk deep dive requirements.

> ⚠️ **Important Reminder**: Ini adalah **last chance** untuk Odoo di PT Quty. Previous implementation GAGAL. Management sangat skeptis. **HARUS BERHASIL** kali ini atau Quty akan permanent abandon ERP idea dan kembali ke manual system selamanya.

---

**Versi Dokumen**: 1.0  
**Last Updated**: 13 Februari 2026  
**Status**: ✅ Siap untuk Odoo Partner Review (Gap Analysis Phase)  
**Prepared By**: IT Lead PT Quty Karunia

**Document Version**: 1.0  
**Last Updated**: 13 Februari 2026  
**Status**: ✅ Ready for Odoo Partner Review
