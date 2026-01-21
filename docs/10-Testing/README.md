# 🧪 TESTING DOCUMENTATION

**Category**: Testing Plans, Guides, Quick Starts  
**Last Updated**: January 21, 2026

---

## 📋 FOLDER CONTENTS (4 Documents)

### 🔴 CRITICAL - Test Plans

1. **[PBAC_TEST_PLAN.md](PBAC_TEST_PLAN.md)** (25KB) ⭐⭐
   - **Purpose**: Comprehensive PBAC testing guide (30+ test cases)
   - **Audience**: QA team, Developers
   - **Contains**: 7 test suites, expected results, bug tracking
   - **Test Suites**:
     - Suite 1: Permission Store & Hooks (5 tests, 2 hours)
     - Suite 2: UI Rendering by Role (9 tests, 3 hours)
     - Suite 3: Permission Management (5 tests, 2 hours)
     - Suite 4: Permission Inheritance (1 test, 1 hour)
     - Suite 5: Sidebar Menu Visibility (2 tests, 1 hour)
     - Suite 6: Performance Testing (3 tests, 1 hour)
     - Suite 7: Error Handling (3 tests, 1 hour)
   - **Estimated Time**: 11 hours for full test execution
   - **Action**: Execute all test cases in Week 4

2. **[WEEK4_TESTING_PLAN.md](WEEK4_TESTING_PLAN.md)** (17KB)
   - **Purpose**: Week 4 testing strategy and plan
   - **Audience**: QA team, Project Manager
   - **Contains**: Testing timeline, resources, success criteria
   - **Scope**: Phase 16 Week 4 testing
   - **Status**: ⏳ Week 4 planned

### 📖 Testing Guides

3. **[TESTING_GUIDE_SESSION_12.1.md](TESTING_GUIDE_SESSION_12.1.md)** (9KB)
   - **Purpose**: Session 12.1 testing guide
   - **Audience**: QA team
   - **Contains**: Test scenarios, setup instructions
   - **Scope**: Session 12.1 features
   - **Status**: ✅ Complete

### 🚀 Quick Start

4. **[TESTING_QUICK_START.md](TESTING_QUICK_START.md)** (5KB) ⭐
   - **Purpose**: Simplified testing workflow for quick validation
   - **Audience**: All roles (developers, QA, operators)
   - **Contains**: 5 critical browser tests, issue checklist, bug template
   - **Time to Complete**: 15-30 minutes
   - **Usage**: Quick smoke testing before deployment

---

## 🚀 QUICK START GUIDE

### For QA Team (First Time)
1. **Setup Environment** (15 minutes)
   - Start backend: `uvicorn app.main:app --reload`
   - Start frontend: `npm run dev`
   - Create test users (9 roles)

2. **Read Test Plan** (30 minutes)
   - Open **[PBAC_TEST_PLAN.md](PBAC_TEST_PLAN.md)**
   - Understand test suites structure
   - Review expected results

3. **Execute Tests** (11 hours)
   - Follow test cases TC-001 through TC-603
   - Document actual results
   - Take screenshots for issues
   - Mark PASS/FAIL for each test

### For Quick Smoke Testing
1. **Read Quick Start** (5 minutes)
   - Open **[TESTING_QUICK_START.md](TESTING_QUICK_START.md)**
   - Review 5 critical tests

2. **Execute Quick Tests** (15-30 minutes)
   - Test 1: Admin access (2 min)
   - Test 2: Operator limited access (3 min)
   - Test 3: QC special permissions (3 min)
   - Test 4: Permission management UI (5 min)
   - Test 5: Performance check (2 min)

3. **Report Issues** (if any)
   - Use bug template in TESTING_QUICK_START.md
   - Include screenshots
   - Assign severity (Critical, High, Medium, Low)

---

## 📊 TEST COVERAGE

### PBAC Test Plan Coverage

| Test Suite | Test Cases | Time Estimate | Priority |
|------------|------------|---------------|----------|
| Permission Store & Hooks | 5 | 2 hours | 🔴 Critical |
| UI Rendering by Role | 9 | 3 hours | 🔴 Critical |
| Permission Management | 5 | 2 hours | 🟡 High |
| Permission Inheritance | 1 | 1 hour | 🟡 High |
| Sidebar Menu Visibility | 2 | 1 hour | 🟢 Medium |
| Performance Testing | 3 | 1 hour | 🟡 High |
| Error Handling | 3 | 1 hour | 🟢 Medium |
| **Total** | **28** | **11 hours** | - |

### Test User Matrix

| Username | Role | Department | Purpose |
|----------|------|------------|---------|
| admin_test | ADMIN | Admin | Full access testing |
| manager_test | MANAGER | Management | Manager-level testing |
| cutting_op_test | OPERATOR | Cutting | Operator limited access |
| cutting_spv_test | SPV_CUTTING | Cutting | Supervisor testing |
| sewing_op_test | OPERATOR_SEWING | Sewing | Sewing operator |
| sewing_spv_test | SPV_SEWING | Sewing | Sewing supervisor |
| qc_inspector_test | QC_INSPECTOR | QC | QC inspector permissions |
| ppic_manager_test | PPIC_MANAGER | PPIC | PPIC manager testing |
| no_perms_test | CUSTOM_ROLE | - | Zero permissions (negative test) |

---

## 🎯 TESTING WORKFLOW

### Phase 1: Setup (Day 1, 30 minutes)
1. Start backend and frontend servers
2. Create test users (manual or via script)
3. Verify database has 36 permissions seeded
4. Verify Redis cache is running
5. Open PBAC_TEST_PLAN.md

### Phase 2: Execute Test Suites (Day 1-2, 11 hours)
1. **Suite 1**: Permission Store & Hooks (2 hours)
   - Test permission loading on login
   - Test permission hooks functionality
   - Verify cache behavior

2. **Suite 2**: UI Rendering by Role (3 hours)
   - Test all 9 user roles
   - Verify button visibility
   - Check sidebar menu items
   - Validate "No Permission" badges

3. **Suite 3**: Permission Management (2 hours)
   - Test grant/revoke custom permissions
   - Test expiration dates
   - Test permission inheritance

4. **Suite 4**: Permission Inheritance (1 hour)
   - Test role-based permissions
   - Test custom permission override

5. **Suite 5**: Sidebar Menu (1 hour)
   - Test menu visibility by role
   - Test permission-based menu items

6. **Suite 6**: Performance (1 hour)
   - Test permission check speed (<1ms)
   - Test initial load time (<100ms)
   - Test cache effectiveness

7. **Suite 7**: Error Handling (1 hour)
   - Test expired token
   - Test missing permissions
   - Test API error responses

### Phase 3: Bug Fixes (Day 3, 2-4 hours)
1. Review all test results
2. Categorize bugs by severity
3. Fix Critical and High priority bugs
4. Regression test fixed bugs
5. Update documentation

### Phase 4: Validation (Day 4, 1 hour)
1. Re-run failed test cases
2. Calculate pass rate (target: >95%)
3. Document final test results
4. Create test results report
5. Sign-off for staging deployment

---

## 🐛 BUG TRACKING

### Bug Severity Levels

- 🔴 **CRITICAL**: Blocks core functionality (0 tolerance)
- 🟠 **HIGH**: Major feature broken (fix before staging)
- 🟡 **MEDIUM**: Minor issue (document, may defer)
- 🟢 **LOW**: Cosmetic (defer to future sprint)

### Bug Template (from TESTING_QUICK_START.md)

```markdown
**BUG ID**: BUG-PBAC-001
**Severity**: [Critical/High/Medium/Low]
**Test Case**: TC-XXX
**Affected Role**: [Role Name]
**Summary**: [One-line description]
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]
**Expected**: [What should happen]
**Actual**: [What actually happened]
**Screenshot**: [Attach screenshot]
**Environment**: [Browser, OS, versions]
**Assignee**: [Developer name]
**Status**: [Open/In Progress/Fixed/Closed]
```

---

## 📊 SUCCESS CRITERIA

### Week 4 Testing Completion

- ✅ **Test Execution**: All 28 test cases executed
- ✅ **Pass Rate**: >95% (max 1-2 failures)
- ✅ **Critical Bugs**: 0 critical bugs
- ✅ **High Bugs**: <3 high priority bugs
- ✅ **Performance**: All performance targets met (<1ms checks)
- ✅ **Documentation**: Test results report created
- ✅ **Sign-off**: Approved for staging deployment

---

## 📁 RELATED FOLDERS

- **[09-Security/](../09-Security/)**: Security documentation (PBAC details)
- **[12-Frontend-PBAC/](../12-Frontend-PBAC/)**: Frontend PBAC implementation
- **[13-Phase16/](../13-Phase16/)**: Phase 16 status reports
- **[04-Session-Reports/](../04-Session-Reports/)**: Session 13.6 testing infrastructure

---

## 📞 TESTING TEAM

**QA Lead**: [Contact Info]  
**Test Engineers**: [Team Members]  
**Test Environment**: Development + Staging

---

## 🔗 EXTERNAL RESOURCES

- Frontend URL: http://localhost:3001
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Test Users: See seed_test_users.py script

---

**Last Reorganization**: January 21, 2026  
**Total Documents**: 4 files, ~56KB  
**Status**: ✅ All testing docs organized  
**Next**: Execute Week 4 testing (11 hours)
