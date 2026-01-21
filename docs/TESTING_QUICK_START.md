# Day 4 Testing Guide - Quick Start
## Phase 16 Week 4 | PBAC System Testing

**Date:** 2026-01-21  
**Purpose:** Quick guide to start testing the PBAC system  
**Full Test Plan:** See `PBAC_TEST_PLAN.md`

---

## 🚀 Quick Start Testing

### Step 1: Create Test Users (Manual)

Since automatic seeding requires backend adjustments, create these test users manually via the admin interface or database:

```sql
-- Quick SQL to create test users
INSERT INTO users (username, email, password_hash, role, department, is_active) VALUES
('admin_test', 'admin@test.com', '$2b$12$...', 'ADMIN', 'Admin', true),
('cutting_op_test', 'cutting_op@test.com', '$2b$12$...', 'OPERATOR', 'Cutting', true),
('sewing_op_test', 'sewing_op@test.com', '$2b$12$...', 'OPERATOR_SEWING', 'Sewing', true),
('qc_inspector_test', 'qc@test.com', '$2b$12$...', 'QC_INSPECTOR', 'QC', true);

-- Password: Test123! (hash with bcrypt)
```

**OR use existing users** from your database with appropriate roles.

---

### Step 2: Browser Testing Checklist

#### Test 1: Admin Full Access
1. Login as ADMIN user
2. Navigate to `/admin/permissions` → Should see full UI
3. Navigate to `/cutting` → Should see all action buttons
4. Check sidebar → Should see all menu items

**Expected:** ✅ All features visible and functional

---

#### Test 2: Operator Limited Access  
1. Login as OPERATOR (Cutting department)
2. Navigate to `/cutting` → Should see cutting buttons
3. Navigate to `/sewing` → Should see Lock icons (no permission)
4. Navigate to `/admin/permissions` → Should show "Access Denied"
5. Check sidebar → Should only see Cutting menu item

**Expected:** ✅ Limited to cutting department only

---

#### Test 3: QC Inspector Special Access
1. Login as QC_INSPECTOR
2. Navigate to `/sewing` 
3. Find "QC Inspection (Inspector Only)" button
4. Other sewing buttons should show Lock icons

**Expected:** ✅ QC button visible, others locked

---

#### Test 4: Permission Management
1. Login as ADMIN
2. Navigate to `/admin/permissions`
3. Select a user (e.g., cutting_op_test)
4. Click "+ Grant Permission"
5. Grant `sewing.inline_qc` with expiration 7 days
6. Verify green badge appears with calendar icon
7. Click X to revoke → Badge should disappear

**Expected:** ✅ Grant/revoke flows work correctly

---

#### Test 5: Performance Check
1. Open browser DevTools → Console
2. Run:
```javascript
console.time('perm-check')
usePermissionStore.getState().hasPermission('cutting.view_status')
console.timeEnd('perm-check')
```
3. Check time

**Expected:** ✅ <1ms response time

---

### Step 3: Check for Common Issues

#### Issue Checklist
- [ ] Buttons showing Lock icons correctly?
- [ ] "No Permission" badges displaying?
- [ ] Admin can grant permissions?
- [ ] Custom permissions show green badges?
- [ ] Expiration dates displaying correctly?
- [ ] Sidebar menu items filtered by permission?
- [ ] TypeScript errors in console?
- [ ] Network errors (check DevTools → Network tab)?

---

## 📊 Testing Progress Tracker

### Test Results Summary

**Total Tests:** 30+ test cases  
**Completed:** _____  
**Passed:** _____  
**Failed:** _____  

---

### Critical Tests (Must Pass)

- [ ] TC-001: Permission load on login
- [ ] TC-101: Cutting Page - Operator View
- [ ] TC-102: Cutting Page - No Permission View
- [ ] TC-105: Admin User Page - Admin View
- [ ] TC-107: Permission Management Page - Admin View
- [ ] TC-109: Permission Management Page - Access Denied
- [ ] TC-201: Grant Custom Permission (No Expiration)
- [ ] TC-202: Grant Custom Permission (With Expiration)
- [ ] TC-203: Revoke Custom Permission
- [ ] TC-501: Permission Check Latency <1ms

---

## 🐛 Bug Report Template

When you find a bug, document it here:

```markdown
### BUG-XXX: [Short Description]

**Severity:** 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW

**Found In:** TC-XXX (Test Case)

**Description:**
[What went wrong]

**Steps to Reproduce:**
1. Login as [user]
2. Navigate to [page]
3. Click [button]
4. Observe [issue]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Screenshot/Console Error:**
[Paste screenshot or error message]

**Impact:**
[How this affects users]

**Suggested Fix:**
[Optional: How to fix]
```

---

## ✅ Day 4 Completion Criteria

### Must Complete Before Staging
- [ ] All 30+ test cases executed
- [ ] Critical bugs documented
- [ ] Performance tests passed (<1ms)
- [ ] Permission inheritance verified
- [ ] Grant/revoke flows working
- [ ] UI rendering correct for all roles
- [ ] Zero TypeScript errors
- [ ] Day 4 completion report created

---

## 📝 Next Steps After Testing

1. **Document Results:** Fill in `PBAC_TEST_PLAN.md` with actual results
2. **Fix Bugs:** Create fixes for any critical/high severity bugs
3. **Regression Test:** Re-test fixed bugs
4. **Create Report:** Document Day 4 completion
5. **Prepare for Staging:** Days 6-7 deployment

---

**Quick Reference:**
- Full Test Plan: `docs/PBAC_TEST_PLAN.md`
- Test Users: See above SQL or use existing
- Expected Completion: Day 4 (8 hours)
- Next: Staging Deployment (Days 6-7)

---

**Status:** 🟡 Testing In Progress  
**Last Updated:** 2026-01-21
