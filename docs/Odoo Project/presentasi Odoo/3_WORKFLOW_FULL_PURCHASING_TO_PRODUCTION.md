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
| 9 | Stock opname 1 hari penuh | Production stop untuk counting |
| 10 | Rework tidak ter-record | Cost tidak tahu, IKEA audit concern |
| 11 | Multi-unit conversion manual + Pallet calculation | UOM error (ROLL/KG/PCS), Pallet IKEA rules complex (karton harus genap per pallet) |

**CRITICAL**: Pain point #4 (Mix Label) adalah **high-risk** untuk IKEA compliance! Operator sering salah lihat Week/Destination di Finishing & Packing, menyebabkan mix label saat dispatch. Tidak ada pengecekan kembali setelah packing selesai → IKEA reject baru ketahuan!

---

## ILUSTRASI WORKFLOW

**NOTE**: Di PT Quty Karunia, **PURCHASING adalah trigger utama** material planning. PPIC tidak menjalankan fungsi planning seperti perusahaan manufacturing lain. Purchasing yang input kebutuhan material dan melakukan pembelian.

### 1. Current Manual Process (SEKARANG) - START FROM PURCHASING

```
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Terima order  │
│  - Lihat order: SKU apa, quantity berapa, production plan kapan │
│  - Buka Excel BOM untuk tiap SKU yang di-order  │
│  - Calculate material needed (pakai Excel!)  │
│  Problem: Harus calculate dari basis pallet!  │
│  IKEA rules: Jumlah karton per pallet HARUS GENAP!  │
│  Example: 1 pallet = 24 karton → Order 1000 pcs tetap  │
│  harus calculate: Berapa pallet? Sisa karton genap tidak?  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Calculate & check stock material  │
│  - Multi-unit conversion MANUAL (ROLL → PCS, KG → GRAM)  │
│  Problem: UOM error frequent! (Purchasing bukan technical!)│
│  Example: Fabric 1 ROLL = 50 meter, tapi suplier A = 45m! │
│  - Pallet calculation MANUAL (IKEA pallet rules!)  │
│  Problem: Karton per pallet harus GENAP sesuai IKEA rule!  │
│  Example: Calculate 1523 pcs → Berapa pallet + sisa karton?│
│  Manual Excel formula: ROUNDUP(1523/pcs_per_karton/24)  │
│  - Check stock di Excel warehouse (data tidak real-time!)  │
│  - Calculate: Material mana yang harus di-order  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Create PO manual di Excel  │
│  - Copy-paste data material (resiko typo tinggi!)  │
│  - Email manual ke suplier (attachment Excel/PDF)  │
│  - Track delivery: Email suplier "Sudah kirim belum?"  │
│  - Record manual di Excel tracking: "PO-001 status: Pending"  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  MATERIAL DATANG: Warehouse Admin terima (packing list)  │
│  - Catat manual: Material apa, quantity berapa, dari PO mana  │
│  - End-of-day baru input ke Excel (salah entry!)  │
│  - Purchasing update Excel tracking manual  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Cek Excel stock, inform production ready/not  │
│  Problem: Excel data outdated (data tidak update real-time dari warehouse)  │
│  Problem: "Material cukup tidak untuk order ini?" → Manual check│
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION: Start production & material consumption  │
│  - Dept Admin catat manual di form kertas (per departemen)  │
│  - End-of-day: Input consumption ke Excel  │
│  - Reconcile: Warehouse vs Production usage (proses manual lama!)  │
│  - Sering tidak match → Meeting produksi  │
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
│  PURCHASING: Terima order IKEA, input ke Odoo  │
│  - Buka Odoo Purchasing module  │
│  - Pilih SKU yang di-order IKEA  │
│  - Input quantity yang dibutuhkan  │
│  - Click "Calculate Material" → System AUTO-EXPLODE BOM  │
│  - Multi-unit conversion AUTOMATIC (ROLL → PCS, KG → GRAM)  │
│  - Pallet calculation AUTOMATIC (IKEA pallet rules built-in!)  │
│  System auto-calculate pallet: Karton per pallet GENAP!  │
│  Example: 1523 pcs → System calculate: 4 pallet (24 karton)│
│  No manual Excel formula lagi!  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  ODOO: Check stock real-time & generate requirement list  │
│  - System check: Warehouse + In-Transit + Reserved stock  │
│  - Calculate: Material kurang berapa untuk order ini  │
│  - Auto-create Purchase Requisition list  │
│  - Dashboard Purchasing: "15 material perlu order sekarang"  │
└──────────────────────────┬──────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  PURCHASING: Review requisition & Create PO (1-click)  │
│  - Quantity SUDAH CALCULATED (tidak perlu kalkulator!)  │
│  - Suplier auto-suggested (dari database preferred suplier)  │
│  - Click "Create PO" → PO auto-generate semua detail  │
│  - Email PO auto-send ke suplier  │
│  - Dashboard tracking: PO status real-time  │
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


---

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

---

#### Planned Odoo Production Workflow (2026)

```
┌─────────────────────────────────────────────────────────────────┐
│  ODOO: Auto-create MO after material available  │
│  - System detect: Material ready for Order IKEA-12345  │
│  - Auto-create MO (Manufacturing Order) untuk artikel ini  │
│  - MO berisi BOM explosion automatic untuk semua dept  │
│  - Auto-calculate target per dept (based on historical defect): │
│  Order 1000 → Packing: 1000 | Finishing: 1020 | Sewing: 1040  │
│  → Embroidery: 1060 | Cutting: 1080  │
│  - Auto-create 5 WO (Work Order/SPK per dept) dalam MO ini:  │
│  WO-Cutting, WO-Embroidery, WO-Sewing, WO-Finishing, WO-Pack  │
│  - WO dependency: Sequential (dept sebelum selesai → next lock) │
│  - Notification ke SPV Production: "MO-12345 ready to start"  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT CUTTING: Start WO di tablet/mobile  │
│  - Admin dept: Open Odoo app → Select WO-Cutting-12345  │
│  - Click "Start" → System record timestamp automatic  │
│  - Material consumption: AUTO-BACKFLUSH dari BOM  │
│  (Fabric deducted automatic, no manual input!)  │
│  - Production progress: Input quantity per batch (real-time!)  │
│  Example: "100 pcs done" → Dashboard update INSTANT!  │
│  - QC CUTTING: Input QC result per batch  │
│  Pass: 95 pcs → Move to Embroidery  │
│  Rework: 4 pcs → System create Rework task automatic  │
│  Reject: 1 pcs → Record defect type, update scrap  │
│  All QC data TRACEABLE! (timestamp, inspector, reason)  │
│  - Click "Transfer to Embroidery" → Select quantity (pass QC)  │
│  System: Deduct Cutting WIP, Add Embroidery WIP (automatic!)  │
│  - Notification auto ke Embroidery: "Material 95 pcs ready"  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT EMBROIDERY: Continue production (seamless!)  │
│  - Notification received: "100 pcs from Cutting available"  │
│  - Admin dept: Click "Receive from Cutting" → Validate  │
│  System: Auto-increment Embroidery WIP balance  │
│  - Production: Input output per batch  │
│  - Click "Transfer to Sewing" → System move WIP automatic  │
│  - Real-time dashboard: SPV lihat progress TANPA tanya admin!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT SEWING: Production 38 lines (managed efisien!)  │
│  - Receive from Embroidery: Automatic WIP tracking  │
│  - 38 Sewing Lines: Each line input production ke Odoo  │
│  Option 1: Tablet per line (operator input sendiri)  │
│  Option 2: Admin input aggregate per shift (easier!)  │
│  - Dashboard: Real-time tracking PER LINE!  │
│  Line 1: 30 pcs | Line 2: 28 pcs | ... | Line 38: 25 pcs  │
│  System aggregate automatic: Total 1040 pcs  │
│  Alert: "Line 15 slower 30% vs others → Check now!"  │
│  - QC SEWING: Input QC result per batch (aggregate 38 lines)  │
│  Pass: 1010 pcs → Move to Finishing  │
│  Rework: 25 pcs → Track by line! (Line 15, 7, 22...)  │
│  System: Create Rework task per line automatic  │
│  Reject: 5 pcs → Record defect type per line  │
│  Dashboard: Defect rate PER LINE visible! (action ready!)  │
│  - Production: Input output per batch/shift  │
│  System: Track per line OR aggregate (flexible!)  │
│  - Transfer to Finishing: System track automatic (pass QC only) │
│  - Dashboard: Real-time bottleneck detection per line!  │
│  Benefit: Tahu line mana yang slow INSTANT!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT FINISHING: 2-Stage tracking automatic  │
│  - Receive from Sewing: WIP balance update automatic  │
│  - Stage 1 (Stuffing): Input material → System track  │
│  Output "Stuffed Body" → TRACKED as intermediate product!  │
│  Location: "WIP-Finishing-Stuffed" (visible di system!)  │
│  - Stage 2 (Closing): Stuffed Body + Tag → Finished Doll  │
│  Input: System deduct "Stuffed Body" stock automatic  │
│  Output: Finished Doll count → System record  │
│  - Label Info: AUTO-DISPLAY dari PO Label (no manual lihat!) │
│  System show: "Week 08 | Destination: IKEA Sweden"  │
│  No human error! Data langsung dari PO Label auto-inherit  │
│  - QC FINISHING: Input QC result per batch  │
│  Pass: 1000 pcs → Move to Packing  │
│  Rework: 8 pcs → Send back to Stage 2 (re-closing)  │
│  System: Create Rework task automatic with reason  │
│  Reject: 2 pcs → Record defect type, update scrap  │
│  Pattern analysis: "Defect Stage 2 meningkat 10%"  │
│  - Transfer to Packing: System track automatic (pass QC only)  │
│  System: Auto-transfer Label info ke Packing (inherit!)  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  DEPT PACKING: Final packing (no QC, sudah pass QC Finishing!)  │
│  - Receive from Finishing: WIP balance update (pass QC only)  │
│  System track: Expected qty from Finishing (exact count!)  │
│  Example: Finishing transfer 1000 pcs → Packing receive 1000 │
│  - Label Info: AUTO-INHERIT dari Finishing (no manual copy!)  │
│  System display: "Week 08 | Destination: IKEA Sweden"  │
│  ZERO MIX LABEL RISK! Data auto-inherit dari PO Label  │
│  - Packing: System auto-print Label dengan info VALIDATED  │
│  Week number: Auto dari PO Label (cannot salah lihat!)  │
│  Destination: Auto dari PO Label (cannot mix!)  │
│  SKU, Quantity, Batch: Auto dari MO  │
│  System LOCK Label info → Cannot change manual!  │
│  - Operator scan/input: Validate packing completion  │
│  System: Cross-check Label vs MO → Auto-validation!  │
│  Alert: "Week mismatch!" (if somehow error, blocked!)  │
│  QTY VALIDATION: Expected 1000 pcs vs Packed 980 pcs?  │
│  ALERT: "Missing 20 pcs! Cannot transfer to FG!"  │
│  System BLOCK transfer jika qty tidak match!  │
│  - Validate complete → Transfer to WH FG automatic  │
│  No missing qty problem! System force reconciliation!  │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  QC FINISHED GOODS: Inspection per pallet sebelum dispatch  │
│  - Unit: PER PALLET tracking (bukan per pcs!)  │
│  - QC Inspector: Check pallet sebelum loading ke container  │
│  - WH FG: Open Odoo → Select pallet untuk QC inspection  │
│  - QC Checklist: Scan/input QC result per pallet  │
│  Pass: 15 pallet → Status "Ready for Dispatch"  │
│  Rework: 2 pallet → Send back to Packing (re-pack)  │
│  System: Record reason (Label salah, Packing rusak, etc)  │
│  Auto-create Rework task per pallet, traceable!  │
│  Reject: 1 pallet → Record defect type, update scrap  │
│  - Check: Packaging, Label, Week, Destination VALIDATED!  │
│  System auto-validation: Compare Label vs PO Label  │
│  DOUBLE-CHECK: Scan Label barcode per pallet → Verify!  │
│  If mismatch → BLOCK dispatch! "Week 07 Label for Week 08 │
│  batch detected! Cannot dispatch!"  │
│  Alert: "Week number mismatch!" (if not match = BLOCKED!)  │
│  ZERO MIX LABEL dispatch! (System prevent 100%!)  │
│  - All QC data: TRACEABLE per pallet! (timestamp, inspector)  │
│  - Dashboard: Defect pattern analysis by pallet, SKU, Week  │
│  - MO status: "DONE" → Close automatic after all pallet pass QC │
└──────────────────────────────────┬──────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  REAL-TIME DASHBOARD: Management visibility!  │
│  - WIP per dept: Live update (tidak delay!)  │
│  - QC metrics: Pass rate per dept (Cutting, Sewing, Finishing)  │
│  Example: "Cutting: 97.2% pass, Sewing: 97.1%, Finishing: 99%"│
│  - Defect tracking: "Sewing Line 15 defect rate 5.2% (high!)"  │
│  - Production vs QC: Auto-reconcile (no mismatch lagi!)  │
│  - Transfer validation: System track qty exact (no missing pcs!) │
│  - Bottleneck alert: "Embroidery below target 15%"  │
│  - Completion forecast: "MO-12345 finish in 2 days"  │
│  - Rework status: "Currently 120 pcs in rework (3 dept)"  │
│  - Reconciliation: AUTOMATIC! (no Meeting panjang untuk reconcile!)  │
│  - Traceability: Click any SKU → See full history (IKEA ready!) │
│  QC data: Integrated with MO (tidak terpisah lagi!)  │
└─────────────────────────────────────────────────────────────────┘

BENEFITS PRODUCTION:
- Form kertas: ZERO! (all digital input tablet/mobile)
- Efisiensi waktu admin: pengurangan signifikan
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
- Reconciliation: AUTOMATIC! (no Meeting panjang untuk reconcile lagi!)
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
Admin: Open Excel dept, scroll cari data (proses manual)
  ↓
Reply: "Sekitar 500-600 pcs pak (estimasi, belum pasti!)"
  ↓
Factory Manager: "QC Sewing pass rate berapa hari ini?"
  ↓