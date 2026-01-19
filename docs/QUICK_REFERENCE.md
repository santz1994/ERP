# 🚀 QUICK REFERENCE - WEEK 2 API GUIDE
**For Developers: Running the System & Testing Endpoints**

---

## ⚡ QUICK START (5 Minutes)

### **1. Start PostgreSQL** (if not running)
```bash
# Windows
net start postgresql-13

# Or use pgAdmin for management
```

### **2. Setup & Run**
```bash
cd D:\Project\ERP2026\erp-softtoys

# Activate environment
venv\Scripts\activate

# Create/reset database
createdb -U postgres erp_quty_karunia
# Or if exists: dropdb -U postgres erp_quty_karunia && createdb -U postgres erp_quty_karunia

# Install dependencies
pip install -r requirements.txt

# Seed test data
python seed_data.py

# Start server
python -m uvicorn app.main:app --reload
```

### **3. Access API**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Base**: http://localhost:8000/api/v1

---

## 🔐 AUTHENTICATION FLOW

### **Test Login**
```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ppic_user",
    "password": "Ppic123456"
  }'

# Save token from response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use in requests
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### **Test Users**
```
admin           / Admin123456           (admin role)
ppic_user       / Ppic123456            (ppic_manager)
spv_cutting     / SpvCut123456          (spv_cutting)
op_cutting      / OpCut123456           (operator_cutting)
warehouse       / Warehouse123456       (warehouse_admin)
```

---

## 📡 ENDPOINT TESTING CHECKLIST

### **✅ Phase 1: Authentication**
```bash
# 1. Register new user
POST /auth/register
Body: {"username": "test_op", "email": "test@quty.com", "password": "TestPass123", "full_name": "Test Operator", "roles": ["operator_cutting"]}

# 2. Login
POST /auth/login
Body: {"username": "test_op", "password": "TestPass123"}

# 3. Get current user info
GET /auth/me
Header: Authorization: Bearer <token>

# 4. Refresh token
POST /auth/refresh?token=<refresh_token>
```

### **✅ Phase 2: PPIC Manufacturing Order**
```bash
# 1. Create Manufacturing Order
POST /ppic/manufacturing-order
Header: Authorization: Bearer <ppic_token>
Body: {
  "so_line_id": 1,
  "product_id": 2,
  "qty_planned": 5000,
  "routing_type": "Route 1",
  "batch_number": "BATCH-2026-TEST-001"
}

# 2. Get MO details
GET /ppic/manufacturing-order/{mo_id}
Header: Authorization: Bearer <ppic_token>

# 3. List all MOs
GET /ppic/manufacturing-orders?skip=0&limit=50
Header: Authorization: Bearer <ppic_token>

# 4. Approve MO (move to IN_PROGRESS)
POST /ppic/manufacturing-order/{mo_id}/approve
Header: Authorization: Bearer <ppic_token>
```

### **✅ Phase 3: Warehouse Stock & Transfers**
```bash
# 1. Check stock availability
GET /warehouse/stock/1?location_id=1
Header: Authorization: Bearer <warehouse_token>

# Response shows:
# - qty_on_hand: Physical stock
# - qty_reserved: Already allocated
# - qty_available: Can be used

# 2. Create transfer (Cutting → Sewing)
POST /warehouse/transfer
Header: Authorization: Bearer <warehouse_token>
Body: {
  "from_dept": "Cutting",
  "to_dept": "Sewing",
  "product_id": 2,
  "qty": 5000,
  "batch_number": "BATCH-2026-001",
  "reference_doc": "SPK-CUT-001",
  "lot_id": 1
}

# Possible responses:
# 201 CREATED - Transfer initiated (status: INITIATED)
# 400 BAD REQUEST - Line occupied or stock insufficient (status: BLOCKED)

# 3. Accept transfer at receiving department
POST /warehouse/transfer/{transfer_id}/accept?qty_received=5000
Header: Authorization: Bearer <warehouse_token>

# Status changes from INITIATED → ACCEPTED
```

---

## 🧪 COMPLETE TEST SCENARIO

### **Scenario: Route 1 Full Process (with Embroidery)**

```bash
#!/bin/bash
# Save as: test_route1.sh

API="http://localhost:8000/api/v1"

echo "=== STEP 1: Login as PPIC Manager ==="
RESPONSE=$(curl -s -X POST $API/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ppic_user","password":"Ppic123456"}')
PPIC_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "PPIC Token: $PPIC_TOKEN"

echo -e "\n=== STEP 2: Create Manufacturing Order ==="
MO_RESPONSE=$(curl -s -X POST $API/ppic/manufacturing-order \
  -H "Authorization: Bearer $PPIC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "so_line_id": 1,
    "product_id": 2,
    "qty_planned": 5000,
    "routing_type": "Route 1",
    "batch_number": "BATCH-ROUTE1-TEST"
  }')
MO_ID=$(echo $MO_RESPONSE | jq -r '.id')
echo "Created MO: $MO_ID"
echo "$MO_RESPONSE" | jq '.'

echo -e "\n=== STEP 3: Approve MO ==="
APPROVE_RESPONSE=$(curl -s -X POST $API/ppic/manufacturing-order/$MO_ID/approve \
  -H "Authorization: Bearer $PPIC_TOKEN")
echo "$APPROVE_RESPONSE" | jq '.state'

echo -e "\n=== STEP 4: Login as Warehouse Admin ==="
WH_RESPONSE=$(curl -s -X POST $API/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"warehouse","password":"Warehouse123456"}')
WH_TOKEN=$(echo $WH_RESPONSE | jq -r '.access_token')
echo "Warehouse Token: $WH_TOKEN"

echo -e "\n=== STEP 5: Check Stock ==="
STOCK_RESPONSE=$(curl -s -X GET "$API/warehouse/stock/1?location_id=1" \
  -H "Authorization: Bearer $WH_TOKEN")
echo "$STOCK_RESPONSE" | jq '.'

echo -e "\n=== STEP 6: Create Transfer (Cutting → Sewing) ==="
TRANSFER_RESPONSE=$(curl -s -X POST $API/warehouse/transfer \
  -H "Authorization: Bearer $WH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from_dept": "Cutting",
    "to_dept": "Sewing",
    "product_id": 2,
    "qty": 5000,
    "batch_number": "BATCH-ROUTE1-TEST",
    "reference_doc": "SPK-CUT-001",
    "lot_id": 1
  }')
TRANSFER_ID=$(echo $TRANSFER_RESPONSE | jq -r '.id')
TRANSFER_STATUS=$(echo $TRANSFER_RESPONSE | jq -r '.status')
echo "Created Transfer: $TRANSFER_ID"
echo "Status: $TRANSFER_STATUS"
echo "$TRANSFER_RESPONSE" | jq '.'

echo -e "\n=== STEP 7: Accept Transfer at Sewing ==="
ACCEPT_RESPONSE=$(curl -s -X POST $API/warehouse/transfer/$TRANSFER_ID/accept?qty_received=5000 \
  -H "Authorization: Bearer $WH_TOKEN")
echo "New Status: $(echo $ACCEPT_RESPONSE | jq -r '.status')"
echo "$ACCEPT_RESPONSE" | jq '.'

echo -e "\n=== TEST COMPLETE ==="
```

**Run**:
```bash
chmod +x test_route1.sh
./test_route1.sh
```

---

## 🔍 DEBUGGING TIPS

### **Check Logs**
```bash
# Real-time logs while running:
python -m uvicorn app.main:app --reload --log-level debug
```

### **Test with curl**
```bash
# Pretty print JSON responses
curl -s http://localhost:8000/api/v1/endpoint | jq '.'

# Save response to file
curl -s http://localhost:8000/api/v1/endpoint > response.json

# Check response headers
curl -i http://localhost:8000/api/v1/endpoint
```

### **Database Check**
```bash
# Connect to PostgreSQL
psql -U postgres -d erp_quty_karunia

# List tables
\dt

# Query users
SELECT * FROM users;

# Query products
SELECT code, name, type FROM products;

# Check stock
SELECT product_id, qty_on_hand, qty_reserved FROM stock_quants;

# Check transfers
SELECT * FROM transfer_logs ORDER BY created_at DESC LIMIT 5;
```

---

## ⚙️ CONFIGURATION REFERENCE

### **Database Connection** (`.env`)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/erp_quty_karunia
```

### **API Settings** (`app/core/config.py`)
```python
API_PREFIX = "/api/v1"
JWT_EXPIRATION_HOURS = 24
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]
```

### **Model Locations**
```
Products:        app/core/models/products.py
Manufacturing:   app/core/models/manufacturing.py
Transfer:        app/core/models/transfer.py
Warehouse:       app/core/models/warehouse.py
Users:           app/core/models/users.py
QC:              app/core/models/quality.py
```

---

## 🐛 COMMON ISSUES & SOLUTIONS

| Issue | Solution |
|-------|----------|
| **"Database connection refused"** | Check PostgreSQL is running: `psql -U postgres` |
| **"ModuleNotFoundError: pydantic"** | Run: `pip install -r requirements.txt` |
| **"Invalid credentials"** | Check test user passwords (case-sensitive) |
| **"Line OCCUPIED"** | Transfer blocked because receiving line has previous batch |
| **"Stock insufficient"** | Check qty_available in `/warehouse/stock/{product_id}` |
| **"CORS error"** | Check CORS_ORIGINS in config.py matches your frontend |

---

## 📊 PERFORMANCE TARGETS

| Metric | Target | How to Test |
|--------|--------|-----------|
| Login response | < 500ms | `time curl -X POST /auth/login ...` |
| Stock check | < 300ms | `time curl -X GET /warehouse/stock/...` |
| Transfer create | < 1000ms | `time curl -X POST /warehouse/transfer ...` |
| API startup | < 5s | `python -m uvicorn app.main:app --reload` |

---

## 🔗 USEFUL LINKS

- **Swagger UI**: http://localhost:8000/docs ← Try it here!
- **API Base**: http://localhost:8000/api/v1
- **PostgreSQL**: localhost:5432
- **Redis** (later): localhost:6379
- **Prometheus** (later): localhost:8001/metrics

---

## 📞 NEXT STEPS

### **For Week 3**
1. Run full test scenario to verify all endpoints
2. Test error scenarios (invalid inputs, wrong roles, etc)
3. Load test with multiple concurrent transfers
4. Verify database persistence across restarts
5. Test with different routes (Route 2, Route 3)

### **Questions?**
- Check `/docs` endpoint for interactive API documentation
- Review code comments in `app/api/v1/` files
- Read [WEEK2_IMPLEMENTATION_REPORT.md](./WEEK2_IMPLEMENTATION_REPORT.md) for details

---

**Happy Testing! 🚀**

*Generated for Week 2 - January 20, 2026*
