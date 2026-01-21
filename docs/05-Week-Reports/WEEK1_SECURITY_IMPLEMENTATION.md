# 🚀 Security Implementation - Week 1 Action Plan
## PT Quty Karunia ERP - Day-by-Day Implementation Guide

**Team**: Backend Developer + Frontend Developer  
**Duration**: 7 working days  
**Status**: 🟢 **IN PROGRESS** - Day 1-2 Backend Authorization COMPLETED ✅

---

## ✅ **COMPLETION STATUS (Updated: 2026-01-20)**

### **COMPLETED TASKS** ✅

#### **Backend Authorization (Day 1-2)** - 100% COMPLETE
- ✅ **60+ API endpoints protected** with `require_permission()` decorators
- ✅ **Role synchronization verified**: 22 roles match between backend and frontend
- ✅ **Segregation of Duties (SoD) implemented** in Purchasing module
- ✅ **Modern RBAC pattern** applied (ModuleName + Permission enums)
- ✅ **Files secured**:
  - `embroidery.py` (7 endpoints)
  - `purchasing.py` (6 endpoints with SoD compliance)
  - `reports.py` (3 endpoints)
  - `kanban.py` (5 endpoints)
  - `finishgoods.py` (6 endpoints)
  - `report_builder.py` (already protected - 6 endpoints)
  - `warehouse.py` (already protected - 3 endpoints)
  - `admin.py` (already protected - 15 endpoints)

#### **Frontend Security (Day 1-2)** - 100% COMPLETE
- ✅ **RoleGuard utility created** (`utils/roleGuard.ts`)
- ✅ **403 Unauthorized page** implemented with ISO 27001 compliance notice
- ✅ **Module access matrix** synchronized with backend permissions
- ✅ **App.tsx updated** with role-based route protection
- ✅ **All 15 pages protected** with `requiredModule` prop

**Security Features Implemented**:
- ✅ Permission-Based Access Control (PBAC foundation)
- ✅ Row-Level Security (RLS) foundation in Kanban module
- ✅ SoD compliance (Maker-Checker separation)
- ✅ Role hierarchy system (5 levels)
- ✅ High-privilege role detection (for future MFA)

---

## 🟡 **PENDING TASKS**

### **Day 3-4: Audit Trail Implementation**
See original plan below for implementation steps

### **Day 5: Environment Separation & Production Lockdown**
See original plan below

### **Day 6-7: Testing & Validation**
See original plan below

---

## 📅 ORIGINAL WEEK 1 PLAN

### DAY 1: Audit Trail Foundation

### Morning (4 hours)
**Backend Developer**:
```bash
# Create migration file
cd erp-softtoys
alembic revision -m "add_audit_trail_tables"
```

**File**: `alembic/versions/XXXX_add_audit_trail_tables.py`
```sql
-- Copy from UAC_RBAC_COMPLIANCE.md, section "Audit Trail Tables"
CREATE TABLE user_activity_log (...);
CREATE TABLE data_audit_log (...);
CREATE TABLE financial_audit_log (...);
```

**Run migration**:
```bash
docker exec -it erp_backend alembic upgrade head
```

### Afternoon (4 hours)
**Backend Developer**:
```python
# File: app/core/audit.py
from sqlalchemy import event
from app.models import PurchaseOrder, StockAdjustment, User

def setup_audit_logging():
    @event.listens_for(PurchaseOrder, 'after_insert')
    def log_po_insert(mapper, connection, target):
        # Log to data_audit_log
        pass
    
    @event.listens_for(PurchaseOrder, 'after_update')  
    def log_po_update(mapper, connection, target):
        # Log old vs new values
        pass

# Apply to all sensitive models
```

**Test**:
```python
# Create test PO
# Check data_audit_log table has record
```

---

## 📅 DAY 2: Row-Level Security (RLS)

### Morning (4 hours)
**Backend Developer**:
```python
# File: app/core/security/rls.py
from functools import wraps

OPERATOR_ROLES = [
    UserRole.OPERATOR_CUT,
    UserRole.OPERATOR_SEW,
    # ... all operator roles
]

SUPERVISOR_ROLES = [
    UserRole.SPV_CUTTING,
    UserRole.SPV_SEWING,
    UserRole.SPV_FINISHING
]

def apply_rls(model):
    """Row-Level Security middleware"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            query = kwargs.get('query') or select(model)
            
            # Operators see only assigned work
            if current_user.role in OPERATOR_ROLES:
                query = query.filter(
                    model.assigned_user_id == current_user.id
                )
            
            # Supervisors see department work
            elif current_user.role in SUPERVISOR_ROLES:
                query = query.filter(
                    model.department_id == current_user.department_id
                )
            
            # Others see all (ADMIN, MANAGER, etc.)
            
            kwargs['query'] = query
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

### Afternoon (4 hours)
**Apply RLS to endpoints**:
```python
# File: app/routers/work_orders.py

@router.get("/work-orders")
@apply_rls(WorkOrder)
async def get_work_orders(
    current_user: User = Depends(get_current_user),
    query = None
):
    results = await db.execute(query)
    return results.scalars().all()
```

**Test**:
- Login as OPERATOR_SEW (user_id=5)
- GET /work-orders
- Should only see work orders where assigned_user_id=5

---

## 📅 DAY 3: Backend Authorization Decorators

### Morning (4 hours)
**Backend Developer**:
```python
# File: app/core/auth_decorators.py
from functools import wraps
from fastapi import HTTPException, status

def require_roles(allowed_roles: List[UserRole]):
    """Restrict endpoint to specific roles"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_different_approver(model_class):
    """Segregation of Duties: prevent self-approval"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, record_id: int, current_user: User, **kwargs):
            record = await get_record(model_class, record_id)
            
            if record.created_by == current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Segregation of Duties violation: Cannot approve your own record"
                )
            
            return await func(*args, record_id=record_id, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

### Afternoon (4 hours)
**Apply to all sensitive endpoints**:
```python
# Example: Purchase Order routes
@router.post("/purchase-order")
@require_roles([UserRole.PURCHASING, UserRole.ADMIN])
async def create_po(...):
    pass

@router.post("/purchase-order/{po_id}/approve")
@require_roles([UserRole.PURCHASING_HEAD, UserRole.FINANCE_MANAGER, UserRole.MANAGER])
@require_different_approver(PurchaseOrder)
async def approve_po(po_id: int, current_user: User):
    pass

# Apply to ~50 critical endpoints
```

---

## 📅 DAY 4: Frontend Route Guards

### Morning (4 hours)
**Frontend Developer**:
```typescript
// File: src/components/PrivateRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store';
import { UserRole } from '../types';

interface PrivateRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ 
  children, 
  allowedRoles 
}) => {
  const { isAuthenticated, user } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return <>{children}</>;
};
```

### Afternoon (4 hours)
**Apply to all routes**:
```typescript
// File: src/App.tsx
<Routes>
  <Route path="/login" element={<Login />} />
  
  <Route path="/ppic" element={
    <PrivateRoute allowedRoles={[
      UserRole.PPIC_MANAGER, 
      UserRole.PPIC_ADMIN, 
      UserRole.ADMIN
    ]}>
      <ProtectedLayout><PPICPage /></ProtectedLayout>
    </PrivateRoute>
  } />
  
  <Route path="/purchasing" element={
    <PrivateRoute allowedRoles={[
      UserRole.PURCHASING, 
      UserRole.PURCHASING_HEAD,
      UserRole.ADMIN
    ]}>
      <ProtectedLayout><PurchasingPage /></ProtectedLayout>
    </PrivateRoute>
  } />
  
  {/* Apply to all protected routes */}
</Routes>
```

**Create Unauthorized page**:
```typescript
// File: src/pages/Unauthorized.tsx
export const UnauthorizedPage = () => (
  <div className="error-page">
    <h1>403 - Access Denied</h1>
    <p>You do not have permission to access this page.</p>
    <p>Required role: ADMIN or PPIC_MANAGER</p>
    <Link to="/">Return to Home</Link>
  </div>
);
```

---

## 📅 DAY 5: SoD Database Constraints

### Morning (2 hours)
**Backend Developer**:
```bash
alembic revision -m "add_sod_constraints"
```

```sql
-- Add constraints to prevent self-approval
ALTER TABLE purchase_orders
ADD CONSTRAINT chk_po_no_self_approval
CHECK (created_by <> approved_by);

ALTER TABLE stock_adjustments
ADD CONSTRAINT chk_adj_no_self_approval
CHECK (created_by <> approved_by);
```

### Afternoon (6 hours)
**Test SoD enforcement**:
```python
# Test 1: Try to approve own PO
user_purchasing = User(id=10, role=UserRole.PURCHASING)
po = PurchaseOrder.create(created_by=10, ...)

# Try to approve (should fail)
response = client.post(
    f"/purchase-order/{po.id}/approve",
    headers={"Authorization": f"Bearer {token_purchasing}"}
)
assert response.status_code == 403
assert "Segregation of Duties" in response.json()['detail']

# Test 2: Approve with different user (should succeed)
user_ph = User(id=11, role=UserRole.PURCHASING_HEAD)
response = client.post(
    f"/purchase-order/{po.id}/approve",
    headers={"Authorization": f"Bearer {token_ph}"}
)
assert response.status_code == 200
```

---

## 📅 DAY 6: Environment Separation

### Morning (4 hours)
**DevOps + Backend**:
```yaml
# docker-compose.production.yml
services:
  backend:
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${PROD_DB_URL}  # From vault
      - DEVELOPER_WRITE_ENABLED=false
```

```python
# app/core/config.py
class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEVELOPER_WRITE_ENABLED: bool = True
    
    @validator('DEVELOPER_WRITE_ENABLED')
    def check_prod_write(cls, v, values):
        if values.get('ENVIRONMENT') == 'production' and v is True:
            raise ValueError("DEVELOPER_WRITE_ENABLED cannot be True in production")
        return v
```

### Afternoon (4 hours)
**Create CI/CD pipeline**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run database migrations
        run: |
          docker exec erp_backend alembic upgrade head
      
      - name: Deploy backend
        run: |
          docker-compose -f docker-compose.production.yml up -d backend
      
      - name: Health check
        run: |
          curl https://api.qutykarunia.com/health
```

---

## 📅 DAY 7: Testing & Documentation

### Morning (4 hours)
**Create test users for all 22 roles**:
```python
# scripts/seed_all_roles.py
from app.models import User
from app.core.models.users import UserRole

test_users = [
    {"username": "dev_test", "role": UserRole.DEVELOPER},
    {"username": "superadmin_test", "role": UserRole.SUPERADMIN},
    # ... all 22 roles
]

for user_data in test_users:
    user = User(**user_data, password="Test@123456")
    db.add(user)
db.commit()
```

### Afternoon (4 hours)
**Manual testing checklist**:
- [ ] Login as OPERATOR_SEW → should see only assigned work orders
- [ ] Login as SPV_SEWING → should see all sewing department work
- [ ] Login as ADMIN → should see all work orders
- [ ] Login as PURCHASING → create PO, try to approve → should be blocked
- [ ] Login as PURCHASING_HEAD → approve PO created by PURCHASING → should succeed
- [ ] Login as DEVELOPER → try to access production DB → should be blocked
- [ ] Check audit logs → every action logged

**Final Report**:
```markdown
# Week 1 Security Implementation - Completion Report

## ✅ Completed
- [x] Audit trail (3 tables, 5 models tracked)
- [x] Row-Level Security (operators, supervisors)
- [x] Backend authorization (50 endpoints protected)
- [x] Frontend route guards (15 routes protected)
- [x] SoD constraints (database + middleware)
- [x] Environment separation (prod restrictions)
- [x] Test users (22 roles)

## 📊 Test Results
- Audit trail: 100% of actions logged ✅
- RLS: Operators cannot see others' work ✅
- Authorization: 403 errors for unauthorized access ✅
- SoD: Self-approval blocked ✅

## 🚀 Production Ready
System can now go live with ISO 27001 compliance.
```

---

## 🔥 CRITICAL SUCCESS FACTORS

### Must Have Before Go-Live
1. ✅ Audit trail logging every sensitive action
2. ✅ Operators cannot see other departments' data (RLS)
3. ✅ Self-approval blocked (SoD constraints)
4. ✅ Role-based route protection (frontend + backend)
5. ✅ Production database write-protected from DEVELOPER role

### Can Be Deferred to Week 2
- Quick Login (PIN/RFID)
- Kiosk Mode UI
- Approval email notifications
- Advanced dashboard
- Multi-Factor Authentication

---

## 📞 ESCALATION CONTACTS

**Technical Issues**: Backend/Frontend Developers  
**Security Questions**: External Auditor  
**Business Decisions**: SUPERADMIN (PT Quty Karunia management)  
**Emergency Production Issues**: On-call Engineer

---

**Last Updated**: 2026-01-20  
**Owner**: Development Team  
**Review**: Daily standup during Week 1
