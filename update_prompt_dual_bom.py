"""
Script to insert Dual-BOM section into prompt.md
"""

# Dual-BOM section content to insert
DUAL_BOM_SECTION = """
## 🔄 DUAL-BOM SYSTEM - February 6, 2026

**🆕 CRITICAL ARCHITECTURE UPDATE: TWO SEPARATE BOM SYSTEMS**

### Why Dual-BOM?

PT Quty Karunia discovered that **ONE BOM cannot serve TWO different purposes**:

| Stakeholder | Needs | Old Single BOM Problem |
|-------------|-------|------------------------|
| **Purchasing** | "What RAW materials to buy?" | Sees WIP components (confusing) |
| **PPIC/Production** | "How to manufacture step-by-step?" | Cannot see department-specific routing |

**Solution**: Split into **BOM Production** (Process) + **BOM Purchasing** (Materials)

---

### BOM PRODUCTION (Process-Oriented)

**Purpose**: Show manufacturing flow step-by-step through each department

**Structure**:
```
Article: AFTONSPARV Bear
├─ CUTTING DEPT (Stage 1)
│  Input: [IKHR504] KOHAIR 0.15 YD + [IJBR105] BOA 0.0015 YD
│  Output: AFTONSPARV_WIP_CUTTING (skin pieces)
│
├─ SEWING DEPT (Stage 2)
│  Input: AFTONSPARV_WIP_CUTTING + [ATR10400] Thread 60 CM
│  Output: AFTONSPARV_WIP_SKIN (sewn skin, no filling)
│
├─ FINISHING DEPT (Stage 3)
│  Input: AFTONSPARV_WIP_SKIN + [IKP20157] Filling 54 GRAM
│  Output: AFTONSPARV_WIP_BONEKA (finished doll)
│
└─ PACKING DEPT (Stage 4)
   Input: AFTONSPARV_WIP_BONEKA 60 PCS + [ACB30104] Carton 1 PCE
   Output: [40551542] AFTONSPARV Bear FG (ready to ship)
```

**Used By**:
- PPIC: MO/SPK explosion per department
- Production Depts: Material request per stage
- Warehouse: WIP tracking between stages
- Costing: Calculate cost per department

**Database Tables**:
- `bom_production_headers` (1 header per article per department)
- `bom_production_details` (materials for that specific stage)

**Import Files** (from docs/Masterdata/BOM Production/):
- Cutting.xlsx (508 rows)
- Embo.xlsx (306 rows)
- Sewing.xlsx (2,450 rows)
- Finishing.xlsx (835 rows)
- Finishing Goods.xlsx (518 rows)
- Packing.xlsx (1,228 rows)
- **Total**: 5,845 BOM lines

---

### BOM PURCHASING (Material-Oriented)  

**Purpose**: Show ONLY RAW materials to purchase (no WIP components)

**Structure**:
```
Article: AFTONSPARV Bear
RAW Materials to Purchase (per 1 PCE):
├─ [IKHR504] KOHAIR Fabric: 0.15 YARD
├─ [IJBR105] BOA Fabric: 0.0015 YARD
├─ [IKP20157] Filling: 54 GRAM
├─ [ATR10400] Thread: 60 CM
├─ [ALL40030] Label: 1 PCE
└─ [ACB30104] Carton: 0.0167 PCE

Total: 6 RAW materials (NO WIP like WIP_CUTTING, WIP_SKIN)
```

**Used By**:
- Purchasing: Calculate material needs for PO
- Inventory Planning: Material Requirement Planning (MRP)
- Procurement: Supplier sourcing and lead time

**Database Tables**:
- `bom_purchasing_headers` (1 header per article)
- `bom_purchasing_details` (aggregated RAW materials only)

**Generation**: AUTO-GENERATED from BOM Production
- Filter: `material_type = 'RAW_MATERIAL'` (exclude WIP)
- Aggregate: Sum quantities across all departments
- Trigger: When BOM Production is imported/updated

---

### Implementation Quick Reference

**API Endpoints**:
```python
# BOM Production APIs
GET /api/v1/bom-production?article_id=X&department_id=Y
POST /api/v1/bom-production
GET /api/v1/bom-production/explode/{article_id}

# BOM Purchasing APIs
GET /api/v1/bom-purchasing?article_id=X
POST /api/v1/bom-purchasing/generate-from-production
GET /api/v1/bom-purchasing/calculate-needs/{article_id}?qty=500

# Bulk Import
POST /api/v1/imports/bom-production?department=cutting
```

**Business Logic**:
1. **PPIC Creates MO**: Uses `bom_production_headers` (department-specific)
2. **Purchasing Creates PO**: Uses `bom_purchasing_details` (RAW materials only)
3. **Auto-Sync**: When BOM Production changes → regenerate BOM Purchasing

**Reference**: See [DUAL_BOM_SYSTEM_IMPLEMENTATION.md](docs/DUAL_BOM_SYSTEM_IMPLEMENTATION.md) for complete guide (1,200+ lines).

---

"""

# Read prompt.md
with open('prompt.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line number after "Deadline: February 8, 2026"
insert_line = None
for i, line in enumerate(lines):
    if 'Deadline: February 8, 2026' in line:
        # Insert after the next "---" line
        for j in range(i+1, len(lines)):
            if lines[j].strip() == '---':
                insert_line = j + 1
                break
        break

if insert_line:
    # Insert the new section
    lines.insert(insert_line, DUAL_BOM_SECTION + '\n')
    
    # Write back
    with open('prompt.md', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ SUCCESS: Added Dual-BOM section to prompt.md at line {insert_line}")
    print(f"   Section length: {len(DUAL_BOM_SECTION.splitlines())} lines")
else:
    print("❌ ERROR: Could not find insertion point in prompt.md")
