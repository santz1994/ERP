# 🏭 PT QUTY KARUNIA - ODOO ERP PROJECT
## Executive One-Pager untuk Gap Analysis Consultation

**Tanggal**: 13 Februari 2026  
**Disusun Oleh**: IT Lead - Daniel Rizaldy  
**Target**: Odoo Sales Team & PM (Quick Overview)  
**Untuk**: Gap Analysis Phase - Initial Review

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
| 3. SPK tidak terpantau | Late delivery → penalty | 🔴 CRITICAL |
| 4. Finished goods sulit verifikasi | Customer complaints | 🟠 HIGH |
| 5. No approval clarity | Fraud potential, no audit | 🟠 HIGH |
| 6. Monthly reports lambat | Delayed decisions | 🟡 MEDIUM |
| 7. Finishing process chaos | Material waste | 🔴 CRITICAL |
| 8. UOM conversion errors | Inventory kacau | 🔴 CRITICAL |
| 9. Rigid production targets | Shortage karena defect | 🔴 CRITICAL |
| 10. Defect tidak tertrack | High waste, no root cause | 🟠 HIGH |
| 11. Previous Odoo GAGAL | Admin trauma, Management skeptis | 🔴 CRITICAL |

> ⚠️ **CRITICAL**: Pain point #11 adalah **paling penting**! PT Quty pernah implementasi Odoo sebelumnya dan **GAGAL TOTAL**. Admin sekarang trauma, Management sangat skeptis. **Ini adalah LAST CHANCE untuk Odoo di Quty!**

---

## 🎯 PROJECT OBJECTIVES

**Goal**: Replace fragmented manual systems dengan **integrated Odoo ERP** yang **disesuaikan** dengan workflow Quty (bukan force-fit!)

**Success Metrics** (6-12 bulan post-GoLive):
- ⏱️ Lead Time: 25 hari → **18 hari** (-28%)
- 📦 On-Time Delivery: 75% → **95%+** (+27%)
- 📊 Inventory Accuracy: 82% → **98%+** (+20%)
- ⚡ Reporting: 3-5 hari → **Real-time** (-99%)
- 👥 **User Adoption**: Admin yang trauma Odoo → **Comfortable** menggunakan sistem

**Critical Success Factor**: Admin harus **tidak trauma lagi** dengan Odoo implementation kali ini!

---

## 🔥 UNIQUE REQUIREMENTS (Critical to Understand!)

### ⚠️ **7 UNIQUE FEATURES** - Tidak ada di Standard Odoo

| # | Feature | Business Impact | Complexity |
|---|---------|-----------------|----------------------|
| **1** | **Dual Trigger MO** | PO Kain (early start) + PO Label (full release) | 🔴 HIGH |
| **2** | **Flexible Target System** | SPK target ≠ MO target (buffer management) | 🔴 HIGH |
| **3** | **Warehouse Finishing 2-Stage** | Internal WIP conversion (Skin → Stuffed) | 🟠 MEDIUM |
| **4** | **UOM Auto-Validation** | Tolerance checking (Yard→Pcs, Box→Pcs) | 🟠 MEDIUM |
| **5** | **Real-Time WIP System** | Parallel production (batch-based transfer) | 🟠 MEDIUM |
| **6** | **Pull System Auto-Deduction** | Zero paperwork material movement | 🟡 LOW |
| **7** | **Rework/Repair Module** | QC defect loop dengan recovery tracking | 🟠 MEDIUM |

**Total Customization**: Level customization akan ditentukan dalam **Gap Analysis Phase** bersama Odoo team

**Catatan Embroidery**: Embroidery bisa dikerjakan **internal** (jika pabrik punya mesin) ATAU **vendor eksternal** (outsourced). Jika vendor, workflow: Cutting → Kirim ke Vendor → Terima dari Vendor → Sewing.

---

## 📋 CORE MODULES YANG DIBUTUHKAN

### Priority 1 (CRITICAL)
- ✅ **Purchasing** - 3 parallel streams (Fabric, Label, Accessories) + PO untuk vendor embroidery
- ✅ **Manufacturing (MRP)** - MO → SPK generation, BOM explosion
- ✅ **Inventory** - 3 warehouses utama (Main, Finishing, FG-per pallet) + warehouse per departemen (setiap departemen punya stock opname), Multi-UOM, Stock tracking (termasuk tracking outbound/inbound vendor)
- ✅ **Quality Control** - 4 checkpoints, Defect recording

### Priority 2 (HIGH)
- ✅ **Production Planning** - Weekly scheduling (W01-2026 format)
- ✅ **Reporting** - Real-time dashboard, Management KPI
- ✅ **User Management** - RBAC, Multi-level approval

### Priority 3 (NICE-TO-HAVE)
- 🔄 **Barcode System** - FG tracking, Pallet system
- 🔄 **Mobile App** - Android untuk production input

---

## 💡 KENAPA FEATURES INI UNIK?

### 1️⃣ Dual Trigger MO System

**Problem**: Label berisi info kritis (Week + Destination), tapi lead time panjang (7-10 hari)

**Solution**:
```
PO Kain arrives (Day 1) → MO = PARTIAL
├─ Cutting: CAN START ✅
├─ Embroidery (internal/vendor): CAN START ✅
└─ Sewing onwards: BLOCKED ❌ (tunggu label)

PO Label arrives (Day 5) → MO = RELEASED
└─ All departments: UNLOCKED ✅
```

**Impact**: Lead time **-30 sampai -40%** (start 5 hari lebih cepat!)

---

### 2️⃣ Flexible Target System

**Problem**: Standard MRP asumsikan SPK Target = MO Target (rigid!) → Shortage jika ada defect

**Solution**:
```
MO: 450 pcs
├─ Cutting SPK: 495 pcs (+10% buffer)
├─ Sewing SPK: 480 pcs (adjust to actual input)
└─ Packing SPK: 465 pcs (urgent match only)
```

**Impact**: **Zero shortage risk**, material efficiency **+15%**

---

### 3️⃣ Warehouse Finishing 2-Stage

**Problem**: Standard warehouse asumsikan 1-step process. Quty butuh 2-step internal conversion.

**Solution**:
```
Warehouse Finishing (Internal):
├─ Stage 1: Skin (485 pcs) + Filling → Stuffed Body (475 pcs)
└─ Stage 2: Stuffed Body + Thread + Label → Finished Doll (470 pcs)

→ 2 separate stocks tracked!
```

**Impact**: Material waste **-8 sampai -12%** (filling cost 15-20% dari total)

---

## ❓ PERTANYAAN KRITIS UNTUK ODOO TEAM

### Technical Feasibility
1. Apakah Odoo MRP support **2-stage MO unlocking** (PARTIAL → RELEASED)?
2. Apakah SPK bisa punya **flexible targets** berbeda dari MO?
3. Bagaimana implement **internal warehouse conversion** tanpa formal transfer?
4. Apakah Odoo support **UOM validation** dengan tolerance checking?
5. Apakah stock movement bisa **auto-triggered** dari production confirmation?
6. Bagaimana handle **previous Odoo failure** issue? Apa yang akan berbeda kali ini?

### Training & Change Management
1. Bagaimana approach untuk **admin yang trauma dengan Odoo**?
2. Training methodology: Hands-on? Classroom? On-the-job?
3. Berapa lama training per role?
4. Post-training support mechanism?

### Project Management
1. **Reference clients**: Apakah ada client dengan manufacturing complexity similar?
2. **Team allocation**: Berapa developer? PM experience?
3. **Timeline**: Realistic estimate setelah Gap Analysis?
4. **Risk mitigation**: Jika mid-project customization tidak feasible, apa plan B?

---

## 🚀 NEXT STEPS

### Setelah Dokumen Ini Diterima Odoo

**Step 1: Gap Analysis Consultation Quote**
- [ ] Odoo team review dokumen ini
- [ ] Odoo assign Project Director & Business Analyst
- [ ] Odoo issue **Gap Analysis Consultation Quote**

**Step 2: Gap Analysis Phase (Workshop & Deep Dive)**
- [ ] Workshop 2-3 sesi: Deep dive 7 unique features
- [ ] Site visit ke factory Quty (understand real operation)
- [ ] Technical feasibility assessment per feature
- [ ] Reference client validation

**Step 3: Gap Analysis Report & Proposal**
- [ ] Odoo deliver: Solution Design, Project Plan, Commercial Proposal
- [ ] PT Quty validate: Apakah sesuai ekspektasi?
- [ ] Revisi sampai clear (jika perlu)

**Step 4: Decision Point**
- [ ] Go/No-Go decision dari Management Quty
- [ ] Jika GO: Contract signing → Kick-off → Implementation

---

##Untuk Dokumentasi Detail Lengkap**:
- Request full technical specification (4,200+ lines)
- Request workflow illustrations (1,500+ lines)
- Request Odoo gap analysis document (1,200+ lines)

---

## ✅ DECISION CRITERIA (Management View)

### GO Decision jika:
✅ Semua 7 unique features **feasible** dengan customization reasonable  
✅ Odoo team demonstrate **deep understanding** workflow Quty  
✅ Reference client proven (**manufacturing domain similar**)  
✅ Training plan solid untuk **admin yang trauma Odoo**  
✅ Post-GoLive support SLA **clear & strong**  
✅ Timeline realistic **<6 bulan**  
✅ Proof of concept untuk critical features **berhasil demonstrated**  

### NO-GO jika:
❌ Major features **TIDAK feasible** di Odoo platform  
❌ Odoo team coba **force-fit** standard tanpa proper customization  
❌ **No clear answer** untuk previous Odoo failure (kenapa kali ini berbeda?)  
❌ Training plan **generic** tanpa consider admin trauma  
❌ Support SLA **vague** atau tidak committed  
❌ Timeline **unrealistic** (<3 bulan atau >9 bulan)

---

**AKHIR ONE-PAGER**

> 🎯 **Call to Action**: Menunggu **Gap Analysis Consultation Quote** dari Odoo team

> ⚠️ **Important**: Ini adalah **LAST CHANCE** untuk Odoo di PT Quty. Previous implementation GAGAL. **HARUS BERHASIL** kali ini!

---

**Versi Dokumen**: 1.0  
**Status**: ✅ Siap untuk Odoo Partner Initial Review (Gap Analysis Phase)  
**Tanggal**: 13 Februari 2026  
**Prepared By**: IT Lead PT Quty Karunia
> 🎯 **Call to Action**: Schedule 2-hour discovery workshop with Odoo PM + Technical Lead ASAP

---

**Document Version**: 1.0  
**Status**: ✅ Ready for Odoo Sales Initial Review  
**Next**: Detailed technical deep-dive meeting
