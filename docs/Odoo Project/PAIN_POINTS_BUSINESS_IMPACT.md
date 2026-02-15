# 11 PAIN POINTS KRITIS - PT QUTY KARUNIA
## Business Impact Analysis untuk Sales Odoo

**Untuk**: Project Director & Business Analyst Odoo  
**Dari**: Daniel Rizaldy (IT Lead - PT Quty Karunia)  
**Tanggal**: 13 Februari 2026  
**Fokus**: Detailed pain points dengan quantified business impact

---

## EXECUTIVE SUMMARY

PT Quty Karunia mengalami **11 pain points kritis** akibat sistem manual (Excel + WhatsApp + kertas). Operational inefficiency yang signifikan dalam:
- Material waste & shortage
- Overtime berlebihan
- Quality issues tidak ter-detect
- Admin overwhelmed dengan manual data entry

**Urgency**: IKEA (80% revenue) mulai demand **real-time traceability** untuk compliance. Risk kehilangan customer utama jika tidak implement ERP proper.

---

## [CRITICAL] PAIN POINT #1: MATERIAL SHORTAGE TIBA-TIBA

### Current Situation:
Production **STOP mendadak** karena material tertentu tiba-tiba habis (tidak ketahuan sebelumnya).

**Frequency**: 8-10x per bulan  
**Impact per Incident**:
- Production downtime: 2-4 jam
- Overtime untuk kejar delivery: 10-15 jam per incident
- Emergency purchasing: Premium price +10-20%
- Customer complaint risk: Delay delivery

**Root Cause**:
- Stock tracking pakai **Excel** → Tidak real-time!
- Consumption tidak auto-calculated → Manual input sering terlambat atau salah
- No safety stock alert → Baru tahu habis pas mau pakai!
- Multi-location inventory (8 locations) tidak terintegrasi

**Real Example**:
> "Hari ini Sewing dept mau start batch 1000 pcs AFTONSPARV. Cek warehouse: Thread hitam HABIS! Purchasing buru-buru order emergency. Production delay 3 jam. SPV frustasi, Manager marah."

**Business Impact**:
- **Direct Cost**: Overtime + emergency purchasing premium yang signifikan
- **Indirect Cost**: Customer trust menurun, team morale down, planning chaos
- **Risk**: IKEA penalty jika miss delivery deadline

**What We Need from ERP**:
- Real-time stock visibility semua locations
- Auto-calculate material requirement per MO
- Safety stock alert BEFORE stock out
- Integrated purchasing workflow (auto-trigger RFQ)

---

## [CRITICAL] PAIN POINT #2: TIDAK TAHU WIP REAL-TIME

### Current Situation:
Manager & SPV **TIDAK TAHU** berapa stock WIP di setiap dept RIGHT NOW.

**Question Yang Tidak Bisa Dijawab**:
- "Batch W05-AFTONSPARV sekarang ada di dept mana? Sudah selesai berapa pcs?"
- "Cutting hari ini output real berapa? Target vs Actual?"
- "Mengapa Sewing dept lambat? Stock menumpuk atau input dari Embroidery kurang?"

**Current "Solution"**:
SPV **WhatsApp** ke setiap admin dept:
- "Mbak, sudah selesai berapa pcs W05-AFTONSPARV?"
- Admin reply (kadang telat 1-2 jam karena sibuk)
- SPV compile manual di **Excel**
- Data sudah **outdated** pas Manager tanya!

**Business Impact**:
- **Planning impossible**: Tidak bisa prioritize batch based on real data
- **Bottleneck detection delayed**: Baru ketahuan end-of-day → TOO LATE!
- **Admin overwhelmed**: 30-40 WA messages per hari hanya untuk status update
- **Decision making slow**: Manager tidak punya visibility untuk quick response

**Quantified Impact**:
- Admin time wasted: **2-3 jam/hari** hanya untuk compile WIP report
- Overtime akibat late bottleneck detection yang signifikan
- Opportunity cost: Cannot prioritize urgent orders effectively

**What We Need from ERP**:
- Real-time WIP dashboard per dept, per MO, per SKU
- Partial transfer tracking (dept to dept)
- Bottleneck alert automatic
- Mobile access untuk SPV (check WIP from anywhere)

---

## [CRITICAL] PAIN POINT #3: QUALITY DEFECT TIDAK TRACEABLE

### Current Situation:
IKEA reject batch karena quality issue. **Kami tidak bisa trace** root cause:
- Batch mana yang affected?
- Material dari supplier mana? Lot number berapa?
- Produced di tanggal berapa? Shift berapa?
- QC checkpoint mana yang miss defect?

**Current "Solution"**:
- QC Inspector catat defect di **kertas form**
- Rework handled manual (tidak ter-record proper)
- Rejected items counted, tapi **no detailed reason tracking**
- Historical data: **TIDAK ADA!**

**IKEA Audit Question** (Kami Tidak Bisa Answer):
> "Show me defect trend last 6 months for AFTONSPARV article. Which dept has highest defect rate? What is the most common defect type?"

**Kami answer**: "Maaf, data defect tidak ter-record sistematis." → **IKEA NOT HAPPY!**

**Business Impact**:
- **IKEA compliance risk**: Audit trail tidak ada → Risk warning letter atau kehilangan order
- **Continuous improvement impossible**: Tidak ada data untuk analyze root cause
- **Cost of quality unknown**: Berapa actual cost dari defect & rework? TIDAK TAHU!
- **Repeat mistakes**: Same defect terjadi berulang karena tidak ada tracking

**Quantified Impact**:
- Estimated defect cost: **5-8% dari total production** (material + labor wasted)
- Rework labor cost (tidak ter-record): Signifikan dan tidak terlacak
- Risk penalty from IKEA: **UNQUANTIFIABLE but CRITICAL!**

**What We Need from ERP**:
- QC checkpoint recording integrated ke production flow
- Defect taxonomy & reason tracking
- Rework workflow dengan traceability
- Quality dashboard: Defect rate per dept, per SKU, trending
- Batch/lot traceability (material origin → finished goods)

---

## [CRITICAL] PAIN POINT #4: DUAL TRIGGER SYSTEM MANUAL

### Current Situation:
Production workflow kami **UNIQUE**: 1 MO butuh **2 PO triggers**:
1. **PO Fabric** datang week 0 → Unlock Cutting & Embroidery
2. **PO Label** datang week +2 → Unlock Sewing, Finishing, Packing

**Kenapa Harus Begini?**
- IKEA kirim Label PO **2 minggu setelah Fabric PO**
- Label contains: Week number, Destination country, Compliance info
- Production **HARUS start** dari Fabric PO (tidak bisa tunggu 2 minggu!)
- Tapi Packing **HARUS tunggu** Label PO (packaging depend on destination)

**Current "Solution"**:
Admin track **manual di Excel + WhatsApp**:
- "PO Fabric datang → Start Cutting"
- "JANGAN mulai Sewing dulu! Tunggu PO Label!"
- "PO Label datang → Boleh lanjut Sewing!"

**Error Frequent**:
- Admin lupa block dept → Sewing start duluan → Salah packaging destination → **IKEA REJECT!**
- Label datang terlambat → Dept Sewing & Finishing **idle menunggu** → Waste capacity
- Excel formula salah → Dept unlock terlalu cepat atau terlambat → Chaos!

**Business Impact**:
- **Admin overwhelmed**: Manual tracking 30-50 active MOs dengan dual trigger → Error unavoidable!
- **Lead time suboptimal**: Fabric idle 2 minggu karena takut start production salah → Missed opportunity untuk lead time reduction!
- **Packaging error**: 2-3x per bulan wrong destination packaging → IKEA complaint

**What We Need from ERP**:
- State machine untuk MO: DRAFT → PARTIAL (PO Fabric OK) → RELEASED (PO Label OK)
- Auto-unlock dept based on PO arrival
- Lock critical fields (Week, Destination) setelah PO Label datang
- Dashboard: Clear status tracking per MO

---

## [HIGH] PAIN POINT #5: EXCEL-BASED PLANNING

### Current Situation:
Production planning pakai **Excel complex macro** yang:
- Developed 5+ tahun lalu (original developer sudah resign!)
- Formula complex & fragile (satu cell salah → chain reaction error!)
- Manual input 200+ SKU parameters setiap minggu
- No validation → Salah input tidak ketahuan sampai production start!

**Problems**:
- **Error prone**: Formula Excel sering break (macro corruption, accidental delete)
- **Single point of failure**: Hanya 1-2 orang ngerti Excel file → Risk jika resign!
- **Not scalable**: Excel slow untuk 478 SKU × 8 weeks planning horizon
- **No version control**: Tidak tahu siapa change apa & kapan

**Real Example**:
> "Planning Excel tiba-tiba error #REF! Panic! Admin debug 3 jam untuk fix. Production delay karena schedule tidak release on time."

**Business Impact**:
- **Planning time excessive**: 5 jam per hari untuk compile & validate plan
- **Frequent errors**: 3-5 planning mistakes per bulan → Wrong material order, wrong priority
- **Knowledge risk**: Jika admin key resign → Planning collapse!

**What We Need from ERP**:
- Integrated MRP (Material Requirement Planning)
- Auto-calculate capacity, material requirement, lead time
- Validation rules prevent wrong input
- Audit trail: Who change what when

---

## [HIGH] PAIN POINT #6: TARGET PRODUKSI FLAT

### Current Situation:
Admin set production target = **Customer order quantity** (flat 1:1).

**Problem**: Defect rate 3-8% per dept! Result: **SHORTAGE!**

**Example**:
- Customer order: 1000 pcs
- Cutting target: 1000 pcs
- Cutting defect: 40 pcs (4%) → Output: 960 pcs [SHORTAGE]
- Sewing target: 1000 pcs (tapi input cuma 960!) → Result: SHORTAGE 40 pcs!

**Current "Solution"**:
SPV estimate buffer **ad-hoc** berdasarkan "feeling":
- Experienced SPV: Add 5-10% buffer → Usually OK
- New SPV: Add 2% buffer → Frequent shortage!
- No konsistensi antar dept

**Business Impact**:
- **Shortage frequent**: 8-10x per bulan
- **Overtime untuk kejar**: 15-20 jam extra per incident
- **Delivery delay**: 2-3x per bulan miss deadline → IKEA unhappy!

**What We Need from ERP**:
- Auto-calculate target per dept based on:
  - Customer order quantity
  - Historical defect rate per dept
  - Configurable buffer percentage
- Reverse calculation: Packing need 1000 → Finishing harus produce 1020 → Sewing 1040 → dst
- Alert jika actual output < target (risk shortage early detection)

---

## [HIGH] PAIN POINT #7: MANUAL MATERIAL TRACKING

### Current Situation:
Material consumption tracked **manual**:
- Admin catat di **kertas form** saat pakai material
- End-of-day: Input manual ke **Excel**
- End-of-week: Reconcile dengan warehouse stock → Often tidak match!

**Problems**:
- **Data entry time**: 2-3 jam per hari admin untuk input consumption data
- **Error frequent**: Salah catat quantity, salah unit (roll vs pcs), double entry
- **Reconciliation nightmare**: Warehouse stock vs consumption data tidak match → Investigation 2-4 jam!
- **No real-time visibility**: Baru tahu consumption pattern end-of-week → TOO LATE untuk adjust!

**Business Impact**:
- **Admin capacity wasted**: 15-20 jam per minggu hanya untuk data entry
- **Inventory inaccuracy**: Stock data tidak reliable untuk planning
- **Material waste undetected**: Over-consumption tidak ketahuan real-time

**What We Need from ERP**:
- Auto-backflush material consumption based on BOM
- Exception handling: Manual input untuk material consumption diluar BOM
- Real-time material balance per dept
- Variance report: Expected vs Actual consumption

---

## [MEDIUM] PAIN POINT #8: STOCK OPNAME 1 HARI PENUH

### Current Situation:
Stock opname = **Production STOP 1 hari penuh!**

**Process**:
- Semua dept stop production
- All staff (admin + workers) involved untuk counting
- Count ALL 8 locations sekaligus
- Manual input ke Excel → Reconcile dengan system → Adjustment entry
- Time: **8-10 jam** (1 hari kerja habis!)

**Problems**:
- **Production loss**: 1 hari produksi hilang untuk stock opname
- **Result tidak akurat**: Karena terburu-buru (mau cepat selesai) → Counting error frequent
- **Chaos**: 50+ orang counting simultaneously di 8 locations → Confusion, miscommunication
- **Frequency insufficient**: Cuma 1x per bulan (karena too disruptive) → Inventory accuracy low

**Business Impact**:
- **Direct production loss**: Signifikan per stock opname (1x/bulan)
- **Inventory inaccuracy**: Stock data only accurate 1-2 minggu setelah opname, then drift again
- **Team fatigue**: Staff complain stock opname day = "hari paling capek & boring"

**What We Need from ERP**:
- Department-level stock opname (not full warehouse)
- Rolling schedule: Today Cutting, Tomorrow Embroidery, dst (production continue!)
- Mobile input untuk fast counting (tablet/barcode scanner)
- Auto-compare physical vs system → Generate adjustment transaction
- More frequent opname (2x per bulan per dept) tanpa disrupt production

---

## [MEDIUM] PAIN POINT #9: REWORK TIDAK TER-RECORD

### Current Situation:
QC reject items → Rework/repair → **Tidak ter-record proper!**

**Current "Solution"**:
- QC Inspector catat reject di **kertas**
- SPV suruh worker rework
- Rework selesai → Submit to QC again
- **Tidak ada system record** untuk:
  - Berapa qty di-rework?
  - Berapa labor time untuk rework?
  - Berapa cost dari rework?
  - Rework success rate berapa %?

**IKEA Audit Question**:
> "Show me rework data last quarter. What is the cost of quality?"

**Kami answer**: "Data rework tidak complete." → **IKEA concern about quality control process!**

**Business Impact**:
- **IKEA compliance risk**: No audit trail untuk quality process
- **Cost of quality unknown**: Tidak bisa calculate true cost per SKU (material + labor + rework)
- **Process improvement impossible**: Tidak ada data untuk analyze "Defect type apa yang paling sering? Rework rate trend membaik atau memburuk?"

**What We Need from ERP**:
- Rework Order workflow: QC reject → Create Rework WO → Assign to dept → Complete → Re-QC
- Track rework cost: Labor time + material consumed
- Rework success/fail tracking
- Dashboard: Rework rate per dept, per SKU, cost analysis

---

## [MEDIUM] PAIN POINT #10: MULTI-UNIT CONVERSION MANUAL

### Current Situation:
Material dibeli & dipakai dalam **unit berbeda**:

| Material | Unit Beli | Unit Pakai | Conversion |
|----------|-----------|------------|------------|
| Fabric | Roll/Yard | Pcs | 1 roll = 50 pcs |
| Filling | Karung 25kg | Gram | 1 karung = 25,000g |
| Thread | Cone 5000m | Meter | 1 cone = 5,000m |
| Label | Pack 1000pcs | Pcs | 1 pack = 1,000pcs |

**Problem**: Admin **CONFUSED!** 

**Frequent Errors**:
- Input production consume "fabric 2 ROLL" (seharusnya 100 PCS) → Stock data salah!
- Calculate "butuh 150kg filling" untuk 5000 pcs → Lupa convert ke unit beli (karung) → Order kurang!
- Stock opname: Warehouse count dalam "10 roll", System dalam "500 pcs" → Reconciliation nightmare!

**Current "Solution"**:
Admin calculate manual pakai **calculator + Excel conversion table**:
- Time consuming: 5-10 menit per SKU untuk calculate
- Error prone: 3-5 conversion mistakes per minggu
- No validation: Salah unit tidak ter-detect sampai reconciliation

**Business Impact**:
- **Purchasing error**: Order quantity salah (terlalu banyak atau kurang) → 2-3x per bulan
- **Inventory data tidak reliable**: Stock balance tidak akurat karena mixed units
- **Admin time wasted**: 1-2 jam per hari untuk convert units manual

**What We Need from ERP**:
- UOM (Unit of Measure) auto-conversion
- Validation: Prevent input wrong unit untuk transaction type tertentu
- Display smart: Warehouse view dalam unit beli, Production view dalam unit pakai
- Configurable conversion rate per material

---

## [MEDIUM] PAIN POINT #11: WHATSAPP-BASED COORDINATION

### Current Situation:
Semua koordinasi production pakai **WhatsApp Group**:
- Group "Produksi Team" (50+ members)
- 100-200 messages per hari!
- Info penting **tenggelam** dalam chit-chat
- Tidak traceable: "Siapa yang approve X? Kapan?" → Scroll 500 messages untuk cari!

**Problems**:
- **Information overload**: Admin overwhelmed dengan WA notifications
- **Critical info missed**: Urgent message tenggelam → Production delay
- **No accountability**: "Aku sudah WA lho!" vs "Aku tidak terima WA kamu!" → He said she said
- **No audit trail**: Historical decision tidak bisa di-trace

**Real Example**:
> Manager: "Siapa yang approve start production MO-2026-050 tanpa PO Label?"  
> Admin: "Pak SPV WA suruh mulai aja!"  
> SPV: "Aku tidak WA begitu! Mungkin salah interpret!"  
> Manager: "Check WA history!" → Scroll 800 messages → **Info tidak ketemu!**

**Business Impact**:
- **Miscommunication frequent**: 5-8x per bulan → Production error, rework
- **Decision delay**: Admin tunggu WA approval → 30 menit-2 jam delay
- **Accountability zero**: Cannot identify who responsible untuk mistake

**What We Need from ERP**:
- In-system messaging/notification (not WA!)
- Approval workflow dengan audit trail
- Task assignment clear (who responsible what)
- Notification priority: Critical (popup) vs Info (log only)

---

## SUMMARY: TOTAL BUSINESS IMPACT

### Strategic Risks (Unquantified but CRITICAL):

**[URGENT] IKEA Compliance Risk** (HIGHEST PRIORITY!):
- IKEA demand real-time traceability → Kami tidak punya!
- Audit trail untuk quality → Kami tidak punya!
- Risk: **Warning letter → Order reduction → Kehilangan 80% revenue source!**

**[URGENT] Scalability Impossible**:
- Current volume: 1-1.5 juta pcs/bulan
- Excel + manual process **CANNOT scale** untuk 2x volume
- IKEA plan increase order → **Kami tidak ready!**

**[URGENT] Knowledge Risk**:
- Key staff resign → Planning collapse (Excel macro complex)
- No system documentation → New staff training 3-6 bulan!

**[URGENT] Team Burnout**:
- Admin overtime 4-5 jam per hari → Morale low, turnover risk high
- Manual repetitive work → Frustration, error meningkat

---

## PRIORITIES UNTUK IMPLEMENTATION

### Phase 1 (CRITICAL - Quick Wins):
**Pain Points to Address First**:
1. [CRITICAL] #2: Real-Time WIP Tracking (visibility immediate!)
2. [CRITICAL] #1: Material Shortage Prevention (safety stock, auto-RFQ)
3. [CRITICAL] #4: Dual Trigger System (unlock complex workflow)

**Expected Impact**: Significant operational efficiency improvement

### Phase 2 (HIGH VALUE):
4. [HIGH] #6: Flexible Target System (reduce shortage)
5. [HIGH] #7: Auto Material Tracking (reduce admin burden)
6. [HIGH] #3: QC Traceability (IKEA compliance)

**Expected Impact**: IKEA compliance ready + further cost reduction

### Phase 3 (OPTIMIZATION):
7. [MEDIUM] #9: Rework Recording (cost visibility)
8. [MEDIUM] #8: Dept-Level Stock Opname (production continuity)
9. [MEDIUM] #10 & #11: UOM Conversion + Workflow (admin efficiency)

**Expected Impact**: Continuous improvement foundation

---

## CONCLUSION

PT Quty Karunia menghadapi **operational crisis** akibat sistem manual yang **tidak scalable** dan **IKEA compliance pressure** yang growing.

**Key Messages untuk Sales Odoo**:
1. **Urgent need**: Bukan "nice to have", tapi **business survival issue!**
2. **Strategic value**: Maintain IKEA relationship (80% revenue) + scalability untuk growth
3. **Phased approach**: Start dengan high-impact pain points (Phase 1) untuk quick wins
4. **Efficiency gains**: Signifikan operational improvements yang terukur

**Ready untuk**:
- Discovery workshop (detail pain points review)
- Process observation (on-site recommended untuk full understanding)
- Gap analysis collaboration
- Pilot/PoC discussion untuk validate solution

---

**Contact**: Daniel Rizaldy (IT Lead - PT Quty Karunia)  
**Supporting Documents**:
- REQUIREMENTS_KOMPREHENSIF_PT_QUTY_KARUNIA.md (full details 35,000+ words)
- EXECUTIVE_SUMMARY_SALES_ODOO.md (1-page overview)
- BUSINESS_REQUIREMENTS_ONLY.md (non-technical requirements)
