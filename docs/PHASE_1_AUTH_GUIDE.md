# 🔐 PHASE 1 AUTHENTICATION SYSTEM
**Complete Implementation Guide - Week 2 Deliverables**

---

## ⚡ QUICK START (3 minutes)

### **1. Start Services**
```bash
cd D:\Project\ERP2026
docker-compose up -d
docker-compose ps  # Verify all services running
```

### **2. Check Health**
```bash
curl http://localhost:8000/health
# {"status":"healthy","environment":"development"}
```

### **3. Register User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@quty.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "roles": ["operator_cutting"]
  }'
```

### **4. Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'
# Response includes: access_token, refresh_token, expires_in
```

### **5. View Swagger UI**
```
http://localhost:8000/docs
```

---

## 📊 WHAT'S INCLUDED

### **Authentication Endpoints (6)**
| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|----------------|
| `/api/v1/auth/register` | POST | Create new user | No |
| `/api/v1/auth/login` | POST | User login | No |
| `/api/v1/auth/refresh` | POST | Refresh token | No |
| `/api/v1/auth/me` | GET | Get profile | **Yes** |
| `/api/v1/auth/change-password` | POST | Change password | **Yes** |
| `/api/v1/auth/logout` | POST | Logout | **Yes** |

### **Admin Management Endpoints (7)**
| Endpoint | Method | Purpose | Auth Required | Role |
|----------|--------|---------|----------------|------|
| `/api/v1/admin/users` | GET | List users | **Yes** | **Admin** |
| `/api/v1/admin/users/{id}` | GET | Get user | **Yes** | **Admin** |
| `/api/v1/admin/users/{id}` | PUT | Update user | **Yes** | **Admin** |
| `/api/v1/admin/users/{id}/deactivate` | POST | Deactivate | **Yes** | **Admin** |
| `/api/v1/admin/users/{id}/reactivate` | POST | Reactivate | **Yes** | **Admin** |
| `/api/v1/admin/users/{id}/reset-password` | POST | Reset pwd | **Yes** | **Admin** |
| `/api/v1/admin/users/role/{role}` | GET | Filter by role | **Yes** | **Admin** |

---

## 🔑 AUTHENTICATION FLOW

### **Step 1: User Registration**
```
User submits:
  ├─ username (unique, 3-50 chars)
  ├─ email (unique, valid format)
  ├─ password (min 8 chars)
  ├─ full_name
  └─ roles (default: operator_cutting)

System:
  ├─ Validates all fields
  ├─ Hashes password with bcrypt
  ├─ Creates user in database
  └─ Returns user profile (201 Created)
```

### **Step 2: User Login**
```
User submits:
  ├─ username (or email)
  └─ password

System:
  ├─ Finds user by username/email
  ├─ Verifies password with bcrypt
  ├─ Checks if account active
  ├─ Generates JWT tokens
  ├─ Updates last_login timestamp
  └─ Returns: access_token + refresh_token

Security:
  ├─ 5 failed attempts → 15 min lockout
  ├─ Track login_attempts counter
  └─ Reset counter on success
```

### **Step 3: Using Access Token**
```
Client sends:
  Authorization: Bearer <access_token>

System:
  ├─ Validates JWT signature
  ├─ Checks token not expired (24h)
  ├─ Extracts user_id, roles
  ├─ Loads user from database
  ├─ Checks is_active status
  └─ Allows/denies request

Failure Cases:
  ├─ No token → 403 Forbidden
  ├─ Invalid token → 401 Unauthorized
  ├─ Expired token → 401 Unauthorized
  ├─ Inactive user → 403 Forbidden
  └─ Insufficient role → 403 Forbidden
```

### **Step 4: Token Refresh**
```
Client submits:
  └─ refresh_token

System:
  ├─ Validates refresh token (7-day validity)
  ├─ Finds user by token claims
  ├─ Generates new access_token
  ├─ Returns: new access_token + same refresh_token
  └─ Old access_token becomes invalid

Use Case:
  └─ Call this when access_token expires or before logout
```

---

## 👥 USER ROLES (16 Total)

### **Administrative (1)**
- `Admin` - Full system access, bypass all checks

### **Planning (2)**
- `PPIC Manager` - Production planning, MO creation
- `PPIC Admin` - PPIC administrative tasks

### **Supervisors (3)**
- `SPV Cutting` - Cutting department supervision
- `SPV Sewing` - Sewing department supervision  
- `SPV Finishing` - Finishing department supervision

### **Operators (5)**
- `Operator Cutting` - Cutting line operator
- `Operator Embroidery` - Embroidery operator
- `Operator Sewing` - Sewing line operator
- `Operator Finishing` - Finishing operator
- `Operator Packing` - Packing operator

### **Quality (2)**
- `QC Inspector` - Quality control field inspection
- `QC Lab` - Laboratory testing

### **Warehouse (2)**
- `Warehouse Admin` - Warehouse administration
- `Warehouse Operator` - Warehouse operations

### **Support (1)**
- `Purchasing` - Procurement

---

## 🔒 SECURITY FEATURES

### **1. Password Security**
✅ **Bcrypt Hashing**: Industry-standard, automatic salt  
✅ **Never Store Plain**: Only hash stored in database  
✅ **Constant-Time Compare**: Prevent timing attacks  
✅ **Minimum 8 Chars**: Enforced on registration & change  
✅ **Change Tracking**: last_password_change timestamp  

### **2. Account Protection**
✅ **Failed Attempt Tracking**: login_attempts counter  
✅ **Account Lockout**: After 5 failed attempts  
✅ **Lockout Duration**: 15 minutes automatic unlock  
✅ **Admin Reset**: Can manually unlock accounts  
✅ **Deactivation**: Admin can disable accounts  

### **3. JWT Tokens**
✅ **Access Tokens**: 24-hour expiration  
✅ **Refresh Tokens**: 7-day expiration  
✅ **HS256 Signing**: HMAC SHA-256 algorithm  
✅ **Claims**: user_id, username, email, roles  
✅ **Validation**: Signature + expiration check  

### **4. Role-Based Access Control**
✅ **16 Distinct Roles**: Department-specific permissions  
✅ **Admin Bypass**: Admin can access everything  
✅ **Decorator Pattern**: @require_role("admin")  
✅ **Route Protection**: All admin endpoints secured  
✅ **Multiple Roles**: User can have single primary role  

### **5. Audit Trail**
✅ **Login Timestamp**: Track last_login on each attempt  
✅ **Account Creation**: created_at on registration  
✅ **Password Changes**: last_password_change timestamp  
✅ **Active Status**: is_active flag  
✅ **Verification Status**: is_verified flag  

---

## 🧪 TESTING

### **Run All Tests**
```bash
cd erp-softtoys
pytest tests/test_auth.py -v
```

### **Run Specific Test Class**
```bash
pytest tests/test_auth.py::TestUserRegistration -v
pytest tests/test_auth.py::TestAdminEndpoints -v
```

### **Run With Coverage**
```bash
pytest tests/test_auth.py --cov=app --cov-report=html
```

### **Test Categories**
- ✅ **Registration Tests** (5) - User creation, duplicate prevention
- ✅ **Login Tests** (5) - Credentials, account lockout
- ✅ **Token Tests** (3) - Refresh, validation
- ✅ **Profile Tests** (4) - Me endpoint, password change
- ✅ **Admin Tests** (5) - User management, role checks
- ✅ **RBAC Tests** (1) - Role-based access

**Total**: 23 comprehensive tests covering all flows

---

## 💻 USING THE API

### **With cURL**

**Register**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"u1@quty.com","password":"Pass123","full_name":"User One","roles":["operator_cutting"]}'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"Pass123"}'
```

**Get Profile** (replace TOKEN with actual token):
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### **With Python**

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "username": "user1",
        "email": "u1@quty.com",
        "password": "Pass123",
        "full_name": "User One",
        "roles": ["operator_cutting"]
    }
)
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "user1", "password": "Pass123"}
)
data = response.json()
access_token = data["access_token"]

# Get Profile
response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(response.json())
```

### **With JavaScript/Node.js**

```javascript
const API_URL = "http://localhost:8000/api/v1";

// Register
const registerResponse = await fetch(`${API_URL}/auth/register`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "user1",
    email: "u1@quty.com",
    password: "Pass123",
    full_name: "User One",
    roles: ["operator_cutting"]
  })
});

// Login
const loginResponse = await fetch(`${API_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "user1",
    password: "Pass123"
  })
});

const { access_token } = await loginResponse.json();

// Get Profile
const profileResponse = await fetch(`${API_URL}/auth/me`, {
  headers: { "Authorization": `Bearer ${access_token}` }
});

console.log(await profileResponse.json());
```

---

## 🛠️ CONFIGURATION

### **Environment Variables** (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/erp_quty_karunia

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=7

# API
ENVIRONMENT=development
DEBUG=true
API_TITLE=ERP Quty Karunia
API_VERSION=2.0.0

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### **Security Best Practices**
1. **Change JWT_SECRET_KEY** in production to strong random value
2. **Use HTTPS** only in production (not HTTP)
3. **Restrict CORS_ORIGINS** to your frontend domain
4. **Enable HTTPS redirect** via reverse proxy
5. **Monitor login failures** for brute force attempts
6. **Rotate JWT_SECRET_KEY** periodically

---

## 🐛 TROUBLESHOOTING

### **Problem: 401 Unauthorized**
**Cause**: Invalid or expired token  
**Solution**: 
- Check token hasn't expired (24h)
- Verify token format: "Authorization: Bearer TOKEN"
- Login again to get fresh token
- Use refresh_token to get new access_token

### **Problem: 403 Forbidden**
**Cause**: Insufficient permissions  
**Solution**:
- Verify user role required for endpoint
- Check user is not deactivated
- Confirm token contains required role

### **Problem: 429 Too Many Requests**
**Cause**: Account locked after 5 failed login attempts  
**Solution**:
- Wait 15 minutes for automatic unlock
- Admin can unlock: POST /admin/users/{id}/reactivate

### **Problem: 422 Validation Error**
**Cause**: Invalid request data  
**Solution**:
- Check all required fields present
- Verify data types (string, email, etc.)
- See /docs for exact schema

### **Problem: Database Connection Failed**
**Cause**: PostgreSQL not running  
**Solution**:
- Check docker-compose: `docker-compose ps`
- Start services: `docker-compose up -d`
- Wait 30s for PostgreSQL to be healthy

---

## 📈 NEXT STEPS (Phase 1 Completion)

**Week 2 Remaining** (Jan 22-23):
- [ ] PPIC module endpoints (products, manufacturing orders)
- [ ] Warehouse module endpoints (stock, locations)
- [ ] Integration test suite
- [ ] Documentation finalization

**After Phase 1** (Week 3):
- [ ] Production modules (Cutting, Sewing, Finishing, Packing)
- [ ] Transfer protocol (QT-09 handshake)
- [ ] Frontend development begins

---

## 📚 DOCUMENTATION LINKS

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Project Docs**: `/docs/Project Docs/Project.md`
- **Flow Production**: `/docs/Project Docs/Flow Production.md`
- **Database Schema**: `/docs/Project Docs/Database Scheme.csv`
- **Implementation Status**: `/docs/IMPLEMENTATION_STATUS.md`

---

## ✅ VERIFICATION

**Before proceeding to next phase, verify:**
- [ ] Docker services running (`docker-compose ps`)
- [ ] API health: `http://localhost:8000/health`
- [ ] Swagger UI accessible: `http://localhost:8000/docs`
- [ ] User registration works
- [ ] User login works
- [ ] Admin endpoints secured
- [ ] All tests passing: `pytest tests/test_auth.py -v`
- [ ] No errors in Docker logs: `docker-compose logs backend`

---

**Status**: ✅ **PRODUCTION READY**  
**Delivered**: January 19, 2026  
**Next Review**: January 22, 2026  
**Maintained By**: Daniel Rizaldy, Senior IT Developer

