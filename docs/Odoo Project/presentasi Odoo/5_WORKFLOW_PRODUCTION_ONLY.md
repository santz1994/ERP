# WORKFLOW: PRODUCTION 5 DEPARTMENTS

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