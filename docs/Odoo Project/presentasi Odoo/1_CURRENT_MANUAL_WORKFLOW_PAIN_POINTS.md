## 11 PAIN POINTS KRITIS

| # | Pain Point | Impact |
|---|------------|--------|
| 1 | Material shortage tiba-tiba | Production stop, overtime, emergency purchasing |
| 2 | Tidak tahu WIP real-time | Planning impossible, bottleneck detection delayed |
| 3 | Quality defect traceable manual (Excel terpisah) | Tidak terintegrasi, IKEA audit risk, sulit root cause analysis |
| 4 | **Mix Label risk (Finishing-Packing)** | **IKEA REJECT! Salah lihat datestamp/destination, no validation** |
| 5 | Dual trigger system manual | Beban kerja admin berlebihan, packaging error frequent |
| 6 | Excel-based planning | Error prone, single point of failure |
| 7 | Target produksi flat | Shortage frequent (tidak hitung defect rate) |
| 8 | Manual material tracking | Waktu admin terbuang untuk tugas manual |
| 9 | Stock opname 1-2 hari | Hasil SO kemungkinan tidak Valid / Tidak sesuai |
| 10 | Rework tidak ter-record | Cost tidak tahu, IKEA audit concern |
| 11 | Multi-unit conversion manual + Pallet calculation | UOM error (ROLL/KG/PCS), Pallet IKEA rules complex (karton harus genap per pallet) |

**CRITICAL**: Pain point #4 (Mix Label) adalah masalah untuk compliance! Operator sering salah lihat Week/Destination di Finishing & Packing, menyebabkan mix label saat dispatch. Tidak ada pengecekan kembali setelah packing selesai → IKEA reject baru ketahuan!

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
│  Problem: Harus calculate dari basis pallet!                    │
│  IKEA rules: Jumlah karton per pallet HARUS GENAP!              │
│  Example: 1 pallet = 24 karton → Order 1000 pcs tetap           │
│  harus calculate: Berapa pallet? Sisa karton genap tidak?       │
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Calculate & check stock material                   │
│  - Multi-unit conversion MANUAL (ROLL → PCS, KG → GRAM)         │
│  Problem: UOM error frequent! (Purchasing bukan technical!)     │
│  Example: Fabric 1 ROLL = 50 meter, tapi suplier A = 45m!       │
│  - Pallet calculation MANUAL (IKEA pallet rules!)               │
│  Problem: Karton per pallet harus GENAP sesuai IKEA rule!       │
│  Example: Calculate 1523 pcs → Berapa pallet + sisa karton?     │
│  Manual Excel formula: ROUNDUP(1523/pcs_per_karton/24)          │
│  - Check stock di Excel warehouse (data tidak real-time!)         │
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
│  Problem: Excel data outdated (data tidak update real-time dari warehouse)    │
│  Problem: "Material cukup tidak untuk order ini?" → Manual check│
└──────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION: Start production & material consumption            │
│  - Dept Admin catat manual di form kertas (per departemen)      │
│  - End-of-day: Input consumption ke Excel                       │
│  - Reconcile: Warehouse vs Production usage (proses manual lama!)    │
│  - Sering tidak match → Meeting produksi                        │
└─────────────────────────────────────────────────────────────────┘

PAIN POINTS:
- Purchasing overwhelmed: Terima order → Calculate manual → Track PO → Inform production
- Excel BOM: 478 SKU dengan 15-30 material each (nightmare!)
- Multi-unit conversion: UOM error frequent (ROLL/KG/PCS confusion, Purchasing bukan technical)
- Pallet calculation: IKEA pallet rules complex (karton per pallet harus GENAP, manual Excel formula)
- Stock visibility: "Material cukup tidak?" → Delay jawaban signifikan
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
│  System auto-calculate pallet: Karton per pallet GENAP!         │
│  Example: 1523 pcs → System calculate: 4 pallet (24 karton)     │
│  No manual Excel formula lagi!                                  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  ODOO: Check stock real-time & generate requirement list        │
│  - System check: Warehouse + In-Transit + Reserved stock        │
│  - Calculate: Material kurang berapa untuk order ini            │
│  - Auto-create Purchase Requisition list                        │
│  - Dashboard Purchasing: "15 material perlu order sekarang"      │
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
│  MATERIAL DATANG: Warehouse receive di Odoo (scan/manual)  │
│  - Select PO yang diterima (list dari sistem)  │
│  - Confirm quantity (validation: tidak boleh over-receive)  │
│  - Click "Validate" → Stock AUTO-UPDATE REAL-TIME!  │
│  - Notification auto ke Purchasing: "PO-12345 received"  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Dashboard tampil "Material Available"  │
│  - Material status: GREEN (semua available untuk order ini)  │
│  - Koordinasi ke Production: "Order X material ready, start!"  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION: Start production, material AUTO-CONSUMED  │
│  - Material consumption AUTO-BACKFLUSH dari BOM  │
│  - System deduct stock automatic (no manual input!)  │
│  - Real-time balance update (Purchasing lihat dashboard)  │
│  - Reconciliation: AUTOMATIC! (tidak perlu meeting panjang!)  │
└─────────────────────────────────────────────────────────────────┘

BENEFITS FOR PURCHASING (PRIMARY USER):
- Terima order IKEA → Input Odoo → System calculate semua!
- Tidak perlu Excel BOM 478 SKU lagi!
- Tidak perlu kalkulator manual!
- Multi-unit conversion automatic (no error ROLL/KG!)
- Pallet calculation automatic (IKEA pallet rules built-in, karton GENAP per pallet!)
- Stock visibility real-time (real-time!)
- PO tracking automatic (tidak Email suplier terus!)
- Dashboard clear: "Material mana yang ready/pending untuk order mana"

BENEFITS FOR PRODUCTION:
- Material status accurate (tidak RED palsu!)
- Tahu order mana yang bisa start (tidak tanya Purchasing terus!)
- Consumption automatic (tidak manual catat kertas!)
- Reconciliation automatic (tidak perlu meeting panjang!)
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
MASALAH: Warehouse tidak tahu cara "Receive PO" di Odoo
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
Step 1: Scan barcode PO (atau select manual)
Step 2: Confirm quantity received
Step 3: Click "Validate" → Stock AUTO-UPDATE
  ↓
System: Material stock = AVAILABLE (GREEN)
  ↓
MO: Auto-change status "Ready to Produce"
  ↓
Notification ke SPV: "Batch X bisa start production"
  ↓
Production: Start dengan data ACCURATE
  ↓
RESULT: Smooth flow, no blocking palsu!
```

**Key Improvements 2026**:
- **Training proper** untuk Warehouse team (2023 tidak ada training!)
- **Mobile app** untuk receive (easier vs desktop only)
- **Validation mandatory** (cannot skip receive step)
- **Visual dashboard** untuk receiving status (tracking jelas)

---

### 4. Dual PO Trigger - Unique Requirement (IKEA Workflow)

**Problem**: 1 Manufacturing Order butuh 2 Purchase Order dengan timing berbeda
- **PO Fabric**: Purchasing order ke Suplier Fabric → Datang Week 0
- **PO Label**: Purchasing order ke Suplier Label → Datang Week +2 (IKEA kirim Label info terlambat waktuggu!)

Production HARUS start dari PO Fabric (Week 0), tapi TIDAK BOLEH sampai Packing tanpa PO Label (Week +2).

**Kenapa Harus Begini?**
- IKEA baru finalize Label info (Week number, Destination) waktuggu setelah order
- Fabric bisa di-order langsung, tapi Label HARUS tunggu info final dari IKEA
- Production tidak bisa tunggu waktuggu baru start (lead time terlalu lama!)
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
RISK: Admin lupa broadcast → Sewing start duluan → 
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
  MO status → "PARTIAL RELEASED"
  UNLOCK: Cutting WO + Embroidery WO (bisa start!)
  LOCK: Sewing WO + Finishing WO + Packing WO (blocked!)
  Field "Week" & "Destination" → Editable (belum final dari IKEA)
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
  MO status → "FULL RELEASED"
  AUTO-INHERIT Week & Destination dari PO Label ke MO
  UNLOCK: ALL remaining work orders (Sewing, Finishing, Packing)
  LOCK field "Week" & "Destination" → Read-only (cannot change lagi!)
  ↓
All departments: Continue production sampai Packing dengan destination correct
  ↓
RESULT: Zero packaging error! System auto-inherit Label info!
```

**Benefit**: 
- Admin tidak perlu track manual
- System automatis enforce business rule (tidak bisa skip!)
- Week & Destination auto-inherit dari PO Label (no manual copy-paste error!)

**Benefit**: Admin tidak perlu track manual atau WhatsApp. System automatis enforce business rule!

---

### 5. Production Flow - Department by Department

**NOTE**: Production di PT Quty Karunia melewati 5 departemen sequential. Tidak ada MO (Manufacturing Order) formal yang mengkoordinasi semua WO/SPK departemen. Tiap dept memiliki jadwal produksi sendiri (dari meeting dengan Factory Manager). Admin dept hanya catat consumption & daily production di Excel.

**Penjelasan**:
- **MO (Manufacturing Order)** = Order manufaktur untuk 1 artikel/SKU yang memuat keseluruhan WO dari semua departemen
- **WO/SPK** = Work Order/Surat Perintah Kerja per departemen (bagian dari MO)

#### Current Manual Production Process (SEKARANG)

```
┌─────────────────────────────────────────────────────────────────┐
│  FACTORY MANAGER: Monthly/Weekly Production Meeting  │
│  - Meeting dengan SPV semua departemen  │
│  - Diskusi: SKU apa yang harus produksi, target berapa  │
│  - Tentukan jadwal produksi per dept (tidak sinkron!)  │
│  Example: Cutting start minggu ini, Embroidery minggu depan  │
│  - TIDAK ada MO formal yang koordinasi semua dept WO!  │
│  - TIDAK ada WO/SPK tertulis per departemen!  │
│  - Hanya verbal agreement + note di Excel masing-masing dept  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING: Ambil material dari Warehouse (Surat Jalan)  │
│  - Admin Cutting: Buat surat jalan manual (kertas)  │
│  "Ambil Fabric SKU-001, 100 ROLL untuk produksi Bear"  │
│  - Warehouse: Catat pengeluaran material di Excel  │
│  - Admin Cutting: Catat consumption di Excel dept  │
│  Problem: Surat jalan & Excel sering tidak match!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING: Start production (tanpa MO reference!)  │
│  - Admin dept: Lihat jadwal dari Excel/note meeting  │
│  - Operator cutting: Material Fabric → Cut pieces  │
│  - QC CUTTING: Inspector check cut pieces quality (manual!)  │
│  Verbal report ke Admin QC: "Pass 1050, Defect 30"  │
│  - Admin QC (1 orang): Record ke Excel QC Master  │
│  Data input: Defect count: 30, Lolos: 1050, Total QC: 1080  │
│  Production output: 1050 pcs (per hari)  │
│  Problem: Admin QC harus manual consolidate 4 checkpoints! │
│  Problem: QC data di Excel terpisah dari production Excel! │
│  (IKEA audit compliance RISK!)  │
│  Rework: Re-cut pieces yang tidak sesuai spec (verbal only!)  │
│  Problem: Rework TIDAK tracked! Tidak tahu cost!  │
│  - Admin dept catat: Daily production output (Excel dept)  │
│  Example: "Hari ini: 1050 pcs cut pieces untuk SKU Bear"  │
│  - Traceability card: Dibuat manual per dept (Excel terpisah)  │
│  Problem: Manual & terpisah tiap dept! Sulit konsolidasi!  │
│  Problem: Audit IKEA butuh data terintegrasi, bukan Excel! │
│  - End-of-day: Admin dept + Admin QC input ke Excel masing2  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING → EMBROIDERY: Transfer material (manual track)  │
│  - Admin Cutting: Catat transfer "1050 pcs pass QC ke Embr"  │
│  - Admin Embroidery: Catat receiving "1050 pcs dari Cutting"  │
│  Problem: Sering tidak match! Cutting catat 1050, Embr 1020│
│  - Tidak ada surat jalan internal (hanya verbal!)  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT EMBROIDERY: Production dengan jadwal sendiri  │
│  - Admin dept: Lihat jadwal dari Excel/note meeting  │
│  - Production: Cut pieces → Embroidered pieces  │
│  - Admin dept catat: Daily production output (Excel)  │
│  Example: "Hari ini: 1060 pcs embroidered untuk SKU Bear"  │
│  - End-of-day: Admin input consumption & output ke Excel dept  │
│  Input: Thread consumption, Output: 1060 pcs embroidered  │
│  Problem: Tidak tahu sisa WIP Cutting berapa!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT EMBROIDERY → SEWING: Transfer material (manual track)  │
│  - Admin Embroidery: Catat transfer "1060 pcs ke Sewing"  │
│  - Admin Sewing: Catat receiving "1060 pcs dari Embroidery"  │
│  Problem: Sering delay entry! Embr input hari ini, Sewing  │
│  input besok → Data tidak sync!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT SEWING: Production dengan jadwal sendiri (38 LINES!)  │
│  - Operasional: 38 sewing lines parallel production  │
│  - Admin dept: Lihat jadwal dari Excel/note meeting  │
│  - Production: Embroidered pieces → Sewn bodies  │
│  Problem: 38 lines = 38 tracking points! (chaos!)  │
│  Admin dept: Track output PER LINE (manual Excel nightmare!)  │
│  - QC SEWING: Inspector check sewn bodies quality (manual!)  │
│  Verbal report ke Admin QC: "Pass 1010, Defect 30"  │
│  - Admin QC (1 orang): Record ke Excel QC Master  │
│  Data input: Defect count: 30, Lolos: 1010, Total QC: 1040  │
│  Production output: 1010 pcs (per hari)  │
│  Problem: Admin QC TIDAK tahu defect dari line mana!  │
│  Problem: Cannot analyze line performance untuk NG rate!  │
│  Rework: Kembalikan ke line untuk re-sewing (verbal only!)  │
│  Problem: Rework TIDAK tracked! Line mana yang banyak NG?  │
│  - Admin dept catat: Daily production output per line (Excel)  │
│  Example: "Line 1: 28 pcs, Line 2: 26 pcs, ... Line 38: 24"  │
│  Total: "Hari ini: 1010 pcs sewn untuk SKU Bear"  │
│  - Traceability card: Dibuat manual per batch (Excel terpisah) │
│  Problem: Manual, terpisah per line, sulit konsolidasi!  │
│  - End-of-day: Admin dept + Admin QC input ke Excel masing2  │
│  Input: Thread consumption aggregate, Output: 1010 pcs sewn  │
│  Problem: TIDAK tahu order IKEA mana ini! (no reference!)  │
│  Problem: Track 38 lines manual = waktu yang lama/hari admin time! │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT SEWING → FINISHING: Transfer material (manual track)  │
│  - Admin Sewing: Catat transfer "1010 pcs pass QC ke Finishing" │
│  - Admin Finishing: Catat receiving "1010 pcs dari Sewing"  │
│  Problem: Sering admin lupa catat! → Reconciliation chaos! │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT FINISHING: Production 2-stage (intermediate tidak tracked)│
│  - Admin dept: Lihat jadwal dari Excel/note meeting  │
│  - Stage 1 (Stuffing): Skin + Filling → Stuffed Body  │
│  Admin catat: Daily output "1010 pcs stuffed" (Excel)  │
│  Problem: Stock intermediate "Stuffed Body" TIDAK tracked! │
│  Tidak tahu berapa WIP Stage 1 vs Stage 2!  │
│  - Stage 2 (Closing): Stuffed Body + Tag → Finished Doll  │
│  Admin catat: Daily output "1010 pcs finished" (Excel)  │
│  - Operator: Lihat Label info manual dari Excel/Email IKEA  │
│  Cari: "SKU Bear untuk Week berapa ya? Destination mana?"  │
│  RISK: Salah lihat datestamp/destination! (human error!)  │
│  Example: "Week 08" tapi salah baca jadi "Week 07"  │
│  - QC FINISHING: Inspector check finished quality (manual!)  │
│  Verbal report ke Admin QC: "Pass 1000, Defect 10"  │
│  - Admin QC (1 orang): Record ke Excel QC Master  │
│  Data input: Defect count: 10, Lolos: 1000, Total QC: 1010  │
│  Production output: 1000 pcs (per hari)  │
│  Problem: Admin QC TIDAK tahu defect dari Stage 1 atau 2!  │
│  Rework: Kembalikan ke Stage 2 untuk re-closing (verbal!)  │
│  Problem: Rework TIDAK tracked! Tidak tahu defect pattern! │
│  - Traceability card: Dibuat manual per batch (Excel terpisah) │
│  Problem: Manual & terpisah, sulit untuk audit IKEA!  │
│  - End-of-day: Admin dept + Admin QC input ke Excel masing2  │
│  Input: Filling consumption, Output: 1000 pcs  │
│  Problem: Tidak catat Stuffed Body intermediate!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT FINISHING → PACKING: Transfer material (manual track)  │
│  - Admin Finishing: Catat transfer "1000 pcs pass QC ke Packing"│
│  Note: Week & Destination info (dari salah lihat tadi!)  │
│  - Admin Packing: Catat receiving "1000 pcs dari Finishing"  │
│  Problem: Tidak ada Label info di system! Manual cari!  │
│  RISK: Info dari Finishing sudah salah! (Mix Label!)  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT PACKING: Packing production (tanpa QC!)  │
│  - Admin dept: Lihat jadwal dari Excel/note meeting  │
│  - Operator: Lihat Label info dari Finishing (verbal/note)  │
│  Atau cari sendiri: "SKU Bear, Week berapa ya? Destination?"  │
│  RISK: Salah lihat datestamp/destination! (human error!)  │
│  Example: Finishing bilang "Week 08" tapi operator dengar  │
│  "Week 07" → Packing pakai Label Week 07! (MIX LABEL!)  │
│  - Packing: Group by Week & Destination (manual lihat Label!)  │
│  CRITICAL PROBLEM: MIX LABEL!  │
│  Week 08 products + Week 07 Label = IKEA REJECT!  │
│  Destination Sweden + Label Germany = IKEA REJECT!  │
│  - Admin dept catat: Daily packing output (Excel)  │
│  Example: "Hari ini: 1000 pcs packed untuk SKU Bear"  │
│  FREQUENT PROBLEM: QTY KURANG saat packing!  │
│  Dari Finishing: 1000 pcs → Packing result: 980 pcs only! │
│  Missing 20 pcs! Entah hilang atau tidak tercatat!  │
│  Tidak tahu hilang di mana: Transfer? Packing process?  │
│  - Transfer ke Warehouse FG: Manual catat (Excel)  │
│  Problem: TIDAK ADA PENGECEKAN KEMBALI setelah packing!  │
│  No validation apakah Label correct atau tidak!  │
│  Mix label baru ketahuan saat IKEA complain!  │
│  - End-of-day: Admin input ke Excel dept  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  QC FINISHED GOODS: Inspection per pallet sebelum loading  │
│  - Unit: PER PALLET (bukan per pcs!)  │
│  - QC Inspector: Check pallet sebelum loading ke container  │
│  - Check: Packaging, Label, Week number, Destination per pallet │
│  Verbal report ke Admin QC: "Pass 15 pallet, Defect 2 pallet" │
│  - Admin QC (1 orang): Record ke Excel QC Master  │
│  Data input: Defect pallet: 2, Lolos pallet: 15, Total: 17  │
│  Production output: 15 pallet (per hari, ready dispatch)  │
│  Problem: Admin QC handle 4 checkpoints sendirian!  │
│  (Cutting, Sewing, Finishing, FG) = overwhelmed!  │
│  Problem: QC data di Excel terpisah dari MO/production!  │
│  (IKEA audit compliance RISK! Cannot trace defect to MO!)  │
│  - Rework: Kembalikan ke Packing untuk re-pack pallet (verbal!) │
│  Problem: Rework TIDAK tracked! Tidak tahu root cause!  │
│  - Traceability card: Dibuat manual per pallet (Excel terpisah) │
│  Problem: 4 checkpoints = 4 Excel terpisah per batch!  │
│  Problem: Manual konsolidasi untuk IKEA audit = nightmare! │
│  - Pass QC: Pallet ready for loading ke container  │
│  - End-of-day: Admin QC input semua QC result ke Excel Master  │
│  Consolidate: 4 checkpoints × multiple batches = chaos!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  END-OF-DAY: Reconciliation nightmare!  │
│  - Factory Manager: Konsolidasi Excel dari 5 dept (manual!)  │
│  - Admin QC (1 orang): Konsolidasi Excel QC dari 4 checkpoints! │
│  (Cutting, Sewing, Finishing, FG) → Manual entry overwhelm!  │
│  - Cross-check: Dept A output = Dept B input? (sering NO MATCH!)│
│  Example: Cutting 1050, Embroidery receive 1020 → Selisih 30!│
│  Example: Finishing 1000, Packing result 980 → Missing 20 pcs!│
│  FREQUENT di Packing: QTY kurang! Hilang atau tidak catat? │
│  - Cross-check QC: Production output vs QC data match? (chaos!) │
│  Example: Cutting output 1050 vs QC data 1050  │
│  Tapi Sewing output 1040 vs QC data 1010 → Selisih 30!  │
│  - QC data: Consolidate dari 4 QC checkpoints (Cutting, Sewing, │
│  Finishing, FG) → TIDAK ada pattern analysis!  │
│  - Meeting panjang untuk reconcile: "Kemana 30 pcs hilang? Rusak? Lupa catat?"  │
│  - Track down: Cek Excel dept + Excel QC, interview operator  │
│  Problem: 2 Excel files (production + QC) tidak terintegrasi│
│  - Manual adjustment di Excel (lost audit trail!)  │
│  - Update WIP status manual untuk management report  │
│  - Estimate completion: TIDAK BISA! (tidak tahu bottleneck!)  │
│  "SKU Bear kapan selesai?" → "Tidak tahu pak, kira-kira..."  │
└─────────────────────────────────────────────────────────────────┘

PAIN POINTS PRODUCTION:
- TIDAK ada MO formal yang koordinasi semua WO departemen!
- TIDAK ada WO/SPK tertulis per departemen! (Hanya verbal dari meeting!)
- Tiap dept jadwal sendiri-sendiri, tidak sinkron!
- Surat jalan material: Manual & sering tidak match dengan Excel!
- Daily production input: HANYA consumption & output, no context!
- Traceability card: Manual per dept (Excel terpisah), sulit konsolidasi untuk audit IKEA!
- Admin tiap dept: waktu yang lama/hari HANYA untuk data entry Excel!
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
- Reconciliation: waktu yang lama/hari untuk match data dept + QC!
- Production delay: Jarang dari bottleneck, lebih sering karena defect banyak ditemukan!
- Intermediate stock (Stuffed Body): TIDAK tracked! (inventory chaos!)
```
