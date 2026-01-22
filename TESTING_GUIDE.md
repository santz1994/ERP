# ERP Testing Suite - Complete Guide

## 📋 Overview

Testing suite komprehensif untuk sistem ERP dengan 4 tools profesional:

1. **Pytest** - Unit & Integration Testing (Backend)
2. **Locust** - Load & Stress Testing (Performance)
3. **Playwright** - End-to-End Testing (Frontend)
4. **Postman** - API Documentation & Testing

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Backend testing tools
cd d:\Project\ERP2026\erp-softtoys
.\venv\Scripts\Activate.ps1
pip install pytest pytest-cov locust requests

# Frontend E2E testing
cd d:\Project\ERP2026
npm install -D @playwright/test
npx playwright install
```

---

## 🧪 1. Pytest - Unit & Integration Tests

### Run All Tests
```powershell
cd d:\Project\ERP2026
pytest tests/test_production_ready.py -v
```

### Run Specific Test Categories
```powershell
# Security tests only
pytest tests/test_production_ready.py -v -m security

# Critical tests only
pytest tests/test_production_ready.py -v -m critical

# Production logic tests
pytest tests/test_production_ready.py -v -m production

# API tests
pytest tests/test_production_ready.py -v -m api

# All integration tests
pytest tests/test_production_ready.py -v -m integration
```

### Run with Coverage Report
```powershell
pytest tests/test_production_ready.py --cov=erp-softtoys/app --cov-report=html
```

### Expected Output
```
================== ERP PRODUCTION-READY TEST SUMMARY ==================
Results: 38/38 passed (100.0%)
✅ ALL TESTS PASSED - PRODUCTION READY!
=======================================================================
```

---

## 📊 2. Locust - Load & Stress Testing

### Start Locust Web UI
```powershell
cd d:\Project\ERP2026
locust -f tests/locustfile.py --host=http://localhost:8000
```

### Access Web Interface
Open browser: **http://localhost:8089**

### Test Scenarios

#### Scenario 1: Normal Load
- **Users**: 50
- **Spawn rate**: 10 users/second
- **Duration**: 5 minutes

#### Scenario 2: Stress Test
- **Users**: 200
- **Spawn rate**: 50 users/second
- **Duration**: 10 minutes

#### Scenario 3: Spike Test
- **Users**: 500
- **Spawn rate**: 100 users/second
- **Duration**: 2 minutes

### Expected Metrics
- **Response Time**: < 500ms (p95)
- **Success Rate**: > 99%
- **Error Rate**: < 1%
- **Throughput**: > 100 req/s

---

## 🎭 3. Playwright - E2E Frontend Tests

### Run All E2E Tests
```powershell
cd d:\Project\ERP2026
npx playwright test
```

### Run Specific Browser
```powershell
# Chrome only
npx playwright test --project=chromium

# Firefox only
npx playwright test --project=firefox

# Mobile Chrome
npx playwright test --project="Mobile Chrome"
```

### Run with UI Mode (Interactive)
```powershell
npx playwright test --ui
```

### Run Specific Test File
```powershell
npx playwright test tests/e2e/erp.spec.ts
```

### View Test Report
```powershell
npx playwright show-report test-results/playwright-report
```

### Debug Failed Tests
```powershell
npx playwright test --debug
```

---

## 📮 4. Postman - API Collection

### Import Collection

1. Open Postman
2. Click **Import**
3. Select `tests/postman/ERP_API_Collection.json`
4. Collection will be loaded with all endpoints

### Setup Environment

Create new environment in Postman:

```json
{
  "base_url": "http://localhost:8000/api/v1",
  "auth_token": ""
}
```

### Run Collection

1. **Manual Testing**:
   - Select collection
   - Run individual requests
   - Token auto-saved after login

2. **Collection Runner**:
   - Click "Run Collection"
   - Select all folders
   - Click "Run ERP API"

3. **Newman (CLI)**:
```powershell
npm install -g newman
newman run tests/postman/ERP_API_Collection.json --environment env.json
```

---

## 📝 Test Coverage

### Total Tests: 38+

#### 1. Security Tests (SEC-01 to SEC-04)
- ✅ Environment Policy Protection
- ✅ Token JWT Hijacking
- ✅ Invalid Token Rejection
- ✅ Audit Trail Integrity

#### 2. Production Logic (PRD-01 to PRD-04)
- ✅ MO to WO Transition
- ✅ Cutting Quantity Validation
- ✅ Sewing Bundle Sync
- ✅ QC Lab Stock Blocking

#### 3. API Integration (API-01 to API-04)
- ✅ WebSocket Kanban (< 500ms)
- ✅ Auth Endpoint Efficiency
- ✅ Import/Export Validation
- ✅ Database Deadlock Handling

#### 4. UI/UX Tests (UI-01 to UI-04)
- ✅ Dynamic Sidebar
- ✅ Barcode Scanner
- ✅ Responsive Table
- ✅ Session Persistence

#### 5. Golden Thread Integration
- ✅ PPIC & Purchasing
- ✅ Warehouse & Production
- ✅ Inter-Production Tracking

#### 6. QC Integration
- ✅ Lab to Purchasing/Warehouse
- ✅ Inspector to Finishing

#### 7. Stress Tests
- ✅ Race Condition
- ✅ Concurrent WebSocket Updates

#### 8. Go-Live Checklist
- ✅ ID Synchronization
- ✅ Negative Flow Validation
- ✅ Report Accuracy
- ✅ Timezone Integrity

---

## 🎯 Running Complete Test Suite

### Step-by-Step Full Validation

```powershell
# 1. Start Backend
cd d:\Project\ERP2026\erp-softtoys
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# 2. Start Frontend (new terminal)
cd d:\Project\ERP2026\erp-ui\frontend
npm run dev

# 3. Run Pytest (new terminal)
cd d:\Project\ERP2026
pytest tests/test_production_ready.py -v

# 4. Run Playwright E2E
npx playwright test

# 5. Run Locust (manual)
locust -f tests/locustfile.py --host=http://localhost:8000
# Then open http://localhost:8089 and run load test

# 6. Run Postman Collection
# Import and run via Postman UI or Newman CLI
```

---

## ✅ Success Criteria

### Pytest
- ✅ 38/38 tests passed
- ✅ 0 failures
- ✅ Code coverage > 70%

### Playwright
- ✅ All E2E tests passed
- ✅ Login flow working
- ✅ Navigation working
- ✅ Session persistent

### Locust
- ✅ 99%+ success rate
- ✅ Response time < 500ms (p95)
- ✅ No crashes under load

### Postman
- ✅ All requests green
- ✅ Token authentication working
- ✅ All validations passing

---

## 🐛 Troubleshooting

### Pytest Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`
```powershell
cd erp-softtoys
.\venv\Scripts\Activate.ps1
pip install -e .
```

**Problem**: Tests timing out
- Check backend is running on port 8000
- Increase timeout in pytest.ini

### Playwright Issues

**Problem**: Browsers not installed
```powershell
npx playwright install
```

**Problem**: Frontend not accessible
- Start frontend: `npm run dev`
- Check port 5173 is not in use

### Locust Issues

**Problem**: Connection refused
- Ensure backend is running
- Check firewall settings

---

## 📊 Test Results Location

- **Pytest**: Terminal output + `htmlcov/` folder
- **Playwright**: `test-results/playwright-report/`
- **Locust**: Web UI at http://localhost:8089
- **Postman**: Collection run results in Postman UI

---

## 🔥 CI/CD Integration

### GitHub Actions Example

```yaml
name: ERP Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          pip install pytest locust
          npm install
          npx playwright install
      
      - name: Run Pytest
        run: pytest tests/test_production_ready.py -v
      
      - name: Run Playwright
        run: npx playwright test
```

---

## 📞 Support

Jika ada test yang gagal:

1. Baca error message dengan teliti
2. Cek logs backend dan frontend
3. Verify semua services running
4. Check network connectivity
5. Review test expectations

**Target**: 100% tests passing sebelum production! 🎯
