# PROPOSAL ERP IMPLEMENTATION - ODOO
## Presentasi untuk Management PT Quty Karunia

**Dari**: Daniel Rizaldy (IT Lead)  
**Untuk**: Management PT Quty Karunia  
**Tanggal**: 13 Februari 2026  
**Tujuan**: Approval untuk proceed dengan Odoo ERP Implementation

---

## COMPANY PROFILE

**PT Quty Karunia** - Manufacturer Soft Toys untuk IKEA
- Main Customer: IKEA (80% revenue)
- Production: 1-1.5 million pcs/bulan
- Products: 478 SKU (boneka, plushies, mascot)
- Users: 33 admin users
- Location: Purwakarta, Indonesia

---

## KENAPA BUTUH ERP SEKARANG?

### 3 Alasan Utama:

1. **IKEA Compliance Pressure**
   - IKEA mulai demand real-time traceability
   - Kami tidak punya audit trail untuk quality issues
   - Risk: Kehilangan 80% revenue source

2. **Operational Chaos**
   - Excel + WhatsApp + kertas = tidak efisien
   - Material shortage tiba-tiba (8-10x per bulan)
   - Tidak tahu WIP real-time
   - Admin overtime berlebihan

3. **Tidak Bisa Scale**
   - System manual tidak bisa handle 2x volume
   - IKEA plan increase order → Kami tidak ready

---

## LESSONS LEARNED: ODOO 2023 (GAGAL) VS RENCANA 2026

### Project Odoo 2023 - APA YANG SALAH?

**1. BOM Management**
- **Masalah**: Admin harus input BOM manual satu per satu untuk 478 SKU
- **Dampak**: 
  - 3-4 bulan hanya untuk data entry BOM
  - Error frequent (typo, salah quantity)
  - Admin exhausted sebelum production mulai
  - Data tidak consistent antar SKU
  - **Tidak memahami requirement Dual BOM**:
    - Hanya input 1 BOM → Tidak tahu harus pakai BOM Purchasing atau BOM Production
    - Material calculation jadi salah (shortage palsu atau over-order)
    - Output production tidak match dengan MO target (confusing!)

**2. Material Availability**
- **Masalah**: Material selalu status MERAH di system
- **Akar Masalah**: 
  - Stock data tidak sync dengan warehouse physical
  - No proper receiving workflow (PO datang tidak ter-record)
  - System hitung stock salah (multi-unit conversion issue)
  - **Dual BOM System tidak di-configure** (CRITICAL!):
    - **BOM Purchasing**: Untuk kalkulasi material yang harus dibeli (include defect rate/waste buffer)
    - **BOM Production**: Untuk actual consumption di lantai produksi (based on efficiency)
    - Odoo 2023 hanya pakai 1 BOM → Material calculation SALAH!
    - Contoh: BOM Purchasing butuh 1000 meter fabric (with 5% defect buffer), tapi BOM Production actual consume hanya 950 meter
    - System block production karena hitung stock berdasarkan BOM Purchasing (padahal BOM Production cukup!)
- **Dampak**: 
  - Production TIDAK BISA jalan karena system block (padahal material ada!)
  - Material shortage palsu: Stock cukup untuk BOM Production, tapi system hitung pakai BOM Purchasing
  - MO quantity salah: MO target 1000 pcs (from BOM Purchasing), tapi SPK actual output 1050 pcs (karena efficiency BOM Production lebih baik)
  - Reconciliation chaos: "Kok output lebih banyak dari target MO?"

**3. Reporting & Data Export**
- **Masalah**: Tidak ada fungsi import/export laporan
- **Dampak**: 
  - Management tidak bisa analyze data (trapped di system)
  - Harus screenshot/manual entry untuk reporting
  - Cannot integrate dengan Excel existing workflows

**4. Suplier Approach**
- **Masalah**: Suplier force-fit standard Odoo tanpa customize
- **Kutipan**: "Ini sudah standard flow Odoo, kalian yang harus adjust"
- **Dampak**: 
  - Business process kami forced pakai workaround
  - User frustasi, adoption failed
  - 6 bulan kemudian abandon project → Balik ke Excel

**5. UOM Conversion Tidak Sesuai**
- **Masalah**: Multi-unit conversion tidak configured dengan benar
- **Akar Masalah**:
  - Material datang dalam berbagai unit (ROLL, YARD, KG, BOX)
  - Setiap suplier punya rate conversion berbeda
  - **Production menggunakan unit berbeda dari Purchasing**:
    - Purchasing terima Fabric dalam ROLL, Production consume dalam METER
    - Purchasing terima Thread dalam KG, Production consume dalam GRAM
    - BOM tidak bisa define conversion yang berbeda per suplier
  - Odoo default UOM terlalu simple untuk PT Quty Karunia workflow
  - **Pallet calculation tidak terintegrasi**:
    - IKEA requirement: 24 carton per pallet (harus GENAP!)
    - System tidak bisa auto-calculate pallet dari order quantity
- **Dampak**:
  - Stock calculation selalu salah (warehouse vs production unit berbeda!)
  - Admin harus manual convert tiap kali check availability
  - Production planning tidak akurat karena quantity mismatch
  - Warehouse receiving harus selalu manual adjustment
  - **BOM consumption salah**: Production report consume 100 METER, tapi system deduct 100 ROLL!
  - **Material shortage palsu**: Stock ada 50 ROLL, tapi system bilang kurang (karena BOM minta 2500 METER)

**6. UI/UX Tidak User Friendly**
- **Masalah**: Interface Odoo terlalu complex untuk user PT Quty Karunia
- **Akar Masalah**:
  - Menu structure terlalu dalam (5-6 klik untuk akses fungsi umum)
  - Terminology bahasa Inggris membingungkan user
  - Mobile view tidak optimal (admin butuh input di lantai produksi)
  - Terlalu banyak field yang tidak relevan ditampilkan
- **Dampak**:
  - User frustasi, adoption rate rendah
  - Training time sangat lama (2-3 minggu masih bingung)
  - User prefer balik ke Excel karena lebih familiar
  - Mobile usage impossible → Admin tetap harus ke office untuk input

**7. MO Manual Creation oleh Admin**
- **Masalah**: Manufacturing Order (MO) harus dibuat manual satu per satu
- **Akar Masalah**:
  - Tidak ada auto-generation dari Purchase Order yang dibuat Purchasing
  - Tidak ada link antara PO IKEA dengan MO Production
  - Admin Production harus manual create MO based on WhatsApp/meeting
- **Dampak**:
  - Admin overwhelmed: 20-30 MO per hari harus manual create!
  - Sering salah quantity atau SKU (human error ketik manual)
  - Delay production start karena admin lupa create MO
  - Tidak ada traceability: MO ini untuk order IKEA mana?

**8. WO Manual Creation per Department**
- **Masalah**: Work Order (WO) harus dibuat manual untuk tiap department
- **Akar Masalah**:
  - Routing tidak configured → WO tidak auto-generate dari MO
  - Admin tiap dept harus manual create WO sendiri-sendiri
  - 5 departments = 5x manual work untuk 1 production run!
- **Dampak**:
  - 5x administrative overhead (Cutting, Embr, Sewing, Finishing, Packing)
  - WO antar dept sering tidak sync (dept A sudah done, dept B belum create WO)
  - Tidak ada visibility production stage (застряло di dept mana?)
  - Shop floor workers bingung: Kerja apa hari ini? (WO tidak ready)

---

### Rencana Odoo 2026 - APA YANG BERBEDA?

**1. BOM Management (Improved)**
- **Solusi**: 
  - Import BOM dari Excel existing (bulk import untuk 478 SKU)
  - **Dual BOM Setup** (untuk setiap SKU):
    - BOM Purchasing (Type: MRP): Include defect buffer 5-10% per material
    - BOM Production (Type: Consumption): Actual efficiency-based consumption
  - Template standardized untuk similar products
  - Validation rules untuk prevent error
  - Progressive data entry (tidak harus complete 100% sebelum start)
- **Garis Waktu**: 2-3 minggu data preparation (vs 3-4 bulan sebelumnya)

**2. Material Availability (Fixed)**
- **Solusi**: 
  - Proper receiving workflow: PO → Receive → Auto-update stock
  - Multi-unit conversion configured correct dari awal
  - **Dual BOM + Dual MO System Configuration** (CRITICAL FIX!):
    
    **A. Dual BOM (untuk setiap SKU)**:
    - **BOM Purchasing**: Include 5-10% defect buffer per material
      - Fabric: 1000 meter + 5% waste = 1050 meter
      - Thread: 500 gram + 10% waste = 550 gram
    - **BOM Production**: Based on efficiency/standard consumption
      - Fabric: Actual consume 950 meter (efficiency 95%+)
      - Thread: Actual consume 480 gram (efficiency 96%+)
    
    **B. Dual MO System (2 Manufacturing Orders parallel)**:
    - **MO IKEA** (untuk IKEA & Pabrik - Fixed/Planning):
      - Dibuat dari PO IKEA menggunakan BOM Purchasing
      - Target: 1000 pcs (sesuai order IKEA)
      - Material requirement: 1050 meter fabric (dengan buffer)
      - Status: Fixed (tidak berubah, untuk IKEA reporting)
      - Fungsi: Planning & material procurement tracking
    
    - **MO Pabrik** (untuk Pabrik Only - Real-time/Execution):
      - Dibuat parallel dengan MO IKEA
      - Target: Flexible (daily target bisa berbeda, especially Sewing dept)
      - Material consumption: Real-time input daily oleh admin dept
      - Integrated dengan QC data: Defect count + Rework tracking
      - Status: Dynamic (update setiap hari based on actual production)
      - Fungsi: Actual production tracking & efficiency monitoring
    
    **C. Daily Production Flow**:
    - Admin dept input daily: Production output + Material consumption
    - System combine dengan QC data: Pass / Defect / Rework
    - Sewing dept: Daily target flexible (tidak harus match MO IKEA!)
      - Contoh: MO IKEA target 1000 pcs, tapi Sewing daily target 150 pcs/hari
      - MO Pabrik track actual: Day 1 = 145 pcs, Day 2 = 160 pcs, etc.
    - End of production: MO IKEA vs MO Pabrik akan beda → NORMAL!
      - MO IKEA: 1000 pcs (fixed planning)
      - MO Pabrik: 1050 pcs actual output (karena efficiency BOM Production)
    
    **D. Reconciliation Otomatis**:
    - System reconcile MO IKEA (planning) vs MO Pabrik (actual)
    - Dashboard show variance: +50 pcs (5% better efficiency) → GREEN
    - Management report: IKEA requirement fulfilled + efficiency gain visible
  
  - Safety stock threshold dengan alert system
  - Real-time stock sync (tidak delayed)
  - Manual adjustment workflow untuk edge cases

- **Hasil**: 
  - Material status ACCURATE → Production bisa jalan!
  - MO IKEA (planning) vs MO Pabrik (actual) reconciliation clear
  - Material planning akurat: Purchasing order based on BOM Purchasing
  - Production flexibility: Dept bisa set daily target sendiri (especially Sewing)
  - QC data terintegrasi dengan production tracking (IKEA audit ready!)
  - Efficiency monitoring real-time: Target vs Actual visible

---

### **2B. OPSI MO SYSTEM - EVALUASI 2 PENDEKATAN**

**PERTANYAAN KUNCI**: Apakah kita perlu 1 MO atau 2 MO parallel untuk handle IKEA requirement vs Factory flexibility?

---

#### **OPSI 1: Single MO (Untuk IKEA & Pabrik)**

**Konsep**:
- 1 Manufacturing Order untuk IKEA reporting & Factory execution
- MO dibuat dari PO IKEA menggunakan BOM Purchasing (dengan buffer)
- Admin dept input daily production & consumption ke MO yang sama
- QC data terintegrasi ke MO yang sama
- End result: MO akan update dari planning (1000 pcs) ke actual (1050 pcs)

**Pro**:
- ✅ **Simple**: Hanya 1 MO, tidak perlu manage 2 system parallel
- ✅ **User familiar**: Mirip dengan workflow Excel existing (1 order 1 tracking)
- ✅ **Training lebih cepat**: Admin hanya perlu belajar 1 MO workflow
- ✅ **Data consolidation mudah**: Semua data (planning + actual) dalam 1 MO
- ✅ **Reporting lebih simple**: Export 1 MO = dapat semua data

**Cons**:
- ❌ **MO target berubah-ubah**: 
  - MO awal: 1000 pcs (from IKEA order)
  - MO akhir: 1050 pcs (after production complete)
  - IKEA butuh report 1000 pcs, tapi sistem show 1050 pcs → Butuh manual adjustment!
- ❌ **Material calculation confusing**:
  - Material requirement awal: 1050 meter fabric (with buffer dari BOM Purchasing)
  - Material consumed: 950 meter fabric (actual dari BOM Production)
  - Variance 100 meter → Terlihat seperti "waste" padahal itu buffer!
- ❌ **Daily target flexibility terbatas**:
  - MO target 1000 pcs → Sewing dept susah set daily target berbeda
  - System akan selalu compare actual vs 1000 pcs (not flexible)
- ❌ **QC data mixing**:
  - Defect count tercampur dengan production output
  - Sulit track: "Berapa actual target vs berapa yang defect?"
- ❌ **IKEA reporting manual adjustment**:
  - IKEA butuh report fixed 1000 pcs, tapi MO final 1050 pcs
  - Admin harus manual adjust report sebelum kirim ke IKEA
- ❌ **Efficiency monitoring tidak clear**:
  - Tidak bisa compare planning vs actual (karena mixed dalam 1 MO)
  - Management tidak bisa lihat: "Kita lebih efisien berapa persen?"

**Rekomendasi Use Case**:
- Cocok jika: Production target selalu match IKEA order (no flexibility)
- Cocok jika: IKEA accept actual production output (bukan fixed reporting)
- Cocok jika: Tidak butuh efficiency monitoring

---

#### **OPSI 2: Dual MO (IKEA Fixed + Pabrik Dynamic)** ✅ RECOMMENDED

**Konsep**:
- 2 Manufacturing Orders parallel:
  - **MO IKEA**: Fixed planning untuk IKEA reporting (1000 pcs, tidak berubah)
  - **MO Pabrik**: Dynamic execution untuk Factory tracking (1050 pcs actual)
- MO IKEA dibuat dari PO IKEA menggunakan BOM Purchasing
- MO Pabrik dibuat parallel, admin input daily production & consumption
- QC data hanya ke MO Pabrik (IKEA tidak perlu tahu defect detail internal)
- End result: MO IKEA tetap 1000 pcs, MO Pabrik 1050 pcs (variance tracked)

**Pro**:
- ✅ **IKEA reporting clean**:
  - MO IKEA fixed 1000 pcs → Export langsung untuk IKEA, tidak perlu manual adjust!
  - Traceability clear: MO-IKEA-12345 untuk Order IKEA-98765
- ✅ **Factory flexibility penuh**:
  - MO Pabrik dynamic → Sewing dept bisa set daily target berbeda
  - Daily progress tracked independent dari IKEA requirement
- ✅ **Material calculation clear**:
  - MO IKEA: Material requirement 1050 meter (untuk Purchasing order)
  - MO Pabrik: Material consumed 950 meter (actual consumption)
  - Variance 100 meter → Jelas ini adalah buffer/efficiency gain!
- ✅ **QC data segregated**:
  - MO IKEA: Clean data untuk IKEA (no defect detail)
  - MO Pabrik: Full QC data (Pass / Defect / Rework) untuk internal monitoring
- ✅ **Efficiency monitoring real-time**:
  - Dashboard compare: MO IKEA (planning) vs MO Pabrik (actual)
  - Management lihat: "Target 1000 pcs, actual 1050 pcs = +5% efficiency!"
- ✅ **Daily target flexibility**:
  - Sewing dept: "Hari ini target 150 pcs" (tidak harus match MO IKEA 1000 pcs)
  - System track cumulative progress per MO Pabrik
- ✅ **Audit ready**:
  - IKEA audit: Show MO IKEA (clean, fixed, match order)
  - Internal audit: Show MO Pabrik (full detail, QC data, efficiency)

**Cons**:
- ❌ **Lebih complex**: 2 MO untuk manage (but system auto-create both!)
- ❌ **Training lebih lama**: Admin perlu belajar 2 MO workflow (estimated +1 week training)
- ❌ **Data entry double?**: NO! Admin hanya input ke MO Pabrik, MO IKEA auto-sync material requirement
- ❌ **Risk data inconsistency**: Mitigated by system validation (MO IKEA vs MO Pabrik linked)

**Rekomendasi Use Case**:
- ✅ Cocok jika: IKEA butuh fixed reporting (1000 pcs), tapi Factory butuh flexibility
- ✅ Cocok jika: Sewing dept butuh set daily target berbeda dari IKEA order
- ✅ Cocok jif: Management butuh efficiency monitoring (planning vs actual)
- ✅ Cocok jika: QC data harus terintegrasi tapi tidak exposed ke IKEA
- ✅ **RECOMMENDED untuk PT Quty Karunia!**

---

#### **TABEL PERBANDINGAN - OPSI 1 VS OPSI 2**

| Aspek | Opsi 1: Single MO | Opsi 2: Dual MO ✅ |
|-------|-------------------|-------------------|
| **Pelaporan IKEA** | Manual adjust (MO berubah) | Otomatis (MO IKEA tetap) |
| **Fleksibilitas Pabrik** | Terbatas (target tetap) | Penuh (target harian fleksibel) |
| **Kalkulasi Material** | Membingungkan (buffer+aktual tercampur) | Jelas (planning vs aktual terpisah) |
| **Data QC** | Mixed dengan production | Terpisah (internal saja) |
| **Monitoring Efisiensi** | Tidak jelas (data tercampur) | Real-time (planning vs aktual) |
| **Waktu Pelatihan** | 2-3 minggu | 3-4 minggu (+1 minggu) |
| **Kompleksitas User** | Sederhana (1 MO) | Sedang (2 MO, tapi otomatis dibuat) |
| **IKEA Audit** | Perlu pembersihan manual | Bersih (tampilkan MO IKEA saja) |
| **Target Harian Sewing** | Susah (harus match MO) | Mudah (target independen) |
| **Variance Akhir** | Terlihat error (+50 pcs) | Gain tercatat (+5% efisiensi) |
| **Rekomendasi** | Jika tidak butuh fleksibilitas | ✅ **Direkomendasikan!** |

---

#### **KEPUTUSAN REKOMENDASI: OPSI 2 (DUAL MO)** ✅

**Alasan**:
1. **IKEA compliance**: Fixed reporting tanpa manual adjustment
2. **Factory flexibility**: Sewing dept butuh daily target berbeda (proven requirement!)
3. **Efficiency visibility**: Management butuh monitoring planning vs actual
4. **QC integration**: Data defect/rework harus ada tapi tidak exposed ke IKEA
5. **Scalability**: Dual MO system bisa handle future complexity (multiple customers)

**Trade-off yang acceptable**:
- +1 week training time → Worth it untuk long-term flexibility
- 2 MO management → Mitigated by auto-creation & system validation

**Kalau mau safe approach**:
- Phase 1 (3 bulan pertama): Pakai Opsi 1 (Single MO) untuk user familiar
- Phase 2 (bulan 4-6): Upgrade ke Opsi 2 (Dual MO) setelah user comfortable
- **TAPI**: Kami rekomendasi langsung Opsi 2 dari awal! (One-time training pain vs long-term manual adjustment pain)

---

**3. Reporting & Data Integration (Enhanced)**
- **Solusi**: 
  - Export to Excel/CSV untuk semua reports
  - API integration untuk custom reporting tools
  - Dashboard configurable per user role
  - Scheduled reports (auto-email daily/weekly)
- **Hasil**: Management tetap bisa analyze di Excel jika perlu

**4. Partnership Approach (Critical Difference!)**
- **Pendekatan Baru**: 
  - Discovery workshop BEFORE commit (understand business process dulu)
  - Gap analysis transparent: What's standard vs what needs custom
  - Phased implementation: Prove value incrementally
  - Change management program: Training + adoption support
  - Post-implementation hypercare 2-3 bulan
- **Komitmen**: "ERP harus fit business, bukan sebaliknya"

**5. UOM Conversion (Configured Correctly)**
- **Solusi**:
  - Configure multi-unit per material: ROLL/YARD/KG/BOX/Pallet
  - **Suplier-specific conversion rates**:
    - Suplier A: 1 ROLL = 50 YARD, Suplier B: 1 ROLL = 45 YARD
    - System auto-pilih conversion rate berdasarkan suplier saat receiving
  - **Production-specific conversion** (PENTING!):
    - BOM menggunakan unit production: Fabric dalam METER, Thread dalam GRAM
    - Warehouse stock dalam unit purchasing: Fabric dalam ROLL, Thread dalam KG
    - System auto-convert saat material consumption
    - Contoh: BOM butuh 2.5 METER fabric → System deduct 0.05 ROLL dari stock (1 ROLL = 50 METER)
    - Contoh: BOM butuh 150 GRAM thread → System deduct 0.15 KG dari stock
  - **Pallet-level tracking untuk Finished Goods**:
    - Production output dalam PCS
    - Packing dalam CARTON (24 pcs/carton)
    - Shipping dalam PALLET (24 carton/pallet = 576 pcs/pallet)
    - System auto-calculate IKEA pallet requirement (karton harus GENAP per pallet!)
  - Auto-conversion di semua transaksi: Receiving, Production, Transfer, Shipping
  - Testing scenarios before go-live (verify semua conversion akurat)
- **Hasil**: 
  - Stock calculation akurat di warehouse & production level!
  - No manual conversion Excel lagi!
  - Purchasing terima dalam ROLL, Production consume dalam METER (seamless!)

**6. UI/UX Customization (User-Friendly)**
- **Solusi**:
  - Simplified menu structure (1-2 klik untuk fungsi sering dipakai)
  - Bahasa Indonesia untuk field labels & instructions
  - Mobile-optimized views untuk admin lantai produksi
  - Hide irrelevant fields per role (Production user tidak lihat Accounting fields)
  - Custom dashboards per department
- **Hasil**: User adoption rate tinggi, training time reduced 50%!

**7. MO Auto-Generation dari Purchase Order yang dibuat Purchasing**
- **Solusi - Dual MO System**:
  - Purchasing create PO IKEA → System auto-generate **2 MO parallel**:
    
    **MO IKEA** (Planning/Fixed):
    - Link traceability: MO-IKEA-12345 untuk Order IKEA-98765
    - Auto-populate: Quantity, SKU, deadline dari PO IKEA
    - Menggunakan BOM Purchasing (with defect buffer)
    - Material requirement calculation untuk Purchasing
    - Status: **Fixed** (tidak berubah, untuk IKEA reporting & traceability)
    - View access: IKEA, Management, Purchasing
    
    **MO Pabrik** (Execution/Dynamic):
    - Link ke MO IKEA: MO-FAC-12345 (linked to MO-IKEA-12345)
    - Same: Quantity, SKU, deadline (initial)
    - Menggunakan BOM Production (efficiency-based)
    - Daily input oleh admin dept: Production output + Material consumption
    - Integrated QC data: Pass / Defect / Rework per checkpoint
    - Status: **Dynamic** (update daily based on actual)
    - View access: Factory Manager, SPV, Admin dept, QC
    
  - Admin Production hanya perlu review & confirm (tidak manual create!)
  - Flexible daily target: Sewing dept bisa set target berbeda dari MO IKEA
    - Contoh: MO IKEA = 1000 pcs, Sewing daily target = 140-160 pcs/hari (adjust per line capacity)
  
- **Hasil**: 
  - Zero admin overhead untuk create MO!
  - Full traceability: IKEA requirement vs Factory actual
  - Flexibility: Dept bisa manage daily target sendiri
  - QC data integrated: Defect & rework tracked per MO Pabrik
  - End-of-production reconciliation: MO IKEA vs MO Pabrik variance visible (efficiency monitoring)

**8. WO Auto-Generation dengan Routing Configured**
- **Solusi**:
  - Configure routing: 1 **MO Pabrik** → 5 WO/SPK auto-generated (Cutting, Embr, Sewing, Finishing, Packing)
  - Sequential dependency: WO Sewing baru bisa start after WO Embr done
  - **WO/SPK Dynamic Tracking**:
    - Admin dept input daily: Production output + Material consumption
    - QC checkpoint integrated: Pass / Defect / Rework per WO
    - Sewing dept: Daily target flexible (bisa berbeda dari MO IKEA target)
      - WO Sewing: Day 1 target 150 pcs, Day 2 target 140 pcs (adjust per line)
      - System track cumulative: Total progress vs MO target
  - Real-time visibility: Dashboard show production stage per MO
  - Shop floor app: Workers lihat WO hari ini (tidak perlu WhatsApp admin!)
- **Hasil**: 
  - 5x efficiency gain, full visibility, zero manual WO creation!
  - Daily flexibility: Dept manage target sendiri
  - QC data integrated per WO: Defect tracking per department
  - Real-time progress monitoring: Cumulative output vs MO target

---

### Ringkasan: Mengapa Kali Ini Akan Berhasil?

| Aspek | Odoo 2023 (GAGAL) | Odoo 2026 (RENCANA) |
|-------|-------------------|---------------------|
| **Setup BOM** | Input manual satu per satu | Import massal + Dual BOM (Purchasing + Produksi) |
| **Sistem MO** | Single MO (variance membingungkan) | Dual MO (IKEA tetap + Pabrik dinamis) |
| **Status Material** | Selalu MERAH (blocking) | Akurat real-time |
| **Pelaporan** | Terjebak di sistem | Export/API tersedia |
| **Konversi UOM** | Salah/tidak dikonfigurasi | Multi-unit (suplier + produksi) |
| **UI/UX** | Kompleks, hanya Bahasa Inggris | Disederhanakan, Bahasa Indonesia |
| **Pembuatan MO** | Manual oleh admin | Otomatis dari PO (Dual MO paralel) |
| **Pembuatan WO** | Manual per dept (5x kerja!) | Otomatis dengan routing + tracking harian |
| **Pelatihan User** | Minimal (diasumsikan mudah) | Komprehensif + dukungan berkelanjutan |
| **Implementasi** | Big bang (sekaligus) | Bertahap (buktikan nilai dulu) |

**Perbedaan Kunci**: Kali ini kami demand **partnership**, bukan Suplier-client transactional. Sales Odoo harus commit untuk customize & support, atau kami tidak proceed.

---

## 11 PAIN POINTS KRITIS

| # | Pain Point | Impact |
|---|------------|--------|
| 1 | Material shortage tiba-tiba | Production stop, overtime, emergency purchasing |
| 2 | Tidak tahu WIP real-time | Planning impossible, bottleneck detection delayed |
| 3 | Quality defect traceable manual (Excel terpisah) | Tidak terintegrasi, IKEA audit risk, sulit root cause analysis |
| 4 | Mix Label risk (Finishing-Packing) | IKEA REJECT! Salah lihat datestamp/destination, no validation |
| 5 | Dual trigger system manual | Admin overwhelmed, packaging error frequent |
| 6 | Excel-based planning | Error prone, single point of failure |
| 7 | Target produksi flat | Shortage frequent (tidak hitung defect rate) |
| 8 | Manual material tracking | Admin time wasted 2-3 jam/hari |
| 9 | Stock opname 1 hari penuh | Production stop untuk counting |
| 10 | Rework tidak ter-record | Cost tidak tahu, IKEA audit concern |
| 11 | Multi-unit conversion manual (Purchasing & Production) + Pallet calculation | UOM error: Purchasing terima ROLL consume METER, Thread KG consume GRAM. Pallet IKEA rules complex (24 karton genap per pallet). Manual Excel formula prone error! |

**CRITICAL**: Pain point #4 (Mix Label) adalah **high-risk** untuk IKEA compliance! Operator sering salah lihat Week/Destination di Finishing & Packing, menyebabkan mix label saat dispatch. Tidak ada pengecekan kembali setelah packing selesai → IKEA reject baru ketahuan!

---

## ILUSTRASI WORKFLOW

**NOTE**: Di PT Quty Karunia, **PURCHASING adalah trigger utama** material planning. PPIC tidak menjalankan fungsi planning seperti perusahaan manufacturing lain. Purchasing yang input kebutuhan material dan melakukan pembelian.

### 1. Current Manual Process (SEKARANG) - START FROM PURCHASING

```
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Terima order                                       │
│  - Lihat order: SKU apa, quantity berapa, production plan kapan │
│  - Buka Excel BOM untuk tiap SKU yang di-order                  │
│  - Calculate material needed (pakai Excel!)                     │
│    ❌ Problem: Harus calculate dari PALLET basis!               │
│       IKEA rules: Jumlah karton per pallet HARUS GENAP!         │
│       Example: 1 pallet = 24 karton → Order 1000 pcs tetap     │
│       harus calculate: Berapa pallet? Sisa karton genap tidak?  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Calculate & check stock material                   │
│  - Multi-unit conversion MANUAL (ROLL → PCS, KG → GRAM)         │
│    ❌ Problem: UOM error frequent! (Purchasing bukan technical!)│
│       Example: Fabric 1 ROLL = 50 meter, tapi suplier A = 45m! │
│  - Pallet calculation MANUAL (IKEA pallet rules!)               │
│    ❌ Problem: Karton per pallet harus GENAP sesuai IKEA rule!  │
│       Example: Calculate 1523 pcs → Berapa pallet + sisa karton?│
│       Manual Excel formula: ROUNDUP(1523/pcs_per_karton/24)     │
│  - Check stock di Excel warehouse (data delay 1-2 jam!)         │
│  - Calculate: Material mana yang harus di-order                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Create PO manual di Excel                          │
│  - Copy-paste data material (resiko typo tinggi!)               │
│  - Email manual ke suplier (attachment Excel/PDF)               │
│  - Track delivery: Email suplier "Sudah kirim belum?"           │
│  - Record manual di Excel tracking: "PO-001 status: Pending"    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  MATERIAL DATANG: Warehouse Admin terima (packing list)         │
│  - Catat manual: Material apa, quantity berapa, dari PO mana    │
│  - End-of-day baru input ke Excel (salah entry!)                │
│  - Purchasing update Excel tracking manual                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Cek Excel stock, inform production ready/not       │
│  Problem: Excel data outdated (delay 1-2 jam dari actual WH)    │
│  Problem: "Material cukup tidak untuk order ini?" → Manual check│
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION: Start production & material consumption            │
│  - Dept Admin catat manual di form kertas (per departemen)      │
│  - End-of-day: Input consumption ke Excel                       │
│  - Reconcile: Warehouse stock vs Production usage (2-4 jam!)    │
│  - Sering tidak match → Meeting produksi                        │
└─────────────────────────────────────────────────────────────────┘

❌ PAIN POINTS:
- Purchasing overwhelmed: Terima order → Calculate manual → Track PO → Inform production
- Excel BOM: 478 SKU dengan 15-30 material each (nightmare!)
- Multi-unit conversion: UOM error frequent (ROLL/KG/PCS confusion, Purchasing bukan technical)
- Pallet calculation: IKEA pallet rules complex (karton per pallet harus GENAP, manual Excel formula)
- Stock visibility: "Material cukup tidak?" → Delay jawaban 1-2 jam
- Reconciliation: Warehouse vs Production data tidak match (CHAOS!)
```

---

### 2. Planned Odoo Workflow (2026) - START FROM PURCHASING

```
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Terima order IKEA, input ke Odoo                   │
│  - Buka Odoo Purchasing module                                  │
│  - Pilih SKU yang di-order IKEA                                 │
│  - Input quantity yang dibutuhkan                               │
│  - Click "Calculate Material" → System AUTO-EXPLODE BOM         │
│  - Multi-unit conversion AUTOMATIC (ROLL → PCS, KG → GRAM)      │
│  - Pallet calculation AUTOMATIC (IKEA pallet rules built-in!)   │
│    ✅ System auto-calculate pallet: Karton per pallet GENAP!    │
│    ✅ Example: 1523 pcs → System calculate: 4 pallet (24 karton)│
│       No manual Excel formula lagi!                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  ODOO: Check stock real-time & generate requirement list        │
│  - System check: Warehouse + In-Transit + Reserved stock        │
│  - Calculate: Material kurang berapa untuk order ini            │
│  - Auto-create Purchase Requisition list                        │
│  - Dashboard Purchasing: "15 material perlu order sekarang"     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Review requisition & Create PO (1-click)           │
│  - Quantity SUDAH CALCULATED (tidak perlu kalkulator!)          │
│  - Suplier auto-suggested (dari database preferred suplier)     │
│  - Click "Create PO" → PO auto-generate semua detail            │
│  - Email PO auto-send ke suplier                                │
│  - Dashboard tracking: PO status real-time                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  MATERIAL DATANG: Warehouse receive di Odoo (scan/manual)       │
│  - Select PO yang diterima (list dari sistem)                   │
│  - Confirm quantity (validation: tidak boleh over-receive)      │
│  - Click "Validate" → Stock AUTO-UPDATE REAL-TIME!              │
│  - Notification auto ke Purchasing: "PO-12345 received"         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Dashboard tampil "Material Available"              │
│  - Material status: GREEN (semua available untuk order ini)     │
│  - Koordinasi ke Production: "Order X material ready, start!"   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION: Start production, material AUTO-CONSUMED           │
│  - Material consumption AUTO-BACKFLUSH dari BOM                 │
│  - System deduct stock automatic (no manual input!)             │
│  - Real-time balance update (Purchasing lihat dashboard)        │
│  - Reconciliation: AUTOMATIC! (tidak perlu meeting 2-4 jam!)    │
└─────────────────────────────────────────────────────────────────┘

✅ BENEFITS FOR PURCHASING (PRIMARY USER):
- Terima order IKEA → Input Odoo → System calculate semua!
- Tidak perlu Excel BOM 478 SKU lagi!
- Tidak perlu kalkulator manual!
- Multi-unit conversion automatic (no error ROLL/KG!)
- Pallet calculation automatic (IKEA pallet rules built-in, karton GENAP per pallet!)
- Stock visibility real-time (tidak delay 1-2 jam!)
- PO tracking automatic (tidak Email suplier terus!)
- Dashboard clear: "Material mana yang ready/pending untuk order mana"

✅ BENEFITS FOR PRODUCTION:
- Material status accurate (tidak RED palsu!)
- Tahu order mana yang bisa start (tidak tanya Purchasing terus!)
- Consumption automatic (tidak manual catat kertas!)
- Reconciliation automatic (tidak meeting 2-4 jam!)
```


### 3. Material Status: Root Cause Problem 2023 vs Solution 2026

**Odoo 2023 (FAILED) - Kenapa Material Selalu MERAH?**
```
Day 1: PO created di Odoo
  ↓
Day 5: Material datang (suplier delivery)
  ↓
Warehouse Admin: Terima material (physical)
  ↓
❌ MASALAH: Warehouse tidak tahu cara "Receive PO" di Odoo
  ↓
Result: Material ada di WH (physical) tapi stock di Odoo = 0
  ↓
System: Status MERAH "Material not available"
  ↓
SPV: Bingung, "Material sudah datang kok system RED?"
  ↓
Admin: Manual override (lost traceability)
  ↓
ATAU: Production STOP karena system block (padahal material ada!)
  ↓
Frustasi → Balik ke Excel → Odoo ditinggalkan
```

**Odoo 2026 (PLANNED) - Bagaimana Fix Problem Ini?**
```
Day 1: PO created di Odoo
  ↓
Day 5: Material datang (suplier delivery)
  ↓
Warehouse Admin: Buka Odoo → "Receive Products" screen
  ↓ [TRAINING PROPER!]
✅ Step 1: Scan barcode PO (atau select manual)
✅ Step 2: Confirm quantity received
✅ Step 3: Click "Validate" → Stock AUTO-UPDATE
  ↓
System: Material stock = AVAILABLE (GREEN)
  ↓
MO: Auto-change status "Ready to Produce"
  ↓
Notification ke SPV: "Batch X bisa start production"
  ↓
Production: Start dengan data ACCURATE
  ↓
✅ RESULT: Smooth flow, no blocking palsu!
```

**Key Improvements 2026**:
- ✅ **Training proper** untuk Warehouse team (2023 tidak ada training!)
- ✅ **Mobile app** untuk receive (easier vs desktop only)
- ✅ **Validation mandatory** (cannot skip receive step)
- ✅ **Visual dashboard** untuk receiving status (tracking jelas)

---

### 4. Dual PO Trigger - Unique Requirement (IKEA Workflow)

**Masalah**: 1 Manufacturing Order butuh 2 Purchase Order dengan timing berbeda
- **PO Fabric**: Purchasing order ke Suplier Fabric → Datang Week 0
- **PO Label**: Purchasing order ke Suplier Label → Datang Week +2 (IKEA kirim Label info terlambat 2 minggu!)

Production HARUS start dari PO Fabric (Week 0), tapi TIDAK BOLEH sampai Packing tanpa PO Label (Week +2).

**Kenapa Harus Begini?**
- IKEA baru finalize Label info (Week number, Destination) 2 minggu setelah order
- Fabric bisa di-order langsung, tapi Label HARUS tunggu info final dari IKEA
- Production tidak bisa tunggu 2 minggu baru start (lead time terlalu lama!)
- Tapi Packing tidak boleh salah destination (IKEA reject!)

**Current Manual (Error Prone)**:
```
Week 0: Purchasing create PO Fabric ke suplier → Material Fabric datang
  ↓
Admin Excel: Mark "Boleh Cutting & Embroidery ONLY"
  ↓
WhatsApp broadcast: "JANGAN start Sewing dulu! Tunggu PO Label!"
  ↓
[WAITING 2 WEEKS... WhatsApp message buried 500 messages deep]
  ↓
Week 2: IKEA finalize Label info → Purchasing create PO Label → Material datang
  ↓
Admin Excel: Update week number & destination dari Label info
  ↓
WhatsApp broadcast: "Sekarang boleh lanjut production full!"
  ↓
❌ RISK: Admin lupa broadcast → Sewing start duluan → 
         Salah packaging destination → IKEA REJECT!
```

**Planned Odoo (Automated State Management)**:
```
Week 0: Purchasing create PO Fabric di Odoo → Send to suplier
  ↓
Material Fabric received (Warehouse validate PO Fabric)
  ↓
System: Detect "PO Fabric received for Order IKEA-12345"
  ↓
Automatic Action:
  ✅ MO status → "PARTIAL RELEASED"
  ✅ UNLOCK: Cutting WO + Embroidery WO (bisa start!)
  ✅ LOCK: Sewing WO + Finishing WO + Packing WO (blocked!)
  ✅ Field "Week" & "Destination" → Editable (belum final dari IKEA)
  ↓
Cutting & Embroidery: Mulai production (material fabric ready)
Sewing-Packing: BLOCKED by system (tunggu PO Label!)
  ↓
[WAITING... System maintain lock status]
  ↓
Factory Manager finalize Label → Purchasing create PO Label di Odoo
  ↓
Material Label received (Warehouse validate PO Label)
  ↓
System: Detect "PO Label received for Order IKEA-12345"
  ↓
Automatic Action:
  ✅ MO status → "FULL RELEASED"
  ✅ AUTO-INHERIT Week & Destination dari PO Label ke MO
  ✅ UNLOCK: ALL remaining work orders (Sewing, Finishing, Packing)
  ✅ LOCK field "Week" & "Destination" → Read-only (cannot change lagi!)
  ↓
All departments: Continue production sampai Packing dengan destination correct
  ↓
✅ RESULT: Zero packaging error! System auto-inherit Label info!
```

**Manfaat**: 
- Admin tidak perlu track manual
- System automatis enforce business rule (tidak bisa skip!)
- Week & Destination auto-inherit dari PO Label (no manual copy-paste error!)

**Manfaat**: Admin tidak perlu track manual atau WhatsApp. System automatis enforce business rule!

---

### 5. Production Flow - Department by Department

**NOTE**: Production di PT Quty Karunia melewati 5 departemen sequential. Tidak ada MO (Manufacturing Order) formal yang mengkoordinasi semua WO/SPK departemen. Tiap dept memiliki jadwal produksi sendiri (dari meeting dengan Factory Manager). Admin dept hanya catat consumption & daily production di Excel.

**Penjelasan**:
- **MO (Manufacturing Order)** = Order manufaktur untuk 1 artikel/SKU yang memuat keseluruhan WO dari semua departemen
- **WO/SPK** = Work Order/Surat Perintah Kerja per departemen (bagian dari MO)

#### Current Manual Production Process (SEKARANG)

```
┌─────────────────────────────────────────────────────────────────┐
│  FACTORY MANAGER: Monthly/Weekly Production Meeting             │
│  - Meeting dengan SPV semua departemen                          │
│  - Diskusi: SKU apa yang harus produksi, target berapa          │
│  - Tentukan jadwal produksi per dept (tidak sinkron!)           │
│    Example: Cutting start minggu ini, Embroidery minggu depan   │
│  - TIDAK ada MO formal yang koordinasi semua dept WO!           │
│  - TIDAK ada WO/SPK tertulis per departemen!                    │
│  - Hanya verbal agreement + note di Excel masing-masing dept    │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING: Ambil material dari Warehouse (Surat Jalan)      │
│  - Admin Cutting: Buat surat jalan manual (kertas)              │
│    "Ambil Fabric SKU-001, 100 ROLL untuk produksi Bear"         │
│  - Warehouse: Catat pengeluaran material di Excel               │
│  - Admin Cutting: Catat consumption di Excel dept               │
│    ❌ Problem: Surat jalan & Excel sering tidak match!          │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING: Start production (tanpa MO reference!)           │
│  - Admin dept: Lihat jadwal dari Excel/note meeting             │
│  - Operator cutting: Material Fabric → Cut pieces               │
│  - QC CUTTING: Inspector check cut pieces quality (manual!)     │
│    Verbal report ke Admin QC: "Pass 1050, Defect 30"            │
│  - Admin QC (1 orang): Record ke Excel QC Master                │
│    Data input: Defect count: 30, Lolos: 1050, Total QC: 1080   │
│    Production output: 1050 pcs (per hari)                       │
│    ❌ Problem: Admin QC harus manual consolidate 4 checkpoints! │
│    ❌ Problem: QC data di Excel terpisah dari production Excel! │
│       (IKEA audit compliance RISK!)                             │
│    Rework: Re-cut pieces yang tidak sesuai spec (verbal only!)  │
│    ❌ Problem: Rework TIDAK tracked! Tidak tahu cost!           │
│  - Admin dept catat: Daily production output (Excel dept)       │
│    Example: "Hari ini: 1050 pcs cut pieces untuk SKU Bear"     │
│  - Traceability card: Dibuat manual per dept (Excel terpisah)  │
│    ❌ Problem: Manual & terpisah tiap dept! Sulit konsolidasi!  │
│    ❌ Problem: Audit IKEA butuh data terintegrasi, bukan Excel! │
│  - End-of-day: Admin dept + Admin QC input ke Excel masing2     │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING → EMBROIDERY: Transfer material (manual track)    │
│  - Admin Cutting: Catat transfer "1050 pcs pass QC ke Embr"     │
│  - Admin Embroidery: Catat receiving "1050 pcs dari Cutting"    │
│    ❌ Problem: Sering tidak match! Cutting catat 1050, Embr 1020│
│  - Tidak ada surat jalan internal (hanya verbal!)               │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT EMBROIDERY: Production dengan jadwal sendiri              │
│  - Admin dept: Lihat jadwal dari Excel/note meeting             │
│  - Production: Cut pieces → Embroidered pieces                  │
│  - Admin dept catat: Daily production output (Excel)            │
│    Example: "Hari ini: 1060 pcs embroidered untuk SKU Bear"     │
│  - End-of-day: Admin input consumption & output ke Excel dept   │
│    Input: Thread consumption, Output: 1060 pcs embroidered      │
│    ❌ Problem: Tidak tahu sisa WIP Cutting berapa!              │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT EMBROIDERY → SEWING: Transfer material (manual track)     │
│  - Admin Embroidery: Catat transfer "1060 pcs ke Sewing"        │
│  - Admin Sewing: Catat receiving "1060 pcs dari Embroidery"     │
│    ❌ Problem: Sering delay entry! Embr input hari ini, Sewing  │
│       input besok → Data tidak sync!                            │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT SEWING: Production dengan jadwal sendiri (38 LINES!)      │
│  - Operasional: 38 sewing lines parallel production             │
│  - Admin dept: Lihat jadwal dari Excel/note meeting             │
│  - Production: Embroidered pieces → Sewn bodies                 │
│    ❌ Problem: 38 lines = 38 tracking points! (chaos!)          │
│    Admin dept: Track output PER LINE (manual Excel nightmare!)  │
│  - QC SEWING: Inspector check sewn bodies quality (manual!)     │
│    Verbal report ke Admin QC: "Pass 1010, Defect 30"            │
│  - Admin QC (1 orang): Record ke Excel QC Master                │
│    Data input: Defect count: 30, Lolos: 1010, Total QC: 1040   │
│    Production output: 1010 pcs (per hari)                       │
│    ❌ Problem: Admin QC TIDAK tahu defect dari line mana!       │
│    ❌ Problem: Cannot analyze line performance untuk NG rate!   │
│    Rework: Kembalikan ke line untuk re-sewing (verbal only!)    │
│    ❌ Problem: Rework TIDAK tracked! Line mana yang banyak NG?  │
│  - Admin dept catat: Daily production output per line (Excel)   │
│    Example: "Line 1: 28 pcs, Line 2: 26 pcs, ... Line 38: 24"   │
│    Total: "Hari ini: 1010 pcs sewn untuk SKU Bear"              │
│  - Traceability card: Dibuat manual per batch (Excel terpisah) │
│    ❌ Problem: Manual, terpisah per line, sulit konsolidasi!    │
│  - End-of-day: Admin dept + Admin QC input ke Excel masing2     │
│    Input: Thread consumption aggregate, Output: 1010 pcs sewn   │
│    ❌ Problem: TIDAK tahu order IKEA mana ini! (no reference!)  │
│    ❌ Problem: Track 38 lines manual = 2-3 jam/hari admin time! │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT SEWING → FINISHING: Transfer material (manual track)      │
│  - Admin Sewing: Catat transfer "1010 pcs pass QC ke Finishing" │
│  - Admin Finishing: Catat receiving "1010 pcs dari Sewing"      │
│    ❌ Problem: Sering admin lupa catat! → Reconciliation chaos! │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT FINISHING: Production 2-stage (intermediate tidak tracked)│
│  - Admin dept: Lihat jadwal dari Excel/note meeting             │
│  - Stage 1 (Stuffing): Skin + Filling → Stuffed Body            │
│    Admin catat: Daily output "1010 pcs stuffed" (Excel)         │
│    ❌ Problem: Stock intermediate "Stuffed Body" TIDAK tracked! │
│       Tidak tahu berapa WIP Stage 1 vs Stage 2!                 │
│  - Stage 2 (Closing): Stuffed Body + Tag → Finished Doll        │
│    Admin catat: Daily output "1010 pcs finished" (Excel)        │
│  - Operator: Lihat Label info manual dari Excel/Email IKEA      │
│    Cari: "SKU Bear untuk Week berapa ya? Destination mana?"     │
│    ❌ RISK: Salah lihat datestamp/destination! (human error!)   │
│       Example: "Week 08" tapi salah baca jadi "Week 07"         │
│  - QC FINISHING: Inspector check finished quality (manual!)     │
│    Verbal report ke Admin QC: "Pass 1000, Defect 10"            │
│  - Admin QC (1 orang): Record ke Excel QC Master                │
│    Data input: Defect count: 10, Lolos: 1000, Total QC: 1010   │
│    Production output: 1000 pcs (per hari)                       │
│    ❌ Problem: Admin QC TIDAK tahu defect dari Stage 1 atau 2!  │
│    Rework: Kembalikan ke Stage 2 untuk re-closing (verbal!)     │
│    ❌ Problem: Rework TIDAK tracked! Tidak tahu defect pattern! │
│  - Traceability card: Dibuat manual per batch (Excel terpisah) │
│    ❌ Problem: Manual & terpisah, sulit untuk audit IKEA!       │
│  - End-of-day: Admin dept + Admin QC input ke Excel masing2     │
│    Input: Filling consumption, Output: 1000 pcs                 │
│    ❌ Problem: Tidak catat Stuffed Body intermediate!           │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT FINISHING → PACKING: Transfer material (manual track)     │
│  - Admin Finishing: Catat transfer "1000 pcs pass QC ke Packing"│
│    Note: Week & Destination info (dari salah lihat tadi!)       │
│  - Admin Packing: Catat receiving "1000 pcs dari Finishing"     │
│    ❌ Problem: Tidak ada Label info di system! Manual cari!     │
│    ❌ RISK: Info dari Finishing sudah salah! (Mix Label!)       │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT PACKING: Packing production (tanpa QC!)                   │
│  - Admin dept: Lihat jadwal dari Excel/note meeting             │
│  - Operator: Lihat Label info dari Finishing (verbal/note)      │
│    Atau cari sendiri: "SKU Bear, Week berapa ya? Destination?"  │
│    ❌ RISK: Salah lihat datestamp/destination! (human error!)   │
│       Example: Finishing bilang "Week 08" tapi operator dengar    │
│       "Week 07" → Packing pakai Label Week 07! (MIX LABEL!)      │
│  - Packing: Group by Week & Destination (manual lihat Label!)   │
│    ❌ CRITICAL PROBLEM: MIX LABEL!                               │
│       Week 08 products + Week 07 Label = IKEA REJECT!           │
│       Destination Sweden + Label Germany = IKEA REJECT!         │
│  - Admin dept catat: Daily packing output (Excel)               │
│    Example: "Hari ini: 1000 pcs packed untuk SKU Bear"          │
│    ❌ FREQUENT PROBLEM: QTY KURANG saat packing!                │
│       Dari Finishing: 1000 pcs → Packing result: 980 pcs only! │
│       Missing 20 pcs! Entah hilang atau tidak tercatat!        │
│       Tidak tahu hilang di mana: Transfer? Packing process?    │
│  - Transfer ke Warehouse FG: Manual catat (Excel)               │
│    ❌ Problem: TIDAK ADA PENGECEKAN KEMBALI setelah packing!    │
│       No validation apakah Label correct atau tidak!            │
│       Mix label baru ketahuan saat IKEA complain!               │
│  - End-of-day: Admin input ke Excel dept                        │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  QC FINISHED GOODS: Inspection per pallet sebelum loading       │
│  - Unit: PER PALLET (bukan per pcs!)                            │
│  - QC Inspector: Check pallet sebelum loading ke container      │
│  - Check: Packaging, Label, Week number, Destination per pallet │
│    Verbal report ke Admin QC: "Pass 15 pallet, Defect 2 pallet" │
│  - Admin QC (1 orang): Record ke Excel QC Master                │
│    Data input: Defect pallet: 2, Lolos pallet: 15, Total: 17   │
│    Production output: 15 pallet (per hari, ready dispatch)      │
│    ❌ Problem: Admin QC handle 4 checkpoints sendirian!         │
│       (Cutting, Sewing, Finishing, FG) = overwhelmed!           │
│    ❌ Problem: QC data di Excel terpisah dari MO/production!    │
│       (IKEA audit compliance RISK! Cannot trace defect to MO!)  │
│  - Rework: Kembalikan ke Packing untuk re-pack pallet (verbal!) │
│    ❌ Problem: Rework TIDAK tracked! Tidak tahu root cause!     │
│  - Traceability card: Dibuat manual per pallet (Excel terpisah) │
│    ❌ Problem: 4 checkpoints = 4 Excel terpisah per batch!      │
│    ❌ Problem: Manual konsolidasi untuk IKEA audit = nightmare! │
│  - Pass QC: Pallet ready for loading ke container               │
│  - End-of-day: Admin QC input semua QC result ke Excel Master   │
│    Consolidate: 4 checkpoints × multiple batches = chaos!       │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  END-OF-DAY: Reconciliation nightmare!                          │
│  - Factory Manager: Konsolidasi Excel dari 5 dept (manual!)     │
│  - Admin QC (1 orang): Konsolidasi Excel QC dari 4 checkpoints! │
│    (Cutting, Sewing, Finishing, FG) → Manual entry overwhelm!   │
│  - Cross-check: Dept A output = Dept B input? (sering NO MATCH!)│
│    Example: Cutting 1050, Embroidery receive 1020 → Selisih 30!│
│    Example: Finishing 1000, Packing result 980 → Missing 20 pcs!│
│    ❌ FREQUENT di Packing: QTY kurang! Hilang atau tidak catat? │
│  - Cross-check QC: Production output vs QC data match? (chaos!) │
│    Example: Cutting output 1050 vs QC data 1050 ✓               │
│    Tapi Sewing output 1040 vs QC data 1010 → Selisih 30!        │
│  - QC data: Consolidate dari 4 QC checkpoints (Cutting, Sewing, │
│    Finishing, FG) → TIDAK ada pattern analysis!                 │
│  - Meeting 2-4 jam: "Kemana 30 pcs hilang? Rusak? Lupa catat?"  │
│  - Track down: Cek Excel dept + Excel QC, interview operator    │
│    ❌ Problem: 2 Excel files (production + QC) tidak terintegrasi│
│  - Manual adjustment di Excel (lost audit trail!)               │
│  - Update WIP status manual untuk management report             │
│  - Estimate completion: TIDAK BISA! (tidak tahu bottleneck!)    │
│    "SKU Bear kapan selesai?" → "Tidak tahu pak, kira-kira..."   │
└─────────────────────────────────────────────────────────────────┘

❌ PAIN POINTS PRODUCTION:
- TIDAK ada MO formal yang koordinasi semua WO departemen!
- TIDAK ada WO/SPK tertulis per departemen! (Hanya verbal dari meeting!)
- Tiap dept jadwal sendiri-sendiri, tidak sinkron!
- Surat jalan material: Manual & sering tidak match dengan Excel!
- Daily production input: HANYA consumption & output, no context!
- Traceability card: Manual per dept (Excel terpisah), sulit konsolidasi untuk audit IKEA!
- Admin tiap dept: 2-3 jam/hari HANYA untuk data entry Excel!
- QC data di Excel terpisah dari production Excel! (tidak terintegrasi!)
- Dept Sewing: 38 lines = 38 tracking points manual! (nightmare!)
- QC checkpoints: 4 locations (Cutting, Sewing, Finishing, FG) manual!
- QC data & traceability: Manual per dept, tidak terintegrasi, sulit untuk IKEA audit!
- Rework: Rework tercatat secara manual, diinput oleh admin QC excel
- MIX LABEL CRITICAL RISK! Finishing & Packing salah lihat datestamp/destination!
- TIDAK ada pengecekan kembali setelah packing! (Mix label baru ketahuan IKEA reject!)
- Dept Packing: QTY KURANG frequent! (Missing/hilang during packing, tidak tahu root cause!)
- Label info: TIDAK di system! Manual lihat → Human error frequent!
- WIP Realtime: Ada di system terpisah (tidak terintegrasi dengan production Excel!)
- Reconciliation: 2-4 jam/hari untuk match data dept + QC!
- Production delay: Jarang dari bottleneck, lebih sering karena defect banyak ditemukan!
- Intermediate stock (Stuffed Body): TIDAK tracked! (inventory chaos!)
```

---

#### Planned Odoo Production Workflow (2026)

```
┌─────────────────────────────────────────────────────────────────┐
│  ODOO: Auto-create MO after material available                  │
│  - System detect: Material ready for Order IKEA-12345           │
│  - Auto-create MO (Manufacturing Order) untuk artikel ini       │
│  - MO berisi BOM explosion automatic untuk semua dept           │
│  - Auto-calculate target per dept (based on historical defect): │
│    Order 1000 → Packing: 1000 | Finishing: 1020 | Sewing: 1040  │
│    → Embroidery: 1060 | Cutting: 1080                           │
│  - Auto-create 5 WO (Work Order/SPK per dept) dalam MO ini:     │
│    WO-Cutting, WO-Embroidery, WO-Sewing, WO-Finishing, WO-Pack  │
│  - WO dependency: Sequential (dept sebelum selesai → next lock) │
│  - Notification ke SPV Production: "MO-12345 ready to start"    │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING: Start WO di tablet/mobile                        │
│  - Admin dept: Open Odoo app → Select WO-Cutting-12345          │
│  - Click "Start" → System record timestamp automatic            │
│  - Material consumption: AUTO-BACKFLUSH dari BOM                │
│    (Fabric deducted automatic, no manual input!)                │
│  - Production progress: Input quantity per batch (real-time!)   │
│    Example: "100 pcs done" → Dashboard update INSTANT!          │
│  - QC CUTTING: Input QC result per batch                        │
│    ✓ Pass: 95 pcs → Move to Embroidery                         │
│    ⚠️ Rework: 4 pcs → System create Rework task automatic      │
│    ❌ Reject: 1 pcs → Record defect type, update scrap          │
│    ✅ All QC data TRACEABLE! (timestamp, inspector, reason)    │
│  - Click "Transfer to Embroidery" → Select quantity (pass QC)   │
│    System: Deduct Cutting WIP, Add Embroidery WIP (automatic!)  │
│  - Notification auto ke Embroidery: "Material 95 pcs ready"     │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT EMBROIDERY: Continue production (seamless!)               │
│  - Notification received: "100 pcs from Cutting available"      │
│  - Admin dept: Click "Receive from Cutting" → Validate          │
│    System: Auto-increment Embroidery WIP balance                │
│  - Production: Input output per batch                           │
│  - Click "Transfer to Sewing" → System move WIP automatic       │
│  - Real-time dashboard: SPV lihat progress TANPA tanya admin!   │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT SEWING: Production 38 lines (managed efisien!)            │
│  - Receive from Embroidery: Automatic WIP tracking              │
│  - 38 Sewing Lines: Each line input production ke Odoo          │
│    Option 1: Tablet per line (operator input sendiri)           │
│    Option 2: Admin input aggregate per shift (easier!)          │
│  - Dashboard: Real-time tracking PER LINE!                      │
│    ✅ Line 1: 30 pcs | Line 2: 28 pcs | ... | Line 38: 25 pcs  │
│    ✅ System aggregate automatic: Total 1040 pcs                │
│    ✅ Alert: "Line 15 slower 30% vs others → Check now!"        │
│  - QC SEWING: Input QC result per batch (aggregate 38 lines)    │
│    ✓ Pass: 1010 pcs → Move to Finishing                        │
│    ⚠️ Rework: 25 pcs → Track by line! (Line 15, 7, 22...)      │
│       System: Create Rework task per line automatic           │
│    ❌ Reject: 5 pcs → Record defect type per line              │
│    ✅ Dashboard: Defect rate PER LINE visible! (action ready!)  │
│  - Production: Input output per batch/shift                     │
│    System: Track per line OR aggregate (flexible!)              │
│  - Transfer to Finishing: System track automatic (pass QC only) │
│  - Dashboard: Real-time bottleneck detection per line!          │
│    ⚠️ Benefit: Tahu line mana yang slow INSTANT!                │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT FINISHING: 2-Stage tracking automatic                     │
│  - Receive from Sewing: WIP balance update automatic            │
│  - Stage 1 (Stuffing): Input material → System track            │
│    Output "Stuffed Body" → ✅ TRACKED as intermediate product!  │
│    Location: "WIP-Finishing-Stuffed" (visible di system!)       │
│  - Stage 2 (Closing): Stuffed Body + Tag → Finished Doll        │
│    Input: System deduct "Stuffed Body" stock automatic          │
│    Output: Finished Doll count → System record                  │
│  - Label Info: ✅ AUTO-DISPLAY dari PO Label (no manual lihat!) │
│    System show: "Week 08 | Destination: IKEA Sweden"            │
│    ✅ No human error! Data langsung dari PO Label auto-inherit  │
│  - QC FINISHING: Input QC result per batch                      │
│    ✓ Pass: 1000 pcs → Move to Packing                          │
│    ⚠️ Rework: 8 pcs → Send back to Stage 2 (re-closing)       │
│       System: Create Rework task automatic with reason        │
│    ❌ Reject: 2 pcs → Record defect type, update scrap          │
│    ✅ Pattern analysis: "Defect Stage 2 meningkat 10%"         │
│  - Transfer to Packing: System track automatic (pass QC only)   │
│    System: Auto-transfer Label info ke Packing (inherit!)       │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT PACKING: Final packing (no QC, sudah pass QC Finishing!)  │
│  - Receive from Finishing: WIP balance update (pass QC only)    │
│    ✅ System track: Expected qty from Finishing (exact count!)  │
│    Example: Finishing transfer 1000 pcs → Packing receive 1000 │
│  - Label Info: ✅ AUTO-INHERIT dari Finishing (no manual copy!)  │
│    System display: "Week 08 | Destination: IKEA Sweden"         │
│    ✅ ZERO MIX LABEL RISK! Data auto-inherit dari PO Label      │
│  - Packing: System auto-print Label dengan info VALIDATED       │
│    ✓ Week number: Auto dari PO Label (cannot salah lihat!)     │
│    ✓ Destination: Auto dari PO Label (cannot mix!)             │
│    ✓ SKU, Quantity, Batch: Auto dari MO                        │
│    ✅ System LOCK Label info → Cannot change manual!            │
│  - Operator scan/input: Validate packing completion             │
│    System: Cross-check Label vs MO → Auto-validation!           │
│    ⚠️ Alert: "Week mismatch!" (if somehow error, blocked!)      │
│    ✅ QTY VALIDATION: Expected 1000 pcs vs Packed 980 pcs?      │
│       ALERT: "Missing 20 pcs! Cannot transfer to FG!"          │
│       System BLOCK transfer jika qty tidak match!               │
│  - Validate complete → Transfer to WH FG automatic              │
│    ✅ No missing qty problem! System force reconciliation!      │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  QC FINISHED GOODS: Inspection per pallet sebelum dispatch      │
│  - Unit: PER PALLET tracking (bukan per pcs!)                   │
│  - QC Inspector: Check pallet sebelum loading ke container      │
│  - WH FG: Open Odoo → Select pallet untuk QC inspection         │
│  - QC Checklist: Scan/input QC result per pallet                │
│    ✓ Pass: 15 pallet → Status "Ready for Dispatch"             │
│    ⚠️ Rework: 2 pallet → Send back to Packing (re-pack)        │
│       System: Record reason (Label salah, Packing rusak, etc)  │
│       Auto-create Rework task per pallet, traceable!           │
│    ❌ Reject: 1 pallet → Record defect type, update scrap       │
│  - Check: Packaging, Label, Week, Destination VALIDATED!        │
│    ✅ System auto-validation: Compare Label vs PO Label         │
│    ✅ DOUBLE-CHECK: Scan Label barcode per pallet → Verify!     │
│       If mismatch → BLOCK dispatch! "Week 07 Label for Week 08 │
│       batch detected! Cannot dispatch!"                         │
│    ✅ Alert: "Week number mismatch!" (if not match = BLOCKED!)  │
│    ✅ ZERO MIX LABEL dispatch! (System prevent 100%!)           │
│  - All QC data: TRACEABLE per pallet! (timestamp, inspector)    │
│  - Dashboard: Defect pattern analysis by pallet, SKU, Week      │
│  - MO status: "DONE" → Close automatic after all pallet pass QC │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  REAL-TIME DASHBOARD: Management visibility!                    │
│  - WIP per dept: Live update (tidak delay!)                     │
│  - QC metrics: Pass rate per dept (Cutting, Sewing, Finishing)  │
│    Example: "Cutting: 97.2% pass, Sewing: 97.1%, Finishing: 99%"│
│  - Defect tracking: "Sewing Line 15 defect rate 5.2% (high!)"   │
│  - Production vs QC: Auto-reconcile (no mismatch lagi!)          │
│  - Transfer validation: System track qty exact (no missing pcs!) │
│  - Bottleneck alert: "Embroidery below target 15%"              │
│  - Completion forecast: "MO-12345 finish in 2 days"             │
│  - Rework status: "Currently 120 pcs in rework (3 dept)"        │
│  - Reconciliation: ✅ AUTOMATIC! (no meeting 2-4 jam!)          │
│  - Traceability: Click any SKU → See full history (IKEA ready!) │
│    QC data: Integrated with MO (tidak terpisah lagi!)           │
└─────────────────────────────────────────────────────────────────┘

✅ BENEFITS PRODUCTION:
- Form kertas: ZERO! (all digital input tablet/mobile)
- Admin time: -60% (2-3 jam → 1 jam data entry)
- Admin QC: No more overwhelmed! (System auto-consolidate 4 checkpoints!)
- QC data: INTEGRATED with MO/production! (tidak Excel terpisah!)
- **ZERO MIX LABEL RISK!** Label auto-inherit dari PO Label, LOCKED di system!
- **Double-check validation!** FG QC scan Label → System verify vs MO, BLOCK if mismatch!
- No salah lihat datestamp/destination lagi! (System auto-display, cannot error!)
- Sewing 38 lines: Tracking per line automatic! (vs manual nightmare!)
- QC checkpoints: 4 locations (Cutting, Sewing, Finishing, FG) digital & traceable!
- QC data: FULLY TRACEABLE! (timestamp, inspector, reason, batch)
- Defect pattern analysis: By dept, by line, by SKU (IKEA compliance ready!)
- Production vs QC: Auto-match! (no mismatch or reconciliation chaos!)
- Rework: TRACKED & TRACEABLE! All rework automatic recorded!
- Real-time WIP: Factory Manager dashboard live update!
- Reconciliation: AUTOMATIC! (no meeting 2-4 jam lagi!)
- **QTY VALIDATION AUTOMATIC!** System block transfer jika qty tidak match (no missing pieces!)
- Bottleneck detection: REAL-TIME alert per line!
- Intermediate stock: TRACKED! (Stuffed Body visible!)
- Material consumption: AUTOMATIC backflush! (no manual deduct!)
- Transfer tracking: AUTOMATIC! (dept-to-dept smooth!)
```

---

#### Production Dashboard - Real-Time Visibility

**Current (Manual Excel)**:
```
Factory Manager: "Dept Embroidery sekarang WIP berapa?"
  ↓
WhatsApp/Call Admin Embroidery: "Tunggu pak, saya cek Excel..."
  ↓
Admin: Open Excel dept, scroll cari data (10 menit)
  ↓
Reply: "Sekitar 500-600 pcs pak (estimasi, belum pasti!)"
  ↓
Factory Manager: "QC Sewing pass rate berapa hari ini?"
  ↓
WhatsApp/Call Admin QC: "Tunggu pak, saya cek Excel QC..."
  ↓
Admin QC: Open Excel QC, calculate manual (5 menit)
  ↓
Reply: "Sekitar 97% pak (estimasi, belum final count!)"
  ↓
❌ Admin QC overwhelmed: 4 checkpoints manual entry!
❌ Data production & QC terpisah (tidak terintegrasi!)
  ↓
Factory Manager: Update Excel konsolidasi manual (data delay 2-4 jam!)
  ↓
❌ Tidak tahu bottleneck sampai terlambat!
❌ "SKU Bear kapan selesai?" → "Tidak tahu pak, estimasi aja..."
```

**Planned (Odoo Dashboard)**:
```
Factory Manager: Open Odoo Dashboard di laptop/tablet
  ↓
Real-Time View:
┌─────────────────────────────────────────────────────────────┐
│  MO-12345: IKEA Order Bear (Target: 1000 pcs)              │
│  Order Reference: IKEA-PO-5678 | Deadline: Feb 20, 2026    │
│                                                             │
│  Cutting:     ████████████████ 100% (1080/1080) ✅ DONE    │
│  Embroidery:  ██████████████░░  85% (901/1060)  🔄 ACTIVE  │
│  Sewing:      ████████░░░░░░░░  55% (572/1040)  🔄 ACTIVE  │
│    └─ [Click untuk drill-down 38 lines detail]             │
│  Finishing:   ████░░░░░░░░░░░░  30% (306/1020)  🔄 ACTIVE  │
│  Packing:     ░░░░░░░░░░░░░░░░   0% (0/1000)    ⏸️  WAITING│
│                                                             │
│  ⚠️ ALERT: Embroidery slower 15% vs target → Action needed!│
│  📊 Forecast: Complete in 1.5 days (was 1 day target)      │
│  🔍 Bottleneck: Sewing (2 machines down for maintenance)   │
│  📦 Label Info: Week 08 | Destination: IKEA Sweden         │
└─────────────────────────────────────────────────────────────┘

Click "Sewing" → Drill-Down View (38 Lines Detail):
┌─────────────────────────────────────────────────────────────┐
│  SEWING DEPT - 38 Lines Performance (Live)                 │
│                                                             │
│  Line 1:  ████████░░ 15 pcs ✅ | Line 20: ████████░░ 14 pcs│
│  Line 2:  ██████░░░░ 12 pcs ⚠️ | Line 21: ████████░░ 16 pcs│
│  Line 3:  ████████░░ 14 pcs ✅ | Line 22: ████████░░ 15 pcs│
│  ...                            | ...                       │
│  Line 15: ████░░░░░░  8 pcs ❌ | Line 38: ████████░░ 14 pcs│
│                                                             │
│  ⚠️ Line 15: Output 50% below average → CHECK NOW!         │
│  ℹ️ Top 5 performers: Line 21, 20, 1, 3, 38               │
│  ℹ️ Bottom 5: Line 15, 2, ... (need support)              │
└─────────────────────────────────────────────────────────────┘

Click "QC Metrics" → QC Dashboard View:
┌─────────────────────────────────────────────────────────────┐
│  QC PERFORMANCE - All Checkpoints (Live)                   │
│                                                             │
│  Today Summary (MO-12345):                                 │
│    Cutting QC:    1050 inspected | 97.2% pass | 30 defect │
│    Sewing QC:     1010 inspected | 97.0% pass | 30 defect │
│    Finishing QC:  1000 inspected | 99.0% pass | 10 defect │
│    FG QC:       15 pallet insp. | 88.2% pass | 2 pallet NG│
│                                                             │
│  ✅ Production-QC Match: 100% reconciled (auto!)           │
│  ⚠️ Alert: FG defect 2 pallet (Label mix!) → Re-pack!      │
│  📊 Trend: Sewing Line 15 defect 5.2% vs avg 3% (action!)  │
│  📋 Rework: 120 pcs (Cutting:30, Sewing:30) + 2 pallet FG  │
│                                                             │
│  ✅ Admin QC: No more overwhelmed! All data auto-update!   │
└─────────────────────────────────────────────────────────────┘

✅ Factory Manager: Langsung action! (allocate resource ke Sewing)
✅ Admin QC: No more manual Excel entry 4 checkpoints!
✅ Tahu LINE MANA yang bermasalah! (vs manual chaos!)
✅ QC data INTEGRATED dengan MO! (tidak terpisah lagi!)
✅ Real-time decision making! (tidak delay 1-2 hari!)
✅ Traceability: Click SKU → See full history dari PO sampai FG!
```

---

## 7 UNIQUE REQUIREMENTS

### 1. Dual Purchase Order Trigger System
- Purchasing create PO Fabric (week 0) → Validate → Unlock Cutting & Embroidery ONLY
- Purchasing create PO Label (week +2) → Validate → Unlock ALL dept + Auto-inherit Week/Destination
- Standard ERP: 1 MO = 1 trigger. Kami butuh: 1 MO = 2 PO triggers dengan state management (PARTIAL → FULL RELEASED)

### 2. Flexible Production Target per Department
- Setiap dept produksi LEBIH dari customer order (cover defect)
- Auto-calculate target based on historical defect rate per dept
- Reverse calculation: Packing need 1000 → Finishing 1020 → Sewing 1040

### 3. 2-Stage Finishing Internal Conversion
- Stage 1: Stuffing (Skin + Filling → Stuffed Body)
- Stage 2: Closing (Stuffed Body + Tag → Finished Doll)
- Track stock intermediate product TANPA transfer document

### 4. Multi-Unit Conversion & Pallet Calculation (IKEA Rules)
- Fabric: Beli ROLL, pakai PCS (1 ROLL = 50 meter, tapi vendor berbeda!)
- Filling: Beli KG, pakai GRAM (conversion automatic)
- Pallet: Calculate dari PCS → Karton → Pallet (IKEA rules: karton per pallet HARUS GENAP!)
  Example: Order 1523 pcs → System calculate: Berapa pallet? Sisa karton genap?
- Auto-convert + validate untuk prevent error
- PO dibuat berdasarkan pallet calculation (bukan flat quantity)

### 5. Real-Time WIP Tracking System
- Dashboard real-time per dept, per MO, per SKU
- Partial transfer support (tidak tunggu full batch)
- Bottleneck alert automatic

### 6. Quality Control Loop (Rework/Repair)
- QC recording: Pass / Rework / Reject
- Rework workflow dengan traceability
- Defect tracking untuk IKEA compliance

### 7. Department-Level Warehouse & Stock Opname
- Stock opname per dept (tidak stop ALL production)
- Rolling schedule: Today Cutting, Tomorrow Embroidery
- Production continue di dept lain

---

## CORE MODULES NEEDED

- Manufacturing Management (BOM, MO, Work Orders)
- Inventory & Warehouse (Multi-location, Real-time tracking)
- Purchasing Management (PO, Suplier tracking)
- Quality Control (QC checkpoints, Defect recording)
- Production Planning (MRP, Capacity planning)
- Reporting & Analytics (Real-time dashboards)

---

## SUCCESS CRITERIA

**Operational Metrics**:
- Material shortage: -80% frequency
- Production planning time: -60%
- Inventory accuracy: +25%
- Stock opname time: -75%
- Admin overtime: -50%

**Strategic Success**:
- IKEA compliance ready (real-time traceability)
- User adoption 80%+ after 3 months
- System handle 2x volume tanpa major issue
- Payback < 18 bulan

---

## IMPLEMENTATION APPROACH

### Phase 1 (CRITICAL):
- Real-Time WIP Tracking
- Material Shortage Prevention
- Dual Trigger System

### Phase 2 (HIGH):
- Flexible Target System
- Auto Material Tracking
- QC Traceability

### Phase 3 (OPTIMIZATION):
- Rework Recording
- Dept-Level Stock Opname
- UOM Conversion + Workflow

---

## REKOMENDASI: ODOO ERP

### Kenapa Odoo?
- Manufacturing ERP proven untuk kompleksitas serupa
- Open source dengan community support kuat
- Modular: Bisa implement phase-wise (tidak big bang)
- Customizable untuk 7 unique requirements kami
- Cost competitive vs SAP/Oracle

### Next Steps Jika Approved:
1. Contact Sales Odoo Indonesia untuk discovery workshop
2. Feasibility assessment 7 unique requirements
3. Gap analysis & proposal detail
4. Budget approval
5. Q2 2026: Implementation start

---

## APPROVAL YANG DIBUTUHKAN

### Yang Diminta dari Management:
1. **Approve proceed** dengan Odoo discovery workshop
2. **Commit budget** untuk ERP implementation (detail setelah proposal Odoo)
3. **Assign project team**: IT Lead + 3-4 Dept SPVs
4. **Timeline commitment**: Q2 2026 implementation start

### Risiko Jika Tidak Implement:
- IKEA compliance issue (risk kehilangan 80% revenue)
- Cannot scale untuk order increase
- Operational inefficiency terus berlanjut
- Team burnout → Turnover risk

---

## KRITERIA KEBERHASILAN (SUCCESS CRITERIA)

**Operational Metrics** (Measurement after 12 months):
- Material shortage: -80% frequency
- Production planning time: -60%
- Inventory accuracy: +25% (70% → 95%)
- Stock opname time: -75% (8 jam → 2 jam)
- Admin overtime: -50%

**Strategic Success**:
- IKEA compliance ready (real-time traceability)
- User adoption 80%+ after 3 months (NO Excel workaround!)
- System handle 2x volume tanpa major issue
- Payback < 18 bulan

**Critical Success Factors** (Non-negotiable):
- Suplier commit untuk 7 unique requirements customization
- BOM bulk import working BEFORE production start
- Material status accuracy 95%+ (vs always RED sebelumnya)
- Export/reporting functionality complete
- Phased implementation approach (NOT big bang)

---

## TIMELINE & NEXT STEPS

**Proposed Timeline**:
- **Feb 2026**: Management approval ← WE ARE HERE
- **Mar 2026**: Discovery workshop dengan Odoo Sales
- **Apr 2026**: Proposal & budget final approval
- **May-Jul 2026**: Phase 1 Implementation (Critical requirements)
- **Aug-Oct 2026**: Phase 2 Implementation (High value)
- **Nov-Dec 2026**: Phase 3 Implementation (Optimization)
- **Q1 2027**: Go-live & stabilization

**Immediate Action Required**:
1. Management approve proceed dengan discovery
2. Schedule discovery workshop (on-site recommended)
3. Assign project team members
4. Prepare detailed budget request (after Odoo proposal)

---

## CATATAN PENTING UNTUK MANAGEMENT

**Yang Harus Dipastikan ke Suplier Odoo**:
- Commit untuk customize (7 unique requirements)
- Commit untuk BOM bulk import solution
- Commit untuk proper training & change management
- Commit untuk hypercare 2-3 bulan post go-live
- **NO FORCE-FIT STANDARD PROCESS** seperti 2023!

**Investment Mindset**:
- Ini bukan "beli software", ini "business transformation"
- ROI datang dari process improvement, bukan system itu sendiri
- User adoption = critical success factor (training & change management penting!)
- Phased approach = minimize risk vs big bang

**Decision Point**:
Jika Sales Odoo tidak bisa commit untuk requirements kami, **kami cari Suplier lain**. Lesson learned 2023: Better no ERP than wrong ERP!

---

## CONTACT & DOKUMEN PENDUKUNG

**Prepared by**: Daniel Rizaldy (IT Lead)  

**Dokumen Lengkap untuk Odoo Sales** (setelah approval):
- REQUIREMENTS_KOMPREHENSIF_PT_QUTY_KARUNIA.md (35,000+ words)
- EXECUTIVE_SUMMARY_SALES_ODOO.md (overview untuk Odoo)
- BUSINESS_REQUIREMENTS_ONLY.md (business requirements)
- PAIN_POINTS_BUSINESS_IMPACT.md (pain points analysis)

---

**STATUS**: WAITING MANAGEMENT APPROVAL  
**ACTION REQUIRED**: Approve proceed dengan Odoo discovery workshop
