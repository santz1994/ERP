# ERP TESTING - LOGIN, ACCESS CONTROL, & FUNCTIONALITY DEEPDIVE

## 📊 SEEDING STATUS: ✅ COMPLETE

**22 Users Successfully Seeded**
```
✅ Total Users: 22
✅ Unique Roles: 22
✅ Status: All Active & Verified
✅ Password: password123 (all users)
```

---

## 🧪 TEST PLAN OVERVIEW

### Phase 1: Authentication & Login
- [ ] Test login with each of 22 user roles
- [ ] Verify password validation
- [ ] Check JWT token generation
- [ ] Verify token expiration

### Phase 2: RBAC (Role-Based Access Control)
- [ ] Test role hierarchy (Level 0 > Level 1 > ... > Level 5)
- [ ] Verify each role has correct permissions
- [ ] Test permission fallback/bypass

### Phase 3: PBAC (Permission-Based Access Control)  
- [ ] Test granular permissions per module
- [ ] Test permission inheritance
- [ ] Verify temporary permission overrides

### Phase 4: Module Access & Buttons
- [ ] Dashboard access by role
- [ ] Admin panel access control
- [ ] Module-specific buttons (Create, Update, Delete, Approve)
- [ ] Action button visibility per role

### Phase 5: API Endpoints
- [ ] Test 150+ endpoints with different roles
- [ ] Verify 403 Forbidden for unauthorized access
- [ ] Test 200 OK for authorized access

---

## 🔑 TEST CREDENTIALS

### All Users: password123

| # | Username | Role | Level | Department |
|---|----------|------|-------|------------|
| 1 | developer | DEVELOPER | 0 | System |
| 2 | superadmin | SUPERADMIN | 1 | System |
| 3 | manager | MANAGER | 2 | Management |
| 4 | finance_mgr | FINANCE_MANAGER | 2 | Finance |
| 5 | admin | ADMIN | 3 | System |
| 6 | ppic_mgr | PPIC_MANAGER | 4 | PPIC |
| 7 | ppic_admin | PPIC_ADMIN | 4 | PPIC |
| 8 | spv_cutting | SPV_CUTTING | 4 | Cutting |
| 9 | spv_sewing | SPV_SEWING | 4 | Sewing |
| 10 | spv_finishing | SPV_FINISHING | 4 | Finishing |
| 11 | wh_admin | WAREHOUSE_ADMIN | 4 | Warehouse |
| 12 | qc_lab | QC_LAB | 4 | Quality |
| 13 | purchasing_head | PURCHASING_HEAD | 4 | Purchasing |
| 14 | purchasing | PURCHASING | 4 | Purchasing |
| 15 | operator_cut | OPERATOR_CUT | 5 | Cutting |
| 16 | operator_embro | OPERATOR_EMBRO | 5 | Embroidery |
| 17 | operator_sew | OPERATOR_SEW | 5 | Sewing |
| 18 | operator_finish | OPERATOR_FINISH | 5 | Finishing |
| 19 | operator_pack | OPERATOR_PACK | 5 | Packing |
| 20 | qc_inspector | QC_INSPECTOR | 5 | Quality |
| 21 | wh_operator | WAREHOUSE_OP | 5 | Warehouse |
| 22 | security | SECURITY | 5 | Security |

---

## 🧪 PHASE 1: AUTHENTICATION TESTS

### Test 1.1: Basic Login - Admin User
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}

EXPECTED: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 5,
  "username": "admin",
  "role": "ADMIN"
}
```

### Test 1.2: Invalid Password
```bash
POST http://localhost:8000/api/v1/auth/login
{
  "username": "admin",
  "password": "wrongpassword"
}

EXPECTED: 401 Unauthorized
{
  "detail": "Invalid credentials"
}
```

### Test 1.3: Non-existent User
```bash
POST http://localhost:8000/api/v1/auth/login
{
  "username": "nonexistent",
  "password": "password123"
}

EXPECTED: 401 Unauthorized
```

### Test 1.4: Login All 22 Users
```python
# Python Test Script
import requests

BASE_URL = "http://localhost:8000/api/v1"
users = [
    ("developer", "password123"),
    ("superadmin", "password123"),
    ("manager", "password123"),
    ("finance_mgr", "password123"),
    ("admin", "password123"),
    ("ppic_mgr", "password123"),
    ("ppic_admin", "password123"),
    ("spv_cutting", "password123"),
    ("spv_sewing", "password123"),
    ("spv_finishing", "password123"),
    ("wh_admin", "password123"),
    ("qc_lab", "password123"),
    ("purchasing_head", "password123"),
    ("purchasing", "password123"),
    ("operator_cut", "password123"),
    ("operator_embro", "password123"),
    ("operator_sew", "password123"),
    ("operator_finish", "password123"),
    ("operator_pack", "password123"),
    ("qc_inspector", "password123"),
    ("wh_operator", "password123"),
    ("security", "password123"),
]

print("\n" + "="*70)
print("PHASE 1: LOGIN TEST - ALL 22 USERS")
print("="*70 + "\n")

for username, password in users:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token", "")[:20] + "..."
        print(f"✅ {username:20} - Token: {token}")
    else:
        print(f"❌ {username:20} - Status: {response.status_code}")

print("\n" + "="*70)
```

---

## 🔐 PHASE 2: RBAC & PERMISSION TESTS

### Test 2.1: Dashboard Access by Role

```bash
# Admin can access dashboard
GET http://localhost:8000/api/v1/dashboard/stats
Authorization: Bearer <admin_token>

EXPECTED: 200 OK

# Operator can access dashboard (read-only)
GET http://localhost:8000/api/v1/dashboard/stats
Authorization: Bearer <operator_cut_token>

EXPECTED: 200 OK (view permission)
```

### Test 2.2: Admin Panel - Developer & SuperAdmin Only

```bash
# Developer can access admin panel
GET http://localhost:8000/api/v1/admin/users
Authorization: Bearer <developer_token>

EXPECTED: 200 OK

# SuperAdmin can access admin panel
GET http://localhost:8000/api/v1/admin/users
Authorization: Bearer <superadmin_token>

EXPECTED: 200 OK

# Operator CANNOT access admin panel
GET http://localhost:8000/api/v1/admin/users
Authorization: Bearer <operator_cut_token>

EXPECTED: 403 Forbidden
{
  "detail": "Insufficient permissions"
}
```

### Test 2.3: Module-Specific Access

```bash
# PPIC Manager can access PPIC module
GET http://localhost:8000/api/v1/ppic/manufacturing-orders
Authorization: Bearer <ppic_mgr_token>

EXPECTED: 200 OK

# Operator Cutting CANNOT access PPIC
GET http://localhost:8000/api/v1/ppic/manufacturing-orders
Authorization: Bearer <operator_cut_token>

EXPECTED: 403 Forbidden

# Warehouse Admin can access Warehouse
GET http://localhost:8000/api/v1/warehouse/inventory
Authorization: Bearer <wh_admin_token>

EXPECTED: 200 OK

# Operator Cutting CANNOT access Warehouse
GET http://localhost:8000/api/v1/warehouse/inventory
Authorization: Bearer <operator_cut_token>

EXPECTED: 403 Forbidden
```

---

## 📋 PHASE 3: ACTION BUTTONS & MUTATIONS

### Test 3.1: Create Operations

```bash
# Admin can CREATE users
POST http://localhost:8000/api/v1/admin/users
Authorization: Bearer <admin_token>
{
  "username": "test_user",
  "email": "test@example.com",
  "role": "OPERATOR_CUT",
  "password": "TempPass@123"
}

EXPECTED: 201 Created

# Operator cannot CREATE users
POST http://localhost:8000/api/v1/admin/users
Authorization: Bearer <operator_cut_token>

EXPECTED: 403 Forbidden
```

### Test 3.2: Update Operations

```bash
# PPIC Manager can UPDATE manufacturing orders (their own module)
PATCH http://localhost:8000/api/v1/ppic/manufacturing-orders/1
Authorization: Bearer <ppic_mgr_token>
{
  "status": "IN_PROGRESS"
}

EXPECTED: 200 OK

# Operator Cutting CANNOT UPDATE PPIC orders
PATCH http://localhost:8000/api/v1/ppic/manufacturing-orders/1
Authorization: Bearer <operator_cut_token>

EXPECTED: 403 Forbidden
```

### Test 3.3: Approval Operations

```bash
# Manager can APPROVE purchase orders >= $5K
POST http://localhost:8000/api/v1/purchasing/orders/1/approve
Authorization: Bearer <manager_token>

EXPECTED: 200 OK

# Operator CANNOT approve orders
POST http://localhost:8000/api/v1/purchasing/orders/1/approve
Authorization: Bearer <operator_cut_token>

EXPECTED: 403 Forbidden

# Finance Manager can APPROVE stock adjustments
POST http://localhost:8000/api/v1/warehouse/adjustments/1/approve
Authorization: Bearer <finance_mgr_token>

EXPECTED: 200 OK
```

### Test 3.4: Delete Operations

```bash
# Admin can DELETE users
DELETE http://localhost:8000/api/v1/admin/users/123
Authorization: Bearer <admin_token>

EXPECTED: 204 No Content

# SuperAdmin can DELETE (emergency override)
DELETE http://localhost:8000/api/v1/admin/users/123
Authorization: Bearer <superadmin_token>

EXPECTED: 204 No Content

# Manager CANNOT delete users
DELETE http://localhost:8000/api/v1/admin/users/123
Authorization: Bearer <manager_token>

EXPECTED: 403 Forbidden
```

---

## 🚀 PHASE 4: COMPREHENSIVE ENDPOINT TEST

### Test 4.1: Critical Endpoints by Role

```python
# Python Comprehensive Test
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test Matrix: Endpoints that should work for each role
test_matrix = {
    "admin": [
        ("GET", "/admin/users", 200),
        ("GET", "/admin/permissions", 200),
        ("GET", "/audit/logs", 200),
        ("GET", "/dashboard/stats", 200),
    ],
    "ppic_mgr": [
        ("GET", "/ppic/manufacturing-orders", 200),
        ("GET", "/dashboard/stats", 200),
        ("GET", "/ppic/manufacturing-orders", 200),
        ("POST", "/admin/users", 403),  # Should be forbidden
    ],
    "operator_cut": [
        ("GET", "/dashboard/stats", 200),
        ("GET", "/admin/users", 403),  # Should be forbidden
        ("POST", "/ppic/manufacturing-orders", 403),  # Should be forbidden
    ],
    "wh_admin": [
        ("GET", "/warehouse/inventory", 200),
        ("POST", "/warehouse/stock-moves", 200),
        ("GET", "/admin/users", 403),  # Should be forbidden
    ],
}

def run_endpoint_tests():
    print("\n" + "="*70)
    print("PHASE 4: COMPREHENSIVE ENDPOINT TESTING")
    print("="*70 + "\n")
    
    for username, endpoints in test_matrix.items():
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": "password123"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ {username}: Login failed")
            continue
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"\n🔹 Testing {username}:")
        print("-" * 70)
        
        for method, endpoint, expected_status in endpoints:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json={})
            
            status = response.status_code
            result = "✅" if status == expected_status else "❌"
            
            print(f"  {result} {method:6} {endpoint:40} - {status} (expected {expected_status})")
```

---

## 📊 DEEPDIVE TEST CHECKLIST

### Authentication (5 tests)
- [x] Login with each of 22 users
- [ ] JWT token expiration
- [ ] Token refresh
- [ ] Session management
- [ ] Password reset flow

### RBAC Access (10 tests)
- [ ] Developer full access
- [ ] SuperAdmin full access
- [ ] Manager limited access
- [ ] Admin access verification
- [ ] Department managers access
- [ ] Supervisors access
- [ ] Operators limited access
- [ ] Role hierarchy enforcement
- [ ] Permission inheritance
- [ ] Fallback/bypass logic

### PBAC Granular (15 tests)
- [ ] Admin panel permissions
- [ ] PPIC module permissions
- [ ] Warehouse module permissions
- [ ] Quality module permissions
- [ ] Purchasing module permissions
- [ ] Production module permissions
- [ ] Custom user overrides (UAC)
- [ ] Temporary permission expiry
- [ ] Permission caching
- [ ] Permission refresh
- [ ] Module-specific buttons
- [ ] CRUD operation tests
- [ ] Approval workflow tests
- [ ] View-only restrictions
- [ ] Execute-only restrictions

### API Endpoints (30+ tests)
- [ ] 150+ endpoints with different roles
- [ ] 200 OK for authorized
- [ ] 403 Forbidden for unauthorized
- [ ] 401 Unauthorized for no token
- [ ] Response validation
- [ ] Error handling
- [ ] Rate limiting
- [ ] CORS headers

### Frontend Buttons (20+ tests)
- [ ] Create buttons visibility
- [ ] Update buttons visibility
- [ ] Delete buttons visibility
- [ ] Approve buttons visibility
- [ ] Submit buttons visibility
- [ ] Cancel buttons availability
- [ ] Button state transitions
- [ ] Modal dialogs
- [ ] Form validation
- [ ] Success messages
- [ ] Error messages
- [ ] Loading states
- [ ] Disabled states
- [ ] Conditional rendering

---

## 🎯 SUCCESS CRITERIA

✅ **All tests should PASS:**
1. 22/22 users can login
2. Each user gets correct permissions
3. All 150+ endpoints respond correctly
4. Buttons show/hide based on permissions
5. RBAC fallback works
6. PBAC fine-grained permissions work
7. UAC overrides work
8. No security bypasses
9. Performance < 200ms per request
10. No data leaks between roles

---

## 📝 EXECUTION INSTRUCTIONS

### 1. Start Backend
```bash
cd D:\Project\ERP2026\erp-softtoys
python -m uvicorn app.main:app --reload
# Server starts on http://localhost:8000
```

### 2. Run API Tests
```bash
# Run comprehensive test suite
python -c "# (Use code above)"

# Or use Postman collection
# Import: /tests/ERP_API_Tests.postman_collection.json
```

### 3. Manual Testing
- Open http://localhost:3000 (frontend)
- Login with each of 22 users
- Test button visibility
- Test module access
- Check permission errors

### 4. Record Results
```markdown
## Test Results Summary

| Test Area | Passed | Failed | Notes |
|-----------|--------|--------|-------|
| Authentication | 22/22 | 0 | ✅ All users login OK |
| RBAC | 10/10 | 0 | ✅ Role hierarchy OK |
| PBAC | 15/15 | 0 | ✅ Permissions OK |
| API Endpoints | 150/150 | 0 | ✅ All working |
| Frontend Buttons | 20/20 | 0 | ✅ Visibility correct |
| **TOTAL** | **227/227** | **0** | **✅ READY FOR PRODUCTION** |
```

---

## 🚀 NEXT STEPS AFTER TESTING

1. ✅ All tests passing → **Production Deployment**
2. Load testing (1000+ concurrent users)
3. Security audit (penetration testing)
4. Performance optimization
5. User acceptance testing (UAT)
6. Go-live preparation
