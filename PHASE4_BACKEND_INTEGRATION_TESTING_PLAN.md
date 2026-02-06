# 🔌 PHASE 4: BACKEND INTEGRATION TESTING PLAN
**Session**: 47 (Continued)  
**Date**: February 6, 2026  
**Status**: 🔄 IN PROGRESS  
**Priority**: HIGH - Critical for Production Readiness

---

## 📋 EXECUTIVE SUMMARY

Phase 4 focuses on **end-to-end testing** of frontend-backend connectivity to ensure:
- ✅ All API endpoints are correctly mapped and functional
- ✅ Data flows correctly between frontend and backend
- ✅ Error handling works as expected
- ✅ Authentication and authorization are properly enforced
- ✅ Real-time updates function correctly
- ✅ All CRUD operations work for each module

**Scope**: Test all modules implemented in Phases 1-3 against backend APIs

---

## 🎯 OBJECTIVES

### Primary Goals
1. **API Connectivity Verification**: Ensure frontend can communicate with backend
2. **Data Flow Testing**: Verify request/response data structures match
3. **Error Handling**: Test error scenarios (400, 401, 403, 404, 500)
4. **Authentication Flow**: Test login, logout, token refresh, session management
5. **CRUD Operations**: Test Create, Read, Update, Delete for all modules
6. **Real-time Features**: Test WebSocket connections, live updates
7. **File Operations**: Test image uploads, Excel import/export, PDF generation

### Secondary Goals
1. **Performance Testing**: Measure API response times
2. **Load Testing**: Test with multiple concurrent users
3. **Security Testing**: Verify JWT validation, permission checks
4. **Edge Cases**: Test boundary conditions, invalid inputs

---

## 🗂️ TESTING MODULES (By Priority)

### Priority 1: Core Authentication & Dashboard (CRITICAL)
- **Module**: Authentication
- **Endpoints**:
  - `POST /auth/login` - User login
  - `GET /auth/me` - Get current user
  - `POST /auth/logout` - User logout
  - `POST /auth/refresh` - Refresh token
- **Tests**:
  - ✅ Valid login (admin, ppic, warehouse, production users)
  - ✅ Invalid credentials rejection
  - ✅ Token storage and retrieval
  - ✅ Session timeout (30 minutes)
  - ✅ Token refresh mechanism
  - ✅ Logout and token cleanup
- **Frontend Files**: `LoginPage.tsx`, `useAuth.ts`, `authStore.ts`

- **Module**: Dashboard
- **Endpoints**:
  - `GET /dashboard/kpi` - Get KPI metrics
  - `GET /dashboard/stats` - Get dashboard stats
  - `GET /dashboard/production-status` - Production status
  - `GET /dashboard/alerts` - Critical alerts
- **Tests**:
  - ✅ Dashboard loads without errors
  - ✅ KPI cards display correct data
  - ✅ Charts render with real data
  - ✅ Alerts show critical items
  - ✅ Role-based dashboard views (PPIC, Warehouse, Manager, Director)
- **Frontend Files**: `DashboardPage.tsx`
- **Status**: ✅ Fixed undefined error (Session 47)

---

### Priority 2: Production Module (HIGH)
- **Module**: Department Pages (Cutting, Sewing, Finishing, Packing)
- **Endpoints**:
  - `GET /production/spk/{dept}` - Get SPK list per department
  - `GET /production/spk/{id}` - Get SPK details
  - `GET /production/calendar/{dept}/{month}` - Calendar data
  - `POST /production/input` - Daily production input
  - `GET /production/wip` - WIP dashboard
  - `GET /production/performance` - Performance metrics
- **Tests**:
  - ✅ Department pages load SPK list
  - ✅ Calendar view displays correctly
  - ✅ Daily input form submission works
  - ✅ Cumulative calculation accurate
  - ✅ Good/defect tracking works
  - ✅ Material consumption tracking
  - ✅ Real-time WIP updates
- **Frontend Files**: 
  - `CuttingPage.tsx` (refactored)
  - `SewingPage.tsx` (refactored)
  - `FinishingPage.tsx` (refactored)
  - `PackingPage.tsx` (refactored)
- **Status**: ✅ Refactored in Phase 2, needs backend testing

---

### Priority 3: PPIC Module (HIGH)
- **Module**: Manufacturing Orders & SPK Management
- **Endpoints**:
  - `GET /ppic/mo` - List MOs
  - `GET /ppic/mo/{id}` - MO details
  - `POST /ppic/mo/create` - Create MO
  - `PUT /ppic/mo/{id}/release-partial` - Partial release
  - `PUT /ppic/mo/{id}/release-full` - Full release
  - `GET /ppic/spk` - List SPKs
  - `POST /ppic/spk/generate` - Generate SPKs
  - `GET /ppic/material-allocation/{mo_id}` - Material allocation
- **Tests**:
  - ✅ MO list loads with filters
  - ✅ MO creation from PO Label
  - ✅ Partial release (Cutting + Embroidery SPKs)
  - ✅ Full release (All department SPKs)
  - ✅ Week & Destination inheritance
  - ✅ Material allocation dashboard
  - ✅ BOM explosion calculation
- **Frontend Files**: `PPICPage.tsx`, `CreateMOPage.tsx`

---

### Priority 4: Warehouse Module (HIGH)
- **Module**: Material Management, FG Management
- **Endpoints**:
  - `GET /warehouse/material/stock` - Material stock list
  - `POST /warehouse/material/receipt` - Material receipt (GRN)
  - `POST /warehouse/material/issue` - Issue to production
  - `POST /warehouse/material/adjust` - Stock adjustment
  - `GET /warehouse/fg/stock` - FG stock list
  - `POST /warehouse/fg/receipt` - FG receipt from Packing
  - `POST /warehouse/fg/shipment` - FG shipment
- **Tests**:
  - ✅ Material stock list loads
  - ✅ Color coding (green, yellow, red, black)
  - ✅ Material receipt with variance validation
  - ✅ Approval workflow (0-5%, 5-10%, >10%)
  - ✅ Material debt tracking
  - ✅ FG receipt with UOM conversion
  - ✅ Barcode scanning integration
- **Frontend Files**: `WarehousePage.tsx`, `MaterialReceiptPage.tsx`, `FGReceiptPage.tsx`

---

### Priority 5: Purchasing Module (MEDIUM)
- **Module**: Purchase Order Management
- **Endpoints**:
  - `GET /purchasing/po` - List POs
  - `GET /purchasing/po/{id}` - PO details
  - `POST /purchasing/po/create` - Create PO
  - `POST /purchasing/po/bom-explosion` - BOM explosion (AUTO mode)
  - `PUT /purchasing/po/{id}` - Update PO
  - `DELETE /purchasing/po/{id}` - Cancel PO
- **Tests**:
  - ✅ PO list with filters
  - ✅ AUTO mode (BOM explosion)
  - ✅ MANUAL mode (custom material list)
  - ✅ Dual trigger system (PO Kain, PO Label)
  - ✅ 3 Purchasing Specialists workflow
  - ✅ PO tracking dashboard
- **Frontend Files**: `PurchasingPage.tsx`, `CreatePOPage.tsx`
- **Status**: ✅ RefactorednRefactored in Phase 1 (NAVIGATION_INTEGRATION_AUDIT)

---

### Priority 6: Quality Control & Rework (MEDIUM)
- **Module**: QC Checkpoints, Rework Management
- **Endpoints**:
  - `POST /qc/checkpoint` - QC checkpoint input
  - `GET /rework/orders` - List rework orders
  - `POST /rework/start` - Start rework
  - `POST /rework/complete` - Complete rework
  - `GET /rework/dashboard` - Rework KPIs
  - `GET /rework/report/copq` - COPQ analysis
- **Tests**:
  - ✅ QC checkpoint form submission
  - ✅ Defect capture and classification
  - ✅ Rework queue management
  - ✅ Recovery tracking
  - ✅ COPQ calculation
  - ✅ First Pass Yield (FPY) report
- **Frontend Files**: `QCPage.tsx`, `QCCheckpointPage.tsx`, `ReworkPage.tsx`
- **Status**: ✅ Pending refactoring (Phase 1 backlog)

---

### Priority 7: Masterdata & Reporting (LOW)
- **Module**: Materials, Suppliers, Articles, BOM, Reports
- **Endpoints**:
  - CRUD endpoints for all masterdata
  - Report builder endpoints
  - Excel import/export endpoints
- **Tests**:
  - ✅ CRUD operations for all masterdata
  - ✅ Excel import/export
  - ✅ Report generation
  - ✅ Chart rendering
- **Frontend Files**: Various masterdata pages, report pages

---

## 🔧 TESTING APPROACH

### 1. Manual Testing (Primary)
**Tools**: Browser DevTools, Postman, Thunder Client

**Process**:
1. Start backend server: `cd erp-softtoys && uvicorn app.main:app --reload`
2. Start frontend server: `cd erp-ui/frontend && npm run dev`
3. Open browser: `http://localhost:3000`
4. Test each module systematically:
   - Navigate to page
   - Check if data loads
   - Test form submissions
   - Check error handling
   - Verify success messages

**Checklist per Page**:
- [ ] Page loads without errors
- [ ] API calls succeed (check Network tab)
- [ ] Data displays correctly
- [ ] Forms can be submitted
- [ ] Success/error messages appear
- [ ] Loading states work
- [ ] Error boundaries catch failures

---

### 2. Automated Testing (Secondary)
**Tools**: Jest, React Testing Library, Playwright

**Test Types**:
1. **Unit Tests**: Test individual API functions
2. **Integration Tests**: Test API + component interaction
3. **E2E Tests**: Test complete user flows

**Example Test**:
```typescript
// tests/api/auth.test.ts
describe('Authentication API', () => {
  it('should login successfully with valid credentials', async () => {
    const response = await authApi.login({
      username: 'admin',
      password: 'admin123'
    })
    
    expect(response.status).toBe(200)
    expect(response.data.access_token).toBeDefined()
    expect(response.data.user.username).toBe('admin')
  })
  
  it('should reject invalid credentials', async () => {
    await expect(
      authApi.login({ username: 'admin', password: 'wrong' })
    ).rejects.toThrow('Invalid credentials')
  })
})
```

---

### 3. Backend Health Check (Prerequisite)
**Before Testing**: Verify backend is running and healthy

**Health Check Endpoints**:
```bash
# Backend health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/db-check

# API docs (Swagger)
open http://localhost:8000/docs
```

**Expected Responses**:
- Health: `{"status": "healthy"}`
- DB Check: `{"status": "connected"}`
- Swagger: Interactive API documentation

---

## 📊 TESTING MATRIX

### Module Status Tracker

| Module | Priority | Pages | Endpoints | Status | Issues |
|--------|----------|-------|-----------|--------|--------|
| **Authentication** | P1 | LoginPage | 4 | ⏳ Pending | - |
| **Dashboard** | P1 | DashboardPage | 4 | ✅ Fixed | Undefined error (resolved) |
| **Production** | P2 | 4 Dept Pages | 7 | ⏳ Pending | - |
| **PPIC** | P3 | PPICPage, CreateMO | 8 | ⏳ Pending | - |
| **Warehouse** | P4 | 3 Pages | 7 | ⏳ Pending | - |
| **Purchasing** | P5 | 2 Pages | 6 | ⏳ Pending | - |
| **QC & Rework** | P6 | 3 Pages | 6 | ⏳ Pending | Needs refactoring first |
| **Masterdata** | P7 | Multiple | 20+ | ⏳ Pending | - |

**Legend**:
- ⏳ Pending - Not yet tested
- 🔄 In Progress - Currently testing
- ✅ Passed - All tests passed
- ⚠️ Issues - Has known issues (documented)
- ❌ Failed - Critical failures blocking

---

## 🐛 ISSUE TRACKING

### Known Issues

#### 1. ✅ RESOLVED: DashboardPage Undefined Error
- **Issue**: `Cannot read properties of undefined (reading 'refreshed_at')`
- **Location**: `DashboardPage.tsx:207`
- **Root Cause**: API response not validated, stats became undefined
- **Fix**: Added optional chaining + fallback values
- **Status**: ✅ Resolved (Session 47)

#### 2. API Endpoint Mismatch (Potential)
- **Issue**: Frontend API calls may not match backend endpoint structure
- **Example**: Frontend calls `/dashboard/kpi`, backend may have `/api/v1/dashboard/kpi`
- **Solution**: Verify API base URL configuration in `api/client.ts`
- **Status**: ⏳ To be verified

#### 3. CORS Configuration (Potential)
- **Issue**: Frontend (localhost:3000) may be blocked by CORS from backend (localhost:8000)
- **Solution**: Verify CORS middleware in `main.py` allows frontend origin
- **Status**: ⏳ To be verified

---

## 🔄 TESTING WORKFLOW

### Step 1: Environment Setup (5 minutes)
```powershell
# Terminal 1: Start Backend
cd d:\Project\ERP2026\erp-softtoys
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd d:\Project\ERP2026\erp-ui\frontend
npm run dev

# Terminal 3: Open Browser
start http://localhost:3000
```

### Step 2: Verify Backend Health (2 minutes)
```powershell
# Check backend is running
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### Step 3: Test Authentication (10 minutes)
1. Navigate to `http://localhost:3000/login`
2. Test valid login (admin/admin123)
3. Verify token storage in localStorage
4. Check redirect to dashboard
5. Test logout
6. Test invalid credentials (should reject)
7. Document any issues

### Step 4: Test Dashboard (10 minutes)
1. Login as admin
2. Verify dashboard loads
3. Check KPI cards display data
4. Verify charts render
5. Test role-based views (PPIC, Warehouse, Manager, Director)
6. Document any issues

### Step 5: Test Production Module (30 minutes)
1. Navigate to Cutting page
2. Verify SPK list loads
3. Test daily input form
4. Repeat for Sewing, Finishing, Packing
5. Document any issues

### Step 6: Test PPIC Module (30 minutes)
1. Navigate to PPIC page
2. Verify MO list loads
3. Test MO creation
4. Test SPK generation
5. Document any issues

### Step 7: Test Warehouse Module (30 minutes)
1. Navigate to Warehouse page
2. Verify material stock list
3. Test material receipt
4. Test FG management
5. Document any issues

### Step 8: Test Remaining Modules (60 minutes)
- Purchasing
- QC & Rework
- Masterdata
- Reporting

---

## 📝 TEST REPORT TEMPLATE

### Test Execution Report

**Date**: [Date]  
**Tester**: [Name]  
**Environment**: Development  
**Backend Version**: [Version]  
**Frontend Version**: [Version]

#### Module: [Module Name]
**Status**: ⏳ / 🔄 / ✅ / ⚠️ / ❌

**Test Cases**:
- [ ] Test Case 1: [Description]
  - **Expected**: [Expected result]
  - **Actual**: [Actual result]
  - **Status**: ✅ Pass / ❌ Fail
  - **Notes**: [Any observations]

- [ ] Test Case 2: [Description]
  - **Expected**: [Expected result]
  - **Actual**: [Actual result]
  - **Status**: ✅ Pass / ❌ Fail
  - **Notes**: [Any observations]

**Issues Found**:
1. **Issue**: [Description]
   - **Severity**: Critical / High / Medium / Low
   - **Location**: [File:Line]
   - **Steps to Reproduce**: [Steps]
   - **Expected**: [Expected behavior]
   - **Actual**: [Actual behavior]
   - **Fix**: [Proposed solution]

**Screenshots**: [Attach if applicable]

**Performance**: [Response times, load times]

---

## ✅ SUCCESS CRITERIA

### Phase 4 Complete When:
- ✅ All Priority 1-2 modules tested (Auth, Dashboard, Production, PPIC)
- ✅ All Priority 3-4 modules tested (Warehouse, Purchasing)
- ✅ Critical issues documented and prioritized
- ✅ API connectivity verified for all modules
- ✅ Error handling works correctly
- ✅ Authentication and authorization enforced
- ✅ Test report generated
- ✅ Issues logged in tracking system

### Quality Gates:
- **Critical Issues**: 0 (all critical bugs must be resolved)
- **High Priority Issues**: <5 (high priority bugs documented with fixes)
- **API Success Rate**: >95% (95% of API calls succeed)
- **Page Load Time**: <2s (average page load time)
- **Error Handling**: 100% (all error scenarios handled gracefully)

---

## 📅 ESTIMATED TIMELINE

### Day 1: Core Testing (4 hours)
- Environment setup: 30 minutes
- Authentication testing: 1 hour
- Dashboard testing: 1 hour
- Production module testing: 1.5 hours

### Day 2: PPIC & Warehouse (4 hours)
- PPIC module testing: 2 hours
- Warehouse module testing: 2 hours

### Day 3: Purchasing & QC (3 hours)
- Purchasing module testing: 1.5 hours
- QC & Rework testing: 1.5 hours

### Day 4: Masterdata & Reporting (2 hours)
- Masterdata testing: 1 hour
- Reporting testing: 30 minutes
- Final verification: 30 minutes

**Total**: ~13 hours (spread over 4 days)

---

## 🚀 NEXT STEPS AFTER PHASE 4

### If All Tests Pass:
1. Move to **Phase 5: Production Testing & Deployment**
2. Setup staging environment
3. Perform UAT (User Acceptance Testing)
4. Prepare deployment guide

### If Issues Found:
1. Create GitHub issues for all bugs
2. Prioritize issues (Critical → High → Medium → Low)
3. Fix critical and high priority issues
4. Re-test affected modules
5. Document workarounds for low priority issues

---

## 📚 REFERENCE DOCUMENTS

- **Primary**: `prompt.md` - Implementation roadmap
- **Phase 1-3**: Completion documents (PHASE1-3 markdown files)
- **Navigation**: `NAVIGATION_INTEGRATION_AUDIT.md` - 3-tier architecture
- **Spec**: `docs/00-Overview/Logic UI/Rencana Tampilan.md` - UI/UX specifications
- **Backend**: `erp-softtoys/app/main.py` - FastAPI application
- **Frontend**: `erp-ui/frontend/src/api/index.ts` - API client

---

**Document Version**: 1.0  
**Created**: February 6, 2026  
**Last Updated**: February 6, 2026  
**Author**: IT Fullstack Team (Claude AI)  
**Status**: 🔄 Active - Phase 4 In Progress
