# Week 4 Complete Task List
**Phase 16 - Post-Security Optimizations**  
**Updated:** January 21, 2026

---

## Backend Tasks ✅ COMPLETE

### Week 3 Completed
- [x] Create PermissionService with Redis caching (540 lines)
- [x] Add require_permission() dependencies
- [x] Migrate Dashboard module (5/5 endpoints)
- [x] Migrate Cutting module (8/8 endpoints)
- [x] Migrate Sewing module (9/9 endpoints)
- [x] Migrate Finishing module (9/9 endpoints)
- [x] Migrate Packing module (6/6 endpoints)
- [x] Migrate PPIC module (4/4 endpoints)
- [x] Migrate Admin module (8/8 endpoints)
- [x] Migrate Import/Export module (6/6 endpoints)
- [x] Create comprehensive documentation
- [x] Create test suites (unit + integration)

**Total:** 80+ endpoints migrated to PBAC ✅

---

## Frontend Tasks 🔄 IN PROGRESS

### Day 1-2: Permission Infrastructure
- [ ] **Create Permission Store** (`src/store/permissionStore.ts`)
  - loadPermissions() function
  - hasPermission() utility
  - hasAnyPermission() utility
  - Clear permissions on logout

- [ ] **Create Permission Hooks** (`src/hooks/usePermission.ts`)
  - usePermission(code) hook
  - useAnyPermission(codes) hook
  - usePermissions() hook

- [ ] **Add Backend Endpoint** (`app/api/v1/auth.py`)
  - GET /auth/permissions endpoint
  - Return user's effective permissions
  - Cache with Redis

- [ ] **Update Auth Flow**
  - Load permissions after login
  - Clear permissions on logout
  - Refresh permissions periodically

### Day 3: Update Navigation Components
- [ ] **Update Sidebar.tsx**
  - Add permission-based menu filtering
  - Keep role-based fallback (backward compatible)
  - Update submenu visibility logic
  - Test with all user roles

- [ ] **Update Navbar.tsx** (if needed)
  - Add permission-based action buttons
  - Update notifications based on permissions
  - Ensure environment indicator still works

### Day 4-5: Update Production Pages
- [ ] **CuttingPage.tsx**
  - Add permission checks for all actions
  - Hide/show buttons based on permissions
  - Test: Operator vs SPV permissions

- [ ] **SewingPage.tsx**
  - Add permission checks
  - QC section (QC Inspector only)
  - Transfer buttons (SPV only)

- [ ] **FinishingPage.tsx**
  - Add permission checks
  - Metal detector QC (QC Inspector only)
  - FG conversion (SPV only)

- [ ] **PackingPage.tsx**
  - Add permission checks
  - Shipping mark (SPV only)
  - Sorting/packing (Operator)

- [ ] **PPICPage.tsx**
  - Add permission checks
  - MO creation (PPIC Manager only)
  - MO approval (PPIC Manager only)

- [ ] **AdminUserPage.tsx**
  - Add permission checks
  - User management section
  - System info section

### Day 6: Error Handling & Polish
- [ ] **Update API Client**
  - Handle 403 Forbidden responses
  - Show error notifications
  - Optional: Redirect to /unauthorized

- [ ] **Create UnauthorizedPage Enhancement**
  - Show which permission was required
  - Link to contact admin
  - Back button to previous page

- [ ] **Update Error Boundaries**
  - Catch permission errors
  - Display user-friendly messages

### Day 7: Testing & Documentation
- [ ] **Frontend Testing**
  - Test all permission combinations
  - Test menu visibility
  - Test button visibility
  - Test error handling

- [ ] **User Acceptance Testing**
  - Test with real user accounts
  - Verify Operator sees only their permissions
  - Verify SPV sees inherited permissions
  - Verify Admin sees everything

- [ ] **Documentation**
  - Update README with permission guide
  - Document permission codes for frontend devs
  - Create troubleshooting guide

---

## Backend Testing Tasks ⏳ PENDING

### Day 1: Unit Tests
- [ ] **PermissionService Tests** (`tests/pbac/test_permission_service.py`)
  - Test direct permission grant
  - Test permission via role
  - Test role hierarchy (SPV inherits operator)
  - Test custom permissions with expiration
  - Test Redis caching (cold cache <10ms)
  - Test Redis caching (hot cache <1ms)
  - Test cache invalidation
  - Test cache TTL
  - Test Redis unavailable fallback

### Day 2: Integration Tests
- [ ] **Endpoint Tests** (`tests/pbac/test_endpoints.py`)
  - Dashboard endpoints (authorized/unauthorized)
  - Cutting endpoints (all 8)
  - Sewing endpoints (all 9)
  - Finishing endpoints (all 9)
  - Packing endpoints (all 6)
  - PPIC endpoints (all 4)
  - Admin endpoints (all 8)
  - Import/Export endpoints (all 6)

### Day 3: Performance Tests
- [ ] **Permission Check Performance**
  - Cold cache performance (<10ms)
  - Hot cache performance (<1ms)
  - Cache hit rate under load (>99%)
  - Concurrent requests (100 parallel)

- [ ] **Dashboard Performance**
  - Stats endpoint (<200ms)
  - Production status (<300ms)
  - Verify 40-100x improvement maintained

### Day 4: Security Tests
- [ ] **Permission Bypass Tests**
  - Invalid token rejection
  - Manipulated token rejection
  - Expired custom permission denied
  - Role escalation prevention

- [ ] **Audit Trail Tests**
  - 403 events logged
  - Permission changes logged
  - Security events logged

---

## Deployment Tasks ⏳ PENDING

### Day 5-6: Staging Deployment
- [ ] **Database Migration**
  - Backup production database
  - Run PBAC migration on staging
  - Verify migration success
  - Seed permissions

- [ ] **Redis Configuration**
  - Verify Redis connectivity
  - Set memory policy (allkeys-lru)
  - Test permission caching
  - Monitor cache hit rate

- [ ] **Environment Setup**
  - Update .env.staging
  - Set SECRET_KEY rotation
  - Configure Redis URL
  - Set cache TTL

### Day 6-7: Validation
- [ ] **Functional Testing** (24 hours)
  - All endpoints return correct responses
  - Permissions enforced correctly
  - No 500 errors
  - Redis cache working

- [ ] **Performance Testing** (24 hours)
  - Dashboard <200ms
  - Permission checks <10ms
  - No memory leaks
  - Cache hit rate >99%

- [ ] **Security Audit**
  - No permission bypasses
  - All security events logged
  - ISO 27001 compliance verified
  - Penetration testing passed

---

## Checklist Summary

### Backend
- [x] PBAC migration (55+ endpoints)
- [x] PermissionService created
- [x] Documentation created
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Performance tests written
- [ ] Security tests written

### Frontend
- [ ] Permission store created
- [ ] Permission hooks created
- [ ] Sidebar updated
- [ ] Pages updated (6 pages)
- [ ] Error handling enhanced
- [ ] Testing complete

### Deployment
- [ ] Staging database migrated
- [ ] Redis configured
- [ ] 48-hour validation complete
- [ ] Security audit passed
- [ ] Production rollout ready

---

## Timeline

**Week 3 (Complete):** Backend PBAC migration  
**Week 4 Days 1-2:** Backend testing  
**Week 4 Days 3-5:** Frontend integration  
**Week 4 Days 6-7:** Staging deployment & validation  
**Week 5 Day 1:** Production rollout (if validation passes)

---

## Priority Levels

🔴 **Critical** - Backend testing, security tests  
🟡 **High** - Frontend integration, staging deployment  
🟢 **Medium** - Documentation, polish  
⚪ **Low** - Nice-to-have enhancements

---

**Status:** 📋 **TASK LIST READY - BEGIN WEEK 4**
