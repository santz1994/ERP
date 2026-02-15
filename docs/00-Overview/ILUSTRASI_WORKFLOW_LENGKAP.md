# 🔄 ILUSTRASI WORKFLOW LENGKAP ERP QUTY KARUNIA
## End-to-End Process Flow: Purchasing → Finished Goods

**Dokumen**: Workflow Illustration Complete  
**Untuk**: PT Quty Karunia  
**Tanggal**: 3 Februari 2026  
**Version**: 2.1

---

## 📖 DAFTAR ISI

1. [Overview Workflow](#overview)
2. [Phase 1: Purchasing & Procurement](#phase-1)
3. [Phase 2: Production Planning (PPIC)](#phase-2)
4. [Phase 3: Production Execution](#phase-3)
5. [Phase 4: Quality Control](#phase-4)
6. [Phase 5: Warehousing & Finishing](#phase-5)
7. [Phase 6: Packing & Dispatch](#phase-6)
8. [Phase 7: Finished Goods](#phase-7)
9. [Material Flow Tracking](#material-flow)
10. [Timeline Example](#timeline-example)

---

<a name="overview"></a>
## 🎯 1. OVERVIEW WORKFLOW

### Big Picture: Order to Delivery

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    ERP QUTY KARUNIA - COMPLETE WORKFLOW                          │
└──────────────────────────────────────────────────────────────────────────────────┘

CUSTOMER ORDER
    │
    ├─→ [PURCHASING] 3 Parallel Streams
    │       ├─ PO KAIN (Fabric) 🔑 TRIGGER 1 (Parent)
    │       ├─ PO LABEL (Label) 🔑 TRIGGER 2 (Child)
    │       └─ PO ACCESSORIES (Thread, Filling, Carton) (Child)
    │
    ├─→ [PPIC] Production Planning
    │       ├─ Create MO (Manufacturing Order)
    │       ├─ MODE: PARTIAL (PO Kain only)
    │       ├─ MODE: RELEASED (PO Label ready)
    │       └─ Auto-generate SPK per department
    │
    ├─→ [PRODUCTION] 6 Stage Process
    │       ├─ 1. CUTTING (2 streams: Body + Baju)
    │       ├─ 2. EMBROIDERY (optional, Body only)
    │       ├─ 3. SEWING (2 streams: Body + Baju)
    │       ├─ 4. WAREHOUSE FINISHING (2-stage: Stuffing + Closing)
    │       ├─ 5. PACKING (Assembly: Boneka + Baju)
    │       └─ 6. FINISHED GOODS (Ready to ship)
    │
    ├─→ [QUALITY CONTROL] Checkpoints
    │       ├─ After Cutting (size check)
    │       ├─ After Sewing (stitch quality)
    │       ├─ After Finishing (appearance)
    │       └─ Before Packing (final inspection)
    │
    └─→ [DELIVERY] Ship to Customer
            ├─ Packed in cartons (60 pcs/CTN)
            ├─ Label Week & Destination
            └─ Generate shipping documents
```

---

<a name="phase-1"></a>
## 📦 2. PHASE 1: PURCHASING & PROCUREMENT

### 2.1 Three Purchasing Specialists

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PURCHASING DEPARTMENT - 3 PARALLEL STREAMS                             │
└─────────────────────────────────────────────────────────────────────────┘

CUSTOMER ORDER: 450 pcs AFTONSPARV for Week 05
    │
    ├─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    ▼                            ▼                         ▼              │
┌──────────────┐        ┌──────────────┐        ┌──────────────┐          │
│ PURCHASING A │        │ PURCHASING B │        │ PURCHASING C │          │
│   (FABRIC)   │        │   (LABEL)    │        │ (ACCESSORIES)│          │
└──────────────┘        └──────────────┘        └──────────────┘          │
        │                       │                       │                 │
        ▼                       ▼                       ▼                 │
┌──────────────┐        ┌──────────────┐        ┌──────────────┐          │
│ PO-FAB-2026  │        │ PO-LBL-2026  │        │ PO-ACC-2026  │          │
│   -0456      │        │   -0789      │        │   -0890      │          │
│              │        │              │        │              │          │
│ • KOHAIR     │        │ • Hang Tag   │        │ • Thread     │          │
│   70.4 YD    │        │   450 pcs    │        │   2500 CM    │          │
│ • JS BOA     │        │ • Label EU   │        │ • Filling    │          │
│   4.7 YD     │        │   450 pcs    │        │   24.3 kg    │          │
│ • NYLEX      │        │ • Sticker    │        │ • Carton     │          │
│   2.5 YD     │        │   900 pcs    │        │   8 pcs      │          │
│ • Polyester  │        │              │        │              │          │
│   85.3 YD    │        │              │        │              │          │
│              │        │              │        │              │          │
│ Lead Time:   │        │ Lead Time:   │        │ Lead Time:   │          │
│ 3-5 days     │        │ 7-10 days ⚠️ │        │ 2-3 days     │          │
│              │        │              │        │              │          │
│ Status: ✅  │        │ Status: ⏳   │        │ Status: ✅   │          │
│ Received     │        │ Waiting      │        │ Received     │          │
└──────────────┘        └──────────────┘        └──────────────┘          │
        │                       │                       │                 │
        │                       │                       │                 │
        ▼                       ▼                       ▼                 │
┌─────────────────────────────────────────────────────────────────────┐   │
│  WAREHOUSE MAIN - MATERIAL RECEIVING                                │   │
│                                                                     │   │
│  ✅ Fabric Stock:                                                  │   │
│     ├─ [IKHR504] KOHAIR: 125 YD (⚠️ Low stock)                     │   │
│     ├─ [IJBR105] JS BOA: 15 YD (✅ OK)                             │   │
│     └─ [IPR301] POLYESTER: 450 YD (✅ OK)                          │   │
│                                                                     │   │
│  ⏳ Label Stock:                                                   │   │
│     └─ [ALB40011] Hang Tag: 0 pcs (🔴 OUT OF STOCK)                │   │
│                                                                     │   │
│  ✅ Accessories Stock:                                             │   │
│     ├─ [IKP20157] Filling: 45 kg (✅ OK)                           │   │
│     ├─ Thread assorted: 5,000 CM (✅ OK)                           │   │
│     └─ [ACB30104] Carton: 18 pcs (⚠️ Low stock)                    │   │
└─────────────────────────────────────────────────────────────────────┘   │
                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Dual Trigger System

```
🔑 TRIGGER 1: PO KAIN RECEIVED ✅
    │
    ├─→ System Action:
    │   ├─ Material Kain available di Warehouse Main
    │   ├─ Notify PPIC: "Fabric ready for cutting"
    │   └─ MO Status: Can upgrade to PARTIAL
    │
    └─→ PPIC Decision:
        ├─ Create MO with MODE: PARTIAL
        ├─ Cutting & Embroidery dapat start
        └─ Sewing, Finishing, Packing: BLOCKED (tunggu PO Label)

⏳ TRIGGER 2: PO LABEL RECEIVED (3-7 days later)
    │
    ├─→ System Action:
    │   ├─ Label available di Warehouse Main
    │   ├─ Auto-inherit: Week & Destination dari PO Label
    │   └─ MO Status: Auto-upgrade to RELEASED
    │
    └─→ Production Impact:
        ├─ Sewing dapat start (batch dari Embroidery sudah ready)
        ├─ Finishing dapat start
        ├─ Packing dapat start
        └─ 🎯 FULL PRODUCTION MODE ACTIVE

⚡ BENEFIT: Lead Time Reduction -3 to -5 days
```

---

<a name="phase-2"></a>
## 📋 3. PHASE 2: PRODUCTION PLANNING (PPIC)

### 3.1 PPIC Workflow

```
┌───────────────────────────────────────────────────────────────────────┐
│  PPIC DASHBOARD - MANUFACTURING ORDER CREATION                        │
└───────────────────────────────────────────────────────────────────────┘

INPUT:
├─ Customer Order: 450 pcs AFTONSPARV
├─ Delivery: Week 05-2026
├─ Destination: IKEA DC Belgium
└─ Deadline: 10 Feb 2026

PPIC CREATE MO:
┌──────────────────────────────────────┐
│ MO-2026-00089                        │
│ Artikel: [40551542] AFTONSPARV       │
│ Target: 450 pcs                      │
│ Week: W05-2026 (auto from PO Label) │
│ Destination: Belgium                 │
│                                      │
│ Status: PARTIAL ⚠️                   │
│ (Upgrade to RELEASED saat PO Label)  │
│                                      │
│ BOM Manufacturing:                   │
│ ├─ Fabric: 30+ SKU                  │
│ ├─ Thread: 9 types                  │
│ ├─ Filling: 24.3 kg                 │
│ ├─ Label: 450 pcs (WAITING)         │
│ └─ Carton: 8 pcs                    │
│                                      │
│ Material Availability:               │
│ ├─ Fabric: ✅ 95% ready             │
│ ├─ Thread: ✅ 100% ready            │
│ ├─ Filling: ✅ 100% ready           │
│ ├─ Label: 🔴 0% (PO-LBL pending)    │
│ └─ Carton: ⚠️ 50% (need reorder)    │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ AUTO SPK GENERATION                  │
│ (Broadcast to Admin Dashboard)       │
├──────────────────────────────────────┤
│                                      │
│ ✅ RELEASED (Active):                │
│ ├─ SPK-CUT-BODY-2026-00120           │
│ │  Target: 495 pcs (450 + 10%)       │
│ │  Access: ✅ GRANTED                │
│ │                                    │
│ └─ SPK-CUT-BAJU-2026-00121           │
│    Target: 495 pcs                   │
│    Access: ✅ GRANTED                │
│                                      │
│ 🔒 LOCKED (Pending PO Label):        │
│ ├─ SPK-SEW-BODY-2026-00156           │
│ ├─ SPK-SEW-BAJU-2026-00157           │
│ ├─ SPK-FIN-STUFFING-2026-00089       │
│ ├─ SPK-FIN-CLOSING-2026-00090        │
│ └─ SPK-PCK-2026-00045                │
│                                      │
│ 📅 Auto-unlock when:                │
│    PO-LBL-2026-0789 received         │
└──────────────────────────────────────┘
```

### 3.2 Material Allocation Logic

```
┌─────────────────────────────────────────────────────────────────┐
│  BOM CALCULATION & MATERIAL ALLOCATION                          │
└─────────────────────────────────────────────────────────────────┘

MO Target: 450 pcs
SPK Strategy: Flexible buffer per department

CALCULATION CASCADE:

[CUTTING] Buffer +10%
├─ SPK Target: 495 pcs (450 × 1.10)
├─ Material Allocated:
│  ├─ KOHAIR: 49.75 YD (495 × 0.1005 YD/pcs)
│  ├─ JS BOA: 4.65 YD (495 × 0.0094)
│  ├─ NYLEX BLACK: 0.50 YD (495 × 0.0010)
│  ├─ NYLEX WHITE: 2.18 YD (495 × 0.0044)
│  ├─ POLYESTER Prints: 20.66 YD
│  └─ POLYESTER Solid: 74.74 YD
│
└─ System Check:
   ├─ Available: KOHAIR 125 YD ✅ (enough)
   ├─ Available: POLYESTER 450 YD ✅
   └─ Action: CREATE RESERVATION in Warehouse

[SEWING] Buffer +15%
├─ SPK Target: 517 pcs (450 × 1.15)
├─ Constraint: ≤ Cutting Output
├─ Material Allocated:
│  ├─ Thread: 2,900 CM (variable per stitch)
│  └─ Wait for: Cut pieces from Cutting dept
│
└─ System Note: Target > MO untuk antisipasi defect

[FINISHING] Demand-Driven
├─ SPK Target: 480 pcs (not rigid to MO)
├─ Based on: Packing urgent need 465 pcs
├─ Material Allocated:
│  ├─ Filling: 25.92 kg (480 × 54 gram)
│  ├─ Thread Closing: 288 meter
│  └─ Hang Tag: 480 pcs (from PO Label)
│
└─ Flexibility: Adjust real-time to demand

[PACKING] Exact Match
├─ SPK Target: 465 pcs (urgent shipping)
├─ Material Allocated:
│  ├─ Carton: 8 pcs (60 pcs/CTN)
│  ├─ Pallet: 1 pc (shared 8 CTN)
│  └─ Pad: 1 pc
│
└─ Assembly: 1 Boneka + 1 Baju per set
```

---

<a name="phase-3"></a>
## 🏭 4. PHASE 3: PRODUCTION EXECUTION

### 4.1 Complete Production Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│  PRODUCTION FLOW - 6 STAGES (Parallel & Sequential)                        │
└────────────────────────────────────────────────────────────────────────────┘

DAY 1-2: CUTTING (2 Parallel Streams)
═══════════════════════════════════════════════════════════════════════════

    WAREHOUSE MAIN
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
    [MATERIAL ISSUE]   [MATERIAL ISSUE]   [MATERIAL ISSUE]
    Fabric for Body    Fabric for Baju   Thread & Acc
         │                  │
         ▼                  ▼
    ┌─────────────┐    ┌─────────────┐
    │  CUTTING A  │    │  CUTTING B  │
    │   (BODY)    │    │   (BAJU)    │
    │             │    │             │
    │ SPK Target: │    │ SPK Target: │
    │  495 pcs    │    │  495 pcs    │
    │             │    │             │
    │ Input Day 1:│    │ Input Day 1:│
    │  250 pcs ✅│    │  250 pcs ✅ │
    │ Input Day 2:│    │ Input Day 2:│
    │  250 pcs ✅│    │  245 pcs ✅ │
    │             │    │             │
    │ Total: 500  │    │ Total: 495  │
    │ Good: 495   │    │ Good: 495   │
    │ Defect: 5→Q │    │ Defect: 0   │
    └─────────────┘    └─────────────┘
         │                  │
         │ AUTO TRANSFER    │ HOLD FOR PACKING
         ▼                  ▼
    🔄 WIP BUFFER      📦 WAREHOUSE MAIN
    (Cut Body 495)     (Cut Baju 495)


DAY 3: EMBROIDERY (Optional, Body Only)
═══════════════════════════════════════════════════════════════════════════

    🔄 WIP BUFFER (Cut Body 495 pcs)
         │
         ▼
    ┌──────────────────┐
    │   EMBROIDERY     │
    │                  │
    │ SPK Target:      │
    │  495 pcs         │
    │                  │
    │ Process:         │
    │ ├─ Logo IKEA     │
    │ ├─ Text detail   │
    │ └─ QC check      │
    │                  │
    │ Input Day 3:     │
    │  495 pcs ✅      │
    │                  │
    │ Good Output:     │
    │  495 pcs (100%)  │
    └──────────────────┘
         │
         │ AUTO TRANSFER
         ▼
    🔄 WIP BUFFER
    (Embroidered Body 495)


DAY 4-5: SEWING (2 Parallel Streams)
═══════════════════════════════════════════════════════════════════════════

    🔄 WIP BUFFER           📦 WAREHOUSE MAIN
    (Embroidered 495)       (Cut Baju 495)
         │                        │
         ▼                        ▼
    ┌─────────────┐         ┌─────────────┐
    │  SEWING A   │         │  SEWING B   │
    │   (BODY)    │         │   (BAJU)    │
    │             │         │             │
    │ 🔒 WAIT PO │         │ 🔒 WAIT PO  │
    │    LABEL    │         │    LABEL    │
    │             │         │             │
    │ Status:     │         │ Status:     │
    │ RELEASED ✅│         │ RELEASED ✅ │
    │ (Day 4)     │         │ (Day 4)     │
    │             │         │             │
    │ SPK Target: │         │ SPK Target: │
    │  517 pcs    │         │  495 pcs    │
    │             │         │             │
    │ Day 4: 260  │         │ Day 4: 250  │
    │ Day 5: 260  │         │ Day 5: 250  │
    │             │         │             │
    │ Total: 520  │         │ Total: 500  │
    │ Good: 508   │         │ Good: 495   │
    │ Defect: 12→Q│         │ Defect: 5→Q │
    │ Rework: +10 │         │ Rework: +5  │
    │ Final: 518  │         │ Final: 500  │
    └─────────────┘         └─────────────┘
         │                        │
         │ AUTO TRANSFER          │ HOLD
         ▼                        ▼
    📦 WAREHOUSE            📦 WAREHOUSE
       FINISHING               MAIN
    (Skin 518 pcs)         (Baju 500 pcs)


DAY 6-7: WAREHOUSE FINISHING (2-Stage Process)
═══════════════════════════════════════════════════════════════════════════

STAGE 1: STUFFING (Internal Process)
────────────────────────────────────────

    📦 WAREHOUSE FINISHING
       (Skin 518 pcs available)
         │
         ▼
    ┌──────────────────────────┐
    │  STAGE 1: STUFFING       │
    │                          │
    │  SPK Target: 480 pcs     │
    │  (Demand-driven)         │
    │                          │
    │  Material Consume:       │
    │  ├─ Skin: 480 pcs        │
    │  ├─ Filling: 25.92 kg    │
    │  │  (480 × 54 gram)      │
    │  └─ Thread: 288 meter    │
    │                          │
    │  Day 6: 240 pcs ✅       │
    │  Day 7: 243 pcs ✅       │
    │                          │
    │  Total: 483 pcs          │
    │  Good: 473 pcs (97.9%)   │
    │  Defect: 10 pcs → QC     │
    │  Rework: +8 pcs          │
    │  Final: 481 pcs          │
    │                          │
    │  Inventory Update:       │
    │  ├─ Skin: 518→38 pcs     │
    │  └─ Stuffed: 0→481 pcs   │
    └──────────────────────────┘
         │
         ▼
    📦 WAREHOUSE FINISHING
       (Stuffed Body 481 pcs)


STAGE 2: CLOSING (Final Touch)
────────────────────────────────────────

    📦 WAREHOUSE FINISHING
       (Stuffed Body 481 pcs)
         │
         ▼
    ┌──────────────────────────┐
    │  STAGE 2: CLOSING        │
    │                          │
    │  SPK Target: 470 pcs     │
    │  (Match packing need)    │
    │                          │
    │  Material Consume:       │
    │  ├─ Stuffed: 470 pcs     │
    │  └─ Hang Tag: 470 pcs    │
    │                          │
    │  Day 7: 235 pcs ✅       │
    │  Day 8: 237 pcs ✅       │
    │                          │
    │  Total: 472 pcs          │
    │  Good: 468 pcs (99.2%)   │
    │  Defect: 4 pcs → QC      │
    │  Rework: +3 pcs          │
    │  Final: 471 pcs          │
    │                          │
    │  Inventory Update:       │
    │  ├─ Stuffed: 481→11 pcs  │
    │  └─ Finished: 0→471 pcs  │
    └──────────────────────────┘
         │
         │ TRANSFER TO PACKING
         ▼
    📦 WAREHOUSE MAIN
       (Finished Doll 471 pcs)


DAY 8-9: PACKING (Assembly)
═══════════════════════════════════════════════════════════════════════════

    📦 WAREHOUSE MAIN
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    Finished Doll   Cut Baju      Carton
    471 pcs         500 pcs       8 pcs
         │              │              │
         └──────────────┴──────────────┘
                     │
                     ▼
    ┌─────────────────────────────────┐
    │  PACKING DEPARTMENT             │
    │                                 │
    │  SPK Target: 465 pcs            │
    │  (Urgent shipping Week 05)      │
    │                                 │
    │  Assembly:                      │
    │  ├─ 1 Finished Doll             │
    │  ├─ 1 Baju                      │
    │  ├─ 1 Carton (60 pcs/CTN)       │
    │  └─ Label Week + Destination    │
    │                                 │
    │  Packing Schedule:              │
    │  Day 8: 300 pcs (5 CTN) ✅      │
    │  Day 9: 165 pcs (3 CTN) ✅      │
    │                                 │
    │  Total Packed: 465 pcs          │
    │  ├─ CTN 001-007: 60 pcs each    │
    │  └─ CTN 008: 45 pcs (partial)   │
    │                                 │
    │  Label Info:                    │
    │  ├─ Week: W05-2026              │
    │  ├─ Destination: Belgium        │
    │  ├─ PO: PO-LBL-2026-0789        │
    │  └─ Artikel: AFTONSPARV         │
    │                                 │
    │  Stock Remaining:               │
    │  ├─ Finished Doll: 6 pcs        │
    │  └─ Baju: 35 pcs                │
    └─────────────────────────────────┘
         │
         │ TRANSFER TO FG
         ▼
    📦 WAREHOUSE FG
       8 CTN (465 pcs)
       READY TO SHIP ✅
```

### 4.2 Real-Time WIP Tracking

```
┌────────────────────────────────────────────────────────────────────┐
│  REAL-TIME WIP DASHBOARD - LIVE INVENTORY TRACKING                 │
└────────────────────────────────────────────────────────────────────┘

ARTIKEL: [40551542] AFTONSPARV - MO-2026-00089
Status: PRODUCTION ONGOING (Day 7 of 9)

┌──────────────────┬──────────┬──────────┬──────────┬──────────────┐
│ LOCATION         │ TYPE     │ QTY      │ STATUS   │ NEXT ACTION  │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ Warehouse Main   │ Fabric   │ 25.5 YD  │ Reserved │ Hold buffer  │
│ Warehouse Main   │ Thread   │ 1200 CM  │ Reserved │ Hold buffer  │
│ Warehouse Main   │ Filling  │ 19.1 kg  │ Reserved │ For next MO  │
│ Warehouse Main   │ Baju     │ 500 pcs  │ Ready    │ Wait Packing │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ WIP Cutting      │ Cut Body │ 0 pcs    │ Complete │ -            │
│ WIP Embroidery   │ Emb Body │ 0 pcs    │ Complete │ -            │
│ WIP Sewing       │ Skin     │ 0 pcs    │ Complete │ -            │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ WH Finishing     │ Skin     │ 38 pcs   │ Buffer   │ For next MO  │
│ WH Finishing     │ Stuffed  │ 11 pcs   │ Buffer   │ Continue Day8│
│ WH Finishing     │ Finished │ 471 pcs  │ Ready ✅ │ To Packing   │
├──────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ Packing Line     │ Sets     │ 465 pcs  │ Packed ✅│ To FG        │
│ Warehouse FG     │ Cartons  │ 8 CTN    │ Ready ✅ │ Ship Day 10  │
└──────────────────┴──────────┴──────────┴──────────┴──────────────┘

📊 PRODUCTION SUMMARY:
├─ MO Target: 450 pcs
├─ Actual Output: 465 pcs (103.3% ✅)
├─ Overall Yield: 94.1%
├─ Total Defects: 41 pcs (4.0%)
├─ Rework Success: 34 pcs (82.9% recovery ✅)
├─ Scrap Loss: 7 pcs (0.7%)
└─ Status: ON-TIME for Week 05 deadline ✅
```

---

<a name="phase-4"></a>
## ✅ 5. PHASE 4: QUALITY CONTROL

### 5.1 QC Checkpoints

```
┌────────────────────────────────────────────────────────────────────┐
│  QUALITY CONTROL - 4 CRITICAL CHECKPOINTS                          │
└────────────────────────────────────────────────────────────────────┘

CHECKPOINT 1: AFTER CUTTING
════════════════════════════════════════════════════════════════════
Location: Cutting Department Exit
Inspector: QC Staff A (Random sampling 10%)

Check Items:
├─ Size accuracy (±2mm tolerance)
├─ Edge cutting quality (no fray)
├─ Pattern alignment (matching marks)
└─ Quantity verification

Input: 500 pcs Cut Body
Sample: 50 pcs (10%)
Result:
├─ PASS: 48 pcs (96%) ✅
├─ MINOR: 2 pcs (4%) → Mark for careful sewing
└─ REJECT: 0 pcs

Action: Release to Embroidery


CHECKPOINT 2: AFTER SEWING
════════════════════════════════════════════════════════════════════
Location: Sewing Department Exit
Inspector: QC Staff B (100% inline inspection)

Check Items:
├─ Stitch quality (no loose thread)
├─ Stitch per inch (SPI) standard
├─ Seam strength (pull test)
├─ Assembly accuracy (all parts attached)
└─ Appearance (no wrinkle)

Input: 520 pcs Sewn Body
Inspection Result:
├─ PASS: 508 pcs (97.7%) ✅ → To Finishing
├─ MINOR DEFECT: 10 pcs (1.9%) → Rework queue
│  └─ Issues: Loose thread, misaligned stitch
├─ MAJOR DEFECT: 2 pcs (0.4%) → Scrap
│  └─ Issues: Broken seam, wrong assembly
└─ REWORK SUCCESS: 10 → 10 recovered (100%) ✅

Final Output: 518 pcs Good


CHECKPOINT 3: AFTER FINISHING
════════════════════════════════════════════════════════════════════
Location: Warehouse Finishing Exit (Stage 2)
Inspector: QC Staff C (100% inspection)

Check Items:
├─ Stuffing quality (firmness check)
├─ Shape consistency (no deform)
├─ Closing quality (hidden stitches)
├─ Hang tag attachment (secure)
├─ Cleanliness (no dust/stain)
└─ Safety check (no sharp edges)

Input: 472 pcs Finished Doll
Inspection Result:
├─ PASS: 468 pcs (99.2%) ✅ → To Packing
├─ MINOR DEFECT: 4 pcs (0.8%) → Quick fix
│  └─ Issues: Hang tag loose, minor stain
├─ MAJOR DEFECT: 0 pcs
└─ REWORK SUCCESS: 4 → 3 recovered (75%)

Final Output: 471 pcs Good


CHECKPOINT 4: PRE-PACKING FINAL
════════════════════════════════════════════════════════════════════
Location: Packing Department Entry
Inspector: QC Staff D (Random + 100% visual)

Check Items:
├─ Final appearance (overall quality)
├─ Baju fit test (boneka + baju assembly)
├─ Label check (correct Week + Destination)
├─ Compliance check (EU safety standards)
└─ Metal detector test (no needle)

Input: 471 Finished Doll + 500 Baju
Inspection Result:
├─ Finished Doll: 471 pcs PASS ✅
├─ Baju: 500 pcs PASS ✅
├─ Assembly Test: 20 samples - All OK ✅
└─ Metal Detector: All PASS ✅

Action: Release for Packing

───────────────────────────────────────────────────────────────────

📊 OVERALL QC PERFORMANCE:

Total Inspection Points: 4 checkpoints
Total Units Inspected: 1,963 pcs (sum of all stages)
Overall Defect Rate: 4.0%
Recovery Rate: 82.9% ✅ (Target: >80%)
Scrap Rate: 0.7% (Target: <2%)

Status: QUALITY STANDARD MET ✅
```

### 5.2 Rework Module Workflow

```
┌────────────────────────────────────────────────────────────────────┐
│  REWORK/REPAIR MODULE - DEFECT MANAGEMENT SYSTEM                   │
└────────────────────────────────────────────────────────────────────┘

DEFECT DETECTED → QC INSPECTION → REWORK QUEUE → RE-QC → PASS/SCRAP

Example: Sewing Defects (12 pcs)

Step 1: DEFECT CAPTURE (Auto by QC)
────────────────────────────────────────
┌──────────────────────────────────────┐
│ DEFECT RECORD #D-2026-0156-001       │
│                                      │
│ SPK: SPK-SEW-BODY-2026-00156         │
│ Batch Date: 05-Feb-2026              │
│ QC Inspector: Staff B                │
│                                      │
│ Defect Details:                      │
│ ├─ Qty: 12 pcs                       │
│ ├─ Type: MINOR (10 pcs)              │
│ │  └─ Issue: Loose thread, gap       │
│ └─ Type: MAJOR (2 pcs)               │
│    └─ Issue: Broken seam             │
│                                      │
│ Root Cause (Operator Input):         │
│ ├─ Machine tension issue             │
│ ├─ Operator: OP-SEW-023              │
│ └─ Machine: SEW-LINE-02              │
│                                      │
│ Decision:                            │
│ ├─ REWORK: 10 pcs → Queue #RW-001    │
│ └─ SCRAP: 2 pcs → Waste bin          │
└──────────────────────────────────────┘

Step 2: REWORK QUEUE ASSIGNMENT
────────────────────────────────────────
┌──────────────────────────────────────┐
│ REWORK QUEUE #RW-001                 │
│                                      │
│ Priority: HIGH (urgent MO)           │
│ Assigned to: Rework Specialist A     │
│ Est. Time: 2 hours (10 pcs)          │
│                                      │
│ Rework SOP:                          │
│ ├─ 1. Unstitch defect area           │
│ ├─ 2. Re-stitch dengan mesin khusus  │
│ ├─ 3. Trim loose threads             │
│ └─ 4. Submit to Re-QC                │
│                                      │
│ Status: IN PROGRESS ⏳               │
└──────────────────────────────────────┘

Step 3: RE-QC INSPECTION
────────────────────────────────────────
┌──────────────────────────────────────┐
│ RE-QC INSPECTION                     │
│                                      │
│ Rework Batch: #RW-001 (10 pcs)       │
│ Inspector: QC Staff B                │
│                                      │
│ Re-inspection Result:                │
│ ├─ PASS: 10 pcs (100%) ✅           │
│ ├─ FAIL: 0 pcs                       │
│ └─ Recovery Rate: 100%               │
│                                      │
│ Cost Analysis:                       │
│ ├─ Rework Cost: $100 (10 × $10)      │
│ ├─ vs Scrap Cost: $400 (10 × $40)    │
│ └─ Savings: $300 💰                 │
│                                      │
│ Action: Add back to Good Output      │
└──────────────────────────────────────┘

Step 4: SYSTEM UPDATE (Auto)
────────────────────────────────────────
SPK-SEW-BODY-2026-00156 Updated:

├─ Total Production: 520 pcs
├─ Initial Good: 508 pcs
├─ Defect: 12 pcs
│  ├─ Rework Success: +10 pcs ✅
│  └─ Scrap: -2 pcs
└─ Final Good Output: 518 pcs (508 + 10)

───────────────────────────────────────────────────────────────────

📊 REWORK MODULE DASHBOARD (Monthly):

Total Defects: 127 pcs
├─ Reworked: 98 pcs
├─ Recovery Success: 87 pcs (88.8%) ✅
├─ Recovery Fail: 11 pcs → Scrap
└─ Direct Scrap: 29 pcs

COPQ (Cost of Poor Quality):
├─ Rework Cost: $980
├─ Scrap Cost: $1,600 (40 × $40)
├─ Total COPQ: $2,580
└─ Savings from Rework: $2,480 💰

Top Defect Types:
1. Loose thread (45 cases)
2. Stitch misalignment (32 cases)
3. Stuffing uneven (21 cases)

Action Plan:
├─ Retrain operators with high defect rate
├─ Maintenance schedule for problematic machines
└─ Update SOP for critical processes
```

---

<a name="phase-5"></a>
## 🏭 6. PHASE 5: WAREHOUSING & FINISHING

### 6.1 Warehouse Structure

```
┌────────────────────────────────────────────────────────────────────┐
│  WAREHOUSE SYSTEM - 3 TYPES                                        │
└────────────────────────────────────────────────────────────────────┘

WAREHOUSE MAIN (Material & Components)
════════════════════════════════════════════════════════════════════

Function: Store raw materials + Cut components
Location: Building A, Floor 1

Inventory Types:
├─ RAW MATERIAL - FABRIC
│  ├─ [IKHR504] KOHAIR: 125 YD
│  ├─ [IJBR105] JS BOA: 15 YD
│  ├─ [INYR002] NYLEX BLACK: 2.5 YD
│  └─ [IPR301] POLYESTER: 450 YD
│
├─ RAW MATERIAL - THREAD
│  ├─ Thread Brown: 1,200 CM
│  ├─ Thread White: 800 CM
│  └─ Thread Black: 500 CM
│
├─ RAW MATERIAL - ACCESSORIES
│  ├─ [IKP20157] Filling: 45 kg
│  ├─ [ALB40011] Hang Tag: 0 pcs 🔴
│  ├─ [ALL40030] Label EU: 450 pcs
│  └─ [ACB30104] Carton: 18 pcs ⚠️
│
└─ SEMI-FINISHED (Cut Components)
   ├─ Cut Baju (various designs): 1,250 pcs
   └─ Cut Accessories: 850 pcs

Material Issue Process:
1. SPK-CUT requests material
2. Warehouse staff scan barcode
3. System deduct stock automatically
4. Material delivered to Cutting dept
5. Cutting input production daily


WAREHOUSE FINISHING (2-Stage Internal Conversion)
════════════════════════════════════════════════════════════════════

Function: Special warehouse for Finishing process
Location: Building A, Floor 2

Inventory Types (2 Stages):
├─ STAGE 1 INVENTORY: SKIN
│  ├─ [AFTONSPARV_WIP_SKIN]: 38 pcs
│  ├─ [VANDRING_WIP_SKIN]: 125 pcs
│  └─ [GOSIG_WIP_SKIN]: 89 pcs
│
└─ STAGE 2 INVENTORY: STUFFED BODY
   ├─ [AFTONSPARV_WIP_STUFFED]: 11 pcs
   ├─ [VANDRING_WIP_STUFFED]: 67 pcs
   └─ [GOSIG_WIP_STUFFED]: 34 pcs

Internal Process Flow:
┌─────────────────────────────────────┐
│ RECEIVE from Sewing                 │
│ ├─ Type: SKIN (sewn body, unstuff)  │
│ ├─ Scan barcode                     │
│ └─ Update Stage 1 Inventory         │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ STAGE 1: STUFFING                   │
│ ├─ Issue: Skin + Filling + Thread   │
│ ├─ Process: Stuff & close           │
│ ├─ Duration: ~3 min/pcs             │
│ └─ Output: Stuffed Body             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ INTERNAL TRANSFER (No paperwork)    │
│ ├─ Deduct: Stage 1 (Skin)           │
│ ├─ Add: Stage 2 (Stuffed Body)      │
│ └─ System auto-update inventory     │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ STAGE 2: CLOSING                    │
│ ├─ Issue: Stuffed + Hang Tag        │
│ ├─ Process: Attach tag + final QC   │
│ ├─ Duration: ~2 min/pcs             │
│ └─ Output: Finished Doll            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ TRANSFER to Packing                 │
│ ├─ Deduct: Stage 2 (Stuffed)        │
│ ├─ Add: Warehouse Main (FG ready)   │
│ └─ Generate delivery note           │
└─────────────────────────────────────┘

Unique Features:
✅ Dual inventory tracking (Skin vs Stuffed)
✅ No manual paperwork for internal transfer
✅ Real-time stock validation per stage
✅ Material consumption auto-tracked
✅ Demand-driven production (not rigid MO)


WAREHOUSE FINISHED GOODS (Ready to Ship)
════════════════════════════════════════════════════════════════════

Function: Store packed finished goods
Location: Building B, Floor 1 (near loading dock)

Inventory Types:
├─ PACKED SETS (Ready to ship)
│  ├─ [40551542] AFTONSPARV: 8 CTN (465 pcs)
│  │  Week: W05-2026, Dest: Belgium
│  ├─ [00511543] VANDRING: 12 CTN (720 pcs)
│  │  Week: W06-2026, Dest: Germany
│  └─ [70401234] GOSIG: 5 CTN (300 pcs)
│     Week: W07-2026, Dest: France
│
└─ PACKING MATERIALS
   ├─ Carton 570×375: 150 pcs
   ├─ Pallet: 8 pcs
   └─ Plastic wrap: 20 rolls

Shipping Process:
1. Customer order confirmed
2. FG Warehouse pull stock by Week + Dest
3. Generate shipping document
4. Load to truck with barcode scan
5. Update stock real-time
6. Customer notified (auto email)

Storage Rules:
├─ FIFO (First In First Out)
├─ Segregate by Week & Destination
├─ Max storage: 30 days
└─ Temperature controlled: 20-25°C
```

---

<a name="phase-6"></a>
## 📦 7. PHASE 6: PACKING & DISPATCH

### 7.1 Packing Workflow

```
┌────────────────────────────────────────────────────────────────────┐
│  PACKING DEPARTMENT - FINAL ASSEMBLY                               │
└────────────────────────────────────────────────────────────────────┘

INPUT MATERIALS (dari 3 sumber):
════════════════════════════════════════════════════════════════════

Source 1: Warehouse Finishing
├─ Finished Doll: 471 pcs
└─ Status: QC Passed ✅

Source 2: Warehouse Main
├─ Cut Baju: 500 pcs
└─ Status: Ready ✅

Source 3: Warehouse Main
├─ Carton 570×375: 8 pcs
├─ Pallet: 1 pc
├─ Pad: 1 pc
└─ Plastic wrap: 2 rolls


PACKING LINE PROCESS:
════════════════════════════════════════════════════════════════════

Station 1: PAIRING & QUALITY CHECK
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Operator: Pick 1 Doll + 1 Baju       │
│ Check:                               │
│ ├─ Size compatibility ✅             │
│ ├─ Color matching ✅                 │
│ ├─ Hang tag attached ✅              │
│ └─ Visual defect check ✅            │
│                                      │
│ Output: 1 Complete Set               │
└──────────────────────────────────────┘
         │
         ▼
Station 2: METAL DETECTOR TEST
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Pass through metal detector          │
│ Check: No needle/sharp objects       │
│ Result:                              │
│ ├─ PASS: 465 sets ✅ (100%)         │
│ └─ FAIL: 0 sets                      │
└──────────────────────────────────────┘
         │
         ▼
Station 3: CARTON PACKING
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Standard: 60 sets per carton         │
│                                      │
│ Packing Detail:                      │
│ ├─ CTN-001: 60 sets ✅              │
│ ├─ CTN-002: 60 sets ✅              │
│ ├─ CTN-003: 60 sets ✅              │
│ ├─ CTN-004: 60 sets ✅              │
│ ├─ CTN-005: 60 sets ✅              │
│ ├─ CTN-006: 60 sets ✅              │
│ ├─ CTN-007: 60 sets ✅              │
│ └─ CTN-008: 45 sets ✅ (partial)    │
│                                      │
│ Total: 465 sets in 8 cartons         │
└──────────────────────────────────────┘
         │
         ▼
Station 4: LABELING & SEALING
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Generate & attach labels:            │
│                                      │
│ Label Info (Auto from PO Label):     │
│ ├─ Week: W05-2026                    │
│ ├─ Destination: IKEA DC Belgium      │
│ ├─ PO Number: PO-LBL-2026-0789       │
│ ├─ Artikel: [40551542] AFTONSPARV    │
│ ├─ Qty per CTN: 60 pcs (or 45)       │
│ └─ Barcode: FG-2026-00089-CTN###     │
│                                      │
│ Sealing:                             │
│ ├─ Tape securely                     │
│ ├─ Shrink wrap (optional)            │
│ └─ Weight verification               │
└──────────────────────────────────────┘
         │
         ▼
Station 5: BARCODE SCANNING
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Android App: Scan each carton        │
│                                      │
│ Scan Result (Real-time):             │
│ ├─ CTN-001: ✅ Verified             │
│ ├─ CTN-002: ✅ Verified             │
│ ├─ CTN-003: ✅ Verified             │
│ ├─ CTN-004: ✅ Verified             │
│ ├─ CTN-005: ✅ Verified             │
│ ├─ CTN-006: ✅ Verified             │
│ ├─ CTN-007: ✅ Verified             │
│ └─ CTN-008: ✅ Verified (45 pcs)    │
│                                      │
│ System Action:                       │
│ ├─ Update FG Inventory: +8 CTN       │
│ ├─ Deduct WIP: -465 sets             │
│ ├─ Status: READY TO SHIP ✅         │
│ └─ Notify: PPIC + Management         │
└──────────────────────────────────────┘
         │
         ▼
Station 6: PALLETIZING
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Stack cartons on pallet:             │
│                                      │
│ Pallet Configuration:                │
│ ├─ Layer 1: 4 CTN (bottom)           │
│ ├─ Layer 2: 4 CTN (top)              │
│ ├─ Total: 8 CTN per pallet           │
│ └─ Plastic wrap: 3 layers            │
│                                      │
│ Pallet Label:                        │
│ ├─ Total Cartons: 8                  │
│ ├─ Total Units: 465 pcs              │
│ ├─ Gross Weight: ~85 kg              │
│ ├─ Destination: Belgium              │
│ └─ Barcode: PLT-2026-00089           │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ TRANSFER TO FG WAREHOUSE             │
│                                      │
│ Status: READY FOR SHIPMENT ✅        │
│ ETA Shipping: 10-Feb-2026            │
└──────────────────────────────────────┘
```

### 7.2 Dispatch & Shipping

```
┌────────────────────────────────────────────────────────────────────┐
│  DISPATCH PROCESS - FROM FG WAREHOUSE TO CUSTOMER                  │
└────────────────────────────────────────────────────────────────────┘

DAY 10: SHIPPING DAY (10-Feb-2026)
════════════════════════════════════════════════════════════════════

06:00 - Shipping Order Preparation
────────────────────────────────────────
┌──────────────────────────────────────┐
│ System Generate:                     │
│                                      │
│ 1. DELIVERY NOTE (DN)                │
│    ├─ DN-2026-00089                  │
│    ├─ Customer: IKEA                 │
│    ├─ Destination: DC Belgium        │
│    ├─ Week: W05-2026                 │
│    └─ Total: 8 CTN (465 pcs)         │
│                                      │
│ 2. PACKING LIST                      │
│    ├─ Artikel: AFTONSPARV            │
│    ├─ CTN 001-007: 60 pcs each       │
│    ├─ CTN 008: 45 pcs                │
│    └─ Total Qty: 465 pcs             │
│                                      │
│ 3. COMMERCIAL INVOICE (optional)     │
│    ├─ Value: EUR 6,975               │
│    ├─ Price: EUR 15/pcs              │
│    └─ Terms: FOB Jakarta             │
└──────────────────────────────────────┘

08:00 - Loading Process
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Truck arrives at loading dock        │
│ Operator scan pallet barcode:        │
│ ├─ PLT-2026-00089 ✅                 │
│ │  └─ Contains: 8 CTN, 465 pcs       │
│ │                                    │
│ Forklift load to truck:              │
│ ├─ Position: Secure strapping        │
│ ├─ Photo documentation               │
│ └─ Driver sign delivery note         │
│                                      │
│ System Update:                       │
│ ├─ FG Stock: -8 CTN                  │
│ ├─ Status: IN-TRANSIT 🚚            │
│ └─ Tracking: #TRK-2026-00089         │
└──────────────────────────────────────┘

09:00 - Dispatch Confirmation
────────────────────────────────────────
┌──────────────────────────────────────┐
│ Auto-notification sent:              │
│                                      │
│ 📧 TO: IKEA Belgium DC              │
│ Subject: Shipment Dispatched         │
│                                      │
│ Dear IKEA Team,                      │
│                                      │
│ Your order has been dispatched:      │
│ ├─ PO: PO-LBL-2026-0789              │
│ ├─ Week: W05-2026                    │
│ ├─ Artikel: AFTONSPARV               │
│ ├─ Qty: 465 pcs (8 cartons)          │
│ ├─ Tracking: #TRK-2026-00089         │
│ └─ ETA: 15-Feb-2026                  │
│                                      │
│ Attached documents:                  │
│ ├─ Delivery Note (PDF)               │
│ ├─ Packing List (PDF)                │
│ └─ Photos (JPG)                      │
│                                      │
│ Best regards,                        │
│ PT Quty Karunia                      │
└──────────────────────────────────────┘

10:00 - Final Status Update
────────────────────────────────────────
┌──────────────────────────────────────┐
│ MO-2026-00089 STATUS: COMPLETE ✅    │
│                                      │
│ Summary:                             │
│ ├─ Order Date: 25-Jan-2026           │
│ ├─ Start Production: 01-Feb-2026     │
│ ├─ Finish Production: 09-Feb-2026    │
│ ├─ Dispatch Date: 10-Feb-2026        │
│ └─ Total Lead Time: 16 days ✅      │
│                                      │
│ Performance:                         │
│ ├─ Target: 450 pcs                   │
│ ├─ Delivered: 465 pcs (103.3%) ✅   │
│ ├─ On-Time: YES ✅                  │
│ └─ Quality: PASS ✅                 │
│                                      │
│ Financial:                           │
│ ├─ Material Cost: $5,580             │
│ ├─ Labor Cost: $930                  │
│ ├─ Total COGS: $6,510                │
│ ├─ Selling Price: $6,975             │
│ └─ Profit: $465 (6.7% margin)        │
└──────────────────────────────────────┘
```

---

<a name="phase-7"></a>
## 📊 8. PHASE 7: FINISHED GOODS

### 8.1 FG Inventory Management

```
┌────────────────────────────────────────────────────────────────────┐
│  FINISHED GOODS WAREHOUSE - REAL-TIME DASHBOARD                    │
└────────────────────────────────────────────────────────────────────┘

CURRENT INVENTORY (10-Feb-2026, 10:00 AM)
════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────┐
│ ARTIKEL                  │ WEEK │ DEST    │ CTN │ PCS  │ STATUS  │
├──────────────────────────┼──────┼─────────┼─────┼──────┼─────────┤
│ [40551542] AFTONSPARV    │ W05  │ Belgium │ 0   │ 0    │ SHIP ✅│
│ [00511543] VANDRING      │ W06  │ Germany │ 12  │ 720  │ READY   │
│ [70401234] GOSIG GOLDEN  │ W07  │ France  │ 5   │ 300  │ READY   │
│ [30551678] JATTELIK      │ W08  │ Sweden  │ 8   │ 480  │ PACK⏳  │
│ [50331245] BLAHAJ        │ W09  │ UK      │ 0   │ 0    │ PROD⏳  │
└──────────────────────────────────────────────────────────────────┘

SHIPPING SCHEDULE (Next 7 Days)
════════════════════════════════════════════════════════════════════

11-Feb: VANDRING to Germany (12 CTN, 720 pcs)
12-Feb: GOSIG to France (5 CTN, 300 pcs)
15-Feb: JATTELIK to Sweden (8 CTN, 480 pcs)
18-Feb: BLAHAJ to UK (10 CTN, 600 pcs) - In Production

ALERTS & ACTIONS
════════════════════════════════════════════════════════════════════

✅ All Week 05 orders dispatched on-time
✅ Week 06-07 ready for shipment
⏳ Week 08: Packing in progress (ETA: 11-Feb)
⚠️ Week 09: Production delayed (material shortage)
   └─ Action: Expedite PO-FAB-2026-0567 (BLAHAJ fabric)
```

---

<a name="material-flow"></a>
## 🔄 9. MATERIAL FLOW TRACKING

### 9.1 Complete Traceability Chain

```
┌────────────────────────────────────────────────────────────────────┐
│  MATERIAL FLOW TRACKING - END-TO-END TRACEABILITY                  │
│  Example: [IKHR504] KOHAIR FABRIC                                  │
└────────────────────────────────────────────────────────────────────┘

TRANSACTION CHAIN (5W1H Tracking)
════════════════════════════════════════════════════════════════════

1. RECEIVING (Material In)
────────────────────────────────────────
WHO:    Warehouse Staff (Budi)
WHAT:   [IKHR504] KOHAIR D.BROWN
WHEN:   25-Jan-2026 14:30
WHERE:  Warehouse Main - Rack A3
WHY:    PO-FAB-2026-0456 received
HOW:    Scan barcode, QC check passed
        ├─ Qty Received: 125 YD
        ├─ Batch: BTH-IKHR504-2026-01
        └─ Supplier: PT Kain Jaya

2. RESERVATION (Material Reserved)
────────────────────────────────────────
WHO:    System (Auto)
WHAT:   [IKHR504] KOHAIR D.BROWN
WHEN:   28-Jan-2026 08:00
WHERE:  Warehouse Main - Rack A3
WHY:    MO-2026-00089 validated by PPIC
HOW:    BOM calculation triggered
        ├─ Qty Reserved: 49.75 YD
        ├─ For: SPK-CUT-BODY-2026-00120
        ├─ Available: 125 → 75.25 YD
        └─ Status: RESERVED (cannot use for other MO)

3. MATERIAL ISSUE (Material Out)
────────────────────────────────────────
WHO:    Warehouse Staff (Siti)
WHAT:   [IKHR504] KOHAIR D.BROWN
WHEN:   01-Feb-2026 07:15
WHERE:  Warehouse Main → Cutting Dept
WHY:    SPK-CUT-BODY-2026-00120 start production
HOW:    Pull system triggered by SPK
        ├─ Qty Issued: 49.75 YD
        ├─ Delivery Note: DN-INT-2026-00234
        ├─ Received by: Admin Cutting (Andi)
        ├─ Stock Update: 75.25 → 25.5 YD
        └─ Status: IN-USE (at Cutting dept)

4. CONSUMPTION (Material Used)
────────────────────────────────────────
WHO:    Admin Cutting (Andi)
WHAT:   [IKHR504] KOHAIR D.BROWN
WHEN:   01-Feb-2026 16:45 (Day 1 production)
WHERE:  Cutting Department - Line 1
WHY:    Production input daily
HOW:    Admin submit production output
        ├─ Qty Used: 25.5 YD (Day 1)
        ├─ Output: 250 pcs Cut Body
        ├─ UOM Conversion: 25.5 YD → 250 pcs
        ├─ Yield: 250 / (25.5/0.1005) = 98.4%
        ├─ Operator: OP-CUT-015, OP-CUT-023
        └─ Machine: CUT-LINE-01

5. VARIANCE DETECTION (Auto Alert)
────────────────────────────────────────
WHO:    System (Auto-monitor)
WHAT:   [IKHR504] KOHAIR D.BROWN
WHEN:   01-Feb-2026 16:46 (1 min after input)
WHERE:  Backend validation engine
WHY:    Consumption variance check
HOW:    Compare actual vs BOM standard
        ├─ Expected: 25.13 YD (250 × 0.1005)
        ├─ Actual: 25.5 YD
        ├─ Variance: +1.5% (within tolerance ✅)
        └─ Action: Log only (no alert)

6. FINAL RECONCILIATION (End of Day)
────────────────────────────────────────
WHO:    System (Auto + Warehouse SPV review)
WHAT:   [IKHR504] KOHAIR D.BROWN
WHEN:   01-Feb-2026 23:59 (End of Day)
WHERE:  Database reconciliation
WHY:    Daily closing & accuracy check
HOW:    Sum all transactions
        ├─ Opening Balance: 125 YD
        ├─ Received Today: 0 YD
        ├─ Issued Today: 49.75 YD
        ├─ Returned: 0 YD
        ├─ Closing Balance: 75.25 YD ✅
        ├─ Physical Count: 75 YD
        ├─ Discrepancy: -0.25 YD (-0.33%)
        └─ Status: ACCEPTABLE (within 1% tolerance)

═══════════════════════════════════════════════════════════════════

AUDIT TRAIL SUMMARY:
├─ Total Transactions: 6 events
├─ Start: 25-Jan 14:30 (Receiving)
├─ End: 01-Feb 23:59 (Reconciliation)
├─ Duration: 7 days
├─ Touched By: 3 users (Budi, Siti, Andi)
├─ Locations: 2 (Warehouse, Cutting)
└─ Traceability: 100% ✅ (Full chain recorded)

VARIANCE ANALYSIS:
├─ Expected Consumption: 25.13 YD
├─ Actual Consumption: 25.5 YD
├─ Variance: +1.5%
├─ Root Cause: Normal fabric waste (edge trim)
└─ Action: No action required (within tolerance)
```

---

<a name="timeline-example"></a>
## ⏱️ 10. TIMELINE EXAMPLE: 16-Day Production Cycle

### 10.1 Gantt Chart View

```
┌────────────────────────────────────────────────────────────────────┐
│  PRODUCTION TIMELINE - MO-2026-00089 (AFTONSPARV 450 pcs)          │
│  Start: 25-Jan-2026 → End: 10-Feb-2026 (16 days total)             │
└────────────────────────────────────────────────────────────────────┘

WEEK 04 (25-31 Jan)
════════════════════════════════════════════════════════════════════
Day  │ Date    │ Activity                              │ Status
─────┼─────────┼───────────────────────────────────────┼──────────
-5   │ 25-Jan  │ 📦 PO Kain received                   │ ✅
     │         │ 📋 PPIC create MO (MODE: PARTIAL)     │ ✅
     │         │ 🔄 System: Auto-generate SPK          │ ✅
─────┼─────────┼────────────────────────────────────────┼──────────
-4   │ 26-Jan  │ 📦 Material issue to Cutting          │ ✅
     │         │ (Fabric, thread for 495 pcs)           │
─────┼─────────┼────────────────────────────────────────┼──────────
-3   │ 27-Jan  │ ⏸️  Standby (setup machines)           │ ✅
─────┼─────────┼────────────────────────────────────────┼──────────
-2   │ 28-Jan  │ 📦 PO Label received 🔑               │ ✅
     │         │ 🔄 MO upgrade: PARTIAL → RELEASED     │ ✅
     │         │ 📝 Week & Dest auto-inherited         │ ✅
─────┼─────────┼────────────────────────────────────────┼──────────
-1   │ 29-Jan  │ 📦 Material issue to Finishing        │ ✅
     │         │ (Filling 25.92 kg, Hang Tag 480 pcs)   │
─────┼─────────┼────────────────────────────────────────┼──────────
WEEKEND (30-31 Jan) - No production

WEEK 05 (01-07 Feb)
════════════════════════════════════════════════════════════════════
Day  │ Date    │ Activity                              │ Status
─────┼─────────┼───────────────────────────────────────┼──────────
1    │ 01-Feb  │ ✂️  CUTTING Day 1                     │ ✅
     │         │ ├─ Body: 250 pcs                      │
     │         │ └─ Baju: 250 pcs                      │
─────┼─────────┼───────────────────────────────────────┼──────────
2    │ 02-Feb  │ ✂️  CUTTING Day 2                     │ ✅
     │         │ ├─ Body: 250 pcs (Total: 500)         │
     │         │ └─ Baju: 245 pcs (Total: 495)         │
─────┼─────────┼───────────────────────────────────────┼──────────
3    │ 03-Feb  │ 🎨 EMBROIDERY (Body only)             │ ✅
     │         │ └─ 495 pcs (100%)                     │
─────┼─────────┼───────────────────────────────────────┼──────────
4    │ 04-Feb  │ 🪡 SEWING Day 1 (Both streams)        │ ✅
     │         │ ├─ Body: 260 pcs                      │
     │         │ └─ Baju: 250 pcs                      │
─────┼─────────┼───────────────────────────────────────┼──────────
5    │ 05-Feb  │ 🪡 SEWING Day 2                       │ ✅
     │         │ ├─ Body: 260 pcs (Total: 520)         │
     │         │ │  └─ Good: 518 after QC & rework     │
     │         │ └─ Baju: 250 pcs (Total: 500)         │
─────┼─────────┼───────────────────────────────────────┼──────────
6    │ 06-Feb  │ 🧸 FINISHING Day 1 (Stuffing)         │ ✅
     │         │ └─ 240 pcs (50%)                      │
─────┼─────────┼───────────────────────────────────────┼──────────
7    │ 07-Feb  │ 🧸 FINISHING Day 2 (Stuffing cont.)   │ ✅
     │         │ ├─ 243 pcs (Total: 483)               │
     │         │ ├─ Good: 481 after QC & rework        │
     │         │ └─ CLOSING start: 235 pcs             │
─────┼─────────┼───────────────────────────────────────┼──────────
WEEKEND (08-09 Feb) - Continue Finishing & Packing

8    │ 08-Feb  │ 🧸 FINISHING (Closing cont.)          │ ✅
     │         │ ├─ 237 pcs (Total: 472)               │
     │         │ └─ Good: 471 after QC                 │
     │         │ 📦 PACKING start: 300 pcs (5 CTN)     │
─────┼─────────┼────────────────────────────────────────┼──────────
9    │ 09-Feb  │ 📦 PACKING complete                   │ ✅
     │         │ └─ 165 pcs (3 CTN) - Total: 8 CTN     │
     │         │ ✅ QC Final check: PASS               │
     │         │ 📊 Transfer to FG Warehouse           │
─────┼─────────┼────────────────────────────────────────┼──────────
10   │ 10-Feb  │ 🚚 DISPATCH to Belgium                │ ✅
     │         │ └─ 8 CTN (465 pcs) - Week 05          │
     │         │ 📧 Customer notification sent         │
     │         │ ✅ MO-2026-00089 COMPLETE             │

═══════════════════════════════════════════════════════════════════

SUMMARY:
├─ Total Calendar Days: 16 days (25-Jan to 10-Feb)
├─ Production Days: 10 days (exclude weekends + prep days)
├─ Lead Time with Dual Trigger: 16 days ✅
├─ Lead Time without Dual Trigger: 21-23 days ❌
├─ Benefit: -5 to -7 days faster (23.8% improvement)
└─ Status: ON-TIME DELIVERY ✅
```

---

## 📊 WORKFLOW SUMMARY & KEY METRICS

### Overall Process Efficiency

```
┌────────────────────────────────────────────────────────────────────┐
│  KEY PERFORMANCE INDICATORS (KPIs)                                 │
└────────────────────────────────────────────────────────────────────┘

PRODUCTION METRICS:
├─ MO Target: 450 pcs
├─ Final Delivery: 465 pcs (103.3% ✅)
├─ Overall Yield: 94.1%
├─ Lead Time: 16 days (vs 21-23 days traditional)
└─ On-Time Delivery: YES ✅

QUALITY METRICS:
├─ Total Production: 1,018 pcs (across all depts)
├─ Total Defects: 41 pcs (4.0%)
├─ Rework Success: 34 pcs (82.9% recovery ✅)
├─ Final Scrap: 7 pcs (0.7%)
└─ QC Pass Rate: 96% ✅

INVENTORY METRICS:
├─ Material Accuracy: 99.7% (real-time tracking)
├─ Stock Variance: <1% (physical vs system)
├─ WIP Visibility: 100% (real-time dashboard)
└─ Zero Stock-out: YES ✅

FINANCIAL METRICS:
├─ Material Cost: $5,580
├─ Labor Cost: $930
├─ COGS per Unit: $14.00
├─ Selling Price: $15.00
└─ Profit Margin: 6.7%

SYSTEM PERFORMANCE:
├─ Data Entry Time: -70% (vs manual Excel)
├─ Report Generation: 5 seconds (vs 3-5 days)
├─ Approval Workflow: 2 hours (vs 2 days)
├─ Material Tracking: Real-time (vs daily manual)
└─ User Satisfaction: 95% ✅
```

---

## 🎯 KESIMPULAN

### Keunggulan Workflow ERP Quty Karunia

1. **🔄 End-to-End Integration**
   - Satu sistem dari Purchasing sampai Finished Goods
   - Zero data entry redundancy
   - Real-time visibility across all departments

2. **🔑 Dual Trigger Innovation**
   - Start production dengan PO Kain (early start)
   - Full release dengan PO Label (auto-inherit data)
   - Lead time reduction: -23.8% (5-7 days faster)

3. **📊 Real-Time Tracking**
   - WIP visibility instant (parsialitas production)
   - Material flow tracking (5W1H audit trail)
   - Dashboard real-time untuk management

4. **✅ Quality Assurance**
   - 4 QC checkpoints dengan 100% traceability
   - Rework module dengan 82.9% recovery rate
   - COPQ analysis untuk continuous improvement

5. **🏭 Warehouse Innovation**
   - 2-stage finishing dengan dual inventory
   - Demand-driven production (flexible target)
   - Paperless internal transfer

6. **📦 Smart Packing**
   - Auto-inherit Week & Destination dari PO Label
   - Barcode scanning dengan Android app
   - Real-time FG inventory update

7. **🔐 Security & Compliance**
   - Multi-level approval workflow
   - Full audit trail (siapa, apa, kapan, dimana, kenapa)
   - Fraud prevention system

8. **📱 Mobile Integration**
   - Admin input produksi via tablet
   - Barcode scanning via Android app
   - Offline mode dengan auto-sync

---

**Dokumen ini menunjukkan complete workflow dari customer order hingga delivery, dengan fokus pada traceability, efficiency, dan quality assurance.**

**Untuk pertanyaan lebih lanjut, hubungi:**  
Daniel Rizaldy - Developer & System Architect  
Email: daniel@qutykarunia.com  
Phone: +62 812-3456-7890
