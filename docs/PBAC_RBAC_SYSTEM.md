# PBAC + RBAC Access Control System

**Status:** Production Ready ✅  
**Session:** 16 Week 4 Phase 1  
**Date:** January 21, 2026  

---

## 🎯 Overview

ERP Quty Karunia menggunakan **hybrid access control system**:
- **Primary:** PBAC (Permission-Based Access Control)
- **Fallback:** RBAC (Role-Based Access Control)

**Keuntungan hybrid system:**
- ✅ Granular control per-action (PBAC)
- ✅ Backward compatible dengan legacy code (RBAC)
- ✅ Performance optimal dengan Redis caching
- ✅ Easy migration path dari RBAC ke PBAC

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ACCESS CONTROL FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Request → JWT Token → User Authentication              │
│  2. Check if DEVELOPER or SUPERADMIN → ✅ BYPASS           │
│  3. Check PBAC permission_code → Has permission?           │
│     └── YES → ✅ Allow                                      │
│     └── NO  → Check RBAC role                              │
│         └── YES → ✅ Allow                                  │
│         └── NO  → ❌ 403 Forbidden                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚫 Bypass Roles (Full System Access)

Kedua role ini **bypass semua permission checks** dan memiliki akses penuh:

| Role | Purpose | Backend | Frontend |
|------|---------|---------|----------|
| **Developer** | System development, debugging, testing | `UserRole.DEVELOPER` | `user.role === 'Developer'` |
| **Superadmin** | System administration, user management | `UserRole.SUPERADMIN` | `user.role === 'Superadmin'` |

**Implementation:**

**Backend** (`app/services/permission_service.py`):
```python
def has_permission(self, db: Session, user: User, permission_code: str) -> bool:
    # BYPASS: SUPERADMIN and DEVELOPER have all permissions
    if user.role in [UserRole.SUPERADMIN, UserRole.DEVELOPER]:
        return True
    
    # Continue with PBAC check...
```

**Frontend** (`src/components/Sidebar.tsx`):
```typescript
const hasAccess = (item: MenuItem | SubMenuItem): boolean => {
  // BYPASS: Developer and Superadmin have full access
  if (user.role === 'Developer' || user.role === 'Superadmin') {
    return true
  }
  
  // Continue with permission/role check...
}
```

---

## ✅ PBAC (Primary System)

### What is PBAC?

**Permission-Based Access Control** memberikan kontrol granular per-action:
- ✅ User bisa punya permission spesifik tanpa role besar
- ✅ Temporary elevated access (expires_at)
- ✅ Role hierarchy support (SPV inherit operator permissions)
- ✅ Redis caching (5-minute TTL untuk performance)

### Permission Code Format

Format: `{module}.{action}`

**Examples:**
```
cutting.create_wo          → Create work order di Cutting
cutting.allocate_material  → Allocate material di Cutting
sewing.inline_qc           → Perform inline QC di Sewing
admin.manage_users         → Manage users di Admin panel
ppic.approve_mo            → Approve manufacturing order
```

### Backend Usage

**File:** `app/api/v1/[module]/router.py`

```python
from app.core.dependencies import require_permission

@router.post("/cutting/work-orders")
async def create_work_order(
    data: WorkOrderCreate,
    current_user: User = Depends(require_permission("cutting.create_wo")),
    db: Session = Depends(get_db)
):
    """Create new work order - requires cutting.create_wo permission"""
    return {"message": "Work order created"}
```

**Multiple permissions (OR logic):**
```python
from app.core.dependencies import require_any_permission

@router.get("/production/work-orders")
async def list_work_orders(
    current_user: User = Depends(require_any_permission([
        "cutting.view_wo",
        "sewing.view_wo",
        "finishing.view_wo"
    ])),
    db: Session = Depends(get_db)
):
    """List work orders - requires ANY production permission"""
    return {"work_orders": [...]}
```

### Frontend Usage

**File:** `src/components/Sidebar.tsx`

```typescript
const menuItems: MenuItem[] = [
  { 
    icon: <Factory />, 
    label: 'Production', 
    permissions: ['cutting.view_status', 'sewing.view_status'], // ANY logic
    submenu: [
      { 
        icon: <Scissors />, 
        label: 'Cutting', 
        path: '/cutting', 
        permissions: ['cutting.view_status', 'cutting.allocate_material']
      },
      // ...
    ]
  }
]
```

**Permission Store Hook:**
```typescript
import { usePermissionStore } from '@/store'

const Component = () => {
  const { hasPermission } = usePermissionStore()
  
  return (
    <>
      {hasPermission('cutting.create_wo') && (
        <Button>Create Work Order</Button>
      )}
    </>
  )
}
```

---

## 🔄 RBAC (Fallback System)

### What is RBAC?

**Role-Based Access Control** memberikan akses berdasarkan role:
- ✅ Backward compatible dengan existing code
- ✅ Simpler untuk menu-level access
- ✅ Easy to understand
- ⚠️ Less granular (all-or-nothing per role)

### 22 Roles in System

| Level | Role | Description |
|-------|------|-------------|
| **0** | Developer | System development & debugging |
| **1** | Superadmin | System administration |
| **2** | Manager | Top management approver |
| **2** | Finance Manager | Financial approver |
| **3** | Admin | System admin |
| **4** | PPIC Manager | PPIC department head |
| **4** | PPIC Admin | PPIC administrator |
| **4** | SPV Cutting | Cutting supervisor |
| **4** | SPV Sewing | Sewing supervisor |
| **4** | SPV Finishing | Finishing & Packing supervisor |
| **4** | Warehouse Admin | Warehouse administrator |
| **4** | QC Lab | QC laboratory head |
| **4** | Purchasing Head | Purchasing department head |
| **4** | Purchasing | Purchasing staff |
| **5** | Operator Cutting | Cutting operator |
| **5** | Operator Embroidery | Embroidery operator |
| **5** | Operator Sewing | Sewing operator |
| **5** | Operator Finishing | Finishing operator |
| **5** | Operator Packing | Packing operator |
| **5** | QC Inspector | QC inspector |
| **5** | Warehouse Operator | Warehouse operator |
| **5** | Security | Security guard |

### Backend Usage

```python
from app.core.dependencies import require_role, require_any_role

# Single role
@router.get("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_role("Admin"))
):
    return {"message": "Admin only"}

# Multiple roles (OR logic)
@router.post("/approve-order")
async def approve_order(
    current_user: User = Depends(require_any_role("PPIC Manager", "Admin"))
):
    return {"message": "Order approved"}
```

### Frontend Usage

```typescript
const menuItems: MenuItem[] = [
  { 
    icon: <Warehouse />, 
    label: 'Warehouse', 
    path: '/warehouse', 
    roles: [UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP, UserRole.ADMIN]
  }
]
```

---

## 🔀 Role Hierarchy

**Supervisors inherit operator permissions:**

```python
# app/services/permission_service.py

self.role_hierarchy = {
    UserRole.SPV_CUTTING: [
        UserRole.SPV_CUTTING,
        UserRole.OPERATOR_CUT,     # ← Inherit
        UserRole.OPERATOR_EMBRO    # ← Inherit
    ],
    UserRole.SPV_SEWING: [
        UserRole.SPV_SEWING,
        UserRole.OPERATOR_SEW      # ← Inherit
    ],
    UserRole.SPV_FINISHING: [
        UserRole.SPV_FINISHING,
        UserRole.OPERATOR_FINISH,  # ← Inherit
        UserRole.OPERATOR_PACK     # ← Inherit
    ],
    # ...
}
```

**Benefit:** SPV Cutting bisa melakukan semua operasi OPERATOR_CUT + OPERATOR_EMBRO

---

## 🎨 Frontend Menu Configuration

### PBAC Menu (Recommended)

```typescript
{ 
  icon: <Scissors />, 
  label: 'Cutting', 
  path: '/cutting', 
  permissions: ['cutting.view_status', 'cutting.allocate_material']
  // User needs ANY of these permissions to see menu
}
```

### RBAC Menu (Legacy)

```typescript
{ 
  icon: <Warehouse />, 
  label: 'Warehouse', 
  path: '/warehouse', 
  roles: [UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP]
  // User needs to have one of these roles
}
```

### Mixed Menu (Submenu example)

```typescript
{ 
  icon: <Factory />, 
  label: 'Production',
  permissions: ['cutting.view_status', 'sewing.view_status'], // Parent PBAC
  submenu: [
    { 
      icon: <Scissors />, 
      label: 'Cutting', 
      path: '/cutting', 
      permissions: ['cutting.view_status']  // Child PBAC
    },
    { 
      icon: <Palette />, 
      label: 'Embroidery', 
      path: '/embroidery', 
      roles: [UserRole.OPERATOR_EMBRO]  // Child RBAC (legacy)
    }
  ]
}
```

---

## ⚡ Performance: Redis Caching

### Cache Strategy

```python
# Cache key format
"pbac:user:{user_id}:perm:{permission_code}"

# TTL: 5 minutes
cache_ttl = 300

# Example cache keys:
"pbac:user:5:perm:cutting.create_wo"
"pbac:user:12:perm:admin.manage_users"
```

### Cache Invalidation

**When to invalidate:**
- User role changed
- User custom permissions added/removed
- Permission expires (expires_at)

**How to invalidate:**
```python
# Redis client
redis_client.delete(f"pbac:user:{user_id}:*")
```

---

## 🚀 Migration Guide: RBAC → PBAC

### Step 1: Identify Endpoint

**Current (RBAC):**
```python
@router.post("/cutting/work-orders")
async def create_work_order(
    current_user: User = Depends(require_role("SPV Cutting"))
):
    pass
```

### Step 2: Define Permission

Add to permissions table:
```sql
INSERT INTO permissions (code, name, module_name, description)
VALUES (
    'cutting.create_wo',
    'Create Work Order',
    'cutting',
    'Create new work order in cutting department'
);
```

### Step 3: Assign to Roles

```sql
-- Give permission to SPV Cutting role
INSERT INTO role_permissions (role, permission_id, is_granted)
VALUES (
    'SPV Cutting',
    (SELECT id FROM permissions WHERE code = 'cutting.create_wo'),
    TRUE
);
```

### Step 4: Update Endpoint

**New (PBAC):**
```python
@router.post("/cutting/work-orders")
async def create_work_order(
    current_user: User = Depends(require_permission("cutting.create_wo"))
):
    pass
```

### Step 5: Update Frontend

**Old (RBAC):**
```typescript
{ 
  label: 'Cutting', 
  path: '/cutting', 
  roles: [UserRole.SPV_CUTTING, UserRole.OPERATOR_CUT]
}
```

**New (PBAC):**
```typescript
{ 
  label: 'Cutting', 
  path: '/cutting', 
  permissions: ['cutting.view_status', 'cutting.create_wo']
}
```

---

## 🛡️ Security Best Practices

### ✅ DO's

1. **Use PBAC for new endpoints**
   ```python
   require_permission("module.action")
   ```

2. **Use specific permission codes**
   ```
   ✅ cutting.create_wo
   ❌ cutting.all
   ```

3. **Use require_any_permission for OR logic**
   ```python
   require_any_permission(["cutting.view_wo", "sewing.view_wo"])
   ```

4. **Always bypass for Developer/Superadmin**
   ```python
   if user.role in [UserRole.DEVELOPER, UserRole.SUPERADMIN]:
       return True
   ```

5. **Cache permission checks**
   ```python
   has_permission(db, user, "cutting.create_wo", use_cache=True)
   ```

### ❌ DON'Ts

1. **Don't mix PBAC and RBAC in same endpoint**
   ```python
   # ❌ BAD
   @router.post("/endpoint")
   async def bad_endpoint(
       user1: User = Depends(require_permission("module.action")),
       user2: User = Depends(require_role("Admin"))
   ):
       pass
   
   # ✅ GOOD - use one or the other
   @router.post("/endpoint")
   async def good_endpoint(
       user: User = Depends(require_permission("module.action"))
   ):
       pass
   ```

2. **Don't hardcode role checks**
   ```typescript
   // ❌ BAD
   if (user.role === 'SPV Cutting') {
       showButton()
   }
   
   // ✅ GOOD
   if (hasPermission('cutting.create_wo')) {
       showButton()
   }
   ```

3. **Don't forget bypass roles**
   ```python
   # ❌ BAD - Developer/Superadmin blocked
   if permission_code not in user_permissions:
       raise HTTPException(403)
   
   # ✅ GOOD
   if user.role in [UserRole.DEVELOPER, UserRole.SUPERADMIN]:
       return True
   if permission_code not in user_permissions:
       raise HTTPException(403)
   ```

---

## 📋 Summary

### PBAC vs RBAC Comparison

| Feature | PBAC | RBAC |
|---------|------|------|
| **Granularity** | ✅ Per-action | ⚠️ Per-role (coarse) |
| **Flexibility** | ✅ High | ⚠️ Medium |
| **Performance** | ✅ Cached (fast) | ✅ Direct (fast) |
| **Complexity** | ⚠️ Higher | ✅ Lower |
| **Migration** | ✅ Gradual | N/A |
| **Use Case** | ✅ New endpoints | ⚠️ Legacy/simple |

### When to Use What?

| Scenario | Recommended |
|----------|-------------|
| New API endpoint | ✅ PBAC (`require_permission`) |
| Legacy endpoint (not migrated yet) | 🔄 RBAC (`require_role`) |
| Simple menu-level access | 🔄 RBAC (`roles: [...]`) |
| Granular button/action control | ✅ PBAC (`permissions: [...]`) |
| Developer/Superadmin access | 🚫 Bypass (no check needed) |

### System Status

| Component | PBAC Ready | RBAC Fallback | Bypass |
|-----------|------------|---------------|--------|
| **Backend** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Frontend** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Permission Service** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Redis Cache** | ✅ Yes | N/A | N/A |
| **Role Hierarchy** | ✅ Yes | ✅ Yes | N/A |

---

## 📚 Related Documentation

- [UAC_RBAC_COMPLIANCE.md](./UAC_RBAC_COMPLIANCE.md) - Role-based access compliance
- [SEGREGATION_OF_DUTIES_MATRIX.md](./SEGREGATION_OF_DUTIES_MATRIX.md) - SoD matrix
- [SECURITY_IMPLEMENTATION_REPORT_2026-01-20.md](./SECURITY_IMPLEMENTATION_REPORT_2026-01-20.md) - Security report

---

**Last Updated:** January 21, 2026  
**Maintainer:** IT Development Team  
**Status:** Production Ready ✅
