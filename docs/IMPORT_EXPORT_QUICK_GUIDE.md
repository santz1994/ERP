# Quick Import Guide - BOM, MO, Documents & Duplicate Management

**Date**: January 23, 2026  
**For**: Quty Karunia ERP System Users

---

## 📊 Import BOM (Bill of Materials)

### What is BOM?
BOM lists all materials/components needed to manufacture a product. Each line specifies:
- **Product Code**: The WIP product being manufactured
- **Component Code**: Material/part needed
- **Quantity**: How much of that component per unit
- **Wastage %**: Expected waste during production

### Step-by-Step: Import BOM

#### Method 1: Via Web UI (Easiest)
```
1. Login as Admin
2. Click: Admin → Import / Export
3. Select Tab: "Import"
4. Choose: "Bill of Materials" from dropdown
5. Click: "Download Template"
6. Open template in Excel
7. Fill in your BOM data
8. Save as CSV or Excel
9. Upload the file
10. System validates & imports
```

#### Template Format (CSV)
```csv
product_code,component_code,qty_needed,wastage_percent
WIP-SEW-SHARK,FAB-VEL-WHT,2.5,5
WIP-SEW-SHARK,THR-BLU-001,0.15,2
WIP-EMB-SHARK,FAB-VEL-WHT,2.5,3
FIN-SHARK,BOX-001,1,1
```

#### Template Format (Excel)
Same columns as CSV, one row per component.

#### Validation Rules
- ✅ Product code must exist in system
- ✅ Component code must exist in system
- ✅ Quantity must be > 0
- ✅ Wastage % must be 0-100
- ❌ Cannot import duplicate product+component combinations
- ❌ Invalid codes will show row number in error

### Result
✅ BOM Header created automatically (if new)  
✅ BOM Details added with quantities  
✅ System ready for Manufacturing Orders

---

## 📦 Create/Import Manufacturing Orders (MO)

### What is MO?
Manufacturing Order (SPK = Sales Order Packing) is instruction to produce X quantity of a product through specific routing (departments).

### MO States
```
DRAFT → (Approve) → IN_PROGRESS → DONE
 ↓
Pending PPIC      Auto-created    Completed
manager approval  work orders     production
```

### Method 1: Create via UI (Easiest)

```
1. Go to: PPIC → Production Planning
2. Click: "➕ Create MO" button
3. Fill form:
   - Product *: Select WIP or Finish Good (required)
   - Quantity *: How many to produce (required)
   - Routing Type: Route 1, 2, or 3
   - Batch Number *: Unique identifier (required)
   - Sales Order ID: Optional reference
4. Click: "Create"
5. Result: MO created in DRAFT state
```

### Method 2: Create via API

```bash
curl -X POST http://localhost:8000/api/v1/ppic/manufacturing-order \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "product_id": 2,
    "qty_planned": 500,
    "routing_type": "Route 1",
    "batch_number": "BATCH-2026-001",
    "so_line_id": 1
  }'
```

### Response
```json
{
  "id": 123,
  "batch_number": "BATCH-2026-001",
  "product_id": 2,
  "qty_planned": 500,
  "routing_type": "Route 1",
  "state": "DRAFT",
  "created_at": "2026-01-23T10:00:00"
}
```

### Next: Approve MO
```
1. MO created in DRAFT state
2. PPIC Manager reviews
3. Click: "Approve" button
4. System creates Work Orders for each department
5. MO moves to IN_PROGRESS
6. Each department gets their tasks
```

---

## 📥 Import / Export All Documents

### Available Document Types
| Type | Import | Export | Purpose |
|------|--------|--------|---------|
| **Products** | ✅ | ✅ | Master product data |
| **Users** | ✅ | ✅ | Bulk user management |
| **BOM** | ✅ | ✅ | Material specifications |
| **Stock Data** | ✅ | ✅ | Inventory levels |
| **Work Orders** | ❌ | ✅ | Production tasks (auto-generated) |
| **QC Inspections** | ✅ | ✅ | Quality control records |
| **Manufacturing Orders** | ❌ | ✅ | Production orders (use PPIC page) |

### Export Process
```
1. Admin → Import / Export
2. Select Tab: "Export"
3. Choose data type
4. Choose format: CSV or Excel
5. Click: "Export"
6. File downloads to your computer
```

### Import Process
```
1. Admin → Import / Export
2. Select Tab: "Import"
3. Choose data type
4. Click: "Download Template" (get required columns)
5. Fill template in Excel
6. Save as CSV or Excel
7. Upload file
8. Review validation errors
9. System imports successful rows
```

---

## 🔄 Delete Duplicate Records from Database

### What Are Duplicates?
Example duplicates:
- Same product code entered twice
- Same batch number twice
- Same user email twice

### Method 1: Via Admin Database Tool

```
1. Admin → System → Database Management (if available)
2. Find duplicates with SQL query
3. Delete by ID
```

### Method 2: Find & Delete via SQL

#### Find Duplicate Products
```sql
-- Products with same code
SELECT code, COUNT(*) as count, GROUP_CONCAT(id) as ids
FROM products
GROUP BY code
HAVING COUNT(*) > 1;
```

#### Delete Duplicate Products (Keep Latest)
```sql
-- Delete older duplicates, keep newest
DELETE FROM products
WHERE id NOT IN (
  SELECT MAX(id)
  FROM (
    SELECT MAX(id) as id
    FROM products
    GROUP BY code
  ) t
);
```

#### Find Duplicate BOMs
```sql
-- BOMs with same product but inactive
SELECT product_id, COUNT(*) as count
FROM bom_headers
WHERE is_active = false
GROUP BY product_id
HAVING COUNT(*) > 1;
```

#### Delete Duplicate BOMs
```sql
-- Keep only active BOM per product
DELETE FROM bom_headers
WHERE is_active = false
  AND product_id IN (
    SELECT product_id
    FROM bom_headers
    WHERE is_active = true
  );
```

### Method 3: Clean via CSV Export/Import

```
1. Export current data (see duplicate rows)
2. Open in Excel
3. Use Data → Remove Duplicates
4. Select columns to check (e.g., Product Code)
5. Delete duplicate rows
6. Save cleaned CSV
7. Re-import without duplicates
```

### Method 4: API Delete

```bash
# Delete specific product by ID
curl -X DELETE http://localhost:8000/api/v1/admin/products/123 \
  -H "Authorization: Bearer <admin_token>"

# Response
{
  "status": "success",
  "message": "Product deleted"
}
```

---

## ⚠️ Important Rules & Permissions

### Required Permissions
| Action | Permission Code | Role |
|--------|-----------------|------|
| Import Data | `import_export.import_data` | Admin |
| Export Data | `import_export.export_data` | Admin |
| Create MO | `ppic.create_mo` | PPIC Manager |
| Approve MO | `ppic.approve_mo` | PPIC Manager |
| Delete Data | `admin.delete_data` | Super Admin |
| Manage Users | `admin.manage_users` | Admin |

### Validation Rules

**BOM Import**:
- ✅ All products/components must exist
- ✅ Quantities must be positive
- ✅ No duplicate product+component pairs per BOM
- ✅ Wastage 0-100%

**MO Creation**:
- ✅ Product must be WIP or Finish Good type
- ✅ Batch number must be unique
- ✅ Quantity must be > 0
- ✅ Routing type must be valid (Route 1/2/3)

**User Import**:
- ✅ Email must be unique
- ✅ Username must be unique
- ✅ Role must exist in system

---

## 📋 Error Reference

| Error | Cause | Solution |
|-------|-------|----------|
| "Product not found" | Product code doesn't exist | Create product first |
| "Duplicate entry" | Record already exists | Check for duplicates, delete if needed |
| "Permission denied" | Not authorized | Ask admin for permission |
| "Invalid format" | File not CSV/Excel | Save as CSV or XLSX |
| "Row N: Invalid qty" | Quantity ≤ 0 | Ensure all quantities > 0 |
| "Batch already exists" | MO batch number duplicate | Use unique batch number |

---

## 🎯 Common Workflows

### Workflow 1: Setup New Product

```
Step 1: Import/Create Product
  → Admin → Products → Add product with code, name, type

Step 2: Define BOM
  → Admin → Import/Export → BOM → Upload template
  → Specify all components needed

Step 3: Create Manufacturing Order
  → PPIC → Create MO → Select product, quantity
  → Assign routing (which departments)

Step 4: Approve & Execute
  → PPIC Manager → Approve MO
  → Each department gets work orders
  → Production begins
```

### Workflow 2: Bulk Update Inventory

```
Step 1: Export current stock
  → Admin → Import/Export → Export Stock Data
  → Select Format: CSV

Step 2: Update in Excel
  → Open file, update quantities
  → Save as CSV

Step 3: Re-import
  → Admin → Import/Export → Import → Stock Data
  → Upload updated CSV
  → Review changes
```

### Workflow 3: Find & Fix Duplicates

```
Step 1: Export data type with duplicates
  → Admin → Import/Export → Export

Step 2: Analyze for duplicates
  → Excel: Data → Remove Duplicates
  → Or SQL: GROUP BY with HAVING COUNT > 1

Step 3: Delete duplicates
  → Via API or Database tool
  → Delete by ID, keep newest/active record

Step 4: Verify
  → Re-export to confirm no duplicates
  → Check system functionality
```

---

## 📞 Support

For issues:
1. Check error message above
2. Review validation rules
3. Contact Admin for permissions
4. Check database logs: `System → Logs`

---

**Last Updated**: January 23, 2026  
**Version**: 1.0  
**Status**: Production Ready

