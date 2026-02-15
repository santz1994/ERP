# BUSINESS REQUIREMENTS ONLY
## PT Quty Karunia - Non-Technical Requirements untuk Odoo

**Untuk**: Sales Odoo - Project Director & Business Analyst  
**Tanggal**: 13 Februari 2026  
**Fokus**: Business needs & process requirements (NO technical solution/code)

---

## PURPOSE DOKUMEN INI

Dokumen ini menjelaskan **APA yang kami butuhkan** (business requirements), **BUKAN BAGAIMANA** implementasinya (technical solution). 

Gap analysis & technical solution adalah domain expertise tim Odoo.

---

## 1. DUAL PURCHASE ORDER TRIGGER SYSTEM

### Business Context:
Customer (IKEA) kirim 2 Purchase Order untuk 1 production batch:
- **PO #1 (Fabric/Materials)**: Datang di week 0
- **PO #2 (Label)**: Datang di week +2 (2 minggu kemudian)

Label PO **SANGAT PENTING** karena berisi:
- Week number (determine delivery schedule)
- Destination negara (affect packaging requirement)
- Compliance information (IKEA specific)

### Business Requirement:

**Yang Kami Butuhkan**:
1. **Admin bisa create Manufacturing Order** begitu PO Fabric datang
2. **System unlock Cutting & Embroidery dept** untuk mulai produksi TANPA label
3. **Dept lain (Sewing, Finishing, Packing) masih LOCKED** sampai PO Label datang
4. **Begitu PO Label datang** → System auto-unlock ALL dept + lock field Week & Destination (tidak bisa diubah lagi)
5. **Status tracking clear**: Admin tahu exact status MO (waiting fabric, waiting label, in progress)

**Business Rules**:
- [CRITICAL] Production TIDAK bisa selesai sampai Packing tanpa PO Label datang
- Material fabric boleh consumed begitu PO Fabric datang
- Label HARUS ada sebelum Packing dept mulai kerja
- [WARNING] Jika PO Label datang terlambat → Dept Sewing & Finishing menunggu!

**Business Value**:
- **Lead time reduction**: -29% (28 hari → 18-20 hari) 
- **Better material utilization**: Fabric tidak idle 2 minggu
- **Flexibility**: Rush order bisa start production lebih cepat

### Current Manual Process (Pain Point):
Sekarang: Admin track pakai **Excel + WhatsApp**  
- "PO Fabric datang, mulai Cutting ya!"
- "PO Label belum datang, JANGAN mulai Sewing!"
- **Error frequent**: Admin lupa block dept → Salah packaging → IKEA reject!

---

## 2. FLEXIBLE PRODUCTION TARGET PER DEPARTMENT

### Business Context:
Setiap production dept produce **LEBIH banyak** dari customer order untuk cover defect rate.

**Contoh**:
- Customer order: **500 pcs**
- Cutting dept target: **520 pcs** (+4% buffer untuk defect)
- Sewing dept target: **510 pcs** (+2% buffer)
- Finishing dept target: **505 pcs** (+1% buffer)
- Packing dept target: **500 pcs** (exact customer order)

**Mengapa?** Karena:
- Cutting defect ~3-4% (fabric salah potong, reject)
- Sewing defect ~2% (jahit crooked, benang lepas)
- Finishing defect ~1% (stuffing tidak rata)
- QC reject ~1-2% (tidak lolos quality check)

### Business Requirement:

**Yang Kami Butuhkan**:
1. **System auto-calculate target per dept** berdasarkan:
   - Customer order quantity
   - Defect rate historis dept tersebut
   - Buffer percentage (configurable per dept)

2. **Target reverse calculation** (dari Packing mundur ke Cutting):
   - Packing need 500 pcs → Finishing harus produce 505 pcs
   - Finishing need 505 pcs → Sewing harus produce 510 pcs
   - Dst...

3. **Constraint validation**: Target dept B TIDAK BOLEH lebih besar dari output dept A
   - Contoh: Sewing need 510 pcs, tapi Cutting hanya produce 508 pcs → **ALERT!**

4. **Real-time adjustment**: Jika defect rate tiba-tiba naik → System suggest adjust target dept berikutnya

**Business Rules**:
- Target boleh adjusted manual by SPV (override auto-calculation)
- System track actual output vs target per dept
- [ALERT] Alert jika actual output significantly below target (risk shortage!)
- Report defect rate per dept untuk continuous improvement

**Business Value**:
- **Shortage reduction**: -80% (8x/bulan → <2x/bulan)
- **Better planning**: SPV bisa predict bottleneck early
- **Data-driven**: Defect rate tracking untuk process improvement

### Current Manual Process (Pain Point):
Sekarang: SPV estimate target **ad-hoc** berdasarkan "feeling"
- Tidak konsisten antar dept
- Sering shortage karena tidak hitung defect enough
- Overtime untuk kejar kekurangan → Cost naik!

---

## 3. 2-STAGE FINISHING INTERNAL CONVERSION

### Business Context:
Dept Finishing punya **2 sub-process** yang distinct:

**Stage 1: STUFFING**
- Input: Skin (dari Sewing) + Filling material (dari Warehouse)
- Process: Isi filling ke dalam skin
- Output: **Stuffed Body** (boneka sudah isi, tapi belum ditutup & tag)

**Stage 2: CLOSING**
- Input: Stuffed Body (dari Stage 1) + Hang Tag (dari Warehouse)
- Process: Tutup lubang isi + pasang hang tag
- Output: **Finished Doll** (siap transfer ke Packing)

**UNIQUE**: Ini BUKAN transfer antar dept! Ini **internal process** di Finishing dept di 2 area berbeda!

### Business Requirement:

**Yang Kami Butuhkan**:
1. **Track stock intermediate product** (Stuffed Body):
   - Harus tahu berapa sudah di-stuff tapi belum di-close
   - Stock Stuffed Body counted terpisah dari Skin & Finished Doll

2. **Material consumption per stage**:
   - Stage 1 consume: Skin + Filling (auto-deduct dari WH Main)
   - Stage 2 consume: Stuffed Body + Hang Tag (auto-deduct)

3. **No physical transfer document** antara Stage 1 & 2:
   - Internal movement dalam Finishing dept
   - Tapi system HARUS track inventory movement!

4. **Quality check per stage**:
   - QC check setelah Stuffing (detect filling tidak rata)
   - QC check setelah Closing (detect tag placement wrong)
   - Reject di stage 1 affect material calculation stage 2

**Business Rules**:
- Stuffing & Closing bisa parallel (different batches)
- Stuffed Body inventory tracked di "WH-Finishing" sub-location
- [IMPORTANT] Material waste per stage harus traceable (untuk cost analysis)
- Admin Finishing input hasil per stage (not combined)

**Business Value**:
- **Inventory accuracy**: +27% (70% → 95%+) untuk Finishing dept
- **Bottleneck detection**: Tahu Stage 1 or 2 yang slow
- **Material waste control**: Track filling over-consumption per stage
- **Process optimization**: Data-driven untuk improve efficiency

### Current Manual Process (Pain Point):
Sekarang: **Campur aduk!** 
- Tidak tahu stock Stuffed Body vs Finished Doll
- Material consumption tidak tracked per stage
- Stock opname Finishing dept = **CHAOS** (4 jam untuk counting!)

---

## 4. MULTI-UNIT CONVERSION & AUTO-VALIDATION

### Business Context:
Material dibeli & digunakan dalam **unit berbeda**:

| Material | Unit Beli | Unit Pakai | Conversion |
|----------|-----------|------------|------------|
| Fabric | Roll/Yard | Pcs (potongan) | 1 roll = 50 pcs |
| Filling | Karung (25 kg) | Gram per pcs | 1 karung = 25,000g |
| Thread | Cone (5000m) | Meter per pcs | 1 cone = 5000m |
| Accessories | Pack (100 pcs) | Pcs | 1 pack = 100 pcs |

**Problem**: Admin sering **confused** mau input unit apa!

### Business Requirement:

**Yang Kami Butuhkan**:
1. **Auto-conversion** saat input:
   - Admin input "2 roll fabric" → System convert ke "100 pcs available"
   - Admin input "1 karung filling" → System convert ke "25,000 gram"

2. **Unit validation** untuk prevent error:
   - Admin input production consume "fabric 10 PCS" → OK
   - Admin input "fabric 10 ROLL" → ERROR "Unit salah! Production tidak consume ROLLs"

3. **Display smart** di interface:
   - Warehouse view: Show "3.5 rolls" (unit beli)
   - Production view: Show "175 pcs available" (unit pakai)
   - Purchasing view: Show BOTH (untuk reorder calculation)

4. **Conversion rate management**:
   - IT Admin bisa set conversion rate per material
   - Alert jika conversion rate berubah drastis (supplier change, etc)

**Business Rules**:
- Conversion rate bisa berbeda per SKU (boneka kecil vs besar)
- System allow fractional units (0.5 roll, 2.3 kg)
- [CRITICAL] Prevent mixing units (ROLL + PCS dalam 1 transaction = ERROR!)
- Report consumption dalam BOTH units (untuk analysis)

**Business Value**:
- **Error reduction**: -90% untuk unit conversion mistakes
- **Time saving**: Admin tidak perlu manual calculate conversion
- **Accuracy**: Stock data reliable untuk planning

### Current Manual Process (Pain Point):
Sekarang: Admin calculate manual pakai **calculator + Excel**
- Sering salah convert (especially filling: kg → gram)
- Input error frequent → Stock data tidak akurat
- Confusion saat stock opname (unit apa yang dicatat?)

---

## 5. REAL-TIME WIP TRACKING SYSTEM

### Business Context:
Production proses panjang (6 stages) + batch besar (1000-2000 pcs).

**Yang Kami Butuh Tahu SETIAP SAAT**:
- Berapa stock WIP di setiap dept RIGHT NOW?
- Batch mana yang stuck di dept tertentu?
- Dept mana yang bottleneck hari ini?

### Business Requirement:

**Yang Kami Butuhkan**:
1. **Real-time dashboard** untuk Manager:
   - View inventory per dept per SKU (tidak delayed!)
   - Filter by MO / Batch / Week

2. **Partial transfer support**:
   - Cutting selesai 300 pcs → Transfer ke Embroidery (tidak tunggu 1000 pcs selesai!)
   - Embroidery receive 300 pcs → Start kerja immediately
   - Next partial: 400 pcs → Transfer again

3. **Stock location per dept**:
   - WH-Cutting, WH-Embroidery, WH-Sewing, WH-Finishing, WH-Packing
   - Each dept punya "input queue" & "output buffer" stock

4. **Transfer tracking**:
   - History: Kapan & berapa qty transferred?
   - Admin input transfer pakai mobile (barcode scan ideal!)
   - Auto-alert jika dept A output ≠ dept B input (lost material!)

**Business Rules**:
- Transfer boleh partial (not full batch)
- Dept bisa start kerja begitu receive transfer (not wait full batch)
- [WARNING] Quality check bisa reject partial batch → Re-transfer ke dept sebelumnya
- Dashboard update IMMEDIATELY after transfer (tidak end-of-day!)

**Business Value**:
- **Visibility**: Manager tahu exact WIP real-time (no guessing!)
- **Bottleneck detection**: Clear visual mana dept yang slow
- **Planning agility**: Bisa shift priority batch based on real data

### Current Manual Process (Pain Point):
Sekarang: **TIDAK TAHU WIP real-time!**
- SPV tanya dept by WhatsApp: "Sudah berapa pcs selesai?"
- Data tidak reliable (SPV estimate doang)
- End-of-day baru ketahuan ada bottleneck → TOO LATE!

---

## 6. QUALITY CONTROL LOOP (REWORK/REPAIR)

### Business Context:
QC check di 4 titik: After Cutting, After Embroidery, After Sewing, After Finishing.

**QC Result bisa**:
- **PASS**: Continue ke dept berikutnya
- **REWORK**: Minor defect, bisa diperbaiki
- **REJECT**: Major defect, scrap (tidak bisa repair)

**Rework Process**:
- Defect di Sewing (jahit crooked) → Rework di Sewing → Re-QC → Continue
- Defect di Finishing (filling kurang) → Rework di Finishing → Re-QC → Continue

### Business Requirement:

**Yang Kami Butuhkan**:
1. **QC recording integrated**:
   - QC Inspector input hasil check (Pass / Rework / Reject)
   - Photo defect (optional tapi useful!)
   - Defect category (fabric, thread, filling, tag, etc)

2. **Rework workflow**:
   - QC reject item → Create "Rework Order" to dept that dept
   - Dept Admin receive rework queue → Fix defect
   - Dept Admin submit to QC → Re-QC check
   - If pass → Continue production, If fail again → Scrap

3. **Scrap/rejection recording**:
   - Track qty & value of rejected items
   - Reason for rejection (untuk root cause analysis)
   - Cost impact (material lost, labor wasted)

4. **Traceability**:
   - Defect bisa di-trace back ke batch/MO specific
   - History: Item ini sudah di-rework berapa kali?
   - Report: Defect pattern per dept, per SKU, per week

**Business Rules**:
- Item boleh di-rework max 2x, after that = SCRAP
- Rework cost tracked terpisah (untuk cost analysis)
- [WARNING] Manager notified jika defect rate > threshold (5%)
- Dashboard: Defect rate per dept, trending over time

**Business Value**:
- **Quality improvement**: Data-driven untuk fix process issue
- **Cost control**: Tahu exact cost dari defect & rework
- **IKEA compliance**: Audit trail untuk quality issues

### Current Manual Process (Pain Point):
Sekarang: Rework **tidak ter-record!**
- QC reject item → SPV handle manual → Tidak tercatat di system
- Tidak tahu berapa cost dari rework
- IKEA audit: "Show me defect trend last 6 months" → Kami tidak punya data!

---

## 7. DEPARTMENT-LEVEL WAREHOUSE & STOCK OPNAME

### Business Context:
Setiap dept produksi punya **mini-warehouse** sendiri untuk:
- WIP stock (waiting to be processed)
- Material buffer (thread, accessories, dll)
- Output buffer (waiting transfer ke dept berikutnya)

**Stock Opname Problem**:
Sekarang: Stock opname HARUS stop SEMUA produksi 1 hari penuh (chaos!)

### Business Requirement:

**Yang Kami Butuhkan**:
1. **Stock location per dept**:
   - WH-Cutting, WH-Embroidery, WH-Sewing, WH-Finishing, WH-Packing
   - Each location tracked independent

2. **Department-level stock opname**:
   - Admin Cutting bisa stock opname WH-Cutting TANPA affect dept lain
   - Sewing tetap jalan, Finishing tetap jalan
   - Rolling stock opname: Today Cutting, Tomorrow Embroidery, dst

3. **Stock opname workflow**:
   - SPV initiate stock opname untuk dept-nya
   - Admin input physical count
   - System compare physical vs system
   - Auto-create adjustment transaction untuk discrepancy

4. **Fast count support**:
   - Group items by category untuk count efficiency
   - Mobile input (tablet untuk count di production floor)
   - Barcode scan untuk speed up counting

**Business Rules**:
- Stock opname per dept (not full warehouse)
- Production continue di dept lain (only freeze 1 dept)
- [WARNING] Discrepancy > 5% require Manager approval untuk adjustment
- Track stock opname accuracy per dept (KPI untuk admin)

**Business Value**:
- **Production continuity**: Tidak stop ALL production untuk stock opname!
- **Time saving**: -75% time (1 hari → 3-4 jam per dept)
- **Accuracy improvement**: More frequent count = better accuracy
- **Accountability**: Clear ownership per dept untuk stock accuracy

### Current Manual Process (Pain Point):
Sekarang: Stock opname = **Production STOP 1 hari penuh!**
- Semua worker involved untuk counting
- Chaos karena count ALL locations sekaligus
- Result sering tidak akurat (karena terburu-buru)

---

## SUMMARY TABLE: 7 UNIQUE REQUIREMENTS

| # | Requirement | Business Impact | Complexity | Priority |
|---|-------------|-----------------|------------|----------|
| 1 | Dual PO Trigger System | Lead time -29% | HIGH | P0 CRITICAL |
| 2 | Flexible Target per Dept | Shortage -80% | MEDIUM | P0 CRITICAL |
| 3 | 2-Stage Finishing Conversion | Inventory accuracy +27% | MEDIUM | P1 HIGH |
| 4 | Multi-Unit Conversion | Error -90% | LOW | P1 HIGH |
| 5 | Real-Time WIP Tracking | Visibility real-time | MEDIUM | P0 CRITICAL |
| 6 | QC Loop (Rework/Repair) | IKEA compliance ready | MEDIUM | P1 HIGH |
| 7 | Dept-Level Stock Opname | Time -75% | LOW | P2 MEDIUM |

**Implementation Recommendation**:
- **Phase 1** (P0): Requirements #1, #2, #5 (greatest business impact)
- **Phase 2** (P1): Requirements #3, #4, #6 (quality & accuracy)
- **Phase 3** (P2): Requirement #7 (operational efficiency)

---

## FUNCTIONAL REQUIREMENTS (Module-Level)

### Manufacturing Module:
- Bill of Materials (BOM) management dengan multi-level BOM
- Manufacturing Orders dengan customizable workflow states
- Work Orders per dept dengan progress tracking
- Material consumption recording (auto-backflush + manual)
- Production reporting per dept, per MO, per SKU

### Inventory & Warehouse Module:
- Multi-location inventory tracking (3 main WH + 5 dept-level)
- Real-time stock visibility per location
- Internal transfers antar dept dengan approval workflow
- Stock adjustment recording dengan reason tracking
- Stock opname per location (not full warehouse)
- Inventory valuation (FIFO/Average)

### Purchasing Module:
- Purchase Order management dengan multi-approval
- Vendor management dengan performance tracking
- PO tracking: Waiting Approval → Confirmed → Received
- Partial receiving support (PO datang bertahap)
- Integration dengan Manufacturing (PO trigger MO)

### Quality Control Module:
- QC checkpoints configurable per production stage
- QC inspection recording dengan defect taxonomy
- Pass / Rework / Reject workflow
- Rework order management
- Defect tracking & trending report
- Quality KPI dashboard per dept

### Production Planning Module:
- Capacity planning per dept berdasarkan historical data
- Material requirement forecast (MRP)
- Lead time calculation per SKU
- Bottleneck detection & alert
- What-if scenario planning

### Reporting & Analytics Module:
- Real-time dashboard untuk Manager (WIP, bottleneck, defect rate)
- Production KPI tracking (OEE, output vs target, defect %)
- Material consumption analysis (waste tracking)
- Cost analysis per MO (material + labor + overhead)
- Custom reports configurable by user

### User Access Control (RBAC):
- Role-based access: Manager, SPV, Admin, QC, Purchasing, Warehouse
- Permission management per module, per action
- Audit trail untuk critical actions
- 33 concurrent users support

---

## SUCCESS CRITERIA

### Quantitative Metrics:

| Metric | Current (Manual) | Target (After ERP) | Improvement |
|--------|------------------|--------------------|----|
| Material shortage frequency | 8x/bulan | <2x/bulan | **-75%** |
| Production planning time | 5 jam/hari | 2 jam/hari | **-60%** |
| Inventory accuracy | 70-75% | 95%+ | **+25%** |
| Stock opname time | 1 hari (8 jam) | 3-4 jam | **-50%** |
| Admin overtime | 4-5 jam/hari | 2 jam/hari | **-50%** |
| Lead time (avg) | 28 hari | 18-20 hari | **-29%** |
| Defect detection time | End of week | Real-time | **Immediate!** |

### Qualitative Success:

**User Adoption**:
- 80%+ active usage after 3 months (no Excel workaround!)
- Positive feedback dari min 70% users
- Department Leads champion system adoption

**IKEA Compliance**:
- Real-time traceability ready untuk audit
- Defect tracking & trend analysis available
- Material origin & lot tracking complete

**Scalability**:
- System handle 2x production volume tanpa major issue
- Adding new SKU straightforward (< 30 min setup)
- Adding new dept / user straightforward

**ROI**:
- Payback period < 18 bulan dari operational savings
- Measurable reduction dalam waste & overtime cost
- Increased throughput tanpa capital investment

---

## IMPLEMENTATION ASSUMPTIONS

**What We Expect from Odoo**:
- Standard manufacturing modules sebagai foundation
- Customization untuk 7 unique requirements
- Training comprehensive untuk 33 users (mix skill level)
- Data migration support (dari Excel + manual records)
- Post-implementation support (2-3 bulan hyper-care)

**What We Commit**:
- Management support & budget commitment
- Dedicated project team (IT Lead + 3 Dept SPVs)
- User availability untuk training & UAT
- Process documentation untuk knowledge transfer
- Realistic timeline expectation (tidak rush!)

**Critical Success Factors**:
- **Partnership approach**: Collaborative, bukan vendor-client transactional
- **Phased implementation**: Modular approach, not big bang
- **Change management**: Training + adoption program structured
- **Data quality**: Clean master data sebelum go-live
- **Iterative UAT**: Real production scenario testing extensive

---

## NEXT STEPS

**Dari PT Quty Karunia**:
1. Requirements documentation complete
2. Ready untuk discovery workshop (on-site visit recommended)
3. Process walkthrough dengan Dept Leads available
4. Sample data & scenarios untuk PoC discussion

**Dari Odoo (Expected)**:
1. Feasibility assessment: 7 unique requirements doable?
2. Gap analysis: Standard vs Custom breakdown
3. High-level effort estimate untuk each requirement
4. Reference case: Similar manufacturing complexity (jika ada)
5. Proposal: Approach + timeline + team structure

**Timeline Expectation**:
- **Q1 2026** (Now): Discovery & Assessment
- **Q2 2026**: Planning & Design (if proceed)
- **Q3-Q4 2026**: Implementation (phased)
- **Q1 2027**: Go-live & Stabilization

---

**Status**: READY FOR EVALUATION  
**Contact**: Daniel Rizaldy (IT Lead - PT Quty Karunia)  
**Supporting Documents**: 
- REQUIREMENTS_KOMPREHENSIF_PT_QUTY_KARUNIA.md (full details dengan technical specs)
- EXECUTIVE_SUMMARY_SALES_ODOO.md (1-page overview)
- PAIN_POINTS_BUSINESS_IMPACT.md (detailed pain points analysis)
