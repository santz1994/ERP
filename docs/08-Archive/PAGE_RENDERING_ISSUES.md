# Page Rendering Issues - Root Cause Analysis

## Issue Summary
**9 out of 14 API endpoints failing** causing pages to show "Page under development" or errors.

## Root Causes

### 1. Dashboard (500 Error)
**Problem:** Queries `mv_dashboard_stats` materialized view that doesn't exist in database  
**File:** `app/api/v1/dashboard.py` line 40-48  
**Fix:** Create materialized view OR use fallback query (already implemented)

**SQL Error:**
```
sqlalchemy.exc.InternalError: (psycopg2.errors.InFailedSqlTransaction) 
current transaction is aborted, commands ignored until end of transaction block
```

### 2. Production Modules (404 Errors)
**Problem:** Frontend uses wrong API paths  
**Expected by Frontend:**
- `/api/v1/cutting/work-orders`
- `/api/v1/sewing/work-orders`
- `/api/v1/finishing/work-orders`
- `/api/v1/packing/work-orders`

**Actual Backend Routes:**
- `/api/v1/production/cutting/...`
- `/api/v1/production/sewing/...`
- `/api/v1/production/finishing/...`
- `/api/v1/production/packing/...`

**Frontend Files to Fix:**
- `erp-ui/frontend/src/pages/CuttingPage.tsx`
- `erp-ui/frontend/src/pages/SewingPage.tsx`
- `erp-ui/frontend/src/pages/FinishingPage.tsx`
- `erp-ui/frontend/src/pages/PackingPage.tsx`

### 3. Warehouse (404 Errors)
**Problem:** Frontend endpoint paths don't exist  
**Expected:** `/warehouse/materials` → **404**  
**Available:** `/warehouse/stock/{product_id}` (requires product_id parameter)

**Frontend File:** `erp-ui/frontend/src/pages/WarehousePage.tsx`

### 4. QC/Finish Goods (404 Errors)
**Problem:** Endpoints don't exist yet  
**Expected:**
- `/qc/inspections` → **404**
- `/finishgoods/shipments` → **404**

**Backend Routers:** Missing `quality_router` implementation for `/qc/inspections`

## Quick Fix Priority

### HIGH PRIORITY (Breaks multiple pages):
1. **Fix Dashboard materialized view error** (affects Dashboard page)
2. **Update frontend API paths** for production modules (affects 4 pages)

### MEDIUM PRIORITY:
3. **Add Warehouse list endpoint** (affects Warehouse page)
4. **Implement QC inspections endpoint** (affects QC page)

### LOW PRIORITY:
5. **Implement Finish Goods shipments endpoint** (affects Finish Goods page)

## Test Results
✅ **Working Endpoints (5/14):**
- PPIC `/ppic/manufacturing-orders`
- Embroidery `/embroidery/work-orders`  
- Purchasing `/purchasing/purchase-orders`
- Kanban `/kanban/cards`
- Admin `/admin/users`

❌ **Failed Endpoints (9/14):**
- Dashboard `/dashboard/stats` (500)
- Cutting `/cutting/work-orders` (404)
- Sewing `/sewing/work-orders` (404)
- Finishing `/finishing/work-orders` (404)
- Packing `/packing/work-orders` (404)
- Warehouse Materials `/warehouse/materials` (404)
- Warehouse Stock `/warehouse/stock/1` (404)
- Finish Goods `/finishgoods/shipments` (404)
- QC `/qc/inspections` (404)

## Impact
**Why pages show "Page under development":**
1. Frontend component loads
2. React Query (`useQuery`) tries to fetch data from API
3. API returns 404/500 error
4. Frontend catches error → shows placeholder/error message
5. Full page components exist (SewingPage = 518 lines) but can't display without data

## Next Steps
Execute fixes in order:
1. Fix dashboard materialized view
2. Update frontend API paths for production modules
3. Restart Docker containers to apply changes
4. Re-run test to verify all pages render correctly
