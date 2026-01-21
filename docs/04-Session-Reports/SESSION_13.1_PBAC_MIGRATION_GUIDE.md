# Week 3: PBAC Endpoint Migration Guide

**Session**: 13.1 - Week 3  
**Date**: January 24, 2026  
**Objective**: Migrate 104 endpoints from `require_roles()` to `require_permission()`

---

## 📋 Migration Strategy

### Phase 1: PermissionService Setup ✅ COMPLETE
- ✅ Created `PermissionService` with Redis caching (5-min TTL)
- ✅ Implemented role hierarchy (SPV can perform operator actions)
- ✅ Added `require_permission()` dependency function
- ✅ Added `require_any_permission()` for OR logic

### Phase 2: Permission Code Mapping

**Permission Naming Convention**: `{module}.{action}`

#### Admin Module (13 endpoints)
- `admin.manage_users` - Create/edit/delete user accounts
- `admin.delete_user` - Permanently delete users
- `admin.reset_password` - Reset user passwords
- `admin.assign_roles` - Change user role assignments
- `admin.view_audit_logs` - Access system audit trail
- `admin.manage_masterdata` - Edit products, BOM, categories
- `admin.import_data` - Bulk import via Excel/CSV
- `admin.export_data` - Export data to Excel/CSV

#### Purchasing Module (5 endpoints)
- `purchasing.create_pr` - Create purchase requisitions
- `purchasing.approve_pr` - Approve purchase requests
- `purchasing.create_po` - Create purchase orders
- `purchasing.receive_material` - Record material receipts
- `purchasing.view_suppliers` - View supplier information

#### PPIC Module (4 endpoints)
- `ppic.create_mo` - Create manufacturing orders
- `ppic.schedule_production` - Plan production schedule
- `ppic.allocate_materials` - Assign materials to MO
- `ppic.view_capacity` - View production capacity

#### Cutting Module (8 endpoints)
- `cutting.create_wo` - Create cutting work orders
- `cutting.allocate_material` - Assign fabric to cutting
- `cutting.complete_operation` - Record cutting output
- `cutting.qc_inspection` - Perform QC checks
- `cutting.handle_variance` - Handle shortage/surplus
- `cutting.line_clearance` - Check line availability
- `cutting.create_transfer` - Transfer to next dept
- `cutting.view_status` - View work order status

#### Sewing Module (9 endpoints)
- `sewing.accept_transfer` - Accept WIP from cutting
- `sewing.validate_input` - Validate BOM quantities
- `sewing.process_stage1` - Assembly (rakit body)
- `sewing.process_stage2` - Labeling
- `sewing.process_stage3` - Stik balik (loop stitching)
- `sewing.inline_qc` - Perform inline QC
- `sewing.segregate_defect` - Segregate defective items
- `sewing.create_transfer` - Transfer to finishing
- `sewing.view_status` - View work order status

#### Finishing Module (8 endpoints)
- `finishing.accept_transfer` - Accept WIP from sewing
- `finishing.line_clearance` - Check packing line
- `finishing.perform_stuffing` - Stuffing (isi dacron)
- `finishing.perform_closing` - Closing & grooming
- `finishing.metal_detector_qc` - Metal detector inspection
- `finishing.convert_to_fg` - Convert to finished goods
- `finishing.create_transfer` - Transfer to warehouse
- `finishing.view_status` - View work order status

#### Packing Module (6 endpoints)
- `packing.receive_fg` - Receive finished goods
- `packing.pack_product` - Pack products into cartons
- `packing.label_carton` - Generate carton labels
- `packing.create_shipment` - Create shipping documents
- `packing.load_container` - Record container loading
- `packing.view_status` - View packing status

#### Quality Module (8 endpoints)
- `quality.create_inspection` - Create QC inspection records
- `quality.record_defect` - Record defect findings
- `quality.approve_batch` - Approve production batch
- `quality.reject_batch` - Reject production batch
- `quality.view_reports` - View quality reports
- `quality.export_defects` - Export defect data
- `quality.create_ncr` - Create non-conformance report
- `quality.close_ncr` - Close NCR after correction

#### Warehouse Module (10 endpoints)
- `warehouse.receive_material` - Receive raw materials
- `warehouse.issue_material` - Issue to production
- `warehouse.receive_fg` - Receive finished goods
- `warehouse.ship_fg` - Ship to customer
- `warehouse.adjust_stock` - Stock adjustment
- `warehouse.cycle_count` - Perform cycle counting
- `warehouse.view_inventory` - View inventory levels
- `warehouse.manage_locations` - Manage storage locations
- `warehouse.generate_label` - Generate barcode labels
- `warehouse.view_transactions` - View all transactions

#### Dashboard Module (5 endpoints)
- `dashboard.view_stats` - View dashboard statistics
- `dashboard.view_production` - View production status
- `dashboard.view_alerts` - View system alerts
- `dashboard.view_trends` - View MO trends
- `dashboard.refresh_views` - Manually refresh materialized views (admin only)

#### Report Builder (12 endpoints)
- `reports.create_report` - Create custom reports
- `reports.edit_report` - Edit report definitions
- `reports.delete_report` - Delete reports
- `reports.execute_report` - Run report queries
- `reports.export_excel` - Export to Excel
- `reports.export_pdf` - Export to PDF
- `reports.schedule_report` - Schedule automatic reports
- `reports.view_history` - View report execution history
- `reports.share_report` - Share with other users
- `reports.manage_templates` - Manage report templates
- `reports.create_dashboard` - Create dashboard layouts
- `reports.view_all` - View all reports (admin)

#### Audit Trail (6 endpoints)
- `audit.view_logs` - View audit logs
- `audit.export_logs` - Export audit data
- `audit.filter_by_user` - Filter by user activity
- `audit.filter_by_module` - Filter by module
- `audit.filter_by_date` - Filter by date range
- `audit.view_system_logs` - View system logs (admin)

#### Import/Export (4 endpoints)
- `import_export.import_products` - Import product data
- `import_export.import_bom` - Import BOM data
- `import_export.export_masterdata` - Export master data
- `import_export.export_transactions` - Export transaction data

#### Barcode Module (6 endpoints)
- `barcode.generate_label` - Generate barcode labels
- `barcode.scan_material` - Scan material barcode
- `barcode.scan_product` - Scan product barcode
- `barcode.scan_transfer` - Scan transfer slip
- `barcode.print_batch` - Print batch labels
- `barcode.view_history` - View scan history

---

## 🔄 Migration Process

### Step 1: Update Import Statements

**BEFORE**:
```python
from app.core.dependencies import get_db, require_role
```

**AFTER**:
```python
from app.core.dependencies import get_db, require_permission
```

### Step 2: Replace Decorator

**BEFORE**:
```python
@router.post("/cutting/work-orders")
def create_work_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["SPV Cutting", "Admin"])),
):
    # ... implementation ...
```

**AFTER**:
```python
@router.post("/cutting/work-orders")
def create_work_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("cutting.create_wo")),
):
    # ... implementation ...
```

### Step 3: Test Migration

1. Run migration script to populate permissions table
2. Assign permissions to roles
3. Test endpoint with different user roles
4. Verify role hierarchy (SPV can perform operator actions)
5. Check Redis caching (performance test)

---

## 📊 Migration Tracker

### Admin Module (13 endpoints) - ⏳ PENDING
- [ ] `/admin/users` - POST, PUT, DELETE
- [ ] `/admin/users/{user_id}` - DELETE
- [ ] `/admin/users/{user_id}/reset-password` - POST
- [ ] `/admin/users/{user_id}/assign-role` - PUT
- [ ] `/admin/audit-logs` - GET
- [ ] `/admin/masterdata` - POST, PUT, DELETE
- [ ] `/admin/import` - POST
- [ ] `/admin/export` - GET

### Cutting Module (8 endpoints) - ⏳ PENDING
- [ ] `/cutting/accept-spk` - POST
- [ ] `/cutting/allocate-material` - POST
- [ ] `/cutting/complete-operation` - POST
- [ ] `/cutting/qc-inspection` - POST
- [ ] `/cutting/handle-shortage` - POST
- [ ] `/cutting/line-clearance` - GET
- [ ] `/cutting/transfer` - POST
- [ ] `/cutting/work-orders` - GET

### Sewing Module (9 endpoints) - ⏳ PENDING
- [ ] `/sewing/accept-transfer` - POST
- [ ] `/sewing/validate-input` - POST
- [ ] `/sewing/process-step/{step}` - POST
- [ ] `/sewing/inline-qc` - POST
- [ ] `/sewing/segregate-defect` - POST
- [ ] `/sewing/transfer` - POST
- [ ] `/sewing/work-orders` - GET

### Finishing Module (8 endpoints) - ⏳ PENDING
- [ ] `/finishing/accept-transfer` - POST
- [ ] `/finishing/line-clearance` - GET
- [ ] `/finishing/stuffing` - POST
- [ ] `/finishing/closing` - POST
- [ ] `/finishing/metal-detector-qc` - POST
- [ ] `/finishing/convert-to-fg` - POST
- [ ] `/finishing/transfer` - POST
- [ ] `/finishing/work-orders` - GET

### Dashboard Module (5 endpoints) - ⏳ PENDING
- [ ] `/dashboard/stats` - GET
- [ ] `/dashboard/production-status` - GET
- [ ] `/dashboard/alerts` - GET
- [ ] `/dashboard/mo-trends` - GET
- [ ] `/dashboard/refresh-views` - POST

**Total Progress**: 0/104 endpoints migrated (0%)

---

## ✅ Testing Checklist

### Unit Tests
- [ ] Test PermissionService.has_permission()
- [ ] Test PermissionService.has_any_permission()
- [ ] Test role hierarchy (SPV inherits operator permissions)
- [ ] Test Redis caching (hit/miss scenarios)
- [ ] Test cache invalidation

### Integration Tests
- [ ] Test require_permission() dependency
- [ ] Test 403 Forbidden responses for unauthorized access
- [ ] Test SUPERADMIN has all permissions
- [ ] Test custom user permissions (temporary elevated access)
- [ ] Test permission expiration

### Performance Tests
- [ ] Benchmark permission check latency (<10ms with cache)
- [ ] Load test with 1000 concurrent requests
- [ ] Verify Redis cache TTL (5 minutes)
- [ ] Test cache invalidation on permission changes

---

## 🚀 Rollout Plan

### Week 3 - Day 1: Infrastructure ✅ COMPLETE
- ✅ Create PermissionService with Redis caching
- ✅ Add require_permission() dependency
- ✅ Document permission codes

### Week 3 - Day 2: High-Priority Modules (30 endpoints)
- ⏳ Migrate Admin module (13 endpoints)
- ⏳ Migrate Dashboard module (5 endpoints)
- ⏳ Migrate Cutting module (8 endpoints)
- ⏳ Migrate PPIC module (4 endpoints)

### Week 3 - Day 3: Production Modules (23 endpoints)
- ⏳ Migrate Sewing module (9 endpoints)
- ⏳ Migrate Finishing module (8 endpoints)
- ⏳ Migrate Packing module (6 endpoints)

### Week 3 - Day 4: Supporting Modules (35 endpoints)
- ⏳ Migrate Quality module (8 endpoints)
- ⏳ Migrate Warehouse module (10 endpoints)
- ⏳ Migrate Report Builder (12 endpoints)
- ⏳ Migrate Barcode module (6 endpoints)

### Week 3 - Day 5: Audit & Import/Export (16 endpoints)
- ⏳ Migrate Audit Trail (6 endpoints)
- ⏳ Migrate Import/Export (4 endpoints)
- ⏳ Migrate Purchasing (5 endpoints)
- ⏳ Final testing + documentation

---

## 📝 Notes

### Role Hierarchy Rules
- **SUPERADMIN**: Has ALL permissions (bypass check)
- **ADMIN**: Has most permissions (except developer tools)
- **SPV Cutting**: Can perform all Cutting operations (including operator tasks)
- **SPV Sewing**: Can perform all Sewing operations
- **SPV Finishing**: Can perform all Finishing operations
- **SPV Packing**: Can perform all Packing operations
- **Operators**: Limited to specific department operations only

### Redis Caching Strategy
- **Cache Key**: `pbac:user:{user_id}:perm:{permission_code}`
- **TTL**: 5 minutes (300 seconds)
- **Invalidation**: Manual via `PermissionService.invalidate_user_cache(user_id)`
- **Cache Miss**: Query database, then store result

### Custom Permissions
- Temporary elevated access for specific users
- Expiration date support (`expires_at` column)
- Useful for: Vacation coverage, emergency access, training

---

**Last Updated**: January 24, 2026  
**Next Steps**: Begin Day 2 migration (Admin + Dashboard + Cutting + PPIC modules)
