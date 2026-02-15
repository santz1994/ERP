# WORKFLOW: PURCHASING DEPARTMENT


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
