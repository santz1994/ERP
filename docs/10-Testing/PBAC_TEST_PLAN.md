# PBAC System - Comprehensive Test Plan
## Phase 16 Week 4 Day 4 | Testing & Validation

**Date:** 2026-01-21  
**Version:** 1.0  
**Status:** 🟡 Testing In Progress  
**Tester:** Development Team  

---

## 📋 Test Overview

### Objectives
1. Verify all permission checks function correctly
2. Test permission inheritance (SPV inherits Operator permissions)
3. Validate custom permission grant/revoke flows
4. Test expiration date logic
5. Measure permission check performance
6. Identify and document bugs
7. Ensure security compliance

### Scope
- **Frontend Pages:** 6 pages (Dashboard, Cutting, Sewing, Finishing, Packing, PPIC, AdminUser, PermissionManagement)
- **Permission Codes:** 36 codes across 10 modules
- **User Roles:** 17 roles (focus on 6 primary roles)
- **Test Duration:** 8 hours (Day 4)

---

## 👥 Test User Accounts

### Required Test Users

```sql
-- Test users to be created via seed script
INSERT INTO users (username, email, password_hash, role, department, is_active) VALUES
('admin_test', 'admin@test.com', '[hashed]', 'ADMIN', 'Admin', true),
('manager_test', 'manager@test.com', '[hashed]', 'MANAGER', 'PPIC', true),
('cutting_op_test', 'cutting_op@test.com', '[hashed]', 'OPERATOR', 'Cutting', true),
('cutting_spv_test', 'cutting_spv@test.com', '[hashed]', 'SPV_CUTTING', 'Cutting', true),
('sewing_op_test', 'sewing_op@test.com', '[hashed]', 'OPERATOR_SEWING', 'Sewing', true),
('sewing_spv_test', 'sewing_spv@test.com', '[hashed]', 'SPV_SEWING', 'Sewing', true),
('qc_inspector_test', 'qc@test.com', '[hashed]', 'QC_INSPECTOR', 'QC', true),
('ppic_manager_test', 'ppic_mgr@test.com', '[hashed]', 'PPIC_MANAGER', 'PPIC', true),
('no_perms_test', 'none@test.com', '[hashed]', 'CUSTOM_ROLE', 'Test', true); -- Zero permissions
```

### Test User Matrix

| Username | Role | Department | Expected Permissions | Purpose |
|----------|------|------------|---------------------|---------|
| admin_test | ADMIN | Admin | All 36 permissions | Test full access |
| manager_test | MANAGER | PPIC | View-only permissions | Test read-only access |
| cutting_op_test | OPERATOR | Cutting | cutting.* (6 perms) | Test department-specific |
| cutting_spv_test | SPV_CUTTING | Cutting | cutting.* + operator perms | Test inheritance |
| sewing_op_test | OPERATOR_SEWING | Sewing | sewing.* (6 perms) | Test sewing access |
| sewing_spv_test | SPV_SEWING | Sewing | sewing.* + operator perms | Test SPV inheritance |
| qc_inspector_test | QC_INSPECTOR | QC | qc.*, sewing.inline_qc | Test QC-specific perms |
| ppic_manager_test | PPIC_MANAGER | PPIC | ppic.* (4 perms) | Test MO approval |
| no_perms_test | CUSTOM_ROLE | Test | None | Test zero permissions |

---

## 🧪 Test Scenarios

### Test Suite 1: Permission Store & Hooks (2 hours)

#### TC-001: Permission Load on Login
**Priority:** HIGH  
**User:** admin_test  
**Steps:**
1. Clear browser localStorage
2. Navigate to `/login`
3. Login with admin_test credentials
4. Open browser DevTools → Application → Local Storage
5. Check for `permission-store` key

**Expected Results:**
- ✅ Permission store populated with 36 permission codes
- ✅ `hasLoadedPermissions` flag = true
- ✅ Permissions loaded within <100ms
- ✅ Console shows: "Permissions loaded: 36"

**Actual Results:**
- [ ] PASS / [ ] FAIL
- Actual permission count: _____
- Load time: _____ ms
- Notes: ___________

---

#### TC-002: Permission Check - Single Permission
**Priority:** HIGH  
**User:** cutting_op_test  
**Steps:**
1. Login as cutting_op_test
2. Navigate to `/cutting`
3. Open browser console
4. Run: `usePermissionStore.getState().hasPermission('cutting.allocate_material')`

**Expected Results:**
- ✅ Returns `true` (user has permission)
- ✅ Check completes in <1ms

**Test Variations:**
- Check valid permission: `cutting.allocate_material` → true
- Check invalid permission: `sewing.inline_qc` → false
- Check non-existent permission: `invalid.permission` → false

**Actual Results:**
- Valid permission: [ ] PASS / [ ] FAIL (Result: _____)
- Invalid permission: [ ] PASS / [ ] FAIL (Result: _____)
- Non-existent: [ ] PASS / [ ] FAIL (Result: _____)
- Performance: _____ ms

---

#### TC-003: Permission Check - Multiple Permissions (OR logic)
**Priority:** MEDIUM  
**User:** cutting_op_test  
**Steps:**
1. Login as cutting_op_test
2. Use hook: `useAnyPermission(['cutting.view_status', 'sewing.view_status'])`

**Expected Results:**
- ✅ Returns `true` (has cutting.view_status)
- ✅ OR logic: Returns true if user has ANY of the permissions

**Test Cases:**
```typescript
useAnyPermission(['cutting.view_status', 'sewing.view_status']) → true (has first)
useAnyPermission(['sewing.view_status', 'finishing.view_status']) → false (has neither)
useAnyPermission(['cutting.allocate_material', 'cutting.complete_operation']) → true (has both)
```

**Actual Results:**
- Test 1: [ ] PASS / [ ] FAIL (Expected: true, Got: _____)
- Test 2: [ ] PASS / [ ] FAIL (Expected: false, Got: _____)
- Test 3: [ ] PASS / [ ] FAIL (Expected: true, Got: _____)

---

#### TC-004: Permission Check - Multiple Permissions (AND logic)
**Priority:** MEDIUM  
**User:** cutting_op_test  
**Steps:**
1. Use hook: `useAllPermissions(['cutting.view_status', 'cutting.allocate_material'])`

**Expected Results:**
- ✅ Returns `true` (has both permissions)
- ✅ AND logic: Returns true only if user has ALL permissions

**Test Cases:**
```typescript
useAllPermissions(['cutting.view_status', 'cutting.allocate_material']) → true (has both)
useAllPermissions(['cutting.view_status', 'sewing.view_status']) → false (missing second)
```

**Actual Results:**
- Test 1: [ ] PASS / [ ] FAIL (Result: _____)
- Test 2: [ ] PASS / [ ] FAIL (Result: _____)

---

#### TC-005: Module Permissions
**Priority:** LOW  
**User:** cutting_op_test  
**Steps:**
1. Use hook: `useModulePermissions('cutting')`

**Expected Results:**
- ✅ Returns array of 6 cutting permissions
- ✅ Format: ['cutting.view_status', 'cutting.allocate_material', ...]

**Actual Results:**
- [ ] PASS / [ ] FAIL
- Permission count: _____
- Permissions: ___________

---

### Test Suite 2: UI Rendering by Role (3 hours)

#### TC-101: Cutting Page - Operator View
**Priority:** HIGH  
**User:** cutting_op_test  
**Page:** `/cutting`  

**Expected UI Elements:**
| Element | Permission | Should Show |
|---------|------------|-------------|
| Work order table | cutting.view_status | ✅ Yes |
| "Start Cutting" button | cutting.allocate_material | ✅ Yes |
| "Complete" button | cutting.complete_operation | ✅ Yes |
| "Handle Shortage" button | cutting.handle_variance | ✅ Yes |
| "Line Clearance" button | cutting.line_clearance | ✅ Yes |
| "Transfer to Next" button | cutting.create_transfer | ✅ Yes |

**Actual Results:**
- Work order table: [ ] Visible / [ ] Hidden
- Start Cutting: [ ] Visible / [ ] Hidden / [ ] Lock Icon
- Complete: [ ] Visible / [ ] Hidden / [ ] Lock Icon
- Handle Shortage: [ ] Visible / [ ] Hidden / [ ] Lock Icon
- Line Clearance: [ ] Visible / [ ] Hidden / [ ] Lock Icon
- Transfer: [ ] Visible / [ ] Hidden / [ ] Lock Icon
- Screenshot: _____

---

#### TC-102: Cutting Page - No Permission View
**Priority:** HIGH  
**User:** sewing_op_test (no cutting permissions)  
**Page:** `/cutting`  

**Expected UI Elements:**
| Element | Should Show |
|---------|-------------|
| Work order table | ✅ Yes (read-only) |
| All action buttons | ❌ No (Lock icons instead) |

**Expected Lock Badge:**
```html
<div class="text-gray-400">
  <Lock className="w-3 h-3" />
  No Permission
</div>
```

**Actual Results:**
- Work order table: [ ] Visible / [ ] Hidden
- Action buttons: [ ] Visible / [ ] Hidden / [ ] Lock Icons ✅
- Lock badge shown: [ ] Yes / [ ] No
- Screenshot: _____

---

#### TC-103: Sewing Page - QC Inspector
**Priority:** HIGH  
**User:** qc_inspector_test  
**Page:** `/sewing`  

**Special Case:** QC Inspector should ONLY see QC-related button

**Expected UI Elements:**
| Element | Permission | Should Show |
|---------|------------|-------------|
| "Start Sewing" button | sewing.accept_transfer | ❌ No (Lock) |
| "QC Inspection" button | sewing.inline_qc | ✅ Yes (Inspector Only) |
| "Transfer to Finishing" button | sewing.create_transfer | ❌ No (Lock) |

**Actual Results:**
- Start Sewing: [ ] Visible / [ ] Hidden ✅ / [ ] Lock ✅
- QC Inspection: [ ] Visible ✅ / [ ] Hidden
- Button label includes "(Inspector Only)": [ ] Yes / [ ] No
- Transfer: [ ] Visible / [ ] Hidden ✅ / [ ] Lock ✅
- Screenshot: _____

---

#### TC-104: PPIC Page - Manager Approval
**Priority:** HIGH  
**User:** ppic_manager_test  
**Page:** `/ppic`  

**Expected UI Elements:**
| Element | Permission | Should Show |
|---------|------------|-------------|
| View MO list | ppic.view_mo | ✅ Yes |
| "Create MO" button | ppic.create_mo | ✅ Yes |
| "Schedule Production" | ppic.schedule_production | ✅ Yes |
| "Approve MO" button | ppic.approve_mo | ✅ Yes (Manager Only) |

**Actual Results:**
- View MO: [ ] Visible / [ ] Hidden
- Create MO: [ ] Visible / [ ] Hidden / [ ] Lock
- Schedule: [ ] Visible / [ ] Hidden / [ ] Lock
- Approve (Manager): [ ] Visible ✅ / [ ] Hidden / [ ] Lock
- Screenshot: _____

---

#### TC-105: Admin User Page - Admin View
**Priority:** HIGH  
**User:** admin_test  
**Page:** `/admin/users`  

**Expected UI Elements:**
| Element | Permission | Should Show |
|---------|------------|-------------|
| User table | (public) | ✅ Yes |
| "+ Create User" button | admin.manage_users | ✅ Yes |
| "Edit" button (per row) | admin.manage_users | ✅ Yes |
| "Deactivate" button | admin.manage_users | ✅ Yes |
| "Reset Password" button | admin.manage_users | ✅ Yes |

**Actual Results:**
- User table: [ ] Visible / [ ] Hidden
- Create User button: [ ] Visible / [ ] "Admin Only" badge
- Edit buttons: [ ] Visible / [ ] "View Only" label
- Deactivate buttons: [ ] Visible / [ ] "View Only" label
- Reset Pwd buttons: [ ] Visible / [ ] "View Only" label
- Screenshot: _____

---

#### TC-106: Admin User Page - Non-Admin View
**Priority:** HIGH  
**User:** cutting_op_test  
**Page:** `/admin/users`  

**Expected Behavior:**
- Cannot access page (redirected to `/unauthorized`)
- OR: Shows "View Only" for all action buttons
- Lock icons instead of functional buttons

**Actual Results:**
- [ ] Redirected to /unauthorized
- [ ] Stayed on page with View Only mode
- User table visible: [ ] Yes / [ ] No
- Action buttons: [ ] Visible / [ ] "View Only" labels ✅ / [ ] Hidden
- Screenshot: _____

---

#### TC-107: Permission Management Page - Admin View
**Priority:** HIGH  
**User:** admin_test  
**Page:** `/admin/permissions`  

**Expected UI Elements:**
| Element | Permission | Should Show |
|---------|------------|-------------|
| User list (left panel) | admin.view_system_info | ✅ Yes |
| Permission details | admin.view_system_info | ✅ Yes |
| Statistics cards | admin.view_system_info | ✅ Yes |
| "+ Grant Permission" button | admin.manage_users | ✅ Yes |
| Revoke buttons (X) | admin.manage_users | ✅ Yes |

**Actual Results:**
- User list: [ ] Visible / [ ] Hidden
- Permission details: [ ] Visible / [ ] Hidden
- Statistics: [ ] Visible / [ ] Hidden
- Grant button: [ ] Visible / [ ] Hidden
- Revoke buttons: [ ] Visible / [ ] Hidden
- Screenshot: _____

---

#### TC-108: Permission Management Page - View-Only
**Priority:** HIGH  
**User:** manager_test (has admin.view_system_info, NO admin.manage_users)  
**Page:** `/admin/permissions`  

**Expected UI Elements:**
| Element | Should Show |
|---------|-------------|
| User list | ✅ Yes |
| Permission details | ✅ Yes |
| Statistics cards | ✅ Yes |
| "+ Grant Permission" button | ❌ No (hidden) |
| Revoke buttons (X) | ❌ No (hidden) |

**Actual Results:**
- User list: [ ] Visible / [ ] Hidden
- Permission details: [ ] Visible / [ ] Hidden
- Statistics: [ ] Visible / [ ] Hidden
- Grant button: [ ] Visible ❌ / [ ] Hidden ✅
- Revoke buttons: [ ] Visible ❌ / [ ] Hidden ✅
- Screenshot: _____

---

#### TC-109: Permission Management Page - Access Denied
**Priority:** HIGH  
**User:** cutting_op_test (NO admin.view_system_info)  
**Page:** `/admin/permissions`  

**Expected UI:**
```html
<div class="bg-red-50 border border-red-200">
  <Lock icon />
  <h2>Access Denied</h2>
  <p>You don't have permission to view user permissions.</p>
  <p>Required: admin.view_system_info</p>
</div>
```

**Actual Results:**
- [ ] Shows "Access Denied" page ✅
- [ ] Redirected to /unauthorized
- [ ] Shows regular page (BUG)
- Lock icon displayed: [ ] Yes / [ ] No
- Required permission shown: [ ] Yes / [ ] No
- Screenshot: _____

---

### Test Suite 3: Permission Management Operations (2 hours)

#### TC-201: Grant Custom Permission (No Expiration)
**Priority:** HIGH  
**Granter:** admin_test  
**Grantee:** cutting_op_test  
**Permission:** `sewing.inline_qc`  

**Steps:**
1. Login as admin_test
2. Navigate to `/admin/permissions`
3. Search for "cutting_op_test"
4. Click on user
5. Click "+ Grant Permission"
6. Select permission: `sewing.inline_qc`
7. Leave expiration empty
8. Click "Grant"

**Expected Results:**
- ✅ Modal closes
- ✅ Success message shown
- ✅ Custom Permissions section shows new green badge
- ✅ Badge shows "CUSTOM" label
- ✅ Shows "Granted by: admin_test"
- ✅ Shows timestamp
- ✅ NO expiration date shown

**API Call:**
```http
POST /admin/users/3/permissions
{
  "permission_code": "sewing.inline_qc",
  "expires_at": null
}
```

**Actual Results:**
- Modal closed: [ ] Yes / [ ] No
- Success message: [ ] Yes / [ ] No (Message: _____)
- Badge appeared: [ ] Yes / [ ] No
- CUSTOM label: [ ] Yes / [ ] No
- Granted by shown: [ ] Yes / [ ] No
- Timestamp shown: [ ] Yes / [ ] No
- Expiration shown: [ ] Yes ❌ / [ ] No ✅
- API response: _____ (status code, body)
- Screenshot: _____

---

#### TC-202: Grant Custom Permission (With Expiration)
**Priority:** HIGH  
**Granter:** admin_test  
**Grantee:** cutting_op_test  
**Permission:** `finishing.convert_to_fg`  
**Expiration:** 2026-02-01T00:00:00  

**Steps:**
1. Login as admin_test
2. Navigate to `/admin/permissions`
3. Select cutting_op_test
4. Click "+ Grant Permission"
5. Select permission: `finishing.convert_to_fg`
6. Set expiration: 2026-02-01 (11 days from now)
7. Click "Grant"

**Expected Results:**
- ✅ Badge shows calendar icon 🗓️
- ✅ Shows "Expires: 2026-02-01" or "Expires in 11 days"
- ✅ Badge color: Green (not expired yet)

**Actual Results:**
- Badge appeared: [ ] Yes / [ ] No
- Calendar icon: [ ] Yes / [ ] No
- Expiration text: [ ] Yes / [ ] No (Text: _____)
- Badge color: [ ] Green ✅ / [ ] Gray (expired)
- API response: _____ 
- Screenshot: _____

---

#### TC-203: Revoke Custom Permission
**Priority:** HIGH  
**Revoker:** admin_test  
**User:** cutting_op_test  
**Permission:** `sewing.inline_qc` (granted in TC-201)  

**Steps:**
1. Login as admin_test
2. Navigate to `/admin/permissions`
3. Select cutting_op_test
4. Find "sewing.inline_qc" in Custom Permissions section
5. Click "X" button
6. Confirm revocation

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ Badge disappears after confirmation
- ✅ Permission removed from effective permissions

**API Call:**
```http
DELETE /admin/users/3/permissions/sewing.inline_qc
```

**Actual Results:**
- Confirmation dialog: [ ] Yes / [ ] No
- Badge removed: [ ] Yes / [ ] No
- API response: _____ (status code)
- User can no longer use permission: [ ] Verified / [ ] Not tested
- Screenshot: _____

---

#### TC-204: Cannot Revoke Role Permission
**Priority:** MEDIUM  
**User:** admin_test  
**Target:** cutting_op_test  
**Permission:** `cutting.view_status` (role-based)  

**Steps:**
1. Login as admin_test
2. Navigate to `/admin/permissions`
3. Select cutting_op_test
4. Check "Role Permissions" section

**Expected Results:**
- ✅ Role permissions show purple badges (not green)
- ✅ NO "X" revoke button on role permissions
- ✅ Only custom permissions (green badges) have "X" button

**Actual Results:**
- Role permissions color: [ ] Purple ✅ / [ ] Green ❌
- Revoke button on role perms: [ ] Yes ❌ / [ ] No ✅
- Revoke button on custom perms: [ ] Yes ✅ / [ ] No ❌
- Screenshot: _____

---

#### TC-205: Expired Permission Display
**Priority:** MEDIUM  
**Setup:** Manually set expiration to past date in database  

**Steps:**
1. Update database: `UPDATE custom_user_permissions SET expires_at = '2026-01-01' WHERE id = X`
2. Login as admin_test
3. Navigate to `/admin/permissions`
4. View user with expired permission

**Expected Results:**
- ✅ Badge shows gray color (not green)
- ✅ Badge has strikethrough text
- ✅ Shows alert icon ⚠️ (not calendar 🗓️)
- ✅ Text shows "Expired"

**Actual Results:**
- Badge color: [ ] Gray ✅ / [ ] Green ❌
- Strikethrough: [ ] Yes / [ ] No
- Alert icon: [ ] Yes / [ ] No
- "Expired" text: [ ] Yes / [ ] No
- Screenshot: _____

---

### Test Suite 4: Permission Inheritance (1 hour)

#### TC-301: SPV Inherits Operator Permissions
**Priority:** HIGH  
**User:** cutting_spv_test (role: SPV_CUTTING)  

**Expected Permissions:**
- All cutting.* permissions (6)
- Plus SPV-specific permissions
- Inherits base operator permissions

**Steps:**
1. Login as cutting_spv_test
2. Navigate to `/cutting`
3. Check visible buttons

**Expected vs Operator:**
| Permission | Operator | SPV | Inherited? |
|------------|----------|-----|------------|
| cutting.view_status | ✅ | ✅ | Yes |
| cutting.allocate_material | ✅ | ✅ | Yes |
| cutting.complete_operation | ✅ | ✅ | Yes |
| cutting.create_transfer | ✅ | ✅ | Yes |

**Actual Results:**
- SPV has all operator permissions: [ ] Yes / [ ] No
- SPV has additional permissions: [ ] Yes / [ ] No
- Permission count: _____ (Operator: 6, SPV: _____)
- Screenshot: _____

---

### Test Suite 5: Sidebar Menu Visibility (1 hour)

#### TC-401: Sidebar - Admin View
**Priority:** MEDIUM  
**User:** admin_test  

**Expected Menu Items:**
| Menu Item | Permission | Visible |
|-----------|------------|---------|
| Dashboard | dashboard.* | ✅ |
| Purchasing | (role-based) | ✅ |
| PPIC | ppic.* | ✅ |
| Production | (any production perm) | ✅ |
| ├─ Cutting | cutting.* | ✅ |
| ├─ Sewing | sewing.* | ✅ |
| ├─ Finishing | finishing.* | ✅ |
| ├─ Packing | packing.* | ✅ |
| Warehouse | (role-based) | ✅ |
| Finish Goods | (role-based) | ✅ |
| QC | (role-based) | ✅ |
| Reports | (role-based) | ✅ |
| Admin | admin.* | ✅ |
| ├─ User Management | admin.manage_users | ✅ |
| ├─ Permissions | admin.view_system_info | ✅ |
| ├─ Audit Trail | (role-based) | ✅ |

**Actual Results:**
- Dashboard: [ ] Visible / [ ] Hidden
- PPIC: [ ] Visible / [ ] Hidden
- Production: [ ] Visible / [ ] Hidden
- Admin: [ ] Visible / [ ] Hidden
- All submenus: [ ] Visible / [ ] Hidden
- Screenshot: _____

---

#### TC-402: Sidebar - Operator View (Limited)
**Priority:** MEDIUM  
**User:** cutting_op_test  

**Expected Menu Items:**
| Menu Item | Visible |
|-----------|---------|
| Dashboard | ❌ (no dashboard perms) |
| Production → Cutting | ✅ (has cutting perms) |
| Production → Sewing | ❌ (no sewing perms) |
| Admin | ❌ (no admin perms) |

**Actual Results:**
- Dashboard: [ ] Visible ❌ / [ ] Hidden ✅
- Cutting: [ ] Visible ✅ / [ ] Hidden ❌
- Sewing: [ ] Visible ❌ / [ ] Hidden ✅
- Admin: [ ] Visible ❌ / [ ] Hidden ✅
- Screenshot: _____

---

### Test Suite 6: Performance Testing (1 hour)

#### TC-501: Permission Check Latency
**Priority:** MEDIUM  
**User:** admin_test (36 permissions)  

**Test:**
```typescript
console.time('permission-check')
const result = usePermissionStore.getState().hasPermission('cutting.view_status')
console.timeEnd('permission-check')
```

**Expected Results:**
- ✅ <1ms for in-memory check
- ✅ <100ms for initial load from backend

**Test 100 iterations:**
```typescript
const times = []
for (let i = 0; i < 100; i++) {
  const start = performance.now()
  usePermissionStore.getState().hasPermission('cutting.view_status')
  times.push(performance.now() - start)
}
console.log('Average:', times.reduce((a,b) => a+b) / times.length, 'ms')
```

**Actual Results:**
- Single check time: _____ ms (Target: <1ms)
- Average over 100 checks: _____ ms
- Min: _____ ms
- Max: _____ ms
- Initial load time: _____ ms (Target: <100ms)
- Pass/Fail: [ ] PASS / [ ] FAIL

---

#### TC-502: Backend API Response Time
**Priority:** MEDIUM  
**Endpoint:** `GET /auth/permissions`  

**Test:**
1. Clear Redis cache (cold test)
2. Make API call
3. Measure response time
4. Make second call (hot test)
5. Measure response time

**Expected Results:**
- ✅ Cold (no cache): <10ms
- ✅ Hot (Redis cache): <1ms

**Actual Results:**
- Cold response time: _____ ms (Target: <10ms)
- Hot response time: _____ ms (Target: <1ms)
- Pass/Fail Cold: [ ] PASS / [ ] FAIL
- Pass/Fail Hot: [ ] PASS / [ ] FAIL

---

#### TC-503: Large Permission Set (Stress Test)
**Priority:** LOW  
**User:** Test user with 100+ permissions  

**Setup:**
- Create test user
- Grant 100 custom permissions
- Test permission check performance

**Expected Results:**
- ✅ Still <1ms per check
- ✅ Load time <200ms

**Actual Results:**
- Check time with 100 perms: _____ ms
- Load time: _____ ms
- Memory usage: _____ KB
- Pass/Fail: [ ] PASS / [ ] FAIL

---

### Test Suite 7: Error Handling (1 hour)

#### TC-601: 403 Forbidden Response
**Priority:** HIGH  
**User:** cutting_op_test  
**Action:** Try to create MO (no ppic.create_mo permission)  

**Steps:**
1. Login as cutting_op_test
2. Navigate to `/ppic`
3. Manually call API: `POST /ppic/manufacturing-orders`

**Expected Results:**
- ✅ Backend returns 403 Forbidden
- ✅ Frontend shows error message
- ✅ Permission cache NOT cleared (permission still valid)
- ✅ User stays on page

**Actual Results:**
- Backend response: _____ (status code)
- Frontend error shown: [ ] Yes / [ ] No (Message: _____)
- Cache cleared: [ ] Yes ❌ / [ ] No ✅
- User redirected: [ ] Yes / [ ] No
- Screenshot: _____

---

#### TC-602: 401 Unauthorized (Token Expired)
**Priority:** HIGH  
**Setup:** Use expired JWT token  

**Expected Results:**
- ✅ Backend returns 401 Unauthorized
- ✅ Frontend clears auth store
- ✅ Frontend clears permission store
- ✅ Redirects to `/login`

**Actual Results:**
- Backend response: _____ (status code)
- Auth store cleared: [ ] Yes / [ ] No
- Permission store cleared: [ ] Yes / [ ] No
- Redirected to login: [ ] Yes / [ ] No
- Screenshot: _____

---

#### TC-603: Network Error
**Priority:** MEDIUM  
**Setup:** Disconnect network while loading permissions  

**Expected Results:**
- ✅ Error message displayed
- ✅ Graceful degradation (no crash)
- ✅ Retry option available

**Actual Results:**
- Error message: [ ] Yes / [ ] No (Message: _____)
- App crashed: [ ] Yes ❌ / [ ] No ✅
- Retry available: [ ] Yes / [ ] No
- Screenshot: _____

---

## 🐛 Bug Tracking

### Bugs Found During Testing

| ID | Severity | Description | Found In | Status |
|----|----------|-------------|----------|--------|
| BUG-001 | | | TC-___ | 🟡 Open |
| BUG-002 | | | TC-___ | 🟡 Open |
| BUG-003 | | | TC-___ | 🟡 Open |

**Severity Levels:**
- 🔴 CRITICAL - Blocks core functionality
- 🟠 HIGH - Major feature broken
- 🟡 MEDIUM - Minor issue, workaround exists
- 🟢 LOW - Cosmetic issue

---

## ✅ Test Execution Checklist

### Pre-Testing Setup
- [ ] Test user accounts created
- [ ] Database seeded with test data
- [ ] Backend server running
- [ ] Frontend dev server running
- [ ] Browser DevTools open
- [ ] Screen recording started (optional)

### Test Execution
- [ ] Test Suite 1: Permission Store & Hooks (2h)
- [ ] Test Suite 2: UI Rendering by Role (3h)
- [ ] Test Suite 3: Permission Management Operations (2h)
- [ ] Test Suite 4: Permission Inheritance (1h)
- [ ] Test Suite 5: Sidebar Menu Visibility (1h)
- [ ] Test Suite 6: Performance Testing (1h)
- [ ] Test Suite 7: Error Handling (1h)

### Post-Testing
- [ ] All test results documented
- [ ] Screenshots collected
- [ ] Bugs logged
- [ ] Bug fixes prioritized
- [ ] Regression testing completed
- [ ] Test report generated

---

## 📊 Test Summary

### Test Statistics
- **Total Test Cases:** 30+
- **Passed:** _____
- **Failed:** _____
- **Blocked:** _____
- **Not Executed:** _____
- **Pass Rate:** _____%

### Critical Issues
1. _____
2. _____
3. _____

### Recommendations
1. _____
2. _____
3. _____

---

## 📝 Sign-off

**Tester:** _____________________  
**Date:** _____________________  
**Status:** [ ] APPROVED FOR STAGING / [ ] REQUIRES FIXES  
**Next Steps:** _____________________

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-21  
**Next Review:** After Day 4 completion
