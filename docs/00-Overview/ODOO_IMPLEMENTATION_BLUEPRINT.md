# 🏢 ODOO IMPLEMENTATION BLUEPRINT
## ERP Quty Karunia - Requirements & Gap Analysis Lengkap

**Jenis Dokumen**: Requirements Implementasi untuk Odoo Partner  
**Perusahaan**: PT Quty Karunia (Soft Toys Manufacturing)  
**Industri**: Soft Toys Manufacturing (B2B - Supplier IKEA)  
**Disusun Oleh**: IT Director Project  
**Tanggal**: 13 Februari 2026  
**Status**: ✅ SIAP UNTUK ODOO DEEP DIVE  

---

## 📑 RINGKASAN EKSEKUTIF

### Konteks Project

PT Quty Karunia adalah **manufacturer soft toys** dengan customer utama IKEA. Perusahaan telah mengembangkan **custom ERP prototype** yang sangat spesifik untuk industri soft toys manufacturing dengan unique business requirements yang **TIDAK standard** di industry lain.

### Tujuan Dokumen Ini

Dokumen ini adalah **blueprint lengkap** untuk membantu tim Odoo:
1. **Memahami** business process & pain points PT Quty Karunia secara detail
2. **Mengidentifikasi GAP** antara Odoo standard modules vs custom requirements
3. **Merencanakan** customization & development strategy
4. **Memvalidasi** feasibility implementasi dengan Odoo platform

### Tantangan Utama

**⚠️ CRITICAL**: Sistem ERP yang dibutuhkan mengandung **10+ unique features** yang TIDAK ada di Odoo standard maupun industry modules. Implementasi memerlukan **heavy customization**.

---

## 📖 DAFTAR ISI

### BAGIAN A: REQUIREMENTS BISNIS
1. [Profil Perusahaan & Konteks Bisnis](#section-1)
2. [Pain Points & Masalah Saat Ini](#section-2)
3. [Workflow Produksi Lengkap](#section-3)
4. [Struktur Organisasi & Peran](#section-4)

### BAGIAN B: REQUIREMENTS FUNGSIONAL
5. [Modul Inti & Fitur](#section-5)
6. [Fitur Custom Unik (USP)](#section-6)
7. [Logika BOM & Manufacturing](#section-7)
8. [Manajemen Inventory & Warehouse](#section-8)
9. [Quality Control & Modul Rework](#section-9)

### BAGIAN C: REQUIREMENTS TEKNIS
10. [Arsitektur & Technology Stack](#section-10)
11. [Overview Database Schema](#section-11)
12. [Requirements Integrasi](#section-12)
13. [Aplikasi Mobile](#section-13)
14. [Reporting & Analytics](#section-14)

### BAGIAN D: GAP ANALYSIS & SOLUTION DESIGN
15. [Gap: Odoo Standard vs Requirements](#section-15)
16. [Strategi Customization](#section-16)
17. [Development Roadmap](#section-17)
18. [Risk Assessment](#section-18)

---

<a name="section-1"></a>
## 1️⃣ PROFIL PERUSAHAAN & KONTEKS BISNIS

### Gambaran Industri

**Sektor**: Soft Toys Manufacturing (B2B)  
**Customer Utama**: IKEA Sweden (80% revenue)  
**Volume Produksi**: 50,000 - 80,000 pcs/bulan  
**Kompleksitas Produk**: HIGH (30+ material SKU per artikel)  
**Mode Produksi**: Make-to-Order (MTO) + Partial Make-to-Stock (MTS)

### Karakteristik Bisnis

| Aspek | Detail |
|--------|--------|
| **Tipe Manufacturing** | Discrete Manufacturing dengan Complex Assembly |
| **Proses Produksi** | 6-Stage Sequential + 2 Parallel Streams (Cutting → Embroidery* → Sewing → Finishing → Packing) |
|  | *Embroidery: Internal OR Vendor Eksternal (outsourced) |
| **Lead Time** | 15-25 hari (dari PO sampai Ship) |
| **Pola Order** | Weekly delivery schedule (Week-based planning) |
| **Destination** | Multi-country (Belgium, Sweden, USA, dll) |
| **Strategi Inventory** | JIT untuk Label, Min/Max untuk Fabric & Filling |

### Karakteristik Industri yang Unik

**🔥 Soft Toys Manufacturing adalah SANGAT SPESIFIK**:

1. **Dual Component Production**:
   - 1 Finished Good = 2 parallel items (Boneka + Baju)
   - Masing-masing memerlukan BOM terpisah, SPK terpisah
   - Assembly hanya di stage Packing

2. **Complex Material Mix**:
   - 9-12 jenis fabric per artikel (YARD)
   - 9 jenis thread per artikel (CM)
   - Filling/Kapas (GRAM/KG)
   - Labels & accessories (PCE)
   - Carton & packing (PCE/SET)
   - **Multi-UOM nightmare!**

3. **2-Stage Finishing Process**:
   - Stage 1: Stuffing (Skin → Stuffed Body)
   - Stage 2: Closing (Stuffed Body → Finished Doll)
   - **Internal warehouse conversion** tanpa surat jalan formal

4. **Label-Driven Production**:
   - Label berisi **Week & Destination** info
   - Label adalah **last material** yang datang (long lead time)
   - Production **cannot finish** without label
   - **PO Label adalah trigger kritis** untuk full production

5. **Embroidery Optional Routing**:
   - Tidak semua artikel butuh embroidery
   - Dynamic routing (Route 1, 2, atau 3)
   - Routing mempengaruhi SPK generation

---

<a name="section-2"></a>
## 2️⃣ PAIN POINTS & MASALAH SAAT INI

### Masalah Historis (Sebelum ERP)

| No | Masalah | Dampak | Frekuensi | Severity |
|----|---------|--------|-----------|----------|
| 1 | **Data Produksi Manual** (Excel/Kertas) | Laporan lambat 3-5 hari | Harian | 🔴 HIGH |
| 2 | **Material Tidak Terdata** | Tiba-tiba habis → produksi stop | Mingguan | 🔴 CRITICAL |
| 3 | **SPK Tidak Terpantau** | Delay baru ketahuan saat deadline | Harian | 🔴 HIGH |
| 4 | **FinishGood Sulit Verifikasi** | Salah hitung → customer complaint | Per shipment | 🟠 MEDIUM |
| 5 | **Approval Tidak Jelas** | Tidak tahu siapa approve apa | Per change | 🟠 MEDIUM |
| 6 | **Laporan Bulanan Lambat** | Decision making terlambat | Bulanan | 🟡 LOW |
| 7 | **Finishing Process Kacau** | Stok Skin vs Stuffed tidak jelas | Harian | 🔴 HIGH |
| 8 | **UOM Conversion Error** | Inventory kacau (Yard→Pcs, Box→Pcs) | Per transaksi | 🔴 CRITICAL |
| 9 | **Target Produksi Rigid** | Shortage karena defect tidak diprediksi | Mingguan | 🟠 MEDIUM |
| 10 | **Defect Tidak Tertrack** | Waste tinggi, root cause tidak jelas | Harian | 🟠 MEDIUM |

### Kuantifikasi Dampak Bisnis

**Dampak Operasional**:
- Lead time: 25 hari (target: 18 hari)
- On-time delivery: 75% (target: 95%)
- Inventory accuracy: 82% (target: 98%)
- Manual reporting time: 15 jam/minggu (target: 1 jam)

---

<a name="section-3"></a>
## 3️⃣ WORKFLOW PRODUKSI LENGKAP

### Alur Proses End-to-End

```
┌─────────────────────────────────────────────────────────────────────┐
│  ALUR PRODUKSI LENGKAP - 7 FASE UTAMA                          │
└─────────────────────────────────────────────────────────────────────┘

FASE 1: PURCHASING (3 Parallel Streams)
════════════════════════════════════════════════════════════════════
Customer Order (IKEA)
    │
    ├─→ [Purchasing A] → PO KAIN (Fabric) 🔑 TRIGGER 1
    ├─→ [Purchasing B] → PO LABEL (Label) 🔑 TRIGGER 2 (CRITICAL!)
    └─→ [Purchasing C] → PO ACCESSORIES (Thread, Filling, Carton)
    
Lead Time:
- Fabric: 3-5 hari ✅ Cepat
- Accessories: 2-3 hari ✅ Cepat  
- Label: 7-10 hari ⚠️ LAMA (bottleneck!)


FASE 2: PRODUCTION PLANNING (Managed by Purchasing → Production)
════════════════════════════════════════════════════════════════════
PO Kain Diterima → Buat MO (MODE: PARTIAL)
    │
    ├─ Status: PARTIAL ⚠️
    ├─ Allow: Cutting + Embroidery (early start)
    ├─ Block: Sewing, Finishing, Packing (tunggu Label)
    └─ Week/Destination: TBD (dari PO Label nanti)

PO Label Diterima → Upgrade MO (MODE: RELEASED)
    │
    ├─ Status: RELEASED ✅
    ├─ Auto-inherit: Week & Destination (read-only)
    ├─ Allow: SEMUA departemen
    └─ Auto-generate: 4-6 SPK per departemen

**Catatan**: Tidak ada PPIC department. Planning flow: Purchasing → Warehouse → Production → FG


FASE 3: EKSEKUSI PRODUKSI (6 Stages)
════════════════════════════════════════════════════════════════════

STAGE 1: CUTTING (2 Parallel Streams)
─────────────────────────────────────
Input: Fabric (YARD)
Output: Cut Body + Cut Baju (PCS)
Conversion: YARD → PCS (via BOM marker)
Buffer: +10% (antisipasi waste)

    Stream A: Cut Body (untuk Boneka)
    Stream B: Cut Baju (untuk Pakaian)

Transfer: 
    Body → Embroidery (jika Route 1) atau Sewing (jika Route 2)
    Baju → Hold di Warehouse Main (sampai Packing)


STAGE 2: EMBROIDERY (Opsional, Body Saja)
─────────────────────────────────────────
Input: Cut Body (PCS)
Output: Embroidered Body (PCS)
Proses: Logo, Text, Detail
Routing: Hanya Route 1 (jika artikel perlu embroidery)

**Lokasi Pengerjaan**:
├─ Option A: Internal Factory (jika punya mesin embroidery)
│   └─ Direct transfer: Cutting → Embroidery Dept → Sewing
│
└─ Option B: Vendor Eksternal (outsourced)
    ├─ Transfer OUT: Cutting → Kirim ke Vendor (DN)
    ├─ Vendor Process: 2-3 hari
    ├─ Transfer IN: Terima dari Vendor → Warehouse Main
    └─ Data Entry: Staff input hasil vendor ke system

Transfer: → Sewing Body


STAGE 3: SEWING (2 Parallel Streams)
─────────────────────────────────────
Input: Embroidered Body (atau Cut Body) + Thread + Accessories
Output: Skin (Body sewn) + Baju (sewn)
Buffer: +15% (highest defect rate dept)
Constraint: Target ≤ Previous dept output

    Stream A: Sewing Body → Skin
    Stream B: Sewing Baju → Baju Complete

Transfer:
    Skin → Warehouse Finishing
    Baju → Hold di Warehouse Main


STAGE 4A: WAREHOUSE FINISHING - Stuffing (Konversi Internal)
────────────────────────────────────────────────────────────────
Input: Skin (PCS) + Filling (GRAM/KG) + Thread
Output: Stuffed Body (PCS)
Proses: Isi kapas, jahit tutup
Yield: 98% (reject 2%)
Inventory: Track terpisah (Skin stock vs Stuffed stock)

Transfer: → Stage 4B (internal, no DN)


STAGE 4B: WAREHOUSE FINISHING - Closing (Final Touch)
────────────────────────────────────────────────────────────────
Input: Stuffed Body (PCS) + Hang Tag (PCE)
Output: Finished Doll (PCS)
Proses: Pasang hang tag, QC final
Yield: 99% (reject 1%)

Transfer: → Warehouse Main (ready for Packing)


STAGE 5: PACKING (Assembly)
─────────────────────────────────────
Input: Finished Doll + Baju + Carton + Label + Sticker
Output: Packed FG (CTN = Cartons)
Proses: 1 set = 1 Boneka + 1 Baju
Conversion: 60 pcs per carton (standard)
Target: Exact match urgency (no buffer)

Label Required Fields:
    - Week: W05-2026
    - Destination: Belgium
    - PO Reference: PO-LBL-2026-0789
    - Artikel Code: 40551542

Transfer: → Warehouse Finished Goods


FASE 4-6: QUALITY CONTROL (4 Checkpoints)
════════════════════════════════════════════════════════════════════
QC1: After Cutting (size check)
QC2: After Sewing (stitch quality) ← HIGH DEFECT RATE!
QC3: After Finishing (appearance)
QC4: Before Packing (safety & compliance)

Rework Module:
    Defect → QC Inspection → Rework Queue → Re-QC → PASS/SCRAP
    Recovery Rate Target: >80%


FASE 7: FINISHED GOODS & SHIPPING
════════════════════════════════════════════════════════════════════
Output: 8 Cartons (465 pcs) packed
Status: READY TO SHIP Week 05
Verifikasi: Barcode scanning via Android app
Dokumentasi: Packing list, shipping label auto-generate
```

### Constraint Produksi Utama

| Jenis Constraint | Aturan | Contoh |
|-----------------|------|--------|
| **Material Dependency** | Tidak bisa start dept tanpa material | Finishing butuh Label → tunggu PO Label |
| **Output Constraint** | Dept B target ≤ Dept A output | Sewing max 518 pcs (dari Cutting 518) |
| **Routing Dependency** | SPK generation based on routing | Route 1 → 6 SPK, Route 2 → 5 SPK |
| **UOM Conversion** | Input/Output must match BOM | Cut 70 YD → expect 480 pcs output |
| **Week Inheritance** | Week dari PO Label (read-only) | Cannot manual edit once inherited |
                    DIRECTOR (View All)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    MANAGER            MANAGER            MANAGER
    Production        Warehouse         Finance/Purchasing
        │                  │                  │
    ┌───┼───┐          ┌───┼───┐          ┌───┼───┐
    │   │   │          │   │   │          │   │   │
  SPV  SPV  SPV      SPV  SPV  SPV       PA  PB  PC
  Cut  Sew  Fin     Main  FG  Finish    Fab Lbl Acc
    │   │   │          │   │   │
   ADM ADM ADM       ADM ADM ADM
  (3) (3) (2)       (2) (1) (2)
```

**Breakdown Departemen**:

| Departemen | Staff | Peran & Tanggung Jawab |
|------------|-------|-----------------------|
| **Purchasing** | 3 specialists | PA: Fabric, PB: Label, PC: Accessories (+ PO vendor embroidery) |
| **Data Entry** | 1 staff | Input hasil vendor embroidery (jika menggunakan vendor) |
| **Cutting** | 3 admins + 1 SPV | Input produksi, material tracking |
| **Embroidery** | INTERNAL atau VENDOR | Jika internal: 2 admins + 1 SPV. Jika vendor: outsourced |
| **Sewing** | 3 admins + 1 SPV | 2 streams (Body + Baju) |
| **Warehouse Finishing** | 2 admins + 1 SPV | 2-stage internal conversion |
| **Packing** | 2 admins + 1 SPV | Assembly + barcode scanning |
| **Warehouse Main** | 2 admins + 1 SPV | Material receiving & issuing |
| **Warehouse FG** | 1 admin + 1 SPV | FG storage & shipping |
| **QC** | 3 inspectors | 4 checkpoints + rework coordination |

**Total Headcount**: ~35 employees (bervariasi tergantung embroidery internal/vendor)

**Catatan**: PPIC tidak ada sebagai departemen terpisah. Production planning handled by Purchasing → Warehouse → Production flow.

### Matriks Kontrol Akses (RBAC)

| Role | Modules Access | Create | Edit | Delete | Approve |
|------|---------------|--------|------|--------|---------|
| **Director** | All | ❌ | ❌ | ❌ | ✅ Level 4 |
| **Manager Production** | MO, SPK, Production | ✅ | ✅ | ❌ | ✅ Level 3 |
| **Manager Warehouse** | Inventory, Transfer | ✅ | ✅ | ❌ | ✅ Level 3 |
| **Manager Purchasing** | PO, Vendor, Material | ✅ | ✅ | ❌ | ✅ Level 3 |
| **Data Entry Staff** | Vendor Embroidery Results | ✅ | ✅ | ❌ | ⏳ Request |
| **SPV Dept** | SPK (own dept only) | ❌ | ✅ | ❌ | ✅ Level 2 |
| **Admin Dept** | Production Input (own) | ✅ | ✅ | ❌ | ⏳ Request |
| **QC Inspector** | QC Records, Rework | ✅ | ✅ | ❌ | ✅ QC only |
| **Purchasing Staff** | PO (own category) | ✅ | ✅ | ❌ | ⏳ Request |

---

<a name="section-5"></a>
## 5️⃣ MODUL INTI & FITUR

### Modul Odoo yang Dibutuhkan (Penilaian Standard)

| Odoo Module | Penggunaan di Quty | Standard Fit | Kebutuhan Customization |
|-------------|---------------|--------------|-------------------|
| **Sales** | Customer order (IKEA PO) | ✅ 80% fit | ⚠️ Field Week/Destination |
| **Purchase** | Vendor PO (3 kategori) | ✅ 90% fit | ⚠️ Klasifikasi PO Type |
| **Inventory** | Material tracking | ⚠️ 60% fit | 🔴 Multi-UOM, WIP tracking |
| **Manufacturing** | MO & SPK generation | ⚠️ 50% fit | 🔴 Dual trigger, Flexible target |
| **Quality** | QC checkpoints | ⚠️ 40% fit | 🔴 Rework module custom |
| **MRP** | Material planning | ⚠️ 60% fit | 🔴 Dual BOM system |
| **Warehouse** | Multi-warehouse | ✅ 70% fit | ⚠️ Warehouse Finishing 2-stage |
| **Barcode** | FG scanning | ✅ 90% fit | ⚠️ Custom Android app |
| **Reporting** | Dashboard & analytics | ⚠️ 50% fit | 🔴 Custom PPIC dashboard |

**Keterangan**:
- ✅ Standard dapat digunakan (minor config)
- ⚠️ Moderate customization dibutuhkan
- 🔴 Heavy customization / custom module required

---

<a name="section-6"></a>
## 6️⃣ FITUR CUSTOM UNIK (USP)

### Fitur Revolutionary (TIDAK ada di Odoo Standard)

#### 1. 🔥 Dual Trigger Production System

**Konsep**: Aktivasi MO 2-fase berdasarkan ketersediaan material

```
TRIGGER 1: PO Kain Received
    ├─ MO Status: PARTIAL ⚠️
    ├─ Allow Dept: Cutting ✅, Embroidery ✅
    ├─ Block Dept: Sewing ❌, Finishing ❌, Packing ❌
    └─ Week/Destination: TBD (empty)

TRIGGER 2: PO Label Received (3-7 days later)
    ├─ MO Status: RELEASED ✅
    ├─ Allow Dept: ALL ✅✅✅✅✅
    ├─ Auto-inherit: Week & Destination from PO Label
    └─ Field Lock: Week/Destination (read-only, no manual edit)
```

**Business Impact**:
- Lead time reduction: **-3 to -5 days** (critical!)
- Fabric utilization: Better (tidak numpuk di warehouse)
- Production flexibility: HIGH
- Human error Week/Dest: **ZERO** (auto-inherit)

**Odoo Gap**: 
- ❌ Odoo MO standard: Binary state (Draft/Confirmed/Done)
- ❌ No partial release per department
- 🔴 **Custom State Machine Required**

**Implementation Complexity**: 🔴 **HIGH**

---

#### 2. 🔥 Flexible Target System per Departemen

**Concept**: SPK Target dapat **BERBEDA** dari MO Target (buffer strategy)

```
MO Target: 450 pcs

SPK Strategy:
├─ Cutting: 495 pcs (450 × 1.10 = +10% buffer)
├─ Sewing: 517 pcs (450 × 1.15 = +15% buffer) ← HIGHEST!
├─ Finishing: 480 pcs (demand-driven, not rigid)
└─ Packing: 465 pcs (exact urgency match)

Constraint Logic:
    SPK Dept B Target ≤ Good Output Dept A
    Example: Sewing max 518 (dari Cutting output 518)
    
Auto Stock Buffer:
    Excess production → Safety stock auto-created
    Example: Cutting 495 actual, MO need 450 → 45 pcs buffer
```

**Format Universal**: `Actual/Target pcs (Percentage%)`
- Example: `520/517 pcs (100.6%)` → exceed target 0.6%

**Business Impact**:
- Zero shortage risk: Defect buffer built-in
- Material optimization: Waste prediction accurate
- Urgency response: Fast (Packing adjust real-time)

**Odoo Gap**:
- ❌ Odoo MO: 1 target applies to all work orders
- ❌ No buffer % configuration per operation
- ❌ No constraint validation between operations
- 🔴 **Complex Logic Custom Required**

**Implementation Complexity**: 🔴 **HIGH**

---

#### 3. 🔥 Warehouse Finishing 2-Stage Internal Conversion

**Concept**: Internal warehouse dengan 2 inventory terpisah tanpa surat jalan

```
WAREHOUSE FINISHING STRUCTURE:

Location 1: SKIN Stock
    ├─ Product: AFTONSPARV_WIP_SKIN
    ├─ Current: 370 pcs
    ├─ Minimum: 400 pcs
    └─ Status: ⚠️ Below Min

Location 2: STUFFED BODY Stock  
    ├─ Product: AFTONSPARV_WIP_BONEKA
    ├─ Current: 285 pcs
    ├─ Minimum: 200 pcs
    └─ Status: ✅ OK

Internal Conversion (Paperless):
    Stage 1: Skin + Filling → Stuffed Body
        ├─ No DN/SJ external
        ├─ System auto-update inventory
        └─ Track filling consumption per batch
    
    Stage 2: Stuffed Body + Hang Tag → Finished Doll
        ├─ No DN/SJ external
        ├─ System auto-update inventory
        └─ QC checkpoint integrated
```

**Business Impact**:
- Kontrol akurat: Per-stage visibility
- Material saving: Filling tracking precise
- Paperless: No manual DN processing
- Demand-driven: Flexible target adjustment

**Odoo Gap**:
- ⚠️ Odoo Manufacturing: 1-stage per Work Center
- ❌ No 2-stage internal conversion di 1 location
- ❌ No separate inventory per stage in same warehouse
- 🔴 **Custom Location & Work Center Logic Required**

**Implementation Complexity**: 🟠 **MEDIUM-HIGH**

---

#### 4. 🔥 UOM Conversion Auto-Validation

**Concept**: Real-time validation untuk prevent inventory chaos

```
CRITICAL POINT 1: CUTTING (YARD → PCS)
─────────────────────────────────────────
Input Material: 70.38 YARD KOHAIR
BOM Reference: 0.1005 YARD/pcs
Target Output: 480 pcs
Expected Consumption: 480 × 0.1005 = 48.24 YD

Tolerance: ±10%
Range: 43.4 - 53.1 YD

System Check:
    70.38 YD in range? NO!
    Variance: +45.7% (too high!)
    
Alert Action:
    ⚠️ WARNING: "Material usage abnormal, please verify"
    Block: NO (allow with approval)
    Log: Record variance for investigation


CRITICAL POINT 2: FG RECEIVING (CTN → PCS)
─────────────────────────────────────────
Input: 8 Cartons
Standard: 60 pcs/CTN
Expected: 8 × 60 = 480 pcs

Physical Count:
├─ CTN 001-007: 60 pcs each (420 pcs)
└─ CTN 008: 45 pcs (partial)

System Check:
    Total: 465 pcs vs Expected 480 pcs
    Variance: -3.1% (acceptable)
    
Alert Action:
    ⚠️ NOTE: "Partial carton detected (CTN-008: 45 pcs)"
    Block: NO (acceptable variance)
    Update: Inventory 465 pcs (not 480)
```

**Validation Rules**:

| Checkpoint | From UOM | To UOM | Tolerance | Action if Exceed |
|------------|----------|--------|-----------|------------------|
| Cutting | YARD | PCS | ±10% | ⚠️ Warning + Log |
| Cutting | YARD | PCS | ±15% | 🔴 Block + Approval |
| FG Receiving | CTN | PCS | ±5% | ⚠️ Warning |
| FG Receiving | CTN | PCS | ±10% | 🔴 Block + Recount |

**Business Impact**:
- Inventory accuracy: 99%+ (vs 82% manual)
- Error prevention: Catch mistakes immediately
- Audit trail: All variance logged

**Odoo Gap**:
- ⚠️ Odoo Multi-UOM: Support conversion BUT no auto-validation
- ❌ No tolerance % configuration
- ❌ No variance alert system
- 🔴 **Custom Validation Logic Required**

**Implementation Complexity**: 🟠 **MEDIUM**

---

#### 5. 🔥 Rework/Repair Module (QC Integration)

**Concept**: Defect tracking dengan recovery workflow

```
DEFECT LIFECYCLE:
═══════════════════════════════════════════════════════════════

1. DEFECT CAPTURE (Auto by QC)
   ├─ Source: QC Checkpoint 1-4
   ├─ Data: Qty, Type, Root Cause, Admin, Machine
   └─ Decision: REWORK atau SCRAP?

2. REWORK QUEUE ASSIGNMENT
   ├─ Priority: HIGH/MEDIUM/LOW (based on MO urgency)
   ├─ Assigned to: Rework Specialist
   ├─ SOP: Step-by-step repair instructions
   └─ Est. Time: Auto-calculate

3. RE-QC INSPECTION
   ├─ Inspector: Same QC who catch defect
   ├─ Result: PASS (add back Good Output) atau FAIL (to Scrap)
   └─ Recovery Rate: Track % success

4. SYSTEM UPDATE (Auto)
   ├─ SPK Good Output: +X pcs (rework success)
   ├─ Scrap Count: +Y pcs (rework fail)
   └─ COPQ Calculation: Cost of Poor Quality

COPQ ANALYSIS DASHBOARD:
─────────────────────────
Total Defects: 127 pcs
├─ Reworked: 98 pcs
├─ Recovery Success: 87 pcs (88.8% ✅)
├─ Recovery Fail: 11 pcs → Scrap
└─ Direct Scrap: 29 pcs

Defect Analysis:
1. Loose thread (45 cases) → Root: Machine tension
2. Stitch misalignment (32 cases) → Root: Admin skill
3. Stuffing uneven (21 cases) → Root: Material quality

Action Plan (Auto-generate):
├─ Retrain admin OP-SEW-023 (12 defects)
├─ Maintenance machine SEW-LINE-02 (15 defects)
└─ Supplier audit for Filling quality
```

**Integration Points**:
- QC Checkpoint → Auto-create Defect Record
- Defect → Reduce SPK Good Output
- Rework Success → Add back SPK Good Output
- Dashboard → Show quality metrics weekly/monthly

**Business Impact**:
- Waste reduction: -60% (significant improvement from tracking)
- Quality improvement: Data-driven root cause analysis
- Continuous improvement: Action plans based on defect patterns

**Odoo Gap**:
- ⚠️ Odoo Quality: Has Quality Alert & Quality Check
- ❌ No Rework Queue management
- ❌ No automatic Good Output adjustment
- ❌ No COPQ analytics dashboard
- 🔴 **Custom Module Required (integrate Quality + Manufacturing)**

**Implementation Complexity**: 🔴 **HIGH**

---

#### 6. 🔥 Real-Time WIP System (Pull System)

**Concept**: Dept berikutnya langsung lihat material available tanpa tunggu SPK selesai

```
TRADITIONAL SYSTEM PROBLEM:
════════════════════════════════════════════════════════════════
Cutting Day 1-5: Total 500 pcs
    ↓ (tunggu SPK Cutting COMPLETE)
Sewing Day 6: Baru bisa start semua 500 pcs
    ↓
Lead Time: LONG (5 days idle for Sewing)


ERP QUTY SOLUTION (Real-Time WIP):
════════════════════════════════════════════════════════════════
Cutting Day 1: 100 pcs selesai → INSTANT transfer to WIP Buffer
    ↓ (0 delay)
Sewing Day 1: Langsung lihat "100 pcs available" → START!
    ↓
Cutting Day 2: 100 pcs selesai → INSTANT transfer
    ↓ (0 delay)
Sewing Day 2: +100 pcs (total 200) → Continue production
    ↓
PARALLEL PRODUCTION → Lead Time -40%!

MAGIC FORMULA:
═══════════════════════════════════════════════════════════════
Admin Dept A Input → Backend Process:
    1. Update SPK Progress (cumulative)
    2. Generate DN Auto (no manual signature)
    3. Update Inventory (WIP Buffer +X pcs)
    4. Broadcast Notification to Dept B Dashboard
    Result: Dept B instant sees "Material Available: +X pcs"
```

**WIP Dashboard** (Real-Time untuk Dept B):

```
┌────────────────────────────────────────┐
│  BAHAN SIAP OLAH - REAL-TIME           │
│  SPK-SEW-BODY-2026-00120               │
├────────────────────────────────────────┤
│  🔔 NEW: +100 pcs Cut Body Available   │
│      (dari Cutting 02-Feb 14:30)      │
│                                        │
│  Total Stock Ready: 500 pcs            │
│  SPK Target: 517 pcs                   │
│                                        │
│  ✅ CAN START PRODUCTION NOW           │
│  [MULAI KERJA]                         │
└────────────────────────────────────────┘
```

**Saldo Minus Handling** (Abnormal Detection):

```
Scenario: Sewing input 200 pcs BUT Cutting belum transfer
Result: WIP Buffer = -200 pcs ⚠️

System Alert:
🚨 SALDO MATERIAL MINUS DETECTED
Dept: Sewing Body
Material: Cut Body AFTONSPARV
Current Saldo: -200 pcs

Possible Causes:
├─ Cutting belum input produksi
├─ Material "melompat" tanpa DN
└─ Admin salah input qty

Action Required:
├─ Verifikasi fisik stock di lantai
├─ Cek dengan Cutting apakah ada DN
└─ Reconcile di akhir shift

[RECONCILE NOW] [REMIND CUTTING]
```

**Business Impact**:
- Production parallelization: +40% faster
- WIP visibility: Real-time (vs daily report)
- Material traceability: 100% (every transfer logged)
- Discrepancy detection: Immediate (vs monthly stocktake)

**Odoo Gap**:
- ⚠️ Odoo Manufacturing: Has transfer between work centers
- ❌ No incremental/partial transfer per day
- ❌ No real-time WIP dashboard per operation
- ❌ No minus stock alert & reconciliation wizard
- 🔴 **Custom WIP Tracking Module Required**

**Implementation Complexity**: 🔴 **HIGH**

---

### Summary USP Features Assessment

| Feature | Business Impact | Odoo Standard Fit | Custom Effort | Priority |
|---------|-----------------|-------------------|---------------|----------|
| 1. Dual Trigger Production | 🔥 CRITICAL | ❌ 0% | 🔴 20 days | P0 |
| 2. Flexible Target System | 🔥 HIGH | ❌ 10% | 🔴 15 days | P0 |
| 3. Warehouse Finishing 2-Stage | 🔥 HIGH | ⚠️ 30% | 🟠 10 days | P1 |
| 4. UOM Auto-Validation | 🔥 MEDIUM | ⚠️ 40% | 🟠 5 days | P1 |
| 5. Rework Module | 🔥 HIGH | ⚠️ 30% | 🔴 12 days | P1 |
| 6. Real-Time WIP | 🔥 HIGH | ❌ 20% | 🔴 18 days | P0 |

**Total Custom Development Estimate**: **80 man-days** (4 months with 1 developer)

---

<a name="section-7"></a>
## 7️⃣ BOM & MANUFACTURING LOGIC

### Dual BOM System

**Concept**: 2 jenis BOM untuk 2 kebutuhan berbeda

```
┌──────────────────────────────────────────────────────────┐
│  ARTIKEL: AFTONSPARV Bear (40551542)                     │
└────────┬────────────────────┬────────────────────────────┘
         │                    │
         ▼                    ▼
┌────────────────────┐  ┌───────────────────────┐
│ BOM PRODUKSI       │  │ BOM PURCHASING        │
│ (Process View)     │  │ (Material View)       │
├────────────────────┤  ├───────────────────────┤
│ Per Departemen:    │  │ Total Material RAW:   │
│                    │  │                       │
│ CUTTING:           │  │ ✓ KOHAIR 0.15 YD      │
│ ├─ Input: KOHAIR   │  │ ✓ BOA 0.0015 YD       │
│ └─ Output: WIP_CUT │  │ ✓ Filling 54 GRAM     │
│                    │  │ ✓ Thread 60 CM        │
│ SEWING:            │  │ ✓ Label 1 PCE         │
│ ├─ Input: WIP_CUT  │  │ ✓ Carton 0.0167 PCE   │
│ ├─ Input: Thread   │  │                       │
│ └─ Output: WIP_SKIN│  │ 6 material (NO WIP!)  │
│                    │  │                       │
│ FINISHING:         │  └───────────────────────┘
│ ├─ Input: WIP_SKIN │            │
│ ├─ Input: Filling  │            ▼
│ └─ Output: WIP_DOLL│    PURCHASING DEPT
│                    │    - Create PO
│ PACKING:           │    - Calculate Needs
│ ├─ Input: WIP_DOLL │    - Supplier Sourcing
│ ├─ Input: Carton   │    (Material list CLEAN)
│ └─ Output: FG      │
│                    │
│ 5,845 BOM lines!   │
└────────────────────┘
         │
         ▼
   PPIC/PRODUKSI
   - Create MO/SPK
   - Alokasi Material
   - Track WIP
   (Routing JELAS!)
```

**BOM Production Details**:

| Level | Department | Input | Process | Output | Material Used |
|-------|------------|-------|---------|--------|---------------|
| 1 | Cutting | Fabric (YARD) | Cut pattern | WIP Cut Body + Cut Baju | 9 jenis fabric |
| 2 | Embroidery | WIP Cut Body | Logo/text | WIP Emb Body | Thread emb 3 warna |
| 3 | Sewing | WIP Emb Body + Cut Baju | Stitch | WIP Skin + Baju | 9 jenis thread, accessories |
| 4 | Finishing-1 | WIP Skin | Stuff | WIP Stuffed Body | Filling 54g, thread closing |
| 5 | Finishing-2 | WIP Stuffed | Final | Finished Doll | Hang tag 1 pcs |
| 6 | Packing | Finished Doll + Baju | Pack | FG (Sets) | Carton, label, sticker |

**Database**: 5,845 BOM lines untuk 478 artikel (average 12 lines per artikel)

### Material Allocation Logic per Department

**Smart Filtering** (Option A - Simple for Odoo):

```python
# Material Category Classification
DEPT_MATERIAL_MAPPING = {
    "CUTTING": ["RAW_FABRIC"],  # KOHAIR, BOA, NYLEX, POLYESTER
    "SEWING": ["RAW_THREAD", "RAW_ACCESSORY"],  # Thread, Button, dll
    "FINISHING": ["RAW_FILLING", "RAW_LABEL"],  # Filling, Hang Tag
    "PACKING": ["RAW_PACKAGING"]  # Carton, Sticker, Label EU
}

# Allocation Flow:
1. PPIC create MO → Select Product (AFTONSPARV)
2. System lookup BOM Production for AFTONSPARV
3. For each department in Routing:
    a. Create SPK (Work Order) for department
    b. Filter materials by DEPT_MATERIAL_MAPPING[dept]
    c. Allocate filtered materials to SPK
    d. Calculate qty = BOM_qty × SPK_target × (1 + buffer%)
4. Generate Material Reservation in Warehouse
```

**Example Calculation**:

```
MO-2026-00089: 450 pcs AFTONSPARV

SPK-CUT-BODY-2026-00120 (Cutting, Buffer +10%):
    Target: 495 pcs (450 × 1.10)
    Material Allocated (filter: RAW_FABRIC):
        ├─ [IKHR504] KOHAIR: 49.75 YD (495 × 0.1005)
        ├─ [IJBR105] JS BOA: 0.75 YD (495 × 0.0015)
        ├─ [INYR002] NYLEX BLACK: 0.50 YD
        ├─ [INYNR701] NYLEX WHITE: 2.18 YD
        ├─ [IPPR351-1] POLYESTER PRINT WHITE: 34.60 YD
        ├─ [IPPR352] POLYESTER PRINT BLUE: 7.03 YD
        ├─ [IPPR353] POLYESTER PRINT WHITE: 19.35 YD
        ├─ [IPR301] POLYESTER WHITE: 61.85 YD
        └─ [IPR302] POLYESTER BLUE: 12.82 YD

SPK-SEW-BODY-2026-00156 (Sewing, Buffer +15%):
    Target: 517 pcs (450 × 1.15)
    Material Allocated (filter: RAW_THREAD):
        ├─ [IKB102] Thread Black: 85 CM per pcs = 43,945 CM
        ├─ [IKB103] Thread White: 60 CM per pcs = 31,020 CM
        └─ ... (9 jenis thread total)

SPK-FIN-STUFFING-2026-00089 (Finishing Stage 1):
    Target: 480 pcs (demand-driven)
    Material Allocated (filter: RAW_FILLING):
        ├─ [IKP20157] Filling: 54 GRAM per pcs = 25,920 GRAM (25.92 KG)
        └─ [IKB105] Thread Closing: 60 CM per pcs = 28,800 CM

SPK-PCK-2026-00045 (Packing):
    Target: 465 pcs (urgency exact)
    Material Allocated (filter: RAW_PACKAGING):
        ├─ [ACB30104] Carton: 0.0167 per pcs = 7.76 ≈ 8 PCE
        ├─ [ALB40011] Hang Tag: 1 per pcs = 465 PCE
        ├─ [ALL40030] Label EU: 1 per pcs = 465 PCE
        ├─ [AUL20220] Sticker ULL: 2 per pcs = 930 PCE
        └─ [ALS40012] Sticker MIA: 1 per pcs = 465 PCE
```

### Odoo Manufacturing Module Gap

| Odoo Feature | Quty Requirement | Gap |
|--------------|------------------|-----|
| **BoM Structure** | Multi-level BoM ✅ | Odoo supports | ✅ OK |
| **BoM Type** | Manufacturing BoM | Odoo has "BoM Type" | ✅ OK |
| **Multi-material** | Variant support | Odoo has "BoM Line Product Variant" | ✅ OK |
| **Routing** | Operations sequence | Odoo has "Routing" | ✅ OK |
| **Work Center** | Department mapping | Odoo has "Work Center" | ✅ OK |
| **Material per Operation** | Allocate material to specific operation | ⚠️ Odoo allocates at MO level | 🟠 **Custom logic needed** |
| **Flexible target per WO** | WO target ≠ MO target | ❌ Odoo forces WO qty = MO qty / operations | 🔴 **Heavy custom** |
| **Dual BoM (Production vs Purchasing)** | 2 BoM views | ❌ Odoo has only 1 BoM | 🟠 **Custom report/view** |

**Customization Strategy for Odoo**:

1. **Use standard Odoo BoM** untuk BOM Production
2. **Add custom field**: `material_category` (RAW_FABRIC, RAW_THREAD, etc.)
3. **Custom allocation logic**: Filter BoM components by category when creating Work Order
4. **Override Work Order**: Allow qty_producing ≠ qty_production (for flexible buffer)
5. **Custom report**: BOM Purchasing view (group by RAW materials only, hide WIP)

**Estimated Effort**: 🟠 **10-12 days**

---

<a name="section-8"></a>
## 8️⃣ INVENTORY & WAREHOUSE MANAGEMENT

### Multi-Warehouse Structure

```
┌─────────────────────────────────────────────────────────────┐
│  WAREHOUSE STRUCTURE - 3 MAIN + 5 DEPARTMENT LOCATIONS      │
└─────────────────────────────────────────────────────────────┘

1. WAREHOUSE MAIN (WH-MAIN)
   ├─ Location: Raw Material Storage
   │  ├─ Fabric Section (YARD)
   │  ├─ Thread Section (CM/METER)
   │  ├─ Filling Section (KG)
   │  ├─ Accessories Section (PCE)
   │  └─ Packaging Section (PCE)
   │
   ├─ Location: WIP Buffer (per Department)
   │  ├─ WIP-CUTTING (Cut Body, Cut Baju)
   │  ├─ WIP-EMBROIDERY (Embroidered Body)
   │  ├─ WIP-SEWING (Skin, Baju Complete)
   │  └─ (Finishing WIP ada di WH-Finishing)
   │
   └─ Inventory Method: FIFO
      Min/Max Reorder: Per SKU
      Valuation: Standard Cost

2. WAREHOUSE FINISHING (WH-FIN) ⭐ UNIQUE!
   ├─ Location: Stage 1 - Stuffing
   │  ├─ Input Stock: Skin (WIP)
   │  ├─ Output Stock: Stuffed Body (WIP)
   │  └─ Material: Filling, Thread Closing
   │
   ├─ Location: Stage 2 - Closing
   │  ├─ Input Stock: Stuffed Body (WIP)
   │  ├─ Output Stock: Finished Doll (SEMI-FG)
   │  └─ Material: Hang Tag
   │
   ├─ Special Rules:
   │  ├─ No external Delivery Note (internal conversion)
   │  ├─ Separate inventory per stage
   │  ├─ Min/Max per WIP product
   │  └─ Alert if Skin < Minimum (auto-notify Sewing)
   │
   └─ Inventory Method: Real-time tracking
      Target-based (not rigid to MO)

3. WAREHOUSE FINISHED GOODS (WH-FG)
   ├─ Purpose: Product jadi siap dikirim - organized per pallet
   ├─ Location: FG Storage (by Week/Destination)
   │  ├─ Week 05 - Belgium Section
   │  ├─ Week 06 - Sweden Section
   │  └─ Week 07 - USA Section
   │
   ├─ Packing Structure: 
   │  ├─ Carton Level: 60 pcs/CTN standard
   │  └─ Pallet Level: Multiple cartons per pallet (shipment-ready unit)
   │  └─ Display format: "8 CTN (465 pcs) / 2 pallets"
   │
   ├─ Label System:
   │  ├─ Barcode per carton
   │  ├─ Week + Destination on label
   │  └─ Scan for receiving verification
   │
   └─ Inventory Method: FEFO (First Expired First Out)
      Aging: Monitor > 30 days (slow-moving alert)

⭐ DEPARTMENT-LEVEL WAREHOUSES (CRITICAL REQUIREMENT!)
───────────────────────────────────────────────────
Setiap departemen produksi punya warehouse/location sendiri:

4. WH-CUTTING (Warehouse Cutting Department)
   ├─ Input: Raw fabric dari WH-MAIN
   ├─ Output: Cut Body + Cut Baju (WIP)
   ├─ Stock Opname: Weekly physical count
   └─ Report: WIP Cutting inventory per SPK

5. WH-EMBROIDERY (Warehouse Embroidery Department)
   ├─ Input: Cut Body dari WH-CUTTING
   ├─ Process: Internal OR Vendor (track outbound/inbound)
   ├─ Output: Embroidered Body (WIP)
   ├─ Stock Opname: Weekly physical count
   └─ Report: WIP Embroidery per SPK (include vendor in-transit)

6. WH-SEWING (Warehouse Sewing Department)
   ├─ Input: Embroidered Body + Cut Baju + Thread
   ├─ Output: Skin + Baju Complete (WIP, tracked separately)
   ├─ Stock Opname: Weekly physical count
   └─ Report: WIP Sewing inventory per SPK (Body vs Baju)

7. WH-PACKING (Warehouse Packing Department)
   ├─ Input: Finished Doll + Baju + Carton + Label
   ├─ Output: Packed FG (Cartons)
   ├─ Stock Opname: Daily physical count (before transfer to WH-FG)
   └─ Report: Ready-to-pack inventory per SPK

**STOCK OPNAME REQUIREMENT**:
├─ Frequency: Weekly per department (Daily untuk Packing)
├─ Method: Physical count vs system record
├─ Tolerance: ±2% acceptable (alert if exceed)
├─ Adjustment: Auto-generate adjustment document if variance
└─ Audit Trail: Log all adjustments (who, when, reason)
```

### Multi-UOM System

**Complexity**: 1 artikel menggunakan **5-6 jenis UOM berbeda**

| Material Type | Primary UOM | Secondary UOM | Conv Factor | Used in Dept |
|---------------|-------------|---------------|-------------|--------------|
| **Fabric** | YARD | METER | 1 YD = 0.9144 M | Cutting |
| **Thread** | CM | METER | 100 CM = 1 M | Sewing, Finishing |
| **Filling** | GRAM | KG | 1000 G = 1 KG | Finishing |
| **Accessories** | PCE | SET | (varies) | Sewing, Packing |
| **Carton** | PCE | BOX | 1 CTN = 1 BOX | Packing |
| **Finished Good** | PCS | CTN | 1 CTN = 60 PCS | FG Warehouse |
| **Pallet** | PCE | - | - | Shipping |

**Critical Conversions** (prone to error):

1. **Cutting: YARD → PCS**
   ```
   Input: 70.38 YARD KOHAIR
   BOM: 0.1005 YARD per pcs
   Expected Output: 70.38 / 0.1005 = 700 pcs
   Actual Output: Check with tolerance ±10%
   ```

2. **Packing: PCS → CTN**
   ```
   Input: 465 PCS Finished Doll
   Standard: 60 PCS per CTN
   Expected: 465 / 60 = 7.75 ≈ 8 CTN
   Reality: 7 full CTN (420 pcs) + 1 partial CTN (45 pcs)
   System: Display as "8 CTN (465 pcs)" with partial note
   ```

3. **Filling: GRAM → KG**
   ```
   BOM: 54 GRAM per pcs
   Production: 480 pcs
   Total: 480 × 54 = 25,920 GRAM = 25.92 KG
   Purchase PO: Round up to 26 KG (practical unit)
   ```

### Inventory Valuation & Costing

**Method**: Standard Costing dengan periodic variance analysis

```
MATERIAL COST STRUCTURE:
═══════════════════════════════════════════════════════════════

Example: [IKHR504] KOHAIR 7MM RECYCLE D.BROWN

Standard Cost: $12.50 per YARD
├─ Purchase Price: $10.80/YD (from supplier)
├─ Freight: $1.20/YD (import cost)
├─ Duties: $0.30/YD (customs)
└─ Overhead: $0.20/YD (warehouse handling)

Variance Tracking:
├─ Price Variance: (Actual PO - Standard) × Qty
├─ Usage Variance: (Actual Usage - BOM) × Standard
└─ Monthly Review: Adjust Standard if sustained variance
```

**Product Cost Buildup** (for AFTONSPARV):

```
Per Unit Cost: $38.50

Material Cost: $25.80 (67%)
├─ Fabric: $18.20 (47%)
├─ Thread: $2.50 (6%)
├─ Filling: 8%
├─ Accessories: 4%
└─ Packaging: 1%

Labor Distribution: 21%
├─ Cutting
├─ Embroidery
├─ Sewing (highest)
├─ Finishing
└─ Packing

Overhead Distribution: 12%
├─ Factory overhead
├─ Utilities: $1.00
└─ Depreciation: $1.00

Selling Price (to IKEA): $52.00
Gross Margin: $13.50 (26%)
```

### Stock Movements & Traceability

**Key Transactions**:

| Transaction Type | Trigger | Source | Destination | Document | Approval |
|------------------|---------|--------|-------------|----------|----------|
| **GR (Good Receipt)** | PO delivered | Vendor | WH-Main | GRN | Auto (with PO) |
| **Material Issue** | SPK start | WH-Main | Production | DN | Auto (with SPK) |
| **WIP Transfer** | Daily prod | Dept A | Dept B | DN Auto | No approval |
| **Internal Conversion** | Finishing | WH-Fin Stage1 | WH-Fin Stage2 | No DN | No approval |
| **FG Receiving** | Packing done | Production | WH-FG | GRN FG | SPV approval |
| **Delivery** | Shipping | WH-FG | Customer | DO | Manager approval |
| **Adjustment** | Stocktake | WH-Main | - | ADJ | Manager approval |
| **Scrap** | QC reject | Production | Scrap Bin | SCRAP | SPV approval |

**Traceability Requirements**:

```
FORWARD TRACING (Material → FG):
═══════════════════════════════════════════════════════════════
Question: "Which FG uses KOHAIR lot KH-2026-0234?"

Answer:
├─ GRN-2026-0456: Received 150 YD lot KH-2026-0234
├─ DN-CUT-2026-0120: Issued 70.4 YD to SPK-CUT-BODY-2026-00120
├─ SPK-CUT-BODY-2026-00120: Produced 495 pcs Cut Body
├─ DN-SEW-2026-0156: Transferred 495 pcs to SPK-SEW-BODY-2026-00156
├─ SPK-SEW-BODY-2026-00156: Produced 518 pcs Skin
├─ ... (continue through Finishing, Packing)
└─ FG: 8 CTN (465 pcs) AFTONSPARV - Batch BATCH-2026-001
    ├─ Week: W05-2026
    ├─ Destination: Belgium
    └─ Ship Date: 10-Feb-2026

BACKWARD TRACING (FG → Material):
═══════════════════════════════════════════════════════════════
Question: "Cust complaint carton CTN-2026-00045-008. 
           Which fabric lot was used?"

Answer:
├─ Barcode Scan: CTN-2026-00045-008 (45 pcs)
├─ Link to: SPK-PCK-2026-00045
├─ Raw input: 
│  ├─ Finished Doll from SPK-FIN-CLOSING-2026-00090
│  └─ Baju from SPK-SEW-BAJU-2026-00157
├─ Trace Finished Doll:
│  ├─ SPK-FIN-STUFFING-2026-00089 (Filling lot: FIL-2026-0123)
│  └─ SPK-SEW-BODY-2026-00156 (Thread lot: THR-2026-0890)
│      └─ SPK-CUT-BODY-2026-00120 (KOHAIR lot: KH-2026-0234 ✅)
└─ Root cause: Fabric defect from lot KH-2026-0234 (supplier: PT AAA)
   Action: Reject lot, claim to supplier
```

### Negative Inventory (Material Debt) System

**Business Case**: 
Production HARUS jalan even if material belum 100% datang (partial receipt)

**Example Scenario**:

```
SCENARIO: PO Filling delay 1 day
════════════════════════════════════════════════════════════════

SPK-FIN-STUFFING-2026-00089 needs: 25.92 KG Filling
Current Stock: 20.50 KG (shortage: 5.42 KG)
PO-2026-0456 status: Datang besok sore 15:00

WITHOUT Material Debt:
├─ Stuffing STOP → Wait 1 day
├─ 480 pcs Skin numpuk di Warehouse Finishing
├─ Sewing cannot send next batch (blocked)
└─ Impact: Delay 1 day for entire MO

WITH Material Debt (ERP Quty):
├─ Stuffing START with 20.50 KG → Complete ~380 pcs (79%)
├─ System record "Material Debt: -5.42 KG"
├─ Sisa 100 pcs (21%) wait di queue
├─ Tomorrow: Material datang → Complete 100 pcs
└─ Impact: ZERO delay to other departments ✅

MATERIAL DEBT REGISTER:
─────────────────────────
SPK: SPK-FIN-2026-00123
Material: [IKP20157] Filling
Debt Qty: -5.42 KG
Reason: "PO-2026-0456 delay 1 hari dari PT Kapas Jaya"
Impact: Can produce 380 pcs (79%), wait 100 pcs (21%)
ETA: 29-Jan-2026 15:00
Status: APPROVED (by Manager)

Approval Required: YES (Manager level)
Audit Trail: Full log (who, when, why, how much)
Auto-clear: When material received (GRN posted)
```

**Governance**:

| Debt Amount | Approval Level | Documentation | Monitoring |
|-------------|----------------|---------------|------------|
| < 5% of need | SPV approval | Reason + ETA | Daily report |
| 5-15% of need | Manager approval | Reason + ETA + Supplier contact | Daily report + Alert |
| > 15% of need | Director approval | Full justification + Risk mitigation | Hourly alert |

**Odoo Gap**:
- ⚠️ Odoo Inventory: Allows negative stock (config option)
- ❌ No "Material Debt" specific workflow
- ❌ No approval chain for negative stock
- ❌ No ETA tracking & auto-clear
- 🟠 **Moderate customization**: Add approval + debt register

**Implementation Complexity**: 🟠 **MEDIUM** (5-7 days)

---

<a name="section-9"></a>
## 9️⃣ QUALITY CONTROL & REWORK MODULE

*(Content sudah dijelaskan di Section 6, point 5 - Rework Module)*

**Summary for Odoo Team**:

- Odoo Quality module provides **foundation**: Quality Alert, Quality Check, Quality Point
- **GAP**: No Rework Queue, No auto-adjustment Good Output, No COPQ dashboard
- **Customization**: Extend Quality module with custom Rework workflow + Manufacturing integration
- **Complexity**: 🔴 **HIGH** (12-15 days development)

---

<a name="section-10"></a>
## 🔧 ARCHITECTURE & TECHNOLOGY STACK

### Current Prototype Stack

**Backend**:
- Language: Python 3.11
- Framework: FastAPI (REST API)
- ORM: SQLAlchemy 2.0
- Database: PostgreSQL 15
- Authentication: JWT Token (OAuth2)

**Frontend**:
- Framework: React 18 + TypeScript
- State Management: Redux Toolkit
- UI Library: Material-UI (MUI) v5
- Calendar: FullCalendar (untuk input harian)
- Charts: Recharts (dashboard analytics)

**Mobile**:
- Platform: Android Native (Kotlin)
- Features: Barcode scanning (ZXing library)
- Sync: REST API dengan offline mode

**Infrastructure**:
- Deployment: Docker + Docker Compose
- Web Server: Nginx (reverse proxy)
- Monitoring: Prometheus + Grafana
- Log: ELK Stack (Elasticsearch, Logstash, Kibana)

### Odoo Migration Consideration

**Odoo Standard Stack**:
- Backend: Python 3.10+ dengan Odoo Framework 17/18
- Database: PostgreSQL 14+
- Frontend: Odoo Web Client (JS framework)
- ORM: Odoo ORM (bukan SQLAlchemy)
- API: XML-RPC / JSON-RPC (standard) + REST API (via module)

**Key Differences**:

| Aspect | Current Prototype | Odoo Standard | Migration Challenge |
|--------|-------------------|---------------|---------------------|
| **ORM** | SQLAlchemy | Odoo ORM | 🔴 HIGH - Rewrite queries |
| **API** | FastAPI REST | XML-RPC + REST module | 🟠 MEDIUM - Adapt endpoints |
| **Frontend** | React + TS | Odoo Web (JS) | 🔴 HIGH - UI redesign |
| **Database** | Direct PostgreSQL | Odoo-managed schema | 🔴 HIGH - Data migration |
| **Authentication** | JWT custom | Odoo Session | 🟠 MEDIUM - Adapt auth |
| **Mobile** | Kotlin native | Odoo Mobile (web-based) | 🟠 MEDIUM - Rewrite or keep separate |

**Migration Strategy Options**:

**Option A: Full Odoo Migration** (Recommended by Odoo standards)
- Pros: Full integration, standard maintenance, long-term support
- Cons: 6-9 months project, high cost, frontend redesign
- Effort: 🔴 **300-400 man-days**

**Option B: Hybrid (Odoo Backend + Custom Frontend)**
- Pros: Keep React UI, leverage Odoo backend
- Cons: Not "pure Odoo", maintenance complexity
- Effort: 🟠 **200-300 man-days**

**Option C: Odoo as Module (minimal integration)**
- Pros: Keep prototype, use Odoo for specific modules
- Cons: Duplicate data, sync complexity
- Effort: 🟡 **100-150 man-days**

---

<a name="section-11"></a>
## 💾 DATABASE SCHEMA OVERVIEW

### Core Tables (28 main tables)

```
MASTER DATA TABLES (7):
═══════════════════════════════════════════════════════════════
├─ products (Finished Good + WIP + Raw Material)
├─ product_categories (RAW, WIP, FG)
├─ units_of_measure (YARD, PCS, KG, CM, CTN, dll)
├─ customers (IKEA, dll)
├─ vendors (Supplier fabric, label, accessories)
├─ warehouses (WH-Main, WH-Finishing, WH-FG)
└─ warehouse_locations (per dept, per section)

BOM TABLES (4):
═══════════════════════════════════════════════════════════════
├─ bom_headers (1 per product)
├─ bom_details (material lines per BOM)
├─ bom_variants (multi-material support)
└─ routings (operation sequence per product)

SALES & PURCHASING (6):
═══════════════════════════════════════════════════════════════
├─ sales_orders
├─ sales_order_lines
├─ purchase_orders
├─ purchase_order_lines (with po_type: KAIN/LABEL/ACC)
├─ purchase_receipts (GRN)
└─ purchase_receipt_items

MANUFACTURING (6):
═══════════════════════════════════════════════════════════════
├─ manufacturing_orders
├─ work_orders (SPK per department)
├─ production_entries (daily input per SPK)
├─ material_allocations (per SPK)
├─ material_debt_registers (negative inventory)
└─ rework_queues (defect management)

INVENTORY (5):
═══════════════════════════════════════════════════════════════
├─ inventory_transactions (all movements)
├─ stock_levels (real-time balance)
├─ wip_buffers (per dept WIP tracking)
├─ finished_goods_inventory
└─ stock_adjustments
```

### Critical Relationships

```sql
-- MO → Multiple SPK (1 to Many)
manufacturing_orders.id → work_orders.mo_id

-- SPK → Daily Production (1 to Many)
work_orders.id → production_entries.work_order_id

-- SPK → Material Allocation (1 to Many)
work_orders.id → material_allocations.work_order_id

-- BOM → Product (Many to 1)
bom_headers.product_id → products.id

-- PO Label → MO Upgrade (1 to 1)
purchase_orders.id (type=LABEL) → manufacturing_orders.po_label_id

-- QC Defect → Rework (1 to 1 or SCRAP)
quality_checks.id → rework_queues.qc_check_id

-- WIP Transfer → Inventory Transaction
production_entries.id → inventory_transactions.source_ref
```

### Data Volume Estimates

| Table | Rows/Month | Rows/Year | Storage | Growth Rate |
|-------|------------|-----------|---------|-------------|
| products | 5 new | 60 | 10 MB | Slow |
| bom_details | 60 | 720 | 50 MB | Slow |
| sales_orders | 120 | 1,440 | 20 MB | Steady |
| purchase_orders | 300 | 3,600 | 80 MB | Steady |
| manufacturing_orders | 150 | 1,800 | 100 MB | Steady |
| work_orders | 900 | 10,800 | 500 MB | Fast |
| production_entries | 5,400 | 64,800 | 2 GB | Fast |
| inventory_transactions | 15,000 | 180,000 | 5 GB | Fast |

**Total Database Size** (projected 1 year): **~8 GB** (with indexes ~12 GB)

---

<a name="section-12"></a>
## 🔗 INTEGRATION REQUIREMENTS

### External Integrations Needed

**1. IKEA EDI Integration** (Future - Phase 2)
- Purpose: Auto-receive Sales Order dari IKEA system
- Protocol: EDI X12 atau EDIFACT
- Frequency: Daily (4x per week)
- Data: Customer PO, Delivery Schedule, Destination, Week

**2. Supplier Portal** (Future - Phase 2)
- Purpose: Supplier self-service untuk PO confirmation & delivery schedule
- Method: Web portal + email notification
- Users: 12 key suppliers

**3. Shipping Label Generation** (Required - Phase 1)
- Purpose: Auto-generate shipping label dengan Week/Destination
- Format: PDF + barcode
- Integration: Printer API (Zebra ZPL language)

**4. Barcode System** (Required - Phase 1)
- Purpose: Generate + Print barcode untuk FG cartons
- Format: Code 128 atau QR Code
- Data: FG ID, Artikel, Week, Destination, Qty

**5. Email/WhatsApp Notification** (Required - Phase 1)
- Purpose: Alert untuk delay, material shortage, approval request
- Method: SMTP (email) + WhatsApp Business API
- Frequency: Real-time + Daily digest

### Odoo Integration Capabilities

Odoo has **strong integration framework**:

✅ **Standard Odoo Features**:
- EDI Framework (module: `edi`)
- Email Integration (built-in)
- Barcode (module: `stock_barcode`)
- Supplier Portal (module: `portal`)
- API (XML-RPC, JSON-RPC, REST via module)

⚠️ **Needs Customization**:
- WhatsApp integration (3rd party module or custom)
- Zebra printer ZPL (custom module)
- IKEA-specific EDI format (custom mapping)

---

<a name="section-13"></a>
## 📱 MOBILE APPLICATIONS

### Android App for FG Barcode Scanning

**Features**:
1. Login dengan credential ERP
2. Scan barcode FG carton
3. Display info: Artikel, Week, Destination, Qty per CTN
4. Verify qty (input jumlah carton)
5. Submit → Auto-create GRN FG di backend
6. Offline mode (sync when online)

**Technology**:
- Current: Kotlin native dengan ZXing library
- Odoo Option 1: Odoo Mobile App (web-based, limited offline)
- Odoo Option 2: Keep current Android app + REST API to Odoo

**Recommendation**: **Keep separate Android app** (better UX, offline capability)

---

<a name="section-14"></a>
## 📊 REPORTING & ANALYTICS

### Critical Reports (Daily)

**1. PPIC Dashboard** (Most Important!)
```
DAILY PRODUCTION OVERVIEW
═══════════════════════════════════════════════════════════════
Date: 13-Feb-2026

ACTIVE MOs: 15
├─ STATUS PARTIAL: 3 (wait PO Label)
├─ STATUS RELEASED: 10 (full production)
└─ STATUS DONE: 2 (completed today)

SPK SUMMARY:
├─ Total SPK: 85
├─ Completed: 32 (38%)
├─ In Progress: 48 (56%)
└─ Delayed: 5 (6%) ⚠️

MATERIAL STATUS:
├─ Critical (< 10%): 3 SKU
├─ Low (10-25%): 12 SKU
└─ OK (> 25%): 215 SKU

PRODUCTION ALERT:
🚨 SPK-FIN-2026-00089: Material Debt -5.42 KG Filling

WEEKLY SHIPMENT STATUS:
├─ Week 06 (due 3 days): 89% complete ✅
├─ Week 07 (due 10 days): 45% complete ⚠️
└─ Week 08 (due 17 days): 12% complete ⏳
```

**2. Material Consumption Report** (Daily)
- Per SPK material usage vs BOM standard
- Variance analysis (over/under consumption)
- Waste tracking per department

**3. Production Efficiency Report** (Weekly)
- Output per day per department
- Yield rate (Good Output / Total Production)
- Defect rate & COPQ
- OEE (Overall Equipment Effectiveness)

**4. Inventory Aging Report** (Weekly)
- Slow-moving material (> 60 days)
- FG aging (> 30 days)
- Dead stock identification

**5. PO Status Report** (Daily)
- PO pending delivery (with ETA)
- PO delay (past ETA)
- Critical PO (blocking production)

### Odoo Reporting Capability

✅ **Strong Points**:
- Built-in reporting engine (QWeb)
- Pivot tables & Graph views (standard)
- Dashboard framework (customizable)
- Export to Excel/PDF (built-in)

⚠️ **Customization Needed**:
- Custom PPIC dashboard (specific layout)
- Real-time WIP dashboard (beyond standard)
- COPQ analytics (custom calculation)

**Effort**: 🟠 **15-20 days** for all custom reports

---

<a name="section-15"></a>
## 🔍 ODOO STANDARD VS REQUIREMENTS GAP ANALYSIS

### Comprehensive Gap Assessment

| Requirement Category | Odoo Standard Capability | Fit % | Gap Level | Custom Effort |
|----------------------|--------------------------|-------|-----------|---------------|
| **Sales Order Management** | Standard Sales module | 85% | 🟢 LOW | 2 days |
| **Purchase Order (3 Types)** | Standard Purchase module | 80% | 🟢 LOW | 3 days |
| **Multi-Warehouse** | Stock multi-location | 75% | 🟡 MEDIUM | 5 days |
| **BOM Management** | Mrp BOM | 70% | 🟡 MEDIUM | 8 days |
| **Manufacturing Order** | Mrp Production | 50% | 🟠 HIGH | 20 days |
| **Work Order (SPK)** | Mrp Workorder | 45% | 🔴 CRITICAL | 25 days |
| **Material Allocation** | Stock reservation | 60% | 🟠 HIGH | 12 days |
| **Quality Control** | Quality module | 55% | 🟠 HIGH | 15 days |
| **Inventory (Multi-UOM)** | Stock UOM | 70% | 🟡 MEDIUM | 7 days |
| **Barcode Scanning** | Stock Barcode module | 80% | 🟢 LOW | 3 days |
| **Reporting & Dashboard** | Report engine + BI | 60% | 🟠 HIGH | 18 days |
| **RBAC (Role-Based Access)** | User groups & ACL | 90% | 🟢 LOW | 2 days |
| **Approval Workflow** | Studio Approval | 70% | 🟡 MEDIUM | 5 days |
| **Mobile App** | Odoo Mobile (web) | 40% | 🔴 CRITICAL | 0 (keep separate) |
| | | | **TOTAL** | **125 days** |

### Critical Gaps Detail

#### 🔴 CRITICAL GAPS (Show-stopper jika tidak ada)

**1. Dual Trigger Production System** (❌ 0% fit)
- Odoo Impact: Manufacturing Order state is binary (confirm/done)
- Workaround: NONE standard
- Solution: Custom state machine + department access control
- Effort: 20 days

**2. Flexible Target per Work Order** (❌ 10% fit)
- Odoo Impact: Work Order qty forced = MO qty / operations
- Workaround: Manual override (but no validation)
- Solution: Override compute method + constraint validation
- Effort: 15 days

**3. Real-Time WIP Buffer System** (❌ 20% fit)
- Odoo Impact: Inventory update only when WO confirm (not daily)
- Workaround: Manual stock move (but no auto)
- Solution: Custom intermediate stock move per production entry
- Effort: 18 days

**4. Rework Module** (❌ 30% fit)
- Odoo Impact: Quality Alert exists BUT no rework queue workflow
- Workaround: Manual quality check + manual MO adjustment
- Solution: Extend Quality module with Rework workflow + auto-adjustment
- Effort: 12 days

**5. Warehouse Finishing 2-Stage** (❌ 30% fit)
- Odoo Impact: Manufacturing can have multi-step BUT not as warehouse location
- Workaround: Create 2 separate Work Centers (but no inventory split)
- Solution: Custom location type + internal conversion logic
- Effort: 10 days

#### 🟠 HIGH GAPS (Workaround exists but painful)

**6. Material Allocation per Work Order** (⚠️ 40% fit)
- Odoo Impact: Material allocated at MO level, shared by all WO
- Workaround: Manual BOM per work center (complex maintenance)
- Solution: Custom allocation logic + filter BOM by operation
- Effort: 12 days

**7. UOM Conversion Validation** (⚠️ 40% fit)
- Odoo Impact: Multi-UOM works BUT no tolerance check
- Workaround: Manual verification (prone to error)
- Solution: Add validator on stock move with tolerance config
- Effort: 5 days

**8. PO Label Week/Destination Inheritance** (⚠️ 50% fit)
- Odoo Impact: MO can link to SO, but not to specific PO field
- Workaround: Manual copy field (error-prone)
- Solution: Auto-populate on PO label receipt + make read-only
- Effort: 3 days

**9. Material Debt (Negative Inventory with Approval)** (⚠️ 60% fit)
- Odoo Impact: Negative stock allowed (config) BUT no approval
- Workaround: Manual approval outside system
- Solution: Add approval chain + debt register view
- Effort: 7 days

**10. Custom PPIC Dashboard** (⚠️ 50% fit)
- Odoo Impact: Dashboard framework exists BUT layout different
- Workaround: Use pivot/graph (not as intuitive)
- Solution: Custom dashboard view with specific widgets
- Effort: 15 days

---

<a name="section-16"></a>
## 🛠️ CUSTOMIZATION STRATEGY

### Approach Options

**Option A: Minimal Custom (Use Odoo Standard Max)**
- Strategy: Adjust business process to fit Odoo standard
- Pros: Fast implementation (3-4 months), low cost, standard support
- Cons: Lose 40% unique features (USP), user adaptation required
- Recommendation: ❌ NOT suitable (too much compromise)

**Option B: Moderate Custom (Recommended)**
- Strategy: Use Odoo standard + custom modules for critical gaps
- Pros: Balance between standard & custom, maintainable, 6-8 months
- Cons: Some features simplified, ongoing custom support
- Recommendation: ✅ **RECOMMENDED**

**Option C: Heavy Custom (Replicate Prototype 100%)**
- Strategy: Custom development for all unique features
- Pros: 100% feature parity, no compromise
- Cons: 9-12 months, high cost, difficult upgrade Odoo version
- Recommendation: ⚠️ Consider only if budget allows

### Module Architecture Plan (Option B)

```
ODOO STANDARD MODULES (Configure):
═══════════════════════════════════════════════════════════════
├─ contacts (Customers, Vendors)
├─ product (Products + UOM)
├─ sale_management (Sales Orders)
├─ purchase (Purchase Orders)
├─ stock (Inventory + Warehouse)
├─ mrp (Manufacturing + BOM + Routing)
├─ quality_control (QC Framework)
└─ web (Dashboard + Reports)

CUSTOM MODULES TO DEVELOP:
═══════════════════════════════════════════════════════════════
Module 1: mrp_dual_trigger (20 days)
├─ Purpose: Implement PARTIAL/RELEASED state
├─ Features:
│  ├─ New MO state field
│  ├─ PO Label link & auto-upgrade logic
│  ├─ Week/Destination auto-inherit
│  └─ Department access control per state
└─ Dependencies: mrp, purchase

Module 2: mrp_flexible_target (15 days)
├─ Purpose: Allow WO target ≠ MO target
├─ Features:
│  ├─ Override qty_producing logic
│  ├─ Buffer % configuration per operation
│  ├─ Constraint validation (WO B ≤ WO A output)
│  └─ Stock buffer auto-creation
└─ Dependencies: mrp

Module 3: mrp_realtime_wip (18 days)
├─ Purpose: Daily production input → instant WIP update
├─ Features:
│  ├─ Production Entry model (daily input)
│  ├─ Auto stock move generation
│  ├─ WIP Buffer dashboard per dept
│  └─ Minus stock alert & reconciliation
└─ Dependencies: mrp, stock

Module 4: quality_rework (12 days)
├─ Purpose: Defect → Rework Queue → Recovery
├─ Features:
│  ├─ Extends quality.alert with rework workflow
│  ├─ Rework queue assignment
│  ├─ Re-QC inspection
│  └─ Auto-adjust WO good output
└─ Dependencies: quality_control, mrp

Module 5: stock_finishing_warehouse (10 days)
├─ Purpose: 2-stage internal conversion
├─ Features:
│  ├─ Custom location type for Finishing
│  ├─ Separate inventory per stage
│  ├─ Paperless internal move
│  └─ Demand-driven target adjustment
└─ Dependencies: stock, mrp

Module 6: stock_uom_validation (5 days)
├─ Purpose: Auto-validate UOM conversion
├─ Features:
│  ├─ Tolerance % config per UOM pair
│  ├─ Variance check on stock move
│  ├─ Alert/Block logic
│  └─ Variance log report
└─ Dependencies: stock

Module 7: stock_material_debt (7 days)
├─ Purpose: Negative stock with approval
├─ Features:
│  ├─ Material Debt Register model
│  ├─ Approval chain (SPV/Manager/Director)
│  ├─ ETA tracking
│  └─ Auto-clear on GRN
└─ Dependencies: stock, approvals

Module 8: mrp_material_allocation (12 days)
├─ Purpose: Allocate material per WO based on operation
├─ Features:
│  ├─ Material category field on product
│  ├─ Filter BOM by dept category mapping
│  ├─ Material reservation per WO
│  └─ Consumption vs BOM report
└─ Dependencies: mrp, stock

Module 9: web_ppic_dashboard (15 days)
├─ Purpose: Custom PPIC real-time dashboard
├─ Features:
│  ├─ MO/SPK status overview
│  ├─ Material critical alert
│  ├─ Production progress per dept
│  └─ Weekly shipment status
└─ Dependencies: web, mrp, stock

Module 10: purchase_po_classification (3 days)
├─ Purpose: PO Type (Kain/Label/Accessories)
├─ Features:
│  ├─ PO Type field + selection
│  ├─ Auto-trigger MO on PO Label
│  └─ PO status dashboard per type
└─ Dependencies: purchase

Module 11: mrp_week_destination (3 days)
├─ Purpose: Week & Destination tracking
├─ Features:
│  ├─ Fields on SO, MO, FG
│  ├─ Auto-inherit from PO Label
│  └─ Report group by Week/Destination
└─ Dependencies: sale, mrp

Module 12: stock_barcode_fg (3 days)
├─ Purpose: FG barcode scanning
├─ Features:
│  ├─ Generate barcode for FG carton
│  ├─ Mobile scan interface (web-based)
│  └─ Auto-create GRN FG
└─ Dependencies: stock_barcode
```

**Total Custom Modules**: 12 modules  
**Total Development**: **123 man-days** (~ 6 months with 1 developer)

---

<a name="section-17"></a>
## 📅 DEVELOPMENT ROADMAP

### Phase-Based Implementation

**PHASE 0: DISCOVERY & DESIGN** (4 weeks)
- Week 1-2: Deep dive workshop with Quty team
- Week 3: Gap analysis validation & Solution design
- Week 4: Architecture finalization & Development plan approval

**PHASE 1: FOUNDATION** (8 weeks)
- Week 1-2: Odoo installation & basic configuration
- Week 3-4: Master data migration (Products, BOM, Customers, Vendors)
- Week 5-6: Sales & Purchase modules setup
- Week 7-8: Inventory & Warehouse configuration

**PHASE 2: MANUFACTURING CORE** (12 weeks)
- Week 9-12: Module 1 (mrp_dual_trigger) - CRITICAL!
- Week 13-15: Module 2 (mrp_flexible_target)
- Week 16-18: Module 8 (mrp_material_allocation)
- Week 19-20: Module 10-11 (PO classification + Week/Destination)

**PHASE 3: WIP & WAREHOUSE** (10 weeks)
- Week 21-24: Module 3 (mrp_realtime_wip)
- Week 25-27: Module 5 (stock_finishing_warehouse)
- Week 28-29: Module 6 (stock_uom_validation)
- Week 30: Module 7 (stock_material_debt)

**PHASE 4: QUALITY & REPORTING** (6 weeks)
- Week 31-33: Module 4 (quality_rework)
- Week 34-36: Module 9 (web_ppic_dashboard)

**PHASE 5: MOBILE & INTEGRATION** (4 weeks)
- Week 37-38: Module 12 (stock_barcode_fg)
- Week 39: Android app REST API integration
- Week 40: Email/notification setup

**PHASE 6: UAT & TRAINING** (4 weeks)
- Week 41-42: User Acceptance Testing (all modules)
- Week 43: Training (PPIC, Dept Admins, SPV)
- Week 44: Bug fixing & refinement

**PHASE 7: GO-LIVE** (2 weeks)
- Week 45: Data migration final (real data)
- Week 46: Go-Live + Hypercare support (1 week)

**TOTAL TIMELINE**: **46 weeks** (~ 11 months)

---

<a name="section-18"></a>
## ⚠️ RISK ASSESSMENT

### Implementation Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Custom module compatibility** dengan future Odoo version | 🟠 HIGH | 🔴 CRITICAL | • Modular design (loose coupling)<br>• Follow Odoo dev best practice<br>• Version compatibility testing |
| **Data migration** error dari prototype | 🟠 MEDIUM | 🔴 CRITICAL | • Incremental migration (test per module)<br>• Validation scripts<br>• Rollback plan |
| **User adoption** resistance (familiar with prototype) | 🟠 HIGH | 🟠 HIGH | • Early user involvement (UAT)<br>• Comprehensive training<br>• Phased rollout (dept-by-dept) |
| **Performance** with 180K transactions/year | 🟡 LOW | 🟠 HIGH | • Database indexing optimization<br>• Query optimization<br>• Load testing (100 concurrent users) |
| **Timeline delay** due to requirement creep | 🟠 HIGH | 🟠 HIGH | • Strict change control process<br>• Prioritization (P0 P1 P2)<br>• Phase-based delivery |
| **Budget overrun** due to heavy customization | 🟠 MEDIUM | 🔴 CRITICAL | • Fixed price per module<br>• Milestone-based payment<br>• Scope freeze after design phase |
| **Vendor lock-in** (Odoo partner dependency) | 🟡 LOW | 🟠 MEDIUM | • Knowledge transfer to internal IT<br>• Documentation (code + functional)<br>• Source code ownership |
| **Integration** failure with IKEA EDI (future) | 🟡 LOW | 🟠 MEDIUM | • Standard EDI framework (not custom)<br>• Test environment from IKEA<br>• Fallback to manual entry |

### Success Criteria

**Technical Success**:
- ✅ All 12 custom modules deployed & functional
- ✅ 99% system uptime (after go-live month 1)
- ✅ Page load time < 2 seconds (dashboard)
- ✅ Mobile barcode scan < 1 second per carton
- ✅ Inventory accuracy > 98%

**Business Success**:
- ✅ Lead time reduction: 25 days → 18 days (target -7 days)
- ✅ On-time delivery: 75% → 95% (target +20%)
- ✅ Manual reporting time: 15h/week → 2h/week (target -87%)
- ✅ Material waste reduction: Significant improvement in inventory accuracy
- ✅ User satisfaction: >80% (post-training survey)

**Adoption Success**:
- ✅ 100% users trained (35 employees)
- ✅ 90% daily active users (after month 2)
- ✅ < 5% manual override (system bypassed)
- ✅ Zero Excel shadow system (eliminate manual tracking)

---

## 🎯 CONCLUSION & NEXT STEPS

### Summary

PT Quty Karunia memiliki **sistem ERP prototype yang sophisticated** dengan **10+ unique features** yang NOT standard di industry lain. Implementasi dengan Odoo **FEASIBLE** namun memerlukan:

1. ✅ **Heavy customization** (12 custom modules, 123 man-days)
2. ✅ **Long timeline** (11 months end-to-end)
3. ✅ **Experienced Odoo partner** (familiar dengan Manufacturing + Python dev)
4. ✅ **Realistic expectations** untuk scope dan effort customization
5. ⚠️ **Risk acceptance** (custom module maintenance, version compatibility)

### Recommended Next Steps

**STEP 1: VALIDATION SESSION** (Week 1)
- Odoo Project Director + Business Analyst visit Quty factory
- Observe actual production process (walking the floor)
- Interview 10+ key users (PPIC, SPV, Admin, Manager)
- Validate requirements accuracy in this document

**STEP 2: PROOF OF CONCEPT** (Week 2-4)
- Build mini-prototype for 3 critical features:
  - Dual Trigger Production System
  - Flexible Target per Work Order
  - Real-Time WIP Dashboard
- Demo to Quty management
- Validate feasibility & user acceptance

**STEP 3: SOLUTION DESIGN FINALIZATION** (Week 5-6)
- Detailed technical design for all 12 modules
- Database schema mapping (prototype → Odoo)
- UI/UX wireframe for custom views
- Integration architecture (mobile app, notification)

**STEP 4: PROPOSAL & CONTRACT** (Week 7-8)
- Fixed price proposal per module
- Timeline commitment with milestones
- SLA for support & maintenance
- Project governance & escalation

**STEP 5: PROJECT KICK-OFF** (Week 9)
- Project team formation (Quty + Odoo partner)
- Development environment setup
- Sprint planning (Agile methodology)
- **START PHASE 1 IMPLEMENTATION**

---

## 📞 CONTACT & OWNERSHIP

**Document Prepared By**:  
IT Director Project - PT Quty Karunia  
Email: it.director@qutykarunia.com  
Date: 13 Februari 2026

**For Odoo Partner**:  
This document is **CONFIDENTIAL** and intended solely for Odoo implementation partner evaluation. Contains proprietary business process and competitive advantages of PT Quty Karunia.

**Document Status**: ✅ **READY FOR ODOO DEEP DIVE**

---

**END OF DOCUMENT**

*Total Pages: ~50*  
*Total Words: ~15,000*  
*Preparation Time: 8 hours deep analysis*  
*Last Updated: 13 Februari 2026*
