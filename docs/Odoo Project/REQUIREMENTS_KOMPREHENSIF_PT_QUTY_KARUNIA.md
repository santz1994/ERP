# 🏭 DOKUMEN REQUIREMENTS KOMPREHENSIF
## PT QUTY KARUNIA - ERP System Requirements

**Disusun Untuk**: Sales Odoo Indonesia (Project Director & Business Analyst)  
**Disusun Oleh**: Daniel Rizaldy (IT Lead - PT Quty Karunia)  
**Tanggal**: 13 Februari 2026  
**Jenis Dokumen**: Business Requirements & Pain Points untuk Gap Analysis Phase  
**Status**: ✅ SIAP UNTUK EVALUASI DAN KONSULTASI  

> 📌 **CATATAN PENTING**: Dokumen ini berisi **REQUIREMENTS SAJA** (bukan gap analysis). Gap analysis adalah tanggung jawab tim Odoo untuk mengevaluasi seberapa besar kesesuaian standard Odoo dengan kebutuhan kami, dan customization apa yang diperlukan.

---

## 📑 DAFTAR ISI

### BAGIAN A: KONTEKS BISNIS
1. [Executive Summary](#section-1)
2. [Profil Perusahaan & Industri](#section-2)
3. [Struktur Organisasi & Roles](#section-3)

### BAGIAN B: SITUASI SAAT INI
4. [11 Pain Points Kritis](#section-4)
5. [Pengalaman ERP Sebelumnya (Gagal)](#section-5)
6. [Mengapa Butuh ERP Sekarang](#section-6)

### BAGIAN C: BUSINESS PROCESS & WORKFLOW
7. [Alur Produksi Lengkap (6 Stages)](#section-7)
8. [Purchasing Workflow (3 Parallel Streams)](#section-8)
9. [Warehouse Structure & Management](#section-9)
10. [Quality Control Process](#section-10)

### BAGIAN D: BUSINESS REQUIREMENTS (CRITICAL!)
11. [7 Business Requirements Unik](#section-11)
    - 11.1 Dual Purchase Order Trigger System ⭐
    - 11.2 Flexible Production Target System
    - 11.3 2-Stage Finishing Internal Process
    - 11.4 Multi-Unit Conversion & Validation
    - 11.5 Real-Time WIP Tracking System
    - 11.6 Quality Control Loop (Rework/Repair)
    - 11.7 Department-Level Warehouse & Stock Opname

### BAGIAN E: FUNCTIONAL REQUIREMENTS
12. [Module Requirements](#section-12)
    - Manufacturing Management
    - Inventory & Warehouse Management
    - Purchasing Management
    - Quality Control
    - Production Planning
    - Reporting & Analytics
    - User Access Control (RBAC)

### BAGIAN F: NON-FUNCTIONAL REQUIREMENTS
13. [System Performance & Scalability](#section-13)
14. [User Experience & Training](#section-14)
15. [Data Migration & Integration](#section-15)

### BAGIAN G: PROJECT SCOPE & SUCCESS CRITERIA
16. [Scope Definition](#section-16)
17. [Critical Success Factors](#section-17)
18. [Expected Deliverables](#section-18)
19. [Next Steps](#section-19)

---

<a name="section-1"></a>
## 📊 1. EXECUTIVE SUMMARY

### 1.1 Konteks Project

PT Quty Karunia adalah **manufacturer soft toys** dengan customer utama **IKEA** (80% revenue contribution). Kami menghadapi **inefficiency operasional serius** akibat sistem manual berbasis Excel dan kertas, serta **trauma dari implementasi ERP sebelumnya yang gagal total**.

Kami membutuhkan **integrated ERP system** yang **disesuaikan** dengan workflow bisnis kami yang spesifik - bukan system generic yang di-force-fit.

### 1.2 Mengapa Odoo?

Kami mempertimbangkan Odoo karena:
- ✅ **Framework modular** yang flexible untuk customization
- ✅ **Open source** dengan community support yang kuat
- ✅ **Manufacturing module** yang bisa dijadikan foundation
- ✅ **Python-based** (development-friendly untuk customization)
- ✅ **Proven track record** di manufacturing industry

### 1.3 Yang Kami TIDAK Butuhkan dari Vendor

❌ **Bukan Gap Analysis lengkap** - ini pekerjaan tim Odoo  
❌ **Bukan detailed technical solution** - ini domain expertise vendor  
❌ **Bukan project timeline exact** - tergantung complexity assessment  

### 1.4 Yang Kami Butuhkan dari Vendor

✅ **Validation**: Apakah requirements kami feasible dengan Odoo?  
✅ **Honest Assessment**: Level customization yang dibutuhkan  
✅ **Experience Sharing**: Case study similar manufacturing complexity  
✅ **Partnership Approach**: Collaborative implementation strategy  

### 1.5 Tujuan Dokumen Ini

Dokumen ini memberikan **complete picture** tentang:
- Siapa kami (company profile, scale, complexity)
- Apa yang salah saat ini (pain points detail)
- Bagaimana proses bisnis kami (workflow end-to-end)
- Apa yang kami butuhkan (business requirements)
- Bagaimana kriteria sukses kami (success factors)

Tim Odoo akan menggunakan dokumen ini untuk:
1. **Assessment Phase**: Evaluate feasibility & complexity
2. **Proposal Phase**: Design solution architecture & estimate effort
3. **Implementation Phase**: Reference untuk development & testing

---

<a name="section-2"></a>
## 🏭 2. PROFIL PERUSAHAAN & INDUSTRI

### 2.1 Informasi Umum

| Aspek | Detail |
|-------|--------|
| **Nama Perusahaan** | PT Quty Karunia |
| **Industri** | Soft Toys Manufacturing (Discrete Manufacturing) |
| **Tahun Berdiri** | 1990 (34+ tahun operational experience) |
| **Customer Utama** | IKEA (80% revenue), Other B2B Export Buyers (20%) |
| **Lokasi Produksi** | Indonesia |
| **Total Karyawan** | ~2200 employees (100 office staff + 2100 production workers) |

### 2.2 Skala Operasional

**Manufacturing Type**: Discrete Manufacturing dengan Complex Assembly

**Volume Produksi**:
- Rata-rata: 1,000,000 - 1,500,000 pieces/bulan
- Peak season: Up to 1,500,000 pieces/bulan
- SKU aktif: 478 artikel (dengan 30+ material per artikel)

**Product Range**:
- Soft toys (boneka, bantal, plushies)
- Export quality (IKEA standard compliance)
- Multi-country destinations (Sweden, Belgium, USA, China, dll)

**Production Flow**:
```
Cutting → Embroidery* → Sewing → Finishing (2-stage) → Packing → Finished Goods
         (internal OR vendor)   (Stuffing + Closing)

*Embroidery: Opsional dan flexible (internal factory ATAU vendor eksternal)
```

**Pola Order**: Weekly delivery schedule
- Format: W01-2026, W02-2026, W03-2026, dst.
- Planning horizon: 4-6 weeks ahead
- Deadline compliance: STRICT (95%+ OTD required)

**Standar Kualitas**:
- IKEA Compliance (mandatory)
- Lab Testing (fabric, filling, safety)
- Metal Detector Scanning (setiap FG)
- Certificate of Compliance (per shipment)

### 2.3 Karakteristik Industri Soft Toys (CRITICAL!)

**⚠️ PENTING**: Soft toys manufacturing memiliki karakteristik **SANGAT SPESIFIK** yang berbeda dari manufacture standar (automotive, electronics, furniture, dll). Ini bukan "just another discrete manufacturing"!

#### 2.3.1 Dual Component Production

**Karakteristik**:
- 1 Finished Good = **2 komponen parallel** (Boneka Body + Baju/Pakaian)
- Kedua komponen diproduksi **terpisah** sejak stage Cutting hingga Sewing
- Assembly hanya terjadi di **Packing stage** (final assembly)

**Impact ke ERP**:
- BOM harus support **parallel streams** (Body stream vs Baju stream)
- Work Orders harus track **2 WIP products** secara terpisah
- Material consumption harus calculate untuk **masing-masing stream**
- Quality control harus inspect **2 products** independently

**Contoh**:
```
Article: AFTONSPARV Bear
├─ Stream A (Body): 
│  └─ Cut Body → Embroider Body → Sew Skin → Stuff → Close → Finished Doll
└─ Stream B (Baju):
   └─ Cut Baju → Sew Baju → Hold (wait for assembly)

Assembly di Packing: Finished Doll + Baju → 1 Set FG
```

#### 2.3.2 Complex Material Mix dengan Multi-UOM

**Karakteristik**:
- Rata-rata 30+ material SKU per 1 artikel finished good
- Material categories: Fabric, Thread, Filling, Labels, Accessories, Carton
- Setiap category punya **UOM berbeda-beda**

**Material Breakdown per Artikel**:

| Material Category | Jumlah SKU | UOM Beli | UOM Simpan | UOM Pakai | Konversi |
|-------------------|------------|----------|------------|-----------|----------|
| **Fabric** | 9-12 jenis | YARD/ROLL | YARD | YARD/METER | 1 YD = 0.9144 M |
| **Thread** | 3-5 jenis | CONE/LUSIN | CONE | CM/METER | 1 Cone ≈ 5000 M |
| **Filling** (Dacron) | 1-2 jenis | BAL/KG | KG | GRAM | 1 KG = 1000 G |
| **Accessories** | 8-10 jenis | GROSS/PCS | PCS | PCS | 1 GROSS = 144 PCS |
| **Label** | 4-6 jenis | PCS/SET | PCS | PCS | 1:1 |
| **Carton** | 1 jenis | PCS | PCS | PCS | 60 pcs/carton |

**Impact ke ERP**:
- Auto-conversion harus **presisi** (inventory accuracy critical!)
- Validation logic: Cegah human error input (misal: 1 boneka pakai 10 Yard kain → ERROR!)
- Yield reporting: System harus calculate "Standard vs Actual"
- Material forecasting: Harus consider conversion loss per stage

**Contoh Conversion Error** (yang sering terjadi manual):
```
❌ SALAH:
   Input: 5 Yard kain
   Output: 50 pcs boneka
   System calculate: 1 Yard = 10 pcs (IMPOSSIBLE!)
   
✅ BENAR:
   Input: 50 Yard kain
   Output: 480 pcs boneka (sesuai BOM marker)
   System calculate: 1 Yard = 9.6 pcs ✅
   Validation: Pass (dalam range toleransi ±10%)
```

#### 2.3.3 2-Stage Finishing Process

**Karakteristik**:
- Warehouse Finishing bukan hanya **storage**, tapi **processing center**
- Ada 2 stage internal: Stuffing (isi kapas) → Closing (pasang hang tag)
- Antara 2 stage **TIDAK ADA surat jalan** (internal conversion)
- Inventory harus track **2 jenis WIP** terpisah: Skin stock vs Stuffed Body stock

**Process Flow Detail**:
```
STAGE 1: STUFFING
────────────────────────────────────────
Location: Warehouse Finishing - Stuffing Area
Input: 
  ├─ Skin (from Sewing): 504 pcs
  ├─ Filling/Dacron: 15,120 gram (30 g/pcs × 504)
  └─ Thread closing: 504 meter

Process: Admin isi kapas + jahit tutup lubang
Time: ~2 menit per pcs
Output: 
  ├─ Stuffed Body: 494 pcs (yield 98%)
  └─ Reject/Scrap: 10 pcs (2%)

Inventory Update (Auto):
  ├─ Skin Stock: -504 pcs
  ├─ Filling Stock: -15,120 gram
  ├─ Thread Stock: -504 meter
  └─ Stuffed Body Stock: +494 pcs


STAGE 2: CLOSING
────────────────────────────────────────
Location: Warehouse Finishing - Closing Area
Input:
  ├─ Stuffed Body: 494 pcs
  └─ Hang Tag: 494 pcs

Process: Admin pasang hang tag + QC final
Time: ~1 menit per pcs
Output:
  ├─ Finished Doll: 489 pcs (yield 99%)
  └─ Reject/Scrap: 5 pcs (1%)

Inventory Update (Auto):
  ├─ Stuffed Body Stock: -494 pcs
  ├─ Hang Tag Stock: -494 pcs
  └─ Finished Doll Stock: +489 pcs

Transfer: Finished Doll → Warehouse Main (dengan DN formal)
```

**Impact ke ERP**:
- System harus support **internal conversion** tanpa surat jalan eksternal
- Inventory tracking harus **real-time** per stage (visibility critical!)
- Material consumption auto-calculated berdasarkan **actual output per stage**
- Yield monitoring per stage untuk **continuous improvement**

#### 2.3.4 Label-Driven Production (CRITICAL!)

**Karakteristik**:
- Label adalah **material paling kritis** meskipun nilai rendah
- Label berisi informasi **Week & Destination** yang determine production planning
- Label punya **lead time paling lama** (7-10 hari vs 3-5 hari untuk fabric)
- Production **TIDAK BOLEH finish** tanpa label (risk: salah negara/bahasa!)

**Label Information**:
```
IKEA Label Standard:
┌────────────────────────────────────────┐
│  AFTONSPARV Bear Soft Toy 40cm         │
│                                        │
│  Week: W05-2026                        │ ← CRITICAL INFO!
│  Destination: Belgium                  │ ← CRITICAL INFO!
│  PO: PO-IKEA-2026-001234              │
│  Article: 40551542                     │
│  Language: French/Dutch                │
│                                        │
│  ⚠️  MADE IN INDONESIA                 │
│  [BARCODE: 123456789012]               │
└────────────────────────────────────────┘
```

**Business Logic**:
- Jika label Week 05 → Harus ship Week 05 (not negotiable!)
- Jika label Belgium → Harus kirim ke Belgium (bukan Sweden!)
- Salah label = **Customer rejection** + **Penalty**

**Impact ke ERP**:
- System harus **auto-inherit** Week & Destination dari PO Label
- Field Week & Destination harus **read-only** (no manual edit!)
- Production stage Sewing-onwards **BLOCKED** sampai PO Label diterima
- Alert system: "PO Label belum datang → Production risk delay!"

#### 2.3.5 Embroidery Optional Routing

**Karakteristik**:
- **Tidak semua** artikel butuh embroidery (tergantung design)
- Embroidery bisa dikerjakan **internal** (jika punya mesin) ATAU **vendor eksternal** (outsourced)
- Routing bersifat **dynamic** per artikel (Route 1, 2, atau 3)

**3 Jenis Routing**:
```
ROUTE 1: FULL (Dengan Embroidery Internal)
────────────────────────────────────────────
Cutting → Embroidery (internal) → Sewing → Finishing → Packing
Timeline: 18-20 hari

ROUTE 2: DIRECT (Tanpa Embroidery)
────────────────────────────────────────────
Cutting → (skip) → Sewing → Finishing → Packing
Timeline: 15-17 hari

ROUTE 3: SUBCON (Embroidery di Vendor)
────────────────────────────────────────────
Cutting → Send to Vendor → Receive from Vendor → Sewing → Finishing → Packing
Timeline: 20-25 hari (longest!)

Notes:
- Send to Vendor: Create Delivery Note (DN) outbound
- Receive from Vendor: Create Goods Receipt (GR) inbound
- Data Entry staff input hasil vendor ke system
```

**Impact ke ERP**:
- BOM harus define **routing type** per artikel (R1/R2/R3)
- Work Order generation harus **conditional** based on routing
- Jika Route 3: System must track **outbound to vendor** dan **inbound from vendor**
- Material consumption: Thread embroidery hanya untuk Route 1 & 3

---

<a name="section-3"></a>
## 👥 3. STRUKTUR ORGANISASI & ROLES

### 3.1 Organization Chart

```
┌───────────────────────────────────────────────────────────────┐
│              PT QUTY KARUNIA - ORGANIZATION                   │
└───────────────────────────────────────────────────────────────┘

                        [DIRECTOR]
                             │
        ┌────────────────────┼────────────────────┬───────────────┐
        │                    │                    │               │
    [FINANCE]            [MANAGER]              [IT]        [ADMIN DATA]
    (2 staff)             (1 person)         (3 person)      (3 staff)
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   [PURCHASING]         [WAREHOUSE]         [PRODUCTION]
   (3 Specialists)       (3 Staff)           (5 Departments)
        │                    │                    │
        │                    │                    ├─ Cutting (SPV + 2 Admin)
        │                    │                    ├─ Embroidery* (SPV + 2 Admin)
        │                    │                    ├─ Sewing (SPV + 2 Admin)
        │                    │                    ├─ Finishing (SPV + 2 Admin)
        │                    │                    └─ Packing (SPV + 2 Admin)
        │                    │
        ├─ Purchasing A      ├─ WH Main          *Embroidery: Internal OR Vendor
        │  (Fabric)          ├─ WH Finishing     Notes:
        ├─ Purchasing B      └─ WH Finished Goods  - Jika internal: team 8-12 workers
        │  (Label)                                  - Jika vendor: outsourced
        └─ Purchasing C                             - Data Entry staff input hasil vendor
           (Accessories)
```

### 3.2 Key Roles & Responsibilities

#### 3.2.1 Management Level

| Role | Jumlah | Tanggung Jawab | ERP Access Needs |
|------|--------|----------------|------------------|
| **Director** | 1 | Strategy, final decision, customer relationship | Dashboard (all KPI), Approval (high-value PO), Financial reports |
| **Manager** | 1 | Operational oversight, performance monitoring, problem escalation | MO monitoring, Production status, Performance analytics, Exception alerts |
| **IT Lead** | 1 | System administration, user management, technical support | Full system access (admin rights), Configuration, User setup |
| **Finance** | 2 | Costing, budget tracking, vendor payment, financial reporting | (Note: Financial module BUKAN priority phase 1) |

#### 3.2.2 Purchasing Department (CRITICAL!)

**⚠️ CATATAN PENTING**: Tidak ada "PPIC Department" di Quty. Planning flow adalah: **Purchasing → Warehouse → Production → Finished Goods**. Purchasing team yang membuat purchasing decision dan trigger production!

| Role | Jumlah | Specialization | Tanggung Jawab | ERP Access Needs |
|------|--------|----------------|----------------|------------------|
| **Purchasing A** | 1 | **Fabric Specialist** | - Create PO Kain/Fabric<br>- **TRIGGER 1**: Early start production (MODE PARTIAL)<br>- Vendor nego fabric<br>- Material forecasting fabric | - Create Purchase Order<br>- Vendor management<br>- Stock monitoring<br>- **Auto-trigger MO creation** |
| **Purchasing B** | 1 | **Label Specialist** | - Create PO Label<br>- **TRIGGER 2**: Full release production (MODE RELEASED)<br>- Input Week & Destination (LOCKED field!)<br>- Vendor nego label/packaging | - Create Purchase Order<br>- **Auto-upgrade MO to RELEASED**<br>- Week & Destination input (one-time, locked!)<br>- Vendor management |
| **Purchasing C** | 1 | **Accessories Specialist** | - Create PO Accessories (Thread, Filling, Carton, dll)<br>- Vendor nego accessories<br>- Stock monitoring accessories | - Create Purchase Order<br>- Vendor management<br>- Stock monitoring |

**Workflow Utama**:
```
Step 1: Customer Order (IKEA) → Email/Portal
Step 2: Purchasing A → Create PO Kain (TRIGGER 1!)
        System: Auto-create MO (MODE: PARTIAL)
        Status: Cutting & Embroidery departments UNLOCKED
        
Step 3: Purchasing B → Create PO Label (TRIGGER 2!)
        System: Auto-upgrade MO to RELEASED
        System: Auto-inherit Week & Destination (READ-ONLY!)
        Status: ALL departments UNLOCKED
        
Step 4: Purchasing C → Create PO Accessories
        System: Validate stock availability (no MO trigger)
```

#### 3.2.3 Warehouse Department

**⚠️ CATATAN**: Setiap warehouse area memiliki **2 admin** untuk handle transactions dan stock management.

| Role | Jumlah | Tanggung Jawab | ERP Access Needs |
|------|--------|----------------|------------------|
| **Warehouse Admin** | 6 total<br>(2 per area:<br>WH Main,<br>WH Finishing,<br>WH FG) | - Receive goods from supplier (PO)<br>- Internal transfer (WIP between dept)<br>- Issue materials to production<br>- Stock adjustment<br>- Physical count (stock opname) | - Goods Receipt Note (GRN)<br>- Internal Transfer<br>- Material Issue<br>- Stock Adjustment<br>- Barcode scanning |

**3 Warehouse Types dengan Admin Assignment**:
```
1. WAREHOUSE MAIN
   ├─ Function: Raw materials & WIP staging
   ├─ Stock: Fabric, Thread, Filling, Accessories, Carton
   ├─ Activities: Receive from supplier, Issue to production
   └─ Admin: 2 persons (shift-based for continuous operation)

2. WAREHOUSE FINISHING (SPECIAL!)
   ├─ Function: 2-stage internal processing
   ├─ Stage 1: Stuffing (Skin → Stuffed Body)
   ├─ Stage 2: Closing (Stuffed Body → Finished Doll)
   ├─ Stock: 2 jenis WIP (Skin + Stuffed Body)
   ├─ Activities: Internal conversion (no formal DN)
   └─ Admin: 2 persons (handle both Stuffing & Closing input)

3. WAREHOUSE FINISHED GOODS (FG) - Organized per pallet
   ├─ Function: Ready-to-ship product storage
   ├─ Organization: Per pallet (multiple cartons per pallet)
   ├─ Stock: Finished Goods (by Week & Destination)
   ├─ Activities: Receive from Packing, Prepare shipment, Loading
   └─ Admin: 2 persons (high-value inventory, need redundancy)
```

#### 3.2.4 Production Departments (5 Departments)

**⚠️ IMPORTANT**: System access **HANYA untuk Admin level**, TIDAK untuk Worker/Operator produksi! Workers melakukan pekerjaan fisik, Admin yang input data ke system.

| Department | Role | Jumlah | Tanggung Jawab | ERP Access Needs |
|------------|------|--------|----------------|------------------|
| **Cutting** | SPV | 1 | Supervise cutting team, approve daily output | View Work Orders (dept only), Approve output |
| | Admin | 2 | Daily production input, material request, shift coordination | Input production (actual qty, good/reject), Request materials |
| **Embroidery** | SPV | 1 | Supervise embroidery (jika internal), manage vendor (jika outsource) | View Work Orders, Approve output/vendor results |
| | Admin | 2 | Input embroidery results (internal OR vendor) | Input production, Create DN (to vendor), Receive GR (from vendor) |
| **Sewing** | SPV | 1 | Supervise sewing team 2 streams (Body + Baju) | View Work Orders (2 parallel), Approve output |
| | Admin | 2 | Daily input 2 streams separately | Input production (Body stream + Baju stream), Material consumption |
| **Finishing** | SPV | 1 | Supervise 2-stage finishing (Stuffing + Closing) | View Work Orders (2 stages), Approve conversion |
| | Admin | 2 | Input per stage (Stuffing + Closing) | Input production per stage, Internal conversion |
| **Packing** | SPV | 1 | Supervise packing team, final assembly | View Work Orders, Approve FG transfer |
| | Admin | 2 | Daily packing input, FG barcode generation | Input packing (assembly Body+Baju), Generate barcode FG, Transfer to WH FG |

**Department-Level Warehouses** (IMPORTANT!):
```
Selain 3 main warehouses, SETIAP departemen punya warehouse/location sendiri:

├─ WH-CUTTING
│  ├─ Purpose: Store WIP cut pieces (Cut Body + Cut Baju)
│  ├─ Stock Opname: Weekly
│  └─ Report: WIP Cutting per SPK

├─ WH-EMBROIDERY
│  ├─ Purpose: Store WIP embroidery (include in-transit vendor)
│  ├─ Stock Opname: Weekly
│  └─ Report: WIP Embroidery + Vendor Transit

├─ WH-SEWING
│  ├─ Purpose: Store WIP sewing (Skin + Baju separate)
│  ├─ Stock Opname: Weekly
│  └─ Report: Skin stock vs Baju stock

├─ WH-FINISHING (Already explained - 2 stages)
│  ├─ Stock Opname: Weekly
│  └─ Report: Skin stock, Stuffed Body stock

└─ WH-PACKING
   ├─ Purpose: Store ready-to-pack inventory
   ├─ Stock Opname: DAILY (high value!)
   └─ Report: Pending assembly items
```

#### 3.2.5 Quality Control

| Role | Jumlah | Tanggung Jawab | ERP Access Needs |
|------|--------|----------------|------------------|
| **QC Inspector** | 2 | - Inspection di 4 checkpoints<br>- Defect categorization<br>- Rework approval/rejection<br>- Final inspection before FG | - Quality inspection interface<br>- Defect recording<br>- Rework queue management<br>- Approval workflow |

**4 QC Checkpoints**:
```
1. CHECKPOINT CUTTING
   ├─ Check: Size accuracy, pattern alignment
   └─ Pass rate target: >95%

2. CHECKPOINT SEWING ← HIGHEST DEFECT RATE!
   ├─ Check: Stitch quality, symmetry, assembly
   ├─ Pass rate target: >85% (hardest stage!)
   └─ Rework queue: Most active here

3. CHECKPOINT FINISHING
   ├─ Check: Stuffing uniformity, tag placement, appearance
   └─ Pass rate target: >98%

4. CHECKPOINT PACKING (FINAL!)
   ├─ Check: Metal detector, safety compliance, completeness
   ├─ Pass rate target: >99%
   └─ Certificate of Compliance issued
```

#### 3.2.6 Data Entry / Admin Support

| Role | Jumlah | Tanggung Jawab | ERP Access Needs |
|------|--------|----------------|------------------|
| **Admin Data Entry** | 3 | - Input data produksi (jika dept admin tidak available)<br>- Input hasil vendor embroidery<br>- Master data maintenance<br>- Report generation<br>- Data verification | - Manufacturing input<br>- Master data edit<br>- Report access<br>- Data validation tools |

### 3.3 Total User Count & Concurrent Access

**📊 SYSTEM ACCESS SUMMARY**:

| Level | Jumlah Users | Pattern Akses | Concurrent Peak | Notes |
|-------|--------------|---------------|-----------------|-------|
| Management | 4 | Sporadic (dashboard only) | 2-3 | Director, Manager, IT Lead, Finance Head |
| Purchasing | 3 | Daily intensive | 3 | Specialist A/B/C |
| **Warehouse Admin** | **6** | Daily intensive | 4-5 | **2 per area** (Main/Finishing/FG) |
| Production SPV | 5 | Daily moderate | 3-4 | 1 per dept (Cutting/Embroidery/Sewing/Finishing/Packing) |
| **Production Admin** | **10** | Daily intensive | 8-9 | **2 per dept** (handle production input) |
| QC Inspector | 2 | Daily moderate | 1-2 | Quality control team |
| Admin Data Entry | 3 | Daily intensive | 2-3 | Support staff for data input |
| **TOTAL USERS** | **33 users** | | **~25-28 concurrent** | |


  - **Admin yang input** hasil produksi ke system
  - **Warehouse Admin yang input** transactions

**Scaling Plan**:
- Business growth +50% → Tambah: +3-5 Production Admin, +2 Warehouse Admin
- Total estimated: ~40 users untuk 2x current volume

---

<a name="section-4"></a>
## ❌ 4. 11 PAIN POINTS KRITIS

### 4.1 Overview Pain Points

Berikut adalah **11 masalah operasional kritis** yang kami alami dengan sistem manual saat ini. Pain points ini **HARUS diselesaikan** oleh sistem ERP baru:

| No | Pain Point | Business Impact | Frekuensi | Severity |
|----|------------|-----------------|-----------|----------|
| 1 | Data produksi manual (Excel/Kertas) | Laporan lambat 3-5 hari | Harian | 🔴 CRITICAL |
| 2 | Material tidak terdata real-time | Produksi STOP tiba-tiba karena habis stok | Mingguan | 🔴 CRITICAL |
| 3 | Work order tracking manual | Late delivery → penalty dari IKEA | Mingguan | 🔴 CRITICAL |
| 4 | Finished goods verification sulit | Customer complaints, salah hitung | Per shipment | 🟠 HIGH |
| 5 | No clear approval process | Fraud risk, no audit trail | Per transaksi | 🟠 HIGH |
| 6 | Monthly closing lambat | Management decision delayed | Bulanan | 🟡 MEDIUM |
| 7 | Warehouse Finishing chaos | Stok Skin vs Stuffed tidak jelas, material waste | Harian | 🔴 CRITICAL |
| 8 | Unit conversion errors | Inventory kacau (Yard→Pcs, Box→Pcs) | Per transaksi | 🔴 CRITICAL |
| 9 | Production target rigid | Shortage karena defect tidak diprediksi | Mingguan | 🔴 CRITICAL |
| 10 | Defect tidak tertrack | Waste tinggi, no root cause analysis | Harian | 🟠 HIGH |
| 11 | Previous ERP implementation FAILURE | Admin trauma, Management skeptis tentang ERP | One-time | 🔴 CRITICAL |

### 4.2 Detail Pain Points

#### 4.2.1 Pain Point #1: Data Produksi Manual

**Kondisi Saat Ini**:
- Admin produksi catat hasil produksi di **kertas** (form manual)
- End of shift → Form diserahkan ke **Admin Data Entry**
- Admin Data Entry → Input manual ke **Excel** (double entry!)
- End of day → Compile Excel → Email ke Manager

**Masalah**:
- ⚠️ **Re-entry data 2-3 kali** (kertas → Excel → Email)
- ⚠️ Laporan **delay 3-5 hari** (compile manual takes time!)
- ⚠️ **Typo & calculation error** (manual input prone to mistakes)
- ⚠️ **Lost paperwork** (form hilang, data loss permanent)

**Impact Bisnis**:
- Manager tidak bisa **action cepat** jika ada problem produksi
- IKEA minta daily report → kami **tidak bisa provide**
- Decision making **terlambat** (sudah terlanjur delay baru ketahuan!)

**Yang Dibutuhkan dari ERP**:
- ✅ Admin input langsung ke system (no paper form!)
- ✅ Real-time data available (no waiting compile!)
- ✅ Auto-calculation (no manual sum!)
- ✅ Auto-validation (detect typo/error immediately!)

#### 4.2.2 Pain Point #2: Material Tidak Terdata Real-Time

**Kondisi Saat Ini**:
- Stock material dicatat manual di **buku gudang** (logbook)
- Material keluar produksi → **Tidak tercatat detail** (cuma tulis "keluar untuk SPK-XX")
- Stock check → Harus **fisik cek gudang** (no system visibility!)

**Masalah**:
- ⚠️ **Tiba-tiba material habis** → Production stop → Panic buying!
- ⚠️ **Tidak tahu kapan re-order** (no min/max alert)
- ⚠️ **Material tersembunyi** (ada di dept A, dept B butuh, tapi tidak tahu!)
- ⚠️ **Forecast inaccurate** (tidak ada data historical consumption)

**Impact Bisnis**:
- Production delay karena **waiting material**
- Purchasing mendadak → Harga **lebih mahal** (no nego time!)
- Material **double order** (A order, B juga order, padahal warehouse ada!)

**Yang Dibutuhkan dari ERP**:
- ✅ Real-time stock visibility (semua dept bisa lihat!)
- ✅ Auto-deduction saat material issued (paperless!)
- ✅ Min/Max alert (auto notify purchasing!)
- ✅ Historical consumption data (untuk forecast!)

#### 4.2.3 Pain Point #3: Work Order Tracking Manual

**Kondisi Saat Ini**:
- SPK dibuat **manual** oleh Admin Data Entry (paper form!)
- SPK progress **tidak tertrack** sistem (Admin produksi lapor verbal/WA)
- Status SPK → Harus **tanya satu-satu** ke setiap departemen

**Masalah**:
- ⚠️ **Delay baru ketahuan saat deadline!** (sudah terlambat untuk action!)
- ⚠️ **Koordinasi nightmare** (Manager WA group ke 5 dept, tunggu reply!)
- ⚠️ **SPK duplicate/lost** (paper form sering hilang atau tertukar!)
- ⚠️ **Priority tidak jelas** (dept tidak tahu mana SPK urgent!)

**Impact Bisnis**:
- IKEA **penalty untuk late delivery**
- Customer relationship **damaged** (trust berkurang!)
- Overtime production **unplanned** (panic mode!)

**Yang Dibutuhkan dari ERP**:
- ✅ Dashboard real-time SPK status (all dept visible!)
- ✅ Alert system (SPK delay auto-notify!)
- ✅ Priority indicator (urgent SPK highlighted!)
- ✅ Progress tracking automatic (dept input → auto-update dashboard!)

#### 4.2.4 Pain Point #4: Finished Goods Verification Sulit

**Kondisi Saat Ini**:
- Packing dept hitung FG **manual** (dengan tally counter)
- Hitung per carton → Tulis di form → Sum manual
- Cross-check dengan customer order → **Manual compare**

**Masalah**:
- ⚠️ **Salah hitung jumlah carton** (misal: 465 pcs = brp carton? Calculate manual error!)
- ⚠️ **Conversion factor lupa** (lupa 60 pcs/carton → salah total!)
- ⚠️ **Customer complaint** (terima barang kurang/lebih → dispute!)

**Impact Bisnis**:
- Customer **reject shipment** (under/over quantity!)
- **Re-packing emergency** (bongkar carton, hitung ulang!)
- **Trust issue** dengan IKEA (quality control dipertanyakan!)

**Yang Dibutuhkan dari ERP**:
- ✅ Barcode system (scan carton → auto-count!)
- ✅ Auto-conversion (pcs → carton automatic!)
- ✅ Validation before shipment (system block jika qty salah!)
- ✅ Packing list auto-generate (no manual calculate!)

#### 4.2.5 Pain Point #5: No Clear Approval Process

**Kondisi Saat Ini**:
- Approval dilakukan **verbal** atau **WhatsApp**
- Tidak ada **audit trail** (siapa approve apa kapan?)
- Jika ada masalah → **Tidak bisa trace** tanggung jawab!

**Masalah**:
- ⚠️ **Fraud potential** (tidak ada control, easy manipulation!)
- ⚠️ **Accountability hilang** (tidak jelas siapa yang responsible!)
- ⚠️ **Dispute resolution sulit** (no evidence of approval!)

**Impact Bisnis**:
- **Internal audit findings** (weak control!)
- **Vendor dispute** (claim "sudah diapprove" tapi no proof!)
- **Management blind** (tidak tahu who approved what!)

**Yang Dibutuhkan dari ERP**:
- ✅ Digital approval workflow (click Approve button!)
- ✅ Audit trail complete (timestamp, user, remarks!)
- ✅ Multi-level approval if needed (SPV → Manager → Director!)
- ✅ Email notification (pending approval alert!)

#### 4.2.6 Pain Point #6: Monthly Closing Lambat

**Kondisi Saat Ini**:
- Finance team **compile manual** dari Excel various sources
- Production report + Warehouse report + Purchasing report → **Merge manual!**
- Butuh waktu **5-7 hari** untuk monthly closing

**Masalah**:
- ⚠️ Report ke Management **selalu late** (sudah bulan depan baru dapat closing bulan lalu!)
- ⚠️ Decision making **tertunda** (data sudah expired!)
- ⚠️ Tidak bisa **quick action** jika ada issue!

**Impact Bisnis**:
- Management **blind** pada performa real-time
- Strategic planning **based on old data** (not relevant!)

**Yang Dibutuhkan dari ERP**:
- ✅ Auto-generate report (1-click monthly closing!)
- ✅ Real-time dashboard (not wait until month-end!)
- ✅ Integrated data (no manual merge!)

#### 4.2.7 Pain Point #7: Warehouse Finishing Chaos

**Kondisi Saat Ini**:
- Warehouse Finishing punya 2 proses: Stuffing + Closing
- Stock dicatat **manual** di 1 buku saja (campur Skin + Stuffed Body!)
- **Tidak jelas** berapa Skin stock vs Stuffed Body stock

**Masalah**:
- ⚠️ **Inventory inaccurate!** (fisik ada, tapi di buku salah catat!)
- ⚠️ Tidak tahu **bottleneck di stage mana** (Stuffing lama or Closing lama?)
- ⚠️ Material consumption **tidak presisi** (berapa kapas terpakai per pcs? Unknown!)
- ⚠️ **Material waste tinggi** (no tracking per stage!)

**Impact Bisnis**:
- **Production delay** (tunggu Stuffing/Closing, tidak tahu progress!)
- **Material over-ordering** (karena tidak tahu actual consumption!)
- **Quality issue** (kapas kurang/lebih, tapi tidak terdetect!)

**Yang Dibutuhkan dari ERP**:
- ✅ Separate tracking 2 stages (Skin stock vs Stuffed Body stock!)
- ✅ Material consumption per stage (kapas consumed per 100 pcs!)
- ✅ Progress visibility (berapa di queue Stuffing? Berapa di queue Closing?)
- ✅ Internal conversion automatic (no manual surat jalan!)

#### 4.2.8 Pain Point #8: Unit Conversion Errors

**Kondisi Saat Ini**:
- Conversion dilakukan **manual** dengan calculator/Excel
- Yang sering error:
  - **Cutting**: Input Yard → Output Pcs (berapa pcs dapat dari 10 Yard? Manual hitung!)
  - **Packing**: Input Pcs → Output Carton (465 pcs = brp carton? Manual divide 60!)

**Masalah**:
- ⚠️ **Calculation error frequent!** (typo 465 jadi 456, dst)
- ⚠️ **Conversion factor lupa** (berbeda per artikel, easy salah!)
- ⚠️ **Inventory chaos** (system catat 500 pcs, fisik 480 pcs → discrepancy!)

**Impact Bisnis**:
- Inventory accuracy **drop drastis** (actual vs system tidak match!)
- **Stock opname nightmare** (adjustment besar setiap bulan!)
- **Production planning jadi salah** (based on wrong stock data!)

**Yang Dibutuhkan dari ERP**:
- ✅ Auto-conversion built-in (YARD → PCS automatic based on BOM!)
- ✅ Validation logic (jika hasil conversion tidak masuk akal → ALERT!)
- ✅ Tolerance checking (±10% OK, >10% WARNING, >15% BLOCK!)
- ✅ Preset conversion per artikel (no manual input conversion factor!)

#### 4.2.9 Pain Point #9: Production Target Rigid

**Kondisi Saat Ini**:
- MO target = 450 pcs → **Semua departemen harus produce exact 450 pcs!**
- Jika Sewing defect 15% → Output = 382 pcs (kurang 68 pcs!)
- Result: **SHORTAGE!** Customer order 450 pcs, cuma dapat 382 pcs!

**Masalah**:
- ⚠️ **Shortage sangat sering!** (hampir setiap batch ada yang kurang!)
- ⚠️ **Emergency re-run production** (rush order untuk fulfill deficit!)
- ⚠️ **Customer penalty** (late/under-quantity delivery!)

**Impact Bisnis**:
- **Delivery delay** (tunggu re-run production!)
- **Extra overtime cost** (unplanned emergency production!)
- **Customer satisfaction turun** (unreliable supplier!)

**Yang Dibutuhkan dari ERP**:
- ✅ **Flexible target per department** (Cutting 495 pcs, Sewing 517 pcs, Packing 450 pcs!)
- ✅ **Buffer management intelligent** (system calculate optimal buffer based on historical defect rate!)
- ✅ **Constraint logic** (dept B target tidak boleh > dept A output!)
- ✅ **Real-time adjustment** (jika defect tinggi → auto-adjust next dept target!)

#### 4.2.10 Pain Point #10: Defect Tidak Tertrack

**Kondisi Saat Ini**:
- QC inspection dilakukan, tapi hasil **tidak dicatat sistematis**
- Defect ditulis di form kertas → **Discard setelah selesai** (no data retention!)
- **Tidak tahu** defect tertinggi dari mana (dept? admin? material?)

**Masalah**:
- ⚠️ **Root cause unknown!** (defect repeat terus, tidak tahu penyebab!)
- ⚠️ **Waste cost tinggi** (banyak scrap karena defect, no improvement plan!)
- ⚠️ **Rework tidak termonitor** (berapa yang bisa diperbaiki? Unknown!)
- ⚠️ **Quality continuous improvement TIDAK JALAN** (no data for Kaizen!)

**Impact Bisnis**:
- **Defect rate stagnan** (tidak turun karena tidak ada action plan!)
- **Material waste terus tinggi**
- **IKEA quality audit** (potential issue!)

**Yang Dibutuhkan dari ERP**:
- ✅ Defect recording per checkpoint (QC1/QC2/QC3/QC4!)
- ✅ Defect categorization (stitch defect, material defect, assembly defect, dll!)
- ✅ Rework queue management (track berapa yang dirework, berapa yang recovery!)
- ✅ Root cause analysis report (by dept, by admin, by material, by machine!)

---

<a name="section-5"></a>
## 💔 5. PENGALAMAN ERP SEBELUMNYA (GAGAL)

### 5.1 Background Kegagalan

**Timeline**: 2 tahun lalu (2024)  
**Vendor**: [Nama vendor dirahasiakan]  
**Investment**: Significant (sistem dibeli, training sudah, dll)  
**Status**: **GAGAL TOTAL** - System tidak jalan sama sekali!  
**Impact**: Admin **TRAUMA**, Management **SKEPTIS** tentang ERP implementation

### 5.2 Root Cause Kegagalan (Deep Analysis)

#### 5.2.1 Vendor Tidak Memahami Complexity

**Masalah**:
- Vendor **assume** soft toys manufacturing = "simple manufacturing"
- Tidak memahami **2-component production** (Body + Baju parallel streams)
- Tidak memahami **Warehouse Finishing 2-stage**
- Tidak memahami **Dual Trigger System** (Fabric PO vs Label PO)

**Impact**:
- System di-setup **salah** (1 stream only, padahal butuh 2 parallel!)
- Production workflow **tidak match** dengan real process
- Admin **bingung** kenapa UI tidak sesuai dengan cara kerja mereka

#### 5.2.2 Force-Fit Standard System

**Masalah**:
- Vendor bilang: "Quty harus **ikut standard system**, jangan custom!"
- Reality: Quty workflow **memang unik**, tidak bisa dipaksakan standard!
- Vendor **refuse customization** atau charge **terlalu mahal**

**Impact**:
- Admin **dipaksa ubah cara kerja** untuk sesuai system → **REJECT!**
- Management frustrasi: "Kami beli ERP untuk help kami, bukan kami yang adjust!"

#### 5.2.3 Training Tidak Adequate

**Masalah**:
- Training cuma **2 hari** (too short untuk complex system!)
- Training **generic** (tidak specific untuk Quty workflow!)
- Tidak ada **hands-on practice**
- Tidak ada **user manual** dalam Bahasa Indonesia

**Impact**:
- Admin **tidak paham** cara pakai system
- Banyak salah input → Data **CHAOS** dalam 1 minggu!
- Admin **give up** → Balik ke Excel lagi!

#### 5.2.4 No Post-Implementation Support

**Masalah**:
- Setelah GoLive, vendor **menghilang**!
- Jika ada problem → **Tidak direspon cepat** (reply 3-5 hari!)
- Tidak ada **onsite support**
- Change request → **Ditolak** atau charge extra expensive!

**Impact**:
- System **bug tidak fixed**
- Admin **frustrasi** pakai system yang error terus
- Management **decision**: Stop pakai system, rugi investment!

### 5.3 Lessons Learned

**Yang HARUS BERBEDA di Implementation Berikutnya**:

#### 5.3.1 Vendor Must Understand Our Business

✅ **Pre-sales workshop WAJIB!** (1-2 hari site visit, observe real process!)  
✅ Vendor must **deep dive** ke complexity kami (bukan cuma baca document!)  
✅ Vendor must **challenge** assumptions (banyak tanya "why", "how", "what if")  
✅ Vendor must provide **reference case** similar manufacturing complexity

#### 5.3.2 Customization is Must-Have (Not Optional!)

✅ Quty workflow **memang unik** → Accept that customization needed!  
✅ Budget for customization **clear from start** (no hidden cost!)  
✅ Customization scope **agreed upfront** (written in contract!)  
✅ Phased delivery OK (deliver critical features first, polish later!)

#### 5.3.3 Training Must Be Comprehensive

✅ Training **minimum 5 hari** (1 day theory + 4 days hands-on!)  
✅ Training **per role** (Purchasing training ≠ Production training!)  
✅ Training material **Bahasa Indonesia** (English OK untuk IT, not for Admin!)  
✅ **Practice environment** untuk trial & error (no fear break production!)  
✅ **Train the trainer** approach (train key users, mereka train yang lain!)

#### 5.3.4 Long-Term Partnership (Not Project-Based!)

✅ **Onsite support** minimum 3 bulan post-GoLive!  
✅ **SLA clear** (response time, resolution time!)  
✅ **Dedicated support person** (not ticket system yang lama reply!)  
✅ **Regular review** (monthly? quarterly? untuk continuous improvement!)  
✅ **Change request process** yang reasonable (tidak semua ditolak!)

### 5.4 Critical Success Factors Kali Ini

**Kami akan PROCEED dengan implementasi Odoo HANYA JIKA**:

| Critical Factor | Why Critical | How to Achieve |
|-----------------|--------------|----------------|
| **1. User Adoption** | Jika admin reject lagi → System mubazir! | - Training comprehensive<br>- UI/UX user-friendly<br>- Involve users from design phase<br>- Quick wins (show value fast!) |
| **2. Customization Feasible** | Standard system will fail (proven!) | - Honest assessment dari vendor<br>- Clear scope customization<br>- Realistic timeline<br>- Budget transparent |
| **3. Vendor Commitment** | No support = No success! | - SLA in contract<br>- Dedicated team<br>- Onsite presence<br>- Long-term partnership mindset |
| **4. Management Buy-In** | Management skeptis, need convince! | - Phased delivery (proof of value!)<br>- Clear ROI tracking<br>- Regular progress update<br>- Risk mitigation plan |
| **5. Change Management** | Culture change butuh strategy! | - Change champions (key users!)<br>- Communication plan<br>- Incentive untuk early adopters<br>- Celebrate small wins! |

**Bottom Line**: Kami **sangat serious** untuk implement ERP yang **right** kali ini. Kami **tidak mau repeat failure** lagi. Kami butuh **partner yang understand**, bukan vendor yang **just sell software**!

---

<a name="section-6"></a>
## 🎯 6. MENGAPA BUTUH ERP SEKARANG

### 6.1 Business Pressure (External)

#### 6.1.1 IKEA Compliance Requirements

**Situasi**:
- IKEA menerapkan **stricter compliance** untuk supplier (2025-2026 period)
- Requirement baru:
  - ✅ **Digital traceability** (batch tracking end-to-end)
  - ✅ **Real-time visibility** (production status on-demand)
  - ✅ **Quality documentation** (Certificate of Compliance per shipment)
  - ✅ **Rapid response** to quality issue (max 24 jam!)

**Impact jika tidak comply**:
- ⚠️ Risk **supplier de-listing** (kehilangan 80% revenue!)
- ⚠️ **Penalty increasing** (late delivery, quality issue)
- ⚠️ **Audit failure** (IKEA annual audit)

**ERP adalah SOLUSI**:
- Digital traceability: ✅ Every batch tracked from PO to shipment
- Real-time visibility: ✅ Dashboard untuk IKEA access (jika diminta)
- Quality docs: ✅ Auto-generate certificate per batch
- Rapid response: ✅ System alert + quick action capability

#### 6.1.2 Market Competition

**Situasi**:
- Competitor (China, Vietnam, Bangladesh) sudah pakai **modern ERP**
- Competitor bisa **lead time faster** (karena system support!)
- Competitor bisa **price competitive** (karena efficiency tinggi!)

**Impact untuk Quty**:
- Risk **kehilangan market share**
- Customer compare kami vs competitor → Kami **kalah di efficiency**
- IKEA shift order ke competitor (karena mereka more reliable!)

**ERP adalah COMPETITIVE ADVANTAGE**:
- Lead time kami **-28%** (18 hari vs competitor 25 hari!)
- On-time delivery **95%+** (vs competitor 80-85%)
- Data-driven decision → **Cost efficiency better**

### 6.2 Internal Pressure

#### 6.2.1 Operational Chaos

**Situasi Saat Ini** (scale 1-10, 10 = chaos):
- Material management: 8/10 chaos (sering habis tiba-tiba!)
- Production coordination: 7/10 chaos (delay baru ketahuan telat!)
- Inventory accuracy: 8/10 chaos (stock opname selalu banyak adjustment!)
- Quality tracking: 9/10 chaos (no systematic!)

**Komentar Manager**: _"Setiap hari kami **fire-fighting**, bukan **planning**. Kami **reactive**, bukan **proactive**. This is NOT sustainable!"_

**ERP akan STABILIZE operations**:
- Material chaos → Real-time visibility + auto-alert
- Production coordination → Dashboard + notification system
- Inventory accuracy → Auto-transaction + validation
- Quality tracking → Systematic recording + analysis

#### 6.2.2 Scalability Issue

**Current Reality**:
- Volume naik 20% → Team stress increase 50%!
- Cannot handle more orders dengan **manual system** (human limit!)
- Jika mau grow → Harus **hire more admin** (not scalable!)

**ERP enables SCALABILITY**:
- Volume +50% → Team stress cuma +10% (system handle!)
- System unlimited capacity (beda dengan human!)
- Automation → No need hire linear dengan volume increase

#### 6.2.3 Management Visibility

**Current Problem**:
- Director ask: "Berapa WIP di Sewing hari ini?" → **Tidak bisa jawab instant!**
- Manager ask: "Mana SPK yang delay?" → **Harus tanya 5 dept satu-satu!**
- Finance ask: "Berapa material cost bulan ini?" → **Tunggu 5 hari!**

**Impact**:
- Decision making **SLOW**
- Opportunity missed (karena no fast data!)
- Problem escalated before detected

**ERP provides REAL-TIME VISIBILITY**:
- Dashboard real-time (1 screen show everything!)
- KPI tracking automatic
- Alert system (problem detected early!)

### 6.3 Window of Opportunity

**Strategic Timing** (Mengapa SEKARANG adalah best time):

| Factor | Why Now? |
|--------|----------|
| **Business Stable** | Volume predictable, no major disruption planned → Good time for change! |
| **Team Ready** | Trauma ERP lama sudah **healing** (2 tahun passed), ready untuk try again! |
| **Budget Available** | Management commit budget untuk proper implementation (learned from failure!) |
| **Technology Mature** | Odoo 18 sudah **mature & stable** (vs Odoo 10-14 yang masih banyak bug!) |
| **Support Ecosystem** | Banyak Odoo partner di Indonesia → Support lebih accessible! |

**Risk jika TUNDA lagi**:
- ⚠️ IKEA compliance deadline → **Cannot postpone!**
- ⚠️ Competitor advantage makin besar → **Market share loss!**
- ⚠️ Team burnout (manual chaos terus-terus!) → **Turnover risk!**

### 6.4 Expected Transformation

**Vision**: FROM Manual Chaos → TO Digital Excellence

**Timeline Expectation**:
```
PHASE 1 (Month 1-6): FOUNDATION
├─ Go-Live core modules (Manufacturing, Inventory, Purchasing)
├─ User training & adoption
├─ Data migration & cleanup
└─ Stabilization period

PHASE 2 (Month 7-12): OPTIMIZATION
├─ Enable advanced features (Quality, Analytics)
├─ Process optimization based on data
├─ Custom reports & dashboards
└─ Integration with external systems (if needed)

PHASE 3 (Month 13+): CONTINUOUS IMPROVEMENT
├─ Kaizen based on KPI
├─ Additional modules (if needed)
├─ Scale to support business growth
└─ Leverage for competitive advantage
```

**Success Metrics** (akan dicapai dalam 12-18 bulan post-GoLive):

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Lead Time** | 25 hari | 18 hari | -28% ⚡ |
| **On-Time Delivery** | 75% | 95%+ | +27% 📦 |
| **Inventory Accuracy** | 82% | 98%+ | +20% 📊 |
| **Reporting Time** | 15 jam/minggu → 1 jam/minggu | -93% ⏱️ |
| **Defect Tracking** | 0% tracked | 100% tracked | +100% ✅ |
| **Manual Data Entry** | 40 hours/week | <5 hours/week | -87% 🎯 |
| **User Satisfaction** | Admin trauma | Admin comfortable | Culture change! 👥 |

---

<a name="section-7"></a>
## 🏭 7. ALUR PRODUKSI LENGKAP (6 STAGES)

### 7.1 Production Flow Overview

**Timeline Total**: 18-25 hari (tergantung routing & complexity)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                   PT QUTY KARUNIA - PRODUCTION FLOW                             │
└─────────────────────────────────────────────────────────────────────────────────┘

TRIGGER SEQUENCE:
═════════════════
1️⃣  PO FABRIC (TRIGGER 1) → MO Created (MODE: PARTIAL)
    ├─ Cutting UNLOCKED ✅
    ├─ Embroidery UNLOCKED ✅ (jika internal atau siap ke vendor)
    └─ Sewing-onwards LOCKED 🔒 (waiting PO Label)

2️⃣  PO LABEL (TRIGGER 2) → MO Upgraded (MODE: RELEASED)
    ├─ Auto-inherit Week & Destination (READ-ONLY!) 🔐
    ├─ ALL departments UNLOCKED ✅
    └─ Full production dapat berjalan


PRODUCTION STAGES (6 STAGES):
════════════════════════════════

┌───────────────┐
│  STAGE 0:     │  Timeline: Variable (3-10 hari)
│  PURCHASING   │  ─────────────────────────────────────────────────────
└───────┬───────┘  • Purchasing A: Create PO Fabric (TRIGGER 1!)
        │          • System: Auto-create MO (mode: PARTIAL)
        │          • Purchasing B: Create PO Label (TRIGGER 2!)  
        │          • System: Auto-upgrade MO → RELEASED
        │          • Purchasing C: Create PO Accessories
        ↓
┌───────────────┐
│  STAGE 1:     │  Timeline: 2-3 hari | Dept: Cutting | Team: 2 Admin
│  CUTTING      │  ─────────────────────────────────────────────────────
└───────┬───────┘  Input:  Fabric (YARD)
        │          Output: Cut pieces - DUAL STREAM!
        │                  ├─ Body pieces (untuk boneka)
        │                  └─ Baju pieces (untuk pakaian)
        │          Conversion: YARD → PCS (via BOM marker)
        │          Storage: WH-Cutting (separate Body vs Baju!)
        │          Target: MO qty + 10% buffer
        ↓
┌───────────────┐
│  STAGE 2:     │  Timeline: 1-2 hari (internal) OR 4-7 hari (vendor)
│  EMBROIDERY   │  ─────────────────────────────────────────────────────
│  (OPTIONAL!)  │  Routing Options:
└───────┬───────┘    ├─ Route 1: Embroidery INTERNAL (jika punya mesin)
        │            ├─ Route 2: SKIP (artikel tanpa embroidery!)
        │            └─ Route 3: Embroidery VENDOR (outsource!)
        │          
        │          [Route 1: Internal]
        │          Input:  Cut Body pieces, Thread embroidery
        │          Process: Embroidery patterns (logo, eyes, etc)
        │          Output: Embroidered Body pieces
        │          Storage: WH-Embroidery
        │          
        │          [Route 3: Vendor]
        │          Process: 
        │            1. Create DN outbound → Send to vendor
        │            2. Vendor proses (track via WA/Email)
        │            3. Receive GR inbound ← Return from vendor
        │            4. Data Entry input hasil vendor ke system
        │          Storage: Transit status (system track!)
        ↓
┌───────────────┐
│  STAGE 3:     │  Timeline: 4-6 hari | Dept: Sewing | Team: 2 Admin
│  SEWING       │  ─────────────────────────────────────────────────────
└───────┬───────┘  Input:  ├─ Embroidered Body pieces (or Cut Body jika skip)
        │                  ├─ Cut Baju pieces
        │                  └─ Thread, Accessories (eyes, nose, etc)
        │          
        │          Process: DUAL PARALLEL STREAM!
        │                  ├─ Stream A: Sew Body → Skin (boneka shell)
        │                  └─ Stream B: Sew Baju → Finished Baju
        │          
        │          Output: ├─ Skin (belum isi kapas)
        │                  └─ Finished Baju
        │          
        │          Storage: WH-Sewing (separate tracking!)
        │          QC Checkpoint: Stitch quality, symmetry
        │          Target: MO qty + 15% buffer (highest defect stage!)
        ↓
┌───────────────┐
│  STAGE 4A:    │  Timeline: 1-2 hari | Dept: Finishing | Team: 2 Admin
│  STUFFING     │  ─────────────────────────────────────────────────────
│  (Finishing   │  Location: Warehouse Finishing - Stuffing Area
│   Stage 1)    │  
└───────┬───────┘  Input:  ├─ Skin (from Sewing)
        │                  ├─ Filling/Dacron (GRAM)
        │                  └─ Thread closing
        │          
        │          Process: Isi kapas + Jahit tutup lubang
        │          
        │          Output: Stuffed Body (boneka isi kapas, belum ada tag)
        │          
        │          Storage: WH-Finishing (Stuffed Body stock)
        │          Conversion: Internal (no formal DN!)
        │          Material consumption: Auto-backflush
        ↓
┌───────────────┐
│  STAGE 4B:    │  Timeline: 1 hari | Dept: Finishing | Team: 2 Admin
│  CLOSING      │  ─────────────────────────────────────────────────────
│  (Finishing   │  Location: Warehouse Finishing - Closing Area
│   Stage 2)    │  
└───────┬───────┘  Input:  ├─ Stuffed Body (from Stage 4A)
        │                  └─ Hang Tag (with Week & Destination!)
        │          
        │          Process: Pasang hang tag + QC final inspection
        │          
        │          Output: Finished Doll (boneka ready!)
        │          
        │          Storage: WH-Finishing (Finished Doll stock)
        │          QC Checkpoint: Tag placement, appearance, metal detector
        │          Transfer: Finished Doll → WH Main (formal DN!)
        ↓
┌───────────────┐
│  STAGE 5:     │  Timeline: 1-2 hari | Dept: Packing | Team: 2 Admin
│  PACKING      │  ─────────────────────────────────────────────────────
└───────┬───────┘  Input:  ├─ Finished Doll (from Finishing)
        │                  ├─ Finished Baju (from Sewing)
        │                  ├─ Accessory packaging (plastic bag, insert, dll)
        │                  └─ Carton (master carton)
        │          
        │          Process: FINAL ASSEMBLY!
        │                  1. Assembly: Doll + Baju → 1 Set FG
        │                  2. Insert plastic bag + marketing insert
        │                  3. Pack into master carton (60 pcs/carton)
        │                  4. Generate barcode FG
        │                  5. Seal carton + label
        │          
        │          Output: Finished Goods (ready to ship!)
        │                  Format: Packed in carton, labeled, barcoded
        │          
        │          Storage: WH-Packing → Transfer to WH FG
        │          Conversion: PCS → CARTON (60 pcs/carton standard)
        │          QC Checkpoint: Completeness, packaging quality
        ↓
┌───────────────┐
│  STAGE 6:     │  Timeline: 0 hari Dept: FinishGood | Team: 2 Admin (storage & shipping)
│  FG STORAGE   │  ─────────────────────────────────────────────────────
└───────────────┘  Location: Warehouse Finished Goods
                   Organization: PER PALLET
                   ├─ Group by Week (W05-2026, W06-2026, etc)
                   ├─ Group by Destination (Belgium, Sweden, USA, etc)
                   ├─ Group by Article (AFTONSPARV, DJUNGELSKOG, etc)
                   └─ Each pallet = Multiple cartons (8-12 cartons/pallet)
                   
                   Stock Opname: DAILY! (high value inventory)
                   Prepare shipment: Pallet → Loading dock
```

### 7.2 Material Flow per Stage

**Tabel Material Input→Output per Departemen**:

| Stage | Input Material | Input UOM | Output Product | Output UOM | Conversion Logic | Waste/Scrap |
|-------|----------------|-----------|----------------|------------|------------------|-------------|
| **Cutting** | Fabric | YARD | Cut pieces (2 streams) | PCS | BOM Marker: 1 YD = X pcs | 3-5% |
| **Embroidery** | Cut pieces, Thread | PCS, CONE | Embroidered pieces | PCS | 1:1 (no conversion, add value) | 1-2% |
| **Sewing** | Embroidered/Cut pieces, Thread, Accessories | PCS, CONE, PCS | Skin + Baju | PCS | 1:1 assembly (2 outputs!) | 10-15% |
| **Stuffing** | Skin, Filling, Thread | PCS, GRAM, M | Stuffed Body | PCS | 30g filling/pcs | 2-3% |
| **Closing** | Stuffed Body, Hang Tag | PCS, PCS | Finished Doll | PCS | 1:1 (add tag) | 1-2% |
| **Packing** | Finished Doll, Finished Baju, Packaging, Carton | PCS, PCS, SET, PCS | Finished Goods | CARTON | 60 pcs/carton | <1% |

### 7.3 WIP Transfer Logic

**Real-Time WIP Batch Transfer**:

Berbeda dengan manufacturing standar (tunggu semua selesai baru transfer), Quty menggunakan **partial batch transfer** untuk **maximize throughput**:

**Contoh Scenario**:
```
SPK-001: Target 495 pcs

Day 1 (Cutting):
  ├─ Jam 10:00 → Output 150 pcs (batch 1) → TRANSFER to Embroidery immediate!
  ├─ Jam 14:00 → Output 120 pcs (batch 2) → TRANSFER to Embroidery immediate!
  └─ Jam 17:00 → Output 135 pcs (batch 3) → TRANSFER to Embroidery immediate!
  Total: 405 pcs completed → SPK-001 Status: IN PROGRESS (82% complete)

Day 1 (Embroidery - parallel start!):
  ├─ Jam 11:00 → Receive batch 1 (150 pcs) → START embroidery LANGSUNG!
  ├─ Jam 15:00 → Receive batch 2 (120 pcs) → Add to queue
  └─ Jam 18:00 → Receive batch 3 (135 pcs) → Add to queue

Day 2 (Cutting):
  └─ Jam 09:00 → Output 90 pcs (batch 4 - final) → TRANSFER
  Total: 495 pcs COMPLETED → SPK-001 Cutting Status: DONE ✅

Day 2 (Embroidery):
  ├─ Jam 10:00 → Batch 1 done (145 pcs after reject) → TRANSFER to Sewing!
  ├─ Jam 14:00 → Batch 2 done (118 pcs) → TRANSFER to Sewing!
  └─ Continue remaining batches...
```

**Impact ke ERP**:
- System harus support **partial transfer** (not wait for full SPK done!)
- Transfer log harus track **batch number** & timestamp
- Next department bisa **start immediately** (no waiting!)
- Status tracking: **Per-SPK status** vs **Per-Batch status**

### 7.4 Production Capacity & Lead Time

**Kapasitas per Departemen** (per shift 8 jam):

| Departemen | Kapasitas/Shift | Bottleneck? | Lead Time Kontribusi |
|------------|----------------|-------------|----------------------|
| Cutting | 800-1000 pcs | ❌ No | 2-3 hari |
| Embroidery (Internal) | 400-600 pcs | ⚠️ Medium | 1-2 hari |
| Embroidery (Vendor) | Variable | ⚠️ Unpredictable | 4-7 hari |
| Sewing | 600-750 pcs | 🔴 **YES! Bottleneck!** | 4-6 hari |
| Stuffing | 1200-1500 pcs | ❌ No | 1 hari |
| Closing | 1500-2000 pcs | ❌ No | 1 hari |
| Packing | 1000-1200 pcs | ❌ No | 1-2 hari |

**⚠️ CRITICAL INSIGHT: Sewing adalah BOTTLENECK utama!**
- Highest complexity (assembly 20-30 pieces per unit!)
- Highest defect rate (10-15% rejection!)
- Longest lead time contribution (25-30% dari total flow!)

**Implikasi untuk ERP**:
- Sewing dept butuh **highest priority attention** di dashboard!
- Alert system: Jika Sewing delay → **Auto-notify semua stakeholders!**
- Planning logic: **Always schedule based on Sewing capacity** (bukan dept lain!)

### 7.5 Quality Control Checkpoints (4 Stages)

**QC Flow Integration**:

```
┌──────────────────────────────────────────────────────────────┐
│              QUALITY CONTROL WORKFLOW                        │
└──────────────────────────────────────────────────────────────┘

QC1: POST-CUTTING
─────────────────────────────────────────────────────────────
Location: End of Cutting dept
Check: Size accuracy (±2mm tolerance)
       Pattern alignment
       Cutting quality (no loose threads)
Action: ├─ PASS → Transfer to Embroidery
        └─ REJECT → Scrap (record defect category)
Target Pass Rate: >95%


QC2: POST-SEWING ← MOST CRITICAL!
─────────────────────────────────────────────────────────────
Location: End of Sewing dept
Check: Stitch quality (no loose/jumping stitch)
       Symmetry (left vs right match)
       Assembly correctness (all pieces attached)
       Appearance (no stain, no defect)
Action: ├─ PASS → Transfer to Finishing
        ├─ REWORK → Send to Rework Queue (repair stitch)
        └─ SCRAP → Record defect (unrepairable)
Target Pass Rate: >85% (hardest QC!)
Rework Recovery Rate Target: >80%


QC3: POST-FINISHING
─────────────────────────────────────────────────────────────
Location: End of Closing (Finishing Stage 2)
Check: Stuffing uniformity (no lumps, no hollow)
       Tag placement (correct position)
       Appearance (clean, no stain)
       Weight check (within ±5% tolerance)
Action: ├─ PASS → Transfer to Packing
        ├─ REWORK → Re-stuff or re-tag
        └─ SCRAP → Record defect
Target Pass Rate: >98%


QC4: FINAL INSPECTION (PRE-SHIPMENT)
─────────────────────────────────────────────────────────────
Location: End of Packing dept
Check: Completeness (Doll + Baju + Packaging complete)
       Metal detector scan (MANDATORY! IKEA requirement)
       Barcode verification
       Carton integrity
       Certificate of Compliance ready
Action: ├─ PASS → Transfer to FG Warehouse → Ready ship!
        └─ REJECT → Unpack, inspect, repack (emergency!)
Target Pass Rate: >99%
```

**Defect Recording Requirements per Checkpoint**:

| Defect Category | QC1 | QC2 | QC3 | QC4 | Root Cause Options |
|-----------------|-----|-----|-----|-----|-------------------|
| **Material defect** | ✅ | ✅ | ✅ | ✅ | Supplier quality, wrong spec |
| **Process defect** | ✅ | ✅ | ✅ | ❌ | Machine setting, admin skill |
| **Assembly defect** | ❌ | ✅ | ✅ | ✅ | Wrong sequence, missing piece |
| **Dimension defect** | ✅ | ✅ | ✅ | ❌ | Pattern error, cutting error |
| **Appearance defect** | ❌ | ✅ | ✅ | ✅ | Stain, color difference |

**Rework Workflow** (untuk defect yang bisa diperbaiki):

```
Defect Detected (QC2 or QC3)
  ↓
QC Inspector: Record defect + Assign to Rework Queue
  ↓
Rework Admin: Receive item + Assess repair feasibility
  ├─ Repairable? → Assign to skilled worker
  │   ↓
  │   Rework process (re-stitch, re-stuff, etc)
  │   ↓
  │   Re-submit to QC (Re-inspection!)
  │   ├─ Pass → Re-join production flow ✅
  │   └─ Fail → SCRAP (2nd reject = unrepairable) ❌
  │
  └─ Not repairable? → Direct SCRAP ❌

System Requirements:
- Rework queue management (FIFO)
- Rework time tracking (untuk KPI)
- Recovery rate calculation (Pass after rework / Total rework)
- Root cause tracking (by admin, by machine, by shift)
```

---

<a name="section-8"></a>
## 🛒 8. PURCHASING WORKFLOW (3 PARALLEL STREAMS)

### 8.1 Overview Purchasing Process

**3 Specialist Roles** = **3 Parallel Streams** (NOT sequential!):

```
┌──────────────────────────────────────────────────────────────────────┐
│         PURCHASING DEPARTMENT - 3 PARALLEL STREAMS                   │
└──────────────────────────────────────────────────────────────────────┘

                      [CUSTOMER ORDER]
                      (Email dari IKEA)
                             │
                 ┌───────────┼───────────┬──────────────┐
                 │           │           │              │
                 ↓           ↓           ↓              ↓
          ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐
          │PURCHASE │ │PURCHASE │ │PURCHASE  │ │   (System    │
          │   A     │ │   B     │ │    C     │ │   Auto-gen   │
          │ FABRIC  │ │ LABEL   │ │ACCESSORY │ │   based on   │
          └────┬────┘ └────┬────┘ └────┬─────┘ │   POs)       │
               │           │           │       └──────────────┘
               ↓           ↓           ↓
        ┌───────────┐ ┌────────────┐ ┌───────────┐
        │ PO KAIN   │ │ PO LABEL   │ │ PO ACCESS │
        │ (Fabric)  │ │ (Critical!)│ │ (Thread,  │
        └─────┬─────┘ └─────┬──────┘ │  Filling, │
              │             │        │  Carton)  │
              │             │        └─────┬─────┘
              │             │              │
              │             │              ↓
              │             │         [Vendor]
              │             │         Deliver
              │             │         accessories
              │             │              │
              │             │              ↓
              │             │         [WH Main]
              │             │         Receive
              │             │              
              ↓             ↓
        [Vendor Kain]  [Vendor Label]
        Deliver        Deliver
              │             │
              ↓             ↓
        [WH Main]      [WH Main]
        Receive        Receive
              │             │
              └──────┬──────┘
                     ↓
              ┌──────────────┐
              │  PRODUCTION  │ ← Auto-Start based on triggers!
              │   UNLOCKED   │
              └──────────────┘

TIMELINE:
════════
├─ PO Fabric (T+0): Lead time 3-5 hari → Receive T+3~5
├─ PO Label (T+0): Lead time 7-10 hari → Receive T+7~10 ← LONGEST!
└─ PO Accessories (T+0): Lead time 3-7 hari → Receive T+3~7

CRITICAL PATH: PO Label (paling lama!)
```

### 8.2 Stream 1: PO FABRIC (Purchase A - TRIGGER 1!)

**📌 CRITICAL: PO FABRIC adalah TRIGGER PERTAMA untuk production start!**

#### 8.2.1 Workflow PO Fabric

```
Step 1: Customer Order Received
─────────────────────────────────────────────────────
├─ Source: Email dari IKEA (OR portal jika ada)
├─ Info: Article, Quantity, Week, Destination
└─ Action: Purchasing A → Review order → Confirm feasibility

Step 2: Calculate Material Requirements
─────────────────────────────────────────────────────
├─ System: Read BOM per artikel
├─ Calculate:
│   └─ Fabric Type 1: 45 YARD (for 495 pcs with buffer)
│       Fabric Type 2: 12 YARD
│       Fabric Type 3: 8 YARD
│       ... (total 9-12 fabric types per artikel!)
└─ Check stock: Apakah WH Main cukup? Or need PO?

Step 3: Create PO Fabric
─────────────────────────────────────────────────────
├─ Input:
│   ├─ Vendor: PT Tekstil Jaya (contoh)
│   ├─ Material: Fabric Type 1 - Cotton Velboa Red
│   ├─ Quantity: 45 YARD
│   ├─ Price: (per YARD)
│   ├─ Delivery date: T+5
│   ├─ Destination: WH Main
│   └─ Link to: Customer order reference
├─ Approval:
│   └─ Jika PO > threshold → Manager approval required
└─ Submit PO

Step 4: TRIGGER 1 ACTIVATED! 🚀
─────────────────────────────────────────────────────
System Auto-Action:
├─ ✅ Create Manufacturing Order (MO)
│   ├─ Article: AFTONSPARV Bear (from customer order)
│   ├─ Quantity: 450 pcs (customer qty)
│   ├─ Week: W05-2026 (TBD - will update from PO Label!)
│   ├─ Destination: TBD (will update from PO Label!)
│   ├─ Status: PARTIAL (not yet fully released!)
│   └─ Departments unlocked:
│       ├─ Cutting: ✅ UNLOCKED (can start!)
│       ├─ Embroidery: ✅ UNLOCKED (can start if Route 1/3!)
│       └─ Sewing onwards: 🔒 LOCKED (wait PO Label!)
│
├─ ✅ Generate Work Orders (per dept)
│   ├─ WO-Cutting-001
│   │   ├─ Input: Fabric 45 YD + 12 YD + 8 YD
│   │   ├─ Output: Cut pieces 495 pcs (target)
│   │   └─ Status: Ready to Start
│   └─ WO-Embroidery-001 (jika applicable)
│       ├─ Input: Cut pieces 495 pcs
│       └─ Status: Waiting (dept locked until PO Label)
│
└─ ✅ Notification
    ├─ To: Purchasing B (Label specialist)
    │   └─ Message: "MO created PARTIAL. Segera create PO Label!"
    └─ To: Cutting SPV
        └─ Message: "WO ready. Tunggu fabric arrive, can start!"

Step 5: Vendor Deliver Fabric
─────────────────────────────────────────────────────
├─ Vendor send fabric (T+3 ~ T+5)
├─ WH Staff: Receive goods
│   ├─ Check quantity (45 YARD received?)
│   ├─ Check quality (sample inspection)
│   └─ Input GRN (Goods Receipt Note) ke system
└─ System update:
    ├─ Stock WH Main: +45 YARD Fabric Type 1
    └─ PO Status: Completed ✅

Step 6: Cutting Can Start! (Early Start Advantage!)
─────────────────────────────────────────────────────
├─ Cutting SPV: View WO-Cutting-001
├─ Check material availability: ✅ Fabric sudah datang!
├─ Assign workers → Start cutting!
└─ Timeline advantage:
    ├─ Without TRIGGER 1: Wait all materials (T+10) → Start cutting T+10
    └─ With TRIGGER 1: Start cutting T+5 → SAVE 5 DAYS! ⚡
```

#### 8.2.2 Material Requirements per Article

**Contoh: AFTONSPARV Bear (40cm)**

| Material | Specification | UOM Beli | Qty Needed (per 495 pcs) | Vendor Lead Time |
|----------|---------------|----------|--------------------------|------------------|
| Fabric Type 1 | Cotton Velboa Red | YARD | 45 YARD | 3-5 hari |
| Fabric Type 2 | Cotton Velboa Brown | YARD | 12 YARD | 3-5 hari |
| Fabric Type 3 | Polyester Black (eyes) | YARD | 2 YARD | 3-5 hari |
| Fabric Type 4 | Velvet Maroon (clothes) | YARD | 8 YARD | 3-5 hari |
| ... | ... | ... | ... | ... |
| **TOTAL FABRIC** | **12 types** | **YARD** | **~80 YARD total** | **3-5 hari** |

**Notes**:
- Buffer included (+10% untuk Cutting defect)
- Setiap artikel beda-beda fabric requirements!
- System must auto-calculate from BOM (no manual!)

### 8.3 Stream 2: PO LABEL (Purchase B - TRIGGER 2!) ⭐ MOST CRITICAL!

**📌 ULTRA CRITICAL: PO LABEL unlock full production + contain Week & Destination!**

#### 8.3.1 Why Label is MOST CRITICAL?

**3 Alasan Label Paling Kritis**:

1. **Longest Lead Time** (7-10 hari vs 3-5 hari untuk fabric!)
   - Label printing membutuhkan artwork approval (customer)
   - Multi-language support (per destination country)
   - Compliance information (safety, material, origin)

2. **Production Blocker** (Sewing onwards CANNOT start without label ready!)
   - Risk: Salah destination → Product REJECT by customer!
   - Example: Label Belgium ≠ Label Sweden (different language!)
   - Cannot proceed to Packing without correct label!

3. ** Contains LOCKED Information** (Week & Destination auto-inherited!)
   - Week: W05-2026 (shipping week - LOCKED after creation!)
   - Destination: Belgium (destination country - LOCKED!)
   - System rule: Week & Destination CANNOT be edited after PO Label created!

#### 8.3.2 Workflow PO Label

```
Step 1: Review MO Status
─────────────────────────────────────────────────────
├─ Purchasing B: Lihat MO list (status: PARTIAL)
├─ Priority: Mana MO yang paling urgent?
└─ Check: Fabric sudah datang? Cutting sudah start?

Step 2: Prepare Label Information
─────────────────────────────────────────────────────
├─ Customer order details:
│   ├─ Article: AFTONSPARV Bear 40cm
│   ├─ Article Code: 40551542
│   ├─ Quantity: 450 pcs
│   ├─ **Week: W05-2026** ← CRITICAL INFO!
│   ├─ **Destination: Belgium** ← CRITICAL INFO!
│   └─ Language: French/Dutch
├─ Artwork:
│   ├─ IKEA standard template
│   ├─ Barcode: [Auto-generate]
│   └─ Compliance info: Made in Indonesia, safety warnings
└─ Quantity calculation:
    └─ 450 pcs + 5% buffer = 473 pcs labels needed

Step 3: Create PO Label
─────────────────────────────────────────────────────
├─ Input:
│   ├─ Vendor: PT Label Prima (contoh)
│   ├─ Material: Hang Tag AFTONSPARV
│   ├─ Quantity: 473 PCS
│   ├─ Week: W05-2026 ← INPUT ONE TIME HERE!
│   ├─ Destination: Belgium ← INPUT ONE TIME HERE!
│   ├─ Artwork: [Attachment file PDF]
│   ├─ Delivery date: T+10
│   └─ Link to: MO-2026-001
├─ Approval:
│   ├─ Manager approval (label critical!)
│   └─ Artwork confirmation from customer
└─ Submit PO

Step 4: TRIGGER 2 ACTIVATED! 🚀🚀
─────────────────────────────────────────────────────
System Auto-Action:
├─ ✅ Upgrade Manufacturing Order status
│   ├─ MO-2026-001: PARTIAL → RELEASED
│   ├─ **Week: TBD → W05-2026** (from PO Label!) 🔐
│   ├─ **Destination: TBD → Belgium** (from PO Label!) 🔐
│   ├─ Field status: READ-ONLY (cannot edit lagi!)
│   └─ Departments UNLOCKED:
│       ├─ Cutting: ✅ (already unlocked)
│       ├─ Embroidery: ✅ (already unlocked)
│       ├─ Sewing: ✅ UNLOCKED NOW! ← Can start!
│       ├─ Finishing: ✅ UNLOCKED NOW!
│       └─ Packing: ✅ UNLOCKED NOW!
│
├─ ✅ Work Orders updated
│   ├─ WO-Sewing-001: Status LOCKED → Ready to Start
│   ├─ WO-Finishing-001: Status LOCKED → Ready to Start
│   └─ WO-Packing-001: Status LOCKED → Ready to Start
│
└─ ✅ Notification
    ├─ To: All Production SPVs
    │   └─ "MO-2026-001 RELEASED! Week: W05-2026, Dest: Belgium"
    └─ To: Manager
        └─ "Production full unlock. Monitor progress!"

Step 5: Label Printing & Delivery
─────────────────────────────────────────────────────
├─ Vendor: Print labels (artwork approved)
├─ Quality check: Barcode scan test, info accuracy
├─ Delivery: T+7 ~ T+10
└─ WH Staff: Receive labels
    ├─ Input GRN ke system
    ├─ Stock update: +473 pcs Hang Tag
    └─ Distribute: Transfer to WH-Finishing (for Closing stage)

Step 6: Production Full Speed!
─────────────────────────────────────────────────────
├─ Timeline:
│   ├─ T+0: PO Label created (TRIGGER 2!)
│   ├─ T+5: Cutting done (early start dari Trigger 1!)
│   ├─ T+7: Sewing start (unlocked by Trigger 2!)
│   ├─ T+10: Label arrived (just in time!)
│   ├─ T+12: Finishing done (with correct label!)
│   └─ T+14: Packing done → FG ready!
└─ Result:
    └─ Total lead time: 14 hari (vs 20 hari tanpa dual trigger!)
```

#### 8.3.3 Week & Destination Lock Logic

**CRITICAL BUSINESS RULE**:

```
┌────────────────────────────────────────────────────────────┐
│  RULE: Week & Destination LOCKED after PO Label created!  │
│  WHY: Prevent production mismatch dengan label info!      │
└────────────────────────────────────────────────────────────┘

Scenario A: CORRECT IMPLEMENTATION ✅
──────────────────────────────────────────────────────
1. Purchasing B create PO Label
   └─ Input: Week = W05-2026, Destination = Belgium

2. System auto-inherit to MO
   └─ MO-2026-001: Week = W05-2026 (READ-ONLY! 🔒)
                   Destination = Belgium (READ-ONLY! 🔒)

3. Label printed dengan info:
   └─ Week: W05-2026, Destination: Belgium

4. Production proceed:
   └─ All departments see: Week W05-2026, Dest Belgium
   └─ No confusion! All aligned!

Result: Label match production info → SHIP SUCCESS! ✅


Scenario B: WRONG IMPLEMENTATION (Manual edit allowed) ❌
──────────────────────────────────────────────────────
1. Purchasing B create PO Label
   └─ Week = W05-2026, Destination = Belgium

2. System allow manual edit MO:
   └─ Admin accidentally change:
       Week W05-2026 → W06-2026 ❌
       Destination Belgium → Sweden ❌

3. Label printed (Week W05, Dest Belgium)
   BUT Production info different (Week W06, Dest Sweden)

4. Packing stage:
   └─ Pack dengan label W05-Belgium
   └─ System report: W06-Sweden (NOT MATCH!)

Result: MISMATCH! Customer reject shipment! PENALTY! ❌❌
```

**System Implementation Need**:
- ✅ Field Week: **Auto-populate** from PO Label (one source of truth!)
- ✅ Field Destination: **Auto-populate** from PO Label
- ✅ Field status: **READ-ONLY after PO Label created** (lock with visual indicator!)
- ✅ Validation: System **block shipment** jika Week/Dest tidak match dengan label!
- ✅ Change request: Jika TERPAKSA harus ubah → **Special approval workflow** + **Re-order label!**

### 8.4 Stream 3: PO ACCESSORIES (Purchase C)

**Material Categories** (bukan trigger, tapi essential!):

#### 8.4.1 Thread (Benang)

| Thread Type | Usage | UOM Beli | UOM Pakai | Conversion |
|-------------|-------|----------|-----------|------------|
| Thread Polyester (Sewing) | Jahit Body & Baju | CONE | METER | 1 Cone = 5000 M |
| Thread Embroidery | Embroidery patterns | CONE | METER | 1 Cone = 3000 M |
| Thread Closing | Stuffing closing | CONE | METER | 1 Cone = 5000 M |

#### 8.4.2 Filling (Kapas)

| Filling Type | Usage | UOM Beli | UOM Pakai | Consumption Rate |
|--------------|-------|----------|-----------|------------------|
| Dacron Hollow Fiber | Stuffing boneka | BAL (25 KG/bal) | GRAM | 30 g/pcs (artikel 40cm) |
| Cotton Filling | Stuffing premium artikel | BAL (20 KG/bal) | GRAM | 35 g/pcs |

#### 8.4.3 Accessories

| Accessory | Usage | UOM Beli | UOM Pakai | Conversion |
|-----------|-------|----------|-----------|------------|
| Plastic Eyes | Boneka eyes | GROSS | PCS | 1 Gross = 144 pcs |
| Safety Nose | Boneka nose | GROSS | PCS | 1 Gross = 144 pcs |
| Plastic Bag | Packaging individual | PCS | PCS | 1:1 |
| Insert Card | Marketing material | PCS | PCS | 1:1 |

#### 8.4.4 PO Accessories Workflow

```
Step 1: MO Created (after Trigger 1 or 2)
─────────────────────────────────────────────────────
├─ System: Read BOM → List all accessories needed
├─ Check stock WH Main:
│   ├─ Thread Polyester: Stock 150 Cone (cukup ✅)
│   ├─ Filling Dacron: Stock 5 Bal = 125 KG (kurang ❌)
│   └─ Plastic Eyes: Stock 200 pcs (kurang ❌)
└─ Generate Purchase Requisition (PR)

Step 2: Purchasing C Review PR
─────────────────────────────────────────────────────
├─ Prioritize material yang stock critical
├─ Vendor selection (best price + fastest delivery)
└─ Create PO Accessories

Step 3: PO Execution
─────────────────────────────────────────────────────
├─ Submit PO to vendor
├─ Track delivery
└─ Receive goods → GRN → Stock update

Notes:
- PO Accessories TIDAK trigger MO creation (passive)
- Tapi tetap essential (production STOP jika accessories habis!)
- Lead time relative short (3-7 hari) vs Label (7-10 hari)
```

### 8.5 Vendor Management

**Vendor Categories**:

| Category | Jumlah Vendor | Material | Lead Time | Payment Terms |
|----------|---------------|----------|-----------|---------------|
| **Fabric Supplier** | 5-8 vendors | Fabric berbagai types | 3-5 hari | NET 30 |
| **Label Supplier** | 2-3 vendors | Hang tag, barcode label, carton label | 7-10 hari | NET 30 |
| **Thread Supplier** | 2-3 vendors | Thread polyester, embroidery | 3-5 hari | NET 30 |
| **Filling Supplier** | 2 vendors | Dacron, cotton filling | 3-7 hari | NET 30 |
| **Accessories Supplier** | 5-7 vendors | Eyes, nose, plastic bag, insert, dll | 3-7 hari | NET 30 |
| **Carton Supplier** | 2 vendors | Master carton | 5-7 hari | NET 30 |
| **Embroidery Subcon** | 2-3 vendors | Embroidery outsource (Route 3) | 5-10 hari | NET 15 |

**Vendor Evaluation Criteria** (system should track!):

| Criteria | Weight | Measurement |
|----------|--------|-------------|
| **Quality** | 35% | Defect rate, compliance |
| **Delivery** | 30% | On-time delivery %, lead time accuracy |
| **Price** | 20% | Competitive pricing |
| **Responsiveness** | 10% | Communication, issue resolution |
| **Flexibility** | 5% | Rush order capability, qty adjustment |

---

<a name="section-9"></a>
## 🏬 9. WAREHOUSE STRUCTURE & MANAGEMENT

### 9.1 Warehouse Ecosystem Overview

**Total Warehouse Types**: **3 Main + 5 Department-Level** = 8 locations

```
┌──────────────────────────────────────────────────────────────────┐
│           PT QUTY KARUNIA - WAREHOUSE STRUCTURE                  │
└──────────────────────────────────────────────────────────────────┘

MAIN WAREHOUSES (3):
═══════════════════════════════════════════════════════════════════

[1] WH MAIN (Raw Materials & Staging)
    ├─ Location: Building A
    ├─ Size: 500 sqm
    ├─ Function: Receive raw materials, issue to production
    ├─ Stock:
    │   ├─ Fabric (by type & color): 50-80 types
    │   ├─ Thread (by type):12-15 types    │   ├─ Filling (Dacron/Cotton): 2-3 types
    │   ├─ Accessories (Eyes, Nose, etc): 20-30 types
    │   └─ Carton (Master carton): 3-5 sizes
    ├─ Organization: Rak system (by material category)
    ├─ Stock Opname: Monthly (full count)
    └─ Staff: 1 person (WH Main staff)


[2] WH FINISHING (2-Stage Processing Center) ⭐ UNIQUE!
    ├─ Location: Adjacent to Finishing dept
    ├─ Size: 200 sqm (2 areas: Stuffing + Closing)
    ├─ Function: Internal conversion (2 stages)
    ├─ Stock:
    │   ├─ AREA 1 - Stuffing:
    │   │   └─ Skin (from Sewing): Variable WIP
    │   └─ AREA 2 - Closing:
    │       └─ Stuffed Body (from Stuffing): Variable WIP
    ├─ Special Logic: Internal conversion WITHOUT formal DN!
    ├─ Stock Opname: Weekly (because high-value WIP!)
    └─ Staff: 1 person (WH Finishing staff)


[3] WH FINISHED GOODS (FG Storage)
    ├─ Location: Building B (near loading dock)
    ├─ Size: 800 sqm
    ├─ Function: Ready-to-ship FG storage
    ├─ Organization: PER PALLET (critical!)
    │   ├─ Group by Week (W05-2026, W06-2026, etc)
    │   ├─ Group by Destination (Belgium, Sweden, USA, China, etc)
    │   ├─ Group by Article (AFTONSPARV, DJUNGELSKOG, etc)
    │   └─ Each pallet:
    │       ├─ 8-12 cartons per pallet
    │       ├─ 60 pcs per carton (standard)
    │       └─ Total: 480-720 pcs per pallet
    ├─ Tracking:
    │   ├─ Pallet barcode (unique ID)
    │   ├─ Carton barcode (per carton)
    │   └─ System knows: Which pallet contains what
    ├─ Stock Opname: DAILY! (high-value inventory!)
    └─ Staff: 1 person (WH FG staff)


DEPARTMENT-LEVEL WAREHOUSES (5):
═══════════════════════════════════════════════════════════════════

[4] WH-CUTTING
    ├─ Location: Inside Cutting dept area
    ├─ Function: Temporary storage for cut pieces (before transfer)
    ├─ Stock: Cut pieces WIP (Body + Baju separate!)
    ├─ Capacity: 2000-3000 pcs (1-2 days buffer)
    ├─ Stock Opname: Weekly
    └─ Staff: Cutting admin (part-time WH duty)

[5] WH-EMBROIDERY
    ├─ Location: Inside Embroidery dept area
    ├─ Function: Embroidery WIP (include vendor transit!)
    ├─ Stock:
    │   ├─ Waiting embroidery: Queue pcs
    │   ├─ In-process: Pcs in machine
    │   └─ Vendor transit: Pcs sent to vendor (Route 3)
    ├─ Stock Opname: Weekly
    └─ Staff: Embroidery admin

[6] WH-SEWING
    ├─ Location: Inside Sewing dept area
    ├─ Function: Sewing WIP (2 products: Skin + Baju)
    ├─ Stock:
    │   ├─ Skin (Body): Variable pcs
    │   └─ Finished Baju: Variable pcs
    ├─ Notes: Track separately! (Skin ≠ Baju)
    ├─ Stock Opname: Weekly
    └─ Staff: Sewing admin (2 persons, track 2 streams!)

[7] WH-FINISHING (Already explained as WH Main #2)

[8] WH-PACKING
    ├─ Location: Inside Packing dept area
    ├─ Function: Pre-packing staging (Doll + Baju ready assembly)
    ├─ Stock:
    │   ├─ Finished Doll (from Finishing)
    │   └─ Finished Baju (from Sewing)
    ├─ Stock Opname: DAILY! (final stage before FG!)
    └─ Staff: Packing admin
```

### 9.2 Stock Opname (Physical Count) Requirements

**⚠️ CRITICAL**: Stock opname adalah **PAIN POINT besar** di sistem manual saat ini. System harus automate dan simplify!

#### 9.2.1 Stock Opname Frequency

| Warehouse | Frequency | Why? | Duration Target |
|-----------|-----------|------|-----------------|
| **WH Main** | Monthly | Large inventory, stable, raw materials | 1 hari (full count) |
| **WH Finishing** | Weekly | High-value WIP, conversion process | 2 jam |
| **WH Finished Goods** | DAILY! | Highest value, shipping critical | 1 jam |
| **WH-Cutting** | Weekly | Fast-moving WIP | 1 jam |
| **WH-Embroidery** | Weekly | Include vendor transit tracking | 1 jam |
| **WH-Sewing** | Weekly | 2 products tracking | 1 jam |
| **WH-Packing** | DAILY! | Pre-shipment critical | 30 menit |

#### 9.2.2 Stock Opname Workflow

```
STOCK OPNAME PROCESS
════════════════════════════════════════════════════════════

Step 1: PHYSICAL COUNT
─────────────────────────────────────────────────────────
├─ WH Staff: Count physical inventory (per SKU)
├─ Tool: Barcode scanner (if available) OR manual count
├─ Input: Count result ke system
│   └─ Example: Fabric Type 1 Red = 35 YARD (physical)
└─ Timestamp: Count date & time recorded

Step 2: SYSTEM COMPARISON (AUTO!)
─────────────────────────────────────────────────────────
├─ System: Compare physical vs system stock
│   ├─ System stock: 38 YARD (from transactions)
│   └─ Physical count: 35 YARD (from Step 1)
│   └─ Variance: -3 YARD (8% difference)
├─ Variance calculation:
│   └─ Variance % = |Physical - System| / System × 100%
│   └─ 8% = |-3| / 38 × 100%
└─ Flag status based on threshold:
    ├─ Variance ≤ 2% → ✅ OK (auto-adjust, no approval!)
    ├─ Variance 2-5% → ⚠️ WARNING (approval SPV)
    └─ Variance > 5% → 🔴 CRITICAL (approval Manager + investigate!)

Step 3: VARIANCE ANALYSIS & APPROVAL
─────────────────────────────────────────────────────────
├─ If variance > 2%:
│   ├─ System: Request input "Reason for variance"
│   │   └─ Options:
│   │       ├─ Counting error (recount!)
│   │       ├─ Transaction not recorded (manual usage?)
│   │       ├─ Material loss/scrap (production waste?)
│   │       ├─ Theft (serious! investigate!)
│   │       └─ System error (bug?)
│   ├─ Assign to: SPV (variance 2-5%) or Manager (>5%)
│   └─ Approval workflow:
│       ├─ SPV/Manager: Review reason
│       ├─ Can request: Recount (jika not confident)
│       └─ Action: Approve OR Reject
└─ If approved:
    └─ System: Create Stock Adjustment transaction
        ├─ Adjust system stock: 38 YD → 35 YD
        ├─ Record: Adjustment reason, approved by, timestamp
        └─ Audit trail: Permanent record

Step 4: CLOSING & REPORT
─────────────────────────────────────────────────────────
├─ System: Generate Stock Opname Report
│   ├─ Summary:
│   │   ├─ Total SKU counted: 120 SKU
│   │   ├─ Variance <2%: 110 SKU (92%) ✅
│   │   ├─ Variance 2-5%: 8 SKU (7%) ⚠️
│   │   └─ Variance >5%: 2 SKU (2%) 🔴
│   ├─ Detail per SKU: Physical, System, Variance, Status
│   └─ Action items: Which SKU need investigation
├─ Distribution: Email to Manager, Finance, Purchasing
└─ System status: Stock Opname CLOSED for this cycle
```

#### 9.2.3 Cycle Count Strategy (untuk WH Main)

**Instead of full monthly count** (yang exhausting!), system should support **cycle count**:

```
CYCLE COUNT APPROACH
════════════════════════════════════════════════════════════

Principle: Count SMALL PORTION daily, complete all SKU dalam 1 bulan

Day 1: Count Category A (Fabric Red-tones) - 10 SKU
Day 2: Count Category B (Fabric Blue-tones) - 10 SKU
Day 3: Count Category C (Fabric Brown-tones) - 8 SKU
...
Day 30: Count Category Z (Carton) - 5 SKU

Result: 
├─ End of month → All SKU counted! (cumulative)
├─ Daily effort: LOW (30 menit/hari vs 8 jam full count!)
└─ Inventory accuracy: BETTER! (errors detected faster!)

System Requirement:
├─ Cycle count schedule (auto-generate daily task)
├─ Which SKU to count today? (system assign based on ABC classification)
├─ Track progress (bar graph: 80% SKU counted this month)
└─ Alert: "Cycle count behind schedule!" (if missed days)
```

### 9.3 Warehouse Transfer & Movement

#### 9.3.1 Material Issue (WH Main → Production Dept)

**2 Methods** (system harus support BOTH!):

**Method 1: Manual Issue (Traditional)**
```
Step 1: Production create Material Request (MR)
  ├─ Request by: Cutting SPV
  ├─ For: WO-Cutting-001
  ├─ Material: Fabric Type 1 Red - 45 YARD
  └─ Delivery to: WH-Cutting

Step 2: WH Main staff process request
  ├─ Pick material dari rak
  ├─ Update system: Issue 45 YARD fabric
  └─ Deliver to WH-Cutting (with delivery note)

Step 3: Cutting admin receive
  ├─ Check qty (match with delivery note?)
  ├─ Confirm receipt di system
  └─ Stock update:
      ├─ WH Main: -45 YARD
      └─ WH-Cutting: +45 YARD
```

**Method 2: Auto-Backflush (Pull System) ⚡ PREFERRED!**
```
Step 1: Material pre-allocated (when MO created)
  ├─ System read BOM
  ├─ Reserve materials di WH Main (for this MO)
  └─ Status: Reserved (not yet issued)

Step 2: Production start (Cutting dept)
  ├─ Cutting admin: Input start work
  └─ System: Auto-issue materials (paperless!)
      └─ No manual request needed!

Step 3: Production complete (Cutting dept)
  ├─ Cutting admin: Input output (495 pcs cut)
  └─ System: Auto-deduct materials based on BOM!
      ├─ Calculate: 495 pcs → 45 YARD fabric needed
      ├─ Stock update:
      │   ├─ WH Main Fabric: -45 YARD (auto!)
      │   └─ WH-Cutting Cut Pieces: +495 pcs (auto!)
      └─ No paperwork! Zero manual transaction! ⚡

Advantage:
├─ ✅ Paperless (no DN, no manual input!)
├─ ✅ Real-time (stock update immediate!)
├─ ✅ Accurate (based on BOM, no human error!)
└─ ✅ Efficient (admin focus on production, not paperwork!)
```

**System Requirement**:
- Support method 1 for **flexibility** (emergency situations)
- **DEFAULT to method 2** untuk normal operations (80% cases)
- Admin dapat **choose** method per transaction (system ask: "Manual issue OR Auto-backflush?")

#### 9.3.2 WIP Transfer (Between Departments)

**Transfer Types**:

```
TYPE A: PARTIAL BATCH TRANSFER (Most common!)
═════════════════════════════════════════════════════════════════
Context: Dept A selesaikan batch → Langsung transfer ke Dept B
Example: Cutting done 150 pcs (batch 1) → Transfer to Embroidery

Workflow:
├─ Dept A admin: Input production output (150 pcs batch 1)
├─ System: Auto-create Transfer Order (TO)
│   ├─ From: WH-Cutting
│   ├─ To: WH-Embroidery
│   ├─ Qty: 150 pcs
│   ├─ Status: In-Transit
│   └─ Batch ID: BATCH-001-SPK-123
├─ Physical transfer: Worker bawa dari Cutting ke Embroidery
├─ Dept B admin: Confirm receipt (scan barcode OR manual confirm)
└─ System: Update stock
    ├─ WH-Cutting: -150 pcs
    ├─ WH-Embroidery: +150 pcs
    └─ Dept B dapat mulai proses LANGSUNG! (no waiting full SPK!)

Timeline advantage:
├─ Traditional: Wait full SPK done (495 pcs) → Transfer → Dept B start
│   └─ Dept B idle time: 1-2 hari! (waiting dept A finish all)
└─ Partial batch: Transfer per batch → Dept B start immediate!
    └─ Dept B idle time: ZERO! (parallel processing!) ⚡


TYPE B: FULL SPK TRANSFER
═════════════════════════════════════════════════════════════════
Context: Transfer semua qty setelah full SPK completed
Example: Finishing done full 489 pcs → Transfer WH FG

Workflow: (Similar with Type A, but full qty)


TYPE C: REWORK LOOP TRANSFER
═════════════════════════════════════════════════════════════════
Context: QC reject → Send to Rework → Return setelah repair
Example: Sewing QC reject 25 pcs → Rework → Return to Sewing flow

Workflow:
├─ QC Inspector: Reject 25 pcs (input defect category)
├─ System: Create Transfer Order
│   ├─ From: WH-Sewing
│   ├─ To: WH-Rework (special location!)
│   └─ Tag: Defect category, reason, timestamp
├─ Rework team: Repair items
├─ Re-submit to QC: Re-inspection
├─ QC pass: Create return Transfer Order
│   ├─ From: WH-Rework
│   └─ To: WH-Sewing (rejoin normal flow!)
└─ System: Track rework cycle time (KPI!)
```

#### 9.3.3 FG Transfer to Warehouse FG

**Special Requirements** (karena FG = highest value!):

```
PACKING → WH FG TRANSFER WORKFLOW
═════════════════════════════════════════════════════════════════

Step 1: Packing Complete
─────────────────────────────────────────────────────────────
├─ Packing admin: Complete packing task
├─ Output:
│   ├─ 8 cartons (each 60 pcs) = 480 pcs total
│   └─ Each carton printed barcode label
└─ System: Generate FG barcode (per carton)

Step 2: QC Final Inspection (QC4)
─────────────────────────────────────────────────────────────
├─ QC Inspector: Scan each carton
│   ├─ Metal detector test: PASS ✅
│   ├─ Weight check: Within tolerance ✅
│   ├─ Barcode scan: Readable ✅
│   └─ Visual inspection: OK ✅
├─ System: Record QC result per carton
└─ QC approve: All cartons PASS → Proceed transfer

Step 3: Pallet Assembly
─────────────────────────────────────────────────────────────
├─ WH FG staff: Prepare pallet
├─ Load 8 cartons to 1 pallet
├─ System: Generate Pallet ID (unique barcode)
│   └─ Example: PLT-W05-2026-BEL-AFTONSPARV-001
│       ├─ Week: W05-2026
│       ├─ Destination: Belgium (BEL)
│       ├─ Article: AFTONSPARV
│       └─ Sequence: 001
└─ Print pallet label → Attach to pallet

Step 4: Transfer Execution
─────────────────────────────────────────────────────────────
├─ System: Create Transfer Order (TO-FG)
│   ├─ From: WH-Packing
│   ├─ To: WH FG
│   ├─ Pallet ID: PLT-W05-2026-BEL-AFTONSPARV-001
│   ├─ Cartons: 8 cartons (detail list)
│   ├─ Total qty: 480 pcs
│   ├─ Week: W05-2026 (from MO)
│   ├─ Destination: Belgium (from MO)
│   └─ Article: AFTONSPARV Bear 40cm
├─ Physical move: Forklift pallet ke WH FG area
├─ WH FG staff: Scan pallet barcode
│   └─ System: Confirm receipt (auto-update stock!)
└─ Place pallet: Designated location per Week+Destination

Step 5: Stock Update & Location
─────────────────────────────────────────────────────────────
├─ System update:
│   ├─ WH-Packing: -480 pcs (stock OUT)
│   └─ WH FG: +480 pcs (stock IN)
├─ Location tracking:
│   └─ PLT-W05-2026-BEL-AFTONSPARV-001 → Location A15
│       (Row A, Column 15)
└─ System dashboard update (real-time!):
    └─ FG Stock by Week:
        └─ W05-2026: 2,450 pcs (before) → 2,930pcs (after)
```

**Pallet Organization Logic** (critical untuk fast picking!):

```
WH FG LAYOUT & ORGANIZATION
═════════════════════════════════════════════════════════════════

ZONE 1: By Week (Primary grouping)
├─ Section W04-2026 (already finished, ready ship soon)
├─ Section W05-2026 (filling up, active production)
├─ Section W06-2026 (just started)
└─ Section W07-2026 (future)

ZONE 2: By Destination (within each week)
├─ W05-Belgium (pallets for Belgium)
├─ W05-Sweden (pallets for Sweden)
├─ W05-USA (pallets for USA)
└─ W05-China (pallets for China)

ZONE 3: By Article (within each destination)
├─ W05-Belgium-AFTONSPARV
├─ W05-Belgium-DJUNGELSKOG
└─ W05-Belgium-KRAMIG

Result:
├─ Fast picking untuk shipment preparation!
├─ Visual management (clear zone boundaries)
├─ Stock opname easier (count per zone!)
└─ FIFO implementation (older week shipped first!)

System visualization:
[Dashboard - FG Warehouse Map]
┌────────────────────────────────────────────────────┐
│  W04      W05        W06         W07               │
│  ╔═══╗   ╔═══╗     ╔═══╗       ╔═══╗             │
│  ║BEL║   ║BEL║     ║BEL║       ║   ║             │
│  ║SWE║   ║SWE║     ║   ║       ║   ║             │
│  ║USA║   ║USA║     ║   ║       ║   ║             │
│  ╚═══╝   ╚═══╝     ╚═══╝       ╚═══╝             │
│  Ready   Active    Started     Future             │
└────────────────────────────────────────────────────┘

Click each box → Detail list of pallets in that zone!
```

---

<a name="section-10"></a>
## ✅ 10. QUALITY CONTROL PROCESS

### 10.1 QC Philosophy & Objectives

**Quality Vision**: "Defect Prevention > Defect Detection > Defect Correction"

### 10.2 4-Checkpoint QC System (Already explained in Section 7.5)

*[Refer to Section 7.5 for detailed QC checkpoints]*

### 10.3 Defect Categorization & Root Cause

**Defect Categories** (system must support standard categories + custom):

```
DEFECT TAXONOMY
═════════════════════════════════════════════════════════════════

LEVEL 1: MAJOR CATEGORY
├─ [A] Material Defect
├─ [B] Process Defect
├─ [C] Assembly Defect
├─ [D] Dimension Defect
├─ [E] Appearance Defect
└─ [F] Safety/Compliance Defect

LEVEL 2: SUB-CATEGORY (per major category)

[A] Material Defect:
    ├─ A1: Fabric quality (pilling, color difference, tears)
    ├─ A2: Thread quality (break easily, wrong color)
    ├─ A3: Filling quality (lumpy, insufficient, contamination)
    ├─ A4: Accessories quality (broken eyes, wrong size)
    └─ A5: Label/Packaging defect (wrong info, print unclear)

[B] Process Defect:
    ├─ B1: Cutting defect (wrong size, asymmetric)
    ├─ B2: Embroidery defect (misalignment, skip stitch)
    ├─ B3: Sewing defect (loose stitch, jumping stitch, wrong seam)
    ├─ B4: Stuffing defect (uneven, too hard/soft)
    └─ B5: Closing defect (hole not closed properly)

[C] Assembly Defect:
    ├─ C1: Missing piece/component
    ├─ C2: Wrong piece attached
    ├─ C3: Assembly sequence error
    └─ C4: Loose attachment (easy fall off)

[D] Dimension Defect:
    ├─ D1: Undersized (smaller than spec)
    ├─ D2: Oversized (larger than spec)
    └─ D3: Asymmetric (left ≠ right)

[E] Appearance Defect:
    ├─ E1: Stain/dirt
    ├─ E2: Color difference (not match spec)
    ├─ E3: Loose threads (not trimmed)
    └─ E4: Wrinkled/crushed

[F] Safety/Compliance Defect: ← MOST CRITICAL!
    ├─ F1: Sharp parts (safety hazard!)
    ├─ F2: Metal detector fail (contain metal!)
    ├─ F3: Loose small parts (choking hazard!)
    └─ F4: Non-compliance material (not certified)

LEVEL 3: ROOT CAUSE (for analysis)
├─ RC1: Operator skill (training needed)
├─ RC2: Machine/tool issue (maintenance needed)
├─ RC3: Material quality from supplier
├─ RC4: Process/method issue (SOP need improvement)
├─ RC5: Design issue (product design flaw)
└─ RC6: Workload/fatigue (too fast, overtime)
```

**Defect Recording Workflow**:

```
QC INSPECTION & DEFECT RECORDING
═════════════════════════════════════════════════════════════════

Step 1: QC Inspector perform inspection
  ├─ Check unit (visual, dimension, weight, etc)
  └─ Result: PASS or DEFECT detected

Step 2: If DEFECT → Record immediately
  ├─ System interface: QC Inspection Form
  ├─ Input required:
  │   ├─ Defect category (Level 1 dropdown)
  │   ├─ Sub-category (Level 2 dropdown)
  │   ├─ Description (free text, detail issue)
  │   ├─ Photo (attach jika perlu!)
  │   ├─ Severity:
  │   │   ├─ MINOR (cosmetic, can rework)
  │   │   ├─ MAJOR (functional issue, must rework)
  │   │   └─ CRITICAL (safety issue, must scrap!)
  │   ├─ Disposition:
  │   │   ├─ REWORK (send to rework queue)
  │   │   └─ SCRAP (reject, record waste)
  │   └─ Root cause (RC dropdown - initial guess)
  ├─ Timestamp: Auto-recorded
  └─ QC Inspector ID: Auto-logged

Step 3: System auto-action
  ├─ Create Defect Record (unique ID)
  ├─ Update statistics:
  │   ├─ Defect rate today: +1
  │   ├─ Category A1 count: +1
  │   └─ QC2 checkpoint defect: +1
  ├─ If disposition = REWORK:
  │   └─ Create Work Order Rework (WO-RW)
  │       ├─ Assign to: Rework queue
  │       ├─ Priority: Based on severity
  │       └─ Status: Waiting rework
  └─ If disposition = SCRAP:
      └─ Record material loss (for costing)

Step 4: Weekly review (continuous improvement!)
  ├─ Manager: Review defect dashboard
  ├─ Identify top 3 defect categories (Pareto analysis)
  ├─ Root cause deep dive (why happening?)
  └─ Action plan:
      ├─ Training (if RC1)
      ├─ Maintenance (if RC2)
      ├─ Supplier feedback (if RC3)
      └─ SOP update (if RC4)
```

### 10.4 Rework Management (Already explained in Section 7.5)

*[Refer to Section 7.5 for Rework Workflow detail]*

### 10.5 Quality KPIs & Dashboard

**System must provide real-time quality dashboard**:

```
QUALITY DASHBOARD (Manager View)
═════════════════════════════════════════════════════════════════

[TODAY'S QUALITY SNAPSHOT]
┌──────────────────────────────────────────────────────────────┐
│ QC1 (Cutting)      │ Inspected: 1,245 pcs │ Pass: 97.2% ✅   │
│ QC2 (Sewing)       │ Inspected: 987 pcs   │ Pass: 87.5% ⚠️  │
│ QC3 (Finishing)    │ Inspected: 1,123 pcs │ Pass: 98.8% ✅   │
│ QC4 (Final)        │ Inspected: 1,058 pcs │ Pass: 99.3% ✅   │
└──────────────────────────────────────────────────────────────┘

[REWORK QUEUE STATUS]
┌──────────────────────────────────────────────────────────────┐
│ Waiting Rework: 45 pcs   │ In Rework: 12 pcs               │
│ Re-Inspection: 8 pcs      │ Recovered: 38 pcs (84%) ✅      │
│ Avg Rework Time: 25 min   │ Recovery Rate: 84% (Target:80%)│
└──────────────────────────────────────────────────────────────┘

[TOP 3 DEFECT CATEGORIES (This Week)]
┌──────────────────────────────────────────────────────────────┐
│ 1. [B3] Sewing Defect - Loose Stitch    │ 127 cases (42%)  │
│ 2. [E3] Appearance - Loose Threads       │  58 cases (19%)  │
│ 3. [C1] Assembly - Missing Piece         │  34 cases (11%)  │
└──────────────────────────────────────────────────────────────┘
Action Plan:
  ├─ B3: Schedule training for sewing team (next Monday)
  ├─ E3: Implement trimming checkpoint (before QC)
  └─ C1: Update checklist (visual aid on workstation)

[DEFECT TREND (Last 4 Weeks)]
┌──────────────────────────────────────────────────────────────┐
│  %  │                                                        │
│ 100 │                                                        │
│  95 │        ██████  ✅ QC Target Line (95%)                │
│  90 │    ▓▓  ██████  ██████                                 │
│  85 │▒▒▒▒▓▓▓▓██████▓▓██████                                 │
│  80 │────────────────────────────                           │
│     │  W02   W03     W04     W05  (Week)                    │
└──────────────────────────────────────────────────────────────┘
Trend: IMPROVING! ✅ (Week 2: 82% → Week 5: 91%)

[ROOT CAUSE DISTRIBUTION]
┌──────────────────────────────────────────────────────────────┐
│ RC1 - Operator Skill       │ ████████████░░░░ 38%           │
│ RC2 - Machine Issue        │ ██████░░░░░░░░░░ 18%           │
│ RC3 - Material Quality     │ ████████░░░░░░░░ 25%           │
│ RC4 - Process/SOP Issue    │ ████░░░░░░░░░░░░ 12%           │
│ RC6 - Workload/Fatigue     │ ██░░░░░░░░░░░░░░  7%           │
└──────────────────────────────────────────────────────────────┘
Action Focus: RC1 (Training!) + RC3 (Supplier quality feedback!)
```

---

<a name="section-11"></a>
## ⭐ 11. 7 BUSINESS REQUIREMENTS UNIK (CORE CUSTOMIZATION!)

**🔴 CRITICAL SECTION**: Ini adalah **JANTUNG** dari requirements kami yang membedakan soft toys manufacturing dengan manufacturing standar. **Semua 7 requirements ini TIDAK ADA di standard ERP** dan membutuhkan customization atau configuration advanced!

### 11.1 Overview Unique Requirements

| No | Requirement Name | Complexity | Standard ERP Support? | Customization Level |
|----|------------------|------------|----------------------|---------------------|
| **1** | **Dual Purchase Order Trigger System** | 🔴 HIGH | ❌ NO | HEAVY (Core logic change) |
| **2** | **Flexible Production Target per Department** | 🟠 MEDIUM-HIGH | ❌ NO | MEDIUM (Logic + UI) |
| **3** | **2-Stage Finishing Internal Conversion** | 🟡 MEDIUM | ⚠️ PARTIAL | MEDIUM (Warehouse config) |
| **4** | **Multi-Unit Conversion & Auto-Validation** | 🟡 MEDIUM | ⚠️ PARTIAL | LIGHT-MEDIUM (Validation rules) |
| **5** | **Real-Time WIP Tracking & Partial Transfer** | 🟠 MEDIUM-HIGH | ⚠️ PARTIAL | MEDIUM (Workflow change) |
| **6** | **Rework/Repair Module with QC Integration** | 🟡 MEDIUM | ⚠️ PARTIAL | MEDIUM (Module development) |
| **7** | **Department-Level Warehouse & Stock Opname** | 🟢 LOW-MEDIUM | ✅ YES | LIGHT (Configuration) |

**Assessment Questions untuk Sales Odoo**:
1. Dari 7 requirements ini, mana yang **sudah ada di Odoo standard** (with configuration only)?
2. Mana yang butuh **minor customization** (< 40 development hours)?
3. Mana yang butuh **major customization** (> 40 development hours)?
4. Apakah ada requirements yang **not feasible** dengan Odoo architecture?
5. Ada **alternative approach** yang lebih efisien tetapi achieve business goal yang sama?

---

### <a name="section-11-1"></a>11.1 Requirement #1: Dual Purchase Order Trigger System ⭐⭐⭐

**Priority**: 🔴 **CRITICAL** (Highest customization complexity!)  
**Business Impact**: **SANGAT TINGGI** (menghemat 5-7 hari lead time!)  
**Standard ERP Support**: ❌ **NONE** (completely custom logic!)

---

#### 11.1.1 Business Context & Problem Statement

**Current Pain Point** (Manual System):
```
TRADITIONAL APPROACH (Sequential - SLOW!):
═══════════════════════════════════════════════════════════════
Timeline:
├─ Day 0: Customer order received
├─ Day 0-2: Wait semua PO approved (Fabric + Label + Accessories)
├─ Day 3-10: Wait ALL materials arrived (longest: Label 10 hari!)
├─ Day 10: Semua material ready → START production
└─ Day 28: Production done (18 hari production cycle)

Total Lead Time: 28 days ❌ (TOO LONG! Customer expect <20 hari!)

PROBLEM:
- Cutting & Embroidery bisa start EARLY (cuma butuh fabric!)
- Tapi WAITING label (yang tidak diperlukan sampai stage Finishing!)
- WASTED TIME: 7 hari idle! (Waiting label yang belum perlu!)
```

**Business Need**:
> **"Kami ingin CUTTING & EMBROIDERY bisa START lebih awal (segera setelah fabric datang), tidak perlu tunggu label. Tapi sistem harus ENSURE label must arrive sebelum Finishing stage, dan Week/Destination dari label harus AUTO-LOCK ke production order agar tidak ada kesalahan!"**

---

#### 11.1.2 Solution Requirements: Dual Trigger System

**Concept**: 2 Purchase Orders **sequentially unlock** production departments

**TRIGGER LOGIC**:

```
STATE MACHINE: Manufacturing Order (MO)
═══════════════════════════════════════════════════════════════

STATE 1: DRAFT (Initial)
───────────────────────────────────────────────────────────────
├─ Status: MO not yet created
├─ Condition: Customer order received, not yet actioned
└─ Departments: ALL LOCKED 🔒

        │
        │ [EVENT: PO FABRIC CREATED] ← TRIGGER 1!
        ↓

STATE 2: PARTIAL (Early Start Allowed!)
───────────────────────────────────────────────────────────────
├─ Status: MO created, partial release
├─ Departments unlocked:
│   ├─ Cutting: ✅ UNLOCKED (can start when fabric arrive!)
│   ├─ Embroidery: ✅ UNLOCKED (can start after cutting!)
│   └─ Sewing-onwards: 🔒 LOCKED (waiting PO Label!)
├─ Fields:
│   ├─ Week: "TBD" (to be determined from PO Label)
│   ├─ Destination: "TBD" (to be determined from PO Label)
│   └─ Status: "PARTIAL - Waiting Label PO"
└─ Alert:
    └─ "⚠️ PO LABEL PENDING! Sewing-onwards blocked until label PO created!"

        │
        │ [EVENT: PO LABEL CREATED] ← TRIGGER 2!
        ↓

STATE 3: RELEASED (Full Production Enabled!)
───────────────────────────────────────────────────────────────
├─ Status: MO fully released
├─ Departments unlocked:
│   ├─ Cutting: ✅ (already unlocked)
│   ├─ Embroidery: ✅ (already unlocked)
│   ├─ Sewing: ✅ UNLOCKED NOW!
│   ├─ Finishing: ✅ UNLOCKED NOW!
│   └─ Packing: ✅ UNLOCKED NOW!
├─ Fields AUTO-UPDATE:
│   ├─ Week: "TBD" → **"W05-2026"** (from PO Label!) 🔐
│   ├─ Destination: "TBD" → **"Belgium"** (from PO Label!) 🔐
│   ├─ Field Status: **READ-ONLY** (locked forever!)
│   └─ Status: "RELEASED - Full Production"
└─ Alert:
    └─ "✅ MO RELEASED! All departments can proceed. Week: W05-2026, Dest: Belgium"

        │
        │ [Production progress...]
        ↓

STATE 4: IN PROGRESS
───────────────────────────────────────────────────────────────
├─ Status: At least 1 department started work
└─ (Standard manufacturing flow...)

        │
        ↓

STATE 5: DONE
───────────────────────────────────────────────────────────────
├─ Status: All departments completed
└─ FG transferred to WH FG
```

---

#### 11.1.3 Detailed Functional Requirements

**FR-1.1: PO Fabric → Auto-Create MO (TRIGGER 1)**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
When: User (Purchasing A) creates PO Fabric untuk article X
Then: System must automatically:
  ├─ Create Manufacturing Order (MO) dengan:
  │   ├─ Product: {artikel dari PO}
  │   ├─ Quantity: {qty dari customer order}
  │   ├─ Week: "TBD" (editable = FALSE, waiting PO Label)
  │   ├─ Destination: "TBD" (editable = FALSE, waiting PO Label)
  │   ├─ State: PARTIAL
  │   └─ Reference: Link ke PO Fabric (for traceability)
  │
  ├─ Generate Work Orders (WO) untuk each department dari BOM routing
  │   ├─ WO-Cutting: State = Ready to Start (UNLOCKED)
  │   ├─ WO-Embroidery: State = Ready to Start (UNLOCKED if Route 1/3)
  │   └─ WO-Sewing-onwards: State = Waiting (LOCKED)
  │
  ├─ Notification:
  │   ├─ To: Purchasing B (Label specialist)
  │   │   └─ Subject: "Action Required: Create PO Label for MO-{number}"
  │   │   └─ Message: "MO created in PARTIAL state. Create PO Label to fully release production!"
  │   │
  │   └─ To: Cutting SPV
  │       └─ Subject: "New Work Order Ready"
  │       └─ Message: "WO-Cutting-{number} ready. Start when fabric arrives."
  │
  └─ Dashboard update: MO list show new MO dengan status "Partial - Pending Label"

BUSINESS RULES:
────────────────────────────────────────────────────────────────
- BR-1.1.1: 1 PO Fabric hanya bisa trigger 1 MO (one-to-one mapping)
- BR-1.1.2: Jika article sudah punya MO dengan state PARTIAL/RELEASED/IN PROGRESS
             → System WARNING: "MO already exists for this article! Check MO-{number}"
- BR-1.1.3: Jika BOM tidak ada untuk article → System BLOCK:
             "Cannot create MO: BOM not found for article {name}"
- BR-1.1.4: Field Week & Destination = "TBD" adalah text literal (temporary placeholder)

UI/UX REQUIREMENTS:
────────────────────────────────────────────────────────────────
- PO Fabric form: Add checkbox "✅ Trigger Production (Create MO)"
  └─ Default: Checked (auto trigger)
  └─ User can uncheck if exceptional case (tidak mau auto-create MO)

- After PO submitted:
  └─ Success message: "PO created successfully! MO-2026-001 auto-created (PARTIAL state)"
  └─ Provide link: "View MO" (click → Navigate to MO detail page)
```

**FR-1.2: PO Label → Auto-Upgrade MO to RELEASED + Lock Fields (TRIGGER 2)**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
When: User (Purchasing B) creates PO Label untuk article X
Then: System must automatically:
  ├─ Find related MO (by article reference)
  │   └─ Validation: MO must exist dengan state = PARTIAL
  │       ├─ If not exist → ERROR: "No MO found for this article! Create PO Fabric first."
  │       └─ If state ≠ PARTIAL → ERROR: "MO already released! Cannot process PO Label."
  │
  ├─ Extract data from PO Label:
  │   ├─ Week: {dari PO Label field "Week"}  
  │   │   └─ Example: "W05-2026"
  │   └─ Destination: {dari PO Label field "Destination"}
  │       └─ Example: "Belgium"
  │
  ├─ Update MO:
  │   ├─ Week: "TBD" → {Week dari PO Label} ✍️
  │   ├─ Destination: "TBD" → {Destination dari PO Label} ✍️
  │   ├─ State: PARTIAL → RELEASED ✍️
  │   ├─ Field editability: Week & Destination → READ-ONLY 🔒 (permanent lock!)
  │   └─ Reference: Link ke PO Label (for traceability)
  │
  ├─ Update related Work Orders:
  │   └─ WO-Sewing, WO-Finishing, WO-Packing:
  │       ├─ State: Waiting → Ready to Start (UNLOCKED!)
  │       ├─ Inherit Week & Destination dari MO (display di WO header)
  │       └─ Make visible di dept dashboard
  │
  ├─ Notification:
  │   ├─ To: All Production SPVs
  │   │   └─ "MO-{number} RELEASED! Week: {week}, Destination: {dest}. All departments can proceed."
  │   │
  │   ├─ To: Manager
  │   │   └─ "Production fully unlocked for MO-{number}. Monitor progress!"
  │   │
  │   └─ To: WH-Finishing staff
  │       └─ "Label PO created for MO-{number}. Expect label delivery on {date}."
  │
  └─ Dashboard update: MO status change from "Partial - Pending Label" → "Released"

BUSINESS RULES:
────────────────────────────────────────────────────────────────
- BR-1.2.1: Week format validation: Must match pattern "W##-####"
             └─ Example: W05-2026 ✅, W5-26 ❌, Week 05 ❌
- BR-1.2.2: Destination must be from predefined list (master data):
             └─ Belgium, Sweden, USA, China, France, Germany, etc.
             └─ Prevent typo: "Belgia" ❌, "Belgian" ❌
- BR-1.2.3: After Week & Destination locked → CANNOT edit via UI (no edit button!)
- BR-1.2.4: Change request process (jika TERPAKSA harus ubah):
             ├─ User submit "Change Request" (special form dengan justification)
             ├─ Approval: Manager + Director approval required
             ├─ System log: Record old value, new value, changed by, approved by, reason
             ├─ Impact check: System WARNING if production already started!
             │   └─ "⚠️ Changing Week/Dest may require RE-ORDER LABEL! Confirm?"
             └─ After approved: Unlock field → Allow edit → Re-lock

UI/UX REQUIREMENTS:
────────────────────────────────────────────────────────────────
- PO Label form:
  ├─ Field "Week": Dropdown (predefined list: W01-2026 s/d W52-2026) + Manual input
  ├─ Field "Destination": Dropdown (master data: country list)
  ├─ Help text: "⚠️ Week & Destination will be LOCKED in MO after PO submitted!"
  └─ Validation: Both fields MANDATORY (cannot submit if empty!)

- MO Detail view (after RELEASED):
  ├─ Show Week & Destination dengan 🔒 icon (visual indicator locked!)
  ├─ Tooltip on hover: "Field locked from PO Label. Submit Change Request to modify."
  └─ If not yet released: Show "TBD" dengan ⏳ icon + tooltip: "Waiting PO Label creation"
```

**FR-1.3: Department Access Control Based on MO State**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
System must control which departments can view/start Work Orders based on MO state:

MO State: DRAFT
────────────────────────────────────────────────────────────────
├─ ALL departments: 🔒 LOCKED
└─ Work Orders: Not yet created

MO State: PARTIAL
────────────────────────────────────────────────────────────────
├─ Cutting: ✅ UNLOCKED
│   ├─ Can view: WO-Cutting detail
│   ├─ Can start: Yes (when materials ready)
│   └─ Can input: Production output
│
├─ Embroidery: ✅ UNLOCKED (conditional - if Route 1 or 3)
│   ├─ Can view: WO-Embroidery detail
│   ├─ Can start: Yes (after receive from Cutting)
│   └─ Can input: Production output (internal) OR Vendor delivery (external)
│
└─ Sewing, Finishing, Packing: 🔒 LOCKED
    ├─ Can view: WO list only (minimal detail, greyed out)
    ├─ Can NOT start: Block with message:
    │   └─ "⚠️ This Work Order is LOCKED. Waiting PO Label creation for MO-{number}."
    └─ Can NOT input: Production form button DISABLED

MO State: RELEASED
────────────────────────────────────────────────────────────────
├─ ALL departments: ✅ UNLOCKED
├─ Can view: Full WO detail
├─ Can start: Yes (based on sequence - dept B after dept A output ready)
└─ Can input: Production output

DASHBOARD VISUALIZATION:
────────────────────────────────────────────────────────────────
[Work Order Dashboard - Cutting Dept View]
┌────────────────────────────────────────────────────────────┐
│ Active Work Orders                                         │
├────────────────────────────────────────────────────────────┤
│ WO-CUT-001 │ AFTONSPARV Bear │ 495 pcs │ ✅ UNLOCKED     │
│            │ Week: TBD        │ Status: Ready to Start   │
│            │ [START WORK] [VIEW DETAIL]                   │
├────────────────────────────────────────────────────────────┤
│ WO-CUT-002 │ DJUNGELSKOG     │ 520 pcs │ ✅ UNLOCKED     │
│            │ Week: W06-2026   │ Status: In Progress 45%  │
│            │ [INPUT PRODUCTION] [VIEW DETAIL]             │
└────────────────────────────────────────────────────────────┘

[Work Order Dashboard - Sewing Dept View - BEFORE RELEASED]
┌────────────────────────────────────────────────────────────┐
│ Upcoming Work Orders (Locked - Waiting Label PO)           │
├────────────────────────────────────────────────────────────┤
│ WO-SEW-001 │ AFTONSPARV Bear │ ?? pcs │ 🔒 LOCKED       │
│            │ Week: TBD        │ Status: Waiting Label PO │
│            │ Details unavailable until MO released        │
├────────────────────────────────────────────────────────────┤
│ WO-SEW-002 │ DJUNGELSKOG     │ 520pcs │ ✅ UNLOCKED     │
│            │ Week: W06-2026   │ Status: Ready to Start   │
│            │ [START WORK] [VIEW DETAIL]                   │
└────────────────────────────────────────────────────────────┘
```

**FR-1.4: Alert & Notification System**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
System must provide proactive alerts untuk monitor dual trigger status:

ALERT TYPE 1: PO Fabric Created (Reminder ke Purchasing B)
────────────────────────────────────────────────────────────────
├─ Trigger: PO Fabric submitted → MO created (state: PARTIAL)
├─ Send to: Purchasing B (Label specialist)
├─ Timing: Immediately after MO created
├─ Channel: Email + In-app notification
├─ Message:
│   Subject: "🔔 Action Required: Create PO Label for MO-2026-001"
│   Body: "
│   Hello {user_name},
│   
│   A new Manufacturing Order (MO-2026-001) has been created in PARTIAL state:
│   - Article: AFTONSPARV Bear 40cm
│   - Quantity: 450 pcs
│   - Customer Order: CO-2026-IKEA-123
│   
│   ACTION REQUIRED:
│   Please create PO Label to fully release this MO. Production departments
│   Sewing, Finishing, and Packing are currently LOCKED waiting for label PO.
│   
│   [CREATE PO LABEL NOW] (button → Navigate to PO Label creation form)
│   "
└─ Escalation: If not actioned dalam 3 hari → Notify Manager


ALERT TYPE 2: PO Label Delayed (Proactive Warning)
────────────────────────────────────────────────────────────────
├─ Trigger: MO state = PARTIAL for > 5 hari (configurable threshold)
├─ Send to: Purchasing B + Manager
├─ Timing: Daily check (automated job)
├─ Channel: Email + In-app notification
├─ Message:
│   Subject: "⚠️ URGENT: PO Label Delayed for MO-2026-001!"
│   Body: "
│   Manufacturing Order MO-2026-001 is STILL in PARTIAL state for 6 days!
│   
│   Risk:
│   - Cutting dept output will accumulate (WIP buildup!)
│   - Cannot proceed to Sewing (BLOCKED!)
│   - Delivery deadline at risk!
│   
│   ACTION: Create PO Label immediately or provide status update.
│   
│   [VIEW MO DETAIL] [CREATE PO LABEL]
│   "
└─ Persistence: Alert repeat setiap hari sampai PO Label created OR MO released


ALERT TYPE 3: MO Released Success (Confirmation)
────────────────────────────────────────────────────────────────
├─ Trigger: PO Label created → MO upgraded to RELEASED
├─ Send to: All Production SPVs + Manager + Purchasing A & B
├─ Timing: Immediately after state change
├─ Channel: Email + In-app notification + Dashboard popup
├─ Message:
│   Subject: "✅ MO-2026-001 RELEASED - Full Production Enabled"
│   Body: "
│   Manufacturing Order MO-2026-001 has been RELEASED:
│   
│   Details:
│   - Article: AFTONSPARV Bear 40cm
│   - Week: W05-2026 🔒 (LOCKED)
│   - Destination: Belgium 🔒 (LOCKED)
│   - Quantity: 450 pcs
│   
│   All production departments are now UNLOCKED. Please proceed with work orders.
│   
│   [VIEW MO DASHBOARD] [VIEW WORK ORDERS]
│   "
└─ Visibility: Dashboard banner show "🎉 1 New MO Released!" for 24 hours

DASHBOARD ALERT PANEL:
────────────────────────────────────────────────────────────────
[Manager Dashboard - Alerts Panel]
┌────────────────────────────────────────────────────────────┐
│ 🔴 URGENT ALERTS (2)                                       │
├────────────────────────────────────────────────────────────┤
│ ⚠️  MO-2026-001: PARTIAL for 6 days! (No PO Label yet)    │
│     Action: [REMIND PURCHASING B] [VIEW MO]               │
├────────────────────────────────────────────────────────────┤
│ ⚠️  MO-2026-015: Cutting done but Sewing still locked!    │
│     WIP accumulating: 485 pcs. [VIEW DETAILS]             │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ 🟡 WARNINGS (5)                                            │
├────────────────────────────────────────────────────────────┤
│ 📋  3 MOs in PARTIAL state (pending label PO)             │
│     [VIEW LIST]                                            │
└────────────────────────────────────────────────────────────┘
```

---

#### 11.1.4 Technical Specifications (untuk Developer Odoo)

**Data Model Extensions**:

```python
# Model: purchase.order (Extension)
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    # New fields
    is_fabric_po = fields.Boolean(
        string='Is Fabric PO',
        default=False,
        help='If True, this PO will trigger MO creation (PARTIAL state)'
    )
    is_label_po = fields.Boolean(
        string='Is Label PO',
        default=False,
        help='If True, this PO will upgrade related MO to RELEASED state'
    )
    related_mo_id = fields.Many2one(
        'mrp.production',
        string='Related Manufacturing Order',
        readonly=True,
        help='MO created/updated by this PO'
    )
    production_week = fields.Char(
        string='Production Week',
        help='Format: W##-####, e.g., W05-2026. For Label PO only.'
    )
    destination_country = fields.Many2one(
        'res.country',
        string='Destination Country',
        help='Destination for this production batch. For Label PO only.'
    )
    
    # Override method
    def button_confirm(self):
        """Override PO confirmation to trigger MO logic"""
        res = super().button_confirm()
        
        for po in self:
            if po.is_fabric_po:
                # TRIGGER 1: Create MO in PARTIAL state
                po._create_manufacturing_order_partial()
                
            elif po.is_label_po:
                # TRIGGER 2: Upgrade MO to RELEASED state
                po._upgrade_manufacturing_order_released()
        
        return res
    
    def _create_manufacturing_order_partial(self):
        """Create MO in PARTIAL state (TRIGGER 1)"""
        # Implementation logic...
        
    def _upgrade_manufacturing_order_released(self):
        """Upgrade MO to RELEASED state + lock fields (TRIGGER 2)"""
        # Implementation logic...


# Model: mrp.production (Extension)
class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    # New states (extend standard state selection)
    state = fields.Selection(
        selection_add=[
            ('partial', 'Partial Release'),  # New state after TRIGGER 1
        ],
        ondelete={'partial': 'set default'}
    )
    
    # New fields
    production_week = fields.Char(
        string='Production Week',
        compute='_compute_week_readonly',
        store=True,
        readonly=True,  # Locked after PO Label!
        help='Auto-populated from Label PO. Format: W##-####'
    )
    destination_country_id = fields.Many2one(
        'res.country',
        string='Destination',
        compute='_compute_destination_readonly',
        store=True,
        readonly=True,  # Locked after PO Label!
        help='Auto-populated from Label PO.'
    )
    fabric_po_id = fields.Many2one(
        'purchase.order',
        string='Fabric PO (Trigger 1)',
        readonly=True
    )
    label_po_id = fields.Many2one(
        'purchase.order',
        string='Label PO (Trigger 2)',
        readonly=True
    )
    is_week_destination_locked = fields.Boolean(
        string='Week/Destination Locked',
        default=False,
        help='True after Label PO created (fields become read-only)'
    )
    days_in_partial_state = fields.Integer(
        string='Days in Partial State',
        compute='_compute_days_in_partial',
        help='For alert system: Track how long MO stuck in PARTIAL'
    )
    
    @api.depends('label_po_id', 'label_po_id.production_week')
    def _compute_week_readonly(self):
        """Compute production week from Label PO"""
        for mo in self:
            if mo.label_po_id and mo.label_po_id.production_week:
                mo.production_week = mo.label_po_id.production_week
            elif not mo.is_week_destination_locked:
                mo.production_week = 'TBD'  # Placeholder
    
    # ... (similar for destination)
    
    def action_request_week_destination_change(self):
        """Special action: Request change to locked fields"""
        # Open wizard for change request with justification
        # Trigger approval workflow
        pass


# Model: mrp.workorder (Extension)
class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    # New field
    is_unlocked = fields.Boolean(
        string='Unlocked for Production',
        compute='_compute_is_unlocked',
        store=True,
        help='Depends on MO state and department routing'
    )
    
    @api.depends('production_id.state', 'operation_id')
    def _compute_is_unlocked(self):
        """Compute if WO is unlocked based on MO state & dept"""
        for wo in self:
            mo_state = wo.production_id.state
            dept = wo.operation_id.workcenter_id.department_id  # Assume workcenter linked to dept
            
            if mo_state == 'partial':
                # Unlock only Cutting & Embroidery
                wo.is_unlocked = dept.code in ['CUTTING', 'EMBROIDERY']
            elif mo_state in ['released', 'progress', 'to_close', 'done']:
                # Unlock all departments
                wo.is_unlocked = True
            else:
                wo.is_unlocked = False
    
    def button_start(self):
        """Override start button to check if WO is unlocked"""
        self.ensure_one()
        if not self.is_unlocked:
            raise UserError(_(
                'This Work Order is LOCKED!\n\n'
                'Reason: Manufacturing Order %s is in PARTIAL state.\n'
                'Action Required: Create Label PO to unlock all departments.'
            ) % self.production_id.name)
        
        return super().button_start()
```

**Workflow Implementation Notes**:

1. **Server Action** (automated):
   - Scheduled job: Daily check MOs in PARTIAL state > 5 days → Send alert email
   - On PO confirm: Trigger `button_confirm` override → Execute TRIGGER 1 or 2 logic

2. **Security/Access Rights**:
   - `mrp.production.week_destination_locked`: Only Manager can access change request
   - Work Order view: Dynamic show/hide START button based on `is_unlocked` field

3. **UI/UX Customizations**:
   - MO Form view: Show 🔒 icon next to Week & Destination fields if locked
   - PO Form view: Add checkbox "Trigger Production?" (for Fabric PO)
   - Dashboard: Custom kanban view with state colors (PARTIAL = Orange, RELEASED = Green)

---

#### 11.1.5 Business Value & Impact

**Quantitative Benefits**:

| Metric | Before (Sequential) | After (Dual Trigger) | Improvement |
|--------|---------------------|----------------------|-------------|
| **Lead Time** | 28 hari | 18-20 hari | **-29% to -36%** ⚡ |
| **Cutting Start Time** | Day 10 (wait all materials) | Day 3-5 (fabric arrive) | **-5 to -7 hari earlier!** |
| **WIP Idle Time** | 7 hari (wait label) | 0 hari (parallel processing) | **Eliminate idle time!** |
| **Customer Satisfaction** | Delivery delay 25% cases | On-time delivery 95%+ | **+70% improvement!** |

**Qualitative Benefits**:
- ✅ **Flexibility**: Dapat respond FASTER ke customer order
- ✅ **Risk Mitigation**: Label delay tidak block seluruh production
- ✅ **Capacity Utilization**: Cutting & Embroidery running lebih awal → Better capacity usage
- ✅ **Visibility**: Manager tahu exact status (PARTIAL vs RELEASED) → Better planning

**Risk if NOT implemented**:
- ❌ Lead time tetap panjang (28 hari vs competitor 18-20 hari) → **Loss competitive advantage!**
- ❌ Cutting & Embroidery team **idle** 5-7 hari (waiting label yang tidak perlu early) → **Wasted labor cost!**
- ❌ Cannot achieve IKEA delivery target (95% OTD) → **Penalty & Risk de-listing!**

---

### <a name="section-11-2"></a>11.2 Requirement #2: Flexible Production Target per Department

**Priority**: 🟠 **HIGH**  
**Business Impact**: **HIGH** (prevent shortage, reduce waste)  
**Standard ERP Support**: ❌ **MINIMAL** (MO target = fixed untuk all dept!)

---

#### 11.2.1 Business Context & Problem Statement

**Current Pain Point**:
```
TRADITIONAL MO TARGET (Rigid - PROBLEMATIC!):
═══════════════════════════════════════════════════════════════
Customer Order: 450 pcs AFTONSPARV Bear

Standard ERP logic:
├─ MO Target: 450 pcs (same untuk SEMUA departemen!)
└─ Department execution:
    ├─ Cutting: Target 450 pcs → Output 445 pcs (5 pcs defect)
    ├─ Sewing: Target 450 pcs → Input 445 pcs only (short 5 pcs!)
    │   └─ Output: 378 pcs (67 pcs defect - 15% reject rate!)
    └─ Finishing: Target 450 pcs → Input 378 pcs only (short 72 pcs!)
        └─ Customer order 450 pcs → SHORTAGE 72 pcs! ❌❌❌

PROBLEM:
- Defect rate UNPREDICTABLE (vary by batch, material, admin skill)
- Rigid target = INSUFFICIENT buffer → Frequent shortage!
- Emergency re-run production → Delay + Extra cost!
```

**Business Need**:
> **"Kami butuh FLEXIBLE TARGET per department dengan intelligent buffer calculation. Jika Sewing historical defect 12%, maka Sewing target harus 450 / (1 - 0.12) = 511 pcs. Tapi system harus ENFORCE constraint: Sewing target TIDAK BOLEH > Cutting output!"**

---

#### 11.2.2 Solution Requirements: Flexible Target System

**Concept**: Setiap department punya **target sendiri** yang calculated dengan buffer, with constraint validation

**CALCULATION LOGIC**:

```
FLEXIBLE TARGET CALCULATION
═══════════════════════════════════════════════════════════════

Given:
├─ Customer Order Qty: 450 pcs
├─ Historical Defect Rate per Dept (3-month average):
│   ├─ Cutting: 3%
│   ├─ Embroidery: 2%
│   ├─ Sewing: 12% ← HIGHEST DEFECT!
│   ├─ Stuffing (Finishing-1): 2%
│   ├─ Closing (Finishing-2): 1%
│   └─ Packing: 0.5%
└─ Manual Buffer Adjustment (Optional): Manager can override

Calculation Formula per Department:
────────────────────────────────────────────────────────────────
Target_Dept_A = Customer_Qty / (1 - Defect_Rate_Dept_A) × (1 + Manual_Buffer_A)

Example Calculation:
────────────────────────────────────────────────────────────────
CUSTOMER ORDER: 450 pcs

Step 1: REVERSE CALCULATION (from Packing backwards to Cutting)
─────────────────────────────────────────────────────────────────
Packing (Last Dept):
  Formula: 450 / (1 - 0.005) = 452 pcs
  Target: 452 pcs (output must be ≥ 450 pcs customer order)

Closing (Finishing-2):
  Formula: 452 / (1 - 0.01) = 457 pcs
  Target: 457 pcs (output must be ≥ 452 pcs to feed Packing)

Stuffing (Finishing-1):
  Formula: 457 / (1 - 0.02) = 466 pcs
  Target: 466 pcs

Sewing:
  Formula: 466 / (1 - 0.12) = 530 pcs ← HIGHEST TARGET! (biggest buffer)
  Target: 530 pcs

Embroidery:
  Formula: 530 / (1 - 0.02) = 541 pcs
  Target: 541 pcs

Cutting (First Dept):
  Formula: 541 / (1 - 0.03) + 20 pcs (manual buffer) = 578 pcs
  Target: 578 pcs (raw material consumption based on this!)


RESULT TARGET per DEPARTMENT:
═══════════════════════════════════════════════════════════════
│ Department    │ Target │ Buffer Calculation                │
├───────────────┼────────┼───────────────────────────────────┤
│ Cutting       │ 578    │ +128 pcs (+28% from customer)     │
│ Embroidery    │ 541    │ +91 pcs (+20%)                    │
│ Sewing        │ 530    │ +80 pcs (+18%) ← High risk dept!  │
│ Stuffing      │ 466    │ +16 pcs (+3.5%)                   │
│ Closing       │ 457    │ +7 pcs (+1.5%)                    │
│ Packing       │ 452    │ +2 pcs (+0.4%)                    │
│ **CUSTOMER**  │**450** │ **Final delivery qty**            │
└───────────────┴────────┴───────────────────────────────────┘
```

**CONSTRAINT VALIDATION LOGIC**:

```
CONSTRAINT RULES (Prevent Impossible Targets!):
═══════════════════════════════════════════════════════════════

Rule 1: Department B Target ≤ Output Department A (Previous Dept)
────────────────────────────────────────────────────────────────
Logic:
  If Target_Dept_B > Actual_Output_Dept_A:
    → BLOCK Dept B from starting!
    → Alert: "Insufficient WIP from Dept A. Wait for more output."

Example:
  ├─ Cutting Target: 578 pcs → Actual Output: 520 pcs (not yet done)
  ├─ Embroidery Target: 541 pcs
  └─ Validation: 541 > 520 → ⚠️ WARNING!
      └─ "Embroidery target (541 pcs) exceeds Cutting current output (520 pcs).
          You can START with available qty (520 pcs), or WAIT for Cutting to complete."

Rule 2: Real-Time Adjustment (if Dept A defect higher than expected)
────────────────────────────────────────────────────────────────
Logic:
  If Actual_Defect_Rate_Dept_A > Historical_Defect_Rate + 5%:
    → Trigger RE-CALCULATION downstream targets
    → Notify Manager: "High defect detected! Targets auto-adjusted."

Example:
  ├─ Cutting Target: 578 pcs → Actual Output: 490 pcs (defect 15%! Higher than expected 3%!)
  ├─ System detect: 490 pcs < 541 pcs (Embroidery target) → PROBLEM!
  └─ System Action:
      ├─ Auto-adjust Embroidery target: 541 → 490 pcs (match actual Cutting output)
      ├─ Recalculate downstream: Sewing 530 → 479 pcs, etc.
      ├─ Alert Manager: "⚠️ Cutting high defect (15%!) caused target adjustment!"
      └─ Recommendation: "Consider emergency re-run Cutting to fulfill original customer order."

Rule 3: Manager Override (Emergency Manual Adjustment)
────────────────────────────────────────────────────────────────
Logic:
  Manager can MANUALLY override target per department (with justification)

Example:
  ├─ Manager see: Sewing output looking good (low defect this batch!)
  ├─ Decision: Reduce Cutting target 578 → 550 pcs (save material!)
  └─ System:
      ├─ Log: "Target changed by {manager_name}: 578 → 550 pcs. Reason: {justification}"
      ├─ Recalculate: Material consumption reduced (save fabric!)
      └─ Alert departments: "Target updated. New Cutting target: 550 pcs."
```

---

#### 11.2.3 Detailed Functional Requirements

**FR-2.1: Auto-Calculate Target per Department (when MO created)**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
When: MO created (manual OR via TRIGGER 1 from PO Fabric)
Then: System must automatically calculate target per department

Input Data needed:
├─ Customer order qty: 450 pcs
├─ BOM with routing (list of departments & sequence)
├─ Historical defect rate per department (from Quality module data)
│   └─ Source: Average defect% last 3 months per department + article category
└─ Manual buffer % (config per department - optional)

Calculation Process:
├─ Step 1: Read BOM routing → Get department sequence
│   └─ Example: Cutting → Embroidery → Sewing → Stuffing → Closing → Packing
│
├─ Step 2: REVERSE iteration (from last dept to first dept)
│   └─ Starting point: Customer qty (450 pcs)
│   └─ For each dept D (from last to first):
│       ├─ Get defect_rate_D from historical data
│       ├─ Get manual_buffer_D from config (default: 0)
│       ├─ Calculate: Target_D = Required_Input_D / (1 - defect_rate_D) × (1 + manual_buffer_D)
│       └─ Set Required_Input_(D-1) = Target_D (chain calculation!)
│
├─ Step 3: Create Work Order per department dengan calculated target
│   └─ WO-Cutting: Target 578 pcs
│       WO-Embroidery: Target 541 pcs
│       WO-Sewing: Target 530 pcs
│       ... (dst)
│
└─ Step 4: Store calculation log (for audit & analysis)
    └─ Table: mo_target_calculation_log
        ├─ MO ID
        ├─ Department
        ├─ Customer qty
        ├─ Historical defect%
        ├─ Manual buffer%
        ├─ Calculated target
        └─ Timestamp

UI Display (MO Detail View):
────────────────────────────────────────────────────────────────
[Manufacturing Order MO-2026-001]
┌────────────────────────────────────────────────────────────┐
│ Product: AFTONSPARV Bear 40cm                              │
│ Customer Qty: 450 pcs                                      │
│ Week: W05-2026 │ Destination: Belgium                      │
└────────────────────────────────────────────────────────────┘

[Department Targets - Flexible Buffer System]
┌─────────────┬────────┬─────────┬────────────┬─────────────┐
│ Department  │ Target │ Defect% │ Buffer pcs │ Status      │
├─────────────┼────────┼─────────┼────────────┼─────────────┤
│ Cutting     │  578   │  3.0%   │  +128      │ In Progress │
│ Embroidery  │  541   │  2.0%   │  +91       │ Ready       │
│ Sewing      │  530   │ 12.0% ⚠️│  +80       │ Waiting     │
│ Stuffing    │  466   │  2.0%   │  +16       │ Waiting     │
│ Closing     │  457   │  1.0%   │  +7        │ Waiting     │
│ Packing     │  452   │  0.5%   │  +2        │ Waiting     │
├─────────────┼────────┼─────────┼────────────┼─────────────┤
│ **Customer**│**450** │         │ Delivery   │ Pending     │
└─────────────┴────────┴─────────┴────────────┴─────────────┘

[Actions]
[📊 View Calculation Detail] [✏️ Adjust Targets (Manager only)]

Click "View Calculation Detail" → Show formula per dept
Click "Adjust Targets" → Open wizard untuk manual override
```

**FR-2.2: Real-Time Constraint Validation (Before Dept B Start)**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
When: User (Dept B) attempts to START work order
Then: System must validate constraint BEFORE allowing start

Validation Logic:
├─ Check: Does previous dept (Dept A) provide sufficient output?
│   └─ Constraint: Target_Dept_B ≤ Actual_Output_Dept_A
│
├─ If PASS:
│   └─ Allow start work order (normal flow)
│
└─ If FAIL:
    ├─ Show WARNING dialog:
    │   Title: "⚠️ Insufficient WIP from Previous Department"
    │   Message: "
    │   Your target: {target_B} pcs
    │   Available from {dept_A}: {output_A} pcs
    │   
    │   You can:
    │   1) START with available qty ({output_A} pcs) - Partial start
    │   2) WAIT for {dept_A} to complete more units
    │   3) ADJUST your target to match available qty
    │   
    │   What would you like to do?
    │   "
    │   [START PARTIAL] [WAIT] [ADJUST TARGET]
    │
    └─ User action options:
        ├─ START PARTIAL: Update WO target → {output_A} pcs, start work
        ├─ WAIT: Close dialog, WO remains in "Ready" state (no start yet)
        └─ ADJUST TARGET: Open adjustment wizard, request Manager approval

Example Scenario:
────────────────────────────────────────────────────────────────
├─ Cutting Output (Actual): 520 pcs (still in progress, target 578 pcs)
├─ Embroidery Target: 541 pcs
└─ Embroidery admin click "START WORK"
    ├─ System check: 520 pcs < 541 pcs → FAIL constraint!
    ├─ Show warning dialog (as above)
    └─ Admin choose "START PARTIAL" → Embroidery target updated to 520 pcs
        └─ Note: When Cutting complete next batch → System notify Embroidery:
            "New WIP available from Cutting (+58 pcs). Resume work?"
```

**FR-2.3: Dynamic Target Adjustment (Real-Time Response to High Defect)**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
When: Dept A complete work order dengan defect rate significantly higher than expected
Then: System must AUTO-ADJUST downstream department targets + ALERT stakeholders

Trigger Condition:
├─ Actual_Defect_Rate > Historical_Defect_Rate + 5%  (threshold configurable)
└─ Example:
    ├─ Cutting historical defect: 3%
    ├─ Cutting actual defect this batch: 15% (12% above expected!)
    └─ TRIGGER adjustment!

System Auto-Action:
├─ Recalculate downstream targets:
│   ├─ OLD: Embroidery 541 pcs, Sewing 530 pcs, ...
│   └─ NEW: Based on Cutting actual output (490 pcs)
│       └─ Embroidery 490 pcs, Sewing 480 pcs, ... (reverse chain recalc!)
│
├─ Update Work Orders:
│   └─ WO-Embroidery: Target 541 → 490 pcs (updated!)
│       WO-Sewing: Target 530 → 480 pcs (updated!)
│       ... (all downstream updated)
│
├─ Log adjustment:
│   └─ Record: Which dept trigger? What defect rate? Old vs new targets? Timestamp?
│
└─ Send alerts:
    ├─ To: Manager (URGENT!)
    │   └─ "🔴 HIGH DEFECT ALERT: Cutting defect 15% (expected 3%)!
    │       Downstream targets auto-adjusted. Shortfall: -40 pcs from customer order.
    │       ACTION: Investigate root cause + Consider re-run Cutting."
    │
    ├─ To: Affected department SPVs (Embroidery, Sewing, ...)
    │   └─ "⚠️ Target Updated: Your WO target reduced to {new_target} pcs
    │       due to upstream defect. Check system for details."
    │
    └─ Dashboard: Show banner alert "🔴 MO-2026-001: Target Adjusted (High Defect!)"

Manager Action Options:
────────────────────────────────────────────────────────────────
After receiving alert, Manager can:
├─ Option 1: ACCEPT adjustment (do nothing - proceed with reduced target)
│   └─ Result: Customer order akan SHORT (less than 450 pcs)
│       └─ Need inform customer OR partial shipment
│
├─ Option 2: EMERGENCY RE-RUN (Cutting department)
│   └─ Action: Create new WO-Cutting for deficit qty (450 - 410 = 40 pcs)
│       └─ Priority: HIGH (express processing!)
│       └─ Timeline: Add 3-5 hari lead time (re-run cycle)
│
└─ Option 3: OVERRIDE DOWNSTREAM BUFFER (risky!)
    └─ Action: Manually reduce downstream buffers (push dept to be more careful!)
        └─ Example: Sewing buffer 12% → Reduce to 8% (force higher yield)
        └─ Risk: Jika Sewing also high defect → Shortage makin parah!

UI - Manager Dashboard Alert:
────────────────────────────────────────────────────────────────
[🔴 URGENT ACTION REQUIRED]
┌────────────────────────────────────────────────────────────┐
│  MO-2026-001: HIGH DEFECT DETECTED!                        │
├────────────────────────────────────────────────────────────┤
│  Department: Cutting                                       │
│  Expected Defect: 3% │ Actual Defect: 15% (⚠️ +12%!)     │
│  Target: 578 pcs │ Output: 490 pcs (Short: -88 pcs!)      │
│                                                            │
│  Impact:                                                   │
│  ├─ All downstream targets adjusted (↓ 88 pcs each)       │
│  └─ Customer order shortfall: -40 pcs (expected 450 pcs)  │
│                                                            │
│  [VIEW DETAILS] [INVESTIGATE ROOT CAUSE] [CREATE RE-RUN]  │
└────────────────────────────────────────────────────────────┘
```

**FR-2.4: Production Output Display Format (Actual/Target with Percentage)**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
System must display production output in consistent format:

Format: Actual / Target (Percentage%)

Examples:
├─ 450 / 578 (77.9%)  - In Progress
├─ 578 / 578 (100%) ✅ - Target Met
├─ 595 / 578 (103%) ✅ - Exceeds Target (good!)
└─ 490 / 578 (84.8%) ⚠️ - Below Target (investigate!)

Color Coding (Visual Management):
├─ Green: Percentage ≥ 98% (Target met/exceeded!)
├─ Yellow: Percentage 90-97% (Close to target, acceptable)
├─ Orange: Percentage 80-89% (Below target, need attention)
└─ Red: Percentage < 80% (Critical! High defect or problem!)

UI Implementation (Dashboard & WO Detail):
────────────────────────────────────────────────────────────────
[Work Order Dashboard - Cutting Department]
┌────────────────────────────────────────────────────────────┐
│ WO-CUT-001 │ AFTONSPARV Bear │ Week: W05-2026             │
├────────────────────────────────────────────────────────────┤
│ Target: 578 pcs │ Actual: 520 pcs │ Progress: 520/578 (90%)│
│ Status: In Progress ●                            🟡 Yellow │
│ Defect: 18 pcs (3.4%) ✅ Within expected range            │
│                                                            │
│ [INPUT PRODUCTION] [VIEW DEFECTS] [COMPLETE WORK ORDER]   │
└────────────────────────────────────────────────────────────┘

[Work Order Dashboard - Sewing Department]
┌────────────────────────────────────────────────────────────┐
│ WO-SEW-001 │ AFTONSPARV Bear │ Week: W05-2026             │
├────────────────────────────────────────────────────────────┤
│ Target: 530 pcs │ Actual: 398 pcs │ Progress: 398/530 (75%)│
│ Status: In Progress ●                            🔴 RED!   │
│ Defect: 62 pcs (13.5%) ⚠️ ABOVE expected (12%)!           │
│                                                            │
│ ⚠️ HIGH DEFECT ALERT! Investigate immediately!            │
│ [INPUT PRODUCTION] [RECORD DEFECTS] [ALERT MANAGER]       │
└────────────────────────────────────────────────────────────┘

Chart Visualization (MO Summary):
────────────────────────────────────────────────────────────────
[MO-2026-001 - Progress Tracking]
┌────────────────────────────────────────────────────────────┐
│ Cutting      ████████████████████░░ 520/578 (90%) 🟡      │
│ Embroidery   ███████████████████░░░ 495/541 (91%) 🟡      │
│ Sewing       ██████████████░░░░░░░░ 398/530 (75%) 🔴      │
│ Stuffing     ░░░░░░░░░░░░░░░░░░░░░░ 0/466 (0%) Waiting    │
│ Closing      ░░░░░░░░░░░░░░░░░░░░░░ 0/457 (0%) Waiting    │
│ Packing      ░░░░░░░░░░░░░░░░░░░░░░ 0/452 (0%) Waiting    │
└────────────────────────────────────────────────────────────┘
Overall Progress: 42% │ Bottleneck: Sewing (Red!) │ ETA: T+8 days
```

---

#### 11.2.4 Business Value & Impact

**Quantitative Benefits**:

| Metric | Before (Rigid Target) | After (Flexible Target) | Improvement |
|--------|----------------------|------------------------|-------------|
| **Shortage Frequency** | 25% of orders | <5% of orders | **-80% cases!** |
| **Emergency Re-Run** | 18% of MOs | <5% of MOs | **-72% reduction!** |
| **Material Waste** | 8-12% over-order (panic buffer!) | 3-5% (calculated buffer) | **-50% waste!** |
| **Customer Satisfaction** | 75% OTD | 95%+ OTD | **+27% improvement!** |

**Qualitative Benefits**:
- ✅ **Predictability**: Manager tahu expected output per dept → Better planning!
- ✅ **Visibility**: Real-time alert jika defect tinggi → Fast response!
- ✅ **Cost Efficiency**: Material consumption optimized (no excessive buffer!)
- ✅ **Quality Focus**: System highlight high-defect dept → Continuous improvement!

**Risk if NOT implemented**:
- ❌ **Frequent shortage** (rigid target + unpredictable defect) → **Customer complaints + Penalty!**
- ❌ **Material waste** (panic buffer ordering) → **Higher COGS!**
- ❌ **Late detection** (defect baru ketahuan di final stage) → **Too late to recover!**

---

### <a name="section-11-3"></a>11.3 Requirement #3: 2-Stage Finishing Internal Conversion

**Priority**: 🟡 **MEDIUM-HIGH**  
**Business Impact**: **MEDIUM** (inventory accuracy + waste tracking)  
**Standard ERP Support**: ⚠️ **PARTIAL** (by-product logic exist, but not exactly match use case!)

---

#### 11.3.1 Business Context & Problem Statement

**Unique Characteristic**:
```
WAREHOUSE FINISHING - 2 INDEPENDENT PROCESSES:
═══════════════════════════════════════════════════════════════
NORMAL WAREHOUSE: Just storage (receive → Store → Issue)
QUTY WH FINISHING: Processing center + Storage!

STAGE 1: STUFFING
├─ Input: Skin (empty shell from Sewing)
├─ Process: Isi kapas filling + Jahit tutup lubang
├─ Output: Stuffed Body (boneka isi kapas, belum ada hang tag)
└─ Location: WH-Finishing-Stuffing area

STAGE 2: CLOSING
├─ Input: Stuffed Body (from Stage 1)
├─ Process: Pasang hang tag + QC final inspection
├─ Output: Finished Doll (ready untuk Packing assembly!)
└─ Location: WH-Finishing-Closing area

CRITICAL:
- Transfer ANTARA 2 stage = INTERNAL (paperless!)
- Tidak ada surat jalan formal (DN) dari Stage 1 ke Stage 2
- Inventory harus track: Skin stock, Stuffed Body stock, Finished Doll stock (3 produk!)
```

**Current Pain Point** (Manual System):
- Logbook hanya 1 buku untuk 2 stage → **Campur aduk!**
- Tidak tahu: "Berapa Skin waiting stuffing? Berapa Stuffed Body waiting closing?"
- Material consumption tidak jelas: "Berapa kapas terpakai per stage?"
- **Bottleneck tidak terdeteksi**: "Stage mana yang lambat? Stuffing or Closing?"

**Business Need**:
> **"Kami butuh system yang OTOMATIS track inventory per stage (Skin, Stuffed Body, Finished Doll) dan AUTO-CALCULATE material consumption (kapas, thread, hang tag) per stage, TANPA perlu buat surat jalan manual antar stage!"**

---

#### 11.3.2 Solution Requirements: Internal Conversion Workflow

**Concept**: 2 Work Orders sequential dalam 1 location (WH Finishing), dengan internal stock transfer

**WORKFLOW DESIGN**:

```
2-STAGE FINISHING WORKFLOW
═══════════════════════════════════════════════════════════════

INPUT from Sewing (via formal Transfer Order):
───────────────────────────────────────────────────────────────
├─ Product: Skin (empty shell)
├─ Qty: 504 pcs (from WO-Sewing output)
├─ Transfer: WH-Sewing → WH-Finishing (via TO with DN)
└─ Stock Update:
    ├─ WH-Sewing Skin: -504 pcs
    └─ WH-Finishing Skin: +504 pcs ✅


STAGE 1 PROCESSING (Stuffing):
───────────────────────────────────────────────────────────────
Work Order: WO-STUFF-001
├─ Location: WH-Finishing / Stuffing Area
├─ Input Materials (from WH Main):
│   ├─ Skin: 504 pcs (already in WH-Finishing!)
│   ├─ Filling (Dacron): 15,120 gram (30 g/pcs × 504 pcs)
│   └─ Thread closing: 504 meter (1 m/pcs)
│
├─ Process: Admin isi kapas manually + Jahit tutup lubang
│   └─ Time: ~2 menit per pcs (1 admin = 30 pcs/hour)
│
├─ Output:
│   ├─ Stuffed Body: 494 pcs ✅ (yield 98%)
│   └─ Reject/Scrap: 10 pcs ❌ (defect: kapas tidak rata, lubang kusut)
│
└─ Stock Update (AUTO-BACKFLUSH when WO completed!):
    ├─ WH-Finishing Skin: -504 pcs (consumed!)
    ├─ WH-Main Filling: -15,120 gram (auto-deduct!)
    ├─ WH-Main Thread: -504 meter (auto-deduct!)
    ├─ WH-Finishing Stuffed Body: +494 pcs ✅ (new intermediate product!)
    └─ Scrap recorded: 10 pcs Skin (reason: Stuffing defect)

🔥 KEY: NO FORMAL TRANSFER ORDER dari "Skin" ke "Stuffed Body"!
         Ini adalah INTERNAL CONVERSION (BOM-driven backflush!)


STAGE 2 PROCESSING (Closing):
───────────────────────────────────────────────────────────────
Work Order: WO-CLOSE-001
├─ Location: WH-Finishing / Closing Area
├─ Input Materials:
│   ├─ Stuffed Body: 494 pcs (from WO-STUFF-001 output!)
│   └─ Hang Tag: 494 pcs (from WH-Main - Label PO!)
│
├─ Process: Admin pasang hang tag + QC final check + Metal detector scan
│   └─ Time: ~1 menit per pcs (1 admin = 60 pcs/hour)
│
├─ Output:
│   ├─ Finished Doll: 489 pcs ✅ (yield 99%)
│   └─ Reject/Scrap: 5 pcs ❌ (defect: tag placement salah, metal detector fail)
│
└─ Stock Update (AUTO-BACKFLUSH when WO completed!):
    ├─ WH-Finishing Stuffed Body: -494 pcs (consumed!)
    ├─ WH-Main Hang Tag: -494 pcs (auto-deduct!)
    ├─ WH-Finishing Finished Doll: +489 pcs ✅ (final product Stage 2!)
    └─ Scrap recorded: 5 pcs Stuffed Body

🔥 KEY: Again, NO FORMAL TRANSFER ORDER dari "Stuffed Body" ke "Finished Doll"!
         INTERNAL CONVERSION via BOM!


OUTPUT to Packing (via formal Transfer Order):
───────────────────────────────────────────────────────────────
├─ Product: Finished Doll
├─ Qty: 489 pcs
├─ Transfer: WH-Finishing → WH-Packing (via TO with DN - FORMAL!)
└─ Stock Update:
    ├─ WH-Finishing Finished Doll: -489 pcs
    └─ WH-Packing Finished Doll: +489 pcs ✅
```

---

#### 11.3.3 Detailed Functional Requirements

**FR-3.1: BOM Structure for 2-Stage Finishing**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
System must support BOM with INTERMEDIATE PRODUCTS (Stuffed Body)

BOM STRUCTURE DESIGN:
────────────────────────────────────────────────────────────────
Product: AFTONSPARV Bear - Finished Doll (Final Output of Finishing)

BOM Level 1: CLOSING (Stage 2)
├─ Input:
│   ├─ Stuffed Body (INTERMEDIATE): 1 pcs ← FROM Stage 1!
│   └─ Hang Tag: 1 pcs
├─ Output:
│   └─ Finished Doll: 1 pcs
└─ Operation: WC-Closing (Workcenter: Closing area)

BOM Level 2: STUFFING (Stage 1) - Sub-BOM of Stuffed Body!
├─ Input:
│   ├─ Skin (from Sewing): 1 pcs
│   ├─ Filling (Dacron): 30 gram
│   └─ Thread closing: 1 meter
├─ Output:
│   └─ Stuffed Body: 1 pcs (INTERMEDIATE product!)
└─ Operation: WC-Stuffing (Workcenter: Stuffing area)

SYSTEM CONFIGURATION:
────────────────────────────────────────────────────────────────
Product Master: Create "Stuffed Body" sebagai product
├─ Product Type: "Intermediate" (new category!)
├─ Tracking: By Lot/Serial (optional)
├─ Inventory: ✅ Yes (stockable! Track di WH-Finishing!)
├─ Valuation: Standard cost (untuk costing calculation)
└─ Note: This product NEVER sold to customer (internal only!)

BOM Master: Link 2 BOMs dengan intermediate product
├─ BOM-1: Skin → Stuffed Body (Stuffing BOM)
│   └─ BOM Type: "Manufacturing" (with operation WC-Stuffing)
│
└─ BOM-2: Stuffed Body → Finished Doll (Closing BOM)
    └─ BOM Type: "Manufacturing" (with operation WC-Closing)

Routing: 2 Operations sequential
├─ Operation 1: Stuffing (WC-Stuffing)
│   ├─ Duration: 2 menit/pcs
│   ├─ Output: Stuffed Body (intermediate)
│   └─ Quality checkpoint: QC3-Stuffing
│
└─ Operation 2: Closing (WC-Closing)
    ├─ Duration: 1 menit/pcs
    ├─ Output: Finished Doll (final)
    └─ Quality checkpoint: QC3-Closing
```

**FR-3.2: Work Orders Generation for 2 Stages**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
When: MO created untuk artikel dengan 2-stage Finishing
Then: System must generate 2 DEPENDENT Work Orders

Work Order Creation Logic:
────────────────────────────────────────────────────────────────
MO: MO-2026-001 (AFTONSPARV Bear - 450 pcs customer order)

Generated WOs:
├─ WO-STUFF-001 (Stage 1 = Stuffing)
│   ├─ Parent MO: MO-2026-001
│   ├─ Operation: Stuffing (WC-Stuffing)
│   ├─ Input Product: Skin (504 pcs from flexible target calc!)
│   ├─ Output Product: Stuffed Body (target: 466 pcs - calculated dari Stage 2 need!)
│   ├─ Materials consumed:
│   │   ├─ Filling: 15,120 gram (30 g × 504 pcs)
│   │   └─ Thread: 504 meter
│   ├─ Status: Ready to Start (after Sewing transfer Skin)
│   └─ Dependency: Must complete BEFORE WO-CLOSE-001 can start!
│
└─ WO-CLOSE-001 (Stage 2 = Closing)
    ├─ Parent MO: MO-2026-001
    ├─ Operation: Closing (WC-Closing)
    ├─ Input Product: Stuffed Body (466 pcs from WO-STUFF-001 output!)
    ├─ Output Product: Finished Doll (target: 457 pcs)
    ├─ Materials consumed:
    │   └─ Hang Tag: 466 pcs
    ├─ Status: LOCKED (Waiting WO-STUFF-001 complete!)
    └─ Dependency: Can START only after WO-STUFF-001 produce sufficient Stuffed Body

DEPENDENCY LOGIC:
────────────────────────────────────────────────────────────────
Rule: WO-CLOSE-001 can start ONLY IF Stock(Stuffed Body) ≥ Target(WO-CLOSE-001)

Example Timeline:
├─ Day 1, 10:00: WO-STUFF-001 start
├─ Day 1, 14:00: WO-STUFF-001 complete 150 pcs (batch 1) → Stock(Stuffed Body) = 150
├─ Day 1, 14:05: System check: 150 pcs < 466 pcs target → WO-CLOSE-001 STILL LOCKED
├─ Day 2, 10:00: WO-STUFF-001 complete 200 pcs (batch 2) → Stock(Stuffed Body) = 350
├─ Day 2, 14:00: WO-STUFF-001 complete 144 pcs (batch 3) → Stock(Stuffed Body) = 494
├─ Day 2, 14:05: System check: 494 pcs ≥ 466 pcs target → ✅ UNLOCK WO-CLOSE-001!
│                └─ Notification: "WO-CLOSE-001 ready to start! Stuffed Body stock sufficient."
└─ Day 2, 15:00: WO-CLOSE-001 start (admin dapat mulai Closing process!)

PARTIAL START OPTION (sama seperti FR-2.2):
────────────────────────────────────────────────────────────────
Jika Closing admin ingin start SEBELUM full target ready:
├─ Day 1, 16:00: Closing admin click "START WORK" (stock hanya 150 pcs)
├─ System: Show dialog "⚠️ Insufficient stock (150/466 pcs). Start partial?"
├─ Admin choose: "YES - Start with available qty"
└─ Result: WO-CLOSE-001 start dengan 150 pcs, continue later when more stock arrive
```

**FR-3.3: Inventory Tracking per Stage (3 Products!)**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
System must track inventory untuk 3 products di WH-Finishing:
1. Skin (input dari Sewing)
2. Stuffed Body (intermediate - output Stage 1, input Stage 2)
3. Finished Doll (output Stage 2, transfer ke Packing)

STOCK LOCATION STRUCTURE:
────────────────────────────────────────────────────────────────
WH-Finishing (Parent Location)
├─ WH-Finishing / Stuffing Area (Sub-location 1)
│   ├─ Stock: Skin (waiting stuffing)
│   └─ Stock: Stuffed Body (output from stuffing)
│
└─ WH-Finishing / Closing Area (Sub-location 2)
    ├─ Stock: Stuffed Body (input for closing)
    └─ Stock: Finished Doll (output from closing)

Note: Stuffed Body dapat berada di 2 locations:
  ├─ Stuffing Area: Baru selesai stuffing, belum dipindah
  └─ Closing Area: Sudah dipindah, siap untuk closing
  System aggregate: Total Stuffed Body = Stuffing Area + Closing Area

INVENTORY VISIBILITY (Dashboard View):
────────────────────────────────────────────────────────────────
[WH-Finishing - Stock Summary]
┌────────────────────────────────────────────────────────────┐
│ Product         │ Location        │ Qty    │ Status        │
├─────────────────┼─────────────────┼────────┼───────────────┤
│ Skin            │ Stuffing Area   │ 125 pcs│ Waiting stuff │
│ Stuffed Body    │ Stuffing Area   │  48 pcs│ Done stuff    │
│ Stuffed Body    │ Closing Area    │ 215 pcs│ Waiting close │
│ Finished Doll   │ Closing Area    │ 378 pcs│ Ready transfer│
└─────────────────┴─────────────────┴────────┴───────────────┘

Total Stuffed Body Stock: 48 + 215 = 263 pcs

[ACTIONS]
[📊 View Stock Movement] [📦 Transfer to Packing] [✏️ Stock Adjustment]

STOCK MOVEMENT LOG (Audit Trail):
────────────────────────────────────────────────────────────────
[Movement History - Stuffed Body]
┌────────────────────────────────────────────────────────────┐
│ Date/Time       │ From → To        │ Qty │ Reference      │
├─────────────────┼──────────────────┼─────┼────────────────┤
│ 2026-02-10 10:00│ Production       │ +150│ WO-STUFF-001   │
│                 │ → Stuffing Area  │     │ (Output batch1)│
├─────────────────┼──────────────────┼─────┼────────────────┤
│ 2026-02-10 14:00│ Stuffing Area    │ -148│ WO-CLOSE-001   │
│                 │ → Closing Area   │     │ (Input batch1) │
├─────────────────┼──────────────────┼─────┼────────────────┤
│ 2026-02-10 15:00│ Production       │ +200│ WO-STUFF-001   │
│                 │ → Stuffing Area  │     │ (Output batch2)│
└─────────────────┴──────────────────┴─────┴────────────────┘

PURPOSE: Traceability! Jika ada quality issue, bisa trace:
  "Stuffed Body batch mana yang bermasalah? From which Skin batch?"
```

**FR-3.4: Material Consumption Auto-Backflush per Stage**

```
REQUIREMENT:
════════════════════════════════════════════════════════════════
System must AUTO-DEDUCT materials when each stage WO completed (backflush!)

STAGE 1 BACKFLUSH (Stuffing):
────────────────────────────────────────────────────────────────
When: User click "COMPLETE" WO-STUFF-001
Then: System auto-execute:

├─ Input from user:
│   ├─ Qty produced: 494 pcs (good output)
│   ├─ Qty rejected: 10 pcs (scrapped)
│   └─ Total qty consumed: 504 pcs Skin
│
├─ System calculate material consumption (from BOM):
│   ├─ Filling: 504 pcs × 30 g/pcs = 15,120 gram
│   ├─ Thread: 504 pcs × 1 m/pcs = 504 meter
│   └─ (System can detect if actual > expected → Show warning!)
│
├─ Stock update (AUTO!):
│   ├─ WH-Finishing / Skin: -504 pcs
│   ├─ WH-Main / Filling: -15,120 gram
│   ├─ WH-Main / Thread: -504 meter
│   └─ WH-Finishing / Stuffed Body: +494 pcs ✅
│
├─ Scrap recording:
│   └─ Create scrap record: 10 pcs Skin
│       ├─ Reason: Stuffing defect (kapas tidak rata)
│       ├─ Value: {cost per pcs} × 10
│       └─ Responsible: {operator name}
│
└─ Notification:
    └─ To: WO-CLOSE-001 responsible (Closing SPV)
        "New stock available: 494 pcs Stuffed Body ready for Closing!"

STAGE 2 BACKFLUSH (Closing):
────────────────────────────────────────────────────────────────
When: User click "COMPLETE" WO-CLOSE-001
Then: System auto-execute:

├─ Input from user:
│   ├─ Qty produced: 489 pcs (good output)
│   ├─ Qty rejected: 5 pcs (scrapped)
│   └─ Total qty consumed: 494 pcs Stuffed Body
│
├─ System calculate material consumption:
│   └─ Hang Tag: 494 pcs × 1 pcs/pcs = 494 pcs
│
├─ Stock update (AUTO!):
│   ├─ WH-Finishing / Stuffed Body: -494 pcs
│   ├─ WH-Main / Hang Tag: -494 pcs
│   └─ WH-Finishing / Finished Doll: +489 pcs ✅
│
├─ Scrap recording:
│   └─ Create scrap record: 5 pcs Stuffed Body
│       ├─ Reason: Closing defect (tag placement wrong OR metal detector fail)
│       └─ Value: {cost including Stage 1 materials!}
│
└─ Notification:
    └─ To: Packing SPV
        "Finished Doll ready: 489 pcs. Ready for transfer to Packing!"

MATERIAL CONSUMPTION REPORT:
────────────────────────────────────────────────────────────────
[MO-2026-001 - Material Analysis]
┌────────────────────────────────────────────────────────────┐
│ Material      │ Expected  │ Actual    │ Variance │ Status│
├───────────────┼───────────┼───────────┼──────────┼───────┤
│ Skin          │ 504 pcs   │ 504 pcs   │ 0 pcs    │  ✅   │
│ Filling       │ 15,120 g  │ 15,350 g  │ +230 g   │  ⚠️  │
│ Thread        │ 504 m     │ 510 m     │ +6 m     │  ✅   │
│ Hang Tag      │ 494 pcs   │ 494 pcs   │ 0 pcs    │  ✅   │
└───────────────┴───────────┴───────────┴──────────┴───────┘

Analysis:
⚠️ Filling consumed 230g MORE than expected (+1.5%)!
   Possible causes:
   ├─ Admin overstuff (too much filling per pcs)
   ├─ BOM standard outdated (need update?)
   └─ Material measurement inaccurate (scale calibration?)
   
Action: Investigate + Adjust BOM if needed
```

---

#### 11.3.4 Business Value & Impact

**Quantitative Benefits**:

| Metric | Before (Manual) | After (System) | Improvement |
|--------|----------------|----------------|-------------|
| **Inventory Accuracy** (WH Finishing) | 70-75% | 95%+ | **+27% accuracy!** |
| **Material Waste Tracking** | Not tracked | 100% tracked per stage | **Full visibility!** |
| **Bottleneck Detection** | Manual ask (slow!) | Real-time dashboard | **Immediate insight!** |
| **Stock Opname Time** (WH Finishing) | 4 jam (confusion!) | 1 jam (clear!) | **-75% time!** |

**Qualitative Benefits**:
- ✅ **Visibility**: Manager tahu exact stock per stage (tidak campur!)
- ✅ **Traceability**: Quality issue bisa di-trace back ke batch specific
- ✅ **Process Control**: Material consumption per stage tracked → Identify waste source
- ✅ **Efficiency**: Auto-backflush → Admin tidak perlu input manual material transaction!

**Risk if NOT implemented**:
- ❌ **Inventory chaos** (tidak tahu berapa Skin vs Stuffed Body stock) → **Production planning impossible!**
- ❌ **Material waste undetected** (filling over-consumption tidak ketahuan) → **Higher COGS!**
- ❌ **Bottleneck hidden** (tidak tahu Stage 1 or 2 yang lambat) → **Cannot optimize!**

---

[Document akan dilanjutkan dengan Requirements #4-#7 + Section 12-19...]

📊 **PROGRESS UPDATE**: 
- ✅ Section 1-10 COMPLETE (Bagian A, B, C)
- ✅ Section 11.1-11.3 COMPLETE (3 dari 7 Unique Requirements!)
- ⏭️ **NEXT**: Section 11.4-11.7 (4 remaining unique requirements) + Functional Specs (Section 12-19)

🔥 **CURRENT STATUS**: Dokumen sudah 25,000+ words! Super comprehensive untuk Sales Odoo!

Saya lanjutkan dengan Requirements #4-#7?
