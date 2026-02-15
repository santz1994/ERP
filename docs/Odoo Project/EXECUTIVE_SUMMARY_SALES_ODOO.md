# EXECUTIVE SUMMARY - PT QUTY KARUNIA
## ERP Requirements untuk Sales Odoo (1-Page Overview)

**Untuk**: Project Director & Business Analyst Odoo  
**Dari**: Daniel Rizaldy (IT Lead - PT Quty Karunia)  
**Tanggal**: 13 Februari 2026  
**Tipe Dokumen**: Executive Summary (Non-Technical)

---

## SIAPA KAMI

**PT Quty Karunia** adalah **manufacturer soft toys** dengan:
- **Main Customer**: IKEA (80% revenue contribution)
- **Production Volume**: 1,000,000-1,500,000 pcs/bulan (1-1.5 juta pieces)
- **Product Range**: 478 SKU aktif (boneka, plushies, mascot)
- **Odoo Users**: 33 admin users (system access HANYA admin level)
- **Location**: Purwakarta, Indonesia

**Business Model**: 
- Make-to-Order (MTO) dengan mix predictable orders + urgent rush orders
- 6-stage production process dengan dual material trigger system
- Quality-critical (IKEA standards) dengan 4 quality checkpoints

---

## MENGAPA BUTUH ERP SEKARANG

### 3 Alasan Kritis:

**1. IKEA Compliance Pressure** 
- IKEA mulai demand **real-time production tracking** 
- Audit trail untuk quality issue → Kami tidak punya!
- Risk: **Kehilangan 80% revenue source** jika tidak comply

**2. Operational Chaos** 
- Excel + WhatsApp + kertas → **Chaos level 9/10**
- Material shortage tiba-tiba (tidak tahu stock real-time)
- Overtime berlebihan karena poor planning

**3. Trauma ERP Sebelumnya (2023 - GAGAL!)** 
- Vendor force-fit system mereka ke workflow kami
- No customization support → Kami forced pakai workaround
- 3 bulan implement → **6 bulan abandon** → Balik ke Excel
- Learning: **ERP HARUS fit business process, bukan sebaliknya!**

---

## 11 PAIN POINTS KRITIS SAAT INI

| # | Pain Point | Business Impact | Urgency |
|---|------------|-----------------|---------|
| 1 | **Material shortage tiba-tiba** | Production stop → OT untuk kejar | CRITICAL |
| 2 | **Tidak tahu WIP real-time** | Planning impossible, chaos daily | CRITICAL |
| 3 | **Quality defect tidak traceable** | Tidak bisa root cause analysis | CRITICAL |
| 4 | **Dual trigger system manual** | Admin overwhelmed, error frequent | CRITICAL |
| 5 | **Excel-based planning** | Error rawan, tidak scalable | HIGH |
| 6 | **Target produksi flat** | Shortage karena tidak hitung defect | HIGH |
| 7 | **Manual material tracking** | 2-3 jam sehari hanya untuk rekap | HIGH |
| 8 | **Stock opname 1 hari penuh** | Produksi stop untuk counting | MEDIUM |
| 9 | **Rework tidak ter-record** | Cost analysis impossible | MEDIUM |
| 10 | **Multi-unit conversion manual** | Error & confusion frequent | MEDIUM |
| 11 | **WhatsApp-based coordination** | Info hilang, tidak traceable | MEDIUM |

---

## APA YANG KAMI BUTUHKAN

### Core Modules:
- **Manufacturing Management** (Production Orders, Work Orders, BOM)  
- **Inventory & Warehouse** (Multi-location, Real-time tracking, Stock Opname)  
- **Purchasing Management** (PO Management, Vendor tracking)  
- **Quality Control** (QC checkpoints, Defect recording, Rework loop)  
- **Production Planning** (Capacity planning, Material forecasting)  
- **Reporting & Analytics** (Real-time dashboards, KPI tracking)  

### 7 Business Requirements UNIK (Perlu Custom):

**1. Dual Purchase Order Trigger System** (MOST COMPLEX!)
- **Business Need**: PO datang 2x (Fabric dulu → Label 2 minggu kemudian)
- **Requirement**: PO #1 unlock dept awal (Cutting, Embroidery), PO #2 unlock ALL dept
- **Why Standard Odoo Tidak Cukup**: MO standard hanya 1 trigger, kami butuh 2 trigger dengan state management

**2. Flexible Production Target per Department**
- **Business Need**: Setiap dept produksi LEBIH banyak dari customer order (untuk cover defect)
- **Requirement**: Auto-calculate target berdasarkan defect rate historis per dept
- **Contoh**: Customer order 500 pcs → Cutting target 520 pcs → Sewing target 510 pcs → dst

**3. 2-Stage Finishing Internal Conversion**
- **Business Need**: Dept Finishing ada 2 sub-process (Stuffing → Closing) TANPA transfer document
- **Requirement**: Track stock intermediate product (Stuffed Body) + auto-consume materials per stage
- **Unique**: Internal process di DALAM 1 dept, bukan antar dept

**4. Multi-Unit Conversion & Auto-Validation**
- **Business Need**: Fabric beli dalam ROLL/YARD, pakai dalam PCS. Filling beli KG, pakai GRAM
- **Requirement**: Auto-convert + validate agar tidak salah unit saat input

**5. Real-Time WIP Tracking System**
- **Business Need**: Harus tahu stock exact di setiap dept real-time (bukan end-of-day)
- **Requirement**: Partial transfer antar dept (not full batch) + real-time dashboard

**6. Quality Control Loop (Rework/Repair)**
- **Business Need**: Defect product bisa di-rework/repair, hasil rework balik ke dept sebelumnya
- **Requirement**: QC reject → Rework workflow → Re-QC → Continue production

**7. Department-Level Warehouse & Stock Opname**
- **Business Need**: Setiap dept produksi punya mini-warehouse sendiri
- **Requirement**: Stock opname per dept (tidak full warehouse), tidak stop produksi dept lain

---

## SUCCESS CRITERIA

Project dianggap **SUCCESS** jika:

**Operational Metrics**:
- Material shortage frequency: **-80%** (8x/bulan → <2x/bulan)
- Production planning time: **-60%** (5 jam → 2 jam)
- Inventory accuracy: **+25%** (70% → 95%+)
- Stock opname time: **-75%** (1 hari → 3-4 jam)
- Admin overtime: **-50%** (4-5 jam/hari → 2 jam/hari)

**Qualitative Success**:
- IKEA compliance: **Real-time traceability** ready for audit
- User Adoption: **80%+ active usage** after 3 months (no Excel workaround!)
- Scalability: System handle **2x volume** tanpa major issue
- ROI: **Payback < 18 bulan** dari operational savings

---

## YANG KAMI HARAPKAN DARI ODOO

### Phase 1: Discovery & Assessment (This Stage!)
- **Validasi Feasibility**: 7 unique requirements kami feasible dengan Odoo?
- **Honest Gap Analysis**: Apa yang bisa standard Odoo vs butuh custom?
- **Complexity Estimate**: High-level effort untuk tiap custom requirement

### Phase 2: Planning (If Proceed)
- Detailed solution design untuk 7 unique requirements
- Implementation roadmap (phased approach recommended)
- Data migration strategy (dari Excel + manual records)

### Phase 3: Implementation (Target Q2 2026)
- Modular implementation (prioritize high-impact requirements)
- Iterative UAT dengan real production scenario
- Comprehensive training (33 users dengan skill range bervariasi)

### Phase 4: Go-Live & Support
- Phased go-live (tidak big bang!)
- Hyper-care period (2-3 bulan)
- Knowledge transfer untuk internal IT team

---

## NEXT STEPS

**Dari PT Quty Karunia**:
- Dokumen requirements comprehensive sudah tersedia (detail 35,000+ words)
- Access ke business process documentation lengkap
- Ready untuk workshop/discovery session dengan tim Odoo
- Team commitment: Management, IT, Department Leads

**Dari Odoo (Yang Kami Harapkan)**:
- Initial assessment: **Feasibility 7 unique requirements**
- Gap analysis: **Standard vs Custom** breakdown
- Case study/reference: **Similar manufacturing complexity** (jika ada)
- Proposal: **High-level approach + timeline + team structure**

---

## CATATAN PENTING

**Yang PERLU Diingat**:
- **Jangan force-fit standard process ke kami** (trauma ERP lama!)
- **Business process kami proven** (IKEA compliant 7+ tahun)
- **Partnership approach**: Kami respek expertise Odoo, Odoo respek workflow kami
- **Ready untuk feedback**: Jika ada alternative approach yang lebih efficient, kami open!

**Dokumen Pendukung**:
1. **REQUIREMENTS_KOMPREHENSIF_PT_QUTY_KARUNIA.md** (35,000+ words - FULL DETAILS)
2. **BUSINESS_REQUIREMENTS_ONLY.md** (Non-technical business needs)
3. **PAIN_POINTS_BUSINESS_IMPACT.md** (11 pain points dengan cost analysis)
4. **NewREQOdoo.md** (Technical requirements & architecture)

---

## CONTACT

**Daniel Rizaldy**  
IT Lead - PT Quty Karunia  
Email: [Email contact]  
Phone: [Phone contact]

**Ready untuk:**
- Discovery workshop (on-site recommended)
- Process walkthrough (production floor observation)
- Q&A session dengan Department Leads
- Pilot/PoC discussion

---

**Status Dokumen**: READY FOR REVIEW  
**Target Response**: Feasibility assessment + Gap analysis outline  
**Timeline Expectation**: Q2 2026 implementation start (jika proceed)

