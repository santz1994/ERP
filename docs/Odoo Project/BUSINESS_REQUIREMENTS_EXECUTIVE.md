# 🏭 PT QUTY KARUNIA - ERP SYSTEM REQUIREMENTS
## Executive Summary untuk Konsultasi Vendor ERP

**Tanggal**: 13 Februari 2026  
**Disusun Oleh**: IT Lead - Daniel Rizaldy  
**Target**: ERP Vendor (Initial Review)  
**Untuk**: Gap Analysis & Feasibility Assessment

---

## 📊 COMPANY AT A GLANCE

| **Perusahaan** | PT Quty Karunia |
|------------|-----------------|
| **Industri** | Soft Toys Manufacturing (B2B Export) |
| **Customer Utama** | IKEA (80% revenue) |
| **Volume** | 50,000 - 80,000 pcs/bulan |
| **Karyawan** | ~250 total (40 staff + 210 workers) |
| **Sistem Saat Ini** | Manual (Excel + Paper + WhatsApp) |

---

## ❌ CURRENT PAIN POINTS (11 Critical Issues)

| Issue | Dampak | Severity |
|-------|--------|----------|
| 1. Manual data entry (Excel/Paper) | Laporan lambat (3-5 hari) | 🔴 CRITICAL |
| 2. Material tidak terdata real-time | Produksi STOP (kehabisan stok) | 🔴 CRITICAL |
| 3. Work order tidak terpantau | Late delivery → penalty | 🔴 CRITICAL |
| 4. Finished goods sulit verifikasi | Customer complaints | 🟠 HIGH |
| 5. No approval clarity | Fraud potential, no audit | 🟠 HIGH |
| 6. Monthly reports lambat | Delayed decisions | 🟡 MEDIUM |
| 7. Finishing process chaos | Material waste | 🔴 CRITICAL |
| 8. Unit conversion errors | Inventory inaccurate | 🔴 CRITICAL |
| 9. Rigid production targets | Shortage karena defect | 🔴 CRITICAL |
| 10. Defect tidak tertrack | High waste, no root cause | 🟠 HIGH |
| 11. Previous ERP implementation GAGAL | Admin trauma, Management skeptis | 🔴 CRITICAL |

> ⚠️ **CRITICAL**: Pain point #11 adalah **paling penting**! PT Quty pernah implementasi ERP sebelumnya dan **GAGAL TOTAL** karena sistem tidak sesuai workflow, user tidak terlatih dengan baik, dan vendor tidak support dengan maksimal. Admin sekarang trauma, Management sangat skeptis. **Ini adalah LAST CHANCE untuk ERP di Quty!**

---

## 🎯 PROJECT OBJECTIVES

**Goal**: Replace fragmented manual systems dengan **integrated ERP system** yang **disesuaikan** dengan workflow Quty (bukan force-fit!)

**Success Metrics** (6-12 bulan post-GoLive):
- ⏱️ Lead Time: 25 hari → **18 hari** (-28%)
- 📦 On-Time Delivery: 75% → **95%+** (+27%)
- 📊 Inventory Accuracy: 82% → **98%+** (+20%)
- ⚡ Reporting: 3-5 hari → **Real-time** (-99%)
- 👥 **User Adoption**: Admin yang trauma ERP → **Comfortable** menggunakan sistem

**Critical Success Factor**: Admin harus **tidak trauma lagi** dengan ERP implementation kali ini!

---

## 🔥 UNIQUE BUSINESS REQUIREMENTS (Critical to Understand!)

### ⚠️ **7 KARAKTERISTIK UNIK** - Berbeda dari Manufacturing Standar

| # | Business Requirement | Business Impact |
|---|---------------------|-----------------|
| **1** | **Dual Purchase Order System** | PO Fabric (early start) + PO Label (full release)
| **2** | **Flexible Production Targets** | Department target ≠ Overall target (buffer management)
| **3** | **2-Stage Internal Processing** | Internal material conversion tanpa surat jalan formal
| **4** | **Unit Conversion Validation** | Auto-check toleransi (Yard→Pcs, Box→Pcs)
| **5** | **Real-Time Work In Progress** | Parallel production dengan batch-based transfer
| **6** | **Paperless Material Movement** | Auto-deduction material tanpa dokumen manual
| **7** | **Quality Control Loop** | Defect tracking dengan repair & recovery workflow

**Total Customization**: Level customization akan ditentukan dalam **Gap Analysis Phase** bersama ERP vendor team

**Catatan Production Process**: Embroidery step bisa dikerjakan **internal** (jika pabrik punya mesin) ATAU **vendor eksternal** (outsourced). Jika vendor, workflow: Cutting → Kirim ke Vendor → Terima dari Vendor → Sewing.

---

## 📋 BUSINESS FUNCTIONS YANG DIBUTUHKAN

### Priority 1 (CRITICAL - Must Have)
- ✅ **Purchase Management** - Kelola pembelian 3 jenis material parallel (Fabric, Label, Accessories) + Purchase Order untuk vendor embroidery
- ✅ **Production Management** - Buat perintah produksi, kelola resep produk (daftar material), atur alur kerja per departemen
- ✅ **Inventory & Warehouse Management** - Kelola 3 gudang utama + warehouse per departemen produksi (setiap departemen punya stock opname sendiri), konversi satuan otomatis, tracking perpindahan barang real-time (termasuk outbound/inbound vendor)
- ✅ **Quality Control** - Inspection di 4 titik quality checkpoint, record defect produksi

### Priority 2 (HIGH - Important)
- ✅ **Production Planning** - Scheduling mingguan (format Week: W01-2026, W02-2026)
- ✅ **Reporting & Analytics** - Dashboard real-time, Management KPI, Production reports
- ✅ **User Access Control** - Pengaturan hak akses per role, Multi-level approval workflow

### Priority 3 (NICE-TO-HAVE)
- 🔄 **Product Tracking System** - Barcode/QR scanning untuk Finished Goods, Pallet tracking
- 🔄 **Mobile Application** - Android app untuk production input dan receiving

---

## 💡 KENAPA BUSINESS REQUIREMENTS INI UNIK?

### 1️⃣ Dual Purchase Order System

**Problem**: Label berisi info kritis (Week + Destination), tapi lead time panjang (7-10 hari), sementara Fabric sudah ready (3-5 hari)

**Business Solution Needed**:
```
PO Fabric arrives (Day 1) → Status: PARTIAL PRODUCTION ALLOWED
├─ Cutting: CAN START ✅
├─ Embroidery (internal/vendor): CAN START ✅
└─ Sewing onwards: BLOCKED ❌ (tunggu label)

PO Label arrives (Day 5) → Status: FULL PRODUCTION RELEASED
├─ Semua department: CAN WORK ✅
├─ Week & Destination: Auto-inherited dari PO Label
└─ Work orders: Auto-generated per department
```

**Business Impact**: 
- Time saved: **5 hari** per order
- On-time delivery: **+15%**

**Requirement dari System**:
- System harus bisa track 2 jenis PO berbeda yang trigger production
- Production status harus punya 2 mode: PARTIAL (sebagian dept boleh jalan) dan RELEASED (semua dept boleh jalan)
- Label info (Week + Destination) harus otomatis ter-inherit ke semua work orders
- System lock/unlock department berdasarkan PO status

---

### 2️⃣ Flexible Production Targets

**Problem**: Defect rate tidak predictable (10-15%), tapi customer minta exact quantity

**Business Solution Needed**:
```
Customer Order: 480 pcs

Production Plan:
├─ Overall Target: 480 pcs (fix, tidak boleh berubah)
├─ Cutting Target: 528 pcs (+10% buffer untuk waste)
├─ Embroidery Target: 516 pcs (+7.5% buffer)
├─ Sewing Target: 552 pcs (+15% buffer, dept paling risky!)
├─ Finishing Target: 504 pcs (+5% buffer)
└─ Packing Target: 480 pcs (EXACT - no buffer)

Catatan: Buffer berbeda per department berdasarkan historical defect rate
```

**Business Impact**:
- Material waste: **-25%**
- Shortage cases: **-40%**

**Requirement dari System**:
- Department target bisa beda dari overall target
- Buffer % configurable per department type
- System monitor realisasi vs target per department
- Alert jika department output terlalu rendah (tidak cukup untuk dept berikutnya)

---

### 3️⃣ 2-Stage Internal Processing (Warehouse Finishing)

**Problem**: Warehouse Finishing punya 2 stage internal (Stuffing → Closing) tanpa surat jalan formal

**Business Workflow**:
```
STAGE 1: STUFFING
Input: Skin (PCS) + Filling (GRAM) + Thread
Output: Stuffed Body (PCS)
├─ Process: Isi kapas ke dalam kulit boneka
├─ Yield: 98% (reject 2%)
└─ Inventory: Skin stock vs Stuffed stock (harus terpisah!)

STAGE 2: CLOSING  
Input: Stuffed Body (PCS) + Hang Tag (PCE)
Output: Finished Doll (PCS)
├─ Process: Pasang hang tag, QC final
├─ Yield: 99% (reject 1%)
└─ Transfer: Siap packing

Note: TIDAK ADA surat jalan antara Stage 1 → Stage 2 (internal conversion)
```

**Business Impact**:
- Inventory visibility: Stage 1 dan Stage 2 harus jelas terpisah
- Material consumption: System harus auto-calculate filling per stuffed body
- Yield tracking: Monitor reject rate per stage

**Requirement dari System**:
- 1 warehouse bisa punya multiple "sub-stages" atau "work centers" internal
- Material tracking per stage (Skin inventory vs Stuffed inventory)
- Internal conversion tanpa formal transfer document
- Auto-calculate material consumption per stage

**⭐ IMPORTANT NOTE: Department-Level Warehouses**

Selain 3 main warehouses (Main, Finishing, Finished Goods), **SETIAP departemen produksi punya warehouse/location sendiri**:
- Warehouse Cutting: WIP cutting results (Cut Body + Cut Baju)
- Warehouse Embroidery: WIP embroidery (include in-transit vendor)
- Warehouse Sewing: WIP sewing (Skin + Baju tracked separately)
- Warehouse Finishing: 2-stage process (Stuffing → Closing)
- Warehouse Packing: Ready-to-pack inventory
- **Warehouse FG (Finished Goods)**: Product jadi siap kirim - organized per pallet (multiple cartons per pallet)

**Stock Opname Requirement**: Setiap departemen melakukan physical count **weekly** (Packing: daily) untuk validasi inventory accuracy. System harus support:
- Physical count input per department location
- Auto-compare physical vs system dengan variance %
- Adjustment workflow dengan approval (jika variance > ±2%)
- Audit trail all adjustments

---

### 4️⃣ Unit Conversion Validation

**Problem**: Manual conversion errors menyebabkan inventory chaos (shortage atau excess tidak terdeteksi)

**Business Scenario**:
```
SCENARIO 1: CUTTING DEPARTMENT
────────────────────────────────
Input Material: 70.38 YARD fabric
Recipe Standard: 0.1005 YARD per piece
Target Output: 480 pcs
Expected Usage: 480 × 0.1005 = 48.24 YARD

Tolerance: ±10%
Acceptable Range: 43.4 - 53.1 YARD

Actual Usage: 70.38 YARD
Variance: +45.7% (ABNORMAL!)

System Action Needed:
⚠️ WARNING: "Material usage abnormal, verify input or marker efficiency"
Option 1: Allow with supervisor approval
Option 2: Block dan require recount


SCENARIO 2: FINISHED GOODS RECEIVING
─────────────────────────────────────
Input: 8 Cartons
Standard: 60 pcs/carton
Expected: 8 × 60 = 480 pcs

Physical Count:
├─ Carton 001-007: 60 pcs each = 420 pcs
└─ Carton 008: 45 pcs (partial)
Total: 465 pcs

Variance: -3.1% (acceptable)

System Action Needed:
⚠️ NOTE: "Partial carton detected (CTN-008: 45 pcs)"
Allow: YES (within tolerance)
Record: Inventory = 465 pcs (not 480)
```

**Business Impact**:
- Inventory accuracy: 82% → **99%+**
- Error detection: Immediate (vs 1-2 minggu manual)
- Prevent fraud: System detect abnormal usage patterns

**Requirement dari System**:
- Auto-validate conversion saat input (real-time checking)
- Configurable tolerance % per conversion type
- Warning level (allow with note) vs Block level (require approval)
- Log all variances untuk audit trail

---

### 5️⃣ Quality Control Loop (Rework/Repair)

**Problem**: Defect tidak tertrack, rework process manual, recovery rate tidak dimonitor

**Business Workflow**:
```
DEFECT DETECTION (QC Inspector)
├─ Checkpoint: 1 of 4 QC points (Cutting/Sewing/Finishing/Packing)
├─ Capture: Qty defect, Type, Root cause, Admin, Machine
└─ Decision: REWORK atau SCRAP?

REWORK ASSIGNMENT (If repairable)
├─ Priority: HIGH/MEDIUM/LOW (based on customer urgency)
├─ Assigned to: Rework specialist
├─ SOP: Step-by-step repair instructions
└─ Est. Time: Auto-calculate based on defect type

RE-INSPECTION (Same QC Inspector)
├─ Result: PASS → Add back to Good Output
├─ Result: FAIL → Send to Scrap
└─ Recovery Rate: Track % success per defect type

REPORTING & ANALYSIS
├─ Cost of Poor Quality (COPQ): Rework labor + scrap
├─ Root Cause Analysis: Which admin/machine most defect
└─ Trend: Defect rate improvement over time
```

**Business Impact**:
- Defect visibility: From 0% → **100%** tracked
- Recovery rate: Monitor apakah rework effective
- COPQ reduction: **-30%** (better root cause action)
- Admin training: Data-driven improvement

**Requirement dari System**:
- Easy defect capture (mobile-friendly jika possible)
- Auto-calculate COPQ per work order
- Rework queue dengan priority management
- Root cause analysis & reporting

---

## 🎯 SUCCESS CRITERIA

### Technical Requirements
✅ System must handle 30+ materials per product (multi-level recipe)  
✅ System must support 6+ unit types with auto-conversion (YARD, GRAM, CM, PCS, BOX, CARTON)  
✅ Real-time inventory visibility across 3 warehouses  
✅ Production tracking per department real-time  
✅ Mobile-friendly untuk production floor input  

### User Experience Requirements
✅ **SIMPLE & INTUITIVE** - Admin yang tidak tech-savvy bisa pakai dengan training minimal  
✅ **FAST INPUT** - Production team bisa input data <2 menit per work order  
✅ **CLEAR ALERTS** - Error messages jelas dalam Bahasa Indonesia  
✅ **MINIMAL CLICKS** - Reduce repetitive data entry (auto-fill where possible)  

### Business Outcomes (Post-Implementation)
✅ Lead time reduction: **-28%** (25 hari → 18 hari)  
✅ On-time delivery: **+27%** (75% → 95%+)  
✅ Inventory accuracy: **+20%** (82% → 98%+)  
✅ Reporting time: **-99%** (3-5 hari → real-time)  
✅ **User satisfaction**: Admin comfortable & confident menggunakan system  

---

## 🚨 CRITICAL SUCCESS FACTORS

### 1. User Adoption (PALING PENTING!)

**Context**: Previous ERP implementation gagal karena:
- ❌ Sistem tidak sesuai workflow (force-fit standard system)
- ❌ Training tidak adequate (admin tidak paham cara pakai)
- ❌ Vendor support buruk (banyak bug tidak fixed)
- ❌ Change management gagal (resistance from team)

**What We Need dari Vendor**:
- ✅ **Customization commitment**: Sistem disesuaikan workflow Quty (bukan sebaliknya!)
- ✅ **Proper training plan**: Hands-on, per role, dengan success criteria jelas
- ✅ **Post-implementation support**: Fast response SLA, dedicated support team
- ✅ **Proof of concept**: Demo critical features sebelum commit full project

**Expectation**: Admin yang sekarang trauma ERP harus **comfortable & confident** menggunakan system baru

### 2. Workflow Flexibility

**We CANNOT change our business process karena**:
- Customer IKEA punya strict requirements (Week-based delivery, exact quality standards)
- Manufacturing process sudah proven (15+ tahun experience)
- Team sudah terbiasa dengan current workflow (training new workflow = high risk)

**What We Need**: ERP system yang **adapt to us**, bukan kita yang adapt to standard ERP

### 3. Realistic Timeline

**We NEED**: Clear phased implementation dengan milestone yang achievable
- Phase 1: Core functions (Purchasing, Inventory, Basic Production)
- Phase 2: Advanced features (Quality, Reporting, Analytics)
- Phase 3: Nice-to-have (Mobile app, Advanced automation)

**Timeline expectation**: <6 bulan untuk Phase 1 (core operational)

---

## 📋 LANGKAH SELANJUTNYA

### Yang PT Quty Harapkan dari Vendor

**1. Gap Analysis Consultation** (2-3 sesi workshop):
- Vendor team memahami **7 unique business requirements** secara detail
- Walk through **end-to-end workflow** dari Purchasing sampai Finished Goods
- Discuss **previous ERP failure** dan bagaimana mitigate (pain point #11)

**2. Feasibility Assessment**:
- Apakah vendor punya experience dengan **manufacturing complexity similar**?
- Case study successful implementation di soft toys / garment / textile industry?
- Reference contact yang bisa PT Quty hubungi untuk testimonial?

**3. Solution Proposal** sebagai output dari Gap Analysis:
- Detailed solution design untuk 7 unique requirements
- Implementation approach & methodology
- Timeline dengan milestone clear (phased approach)
- Resource requirement dari kedua belah pihak
- Commercial proposal (license, implementation cost, training, support)

**4. Training & Change Management Plan**:
- Training methodology untuk **admin yang trauma ERP**
- Duration & success criteria per role
- Post-training support mechanism
- User acceptance testing approach

**5. Support & Maintenance Commitment**:
- Post-GoLive support: Response time? Escalation path?
- Bug fix commitment: Berapa lama resolve critical issue?
- Enhancement request process & pricing
- System upgrade policy (impact pada customization?)

---

## ✅ DECISION CRITERIA

### We Will PROCEED if:
✅ Semua 7 unique requirements **feasible** dengan customization reasonable  
✅ Vendor punya **proven track record** di manufacturing industry  
✅ Timeline realistic **<6 bulan** untuk core implementation  
✅ Commercial proposal **reasonable** dengan scope jelas  
✅ Training & change management plan **solid**  
✅ Post-implementation support **commitment clear** dengan SLA  

### We Will REJECT if:
❌ Vendor coba **force-fit** standard system tanpa proper customization  
❌ No experience dengan **similar manufacturing complexity**  
❌ Timeline unrealistic (too fast atau too long)  
❌ Commercial proposal tidak transparent atau terlalu mahal  
❌ Training plan generic (tidak address trauma dari previous implementation)  
❌ Support SLA vague atau tidak commit  

---

## 📞 CONTACT & NEXT STEPS

**Contact Person**: Daniel Rizaldy (IT Lead)  
**Company**: PT Quty Karunia  
**Location**: Indonesia  

**Requested Action dari Vendor**:
1. Review dokumen requirements ini
2. Schedule **Gap Analysis Consultation** (initial meeting 1-2 jam)
3. Prepare **consultation quote** untuk Gap Analysis phase
4. Assign **Project Director & Business Analyst** untuk deep dive

**Timeline**:
- Initial meeting: **ASAP** (within 1-2 minggu)
- Gap Analysis phase: 2-4 minggu
- Proposal submission: 1 minggu after Gap Analysis
- Decision: 1-2 minggu after proposal review

---

**Document Status**: ✅ Ready for Vendor Review  
**Version**: 1.0  
**Last Updated**: 13 Februari 2026  
**Prepared By**: IT Lead PT Quty Karunia  

> 🎯 **Call to Action**: Menunggu **Gap Analysis Consultation Quote** dari ERP Vendor Team

> ⚠️ **Important Context**: Ini adalah **last chance** untuk ERP di PT Quty. Previous implementation GAGAL. Management sangat skeptis. **HARUS BERHASIL** kali ini atau Quty akan permanent abandon ERP idea dan kembali ke manual system selamanya.
