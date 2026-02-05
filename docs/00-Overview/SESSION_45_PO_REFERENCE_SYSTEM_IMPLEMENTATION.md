# 🔗 SESSION 45 - PO REFERENCE SYSTEM IMPLEMENTATION
**ERP Quty Karunia - Purchase Order Hierarchy & Traceability**

**Date**: 4 Februari 2026  
**Expert**: IT UI/UX Expert  
**Method**: Deep Think + Deep Analysis + Deep Learning  
**Status**: ✅ SPECIFICATION COMPLETE

---

## 📋 EXECUTIVE SUMMARY

### What Changed?

**CRITICAL NEW REQUIREMENT**:  
*"PO Accessories dan PO Label, keduanya mengacu pada PO Kain. Namun proses trigger MOnya tetap."*

**Translation**:
- PO LABEL and PO ACCESSORIES now **REFERENCE** PO KAIN (parent-child relationship)
- MO trigger process **REMAINS UNCHANGED** (PO KAIN → MO DRAFT, PO LABEL → MO RELEASED)
- This creates a **PO Hierarchy System** for complete traceability

---

## 🎯 BUSINESS OBJECTIVES

### Problems Solved

1. **Article Mismatch Prevention** ❌ → ✅
   - **Before**: User manually selects article in PO LABEL → risk of selecting wrong article
   - **After**: Article auto-populated from PO KAIN → impossible to mismatch

2. **Complete Traceability** 📊
   - **Before**: Hard to find all PO related to one production order
   - **After**: One-click view of complete PO family (KAIN + LABEL + ACCESSORIES)

3. **Project Cost Tracking** 💰
   - **Before**: Manual calculation of total cost per order
   - **After**: Auto-calculation of PO KAIN + PO LABEL + PO ACCESSORIES

4. **Better MO Management** 🏭
   - **Before**: MO status tracking independent of PO
   - **After**: Clear visibility: which PO KAIN created which MO, which PO LABEL released it

---

## 🏗️ ARCHITECTURAL DESIGN

### PO Hierarchy Structure

```
PO KAIN (Parent) ────────────────┐
   │                              │
   ├─ Creates: MO (DRAFT)         │
   │     └─ PPIC Confirms         │
   │        └─ MO: PARTIAL        │
   │                              │
   ├─ Has ONE: PO LABEL (1:1) ───┤
   │     └─ Upgrades: MO RELEASED │
   │                              │
   └─ Has MANY: PO ACC (1:N) ────┘
        └─ No MO action
           (just cost tracking)
```

### Entity Relationships

```sql
purchase_orders
├─ id (PK)
├─ po_number
├─ po_type (KAIN | LABEL | ACCESSORIES)
├─ source_po_kain_id (FK → purchase_orders.id)
│    • NULL for PO KAIN
│    • REQUIRED for PO LABEL
│    • OPTIONAL for PO ACCESSORIES
├─ article_id (FK → products.id)
│    • REQUIRED for PO KAIN & PO LABEL
│    • OPTIONAL for PO ACCESSORIES
├─ week (VARCHAR)
│    • REQUIRED for PO LABEL
│    • NULL for others
└─ destination (VARCHAR)
     • REQUIRED for PO LABEL
     • NULL for others
```

---

## 📝 IMPLEMENTATION DETAILS

### 1. Backend API Updates

#### A. POST /api/v1/purchasing/purchase-orders (PO LABEL)

**New Request Payload**:
```json
{
  "po_type": "LABEL",
  "source_po_kain_id": 789,  // 🔥 NEW: REQUIRED
  "article_id": 40551542,    // Must match PO KAIN
  "week": "05-2026",         // REQUIRED
  "destination": "IKEA Norway DC",  // REQUIRED
  "items": [...]
}
```

**Validation Logic**:
```python
# 1. Validate PO KAIN exists
po_kain = PurchaseOrder.query.get(source_po_kain_id)
if not po_kain or po_kain.po_type != "KAIN":
    raise ValidationError("Invalid PO KAIN reference")

# 2. Validate article match
if article_id != po_kain.article_id:
    raise ValidationError(f"Article mismatch!")

# 3. Validate no duplicate PO LABEL
existing_label = PurchaseOrder.query.filter_by(
    source_po_kain_id=po_kain.id,
    po_type="LABEL"
).first()
if existing_label:
    raise ValidationError("PO LABEL already exists for this PO KAIN")

# 4. Find MO and upgrade
mo = ManufacturingOrder.query.filter_by(
    source_po_kain_id=po_kain.id,
    status="PARTIAL"
).first()
if not mo:
    raise ValidationError("No MO PARTIAL found for this PO KAIN")

# 5. Upgrade MO to RELEASED
mo.status = "RELEASED"
mo.week = week
mo.destination = destination
mo.source_po_label_id = po_label.id
```

#### B. POST /api/v1/purchasing/purchase-orders (PO ACCESSORIES)

**New Request Payload**:
```json
{
  "po_type": "ACCESSORIES",
  "source_po_kain_id": 789,  // 🔥 NEW: OPTIONAL
  "article_id": 40551542,    // Optional (auto if linked)
  "items": [...]
}
```

**Validation Logic**:
```python
# 1. If source_po_kain_id provided, validate it
if source_po_kain_id:
    po_kain = PurchaseOrder.query.get(source_po_kain_id)
    if not po_kain or po_kain.po_type != "KAIN":
        raise ValidationError("Invalid PO KAIN reference")
    
    # If article_id provided, must match PO KAIN
    if article_id and article_id != po_kain.article_id:
        raise ValidationError("Article mismatch!")

# 2. Create PO (no MO action)
po = PurchaseOrder.create(...)
```

#### C. New Endpoint: GET /api/v1/purchasing/purchase-orders/{po_kain_id}/related

**Purpose**: Fetch all related PO for a PO KAIN

**Response**:
```json
{
  "po_kain": {
    "po_id": 789,
    "po_number": "PO-K-2026-00012",
    "article": "AFTONSPARV",
    "mo_number": "MO-2026-00089",
    "mo_status": "PARTIAL"
  },
  "related_po_label": [
    {
      "po_id": 790,
      "po_number": "PO-L-2026-00089",
      "week": "05-2026",
      "destination": "IKEA Norway DC"
    }
  ],
  "related_po_accessories": [
    {"po_id": 791, "po_number": "PO-A-2026-00156", "items_count": 4},
    {"po_id": 792, "po_number": "PO-A-2026-00157", "items_count": 2}
  ]
}
```

---

### 2. Frontend UI Updates

#### A. PurchasingPage.tsx

**Component 1: PO Type Selector (Enhanced)**
```tsx
// Already exists, no changes needed
<div className="flex gap-2">
  <button className={poType === 'KAIN' ? 'active' : ''}>
    PO KAIN
  </button>
  <button className={poType === 'LABEL' ? 'active' : ''}>
    PO LABEL
  </button>
  <button className={poType === 'ACCESSORIES' ? 'active' : ''}>
    PO ACCESSORIES
  </button>
</div>
```

**Component 2: PO KAIN Reference Selector (NEW)**
```tsx
{poType === 'LABEL' && (
  <div className="mb-4">
    <label className="block mb-2 font-semibold">
      🔗 PO KAIN Reference *
    </label>
    <select
      value={sourcePoKainId}
      onChange={(e) => {
        setSourcePoKainId(e.target.value);
        // Auto-populate article from PO KAIN
        const poKain = availablePoKain.find(po => po.id == e.target.value);
        if (poKain) {
          setArticleId(poKain.article_id);
          setArticleQty(poKain.article_qty);
        }
      }}
      required
    >
      <option value="">Select PO KAIN...</option>
      {availablePoKain.map(po => (
        <option key={po.id} value={po.id}>
          {po.po_number} | {po.article_name} | MO: {po.mo_status}
        </option>
      ))}
    </select>
  </div>
)}

{poType === 'ACCESSORIES' && (
  <div className="mb-4">
    <label className="flex items-center gap-2">
      <input
        type="checkbox"
        checked={linkToPoKain}
        onChange={(e) => setLinkToPoKain(e.target.checked)}
      />
      Link to PO KAIN (for project tracking)
    </label>
    
    {linkToPoKain && (
      <select
        value={sourcePoKainId}
        onChange={(e) => {
          setSourcePoKainId(e.target.value);
          const poKain = availablePoKain.find(po => po.id == e.target.value);
          if (poKain) {
            setArticleId(poKain.article_id); // Auto-populate
          }
        }}
      >
        <option value="">Select PO KAIN...</option>
        {availablePoKain.map(po => (
          <option key={po.id} value={po.id}>
            {po.po_number} | {po.article_name}
          </option>
        ))}
      </select>
    )}
  </div>
)}
```

**Component 3: Article Field (Modified)**
```tsx
{poType === 'LABEL' ? (
  // Read-only for PO LABEL (auto-populated from PO KAIN)
  <div className="mb-4">
    <label className="block mb-2 font-semibold">
      📦 Article (from PO KAIN) 🔒
    </label>
    <input
      type="text"
      value={selectedArticle?.name || ''}
      disabled
      className="bg-gray-100 cursor-not-allowed"
    />
  </div>
) : (
  // Editable for PO KAIN and PO ACCESSORIES
  <div className="mb-4">
    <label className="block mb-2 font-semibold">
      📦 Article {poType === 'KAIN' ? '*' : '(Optional)'}
    </label>
    <select
      value={articleId}
      onChange={(e) => setArticleId(e.target.value)}
      required={poType === 'KAIN'}
    >
      <option value="">Select Article...</option>
      {articles.map(a => (
        <option key={a.id} value={a.id}>
          {a.article_code} - {a.name}
        </option>
      ))}
    </select>
  </div>
)}
```

**Component 4: PO Detail Modal with Related PO (NEW)**
```tsx
const PODetailModal = ({ poId, onClose }) => {
  const [poFamily, setPoFamily] = useState(null);
  
  useEffect(() => {
    if (po.po_type === 'KAIN') {
      // Fetch related PO
      fetch(`/api/v1/purchasing/purchase-orders/${poId}/related`)
        .then(res => res.json())
        .then(data => setPoFamily(data));
    }
  }, [poId]);
  
  return (
    <div className="modal">
      <h2>PO Detail: {po.po_number}</h2>
      
      {/* Basic Info */}
      <div className="mb-4">
        <p>Type: {po.po_type}</p>
        <p>Article: {po.article_name}</p>
        <p>Status: <StatusBadge status={po.status} /></p>
      </div>
      
      {/* Related MO (if PO KAIN) */}
      {po.po_type === 'KAIN' && po.mo_number && (
        <div className="mb-4">
          <h3>🤖 Related MO:</h3>
          <p>MO: {po.mo_number}</p>
          <p>Status: <StatusBadge status={po.mo_status} /></p>
        </div>
      )}
      
      {/* Related PO (if PO KAIN) */}
      {poFamily && (
        <div className="mb-4">
          <h3>🔗 Related Purchase Orders:</h3>
          
          {/* PO LABEL */}
          {poFamily.related_po_label?.length > 0 && (
            <div className="mb-2">
              <h4>PO LABEL:</h4>
              {poFamily.related_po_label.map(label => (
                <div key={label.po_id} className="p-2 bg-blue-50">
                  <p>{label.po_number}</p>
                  <p>Week: {label.week}</p>
                  <p>Destination: {label.destination}</p>
                  <StatusBadge status={label.status} />
                </div>
              ))}
            </div>
          )}
          
          {/* PO ACCESSORIES */}
          {poFamily.related_po_accessories?.length > 0 && (
            <div className="mb-2">
              <h4>PO ACCESSORIES ({poFamily.related_po_accessories.length}):</h4>
              {poFamily.related_po_accessories.map(acc => (
                <div key={acc.po_id} className="p-2 bg-gray-50">
                  <p>{acc.po_number}</p>
                  <p>Items: {acc.items_count}</p>
                  <StatusBadge status={acc.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Total Project Cost */}
      {poFamily && (
        <div className="mb-4 p-4 bg-green-50">
          <h3>💰 Total Project Cost:</h3>
          <p>PO KAIN: {formatCurrency(po.total_amount)}</p>
          {poFamily.related_po_label?.[0] && (
            <p>PO LABEL: {formatCurrency(poFamily.related_po_label[0].total_amount)}</p>
          )}
          <p>PO ACC: {formatCurrency(calculateAccTotal(poFamily.related_po_accessories))}</p>
          <hr />
          <p className="font-bold">GRAND TOTAL: {formatCurrency(grandTotal)}</p>
        </div>
      )}
      
      <button onClick={onClose}>Close</button>
    </div>
  );
};
```

**Component 5: PO List with Relationship Indicators (Enhanced)**
```tsx
<table>
  <thead>
    <tr>
      <th>Type</th>
      <th>PO Number</th>
      <th>Article</th>
      <th>Status</th>
      <th>Linked To</th>  {/* NEW COLUMN */}
      <th>Amount</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {purchaseOrders.map(po => (
      <tr key={po.id}>
        <td>{po.po_type}</td>
        <td>{po.po_number}</td>
        <td>{po.article_name}</td>
        <td><StatusBadge status={po.status} /></td>
        <td>
          {po.po_type === 'KAIN' && (
            <span>
              🔗 {po.related_label_count}L+{po.related_acc_count}A
              {po.mo_status && (
                <> | MO: <StatusBadge status={po.mo_status} size="sm" /></>
              )}
            </span>
          )}
          {po.po_type === 'LABEL' && po.source_po_kain_number && (
            <span>
              → {po.source_po_kain_number}
              {po.mo_upgraded && <> | ✅ MO RELEASED</>}
            </span>
          )}
          {po.po_type === 'ACCESSORIES' && po.source_po_kain_number && (
            <span>→ {po.source_po_kain_number} (Optional)</span>
          )}
        </td>
        <td>{formatCurrency(po.total_amount)}</td>
        <td>
          <button onClick={() => viewDetail(po.id)}>👁</button>
        </td>
      </tr>
    ))}
  </tbody>
</table>
```

---

### 3. Database Migrations

**Migration File**: `migration-po-reference-system.sql`

```sql
-- =====================================================
-- MIGRATION: PO Reference System
-- Date: 2026-02-04
-- Purpose: Add PO KAIN reference to PO LABEL and PO ACC
-- =====================================================

-- Step 1: Add new columns
ALTER TABLE purchase_orders 
ADD COLUMN source_po_kain_id INTEGER,
ADD COLUMN article_id INTEGER,
ADD COLUMN article_qty INTEGER,
ADD COLUMN week VARCHAR(10),
ADD COLUMN destination VARCHAR(255);

-- Step 2: Add foreign keys
ALTER TABLE purchase_orders
ADD CONSTRAINT fk_po_source_po_kain 
  FOREIGN KEY (source_po_kain_id) 
  REFERENCES purchase_orders(id) 
  ON DELETE RESTRICT;

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_po_article 
  FOREIGN KEY (article_id) 
  REFERENCES products(id) 
  ON DELETE RESTRICT;

-- Step 3: Add indexes for performance
CREATE INDEX idx_po_source_po_kain ON purchase_orders(source_po_kain_id);
CREATE INDEX idx_po_article ON purchase_orders(article_id);
CREATE INDEX idx_po_type_status ON purchase_orders(po_type, status);
CREATE INDEX idx_po_week ON purchase_orders(week);

-- Step 4: Add validation constraints
ALTER TABLE purchase_orders
ADD CONSTRAINT chk_po_label_requires_kain
CHECK (
    (po_type = 'LABEL' AND source_po_kain_id IS NOT NULL) OR
    (po_type != 'LABEL')
);

ALTER TABLE purchase_orders
ADD CONSTRAINT chk_po_label_week_destination
CHECK (
    (po_type = 'LABEL' AND week IS NOT NULL AND destination IS NOT NULL) OR
    (po_type != 'LABEL')
);

ALTER TABLE purchase_orders
ADD CONSTRAINT chk_po_kain_no_self_reference
CHECK (
    po_type != 'KAIN' OR source_po_kain_id IS NULL
);

ALTER TABLE purchase_orders
ADD CONSTRAINT chk_po_article_required_for_kain_label
CHECK (
    ((po_type IN ('KAIN', 'LABEL')) AND article_id IS NOT NULL) OR
    (po_type = 'ACCESSORIES')
);

-- Step 5: Add column to manufacturing_orders for PO LABEL tracking
ALTER TABLE manufacturing_orders
ADD COLUMN source_po_label_id INTEGER;

ALTER TABLE manufacturing_orders
ADD CONSTRAINT fk_mo_source_po_label 
  FOREIGN KEY (source_po_label_id) 
  REFERENCES purchase_orders(id) 
  ON DELETE SET NULL;

CREATE INDEX idx_mo_source_po_label ON manufacturing_orders(source_po_label_id);

-- Step 6: Verification queries
-- Check existing data (should return 0 if fresh install)
SELECT COUNT(*) as existing_po_count FROM purchase_orders;

-- Test constraint (should fail)
-- INSERT INTO purchase_orders (po_type, source_po_kain_id) VALUES ('LABEL', NULL);

COMMIT;
```

---

## 📊 TESTING SCENARIOS

### Test Case 1: Create PO LABEL with Valid PO KAIN

**Prerequisites**:
- PO KAIN exists: PO-K-2026-00012 (Article: AFTONSPARV, MO: PARTIAL)

**Steps**:
1. Open "Create PO" form
2. Select PO Type: "LABEL"
3. Select PO KAIN Reference: "PO-K-2026-00012"
4. Verify article auto-populated: "AFTONSPARV" (read-only)
5. Input Week: "05-2026"
6. Input Destination: "IKEA Norway DC"
7. Add label materials
8. Submit

**Expected Result**:
- ✅ PO LABEL created successfully
- ✅ PO LABEL linked to PO-K-2026-00012
- ✅ MO-2026-00089 upgraded to RELEASED
- ✅ Week & Destination inherited to MO
- ✅ Notification sent to PPIC

---

### Test Case 2: Attempt to Create PO LABEL without PO KAIN

**Steps**:
1. Open "Create PO" form
2. Select PO Type: "LABEL"
3. Leave PO KAIN Reference empty
4. Try to submit

**Expected Result**:
- ❌ Validation error: "PO KAIN reference is required for PO LABEL"
- ❌ Form not submitted

---

### Test Case 3: Create PO ACCESSORIES with Optional Link

**Scenario A: Linked to PO KAIN**

**Steps**:
1. Open "Create PO" form
2. Select PO Type: "ACCESSORIES"
3. Check: "Link to PO KAIN"
4. Select PO KAIN: "PO-K-2026-00012"
5. Verify article auto-populated (read-only)
6. Add materials
7. Submit

**Expected Result**:
- ✅ PO ACCESSORIES created
- ✅ Linked to PO-K-2026-00012
- ✅ No MO action (as expected)
- ✅ Visible in PO KAIN detail view

**Scenario B: General Purchase (Not Linked)**

**Steps**:
1. Open "Create PO" form
2. Select PO Type: "ACCESSORIES"
3. Leave "Link to PO KAIN" unchecked
4. Select article manually or leave blank
5. Add materials
6. Submit

**Expected Result**:
- ✅ PO ACCESSORIES created
- ✅ Not linked to any PO KAIN
- ✅ No MO action

---

### Test Case 4: View PO Family Tree

**Prerequisites**:
- PO KAIN: PO-K-2026-00012
- PO LABEL: PO-L-2026-00089 (linked to PO-K-2026-00012)
- PO ACC: PO-A-2026-00156, PO-A-2026-00157 (both linked)

**Steps**:
1. Navigate to PO List
2. Click "View Detail" on PO-K-2026-00012
3. Verify PO family tree displayed

**Expected Result**:
- ✅ PO KAIN info shown
- ✅ Related MO: MO-2026-00089 (RELEASED)
- ✅ PO LABEL: 1 record shown with Week/Destination
- ✅ PO ACCESSORIES: 2 records shown
- ✅ Total Project Cost calculated: 132M IDR

---

## 📈 SUCCESS METRICS

### Quantitative KPIs

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Article Mismatch Errors** | 0% | Track validation errors in logs |
| **PO Creation Time** | -20% | Avg time to create PO LABEL (auto-populate saves time) |
| **Traceability Clicks** | 1-click | Count clicks to view complete PO family |
| **Cost Calculation Time** | <2 sec | Time to calculate total project cost |
| **User Errors** | -80% | Track PO LABEL with wrong article |

### Qualitative Benefits

- ✅ **Improved UX**: Auto-populated fields reduce manual entry
- ✅ **Better Visibility**: Complete PO family in one view
- ✅ **Reduced Errors**: Impossible to create PO LABEL with wrong article
- ✅ **Enhanced Reporting**: Easy to generate cost reports per project
- ✅ **Better Collaboration**: Purchasing team can see complete picture

---

## 🚀 ROLLOUT PLAN

### Phase 1: Backend Implementation (Week 1)
- Day 1-2: Database migration
- Day 3-4: API endpoint updates (PO LABEL, PO ACCESSORIES)
- Day 5: New endpoint: GET /related
- Day 6-7: Unit tests + Integration tests

### Phase 2: Frontend Implementation (Week 2)
- Day 1-2: PO KAIN Reference Selector component
- Day 3: Article auto-population logic
- Day 4: PO Detail Modal with family tree
- Day 5: PO List relationship indicators
- Day 6-7: Integration testing + Bug fixes

### Phase 3: User Training (Week 3)
- Day 1: Create training materials (screenshots, videos)
- Day 2-3: Train Purchasing A (Fabric Specialist)
- Day 4-5: Train Purchasing B (Label Specialist)
- Day 6-7: Train Purchasing C (Accessories Specialist)

### Phase 4: Go-Live (Week 4)
- Day 1: Staging deployment
- Day 2-3: UAT (User Acceptance Testing)
- Day 4: Production deployment
- Day 5-7: Post-deployment support

---

## 📚 APPENDIX

### A. API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/purchasing/purchase-orders` | POST | Create PO (KAIN/LABEL/ACC) |
| `/api/v1/purchasing/purchase-orders/{id}` | GET | Get PO detail |
| `/api/v1/purchasing/purchase-orders/{po_kain_id}/related` | GET | Get PO family tree |
| `/api/v1/purchasing/purchase-orders/{id}` | PUT | Update PO |

### B. Database Schema Diagram

```
┌─────────────────────────┐
│   purchase_orders       │
├─────────────────────────┤
│ id (PK)                 │
│ po_number               │
│ po_type                 │
│ source_po_kain_id (FK)  │───┐
│ article_id (FK)         │   │
│ article_qty             │   │
│ week                    │   │ Self-reference
│ destination             │   │ (PO LABEL/ACC
│ status                  │   │  → PO KAIN)
│ total_amount            │   │
│ created_at              │ ◄─┘
└─────────────────────────┘
         │
         │ 1:1 (PO KAIN → MO)
         ▼
┌─────────────────────────┐
│  manufacturing_orders   │
├─────────────────────────┤
│ id (PK)                 │
│ mo_number               │
│ source_po_kain_id (FK)  │
│ source_po_label_id (FK) │
│ article_id              │
│ status                  │
│ week                    │
│ destination             │
└─────────────────────────┘
```

### C. Status Flow Diagram

```
PO KAIN Created
     ↓
MO Created (DRAFT)
     ↓
PPIC Confirms
     ↓
MO Status: PARTIAL ────┐
     ↓                 │
Cutting/Embo Start     │
     ↓                 │
Wait for PO LABEL ◄────┘
     ↓
PO LABEL Created (with PO KAIN reference)
     ↓
MO Status: RELEASED ───┐
     ↓                 │
ALL Dept Start        │
     ↓                 │
PO ACCESSORIES        │
(Optional) ───────────┘
```

---

## ✅ COMPLETION CHECKLIST

**Documentation**:
- [x] API specification updated (API_REQUIREMENTS_NEW_WORKFLOW.md)
- [x] UI mockups created (Rencana Tampilan.md)
- [x] Database schema defined
- [x] Testing scenarios written
- [x] Implementation summary created (this document)

**Code Ready for**:
- [ ] Backend developers to implement API endpoints
- [ ] Frontend developers to implement UI components
- [ ] Database admins to run migrations
- [ ] QA team to execute test cases
- [ ] Training team to prepare materials

**Next Actions**:
1. Review this document with management
2. Allocate resources (2 backend + 2 frontend developers)
3. Create sprint backlog in project management tool
4. Schedule kickoff meeting
5. Begin Phase 1 implementation

---

**Document Version**: 1.0  
**Last Updated**: 4 Februari 2026  
**Author**: IT UI/UX Expert Team  
**Status**: READY FOR IMPLEMENTATION ✅
