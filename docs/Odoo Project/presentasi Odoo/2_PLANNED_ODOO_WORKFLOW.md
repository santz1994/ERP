
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


---

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