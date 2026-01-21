# 🔐 PHASE 16 WEEK 3: PBAC IMPLEMENTATION PLAN

**Date**: January 21, 2026  
**Phase**: Week 3 of Phase 16 Post-Security Optimizations  
**Methodology**: DeepSeek (Root Cause) + DeepSearch (Inventory) + DeepThink (Strategy)  
**Status**: ⏳ PLANNING PHASE

---

## 📊 PBAC IMPLEMENTATION INVENTORY

### Endpoint Status Analysis (77 Total)

```
┌─────────────────────────────────────────────────────────────┐
│ OVERALL STATUS: 47/77 (61%) Protected | 30/77 (39%) At Risk │
└─────────────────────────────────────────────────────────────┘

TIER 1: FULLY PROTECTED (38 endpoints - 49%)
├── dashboard.py          (6/6)   ✅ COMPLETE
├── purchasing.py         (6/6)   ✅ COMPLETE
├── reports.py            (3/3)   ✅ COMPLETE
├── report_builder.py     (5/5)   ✅ COMPLETE
├── kanban.py             (5/5)   ✅ COMPLETE
├── ppic.py               (4/4)   ✅ COMPLETE
└── import_export.py      (6/6)   ✅ COMPLETE

TIER 2: ROLE-BASED (6 endpoints - 8%)
├── warehouse.py          (3/3)   ⚠️ NEEDS STANDARDIZATION
├── auth.py               (7/7)   ⚠️ PUBLIC ENDPOINTS (EXEMPT)
└── Total: 10 endpoints

TIER 3: UNPROTECTED - CRITICAL (30 endpoints - 39%) 🔴
├── embroidery.py         (6/6)   ❌ PRIORITY HIGH
├── finishgoods.py        (5/5)   ❌ PRIORITY HIGH
├── barcode.py            (4/4)   ❌ PRIORITY CRITICAL
├── audit.py              (7/7)   ❌ PRIORITY CRITICAL
├── admin.py              (7/7)   ❌ PRIORITY CRITICAL
└── Total: 29 endpoints needing immediate PBAC protection
```

---

## 🎯 WEEK 3 IMPLEMENTATION STRATEGY

### Phase 3A: Critical Endpoints (Mon-Tue) - 23 endpoints
1. **admin.py** (7 endpoints) - User management, permissions
   - GET /users
   - GET /users/{user_id}
   - PUT /users/{user_id}
   - POST /users/{user_id}/deactivate
   - POST /users/{user_id}/reactivate
   - POST /users/{user_id}/reset-password
   - GET /users/role/{role_name}
   - GET /environment-info

2. **audit.py** (7 endpoints) - Audit trail access
   - GET /logs (requires audit.view_logs)
   - GET /logs/{log_id}
   - GET /entity/{entity_type}/{entity_id}
   - GET /summary
   - GET /security-logs (CRITICAL - admin only)
   - GET /user-activity/{user_id}
   - GET /export/csv

3. **barcode.py** (4 endpoints) - Critical inventory operations
   - POST /validate
   - POST /receive
   - POST /pick
   - GET /history
   - GET /stats

**Permission Requirements**:
```python
# admin.py
admin.view_users           → GET /users, GET /users/{user_id}
admin.manage_users         → PUT /users/{user_id}
admin.deactivate_user      → POST /deactivate
admin.reactivate_user      → POST /reactivate
admin.reset_password       → POST /reset-password
admin.view_user_roles      → GET /users/role/{role_name}
admin.view_environment     → GET /environment-info

# audit.py
audit.view_logs            → GET /logs, GET /logs/{log_id}
audit.view_entity_logs     → GET /entity/...
audit.view_summary         → GET /summary
audit.view_security_logs   → GET /security-logs (ADMIN ONLY)
audit.view_user_activity   → GET /user-activity/{user_id}
audit.export_logs          → GET /export/csv

# barcode.py
barcode.validate           → POST /validate
barcode.receive_stock      → POST /receive
barcode.pick_stock         → POST /pick
barcode.view_history       → GET /history
barcode.view_stats         → GET /stats
```

### Phase 3B: Production Endpoints (Wed-Thu) - 6 endpoints
1. **embroidery.py** (6 endpoints)
   - GET /work-orders (embroidery.view_orders)
   - POST /work-order/{id}/start (embroidery.start_order)
   - POST /work-order/{id}/record-output (embroidery.record_output)
   - POST /work-order/{id}/complete (embroidery.complete_order)
   - POST /work-order/{id}/transfer (embroidery.transfer_output)
   - GET /line-status (embroidery.view_line_status)

2. **finishgoods.py** (5 endpoints)
   - GET /inventory (finishgoods.view_inventory)
   - POST /receive-from-packing (finishgoods.receive_goods)
   - POST /prepare-shipment (finishgoods.prepare_shipment)
   - POST /ship (finishgoods.execute_shipment)
   - GET /ready-for-shipment (finishgoods.view_ready_shipments)
   - GET /stock-aging (finishgoods.view_aging_analysis)

### Phase 3C: Standardization (Fri) - 3 endpoints
1. **warehouse.py** Standardization
   - Convert from role-based to PBAC permission model
   - GET /inventory → warehouse.view_inventory
   - POST /issue → warehouse.issue_material
   - POST /receive → warehouse.receive_material

---

## 🔧 IMPLEMENTATION STEPS

### Day 1-2: Critical Admin + Audit + Barcode (23 endpoints)

**Step 1: Admin.py PBAC Protection**
```python
# File: app/api/v1/admin.py
from app.core.permissions import require_permission, ModuleName, Permission

@router.get("/users", response_model=List[UserListResponse])
def list_users(
    current_user: User = Depends(require_permission("admin.view_users")),
    # ... rest of parameters
):
    """Protected: Only ADMIN role can view all users"""

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    current_user: User = Depends(require_permission("admin.manage_users")),
    # ... rest of parameters
):
    """Protected: Only ADMIN can modify users"""

# ... similar for all 7 endpoints
```

**Step 2: Audit.py PBAC Protection**
```python
# File: app/api/v1/audit.py
@router.get("/logs", response_model=dict)
def get_audit_logs(
    current_user: User = Depends(require_permission("audit.view_logs")),
    # ... rest of parameters
):
    """Protected: Requires audit.view_logs permission"""

@router.get("/security-logs")
def get_security_logs(
    current_user: User = Depends(require_permission("audit.view_security_logs")),
    # ... rest of parameters
):
    """CRITICAL: Only ADMIN can view security logs"""

# ... similar for all 7 endpoints
```

**Step 3: Barcode.py PBAC Protection**
```python
# File: app/api/v1/barcode.py
@router.post("/validate")
def validate_barcode(
    current_user: User = Depends(require_permission("barcode.validate")),
    # ... rest of parameters
):
    """Protected: Warehouse staff can validate barcodes"""

@router.post("/receive")
def receive_by_barcode(
    current_user: User = Depends(require_permission("barcode.receive_stock")),
    # ... rest of parameters
):
    """Protected: Only warehouse staff can receive stock"""

# ... similar for all 4 endpoints
```

### Day 3-4: Production Endpoints (11 endpoints)

**Step 4: Embroidery.py PBAC Protection**
```python
# File: app/api/v1/embroidery.py
@router.get("/work-orders")
def list_embroidery_orders(
    current_user: User = Depends(require_permission("embroidery.view_orders")),
    # ... rest of parameters
):
    """Protected: Embroidery supervisors can view orders"""

# ... similar for all 6 endpoints
```

**Step 5: Finishgoods.py PBAC Protection**
```python
# File: app/api/v1/finishgoods.py
@router.get("/inventory")
def list_finishgoods_inventory(
    current_user: User = Depends(require_permission("finishgoods.view_inventory")),
    # ... rest of parameters
):
    """Protected: FG warehouse staff can view inventory"""

# ... similar for all 5 endpoints
```

### Day 5: Standardization + Testing

**Step 6: Warehouse.py Standardization**
- Convert 3 endpoints from role-based to PBAC
- Align with other production modules

**Step 7: Comprehensive Testing**
```bash
# Run permission tests for all updated endpoints
pytest tests/pbac/test_admin_endpoints.py -v
pytest tests/pbac/test_audit_endpoints.py -v
pytest tests/pbac/test_barcode_endpoints.py -v
pytest tests/pbac/test_embroidery_endpoints.py -v
pytest tests/pbac/test_finishgoods_endpoints.py -v
pytest tests/pbac/test_warehouse_endpoints.py -v
```

---

## 📋 PERMISSION MATRIX

### Admin Module Permissions
| Endpoint | Operation | Required Permission | Roles |
|----------|-----------|-------------------|-------|
| GET /users | List all users | admin.view_users | ADMIN, SUPERADMIN |
| GET /users/{id} | View user | admin.view_users | ADMIN, SUPERADMIN |
| PUT /users/{id} | Edit user | admin.manage_users | ADMIN, SUPERADMIN |
| POST /deactivate | Deactivate user | admin.deactivate_user | ADMIN, SUPERADMIN |
| POST /reactivate | Reactivate user | admin.reactivate_user | ADMIN, SUPERADMIN |
| POST /reset-password | Reset password | admin.reset_password | ADMIN, SUPERADMIN |
| GET /users/role/{role} | View by role | admin.view_user_roles | ADMIN, SUPERADMIN |
| GET /environment-info | System info | admin.view_environment | ADMIN, SUPERADMIN, IT |

### Audit Module Permissions
| Endpoint | Operation | Required Permission | Roles |
|----------|-----------|-------------------|-------|
| GET /logs | View audit logs | audit.view_logs | ADMIN, FINANCE_MANAGER, AUDIT |
| GET /logs/{id} | View specific log | audit.view_logs | ADMIN, FINANCE_MANAGER, AUDIT |
| GET /entity/{type}/{id} | Entity history | audit.view_entity_logs | ADMIN, FINANCE_MANAGER |
| GET /summary | Audit summary | audit.view_summary | ADMIN, FINANCE_MANAGER, AUDIT |
| GET /security-logs | Security logs | audit.view_security_logs | ADMIN, SUPERADMIN (CRITICAL) |
| GET /user-activity/{id} | User activity | audit.view_user_activity | ADMIN, FINANCE_MANAGER |
| GET /export/csv | Export logs | audit.export_logs | ADMIN, FINANCE_MANAGER |

### Barcode Module Permissions
| Endpoint | Operation | Required Permission | Roles |
|----------|-----------|-------------------|-------|
| POST /validate | Validate barcode | barcode.validate | WAREHOUSE_STAFF, SPV_WAREHOUSE |
| POST /receive | Receive by barcode | barcode.receive_stock | WAREHOUSE_STAFF, SPV_WAREHOUSE |
| POST /pick | Pick stock | barcode.pick_stock | WAREHOUSE_STAFF, SPV_WAREHOUSE |
| GET /history | View scan history | barcode.view_history | WAREHOUSE_STAFF, SPV_WAREHOUSE |
| GET /stats | Barcode statistics | barcode.view_stats | SPV_WAREHOUSE, ADMIN |

---

## ✅ SUCCESS CRITERIA

- ✅ All 30 unprotected endpoints have PBAC decorators
- ✅ Permission matrix defined and implemented
- ✅ No permission conflicts or gaps
- ✅ All tests pass (no regressions)
- ✅ Role-based access properly enforced
- ✅ Audit trail captures permission checks
- ✅ Documentation updated

---

## 🚀 DELIVERABLES (End of Week 3)

**Code Changes**:
- ✅ admin.py - 7 endpoints PBAC protected
- ✅ audit.py - 7 endpoints PBAC protected
- ✅ barcode.py - 4 endpoints PBAC protected
- ✅ embroidery.py - 6 endpoints PBAC protected
- ✅ finishgoods.py - 5 endpoints PBAC protected
- ✅ warehouse.py - 3 endpoints standardized

**Testing**:
- ✅ Permission enforcement tests pass
- ✅ Role-based access validated
- ✅ No regressions (all existing tests pass)
- ✅ Audit logs properly recorded

**Documentation**:
- ✅ Permission matrix documented
- ✅ API endpoints documented with permissions
- ✅ Deployment checklist prepared

---

## 📈 RISK ASSESSMENT

### High Risk (Currently Unprotected)
- 🔴 **CRITICAL**: Admin endpoints (user management)
- 🔴 **CRITICAL**: Audit endpoints (security logs)
- 🔴 **HIGH**: Barcode endpoints (inventory operations)
- 🔴 **HIGH**: Embroidery endpoints (production data)
- 🔴 **HIGH**: Finishgoods endpoints (output shipping)

### Mitigation Strategy
- Daily testing of protected endpoints
- Audit logging of all permission failures
- Role-based access strictly enforced
- Admin endpoints require SoD (Maker-Checker)

---

**Status**: ⏳ READY TO EXECUTE  
**Next Step**: Begin Day 1 - Admin.py PBAC Protection  
**Expected Timeline**: 5 working days  
**Checkpoint**: Daily team sync-ups
