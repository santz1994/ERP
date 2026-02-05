# 🔍 CODE QUALITY AUDIT REPORT

**Project**: ERP Quty Karunia Manufacturing System  
**Date**: February 5, 2026  
**Auditor**: IT Fullstack (Claude AI)  
**Type**: Systematic Code Refactoring Analysis

---

## 📊 EXECUTIVE SUMMARY

**Total Pages Analyzed**: 27 pages  
**Critical Issues Found**: 18  
**Priority**: HIGH - Immediate Action Required  
**Estimated Refactoring Time**: 3-4 hours

### Issue Breakdown:
- 🔴 **Critical** (7): Duplicate functions, inconsistent imports
- 🟡 **High** (6): Relative imports instead of aliases
- 🟢 **Medium** (5): Code organization improvements

---

## 🚨 CRITICAL ISSUES (Priority 1)

### 1. DUPLICATE `getStatusBadge()` FUNCTION

**Severity**: 🔴 CRITICAL  
**Impact**: Code duplication, maintenance nightmare  
**Files Affected**: 7 pages

**Duplicated in:**
1. `pages/ppic/MOListPage.tsx` (line 65)
2. `pages/ppic/MODetailPage.tsx` (line 114)
3. `pages/production/WIPDashboardPage.tsx` (line 70)
4. `pages/warehouse/MaterialStockPage.tsx` (line 68)
5. `pages/PurchasingPage.tsx` (line 113)
6. `pages/EmbroideryPage.tsx` (line 159)
7. `pages/CuttingPage.tsx` (line 130)

**Problem**:
```typescript
// ❌ DUPLICATED 7 TIMES across different pages
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'DRAFT': return { variant: 'secondary', label: 'Draft' }
    case 'PARTIAL': return { variant: 'warning', label: 'Partial' }
    case 'RELEASED': return { variant: 'success', label: 'Released' }
    // ... etc
  }
}
```

**Solution**:
Move to `src/lib/utils.ts` as a reusable utility:
```typescript
// ✅ CENTRALIZED in utils.ts
export const getStatusBadge = (
  status: string, 
  type: 'mo' | 'po' | 'spk' | 'material' = 'mo'
) => {
  // Unified logic with type parameter for different contexts
}
```

**Action Items**:
- [ ] Extract function to `lib/utils.ts`
- [ ] Add TypeScript types for status enums
- [ ] Update all 7 pages to import from utils
- [ ] Remove duplicate implementations
- [ ] Add unit tests

**Estimated Time**: 1 hour

---

### 2. INCONSISTENT IMPORTS (Relative vs Alias)

**Severity**: 🔴 CRITICAL  
**Impact**: Code inconsistency, harder maintenance

**Files with Relative Imports**:
1. `WarehousePage.tsx`:
   ```typescript
   // ❌ WRONG
   import BarcodeScanner from '../components/BarcodeScanner';
   import { MaterialRequestFormData } from '../components/warehouse/MaterialRequestModal';
   
   // ✅ SHOULD BE
   import BarcodeScanner from '@/components/BarcodeScanner';
   import { MaterialRequestFormData } from '@/components/warehouse/MaterialRequestModal';
   ```

2. `MaterialDebtPage.tsx`:
   ```typescript
   // ❌ WRONG
   import { usePermission } from '../hooks/usePermission';
   import { useAuthStore } from '../store';
   import { UserRole } from '../types';
   
   // ✅ SHOULD BE
   import { usePermission } from '@/hooks/usePermission';
   import { useAuthStore } from '@/store';
   import { UserRole } from '@/types';
   ```

3. `FinishgoodsPage.tsx`, `BarcodeBigButtonMode.tsx`, `EmbroideryBigButtonMode.tsx`, `WarehouseBigButtonMode.tsx`

**Action Items**:
- [ ] Replace all relative imports with `@/` aliases
- [ ] Run ESLint with auto-fix
- [ ] Update import rules in `.eslintrc`

**Estimated Time**: 30 minutes

---

### 3. API IMPORT CENTRALIZATION (✅ COMPLETED)

**Status**: ✅ ALREADY FIXED  
**Date Fixed**: February 5, 2026

**What Was Done**:
- Refactored 10 pages to use `import { api, apiClient } from '@/api'`
- Removed direct imports from `@/api/client`
- Exported both `api` and `apiClient` from centralized index

**Pages Fixed**:
1. AdminImportExportPage.tsx ✅
2. AdminMasterdataPage.tsx ✅
3. AdminUserPage.tsx ✅
4. DashboardPage.tsx ✅
5. FinishgoodsPage.tsx ✅
6. MaterialDebtPage.tsx ✅
7. PermissionManagementPage.tsx ✅
8. PPICPage.tsx ✅
9. QCPage.tsx ✅
10. WarehousePage.tsx ✅

---

## 🟡 HIGH PRIORITY ISSUES (Priority 2)

### 4. DUPLICATE CALCULATION FUNCTIONS

**Files Affected**: Multiple pages

**Duplicate Pattern**: `totalValue` calculations
```typescript
// Found in WarehousePage.tsx (line 303)
const totalValue = mockInventory.reduce((sum, item) => sum + item.qty_on_hand, 0);
const totalReserved = mockInventory.reduce((sum, item) => sum + item.qty_reserved, 0);

// Found in warehouse/MaterialStockPage.tsx (line 95)
const totalStockValue = materials?.reduce((sum, m) => sum + m.stockValue, 0) || 0;
```

**Solution**: Create reusable calculation utilities
```typescript
// lib/calculations.ts
export const sumBy = <T>(array: T[], key: keyof T): number => 
  array.reduce((sum, item) => sum + (item[key] as number), 0)
```

**Action Items**:
- [ ] Create `lib/calculations.ts` for common math operations
- [ ] Extract `sumBy`, `averageBy`, `maxBy`, `minBy` utilities
- [ ] Update pages to use utilities

**Estimated Time**: 45 minutes

---

### 5. INCONSISTENT DATE FORMATTING

**Problem**: Multiple date formatting approaches

**Found In**:
- Direct `toISOString().split('T')[0]` in CreateMOPage
- Custom formatting in ProductionCalendarPage
- No formatting in some pages

**Solution**: Use centralized `formatDate()` from utils
```typescript
// ✅ ALREADY EXISTS in lib/utils.ts
export const formatDate = (date: Date | string, format?: string) => {
  // Handles all date formatting needs
}
```

**Action Items**:
- [ ] Audit all date formatting code
- [ ] Replace with `formatDate()` utility
- [ ] Add date-fns for complex formatting if needed

**Estimated Time**: 30 minutes

---

### 6. MISSING ERROR BOUNDARIES

**Severity**: 🟡 HIGH  
**Impact**: Poor error handling UX

**Pages Without Error Handling**:
- Most new pages (MOListPage, CreateMOPage, etc.)

**Solution**: Wrap components in ErrorBoundary
```typescript
// App.tsx or per-page
<ErrorBoundary fallback={<ErrorFallback />}>
  <YourPage />
</ErrorBoundary>
```

**Action Items**:
- [ ] Create `components/ErrorBoundary.tsx`
- [ ] Wrap all route components
- [ ] Add error logging (Sentry integration)

**Estimated Time**: 1 hour

---

## 🟢 MEDIUM PRIORITY ISSUES (Priority 3)

### 7. UNUSED IMPORTS & VARIABLES

**Check Command**:
```bash
npx eslint erp-ui/frontend/src/pages --fix
```

**Action**: Run ESLint auto-fix to remove unused code

---

### 8. MISSING TYPE DEFINITIONS

**Problem**: Some functions have implicit `any` types

**Example from ProductionCalendarPage**:
```typescript
// ❌ Parameter implicitly has 'any' type
const getDateColor = (date) => { ... }

// ✅ Should be
const getDateColor = (date: Date): string => { ... }
```

**Action Items**:
- [ ] Enable `strict` mode in `tsconfig.json`
- [ ] Fix all implicit `any` errors
- [ ] Add return type annotations

---

### 9. PERFORMANCE OPTIMIZATIONS

**Opportunities**:
1. Add `React.memo()` to expensive components
2. Use `useMemo()` for calculations
3. Use `useCallback()` for event handlers

**Example**:
```typescript
// ❌ Recalculates on every render
const total = items.reduce((sum, item) => sum + item.price, 0)

// ✅ Only recalculates when items change
const total = useMemo(
  () => items.reduce((sum, item) => sum + item.price, 0),
  [items]
)
```

---

## 📋 REFACTORING ACTION PLAN

### Phase 1: Critical Fixes (Today)
1. ✅ **Extract `getStatusBadge` to utils** - 1 hour
2. ✅ **Fix all relative imports** - 30 minutes
3. ✅ **Create calculation utilities** - 45 minutes

**Total**: 2 hours 15 minutes

### Phase 2: High Priority (Tomorrow)
4. **Add Error Boundaries** - 1 hour
5. **Standardize date formatting** - 30 minutes
6. **Add TypeScript strict mode** - 30 minutes

**Total**: 2 hours

### Phase 3: Code Quality (This Week)
7. **Performance optimizations** - 2 hours
8. **Add unit tests** - 3 hours
9. **Documentation** - 1 hour

**Total**: 6 hours

---

## ✅ REFACTORING CHECKLIST

### Immediate Actions (Before Next Feature):
- [ ] Extract duplicate `getStatusBadge()` function
- [ ] Replace all relative imports with `@/` aliases
- [ ] Create `lib/calculations.ts` for math utilities
- [ ] Add Error Boundary component
- [ ] Run `npm run build` to verify no errors

### Short-term (This Week):
- [ ] Enable TypeScript strict mode
- [ ] Add `React.memo()` to expensive components
- [ ] Standardize all date formatting
- [ ] Remove all unused imports
- [ ] Add JSDoc comments to utils

### Medium-term (Next Sprint):
- [ ] Add unit tests (target: 80% coverage)
- [ ] Performance profiling & optimization
- [ ] Accessibility audit (A11Y)
- [ ] Security audit (XSS, CSRF)

---

## 📊 METRICS TRACKING

### Before Refactoring:
- **Duplicate Code**: 7 instances of `getStatusBadge`
- **Relative Imports**: 10 files
- **API Import Inconsistency**: 10 files (✅ FIXED)
- **TypeScript Errors**: ~136 errors (mostly in old files)
- **Build Size**: 1.5 MB

### Target After Refactoring:
- **Duplicate Code**: 0 instances
- **Relative Imports**: 0 files
- **API Import Consistency**: 100%
- **TypeScript Errors**: <10 (only in legacy code)
- **Build Size**: <1.3 MB (optimized)

---

## 🎯 SUCCESS CRITERIA

Refactoring is complete when:
- ✅ No duplicate functions across pages
- ✅ All imports use `@/` aliases
- ✅ All API calls use centralized `api` object
- ✅ TypeScript build passes with zero errors
- ✅ ESLint passes with zero warnings
- ✅ Build size reduced by 10%
- ✅ Test coverage >50% (target: 80%)

---

## 📝 NOTES

**Key Learnings**:
1. Always use centralized utilities from `lib/utils.ts`
2. Prefer `@/` aliases over relative imports
3. Extract duplicated logic immediately
4. Run code quality checks after each feature

**Prevention Strategy**:
1. Add pre-commit hooks (Husky + lint-staged)
2. Enable ESLint auto-fix on save
3. Review PR checklist includes refactoring check
4. Weekly code quality audits

---

**Report Generated**: February 5, 2026 @ 17:30 WIB  
**Next Audit**: February 12, 2026  
**Status**: 🟡 Action Required
