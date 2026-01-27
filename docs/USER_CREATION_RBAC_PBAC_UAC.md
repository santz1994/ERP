# User Creation & Access Control (RBAC/PBAC/UAC) Guide

## 📋 Overview

The ERP system uses **3-layer security model**:
- **RBAC (Role-Based Access Control)**: 22 roles with predefined permissions
- **PBAC (Permission-Based Access Control)**: Fine-grained, individual permissions  
- **UAC (User Access Control)**: User-specific permission overrides

---

## 🏢 USER HIERARCHY (22 Roles - 5 Levels)

### Level 0: System Development & Protection
```
DEVELOPER
├─ Full database access
├─ CI/CD pipeline control
├─ Schema changes
└─ Production READ-ONLY
```

### Level 1: System Administration
```
SUPERADMIN
├─ User management
├─ System configuration
├─ Security policies
└─ Emergency access (all modules)
```

### Level 2: Top Management (Approvers)
```
MANAGER              → View all + Approve PO >= $5K
FINANCE_MANAGER      → Financial approvals + Stock adjustments
```

### Level 3: System Admin
```
ADMIN
├─ Full system access (except CI/CD)
├─ User management
└─ Audit trails
```

### Level 4: Department Management
```
PPIC_MANAGER         → Production planning & approvals
PPIC_ADMIN          → MO data entry & BOM updates
PURCHASING_HEAD     → PO < $5K approvals
WAREHOUSE_ADMIN     → Inventory management
QC_LAB              → Lab head & test execution
SPV_CUTTING         → Cutting supervisor
SPV_SEWING          → Sewing supervisor
SPV_FINISHING       → Finishing supervisor
PURCHASING          → Purchase officer
```

### Level 5: Operations & Staff
```
OPERATOR_CUT        → Cutting operations
OPERATOR_EMBRO      → Embroidery operations
OPERATOR_SEW        → Sewing operations
OPERATOR_FINISH     → Finishing operations
OPERATOR_PACK       → Packing operations
QC_INSPECTOR        → Quality inspection
WAREHOUSE_OP        → Warehouse operations
SECURITY            → Security guard/access
```

---

## ✅ REQUIREMENTS TO CREATE USER

### 1. **RBAC - Role Assignment (Required)**
User MUST have one of 22 roles:
```python
from app.core.models.users import UserRole

user = User(
    username="operator_john",
    email="john@qutykarunia.com",
    role=UserRole.OPERATOR_CUT,  # ← MUST BE ONE OF 22 ROLES
    full_name="John Operator",
    is_active=True,
    is_verified=True
)
```

**Validation**: Role must exist in `UserRole` enum

---

### 2. **PBAC - Permission Check (Automatic)**

Once role assigned, user automatically gets permissions from `ROLE_PERMISSIONS` matrix:

```python
# Example: OPERATOR_CUT gets these permissions:
{
    "cutting": ["view", "execute"],
    "dashboard": ["view"],
    "reports": ["view"],
    "barcode": ["view"]
}

# CANNOT access:
❌ "admin" - No permission
❌ "purchasing" - No permission
❌ "warehouse" - No permission
```

**Source**: `app/core/permissions.py` - `ROLE_PERMISSIONS` dict

---

### 3. **UAC - User Overrides (Optional)**

User can have **custom permissions** (exceptions to role defaults):

#### A. Grant Extra Permission
```sql
-- Give OPERATOR_CUT extra "warehouse.view" permission
INSERT INTO user_custom_permissions (
    user_id, permission_id, is_granted, reason, expires_at
) VALUES (
    123,  -- operator_john's ID
    456,  -- warehouse.view permission ID
    TRUE,
    'Temporary access for inventory audit',
    NOW() + INTERVAL '30 days'  -- Expires in 30 days
);
```

#### B. Revoke Permission
```sql
-- Remove PPIC_MANAGER's "ppic.delete_mo" permission temporarily
INSERT INTO user_custom_permissions (
    user_id, permission_id, is_granted, reason, expires_at
) VALUES (
    789,  -- ppic_mgr's ID
    890,  -- ppic.delete_mo permission ID
    FALSE,  -- REVOKE
    'Under investigation - temp restricted',
    NOW() + INTERVAL '7 days'  -- Expires in 7 days
);
```

**Where Stored**: `user_custom_permissions` table

---

## 🔐 CREATION PROCESS (Step-by-Step)

### Via Python (Backend)

```python
from app.core.database import SessionLocal
from app.core.models.users import User, UserRole
from app.core.security import PasswordUtils

def create_user_with_validation(
    username: str,
    email: str,
    full_name: str,
    role: UserRole,
    password: str,
    department: str = None
) -> User:
    """Create user with full RBAC validation"""
    
    db = SessionLocal()
    
    # 1. Validate role exists
    if role not in UserRole:
        raise ValueError(f"Invalid role: {role}")
    
    # 2. Check user doesn't exist
    existing = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        raise ValueError("User or email already exists")
    
    # 3. Hash password (max 72 bytes for bcrypt)
    hashed_pwd = PasswordUtils.hash_password(password[:72])
    
    # 4. Create user with role
    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,  # ← Automatic PBAC permissions assigned
        department=department,
        hashed_password=hashed_pwd,
        is_active=True,
        is_verified=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ User created: {username} ({role})")
    print(f"   Permissions: {get_user_permissions(new_user)}")
    
    db.close()
    return new_user
```

### Via API Endpoint

```bash
POST /api/v1/admin/users
Authorization: Bearer <superadmin_token>

{
    "username": "spv_cutting_01",
    "email": "supervisor@qutykarunia.com",
    "full_name": "Supervisor Cutting #1",
    "role": "SPV Cutting",
    "password": "TempPassword@123",
    "department": "Cutting"
}

RESPONSE (201 Created):
{
    "id": 101,
    "username": "spv_cutting_01",
    "email": "supervisor@qutykarunia.com",
    "role": "SPV Cutting",
    "is_active": true,
    "created_at": "2026-01-27T10:00:00Z",
    "permissions": {
        "cutting": ["view", "create", "update", "execute"],
        "dashboard": ["view"],
        "reports": ["view"]
    }
}
```

---

## 🎯 ACCESS CONTROL MATRIX (22 Roles × 18 Modules)

| Module | Developer | SuperAdmin | Manager | Admin | PPIC_Mgr | PPIC_Admin | SPV_* | Operators |
|--------|-----------|------------|---------|-------|----------|------------|-------|-----------|
| **Dashboard** | ✅ VIEW | ✅ FULL | ✅ FULL | ✅ FULL | ✅ VIEW | ✅ VIEW | ✅ VIEW | ✅ VIEW |
| **Admin** | ✅ FULL | ✅ FULL | ❌ | ✅ FULL | ❌ | ❌ | ❌ | ❌ |
| **Audit** | ✅ FULL | ✅ FULL | ✅ VIEW | ✅ VIEW | ❌ | ❌ | ❌ | ❌ |
| **PPIC** | ✅ FULL | ✅ FULL | ✅ CRUD | ✅ FULL | ✅ FULL | ✅ CRUD | ❌ | ❌ |
| **Purchasing** | ✅ FULL | ✅ FULL | ✅ APPROVE | ✅ FULL | ❌ | ❌ | ❌ | ❌ |
| **Warehouse** | ✅ FULL | ✅ FULL | ✅ APPROVE | ✅ FULL | ❌ | ❌ | ❌ | ❌ |
| **Cutting** | ✅ FULL | ✅ FULL | ✅ VIEW | ✅ FULL | ✅ VIEW | ❌ | ✅ FULL | ✅ EXECUTE |
| **Sewing** | ✅ FULL | ✅ FULL | ✅ VIEW | ✅ FULL | ✅ VIEW | ❌ | ✅ FULL | ✅ EXECUTE |
| **Finishing** | ✅ FULL | ✅ FULL | ✅ VIEW | ✅ FULL | ✅ VIEW | ❌ | ✅ FULL | ✅ EXECUTE |
| **QC** | ✅ FULL | ✅ FULL | ✅ VIEW | ✅ FULL | ✅ VIEW | ❌ | ❌ | ✅ APPROVE |
| **Barcode** | ✅ FULL | ✅ FULL | ❌ | ✅ FULL | ❌ | ❌ | ❌ | ✅ EXECUTE |
| **Reports** | ✅ FULL | ✅ FULL | ✅ FULL | ✅ FULL | ✅ VIEW | ❌ | ✅ VIEW | ❌ |

---

## 🔍 VERIFY USER PERMISSIONS

### Check via Python
```python
from app.core.database import SessionLocal
from app.core.models.users import User
from app.core.permissions import ROLE_PERMISSIONS

db = SessionLocal()
user = db.query(User).filter(User.username == "operator_john").first()

if user:
    permissions = ROLE_PERMISSIONS.get(user.role, {})
    print(f"User: {user.full_name}")
    print(f"Role: {user.role.value}")
    print(f"Permissions:")
    for module, perms in permissions.items():
        print(f"  - {module}: {perms}")
        
    # Check for custom overrides
    custom_perms = db.query(UserCustomPermission).filter(
        UserCustomPermission.user_id == user.id
    ).all()
    if custom_perms:
        print(f"Custom Overrides: {len(custom_perms)}")
```

### Check via SQL
```sql
-- Get user's role permissions
SELECT u.username, u.role, rp.permission_id, p.code, p.name
FROM users u
LEFT JOIN role_permissions rp ON rp.role = u.role
LEFT JOIN permissions p ON p.id = rp.permission_id
WHERE u.username = 'operator_john';

-- Get user's custom overrides
SELECT ucp.user_id, p.code, p.name, ucp.is_granted, ucp.expires_at
FROM user_custom_permissions ucp
JOIN permissions p ON p.id = ucp.permission_id
WHERE ucp.user_id = (SELECT id FROM users WHERE username = 'operator_john');
```

---

## ⚠️ IMPORTANT RULES

### ✅ DO
- ✅ Always assign ONE role (required)
- ✅ Use role hierarchy for department access
- ✅ Set expiry dates on temporary permissions
- ✅ Log all UAC changes in audit trail
- ✅ Verify user exists before UAC override
- ✅ Use password[:72] for bcrypt compatibility

### ❌ DON'T
- ❌ Create user without role
- ❌ Bypass role permissions directly
- ❌ Store passwords in plain text
- ❌ Grant permissions beyond user's role permanently
- ❌ Skip audit logging for UAC changes
- ❌ Use generic passwords

---

## 📊 CURRENT SEEDED USERS (22 Users)

All demo users already created with `seed_all_users.py`:

| Username | Role | Password | Status |
|----------|------|----------|--------|
| admin | Admin | password123 | ✅ Active |
| superadmin | Superadmin | password123 | ✅ Active |
| developer | Developer | password123 | ✅ Active |
| manager | Manager | password123 | ✅ Active |
| finance_mgr | Finance Manager | password123 | ✅ Active |
| ppic_mgr | PPIC Manager | password123 | ✅ Active |
| ppic_admin | PPIC Admin | password123 | ✅ Active |
| spv_cutting | SPV Cutting | password123 | ✅ Active |
| spv_sewing | SPV Sewing | password123 | ✅ Active |
| spv_finishing | SPV Finishing | password123 | ✅ Active |
| wh_admin | Warehouse Admin | password123 | ✅ Active |
| qc_lab | QC Lab | password123 | ✅ Active |
| purchasing_head | Purchasing Head | password123 | ✅ Active |
| purchasing | Purchasing | password123 | ✅ Active |
| operator_cut | Operator Cutting | password123 | ✅ Active |
| operator_embro | Operator Embroidery | password123 | ✅ Active |
| operator_sew | Operator Sewing | password123 | ✅ Active |
| operator_finish | Operator Finishing | password123 | ✅ Active |
| operator_pack | Operator Packing | password123 | ✅ Active |
| qc_inspector | QC Inspector | password123 | ✅ Active |
| wh_operator | Warehouse Operator | password123 | ✅ Active |
| security | Security | password123 | ✅ Active |

---

## 🚀 NEXT STEPS

1. **Verify users seeded**: `python -c "from app.core.database import SessionLocal; from app.core.models.users import User; db = SessionLocal(); print(f'Total users: {db.query(User).count()}')"`

2. **Check permissions**: Review `docs/SESSION_25_RBAC_PBAC_UAC_TEST_REPORT.md`

3. **Test access**: Login with different roles and verify module access

4. **Create new users**: Use API endpoint or `create_user_with_validation()` function

5. **Grant UAC overrides**: When needed, use SQL inserts or API endpoint
