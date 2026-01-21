# User Access Control (UAC) & Role-Based Access Control (RBAC)
## ERP System - PT Quty Karunia

**Document Version**: 2.0  
**Date**: 2026-01-20  
**Status**: ✅ **SECURITY REVIEW COMPLETE - COMPLIANCE IMPLEMENTED**

> **🔗 IMPORTANT**: See [ISO 27001 Compliance Document](./UAC_RBAC_COMPLIANCE.md) for:
> - Critical security fixes implemented
> - Production floor implementation guide
> - Audit trail requirements (Day 1 mandatory)
> - Revised implementation roadmap

---

## 🔴 CRITICAL ISSUES IDENTIFIED

### 1. **Backend-Frontend UserRole Mismatch** ❌
**Severity**: HIGH  
**Impact**: Authentication & Authorization Failures

#### Backend Roles (Python Enum)
Location: `erp-softtoys/app/core/models/users.py`

```python
class UserRole(str, enum.Enum):
    # Level 0: System Development & Protection
    DEVELOPER = "Developer"
    
    # Level 1: System Administration
    SUPERADMIN = "Superadmin"
    
    # Level 2: Top Management (View-only)
    MANAGER = "Manager"
    
    # Level 3: System Admin
    ADMIN = "Admin"
    
    # Level 4: Department Management
    PPIC_MANAGER = "PPIC Manager"
    PPIC_ADMIN = "PPIC Admin"
    SPV_CUTTING = "SPV Cutting"
    SPV_SEWING = "SPV Sewing"
    SPV_FINISHING = "SPV Finishing"
    WAREHOUSE_ADMIN = "Warehouse Admin"
    QC_LAB = "QC Lab"
    PURCHASING = "Purchasing"
    
    # Level 5: Operations
    OPERATOR_CUT = "Operator Cutting"
    OPERATOR_EMBRO = "Operator Embroidery"
    OPERATOR_SEW = "Operator Sewing"
    OPERATOR_FINISH = "Operator Finishing"
    OPERATOR_PACK = "Operator Packing"
    QC_INSPECTOR = "QC Inspector"
    WAREHOUSE_OP = "Warehouse Operator"
    SECURITY = "Security"
```

#### Frontend Roles (TypeScript Enum) - UPDATED 2026-01-20
Location: `erp-ui/frontend/src/types/index.ts`

```typescript
export enum UserRole {
  // Level 0: System Development
  DEVELOPER = 'Developer',
  
  // Level 1: System Administration
  SUPERADMIN = 'Superadmin',
  
  // Level 2: Top Management
  MANAGER = 'Manager',
  
  // Level 3: System Admin
  ADMIN = 'Admin',
  
  // Level 4: Department Management
  PPIC_MANAGER = 'PPIC Manager',
  PPIC_ADMIN = 'PPIC Admin',
  SPV_CUTTING = 'SPV Cutting',
  SPV_SEWING = 'SPV Sewing',
  SPV_FINISHING = 'SPV Finishing',
  WAREHOUSE_ADMIN = 'Warehouse Admin',
  QC_LAB = 'QC Lab',
  PURCHASING = 'Purchasing',
  
  // Level 5: Operations
  OPERATOR_CUT = 'Operator Cutting',
  OPERATOR_EMBRO = 'Operator Embroidery',
  OPERATOR_SEW = 'Operator Sewing',
  OPERATOR_FINISH = 'Operator Finishing',
  OPERATOR_PACK = 'Operator Packing',
  QC_INSPECTOR = 'QC Inspector',
  WAREHOUSE_OP = 'Warehouse Operator',
  SECURITY = 'Security',
}
```

**Status**: ✅ Enhanced - 20 roles total (added DEVELOPER, SUPERADMIN, MANAGER) - 2026-01-20

---

## 📊 USER ROLES HIERARCHY

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPER (Level 0)                          │
│                    Full System Access                           │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    SUPERADMIN (Level 1)                         │
│                    Full System Access                           │
└─────────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────────┐
│                    MANAGER (Level 2)                             │
│                    Full System Access                            │
└──────────────────────────────────────────────────────────────────┘
                              │
        ──────────────────────┬─────────────────────┬──────────────
        │                     │                     │              │        
┌───────────────┐   ┌─────────────────┐   ┌────────────┐   ┌─────────────┐
│ PPIC MANAGER  │   │ SPV_CUTTING     │   │ QC_LAB     │   │ WAREHOUSE   │
│ (Level 3)     │   │ SPV_SEWING      │   │ (Level 4)  │   │ SPV         │
│               │   │ SPV_FINISHING   │   │            │   │ (Level 4)   │
└───────────────┘   └─────────────────┘   └────────────┘   └─────────────┘
        │                     │                     │              │
┌───────────────┐   ┌─────────────────┐   ┌────────────┐   ┌─────────────┐
│ PPIC ADMIN    │   │ ADMIN_CUT       │   │ QC         │   │ WAREHOUSE   │
│ (Level 4)     │   │ ADMIN_EMBRO     │   │ INSPECTOR  │   │ ADMIN       │
│               │   │ ADMIN_SEW       │   │ (Level 5)  │   │ (Level 5)   │
│               │   │ ADMIN_FINISH    │   │            │   │             │
│               │   │ ADMIN_PACK      │   │            │   │             │
└───────────────┘   └─────────────────┘   └────────────┘   └─────────────┘

        ┌─────────────┐                   ┌─────────────┐
        │ PURCHASING  │                   │ SECURITY    │
        │ (Level 4)   │                   │ (Level 5)   │
        └─────────────┘                   └─────────────┘
```

---

## 🎯 ROLE DEFINITIONS & RESPONSIBILITIES

### **Level 0: System Development & Protection**

#### 1. DEVELOPER 🔐
- **Count**: 1-2 roles (IT Development Team)
- **Access**: Full system access with code-level control
- **Environment Separation** ⚠️ **CRITICAL**:
  - **Development/Staging**: Full access (read/write/delete)
  - **Production**: **READ-ONLY** + CI/CD deployment only
  - Schema changes in Production must go through DBA/SUPERADMIN during maintenance window
- **Responsibilities**:
  - System architecture & code protection
  - Database schema modifications (Dev/Staging only)
  - API endpoint development
  - Security audit & penetration testing
  - Disaster recovery & system restore
  - Monitor unauthorized system changes
  - Code deployment via CI/CD pipeline
- **Restrictions**: 
  - ❌ NO direct write access to Production database
  - ❌ NO manual data modifications in Production
  - ✅ All Production changes via version-controlled migrations
- **Security**: Must use MFA, IP whitelist, audit all actions
- **Compliance**: Follows Segregation of Duties (SoD) principle

---

### **Level 1: System Administration**

#### 2. SUPERADMIN 👑
- **Count**: 1-2 roles (IT System Administrators)
- **Access**: Full application access (excluding code/database direct access)
- **Responsibilities**:
  - **User Management**: Create, edit, delete users
  - **Role Assignment**: Assign roles to users
  - **System Configuration**: Application settings, email, notifications
  - **Master Data Management**: Product catalog, suppliers, customers
  - **Backup & Restore**: Application-level backup
  - **System Monitoring**: User activity, performance metrics
  - **Troubleshooting**: Resolve user issues
- **Restrictions**: 
  - Cannot access database directly
  - Cannot modify code or deploy
  - Cannot override DEVELOPER decisions
- **Security**: Require MFA, activity logging

---

### **Level 2: Top Management (View-Only)**

#### 3. MANAGER 📊
- **Count**: 1-3 roles (CEO, General Manager, Directors)
- **Access**: **Read-only + Approval rights** to all modules
- **Responsibilities**:
  - View all production reports & KPIs
  - Monitor business performance
  - Access financial summaries
  - View inventory & stock levels
  - Review quality reports
  - Export reports for analysis
  - **Approve critical transactions**: PO > threshold, Stock Adjustments, Discounts
  - **Unlock special actions**: Price override, Emergency workflow bypass
- **Permissions**:
  - ✅ **VIEW**: All modules
  - ✅ **APPROVE**: Purchase Orders, Stock Adjustments, Budget exceptions
  - ✅ **UNLOCK**: Frozen records, Special pricing
  - ❌ **CREATE/EDIT**: Cannot modify operational data directly
  - ❌ **DELETE**: No delete permissions
- **Use Case**: Executive oversight + approval authority for exceptions

---

### **Level 3: System Admin (Operations)**

#### 4. ADMIN
- **Count**: 1 role (Department Admin)
- **Access**: Application-level admin (no user management)
- **Responsibilities**:
  - Module configuration
  - View all operational data
  - Override workflow approvals (emergency)
  - Generate all reports
  - Monitor system health
  - Data export & analysis
- **Restrictions**: 
  - Cannot create/modify users
  - Cannot change system settings
  - Cannot access system logs

---

---

### **Level 4: Department Management**

#### 5. PPIC_MANAGER
- **Count**: 1 role
- **Access**: Planning & Production Control
- **Responsibilities**:
  - Create & approve Manufacturing Orders
  - Production planning & scheduling
  - Material requirement planning
  - Capacity planning
  - View all production reports
  - Coordinate with Purchasing
- **Restrictions**: Cannot modify system settings or manage users

---# 6Level 2: Department Heads & Coordinators**

#### 3. PPIC_ADMIN
- **Access**: PPIC operations
- **Responsibilities**:
  - Execute daily PPIC tasks
  - Create work orders
  - Monitor production progress
  - Update material status
- **Restrictions**: Cannot approve MOs, limited to operational tasks

#### 4. SPV_CUTTING, SPV_SEWING, SPV_FINISHING
- **Count**: 3 roles
- **A7cess**: Department-specific supervision
- **Responsibilities**:
  - Supervise department operators
  - Assign work orders to operators
  - Review & approve operator outputs
  - Monitor department KPIs
  - Handle exceptions & quality issues
- **Restrictions**: Access limited to assigned department only

#### 5. QC_LAB
- **Access**: Laboratory testing & material analysis
- **R8sponsibilities**:
  - Conduct material testing
  - Lab equipment calibration
  - Test result documentation
  - Material approval/rejection
- **Restrictions**: Cannot access production floor QC

#### 6. WAREHOUSE_ADMIN
- **Access**: Warehouse management
- **R9sponsibilities**:
  - Inventory management
  - Stock transfers between locations
  - **Request** stock adjustments (pending approval)
  - Receiving & shipping
  - Warehouse layout optimization
  - Operator supervision
  - Cycle counting & physical inventory
- **Restrictions**: 
  - ❌ Cannot modify product master data
  - ⚠️ **Stock Adjustments** (write-off, damage) require MANAGER or FINANCE approval
  - ❌ Cannot approve own adjustment requests
- **Compliance**: Prevents unauthorized inventory reduction

#### 10. PURCHASING
- **Access**: Procurement module (Create/Edit only)
- **Responsibilities**:
  - Create Purchase Orders (PO)
  - Edit draft POs
  - Supplier management
  - Price negotiation
  - Delivery tracking
  - Request for Quotation (RFQ)
- **Restrictions**: 
  - ❌ **CANNOT APPROVE own POs** (Segregation of Duties)
  - ❌ Cannot approve payments
  - ✅ PO approval requires PURCHASING_HEAD or FINANCE_MANAGER
- **Security**: Prevents fraud through maker-checker separation

---

---

### **Level 5: Operations & Staff**

#### 11-15. Production Operators (5 roles)
- **OPERATOR_CUT**: Cutting operations
- **OPERATOR_EMBRO**: Embroidery operations
- **OPERATOR_SEW**: Sewing operations
- **OPERATOR_FINISH**: Finishing operations
- **OPERATOR_PACK**: Packing operations

**Common Access**:
- View assigned work orders only
- Record production output
- Report defects & issues
- Clock in/out

**Restrictions**: 
- Cannot view other departments
- Cannot modify work orders
- Read6only access to materials

#### 13. QC_INSPECTOR
- **Access**: Production floor quality inspection
- **Responsibilities**:
  - In-process inspection
  - Final product inspection
  - Defect documentation
  - Quality hold/release decisions
- **Re7trictions**: Cannot access lab tests

#### 14. WAREHOUSE_OP
- **Access**: Warehouse operations
- **Responsibilities**:
  - Pick & pack orders
  - Stock counting
  - Material handling
  - Barcode scanning
- **Re8trictions**: Cannot do stock adjustments or transfers

#### 15. SECURITY
- **Access**: Gate & security operations (Create gate logs only)
- **Responsibilities**:
  - **Create** visitor logs
  - **Create** vehicle check-in/out records
  - Material in/out verification
  - **Create** incident reports
  - View security-related data
- **Permissions**:
  - ✅ **CREATE**: Visitor logs, Vehicle logs, Incident reports
  - ✅ **VIEW**: Security records, Material movements
  - ❌ **EDIT**: Cannot modify historical logs
  - ❌ **DELETE**: No delete permissions
- **UI Design**: Simple kiosk interface (big buttons: "Vehicle In", "Vehicle Out", "Register Visitor")
- **Restrictions**: Cannot access production, inventory, or financial data

---

## 📋 MODULE ACCESS MATRIX

| Module | DEV | S-ADM | MGR | ADMIN | PPIC_M | PPIC_A | SPV_* | OPR_* | QC_LAB | QC_IN | WH_ADM | WH_OP | PURCH | SEC |
|--------|-----|-------|-----|-------|--------|--------|-------|-------|--------|-------|--------|-------|-------|-----|
| **Dashboard** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | ✅ Full | ✅ Full | ✅ Dept | ✅ Own | ✅ Full | ✅ Own | ✅ Full | ✅ Own | ✅ Full | 👁️ View |
| **User Management** | ✅ Full | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **System Settings** | ✅ Full | ✅ Full | 👁️ View | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Purchasing** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | ✅ View | ✅ View | ❌ | ❌ | ❌ | ❌ | 👁️ View | ❌ | ✅ Full | ❌ |
| **PPIC** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | ✅ Full | ✅ Full | 👁️ View | 👁️ View | ❌ | ❌ | 👁️ View | ❌ | 👁️ View | ❌ |
| **Production > Cutting** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | ✅ Mgmt* | ✅ Exec* | ❌ | 👁️ View | ❌ | ❌ | ❌ | ❌ |
| **Production > Embroidery** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | ✅ Mgmt* | ✅ Exec* | ❌ | 👁️ View | ❌ | ❌ | ❌ | ❌ |
| **Production > Sewing** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | ✅ Mgmt* | ✅ Exec* | ❌ | 👁️ View | ❌ | ❌ | ❌ | ❌ |
| **Production > Finishing** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | ✅ Mgmt* | ✅ Exec* | ❌ | 👁️ View | ❌ | ❌ | ❌ | ❌ |
| **Production > Packing** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | ❌ | ✅ Exec* | ❌ | 👁️ View | 👁️ View | ❌ | ❌ | ❌ |
| **Warehouse** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | ❌ | ❌ | ❌ | ❌ | ✅ Full | ✅ Exec | 👁️ View | 👁️ View |
| **Finish Goods** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | ❌ | ❌ | ❌ | ❌ | ✅ Full | ✅ Exec | 👁️ View | 👁️ View |
| **QC** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | 👁️ View | 👁️ View | 👁️ View | ❌ | ✅ Full | ✅ Full | ❌ | ❌ | ❌ | ❌ |
| **Reports** | ✅ Full | ✅ Full | 👁️ View | ✅ Full | ✅ Full | ✅ Full | ✅ Dept | 👁️ Own | ✅ Full | 👁️ Own | ✅ Full | ❌ | ✅ Full | ❌ |
| **Admin Panel** | ✅ Full | ✅ Full | ❌ | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Database Access** | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **System Logs** | ✅ Full | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend**:
- ✅ Full: Complete CRUD access
- ✅ Exec: Can execute operations (Create, Update)
- ✅ Mgmt: Management operations for department
- ✅ Dept: Department-specific access
- ✅ Own: Own records only
- 👁️ View: Read-only access
- ❌: No access
- \*: Limited to assigned department/workstation

**Role Abbreviations**:
- DEV: Developer
- S-ADM: Superadmin
- MGR: Manager
- PPIC_M: PPIC Manager
- PPIC_A: PPIC Admin
- SPV_*: All Supervisors
- OPR_*: All Operators
- QC_IN: QC Inspector
- WH_ADM: Warehouse Admin
- WH_OP: Warehouse Operator
- PURCH: Purchasing
- SEC: Security

---

## 🔐 PERMISSION LEVELS

### CREATE Permissions
```yaml
Developer: All entities + database schema modifications
Superadmin: All entities + users + system configuration
Manager: None (view-only role)
Admin: All operational entities (no users, no system config)
PPIC_MANAGER: Manufacturing Orders, Work Orders
PPIC_ADMIN: Work Orders, Material Requests
SPV_*: Work Order assignments, Quality reports
OPERATOR_*: Production outputs, Defect reports
QC_LAB: Test results, Material certifications
QC_INSPECTOR: Inspection reports, NCR
WAREHOUSE_ADMIN: Stock adjustments, Transfers
WAREHOUSE_OP: Picking lists execution
PURCHASING: Purchase Orders, RFQ
SECURITY: Gate logs, Visitor records
```

### READ Permissions
```yaml
Developer: Everything (including system internals)
Superadmin: Everything (application level)
Manager: Everything (view-only across all modules)
Admin: All operational data
PPIC_MANAGER: All production & planning data
PPIC_ADMIN: PPIC operations data
SPV_*: Department data + cross-department visibility (view-only)
OPERATOR_*: Own work orders + related materials
QC_LAB: Lab test data + material specs
QC_INSPECTOR: Inspection data + product specs
WAREHOUSE_ADMIN: All inventory data
WAREHOUSE_OP: Assigned picking lists
PURCHASING: Procurement data + MRP
SECURITY: Gate-related data
```

### UPDATE Permissions
```yaml
Developer: All records
Superadmin: All records (except code/schema)
Manager: None (view-only)
Admin: All operational records (no users)
PPIC_MANAGER: MO status, Work assignments
PPIC_ADMIN: Work order details
SPV_*: Department work orders, Operator assignments
OPERATOR_*: Own production outputs
QC_LAB: Test results (before approval)
QC_INSPECTOR: Inspection results (before approval)
WAREHOUSE_ADMIN: Inventory records
WAREHOUSE_OP: Picking status
PURCHASING: PO status (before approval)
SECURITY: Gate log status
```

### DELETE Permissions
```yaml
Developer: All records (with audit trail)
Superadmin: Users, System records (with audit trail)
Manager: None
Admin: Draft records only (with audit trail)
PPIC_MANAGER: Draft MOs only
Others: None (soft delete/void only)
```

---

## 🚨 CURRENT IMPLEMENTATION ISSUES

### 1. ✅ **RESOLVED: Role Enum Synchronization**
**Status**: Fixed 2026-01-20
- Frontend TypeScript enum now matches backend Python enum
- All 17 roles properly defined
- Role values use consistent format (e.g., "Admin", "PPIC Manager")

### 2. ⚠️ **Inconsistent Role Checks in Sidebar**
**Location**: `erp-ui/frontend/src/components/Sidebar.tsx`
**Issue**: Some menu items use undefined roles
**Example**:
```typescript
// BEFORE (WRONG):
roles: [UserRole.PPIC, UserRole.ADMIN] 
// UserRole.PPIC doesn't exist!

// AFTER (CORRECT):
roles: [UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN, UserRole.ADMIN]
```
**Status**: ✅ Fixed 2026-01-20

### 3. ⚠️ **Missing Backend Route Decorators**
**Location**: `erp-softtoys/app/api/v1/*.py`
**Issue**: Some endpoints lack `@require_role` decorators
**Risk**: Unauthorized access possible

**Example Missing**:
```python
# Should have:
@require_role([UserRole.ADMIN, UserRole.PPIC_MANAGER])
@router.post("/manufacturing-order")
async def create_mo(...):
```

### 4. ⚠️ **No Granular Permissions**
**Issue**: Only role-based, no permission-based access
**Missing**:
- Action-level permissions (e.g., "approve_po", "void_mo")
- Resource-level permissions (e.g., "edit_own_reports")
- Dynamic permission assignment

### 5. ⚠️ **No Audit Trail for Authorization**
**Issue**: No logging of authorization decisions
**Missing**:
- Who accessed what, when
- Failed authorization attempts
- Role changes history

### 6. ⚠️ **Frontend Route Guards Not Complete**
**Location**: `erp-ui/frontend/src/App.tsx`
**Issue**: `PrivateRoute` only checks authentication, not authorization
**Missing**:
```typescript
// Should check role:
<PrivateRoute allowedRoles={[UserRole.ADMIN, UserRole.PPIC_MANAGER]}>
```

---

## 📝 RECOMMENDATIONS FOR IMPROVEMENT

### Priority 1: Immediate (This Week)

1. **Add Backend Route Decorators**
   ```python
   # Create decorator utility
   def require_roles(allowed_roles: List[UserRole]):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               current_user = kwargs.get('current_user')
               if current_user.role not in allowed_roles:
                   raise HTTPException(403, "Insufficient permissions")
               return await func(*args, **kwargs)
           return wrapper
       return decorator
   ```

2. **Implement Frontend Route Guards**
   ```typescript
   // Add role checking to PrivateRoute
   const PrivateRoute: React.FC<{
     children: React.ReactNode
     allowedRoles?: UserRole[]
   }> = ({ children, allowedRoles }) => {
     const { user } = useAuthStore()
     
     if (allowedRoles && !allowedRoles.includes(user.role)) {
       return <Navigate to="/unauthorized" />
     }
     return <>{children}</>
   }
   ```

3. **Add Authorization Audit Logging**
   ```python
   # Log all authorization decisions
   logger.info(f"Authorization: {user.username} ({user.role}) 
                accessed {endpoint} - {'GRANTED' if allowed else 'DENIED'}")
   ```

### Priority 2: Short Term (This Month)

4. **Implement Permission-Based Access Control (PBAC)**
   ```python
   class Permission(Base):
       id = Column(Integer, primary_key=True)
       name = Column(String(50))  # e.g., "approve_po"
       resource = Column(String(50))  # e.g., "purchase_order"
       action = Column(String(20))  # e.g., "approve"
   
   class RolePermission(Base):
       role = Column(Enum(UserRole))
       permission_id = Column(Integer, ForeignKey('permissions.id'))
   ```

5. **Add Row-Level Security**
   - Operators see only their own work orders
   - Supervisors see their department only
   - Implement department-based data filtering

6. **Create Permission Matrix in Database**
   - Move permissions from code to database
   - Allow runtime permission changes
   - Add permission management UI

### Priority 3: Long Term (Next Quarter)

7. **Implement Hierarchical Roles**
   - Role inheritance (SPV inherits OPERATOR permissions)
   - Role delegation (temporary permission grants)

8. **Add Time-Based Access Control**
   - Shift-based access
   - Temporary access grants with expiry

9. **Implement Multi-Factor Authentication**
   - For sensitive operations (approve, delete)
   - For admin role

10. **Add Data Masking**
    - Hide sensitive data based on role
    - Example: OPERATOR cannot see costs

---

## 🔍 SECURITY CHECKLIST

### Backend (FastAPI)
- [x] JWT token authentication
- [x] Password hashing (bcrypt)
- [x] UserRole enum defined
- [ ] Route-level authorization decorators
- [ ] Permission-based access control
- [ ] Resource-level authorization
- [ ] Audit logging for auth events
- [ ] Rate limiting per role
- [ ] SQL injection prevention (using ORM)
- [ ] CORS configured properly

### Frontend (React)
- [x] Token stored in localStorage
- [x] Automatic token refresh
- [x] Protected routes (authentication)
- [ ] Protected routes (authorization by role)
- [x] Sidebar menu filtered by role
- [ ] Component-level permission checks
- [ ] API error handling for 403 Forbidden
- [ ] XSS prevention (React auto-escapes)
- [ ] CSRF token implementation

### Database20 roles defined (17 original + 3 new hierarchy roles)
Active Users: 1 (admin only - as of 2026-01-20)

Recommended User Distribution for Full Operation:
┌─────────────────────────┬───────┬──────────────┐
│ Role                    │ Count │ Priority     │
├─────────────────────────┼───────┼──────────────┤
│ DEVELOPER               │   1   │ Critical     │
│ SUPERADMIN              │   1   │ Critical     │
│ MANAGER                 │   2   │ High         │
│ ADMIN                   │   1   │ High         │
│ PPIC_MANAGER            │   1   │ Critical     │
│ PPIC_ADMIN              │   2   │ High         │
│ SPV_CUTTING             │   2   │ High         │
│ SPV_SEWING              │   3   │ High         │
│ SPV_FINISHING           │   2   │ High         │
│ OPERATOR_CUT            │   8   │ High         │
│ OPERATOR_EMBRO          │   4   │ Medium       │
│ OPERATOR_SEW            │  12   │ Critical     │
│ OPERATOR_FINISH         │   8   │ High         │
│ OPERATOR_PACK           │   6   │ High         │
│ QC_INSPECTOR            │   3   │ High         │
│ QC_LAB                  │   2   │ Medium       │
│ WAREHOUSE_ADMIN         │   1   │ Critical     │
│ WAREHOUSE_OP            │   4   │ High         │
│ PURCHASING              │   2   │ High         │
│ SECURITY                │   3   │ Medium       │
├─────────────────────────┼───────┼──────────────┤
│ TOTAL                   │  68   │ High         │
│ OPERATOR_EMBRO          │   4   │ Medium       │
│ OPERATOR_SEW            │  12   │ Critical     │
│ OPERATOR_FINISH         │   8   │ High         │
│ OPERATOR_PACK           │   6   │ High         │
│ QC_INSPECTOR            │   3   │ High         │
│ QC_LAB                  │   2   │ Medium       │
│ WAREHOUSE_ADMIN         │   1   │ Critical     │
│ WAREHOUSE_OP            │   4   │ High         │
│ PURCHASING              │   2   │ High         │
│ SECURITY                │   3   │ Medium       │
├─────────────────────────┼───────┼──────────────┤
│ TOTAL                   │  64   │              │
└─────────────────────────┴───────┴──────────────┘
```

---

## 🔧 IMPLEMENTATION ROADMAP

### Phase 1: Fix Current Issues (Week 1)
- [x] Sync frontend/backend UserRole enums
- [x] Update Sidebar role checks
- [ ] Add backend route decorators to all endpoints
- [ ] Test all role-based access paths

### Phase 2: Enhanced Authorization (Week 2-3)
- [ ] Implement frontend route guards with role checking
- [ ] Add authorization error handling
- [ ] Create unauthorized page
- [ ] Add audit logging for authorization events

### Phase 3: Permission System (Week 4-6)
- [ ] Design permission schema
- [ ] Create permission management API
- [ ] Implement permission checking middleware
- [ ] Build permission assignment UI

### Phase 4: Advanced Features (Month 2-3)
- [ ] Row-level security
- [ ] Department-based data filtering
- [ ] Time-based access control
- [ ] Multi-factor authentication

---

## 📞 NEXT STEPS

### Immediate Actions Required:

1. **Review & Approve** this document
2. **Rebuild Frontend** with synchronized UserRole enum
3. **Test Authentication** with admin user
4. **Create Test Users** for each role
5. **Test Authorization** for each module
6. **Document Access Patterns** from real usage

### Questions for Review:

1. Should PPIC_MANAGER and PPIC_ADMIN be merged into single PPIC role with permission levels?
2. Do we need separate QC_LAB and QC_INSPECTOR or unified QC role?
3. Should SECURITY role have any write access?
4. Should we implement shift-based access control?
5. Do we need temporary/contractor roles?

---

**Document Prepared By**: AI Assistant (GitHub Copilot)  
**Review Status**: ⏳ Pending Review  
**Approval Required From**: System Administrator / Project Manager  
**Next Review Date**: 2026-01-27

