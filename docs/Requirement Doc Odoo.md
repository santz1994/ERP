# 🏭 ODOO 18 IMPLEMENTATION - REQUIREMENTS DOCUMENT
## PT Quty Karunia (Soft Toys Manufacturing - IKEA Supplier)

**Document Type**: Comprehensive Requirements & Technical Specification  
**Target Platform**: Odoo 18 (Community/Enterprise)  
**Industry**: Discrete Manufacturing - Soft Toys (B2B)  
**Company**: PT Quty Karunia  
**Main Customer**: IKEA (80% revenue)  
**Production Volume**: 50,000 - 80,000 pcs/month  
**Prepared By**: Daniel Rizaldy S.W. (IT Lead)  
**Date**: 13 Februari 2026  
**Status**: ✅ READY FOR ODOO PARTNER EVALUATION  
**Context**: Custom Manufacturing Workflow (Dual Trigger System)

---

## 📑 DOCUMENT STRUCTURE

### PART A: EXECUTIVE SUMMARY
1. [Company Profile & Business Context](#section-1)
2. [Project Objectives & Success Criteria](#section-2)
3. [Current Pain Points Analysis](#section-3)

### PART B: BUSINESS REQUIREMENTS
4. [Production Workflow Complete](#section-4)
5. [Organizational Structure & Roles](#section-5)
6. [Critical Custom Features (Must-Have)](#section-6)
7. [BOM & Manufacturing Logic](#section-7)
8. [Inventory & Warehouse Management](#section-8)

### PART C: TECHNICAL REQUIREMENTS
9. [Architecture & Technology Stack](#section-9)
10. [Database Schema Overview](#section-10)
11. [Integration Requirements](#section-11)
12. [Mobile Applications](#section-12)
13. [Reporting & Analytics](#section-13)

### PART D: ODOO-SPECIFIC REQUIREMENTS
14. [Odoo Modules Mapping](#section-14)
15. [Customization Requirements](#section-15)
16. [Gap Analysis: Odoo Standard vs Requirements](#section-16)
17. [Implementation Roadmap](#section-17)
18. [Success Metrics & KPI](#section-18)

### APPENDIX
- [Glossary](#glossary)
- [References](#references)
- [Contact Information](#contact)

---

<a name="section-1"></a>
## 1️⃣ COMPANY PROFILE & BUSINESS CONTEXT

### Industry Overview

**Sector**: Soft Toys Manufacturing (Discrete Manufacturing)  
**Business Model**: B2B - Make-to-Order (MTO) + Partial Make-to-Stock (MTS)  
**Main Customer**: IKEA Sweden (80% revenue contribution)  
**Other Customers**: IKEA Belgium, IKEA USA, Other retailers  
**Production Volume**: 50,000 - 80,000 pieces/month  
**Product Range**: 478 SKU (Soft toys - Boneka, Bantal, dll)  
**Product Complexity**: HIGH - 30+ material SKU per artikel  

### Business Characteristics

| Aspect | Details |
|--------|---------|
| **Manufacturing Type** | Discrete Manufacturing dengan Complex Assembly |
| **Production Process** | 6-Stage Sequential: Cutting → Embroidery (Optional) → Sewing → Finishing (2-stage: Stuffing & Closing) → Packing |
| **Lead Time** | 15-25 days (from PO to Ship) |
| **Order Pattern** | Weekly delivery schedule (Week-based planning: W01-2026, W02-2026, etc.) |
| **Destination** | Multi-country (Belgium, Sweden, USA, China, dll) |
| **Inventory Strategy** | JIT untuk Label, Min/Max untuk Fabric & Filling |
| **Quality Standard** | IKEA Compliance (STRICT - 95%+ OTD required) |

### Unique Industry Characteristics (Critical for Odoo Implementation)

**⚠️ IMPORTANT**: Soft Toys Manufacturing memiliki karakteristik SANGAT SPESIFIK yang berbeda dari manufacture standar:

1. **🔥 Dual Component Production**:
   - 1 Finished Good = **2 parallel items** (Boneka Body + Baju)
   - Body & Baju diproduksi **terpisah** sejak Cutting
   - Assembly hanya terjadi di **Packing stage**
   - **Impact Odoo**: Memerlukan custom BOM structure & routing logic

2. **🔥 Complex Material Mix dengan Multi-UOM**:
   - 9-12 jenis fabric per artikel (YARD)
   - 3-5 jenis thread (CM/METER)
   - Filling/Kapas (GRAM/KG)
   - Label & accessories (PCS)
   - Carton (PCS dengan conversion factor: 60 pcs/carton)
   - **Impact Odoo**: Auto-conversion & validation kritis untuk inventory accuracy

3. **🔥 2-Stage Finishing Process**:
   - Stage 1: **Stuffing** (Skin → Stuffed Body menggunakan filling/kapas)
   - Stage 2: **Closing** (Stuffed Body → Finished Doll dengan hand-stitching)
   - **Internal warehouse conversion** tanpa surat jalan formal
   - **Impact Odoo**: Memerlukan custom WIP tracking & internal transfer logic

4. **🔥 Label-Driven Production (Dual Trigger System)**:
   - **PO Kain** (Fabric) → Trigger 1: Cutting & Embroidery dapat START
   - **PO Label** (Label) → Trigger 2: Full production RELEASED (Sewing, Finishing, Packing dapat start)
   - Label berisi **Week & Destination** info yang CRITICAL
   - Week & Destination harus **LOCKED** setelah PO Label approved (tidak bisa diedit manual)
   - **Impact Odoo**: Memerlukan custom MO workflow & state management

5. **🔥 Embroidery Optional Routing**:
   - Tidak semua artikel butuh embroidery (contoh: AFTONSPARV butuh, tapi BLÅHAJ tidak butuh)
   - Routing mempengaruhi **SPK generation** (Route 1: with embroidery, Route 2: without)
   - **Impact Odoo**: Memerlukan flexible routing configuration per artikel

6. **🔥 Flexible Target System per Departemen**:
   - SPK Target dapat **berbeda** dari MO Target (buffer allocation)
   - Cutting: +10% buffer (antisipasi waste)
   - Sewing: +15% buffer (highest defect rate)
   - Finishing: +3% buffer (high yield)
   - Packing: Exact match (urgency-based)
   - **Impact Odoo**: Memerlukan custom SPK logic & smart buffer calculation

---

<a name="section-2"></a>
## 2️⃣ PROJECT OBJECTIVES & SUCCESS CRITERIA

### Project Objectives

**Primary Objective**:
Implementasi Odoo 18 ERP System untuk menggantikan proses manual dan spreadsheet yang terfragmentasi, dengan fokus pada:

1. **Single Source of Truth**: Integrasi total Purchasing, Production, Warehouse, dan Accounting dalam satu database terpusat
2. **Audit Ready (5W1H)**: Traceability penuh dari Raw Material Batch sampai Finished Goods Serial Number
3. **Loss Reduction**: Mengontrol Fabric Yield (Susut Kain) dan memantau Cost of Poor Quality (Biaya Rework/Reject)
4. **Real-Time Visibility**: Dashboard real-time untuk PPIC, Management, dan Department heads
5. **Automation**: Eliminasi manual data entry dan reduce human error dari 20% → <2%

### Success Criteria

| No | Metric | Current (Before ERP) | Target (After Odoo) | Measurement |
|----|--------|----------------------|---------------------|-------------|
| 1 | **Lead Time** | 25 days | 18 days (-28%) | Days from PO to shipment |
| 2 | **On-Time Delivery (OTD)** | 75% | 95%+ | % orders delivered on target week |
| 3 | **Inventory Accuracy** | 82% | 98%+ | Physical count vs system |
| 4 | **Fabric Yield** | 85% (15% waste) | 92% (8% waste) | Good output vs material consumed |
| 5 | **Reporting Time** | 3-5 days (manual) | 5 seconds (1 click) | Time to generate monthly report |
| 6 | **Cost of Poor Quality (COPQ)** | $35,000/year | $12,000/year (-66%) | Rework + scrap costs |
| 7 | **Material Shortage Incidents** | 8-12 times/month | <3 times/month | Production stop due to material out |
| 8 | **Manual Data Entry Time** | 15 hours/week | 2 hours/week (-87%) | Admin time for data input |
| 9 | **Inventory Discrepancy Loss** | $35,000/year | $8,000/year (-77%) | Unaccounted material loss |
| 10 | **Decision Making Speed** | 3-5 days (wait report) | Real-time (dashboard) | Management response time |

**ROI Target**: 18-24 months (break-even after implementation cost)

---

<a name="section-3"></a>
## 3️⃣ CURRENT PAIN POINTS ANALYSIS

### Historical Problems (Before ERP Initiative)

| No | Problem Category | Pain Point Detail | Business Impact | Frequency | Severity | Expected Odoo Solution |
|----|------------------|-------------------|-----------------|-----------|----------|------------------------|
| 1 | **Data Produksi Manual** | Input via Excel/Kertas, compile manual | • Laporan lambat 3-5 hari<br>• Sering salah hitung (±10%)<br>• Sulit lacak progres real-time | Daily | 🔴 HIGH | Auto-Generate MO/SPK berdasarkan Trigger PO. Real-time dashboard dengan barcode scanning. |
| 2 | **Material Tidak Terdata** | Stok tidak tercatat saat pengambilan | • Tiba-tiba material habis<br>• Produksi terhambat<br>• Pembelian mendadak (harga mahal) | Weekly | 🔴 CRITICAL | Barcode Scanning pada setiap Internal Transfer. Real-time stock alert dengan reorder point automation. |
| 3 | **SPK Tidak Terpantau** | Tidak ada sistem tracking progress SPK | • Tidak tahu SPK mana yang terlambat<br>• PPIC kesulitan koordinasi<br>• Delay baru ketahuan saat deadline | Daily | 🔴 HIGH | Work Order tracking dengan Kanban view & automatic notification untuk delay. |
| 4 | **FinishGood Sulit Verifikasi** | Hitung manual box & pieces | • Hitung manual (lama & error prone)<br>• Salah hitung jumlah box<br>• Customer komplain receiving | Per shipment | 🟠 MEDIUM | Barcode scanning + auto-calculation Carton→Pieces dengan UOM conversion validation. |
| 5 | **Approval Tidak Jelas** | Tidak ada audit trail | • Tidak tahu siapa yang sudah approve<br>• Perubahan SPK tanpa kontrol<br>• Accountability hilang | Per change | 🟠 MEDIUM | Multi-level approval workflow dengan audit log (auto-record who/when/what). |
| 6 | **Laporan Bulanan Lambat** | Compile manual dari berbagai Excel | • Butuh 3-5 hari untuk compile<br>• Data sudah telat saat selesai<br>• Decision making terlambat | Monthly | 🟡 LOW | Real-time reporting & dashboard. 1-click export to Excel/PDF. |
| 7 | **Finishing Process Tidak Terstruktur** | Stuffing & Closing campur aduk | • Stuffing & Closing campur aduk<br>• Sulit track konsumsi kapas<br>• Stok Skin vs Stuffed Body tidak jelas | Daily | 🔴 HIGH | 2-stage Finishing tracking dengan separate WIP inventory per stage. Auto-track material consumption (filling/kapas). |
| 8 | **UOM Conversion Manual Rawan Error** | Konversi manual Yard→Pcs, Box→Pcs | • Cutting: Yard → Pcs salah hitung<br>• FG Receiving: Box → Pcs tidak konsisten<br>• Inventory kacau karena konversi salah | Per transaction | 🔴 CRITICAL | Auto-conversion dengan BOM marker. Real-time validation: Warning >10% variance, Block >15% variance. |
| 9 | **Target Produksi Kaku (Rigid)** | SPK = MO Target (tidak ada buffer) | • SPK harus sama dengan MO Target<br>• Tidak ada buffer untuk antisipasi reject<br>• Sering shortage karena defect tidak diprediksi<br>• Delay shipping karena kekurangan qty | Weekly | 🟠 MEDIUM | Flexible Target System per Department dengan smart buffer allocation (+10% to +15% by dept risk level). |
| 10 | **Defect Tidak Tertrack** | Tidak ada sistem rework & QC tracking | • Waste tinggi, root cause tidak jelas<br>• COPQ (Cost of Poor Quality) tidak terukur<br>• Rework tidak terorganisir | Daily | 🟠 MEDIUM | Rework/Repair Module dengan QC Integration. Auto-capture defects, workflow: Defect → QC Inspection → Rework → Re-QC → Approve. |
| 11 | **Purchasing Coordination Complex** | 3 PO types (Fabric, Label, Accessories) tidak linked | • PO Kain dan PO Label terpisah<br>• Ketidakjelasan jadwal produksi<br>• Week & Destination sering salah | Per order | 🔴 HIGH | **Dual Trigger System**: PO Kain (Trigger 1: Early Start). PO Label (Trigger 2: Full Release + Auto Week/Destination inheritance - LOCKED). |
| 12 | **Reporting COGS & WIP Lambat** | Manual calculation end of month | • Laporan COGS dan WIP lambat (akhir bulan)<br>• Decision making terlambat<br>• Cost variance baru ketahuan setelah 1 bulan | Monthly | 🟡 LOW | Real-time Valuation untuk WIP dan Finished Goods. Auto-calculation per SPK completion. |

### Financial Impact Quantification

**Annual Loss Before ERP** (estimated):
- Material waste karena shortage: **$120,000**
- Delay penalty dari IKEA: **$80,000**
- Manual data entry cost (opportunity cost): **$45,000**
- Inventory discrepancy loss: **$35,000**
- Rework/reject tidak tertrack: **$60,000**
- **Total Estimated Annual Loss**: **$340,000/year**

**Expected Savings After Odoo Implementation**:
- Material waste reduction (-60%): **$72,000/year savings**
- Delay penalty reduction (-80%): **$64,000/year savings**
- Manual work reduction (-87%): **$39,000/year savings**
- Inventory accuracy improvement: **$27,000/year savings**
- COPQ tracking & reduction (-66%): **$40,000/year savings**
- **Total Expected Annual Savings**: **$242,000/year**

---

<a name="section-4"></a>
## 4️⃣ PRODUCTION WORKFLOW COMPLETE
3. CORE BUSINESS LOGIC (The "Must-Have" Customizations)
Bagian ini adalah CRITICAL PATH. Module Odoo standar tidak mengakomodasi alur ini. Kami membutuhkan Partner untuk mengimplementasikan logika berikut:
### Organizational Chart

```
┌────────────────────────────────────────────────────────────────────┐
│                    PT QUTY KARUNIA - ORG STRUCTURE                  │
└────────────────────────────────────────────────────────────────────┘

                        [DIRECTOR]
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    [FINANCE]            [MANAGER]            [IT LEAD]
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   [PURCHASING]           [PPIC]            [PRODUCTION]
   (3 Specialist)      (1 Manager)         (5 Departments)
        │                    │                    │
        ├─ Fabric            │                    ├─ Cutting (SPV + 15 Operator)
        ├─ Label             │                    ├─ Embroidery (SPV + 8 Operator)
        └─ Accessories       │                    ├─ Sewing (SPV + 35 Operator)
                             │                    ├─ Finishing (SPV + 20 Operator)
                             │                    └─ Packing (SPV + 12 Operator)
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   [WAREHOUSE]            [QC]              [ADMIN/DATA ENTRY]
   (3 Staff)           (2 Inspector)         (3 Staff)
```

### User Roles & Odoo Access Requirements

| Role | User Count | Odoo Module Access | Critical Features Required |
|------|------------|-------------------|----------------------------|
| **Director** | 1 | All (Read-only for most) | • Dashboard (all KPI)<br>• Financial reports<br>• Approval (high-value PO, MO changes) |
| **Manager** | 1 | Manufacturing, Inventory, Purchasing, Sales | • MO approval<br>• SPK monitoring dashboard<br>• Performance analytics<br>• Exception management |
| **Finance** | 2 | Accounting, Invoicing, Reports | • COGS calculation<br>• WIP valuation<br>• Vendor payment<br>• Cost analysis |
| **IT Lead** | 1 | Settings, Users, Technical | • User management<br>• System configuration<br>• Custom module development |
| **Purchasing A (Fabric)** | 1 | Purchase, Inventory | • Create PO Kain<br>• **Trigger MO (PARTIAL)**<br>• Vendor management<br>• Material forecast |
| **Purchasing B (Label)** | 1 | Purchase, Inventory | • Create PO Label<br>• **Upgrade MO to RELEASED**<br>• Week & Destination input (LOCKED after approve)<br>• Vendor management |
| **Purchasing C (Accessories)** | 1 | Purchase, Inventory | • Create PO Accessories<br>• Stock monitoring<br>• Vendor management |
| **PPIC** | 2 | Manufacturing, MRP, Planning | • **Review & Accept/Reject MO** (NOT CREATE!)<br>• Monitor SPK progress<br>• Material requirement planning<br>• Production scheduling<br>• Capacity planning |
| **Warehouse Staff** | 3 | Inventory, Barcode | • Receive goods (PO)<br>• Internal transfer (WIP)<br>• Issue materials to production<br>• Stock adjustment<br>• **Barcode scanning** |
| **QC Inspector** | 2 | Quality, Manufacturing | • Quality checkpoints<br>• Defect categorization<br>• Rework approval/rejection<br>• Final inspection before FG |
| **Production SPV** | 5 | Manufacturing (Work Orders) | • View SPK (their dept only)<br>• Input daily production<br>• Report defects<br>• Request materials<br>• **Tablet/Kiosk mode** |
| **Production Operator** | 90 | Manufacturing (Limited) | • Input work completion<br>• Report defects<br>• **Barcode scanning** (material consumption) |
| **Admin/Data Entry** | 3 | All (Data Entry) | • Master data maintenance<br>• Daily production input<br>• Report generation<br>• Data verification |

**Total Users**: ~111 concurrent users

---

<a name="section-6"></a>
## 6️⃣ CRITICAL CUSTOM FEATURES (Must-Have for Odoo 18)

### ⚠️ DISCLAIMER: These features are NOT available in Odoo Standard!

Berikut adalah **10 Killer Features** yang HARUS di-customakan dalam Odoo 18. Fitur-fitur ini adalah **CORE BUSINESS LOGIC** PT Quty Karunia dan **TIDAK BISA KOMPROMI**.

---

### 🔥 FEATURE 1: Dual Trigger Production System

**Problem**: 
- Odoo standard: MO triggered from Sales Order (single trigger)
- Quty needs: MO triggered by **2 separate PO** (Fabric PO + Label PO)
- Label PO selalu lebih lama (7-10 days vs 3-5 days untuk Fabric)

**Solution Required**:

```python
# Custom State Machine for MO
class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('partial', 'Partial (Fabric Ready)'),  # NEW STATE
        ('released', 'Released (Label Ready)'),  # EXTENDED STATE
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ])
    
    # Link to PO
    po_fabric_id = fields.Many2one('purchase.order', 'PO Fabric (Trigger 1)')
    po_label_id = fields.Many2one('purchase.order', 'PO Label (Trigger 2)')
    
    # Week & Destination (from PO Label)
    production_week = fields.Char('Week', readonly=True)  # AUTO from PO Label
    destination_country = fields.Char('Destination', readonly=True)  # AUTO from PO Label
    
    def action_trigger_from_po_fabric(self):
        """Trigger 1: PO Fabric received"""
        self.state = 'partial'
        # Generate Work Orders for: Cutting, Embroidery (optional)
        self._generate_work_orders_early_stage()
        
    def action_trigger_from_po_label(self):
        """Trigger 2: PO Label received"""
        self.state = 'released'
        # Inherit Week & Destination from PO Label (LOCKED!)
        self.production_week = self.po_label_id.production_week
        self.destination_country = self.po_label_id.destination_country
        # Generate remaining Work Orders: Sewing, Finishing, Packing
        self._generate_work_orders_full()
```

**Odoo Module to Customize**: `mrp` (Manufacturing)

**Complexity**: 🔴 CRITICAL - Heavy customization of MO workflow

---

### 🔥 FEATURE 2: Flexible Target System per Departemen

**Problem**:
- Odoo standard: Work Order qty = MO qty (rigid, no buffer)
- Quty needs: Different target per department with smart buffer

**Business Logic**:
- Cutting: MO Target + 10% (waste buffer)
- Sewing: Cutting Good Output + 15% (defect buffer)
- Finishing: Sewing Good Output + 3% (minor buffer)
- Packing: Exact match to MO Target (no buffer)

**Solution Required**:

```python
class WorkOrder(models.Model):
    _inherit = 'mrp.workorder'
    
    target_qty = fields.Float('Target Quantity')  # Can differ from MO qty!
    good_qty = fields.Float('Good Output', compute='_compute_good_qty')
    defect_qty = fields.Float('Defect Quantity')
    buffer_percentage = fields.Float('Buffer %', related='workcenter_id.default_buffer_pct')
    
    @api.depends('qty_producing', 'defect_qty')
    def _compute_good_qty(self):
        for wo in self:
            wo.good_qty = wo.qty_producing - wo.defect_qty
    
    def _compute_target_with_buffer(self):
        """Auto-calculate target based on previous WO output + buffer"""
        if self.workcenter_id.code == 'CUTTING':
            self.target_qty = self.production_id.product_qty * (1 + self.buffer_percentage/100)
        elif self.workcenter_id.code == 'SEWING':
            prev_wo = self._get_previous_wo('CUTTING')
            self.target_qty = prev_wo.good_qty * (1 + self.buffer_percentage/100)
        # ... and so on
    
    @api.constrains('target_qty')
    def _check_target_constraint(self):
        """Validation: Target dept ≤ Good Output dept sebelumnya"""
        prev_wo = self._get_previous_wo()
        if prev_wo and self.target_qty > prev_wo.good_qty:
            raise ValidationError(
                f"Target {self.target_qty} cannot exceed previous WO good output {prev_wo.good_qty}"
            )
```

**Odoo Module to Customize**: `mrp` (Work Orders)

**Complexity**: 🔴 HIGH - Complex inter-WO dependency logic

---

### 🔥 FEATURE 3: Dual-BOM System (Production vs Purchasing)

**Problem**:
- Odoo standard: 1 BOM per product
- Quty needs: 2 BOM types for different purposes
  - **BOM Production**: Step-by-step per department (includes WIP components)
  - **BOM Purchasing**: Aggregated RAW materials only (excludes WIP)

**Why 2 BOMs**:
- Purchasing tidak perlu tahu "WIP_CUTTING", "WIP_SKIN", dll (bingung: beli dimana?)
- PPIC perlu tahu routing detail per department
- Material calculation untuk PO harus aggregate RAW materials only

**Solution Required**:

```python
class BillOfMaterials(models.Model):
    _inherit = 'mrp.bom'
    
    bom_type_custom = fields.Selection([
        ('production', 'BOM Production'),  # For PPIC/Production
        ('purchasing', 'BOM Purchasing'),  # For Purchasing Dept
    ], string='BOM Type (Custom)', required=True)
    
    # Auto-sync: BOM Purchasing generated from BOM Production
    source_production_bom_id = fields.Many2one('mrp.bom', 'Source Production BOM')
    
    def action_generate_purchasing_bom(self):
        """Auto-generate BOM Purchasing from BOM Production"""
        if self.bom_type_custom != 'production':
            return
        
        # Aggregate all RAW materials (exclude WIP)
        raw_materials = {}
        for line in self.bom_line_ids:
            self._aggregate_materials_recursive(line, raw_materials)
        
        # Create BOM Purchasing
        purchasing_bom = self.create({
            'product_tmpl_id': self.product_tmpl_id.id,
            'bom_type_custom': 'purchasing',
            'source_production_bom_id': self.id,
        })
        
        # Create lines (RAW materials only)
        for material, qty in raw_materials.items():
            if material.type == 'product':  # Exclude WIP (type='consu')
                self.env['mrp.bom.line'].create({
                    'bom_id': purchasing_bom.id,
                    'product_id': material.id,
                    'product_qty': qty,
                })
    
    def _aggregate_materials_recursive(self, line, aggregator):
        """Recursive aggregation to get final RAW materials"""
        if line.product_id.type == 'product':
            # This is RAW material
            if line.product_id in aggregator:
                aggregator[line.product_id] += line.product_qty
            else:
                aggregator[line.product_id] = line.product_qty
        elif line.product_id.bom_ids:
            # This is WIP, explode further
            for sub_line in line.product_id.bom_ids[0].bom_line_ids:
                self._aggregate_materials_recursive(sub_line, aggregator)
```

**Odoo Module to Customize**: `mrp` (BOM)

**Complexity**: 🔴 CRITICAL - Major BOM structure change

---

### 🔥 FEATURE 4: Warehouse Finishing 2-Stage (Internal Conversion)

**Problem**:
- Odoo standard: Stock move antar location perlu Delivery Order
- Quty needs: Internal conversion tanpa surat jalan formal
  - Stage 1 (Stuffing): Skin → Stuffed Body (consume filling)
  - Stage 2 (Closing): Stuffed Body → Finished Doll

**Solution Required**:

```python
class FinishingStageConversion(models.Model):
    _name = 'finishing.conversion'
    _description = 'Finishing 2-Stage Internal Conversion'
    
    name = fields.Char('Reference', required=True)
    workorder_id = fields.Many2one('mrp.workorder', 'Related Work Order')
    stage = fields.Selection([
        ('stuffing', 'Stage 1: Stuffing'),
        ('closing', 'Stage 2: Closing'),
    ], required=True)
    
    # Input
    input_product_id = fields.Many2one('product.product', 'Input Product')
    input_qty = fields.Float('Input Quantity')
    input_location_id = fields.Many2one('stock.location', 'Input Location')
    
    # Material Consumption
    material_ids = fields.One2many('finishing.conversion.material', 'conversion_id', 'Materials Used')
    
    # Output
    output_product_id = fields.Many2one('product.product', 'Output Product')
    good_qty = fields.Float('Good Output')
    defect_qty = fields.Float('Defect Quantity')
    output_location_id = fields.Many2one('stock.location', 'Output Location')
    
    def action_process_conversion(self):
        """Process internal conversion without delivery order"""
        # 1. Deduct input product from input location
        self.env['stock.quant']._update_available_quantity(
            self.input_product_id,
            self.input_location_id,
            -self.input_qty,
        )
        
        # 2. Consume materials (filling, thread)
        for material_line in self.material_ids:
            self.env['stock.quant']._update_available_quantity(
                material_line.product_id,
                material_line.location_id,
                -material_line.qty_used,
            )
        
        # 3. Add output product to output location
        self.env['stock.quant']._update_available_quantity(
            self.output_product_id,
            self.output_location_id,
            self.good_qty,
        )
        
        # 4. Track in WIP valuation
        self._update_wip_valuation()

class FinishingConversionMaterial(models.Model):
    _name = 'finishing.conversion.material'
    
    conversion_id = fields.Many2one('finishing.conversion', 'Conversion')
    product_id = fields.Many2one('product.product', 'Material')
    qty_planned = fields.Float('Planned Qty')
    qty_used = fields.Float('Actual Qty Used')
    variance_pct = fields.Float('Variance %', compute='_compute_variance')
    location_id = fields.Many2one('stock.location', 'Source Location')
    
    @api.depends('qty_planned', 'qty_used')
    def _compute_variance(self):
        for line in self:
            if line.qty_planned:
                line.variance_pct = ((line.qty_used - line.qty_planned) / line.qty_planned) * 100
```

**Odoo Module to Customize**: `stock`, `mrp`

**Complexity**: 🟠 HIGH - Custom inventory movement logic

---

### 🔥 FEATURE 5: UOM Conversion Auto-Validation

**Problem**:
- Manual conversion error: Yard → Pcs (Cutting), Box → Pcs (FG Receiving)
- Result: Inventory chaos, stock discrepancy

**Solution Required**:

```python
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    uom_conversion_validation = fields.Boolean('Enable UOM Validation', default=True)
    expected_conversion_qty = fields.Float('Expected Qty (from BOM)')
    actual_input_qty = fields.Float('Actual Input Qty')
    conversion_variance_pct = fields.Float('Variance %', compute='_compute_conversion_variance')
    
    @api.depends('expected_conversion_qty', 'product_uom_qty')
    def _compute_conversion_variance(self):
        for move in self:
            if move.expected_conversion_qty:
                variance = abs((move.product_uom_qty - move.expected_conversion_qty) / move.expected_conversion_qty) * 100
                move.conversion_variance_pct = variance
    
    @api.constrains('conversion_variance_pct')
    def _validate_uom_conversion(self):
        for move in self:
            if not move.uom_conversion_validation:
                continue
            
            variance = move.conversion_variance_pct
            
            if variance > 15:
                # BLOCK transaction
                raise ValidationError(
                    f"UOM Conversion ERROR! Variance {variance:.1f}% exceeds 15% limit.\n"
                    f"Expected: {move.expected_conversion_qty} {move.product_uom.name}\n"
                    f"Actual: {move.product_uom_qty} {move.product_uom.name}\n"
                    f"Please verify your input!"
                )
            elif variance > 10:
                # WARNING (allow but alert)
                return {
                    'warning': {
                        'title': 'UOM Conversion Warning',
                        'message': f"Variance {variance:.1f}% exceeds 10%. Please double-check your input."
                    }
                }
    
    def _compute_expected_from_bom(self):
        """Calculate expected qty based on BOM marker/conversion factor"""
        if self.raw_material_workorder_id:  # This is for Cutting
            wo = self.raw_material_workorder_id
            bom_line = wo.bom_id.bom_line_ids.filtered(lambda l: l.product_id == self.product_id)
            
            if bom_line and bom_line.product_uom.id != self.product_uom.id:
                # Conversion needed (e.g. YARD → PCS)
                marker = bom_line.product_qty  # e.g. 0.1466 YARD per 1 PCS
                target_pcs = wo.target_qty
                
                self.expected_conversion_qty = target_pcs * marker
                self.actual_input_qty = self.product_uom_qty
```

**Odoo Module to Customize**: `stock`, `mrp`

**Complexity**: 🟠 MEDIUM - Validation logic on stock moves

---

### 🔥 FEATURE 6: Rework/Repair Module (QC Integration)

**Problem**:
- Defect tidak ter-track, waste tinggi
- Rework tidak terorganisir, COPQ tidak terukur

**Solution Required**:

**(Sudah ada di current prototype, perlu di-port ke Odoo)**

```python
class QualityDefect(models.Model):
    _name = 'quality.defect'
    _description = 'Quality Defect Tracking'
    
    name = fields.Char('Defect Reference')
    workorder_id = fields.Many2one('mrp.workorder', 'Work Order')
    defect_qty = fields.Float('Defect Quantity')
    defect_category_id = fields.Many2one('quality.defect.category', 'Defect Type')
    severity = fields.Selection([
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ])
    
    # Rework tracking
    rework_request_id = fields.Many2one('quality.rework.request', 'Rework Request')
    state = fields.Selection([
        ('detected', 'Detected'),
        ('rework_requested', 'Rework Requested'),
        ('rework_approved', 'Approved by QC'),
        ('rework_in_progress', 'Reworking'),
        ('rework_completed', 'Rework Done'),
        ('verified', 'QC Verified'),
        ('scrapped', 'Scrapped'),
    ])
    
class QualityReworkRequest(models.Model):
    _name = 'quality.rework.request'
    _description = 'Rework Request'
    
    name = fields.Char('Rework Reference')
    defect_id = fields.Many2one('quality.defect', 'Related Defect')
    workorder_id = fields.Many2one('mrp.workorder', 'Original Work Order')
    
    # QC Approval
    qc_inspector_id = fields.Many2one('res.users', 'QC Inspector')
    qc_approved = fields.Boolean('QC Approved')
    qc_notes = fields.Text('QC Notes')
    
    # Rework execution
    rework_operator_id = fields.Many2one('res.users', 'Rework Operator')
    rework_started_at = fields.Datetime('Rework Started')
    rework_completed_at = fields.Datetime('Rework Completed')
    
    # Result
    recovered_qty = fields.Float('Recovered Good Qty')
    still_defect_qty = fields.Float('Still Defect (Scrap)')
    recovery_rate = fields.Float('Recovery %', compute='_compute_recovery_rate')
    
    # Cost tracking (COPQ)
    material_cost = fields.Float('Material Cost')
    labor_cost = fields.Float('Labor Cost')
    total_rework_cost = fields.Float('Total Rework Cost')
    
    @api.depends('defect_id.defect_qty', 'recovered_qty')
    def _compute_recovery_rate(self):
        for rework in self:
            if rework.defect_id.defect_qty:
                rework.recovery_rate = (rework.recovered_qty / rework.defect_id.defect_qty) * 100
    
    def action_approve_rework(self):
        """QC approve rework request"""
        self.qc_approved = True
        self.defect_id.state = 'rework_approved'
        # Create rework work order
        self._create_rework_workorder()
```

**Odoo Module to Customize**: `quality`, `mrp`

**Complexity**: 🟠 MEDIUM - New module integration

---

### 🔥 FEATURE 7: Week & Destination Auto-Inheritance (LOCKED)

**Problem**:
- Manual input Week/Destination → error prone
- Sering salah input, customer complaint

**Solution Required**:

```python
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    po_type_custom = fields.Selection([
        ('fabric', 'PO Fabric'),
        ('label', 'PO Label'),
        ('accessories', 'PO Accessories'),
    ], 'PO Type (Custom)')
    
    # For PO Label only
    production_week = fields.Char('Production Week')  # Format: W05-2026
    destination_country = fields.Char('Destination Country')  # Belgium, Sweden, etc.
    
    @api.constrains('production_week', 'destination_country')
    def _validate_week_destination(self):
        if self.po_type_custom == 'label':
            if not self.production_week or not self.destination_country:
                raise ValidationError("PO Label must have Week and Destination!")

class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'
    
    production_week = fields.Char('Week', readonly=True)  # From PO Label
    destination_country = fields.Char('Destination', readonly=True)  # From PO Label
    week_destination_locked = fields.Boolean('Week/Dest Locked', default=False)
    
    def action_inherit_week_destination_from_po_label(self):
        """Auto-inherit from PO Label when MO upgraded to RELEASED"""
        if self.po_label_id:
            self.write({
                'production_week': self.po_label_id.production_week,
                'destination_country': self.po_label_id.destination_country,
                'week_destination_locked': True,
            })
    
    @api.constrains('production_week', 'destination_country')
    def _prevent_manual_edit_week_destination(self):
        if self.week_destination_locked:
            # Check if trying to modify
            if self._origin.production_week != self.production_week or \
               self._origin.destination_country != self.destination_country:
                raise ValidationError(
                    "Week and Destination are LOCKED! Cannot edit manually.\n"
                    "These fields are auto-inherited from PO Label and cannot be changed."
                )
```

**Odoo Module to Customize**: `purchase`, `mrp`

**Complexity**: 🟡 MEDIUM - Field locking logic

---

### 🔥 FEATURE 8: Material Debt System (Negative Stock dengan Approval)

**Problem**:
- Produksi harus jalan meskipun material belum datang
- Tapi harus ada kontrol ketat (tidak sembarangan negative stock)

**Solution Required**:

```python
class MaterialDebt(models.Model):
    _name = 'material.debt'
    _description = 'Material Debt (Approved Negative Stock)'
    
    name = fields.Char('Debt Reference')
    workorder_id = fields.Many2one('mrp.workorder', 'Work Order')
    product_id = fields.Many2one('product.product', 'Material')
    debt_qty = fields.Float('Debt Quantity (Negative)')
    uom_id = fields.Many2one('uom.uom', 'UoM')
    
    # Approval
    state = fields.Selection([
        ('requested', 'Requested'),
        ('approved_spv', 'Approved by SPV'),
        ('approved_manager', 'Approved by Manager'),
        ('cleared', 'Debt Cleared'),
        ('rejected', 'Rejected'),
    ])
    requested_by_id = fields.Many2one('res.users', 'Requested By')
    approved_by_spv_id = fields.Many2one('res.users', 'Approved by SPV')
    approved_by_manager_id = fields.Many2one('res.users', 'Approved by Manager')
    
    # Justification
    reason = fields.Text('Reason for Debt', required=True)
    expected_po_id = fields.Many2one('purchase.order', 'Expected PO')
    expected_receipt_date = fields.Date('Expected Receipt Date')
    
    # Impact
    affected_production_qty = fields.Float('Affected Production Qty')
    delay_days = fields.Integer('Potential Delay (days)')
    
    def action_request_approval(self):
        """Send approval request"""
        self.state = 'requested'
        # Send notification to SPV
        self._send_notification_to_spv()
    
    def action_approve_spv(self):
        """SPV approve material debt"""
        self.state = 'approved_spv'
        self.approved_by_spv_id = self.env.user.id
        # Forward to Manager for final approval
        self._send_notification_to_manager()
    
    def action_approve_manager(self):
        """Manager approve material debt"""
        self.state = 'approved_manager'
        self.approved_by_manager_id = self.env.user.id
        # Allow negative stock for this material
        self._allow_negative_stock()
    
    def _allow_negative_stock(self):
        """Create negative stock move (with approval logged)"""
        self.env['stock.move'].create({
            'name': f'Material Debt: {self.product_id.name}',
            'product_id': self.product_id.id,
            'product_uom_qty': -self.debt_qty,
            'product_uom': self.uom_id.id,
            'location_id': self.workorder_id.location_dest_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'state': 'done',
            'material_debt_id': self.id,  # Link to debt record
        })
```

**Odoo Module to Customize**: `stock`, `mrp`

**Complexity**: 🟠 HIGH - Approval workflow + negative stock control

---

### 🔥 FEATURE 9: Android Mobile App untuk Barcode Scanning

**Problem**:
- Warehouse & Operator produksi menggunakan tablet
- Perlu scan barcode untuk FG receiving & material consumption

**Solution Required**:

**A. Odoo Barcode Module Extension**:
```python
# Extend Odoo Barcode module for custom workflows

class BarcodeScanner(models.Model):
    _inherit = 'barcodes.barcode_events_mixin'
    
    def on_barcode_scanned_finishing_stage1(self, barcode):
        """Scan Skin entering Stuffing stage"""
        # Parse barcode to get WO info
        wo, product, qty = self._parse_barcode(barcode)
        
        # Create finishing conversion record
        conversion = self.env['finishing.conversion'].create({
            'stage': 'stuffing',
            'workorder_id': wo.id,
            'input_product_id': product.id,
            'input_qty': qty,
        })
        
        return {'conversion_id': conversion.id}
    
    def on_barcode_scanned_fg_carton(self, barcode):
        """Scan Finished Goods carton"""
        # Parse barcode: FG-2026-00123-CTN001
        mo_id, carton_number = self._parse_fg_barcode(barcode)
        
        # Retrieve MO info
        mo = self.env['mrp.production'].browse(mo_id)
        
        # Display info to user
        return {
            'article': mo.product_id.default_code,
            'week': mo.production_week,
            'destination': mo.destination_country,
            'pcs_per_carton': mo.product_id.carton_capacity,
        }
```

**B. Custom Mobile UI (Odoo Mobile)**:
- Kiosk Mode untuk operator produksi
- Simplified UI untuk barcode scanning
- Offline capability (sync saat online)

**Odoo Module to Customize**: `barcodes`, custom mobile app

**Complexity**: 🔴 HIGH - Mobile app development + offline sync

---

### 🔥 FEATURE 10: Real-Time Dashboard & Analytics

**Problem**:
- Management perlu real-time visibility
- Current: Laporan manual 3-5 hari

**Solution Required**:

```python
# Custom dashboard using Odoo Dashboards module

class PPICDashboard(models.Model):
    _name = 'ppic.dashboard'
    _description = 'PPIC Real-Time Dashboard'
    
    @api.model
    def get_dashboard_data(self):
        """Fetch real-time data for dashboard"""
        today = fields.Date.today()
        
        # SPK Today
        spk_today = self.env['mrp.workorder'].search([
            ('date_planned_start', '=', today),
        ])
        
        spk_completed = spk_today.filtered(lambda w: w.state == 'done')
        spk_in_progress = spk_today.filtered(lambda w: w.state == 'progress')
        spk_delayed = spk_today.filtered(lambda w: w.date_planned_finished < fields.Date.today() and w.state != 'done')
        
        # Material Stock (Critical Items)
        critical_materials = self.env['product.product'].search([
            ('is_critical', '=', True),
        ])
        
        material_stock = []
        for material in critical_materials:
            qty = material.qty_available
            min_qty = material.reorder_point_ids[0].product_min_qty if material.reorder_point_ids else 0
            
            status = 'OK' if qty > min_qty * 1.5 else 'LOW' if qty > min_qty else 'CRITICAL'
            
            material_stock.append({
                'name': material.name,
                'code': material.default_code,
                'qty': qty,
                'uom': material.uom_id.name,
                'min_qty': min_qty,
                'status': status,
            })
        
        # Production Today (by Article)
        production_stats = {}
        for wo in spk_today:
            article = wo.production_id.product_id.default_code
            if article not in production_stats:
                production_stats[article] = {
                    'target': 0,
                    'actual': 0,
                }
            production_stats[article]['target'] += wo.target_qty
            production_stats[article]['actual'] += wo.qty_produced
        
        return {
            'spk_summary': {
                'total': len(spk_today),
                'completed': len(spk_completed),
                'in_progress': len(spk_in_progress),
                'delayed': len(spk_delayed),
            },
            'material_stock': material_stock,
            'production_stats': production_stats,
        }
```

**Odoo Module to Customize**: `board` (Dashboards), custom reporting

**Complexity**: 🟡 MEDIUM - Dashboard + reporting logic

---

### Summary of Custom Features

| # | Feature | Odoo Module | Complexity | Priority | Estimated Dev Time |
|---|---------|-------------|------------|----------|--------------------|
| 1 | Dual Trigger Production System | `mrp`, `purchase` | 🔴 CRITICAL | 🔴 MUST-HAVE | 15-20 days |
| 2 | Flexible Target System | `mrp` | 🔴 HIGH | 🔴 MUST-HAVE | 10-12 days |
| 3 | Dual-BOM System | `mrp` | 🔴 CRITICAL | 🔴 MUST-HAVE | 12-15 days |
| 4 | Warehouse Finishing 2-Stage | `stock`, `mrp` | 🟠 HIGH | 🔴 MUST-HAVE | 8-10 days |
| 5 | UOM Conversion Validation | `stock`, `mrp` | 🟠 MEDIUM | 🔴 MUST-HAVE | 5-7 days |
| 6 | Rework/Repair Module | `quality`, `mrp` | 🟠 MEDIUM | 🟠 HIGH | 8-10 days |
| 7 | Week/Destination Auto-Inheritance | `purchase`, `mrp` | 🟡 MEDIUM | 🔴 MUST-HAVE | 5-7 days |
| 8 | Material Debt System | `stock`, `mrp` | 🟠 HIGH | 🟠 HIGH | 7-9 days |
| 9 | Mobile Barcode App | `barcodes`, custom | 🔴 HIGH | 🟠 HIGH | 15-20 days |
| 10 | Real-Time Dashboard | `board`, reports | 🟡 MEDIUM | 🟠 MEDIUM | 5-7 days |

**Total Estimated Development Time**: **90-117 days** (3-4 months of heavy customization)

**⚠️ CRITICAL NOTE untuk Sales Odoo Indonesia**:
Ini adalah estimasi development time untuk **customization only**. Belum termasuk:
- Initial Odoo configuration (2-3 weeks)
- Data migration (2-3 weeks)
- Testing & QA (3-4 weeks)
- User training (2 weeks)
- Go-live preparation (1-2 weeks)

**Total Project Timeline**: **6-8 months** (realistic estimate)

---

<a name="section-7"></a>
## 7️⃣ BOM & MANUFACTURING LOGIC
