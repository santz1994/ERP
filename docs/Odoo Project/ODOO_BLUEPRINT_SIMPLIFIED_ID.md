# 🏢 ODOO IMPLEMENTATION BLUEPRINT - VERSI RINGKAS
## PT Quty Karunia - Gap Analysis Quick Reference

**Jenis Dokumen**: Ringkasan Requirements untuk Gap Analysis Phase  
**Perusahaan**: PT Quty Karunia (Soft Toys Manufacturing)  
**Industri**: Soft Toys Manufacturing (B2B - Supplier IKEA)  
**Disusun Oleh**: IT Lead - Daniel Rizaldy  
**Tanggal**: 13 Februari 2026  
**Target**: Odoo PM & BA (Quick Reference untuk Workshop)  
**Status**: ✅ SIAP UNTUK GAP ANALYSIS WORKSHOP  

> 📘 **CATATAN**: Dokumen ini adalah **versi ringkas** dari ODOO_IMPLEMENTATION_BLUEPRINT.md (50 halaman). Untuk detail lengkap, lihat dokumen full version.

---

## 📋 ISI DOKUMEN

1. [Ringkasan Eksekutif](#executive-summary)
2. [Profil Perusahaan Singkat](#company-profile)
3. [Pain Points Utama](#pain-points)
4. [7 Fitur Unik (CORE GAP!)](#unique-features)
5. [Odoo Modules yang Dibutuhkan](#modules-needed)
6. [Gap Analysis Ringkas](#gap-analysis)
7. [Strategi Customization](#customization-strategy)
8. [Estimasi Timeline & Effort](#timeline-effort)
9. [Langkah Selanjutnya](#next-steps)

---

<a name="executive-summary"></a>
## 📊 RINGKASAN EKSEKUTIF

### Konteks Project

PT Quty Karunia adalah manufacturer soft toys dengan **IKEA sebagai customer utama** (80% revenue). Volume produksi 50,000-80,000 pcs/bulan dengan kompleksitas tinggi (30+ material SKU per artikel).

### Tantangan Utama

**⚠️ CRITICAL**: Soft toys manufacturing memiliki **7 karakteristik unik** yang TIDAK ada di Odoo standard maupun industry manufacturing modules:

1. **Dual Trigger Production System** - 2 jenis PO trigger produksi (Kain = early start, Label = full release)
2. **Flexible Target per Departemen** - SPK target ≠ MO target (buffer management)
3. **Warehouse Finishing 2-Stage** - Internal conversion tanpa surat jalan
4. **UOM Auto-Validation** - Tolerance checking untuk prevent inventory chaos
5. **Real-Time WIP System** - Parallel batch-based transfer
6. **Pull System Auto-Deduction** - Zero paperwork material movement
7. **Rework/Repair Module** - QC defect loop dengan recovery tracking

### Kesimpulan Awal

✅ Implementasi dengan Odoo **FEASIBLE** namun memerlukan:
- **Heavy customization** (12 custom modules perkiraan)
- **Timeline 11 bulan** (end-to-end)
- **Experienced Odoo partner** (familiar Manufacturing + Python dev)
- **Realistic expectations** untuk scope dan effort customization

---

<a name="company-profile"></a>
## 🏭 PROFIL PERUSAHAAN SINGKAT

### Data Dasar

| Aspek | Detail |
|-------|--------|
| **Industri** | Soft Toys Manufacturing (Discrete) |
| **Customer** | IKEA (80% revenue) + others |
| **Volume** | 50,000 - 80,000 pcs/bulan |
| **Lead Time** | 15-25 hari (target: 18 hari) |
| **Produk** | 478 SKU (Boneka, Bantal, Soft Toys) |
| **Karyawan** | ~250 total (40 staff + 210 workers) |

### Proses Produksi (6 Stage)

```
Cutting → Embroidery* → Sewing → Finishing (2-stage) → Packing → FG
         (optional & Vendor)    (Stuffing + Closing)
```

**Unique Process**:
- 1 Finished Good = 2 komponen parallel (Boneka Body + Pakaian)
- Assembly hanya di Packing stage
- Finishing memiliki 2-stage internal conversion (Skin → Stuffed → Finished)

---

<a name="pain-points"></a>
## ❌ PAIN POINTS UTAMA

### Top 5 Critical Problems

| # | Problem | Dampak Bisnis | Severity |
|---|---------|---------------|----------|
| 1 | Data produksi manual (Excel/Kertas) | Laporan lambat 3-5 hari | 🔴 CRITICAL |
| 2 | Material tidak terdata real-time | Produksi STOP tiba-tiba | 🔴 CRITICAL |
| 3 | SPK tidak terpantau | Late delivery → penalty | 🔴 CRITICAL |
| 4 | Finishing process kacau | Stok Skin vs Stuffed tidak jelas | 🔴 CRITICAL |
| 5 | UOM conversion error | Inventory kacau (Yard→Pcs) | 🔴 CRITICAL |

### Operational Impact

- Lead time: 25 hari (target: 18 hari) → **-28% reduction needed**
- On-time delivery: 75% → **95% target** → **+27% improvement needed**
- Inventory accuracy: 82% → **98% target** → **+20% improvement needed**

---

<a name="unique-features"></a>
## 🔥 7 FITUR UNIK (CORE GAP!)

### Feature #1: Dual Trigger Production System

**Konsep**: MO memiliki 2 status (PARTIAL → RELEASED) berdasarkan 2 trigger material

```
TRIGGER 1: PO Kain diterima (Day 1)
├─ MO Status: PARTIAL ⚠️
├─ Allow: Cutting ✅, Embroidery ✅
├─ Block: Sewing ❌, Finishing ❌, Packing ❌
└─ Week/Destination: TBD

TRIGGER 2: PO Label diterima (Day 5-7)
├─ MO Status: RELEASED ✅
├─ Allow: SEMUA dept ✅✅✅
├─ Auto-inherit: Week & Destination dari PO Label
└─ Field Lock: Week/Dest tidak bisa diedit manual
```

**Business Impact**:
- Lead time reduction: **-3 sampai -5 hari** (critical!)
- Human error Week/Dest: **ZERO** (auto-inherit)

**Odoo Gap**: 
- ❌ Odoo MO standard: Binary state (Draft/Confirmed/Done)
- ❌ No partial release per department
- 🔴 **Custom State Machine Required**

**Customization Complexity**: 🔴 **HIGH** (12-15 hari)

---

### Feature #2: Flexible Target System per Departemen

**Konsep**: SPK Target dapat **BERBEDA** dari MO Target (buffer strategy)

```
MO Target: 450 pcs

SPK Strategy per dept:
├─ Cutting: 495 pcs (450 × 1.10 = +10% buffer)
├─ Sewing: 517 pcs (450 × 1.15 = +15% buffer) ← HIGHEST!
├─ Finishing: 480 pcs (demand-driven, adjust real-time)
└─ Packing: 465 pcs (exact urgency match)

Constraint Logic:
    SPK Dept B Target ≤ Good Output Dept A
    
Format Display: Actual/Target pcs (Percentage%)
    Example: 520/517 pcs (100.6%)
```

**Business Impact**:
- Zero shortage risk (defect buffer built-in)
- Material optimization: Waste prediction akurat
- Urgency response: Fast adjustment

**Odoo Gap**:
- ❌ Odoo MO: 1 target applies to all work orders
- ❌ No buffer % configuration per operation
- 🔴 **Complex Logic Custom Required**

**Customization Complexity**: 🔴 **HIGH** (10-12 hari)

---

### Feature #3: Warehouse Finishing 2-Stage Internal Conversion

**Konsep**: Internal warehouse dengan 2 inventory terpisah tanpa surat jalan

```
WAREHOUSE FINISHING:

Location 1: SKIN Stock
    ├─ Product: WIP_SKIN
    ├─ Qty tracking per SKU
    └─ Min/Max alert

Location 2: STUFFED BODY Stock  
    ├─ Product: WIP_BONEKA
    ├─ Qty tracking per SKU
    └─ Min/Max alert

Internal Conversion (Paperless):
    Stage 1: Skin + Filling → Stuffed Body
    Stage 2: Stuffed Body + Hang Tag → Finished Doll
    
    No DN/SJ eksternal, system auto-update inventory
```

**Business Impact**:
- Kontrol akurat per stage
- Material tracking precise (filling consumption per batch)
- Paperless workflow

**⭐ CATATAN PENTING: Warehouse Per Departemen**

Selain 3 main warehouses (Main, Finishing, FG - organized per pallet untuk shipment), **setiap departemen produksi punya warehouse/location sendiri**:
- WH-Cutting, WH-Embroidery, WH-Sewing, WH-Finishing, WH-Packing
- **Stock Opname Weekly**: Setiap departemen physical count untuk validasi inventory
- System harus support multi-location tracking + stock opname workflow dengan approval
- **WH-FG Details**: Product jadi dalam bentuk per pallet (multiple cartons per pallet, ready to ship)

**Odoo Gap**:
- ⚠️ Odoo Manufacturing: 1-stage per Work Center
- ❌ No 2-stage internal conversion di 1 location
- ⚠️ Stock Opname feature ada, tapi perlu enhancement untuk approval workflow
- 🔴 **Custom Location & Work Center Logic + Stock Opname Enhancement**

**Customization Complexity**: 🟠 **MEDIUM-HIGH** (8-10 hari)

---

### Feature #4: UOM Conversion Auto-Validation

**Konsep**: Real-time validation untuk prevent inventory chaos

```
CRITICAL POINT 1: CUTTING (YARD → PCS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: 70.38 YARD fabric
BOM Reference: 0.1005 YARD/pcs
Target Output: 480 pcs
Expected: 48.24 YD

Tolerance: ±10% → Range: 43.4 - 53.1 YD

System Check:
    70.38 YD in range? NO!
    Variance: +45.7% (too high!)
    
Alert:
    ⚠️ WARNING: "Material usage abnormal"
    Log variance untuk investigasi


CRITICAL POINT 2: FG RECEIVING (CTN → PCS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: 8 Cartons
Standard: 60 pcs/CTN
Expected: 480 pcs

Physical Count: 465 pcs (partial carton)

System Check:
    Variance: -3.1% (acceptable)
    
Alert:
    ⚠️ NOTE: "Partial carton detected"
    Update inventory: 465 pcs (not 480)
```

**Business Impact**:
- Inventory accuracy: 99%+ (vs 82% manual)
- Error prevention sejak awal
- Audit trail lengkap

**Odoo Gap**:
- ⚠️ Odoo Multi-UOM: Support conversion BUT no auto-validation
- ❌ No tolerance % configuration
- 🔴 **Custom Validation Logic**

**Customization Complexity**: 🟠 **MEDIUM** (5-7 hari)

---

### Feature #5: Rework/Repair Module (QC Integration)

**Konsep**: Defect tracking dengan recovery workflow

```
DEFECT LIFECYCLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. DEFECT CAPTURE (Auto by QC)
   ├─ Source: QC Checkpoint 1-4
   ├─ Data: Qty, Type, Root Cause, Admin
   └─ Decision: REWORK atau SCRAP?

2. REWORK QUEUE
   ├─ Priority: HIGH/MEDIUM/LOW
   ├─ Assigned to: Rework Specialist
   └─ SOP: Step-by-step repair

3. RE-QC INSPECTION
   ├─ Pass → Add back to Good Output
   └─ Fail → SCRAP

4. RECOVERY RATE TRACKING
   └─ Target: >80% berhasil diperbaiki
```

**Business Impact**:
- Waste minimization
- Root cause tracking per admin/line
- COPQ (Cost of Poor Quality) analysis

**Odoo Gap**:
- ⚠️ Odoo Quality: Basic QC check saja
- ❌ No rework workflow built-in
- 🔴 **Custom Rework Module**

**Customization Complexity**: 🟠 **MEDIUM** (6-8 hari)

---

### Feature #6: Real-Time WIP System

**Konsep**: Real-time tracking WIP per departemen dengan batch transfer

**Business Impact**:
- Visibility penuh semua WIP
- Bottleneck detection cepat

**Odoo Gap**: ⚠️ Moderate customization (custom views)

**Customization Complexity**: 🟡 **LOW-MEDIUM** (4-5 hari)

---

### Feature #7: Pull System Auto Material Deduction

**Konsep**: Material auto-deduct saat production confirm (no manual DN)

**Business Impact**:
- Zero paperwork
- Real-time inventory update

**Odoo Gap**: ⚠️ Minor customization (Odoo sudah support)

**Customization Complexity**: 🟡 **LOW** (2-3 hari)

---

<a name="modules-needed"></a>
## 📦 ODOO MODULES YANG DIBUTUHKAN

### Priority 1 (CRITICAL - Must Have)

| Module | Usage | Standard Fit | Customization |
|--------|-------|--------------|---------------|
| **Manufacturing (MRP)** | MO & SPK generation | ⚠️ 50% fit | 🔴 Heavy (Dual Trigger) |
| **Inventory** | Material tracking | ⚠️ 60% fit | 🔴 Heavy (Multi-UOM) |
| **Purchase** | PO creation | ✅ 90% fit | ⚠️ Minor (PO Type) |
| **Quality** | QC checkpoints | ⚠️ 40% fit | 🔴 Heavy (Rework) |

### Priority 2 (HIGH - Important)

| Module | Usage | Standard Fit | Customization |
|--------|-------|--------------|---------------|
| **Warehouse** | Multi-warehouse | ✅ 70% fit | ⚠️ Moderate (Finishing 2-stage) |
| **Reporting** | Dashboard & KPI | ⚠️ 50% fit | 🔴 Heavy (PPIC Dashboard) |
| **MRP Planning** | Material planning | ⚠️ 60% fit | 🔴 Heavy (Dual BOM) |

### Priority 3 (NICE-TO-HAVE)

| Module | Usage | Standard Fit | Customization |
|--------|-------|--------------|---------------|
| **Barcode** | FG scanning | ✅ 90% fit | ⚠️ Minor (Custom Android) |
| **Portal** | Supplier portal | ✅ 80% fit | 🟡 Low |

**Legend**:
- ✅ Standard dapat digunakan langsung
- ⚠️ Moderate customization needed
- 🔴 Heavy customization / custom module required

---

<a name="gap-analysis"></a>
## 🔍 GAP ANALYSIS RINGKAS

### Ringkasan Gap Odoo Standard vs Quty Requirements

| Requirement Area | Odoo Standard | Quty Need | Gap Level | Solution |
|-----------------|---------------|-----------|-----------|----------|
| **MO State Management** | Draft/Confirmed/Done | PARTIAL/RELEASED | 🔴 HIGH | Custom state machine |
| **Work Order Target** | Fixed (= MO qty) | Flexible (buffer %) | 🔴 HIGH | Custom WO logic |
| **Warehouse Finishing** | Standard location | 2-stage conversion | 🟠 MED | Custom location + WC |
| **UOM Validation** | Basic conversion | Auto-validation + tolerance | 🟠 MED | Custom validation |
| **Rework Module** | Not available | Full rework workflow | 🟠 MED | Custom module |
| **Material Allocation** | At MO level | Per WO by dept | 🟠 MED | Custom allocation |
| **BOM Views** | Single view | Dual (Production vs Purchasing) | 🟡 LOW | Custom report |
| **PPIC Dashboard** | Standard | Real-time custom | 🔴 HIGH | Custom dashboard |

### Summary Gap Level

- 🔴 **HIGH Gap** (3 areas): Memerlukan custom module atau heavy modification
- 🟠 **MEDIUM Gap** (4 areas): Memerlukan moderate customization
- 🟡 **LOW Gap** (1 area): Minor customization atau configuration

**Overall Assessment**: **Odoo CAN handle** dengan **heavy customization** (60-70% standard + 30-40% custom)

---

<a name="customization-strategy"></a>
## 🛠️ STRATEGI CUSTOMIZATION

### 12 Custom Modules Dibutuhkan

**High Priority (Must Have - Phase 1-2)**:

1. **mrp_dual_trigger** (15 hari) - PARTIAL/RELEASED state
2. **mrp_flexible_target** (12 hari) - SPK buffer logic
3. **mrp_realtime_wip** (10 hari) - Real-time WIP tracking
4. **quality_rework** (8 hari) - Rework workflow  
5. **stock_finishing_warehouse** (10 hari) - 2-stage Finishing
6. **stock_uom_validation** (6 hari) - Tolerance checking

**Medium Priority (Important - Phase 3)**:

7. **stock_material_debt** (5 hari) - Negative inventory management
8. **mrp_material_allocation** (12 hari) - Material per WO
9. **web_ppic_dashboard** (15 hari) - Custom dashboard

**Low Priority (Nice-to-Have - Phase 4)**:

10. **purchase_po_classification** (3 hari) - PO Type field
11. **mrp_week_destination** (3 hari) - Week/Dest tracking
12. **stock_barcode_fg** (3 hari) - FG barcode

**Total Development Effort**: **123 hari** (~ 6 bulan dengan 1 developer)

### Development Approach

**Option A: Odoo Partner** (Recommended)
- ✅ Expert Odoo developers
- ✅ Odoo upgrade support
- ⚠️ Requires proper evaluation of scope
- ✅ Lower risk

**Option B: Internal Development**
- ⚠️ Need hire/train Odoo developer
- ✅ More control over development
- 🔴 Higher risk
- ⚠️ Longer timeline (+3-4 bulan)

---

<a name="timeline-effort"></a>
## 📅 ESTIMASI TIMELINE & EFFORT

### Phased Implementation (11 Bulan)

**PHASE 0: DISCOVERY & DESIGN** (4 minggu)
- Gap Analysis Workshop (1 minggu)
- Solution Design (2 minggu)
- Approval & Kick-off (1 minggu)

**PHASE 1: FOUNDATION** (8 minggu)
- Odoo installation & config (2 minggu)
- Master data migration (2 minggu)
- Sales & Purchase setup (2 minggu)
- Inventory & Warehouse config (2 minggu)

**PHASE 2: MANUFACTURING CORE** (12 minggu)
- Dual Trigger module (4 minggu)
- Flexible Target module (3 minggu)
- Material Allocation (3 minggu)
- PO Classification + Week/Dest (2 minggu)

**PHASE 3: WIP & WAREHOUSE** (10 minggu)
- Real-Time WIP (4 minggu)
- Finishing Warehouse (3 minggu)
- UOM Validation (2 minggu)
- Material Debt (1 minggu)

**PHASE 4: QUALITY & REPORTING** (6 minggu)
- Rework Module (3 minggu)
- PPIC Dashboard (3 minggu)

**PHASE 5: MOBILE & INTEGRATION** (4 minggu)
- Barcode FG (1 minggu)
- Android app integration (2 minggu)
- Email/notification (1 minggu)

**PHASE 6: UAT & TRAINING** (4 minggu)
- UAT all modules (2 minggu)
- Training (1 minggu)
- Bug fixing (1 minggu)

**PHASE 7: GO-LIVE** (2 minggu)
- Data migration final (1 minggu)
- Go-Live + Hypercare (1 minggu)

**TOTAL**: **46 minggu** (~ 11 bulan)

### Resource Requirement

**From Odoo Partner**:
- Project Manager (20% FTE)
- Sr. Odoo Developer (100% FTE)
- Jr. Odoo Developer (50% FTE)
- Business Analyst (30% FTE)

**From Quty**:
- Project Sponsor (Manager level)
- IT Lead (80% FTE)
- Key Users (PPIC, SPV, Admin) - 20% FTE
- Data Migration Support (Temp work)

---

<a name="next-steps"></a>
## 🎯 LANGKAH SELANJUTNYA

### Step 1: Validation Workshop (Week 1)

**Agenda**:
- Factory visit (walking the floor)
- Interview key users (10+ orang: PPIC, SPV, Admin, Manager)
- Validate 7 unique features dengan actual process
- Demo prototype features (jika ada)

**Output**: Validated requirements document

### Step 2: Solution Design (Week 2-3)

**Deliverables**:
- Detailed technical design untuk 12 custom modules
- Database schema mapping (prototype → Odoo)
- UI/UX wireframe untuk custom views
- Integration architecture (mobile app, notification)

**Output**: Solution Design Document

### Step 3: Proof of Concept (Week 4)

**Scope**: Build mini-prototype untuk 3 critical features:
1. Dual Trigger Production System
2. Flexible Target per Work Order
3. Real-Time WIP Dashboard

**Output**: Working POC untuk demo ke Management

### Step 4: Proposal & Contract (Week 5-6)

**Deliverables**:
- Fixed price proposal per module
- Timeline dengan milestones
- SLA untuk support & maintenance
- Payment terms

**Output**: Signed contract

### Step 5: Project Kick-Off (Week 7)

- Project team formation
- Development environment setup
- Sprint planning (Agile)
- **START PHASE 1 IMPLEMENTATION**

---

## 📊 SUMMARY TABLE - CRITICAL FEATURES

| Feature | Business Impact | Odoo Gap | Customization | Effort (days) | Priority |
|---------|----------------|----------|---------------|---------------|----------|
| Dual Trigger MO | Lead time -5 hari | HIGH | Heavy | 15 | P0 |
| Flexible Target | Zero shortage | HIGH | Heavy | 12 | P0 |
| Warehouse Finishing | Kontrol akurat | MEDIUM | Moderate | 10 | P0 |
| UOM Validation | Inventory 99% | MEDIUM | Moderate | 6 | P0 |
| Rework Module | Waste -40% | MEDIUM | Moderate | 8 | P1 |
| Real-Time WIP | Bottleneck detection | LOW | Light | 10 | P1 |
| Pull System | Paperless | LOW | Light | 3 | P2 |

**Total Critical Path**: 64 hari development untuk P0+P1 features

---

## 📞 KONTAK

**Disusun Oleh**: IT Lead PT Quty Karunia  
**Email**: it@qutykarunia.com  
**Untuk**: Odoo Partner - Gap Analysis Phase  

**Dokumen Status**: ✅ **SIAP UNTUK GAP ANALYSIS WORKSHOP**

**Versi Dokumen**: 1.0 Simplified  
**Tanggal**: 13 Februari 2026  
**Halaman**: ~15 halaman (vs 50 halaman full version)

---

**CATATAN PENTING UNTUK ODOO TEAM**:

1. ⚠️ **7 unique features** adalah **NON-NEGOTIABLE** - ini adalah core business process Quty
2. ⚠️ **Timeline 11 bulan** adalah realistis untuk customization level ini
3. ⚠️ **Scope evaluation** untuk customization diperlukan dalam Gap Analysis session
4. ⚠️ **Proof of Concept** SANGAT DISARANKAN sebelum commit full implementation
5. ✅ **Odoo Partner HARUS experienced** dalam Manufacturing + Heavy Customization

**END OF SIMPLIFIED BLUEPRINT**
