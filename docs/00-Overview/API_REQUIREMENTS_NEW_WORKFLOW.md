# 🔧 API REQUIREMENTS - NEW AUTOMATED WORKFLOW
**ERP Quty Karunia - Backend Implementation Guide**

**Date**: 4 Februari 2026  
**Purpose**: API specifications untuk PO → Auto MO → Auto WO workflow  
**Status**: SPECIFICATION READY ✅

---

## 📋 OVERVIEW

Workflow baru memerlukan **backend automation** untuk:
1. **Auto-create MO** saat PO KAIN submitted
2. **Auto-upgrade MO** saat PO LABEL submitted  
3. **Auto-generate WO/SPK** saat PPIC confirm MO
4. **Auto-notification** ke stakeholders

---

## 🔥 CRITICAL API ENDPOINTS

### 1. POST /api/v1/purchasing/purchase-orders

**Purpose**: Create PO dengan 3-type system

**Request Payload**:
```json
{
  "po_number": "PO-K-2026-00012",
  "po_type": "KAIN",  // ENUM: KAIN | LABEL | ACCESSORIES
  "po_date": "2026-02-04",
  "supplier_id": null,  // Null if multiple suppliers
  "expected_date": "2026-02-20",
  "article_id": 40551542,  // REQUIRED for KAIN/LABEL
  "article_qty": 1000,
  "week": null,  // REQUIRED for LABEL
  "destination": null,  // REQUIRED for LABEL
  "items": [
    {
      "material_id": 1234,
      "material_name": "[IKHR504] KOHAIR D.BROWN",
      "supplier_id": 56,  // Per-material supplier
      "quantity": 146.6,
      "unit": "YARD",
      "unit_price": 125000,
      "total_price": 18325000,
      "is_auto_generated": true  // From BOM explosion
    }
    // ... more items
  ],
  "total_amount": 45000000,
  "currency": "IDR"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "po_id": 789,
    "po_number": "PO-K-2026-00012",
    "po_type": "KAIN",
    "status": "DRAFT",
    "auto_mo_created": true,  // 🔥 NEW
    "mo_id": 890,  // 🔥 NEW
    "mo_number": "MO-2026-00089",  // 🔥 NEW
    "created_at": "2026-02-04T09:15:00"
  },
  "message": "PO created successfully. MO-2026-00089 auto-generated (DRAFT status)."
}
```

**Backend Logic** (if po_type == "KAIN"):
```python
# 1. Create PO
po = PurchaseOrder.create(po_data)

# 2. Auto-create MO (if KAIN)
if po.po_type == "KAIN" and po.article_id:
    mo = ManufacturingOrder.create({
        "mo_number": generate_mo_number(),
        "article_id": po.article_id,
        "qty_planned": po.article_qty,
        "status": "DRAFT",
        "source_po_kain_id": po.id,
        "created_by": "SYSTEM",
        "routing_type": auto_detect_routing(po.article_id),
        "batch_number": auto_generate_batch(po.article_id)
    })
    
    # 3. Notify PPIC
    send_notification(
        to=["ppic@qutykarunia.com"],
        subject=f"New MO DRAFT: {mo.mo_number}",
        body=f"MO auto-created from {po.po_number}. Please review."
    )
    
    return {"auto_mo_created": True, "mo_id": mo.id}
```

---

### 2. POST /api/v1/purchasing/purchase-orders (PO LABEL)

**Request Payload**:
```json
{
  "po_type": "LABEL",
  "source_po_kain_id": 789,  // 🔥 NEW: REQUIRED reference to PO KAIN
  "article_id": 40551542,  // MUST match source PO KAIN article
  "article_qty": 1000,
  "week": "05-2026",  // 🔑 CRITICAL
  "destination": "IKEA Norway DC",  // 🔑 CRITICAL
  "items": [
    {
      "material_name": "Hang Tag AFTONSPARV",
      "quantity": 1000,
      "unit": "PCS"
    }
  ]
}
```

**Backend Logic**:
```python
# 1. Validate PO KAIN reference
po_kain = PurchaseOrder.query.get(po_data.source_po_kain_id)
if not po_kain or po_kain.po_type != "KAIN":
    raise ValidationError(
        "Invalid PO KAIN reference. Please select a valid PO KAIN."
    )

# 2. Validate article match
if po_data.article_id != po_kain.article_id:
    raise ValidationError(
        f"Article mismatch! PO KAIN has article {po_kain.article_id}, "
        f"but you selected {po_data.article_id}"
    )

# 3. Create PO Label with reference
po_label = PurchaseOrder.create(po_data)

# 4. Find existing MO PARTIAL (created by PO KAIN)
mo = ManufacturingOrder.query.filter_by(
    source_po_kain_id=po_kain.id,
    status="PARTIAL"
).first()

if not mo:
    raise ValidationError(
        f"No MO found for PO KAIN {po_kain.po_number}. "
        "MO might already be RELEASED or not created yet."
    )

# 5. Auto-upgrade MO to RELEASED
mo.status = "RELEASED"
mo.week = po_label.week  # 🔒 Inherited
mo.destination = po_label.destination  # 🔒 Inherited
mo.source_po_label_id = po_label.id
mo.released_at = datetime.now()
mo.save()

# 4. Auto-generate remaining WO/SPK (Sewing, Finishing, Packing)
generate_wo_for_remaining_depts(mo)

# 5. Notify PPIC + Production
send_notification(
    to=["ppic@qutykarunia.com", "production@qutykarunia.com"],
    subject=f"MO {mo.mo_number} RELEASED - Full Production Start",
    body=f"Week: {mo.week}, Destination: {mo.destination}"
)

return {
    "mo_upgraded": True,
    "mo_id": mo.id,
    "mo_status": "RELEASED",
    "wo_generated_count": 5
}
```

---

### 2.5 POST /api/v1/purchasing/purchase-orders (PO ACCESSORIES)

**Purpose**: Create PO Accessories with optional PO KAIN reference

**Request Payload**:
```json
{
  "po_type": "ACCESSORIES",
  "po_date": "2026-02-05",
  "source_po_kain_id": 789,  // 🔥 NEW: OPTIONAL reference to PO KAIN (for traceability)
  "article_id": 40551542,  // Optional (can be null for general purchase)
  "items": [
    {
      "material_id": 5678,
      "material_name": "Thread Polyester Black",
      "supplier_id": 45,
      "quantity": 500,
      "unit": "KG",
      "unit_price": 85000,
      "total_price": 42500000
    },
    {
      "material_id": 5679,
      "material_name": "Filling Dacron",
      "supplier_id": 46,
      "quantity": 200,
      "unit": "KG",
      "unit_price": 120000,
      "total_price": 24000000
    }
  ],
  "total_amount": 66500000,
  "currency": "IDR"
}
```

**Backend Logic**:
```python
# 1. If source_po_kain_id provided, validate it
if po_data.source_po_kain_id:
    po_kain = PurchaseOrder.query.get(po_data.source_po_kain_id)
    if not po_kain or po_kain.po_type != "KAIN":
        raise ValidationError(
            "Invalid PO KAIN reference."
        )
    
    # Validate article match (if article_id provided)
    if po_data.article_id and po_data.article_id != po_kain.article_id:
        raise ValidationError(
            f"Article mismatch! PO KAIN has article {po_kain.article_id}"
        )

# 2. Create PO Accessories
po = PurchaseOrder.create(po_data)

# 3. NO AUTO-ACTION (no MO creation/upgrade)
# This is standard purchase only, but linked for traceability

return {
    "success": True,
    "data": {
        "po_id": po.id,
        "po_number": po.po_number,
        "po_type": "ACCESSORIES",
        "status": "DRAFT",
        "linked_to_po_kain": po.source_po_kain_id is not None
    },
    "message": "PO Accessories created successfully."
}
```

**Key Features**:
- ✅ **Optional Reference**: PO KAIN reference not mandatory (for general stock)
- ✅ **Traceability**: If linked, can track all PO related to one production order
- ✅ **Validation**: Article must match if both provided
- ✅ **No Trigger**: Does not affect MO status

---

### 3. PUT /api/v1/ppic/manufacturing-orders/{mo_id}/confirm

**Purpose**: PPIC confirm MO → Auto-generate WO/SPK

**Request Payload**:
```json
{
  "action": "CONFIRM",  // ENUM: CONFIRM | SAVE_DRAFT
  "edits": {
    "qty_planned": 950,  // Optional: PPIC dapat edit target
    "priority": "HIGH",  // Optional
    "routing_type": "Route1",
    "notes": "Rush order for Norway, prioritize"
  }
}
```

**Backend Logic**:
```python
# 1. Update MO with PPIC edits
mo = ManufacturingOrder.get(mo_id)
mo.qty_planned = edits.get("qty_planned", mo.qty_planned)
mo.priority = edits.get("priority")
mo.notes = edits.get("notes")
mo.routing_type = edits.get("routing_type", mo.routing_type)

# 2. Handle action type
if action == "SAVE_DRAFT":
    # Just save edits, keep status as DRAFT
    mo.status = "DRAFT"
    mo.last_edited_by = request.user.id
    mo.last_edited_at = datetime.now()
    mo.save()
    
    return {
        "success": True,
        "message": "MO saved as draft. You can confirm it later.",
        "mo_status": "DRAFT"
    }

# 3. If action == CONFIRM, activate MO
mo.status = "PARTIAL"
mo.confirmed_by_ppic = request.user.id
mo.confirmed_at = datetime.now()
mo.save()

# 3. BOM Explosion
materials = explode_bom(mo.article_id, mo.qty_planned)

# 4. Material Reservation
reserve_materials(mo.id, materials)

# 5. Auto-generate WO/SPK
wos_created = []

# Cutting (2 streams: Body + Baju)
wo_cut_body = WorkOrder.create({
    "wo_number": generate_wo_number("CUT-BODY"),
    "mo_id": mo.id,
    "department": "CUTTING",
    "stream": "BODY",
    "target_qty": calculate_with_buffer(mo.qty_planned, 0.10),
    "status": "PENDING"
})
wos_created.append(wo_cut_body)

wo_cut_baju = WorkOrder.create({
    "wo_number": generate_wo_number("CUT-BAJU"),
    "mo_id": mo.id,
    "department": "CUTTING",
    "stream": "BAJU",
    "target_qty": calculate_with_buffer(mo.qty_planned, 0.10),
    "status": "PENDING"
})
wos_created.append(wo_cut_baju)

# Embroidery
wo_emb = WorkOrder.create({
    "wo_number": generate_wo_number("EMB"),
    "mo_id": mo.id,
    "department": "EMBROIDERY",
    "target_qty": calculate_with_buffer(mo.qty_planned, 0.05),
    "status": "PENDING"
})
wos_created.append(wo_emb)

# Sewing/Finishing/Packing: HOLD (if status=PARTIAL)
# Will be generated when MO upgrades to RELEASED

# 6. Send Notifications
send_notification(
    to=["cutting.supervisor@qutykarunia.com"],
    subject=f"New WO: {wo_cut_body.wo_number}",
    body=f"MO {mo.mo_number} confirmed. Start production."
)

return {
    "success": True,
    "mo_status": "PARTIAL",
    "wos_created": [wo.wo_number for wo in wos_created]
}
```

---

### 4. GET /api/v1/purchasing/purchase-orders/{po_kain_id}/related

**Purpose**: Get all related PO (LABEL & ACCESSORIES) for a PO KAIN

**Response**:
```json
{
  "success": true,
  "data": {
    "po_kain": {
      "po_id": 789,
      "po_number": "PO-K-2026-00012",
      "article_id": 40551542,
      "article_name": "AFTONSPARV",
      "article_qty": 1000,
      "status": "CONFIRMED",
      "mo_number": "MO-2026-00089",
      "mo_status": "PARTIAL"
    },
    "related_po_label": [
      {
        "po_id": 790,
        "po_number": "PO-L-2026-00089",
        "week": "05-2026",
        "destination": "IKEA Norway DC",
        "status": "CONFIRMED"
      }
    ],
    "related_po_accessories": [
      {
        "po_id": 791,
        "po_number": "PO-A-2026-00156",
        "items_count": 4,
        "total_amount": 66500000,
        "status": "DRAFT"
      },
      {
        "po_id": 792,
        "po_number": "PO-A-2026-00157",
        "items_count": 2,
        "total_amount": 15000000,
        "status": "SENT"
      }
    ]
  }
}
```

---

### 5. GET /api/v1/ppic/manufacturing-orders/pending-review

**Purpose**: Get list of MO DRAFT (waiting PPIC confirmation)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "mo_id": 890,
      "mo_number": "MO-2026-00089",
      "status": "DRAFT",
      "article_code": "40551542",
      "article_name": "AFTONSPARV",
      "qty_planned": 1000,
      "source_po_number": "PO-K-2026-00012",
      "created_at": "2026-02-04T09:15:00",
      "created_by": "SYSTEM",
      "material_check": {
        "total_materials": 32,
        "sufficient": 28,
        "low_stock": 3,
        "out_of_stock": 1
      }
    }
  ],
  "count": 1
}
```

---

## ⚠️ HANDLING INCORRECT MOs

If MO is fundamentally wrong (wrong article, wrong source PO), PPIC should:

1. **Save as DRAFT** (don't confirm)
2. **Contact Purchasing** to review source PO
3. **Purchasing cancels/edits PO**
4. **System auto-updates MO** or creates new one

**Why no REJECT button?**
- MO is auto-generated from PO (source of truth)
- Rejecting MO doesn't fix the root cause (PO)
- Better workflow: Fix PO → MO auto-updates

**Workflow if PO is wrong**:
```
❌ BAD: PPIC rejects MO → Purchasing confused
✅ GOOD: PPIC saves draft → Notify Purchasing → Purchasing fixes PO
```

---

## 🔔 NOTIFICATION SYSTEM

### Email Template: MO Auto-Created

**To**: ppic@qutykarunia.com  
**Subject**: 🆕 New MO DRAFT: MO-2026-00089  

```
Hi PPIC Team,

A new Manufacturing Order has been auto-created from Purchase Order.

MO Details:
• MO Number: MO-2026-00089
• Article: [40551542] AFTONSPARV soft toy w astronaut suit
• Target Qty: 1000 pcs
• Source PO: PO-KAIN-2026-00012
• Status: DRAFT (Waiting Your Confirmation)

Action Required:
1. Review MO details
2. Check material availability
3. Edit if necessary
4. Confirm MO to activate production

⚠️ Material Stock Alert:
• 1 material OUT OF STOCK: [IKHR504] KOHAIR D.BROWN

View & Confirm MO: [Link to PPIC Dashboard]

Regards,
Quty Karunia ERP System
```

---

### Email Template: MO Upgraded to RELEASED

**To**: ppic@qutykarunia.com, production@qutykarunia.com  
**Subject**: 🟢 MO-2026-00089 RELEASED - Full Production Start  

```
Hi Team,

MO-2026-00089 has been upgraded to RELEASED status.

Details:
• MO Number: MO-2026-00089
• Article: [40551542] AFTONSPARV
• Target Qty: 1000 pcs
• Week: Week 05-2026 (Auto-inherited from PO Label)
• Destination: IKEA Norway DC (Auto-inherited)

Production Release:
✅ Cutting - Can start
✅ Embroidery - Can start
✅ Sewing - Can start NOW (PO Label received!)
✅ Finishing - Can start NOW
✅ Packing - Can start NOW

5 Work Orders automatically generated.

View WOs: [Link to Production Dashboard]

Regards,
Quty Karunia ERP System
```

---

## 🔐 VALIDATION RULES

### PO Creation
```python
if po_type == "KAIN" or po_type == "LABEL":
    if not article_id:
        raise ValidationError("Article is REQUIRED for KAIN/LABEL PO")
    if not article_qty or article_qty <= 0:
        raise ValidationError("Article quantity must be > 0")

if po_type == "LABEL":
    if not week:
        raise ValidationError("Week is REQUIRED for LABEL PO")
    if not destination:
        raise ValidationError("Destination is REQUIRED for LABEL PO")
    
    # Check if MO PARTIAL exists
    mo_partial = ManufacturingOrder.query.filter_by(
        article_id=article_id,
        status="PARTIAL"
    ).first()
    
    if not mo_partial:
        raise ValidationError(
            "No MO PARTIAL found for this article. "
            "Please create PO KAIN first!"
        )
```

### PPIC MO Confirmation
```python
if mo.status != "DRAFT":
    raise ValidationError("Only DRAFT MO can be confirmed")

if edits.get("qty_planned"):
    if edits["qty_planned"] > materials_available:
        raise ValidationError("Not enough materials for this quantity")
    if edits["qty_planned"] <= 0:
        raise ValidationError("Quantity must be greater than 0")

if action not in ["CONFIRM", "SAVE_DRAFT"]:
    raise ValidationError("Invalid action. Use CONFIRM or SAVE_DRAFT")

# Note: PPIC cannot reject MO. If MO is incorrect, 
# coordinate with Purchasing to modify source PO.
```

---

## 📊 DATABASE SCHEMA UPDATES

### Table: purchase_orders
```sql
ALTER TABLE purchase_orders ADD COLUMN po_type VARCHAR(20); 
-- ENUM: 'KAIN', 'LABEL', 'ACCESSORIES'

ALTER TABLE purchase_orders ADD COLUMN article_id INTEGER;
ALTER TABLE purchase_orders ADD COLUMN article_qty INTEGER;
ALTER TABLE purchase_orders ADD COLUMN week VARCHAR(20);
ALTER TABLE purchase_orders ADD COLUMN destination VARCHAR(255);

CREATE INDEX idx_po_type ON purchase_orders(po_type);
CREATE INDEX idx_po_article ON purchase_orders(article_id);
```

### Table: manufacturing_orders
```sql
ALTER TABLE manufacturing_orders ADD COLUMN source_po_kain_id INTEGER;
ALTER TABLE manufacturing_orders ADD COLUMN source_po_label_id INTEGER;
ALTER TABLE manufacturing_orders ADD COLUMN confirmed_by_ppic INTEGER;
ALTER TABLE manufacturing_orders ADD COLUMN confirmed_at TIMESTAMP;
ALTER TABLE manufacturing_orders ADD COLUMN released_at TIMESTAMP;
ALTER TABLE manufacturing_orders ADD COLUMN week VARCHAR(20);
ALTER TABLE manufacturing_orders ADD COLUMN destination VARCHAR(255);

-- New status values: DRAFT, PARTIAL, RELEASED, IN_PROGRESS, COMPLETED
ALTER TABLE manufacturing_orders MODIFY COLUMN status VARCHAR(20);

CREATE INDEX idx_mo_status ON manufacturing_orders(status);
CREATE INDEX idx_mo_article ON manufacturing_orders(article_id);
```

### Table: work_orders
```sql
ALTER TABLE work_orders ADD COLUMN stream VARCHAR(20); 
-- For dual stream: 'BODY', 'BAJU', or NULL

ALTER TABLE work_orders ADD COLUMN auto_generated BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_wo_stream ON work_orders(stream);
```

---

## 🧪 TESTING SCENARIOS

### Scenario 1: Happy Path (PO KAIN → MO → WO)
```python
def test_po_kain_auto_creates_mo():
    # 1. Create PO KAIN
    po = create_po({
        "po_type": "KAIN",
        "article_id": 40551542,
        "article_qty": 1000
    })
    
    # 2. Check MO auto-created
    mo = ManufacturingOrder.query.filter_by(
        source_po_kain_id=po.id
    ).first()
    
    assert mo is not None
    assert mo.status == "DRAFT"
    assert mo.qty_planned == 1000
    assert mo.article_id == 40551542
    
    # 3. PPIC confirm MO
    confirm_mo(mo.id, action="CONFIRM")
    
    # 4. Check WO auto-generated
    wos = WorkOrder.query.filter_by(mo_id=mo.id).all()
    assert len(wos) >= 3  # Cutting Body, Cutting Baju, Embroidery
    
    # 5. Check status
    mo.refresh()
    assert mo.status == "PARTIAL"
```

### Scenario 2: PO LABEL Auto-Upgrade MO
```python
def test_po_label_upgrades_mo():
    # Setup: MO PARTIAL exists
    mo = create_mo_partial(article_id=40551542)
    
    # 1. Create PO LABEL
    po_label = create_po({
        "po_type": "LABEL",
        "article_id": 40551542,
        "week": "05-2026",
        "destination": "IKEA Norway"
    })
    
    # 2. Check MO upgraded
    mo.refresh()
    assert mo.status == "RELEASED"
    assert mo.week == "05-2026"
    assert mo.destination == "IKEA Norway"
    assert mo.source_po_label_id == po_label.id
    
    # 3. Check additional WOs generated
    wos_sewing = WorkOrder.query.filter_by(
        mo_id=mo.id,
        department="SEWING"
    ).all()
    assert len(wos_sewing) == 2  # Body + Baju
```

### Scenario 3: Validation - PO LABEL without PO KAIN
```python
def test_po_label_without_mo_partial():
    # Attempt to create PO LABEL without MO PARTIAL
    with pytest.raises(ValidationError) as exc:
        create_po({
            "po_type": "LABEL",
            "article_id": 99999,  # No MO PARTIAL for this article
            "week": "05-2026"
        })
    
    assert "No MO PARTIAL found" in str(exc.value)
```

---

## 📈 PERFORMANCE CONSIDERATIONS

1. **Async Processing**: Use Celery/Redis for background tasks
   - MO auto-creation (instant UI response)
   - WO generation (can take 2-3 seconds)
   - Email notifications

2. **Database Indexing**: 
   - Index on `po_type`, `article_id`, `status`
   - Optimize queries with proper JOINs

3. **Caching**:
   - Cache BOM data (Redis)
   - Cache material stock levels (refresh every 5 min)

4. **Batch Operations**:
   - Generate multiple WOs in one transaction
   - Bulk notification sending

---

## ✅ ACCEPTANCE CRITERIA

- [ ] PO KAIN creation auto-creates MO (status: DRAFT)
- [ ] PPIC can review, edit, and confirm MO
- [ ] MO confirmation auto-generates WOs with flexible targets
- [ ] PO LABEL creation auto-upgrades MO to RELEASED
- [ ] Week & Destination auto-inherited from PO LABEL
- [ ] Remaining WOs auto-generated on MO upgrade
- [ ] Email notifications sent to correct stakeholders
- [ ] Validation prevents PO LABEL without PO KAIN
- [ ] Complete audit trail logged for all actions
- [ ] Dashboard shows pending MO reviews with alerts

---

**Version**: 1.0  
**Last Updated**: 4 Februari 2026
