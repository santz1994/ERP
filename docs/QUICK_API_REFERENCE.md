---
# 🚀 QUICK START - PHASE 1 PRODUCTION READY
## API Reference Card for Developers

---

## ⚡ 30-SECOND START

```bash
# 1. Navigate to project
cd d:\Project\ERP2026

# 2. Start services
docker-compose up -d

# 3. View API docs
# Visit: http://localhost:8000/docs

# 4. Run tests (optional)
cd erp-softtoys
python run_tests.py --auth
```

---

## 🔑 QUICK API REFERENCE

### **Authentication**

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "Pass123!",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "Pass123!"
  }'

# Result: {
#   "access_token": "eyJ0eXAi...",
#   "refresh_token": "eyJ0eXAi...",
#   "token_type": "bearer"
# }

# Get current user (use access_token from login)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### **Admin Operations**

```bash
# List users (admin only)
curl -X GET "http://localhost:8000/api/v1/admin/users?skip=0&limit=10" \
  -H "Authorization: Bearer <admin_token>"

# Get user details
curl -X GET http://localhost:8000/api/v1/admin/users/1 \
  -H "Authorization: Bearer <admin_token>"

# Update user
curl -X PUT http://localhost:8000/api/v1/admin/users/1 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "role": "operator_cutting"
  }'

# Filter by role
curl -X GET "http://localhost:8000/api/v1/admin/users/role/operator_cutting" \
  -H "Authorization: Bearer <admin_token>"
```

### **Production Planning (PPIC)**

```bash
# Create manufacturing order
curl -X POST http://localhost:8000/api/v1/ppic/manufacturing-order \
  -H "Authorization: Bearer <ppic_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "so_line_id": 1,
    "product_id": 2,
    "qty_planned": 100,
    "routing_type": "Route1",
    "batch_number": "BATCH-001"
  }'

# List manufacturing orders
curl -X GET "http://localhost:8000/api/v1/ppic/manufacturing-orders?status=DRAFT" \
  -H "Authorization: Bearer <ppic_token>"

# Approve manufacturing order
curl -X POST http://localhost:8000/api/v1/ppic/manufacturing-order/1/approve \
  -H "Authorization: Bearer <ppic_token>"
```

### **Warehouse Management**

```bash
# Check stock
curl -X GET "http://localhost:8000/api/v1/warehouse/stock/1?location_id=5" \
  -H "Authorization: Bearer <warehouse_token>"

# Create stock transfer (QT-09 protocol)
curl -X POST http://localhost:8000/api/v1/warehouse/transfer \
  -H "Authorization: Bearer <warehouse_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_dept": "Cutting",
    "to_dept": "Sewing",
    "product_id": 2,
    "qty": 50,
    "batch_number": "BATCH-001",
    "reference_doc": "SPK-123"
  }'

# List locations
curl -X GET http://localhost:8000/api/v1/warehouse/locations \
  -H "Authorization: Bearer <warehouse_token>"
```

---

## 🔐 AUTHENTICATION HEADERS

All API calls (except /auth/register and /auth/login) require:

```
Authorization: Bearer <access_token>
```

**Getting Access Token**:
```bash
# Login to get tokens
POST /api/v1/auth/login
{
  "username": "john",
  "password": "Pass123!"
}

# Response includes:
# "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."  ← USE THIS
```

---

## 👥 USER ROLES (16 Available)

```
Admin               - Full system access
ppic_manager        - Production planning
ppic_admin          - Planning admin
spv_cutting         - Cutting supervisor
spv_sewing          - Sewing supervisor
spv_finishing       - Finishing supervisor
operator_cutting    - Cutting machine operator
operator_embroidery - Embroidery operator
operator_sewing     - Sewing operator
operator_finishing  - Finishing operator
operator_packing    - Packing operator
qc_inspector        - Quality inspector
qc_lab              - QC lab technician
warehouse_admin     - Warehouse admin
warehouse_operator  - Warehouse staff
purchasing_support  - Purchasing clerk
```

---

## ❌ ERROR CODES

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request body & parameters |
| 401 | Unauthorized | Include Authorization header |
| 403 | Forbidden | Check user role for endpoint |
| 404 | Not Found | Verify resource ID exists |
| 422 | Validation Error | Check field types & formats |
| 429 | Too Many Attempts | Account locked (try after 15 min) |

**Example Error Response**:
```json
{
  "detail": "Insufficient permissions for this endpoint"
}
```

---

## 📊 ENDPOINTS SUMMARY

### Authentication (6)
- POST /auth/register - Create user
- POST /auth/login - Get tokens
- POST /auth/refresh - Refresh token
- GET /auth/me - Get current user
- POST /auth/change-password - Change password
- POST /auth/logout - Logout

### Admin (7)
- GET /admin/users - List users
- GET /admin/users/{id} - Get user
- PUT /admin/users/{id} - Update user
- POST /admin/users/{id}/deactivate - Deactivate
- POST /admin/users/{id}/reactivate - Reactivate
- POST /admin/users/{id}/reset-password - Reset pwd
- GET /admin/users/role/{role} - Filter by role

### PPIC (4)
- POST /ppic/manufacturing-order - Create MO
- GET /ppic/manufacturing-order/{id} - Get MO
- GET /ppic/manufacturing-orders - List MO
- POST /ppic/manufacturing-order/{id}/approve - Approve MO

### Warehouse (5+)
- GET /warehouse/stock/{product_id} - Check stock
- POST /warehouse/transfer - Transfer stock
- GET /warehouse/locations - List locations
- POST /warehouse/receive - Receive goods
- GET /warehouse/stock-history - Stock audit

---

## 🧪 TESTING

```bash
# Run all tests
cd erp-softtoys
python run_tests.py

# Run specific test class
python run_tests.py --auth

# Run with coverage
python run_tests.py --coverage
```

---

## 📁 KEY FILES

```
/docs/
├── PHASE_1_AUTH_GUIDE.md       ← Full guide
├── PHASE_1_COMPLETION_REPORT.md ← Details
└── IMPLEMENTATION_STATUS.md     ← Status

/erp-softtoys/
├── app/api/v1/
│   ├── auth.py                 ← Auth endpoints
│   ├── admin.py                ← Admin endpoints
│   ├── ppic.py                 ← PPIC endpoints
│   └── warehouse.py            ← Warehouse endpoints
├── app/core/
│   ├── security.py             ← JWT & bcrypt
│   ├── dependencies.py         ← Auth logic
│   └── models/users.py         ← User model
└── tests/
    └── test_auth.py            ← Test suite
```

---

## 🔐 SECURITY FEATURES

- ✅ JWT tokens (24h access, 7d refresh)
- ✅ Bcrypt password hashing
- ✅ Account lockout (5 failed → 15 min lock)
- ✅ Role-based access control
- ✅ Login audit trail
- ✅ Input validation on all endpoints

---

## 🚨 COMMON ISSUES

### Issue: 401 Unauthorized
**Solution**: Include valid Authorization header
```
Authorization: Bearer <access_token>
```

### Issue: 403 Forbidden
**Solution**: User doesn't have required role for endpoint

### Issue: 429 Too Many Requests
**Solution**: Account locked (5 failed attempts). Try after 15 minutes

### Issue: 422 Validation Error
**Solution**: Check request body fields and types

---

## 📞 SUPPORT

**For API Details**: 
- Visit Swagger UI: http://localhost:8000/docs
- Check docs/PHASE_1_AUTH_GUIDE.md

**For Code Help**:
- Check inline documentation
- Review tests in tests/test_auth.py

**For Production Issues**:
- Check IMPLEMENTATION_STATUS.md
- Review PHASE_1_COMPLETION_REPORT.md

---

## ✅ STATUS

**Phase 1**: ✅ COMPLETE (20 endpoints, 23 tests)  
**Ready**: ✅ PRODUCTION  
**Next**: 🔄 Phase 2 Production Modules  

---

> "All endpoints are working. Ready to build production modules." - Daniel
