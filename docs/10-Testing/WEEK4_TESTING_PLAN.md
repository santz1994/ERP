# Week 4 Testing & Deployment Plan
**Phase 16 - Post-Security Optimizations**  
**Date:** January 21, 2026  
**Status:** 🚀 Ready to Execute

---

## Overview

With **80+ core production endpoints** successfully migrated to PBAC, Week 4 focuses on comprehensive testing, UI development, and staging deployment preparation.

---

## Testing Strategy (Days 1-3)

### 1. PermissionService Unit Tests (Day 1)

**File:** `tests/test_permission_service.py`

**Test Cases:**
```python
class TestPermissionService:
    def test_has_permission_direct(self):
        """Test user with direct permission"""
        # Setup: User with cutting.allocate_material permission
        # Assert: has_permission returns True
        
    def test_has_permission_via_role(self):
        """Test user with permission via role"""
        # Setup: Operator role with cutting.complete_operation
        # Assert: has_permission returns True
        
    def test_has_permission_role_hierarchy(self):
        """Test SPV inherits operator permissions"""
        # Setup: SPV Cutting user
        # Assert: Has both SPV and Operator permissions
        
    def test_has_permission_custom_expiration(self):
        """Test custom permission with expiration"""
        # Setup: User with temp permission (expires tomorrow)
        # Assert: Permission valid today, invalid after expiration
        
    def test_redis_cache_hit(self):
        """Test Redis caching works"""
        # Setup: Permission check (cold cache)
        # Action: Second check (hot cache)
        # Assert: Second check <1ms
        
    def test_cache_invalidation(self):
        """Test cache invalidates on permission change"""
        # Setup: Cached permission
        # Action: Revoke permission
        # Assert: Cache cleared, returns False
```

**Expected Results:**
- All tests pass
- Redis cache hit rate >99%
- Permission checks <10ms (cold), <1ms (hot)

---

### 2. Endpoint Integration Tests (Day 2)

**File:** `tests/test_pbac_endpoints.py`

**Test Cases by Module:**

#### Dashboard Module
```python
def test_dashboard_stats_with_permission():
    """Test /stats endpoint with dashboard.view_stats permission"""
    # Arrange: User with dashboard.view_stats
    # Act: GET /api/v1/dashboard/stats
    # Assert: 200 OK with stats data
    
def test_dashboard_stats_without_permission():
    """Test /stats endpoint without permission"""
    # Arrange: User without dashboard.view_stats
    # Act: GET /api/v1/dashboard/stats
    # Assert: 403 Forbidden
```

#### Cutting Module
```python
def test_cutting_allocate_material_authorized():
    """Test SPK receive with cutting.allocate_material"""
    # Arrange: User with permission
    # Act: POST /production/cutting/spk/receive
    # Assert: 200 OK, material allocated
    
def test_cutting_allocate_material_unauthorized():
    """Test SPK receive without permission"""
    # Arrange: User without permission
    # Act: POST /production/cutting/spk/receive
    # Assert: 403 Forbidden
```

#### Sewing Module
```python
def test_sewing_inline_qc_qc_inspector():
    """Test inline QC with QC Inspector role"""
    # Arrange: QC Inspector user
    # Act: POST /production/sewing/qc-inspect
    # Assert: 200 OK, QC recorded
    
def test_sewing_inline_qc_operator_denied():
    """Test inline QC with Operator role (should fail)"""
    # Arrange: Operator Sewing user (no QC permission)
    # Act: POST /production/sewing/qc-inspect
    # Assert: 403 Forbidden
```

#### Finishing Module
```python
def test_finishing_metal_detector_authorized():
    """Test metal detector QC (IKEA ISO 8124 compliance)"""
    # Arrange: QC Inspector with finishing.metal_detector_qc
    # Act: POST /production/finishing/metal-detector-test
    # Assert: 200 OK, test recorded
    
def test_finishing_convert_to_fg_spv_only():
    """Test FG conversion restricted to SPV"""
    # Arrange: Operator user (no finishing.convert_to_fg)
    # Act: POST /production/finishing/convert-to-fg
    # Assert: 403 Forbidden
```

#### Packing Module
```python
def test_packing_shipping_mark_spv_only():
    """Test shipping mark generation (SPV only)"""
    # Arrange: SPV Packing user
    # Act: POST /production/packing/shipping-mark
    # Assert: 200 OK, mark generated
```

#### PPIC Module
```python
def test_ppic_create_mo_authorized():
    """Test MO creation with ppic.create_mo"""
    # Arrange: PPIC Manager user
    # Act: POST /ppic/manufacturing-order
    # Assert: 201 Created
    
def test_ppic_approve_mo_authorized():
    """Test MO approval with ppic.approve_mo"""
    # Arrange: PPIC Manager user
    # Act: POST /ppic/manufacturing-order/{id}/approve
    # Assert: 200 OK, MO approved
```

#### Admin Module
```python
def test_admin_manage_users_authorized():
    """Test user management with admin.manage_users"""
    # Arrange: Admin user
    # Act: PUT /admin/users/{id}
    # Assert: 200 OK, user updated
    
def test_admin_manage_users_unauthorized():
    """Test user management without permission"""
    # Arrange: Regular user (no admin permission)
    # Act: PUT /admin/users/{id}
    # Assert: 403 Forbidden
```

#### Import/Export Module
```python
def test_import_products_authorized():
    """Test product import with import_export.import_data"""
    # Arrange: Data Admin user
    # Act: POST /import-export/import/products
    # Assert: 200 OK, products imported
    
def test_export_without_import_permission():
    """Test export without import permission"""
    # Arrange: User with import_export.export_data only
    # Act: POST /import-export/import/products
    # Assert: 403 Forbidden
```

**Expected Results:**
- All authorized requests return 200/201
- All unauthorized requests return 403
- No 500 Internal Server Errors
- Response times <100ms for simple endpoints

---

### 3. Performance Tests (Day 2-3)

**File:** `tests/test_pbac_performance.py`

**Test Scenarios:**

#### Redis Cache Performance
```python
def test_permission_check_performance_cold_cache():
    """Test permission check with cold Redis cache"""
    # Action: Clear Redis, check permission
    # Assert: Response time <10ms
    
def test_permission_check_performance_hot_cache():
    """Test permission check with hot Redis cache"""
    # Action: Check same permission twice
    # Assert: Second check <1ms (from cache)
    
def test_cache_hit_rate_under_load():
    """Test cache hit rate with 1000 requests"""
    # Action: 1000 permission checks
    # Assert: Cache hit rate >99%
```

#### Concurrent Request Performance
```python
def test_concurrent_permission_checks():
    """Test 100 concurrent permission checks"""
    # Action: 100 parallel requests to different endpoints
    # Assert: All complete within 2 seconds
    # Assert: No cache stampede issues
```

#### Dashboard Performance (Materialized Views)
```python
def test_dashboard_stats_performance():
    """Test dashboard /stats endpoint performance"""
    # Action: GET /api/v1/dashboard/stats
    # Assert: Response time <200ms (was 2-5s before optimization)
    
def test_dashboard_production_status_performance():
    """Test production status endpoint performance"""
    # Action: GET /api/v1/dashboard/production-status
    # Assert: Response time <300ms
```

**Expected Results:**
- Permission checks <10ms (cold cache)
- Permission checks <1ms (hot cache)
- Cache hit rate >99%
- Dashboard queries <200ms (40-100x faster than before)
- No Redis connection failures
- No cache stampede issues

---

### 4. Security Tests (Day 3)

**File:** `tests/test_pbac_security.py`

**Test Scenarios:**

#### Permission Bypass Attempts
```python
def test_cannot_bypass_with_invalid_token():
    """Test permission check with invalid JWT"""
    # Action: Request with invalid/expired token
    # Assert: 401 Unauthorized (not 403)
    
def test_cannot_bypass_with_manipulated_token():
    """Test permission check with manipulated token payload"""
    # Action: Request with token modified to add permissions
    # Assert: 401 Unauthorized (signature invalid)
```

#### Role Escalation Prevention
```python
def test_operator_cannot_access_spv_endpoints():
    """Test operator cannot access SPV-only endpoints"""
    # Arrange: Operator Cutting user
    # Act: POST /production/cutting/line-clear (SPV only)
    # Assert: 403 Forbidden
    
def test_qc_inspector_cannot_perform_production():
    """Test QC Inspector cannot perform production ops"""
    # Arrange: QC Inspector user
    # Act: POST /production/cutting/complete (Operator permission)
    # Assert: 403 Forbidden
```

#### Custom Permission Expiration
```python
def test_expired_custom_permission_denied():
    """Test expired custom permission returns 403"""
    # Arrange: User with expired custom permission
    # Act: Request endpoint requiring that permission
    # Assert: 403 Forbidden
    
def test_custom_permission_revocation():
    """Test revoked custom permission immediately denied"""
    # Arrange: User with custom permission
    # Action: Revoke permission, invalidate cache
    # Assert: Next request returns 403
```

#### Audit Trail
```python
def test_permission_denied_logged():
    """Test 403 Forbidden events are logged"""
    # Action: Unauthorized request
    # Assert: Security log entry created with user, endpoint, timestamp
```

**Expected Results:**
- No permission bypass vulnerabilities
- No role escalation possible
- Expired permissions immediately denied
- All security events logged
- ISO 27001 A.9.2.3 compliance (authorization controls)

---

## Permission Management UI (Days 4-5)

### Feature Requirements

#### 1. Permission Assignment Interface
**Route:** `/admin/permissions`

**Features:**
- Search users by username, email, role
- View effective permissions for selected user
- Assign/revoke permissions to users
- Assign/revoke permissions to roles
- Bulk permission assignment

**Wireframe:**
```
┌─────────────────────────────────────────────────┐
│ Permission Management                            │
├─────────────────────────────────────────────────┤
│ Search: [___________________] [Search]          │
├─────────────────────────────────────────────────┤
│ Users                    │ Effective Permissions │
│ ┌───────────────────────┼─────────────────────┐ │
│ │ john.doe@example.com  │ ✅ cutting.allocate  │ │
│ │ Role: Operator_Cutting│ ✅ cutting.complete  │ │
│ │                       │ ✅ cutting.view      │ │
│ │                       │ ❌ cutting.variance  │ │
│ │                       │                      │ │
│ │ [View Details]        │ [+ Add Permission]   │ │
│ └───────────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────┘
```

#### 2. Role Permissions Manager
**Route:** `/admin/roles/permissions`

**Features:**
- List all roles
- View permissions for each role
- Add/remove permissions from role
- See which users have the role

#### 3. Audit Log Viewer
**Route:** `/admin/permissions/audit`

**Features:**
- View permission changes (granted/revoked)
- Filter by user, date range, action
- Export audit log to CSV
- Real-time security alerts

#### 4. Custom Permission Creator
**Route:** `/admin/permissions/custom`

**Features:**
- Create temporary permission with expiration date
- Assign to specific user
- Set reason/justification
- Email notification to user

---

## Staging Deployment (Days 6-7)

### Pre-Deployment Checklist

#### Database Migration
```bash
# 1. Backup production database
pg_dump erp_production > backup_pre_pbac.sql

# 2. Run migration script on staging
python scripts/migrate_rbac_to_pbac.py --environment=staging

# 3. Verify migration
python scripts/migrate_rbac_to_pbac.py --verify-only

# 4. Seed permissions
python scripts/seed_permissions.py --environment=staging
```

#### Redis Configuration
```bash
# 1. Verify Redis connectivity
redis-cli ping

# 2. Set Redis memory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 3. Test permission caching
python tests/test_redis_cache.py
```

#### Environment Variables
```bash
# Update .env.staging
SECRET_KEY=<new_key>
OLD_SECRET_KEY=<current_key>
REDIS_URL=redis://localhost:6379/1
PBAC_CACHE_TTL=300  # 5 minutes
```

### 48-Hour Staging Validation

#### Day 1: Functional Testing
- ✅ All endpoints return correct responses
- ✅ Permissions enforced correctly
- ✅ No 500 errors
- ✅ Redis cache working

#### Day 2: Performance Testing
- ✅ Dashboard <200ms
- ✅ Permission checks <10ms
- ✅ No memory leaks
- ✅ Cache hit rate >99%

#### Security Audit
- ✅ No permission bypasses
- ✅ All security events logged
- ✅ ISO 27001 compliance
- ✅ Penetration testing passed

### Production Rollout Plan

#### Blue-Green Deployment
```bash
# 1. Deploy new version to Green environment
docker-compose -f docker-compose.production-green.yml up -d

# 2. Run database migration
python scripts/migrate_rbac_to_pbac.py --environment=production

# 3. Warm up Redis cache
python scripts/warm_cache.py

# 4. Switch traffic to Green
# Update nginx.conf to route to green

# 5. Monitor for 1 hour
# Watch metrics: error rate, response times, cache hit rate

# 6. If stable, decomission Blue
# If issues, rollback to Blue
python scripts/rollback_pbac.sh
```

---

## Success Criteria

### Performance Targets
- ✅ Permission checks <10ms (cold cache)
- ✅ Permission checks <1ms (hot cache)
- ✅ Dashboard queries <200ms
- ✅ Redis cache hit rate >99%
- ✅ Zero downtime deployment

### Security Targets
- ✅ No permission bypass vulnerabilities
- ✅ All 403 events logged
- ✅ ISO 27001 A.9.2.3 compliance
- ✅ Custom permissions with expiration working

### Functional Targets
- ✅ 100% endpoint coverage (80+ endpoints)
- ✅ Zero API contract changes
- ✅ Backward compatibility maintained
- ✅ All tests passing (unit + integration)

### Documentation Targets
- ✅ API documentation updated
- ✅ Permission code reference published
- ✅ Admin guide for permission management
- ✅ Troubleshooting guide
- ✅ Rollback procedures documented

---

## Risk Mitigation

### Risk: Redis Failure
**Mitigation:** Fallback to database permission check if Redis unavailable

### Risk: Performance Degradation
**Mitigation:** Increase Redis cache TTL, add more Redis instances

### Risk: Permission Misconfiguration
**Mitigation:** Comprehensive testing, rollback plan ready

### Risk: User Lockout
**Mitigation:** Superadmin always has all permissions, emergency access script

---

## Timeline

| Day | Activity | Owner | Status |
|-----|----------|-------|--------|
| 1 | PermissionService unit tests | Dev Team | Pending |
| 2 | Endpoint integration tests | Dev Team | Pending |
| 3 | Performance & security tests | Dev Team | Pending |
| 4-5 | Permission Management UI | Frontend Team | Pending |
| 6-7 | Staging deployment & validation | DevOps + QA | Pending |

**Target Completion:** January 28, 2026 (7 days from now)

---

## Next Immediate Actions

1. ✅ **Create test file structure**
   ```bash
   mkdir -p tests/pbac
   touch tests/pbac/test_permission_service.py
   touch tests/pbac/test_endpoints.py
   touch tests/pbac/test_performance.py
   touch tests/pbac/test_security.py
   ```

2. ✅ **Setup pytest configuration**
   ```ini
   # pytest.ini
   [pytest]
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   markers =
       pbac: Permission-based access control tests
       performance: Performance tests
       security: Security tests
   ```

3. ✅ **Create Redis test utilities**
   ```python
   # tests/pbac/conftest.py
   import pytest
   import redis
   
   @pytest.fixture
   def redis_client():
       client = redis.Redis(host='localhost', port=6379, db=1)
       yield client
       client.flushdb()  # Clean up after tests
   ```

---

**Status:** 🚀 **READY TO START WEEK 4 TESTING**
