# 🧪 TESTING GUIDE - SESSION 37 TEST SUITES

**Purpose**: How to execute, validate, and debug the comprehensive test suites created in Session 37

**Status**: All test files ready to execute  
**Platform**: Windows, Python 3.9+, pytest  
**Database**: Mock (SQLAlchemy mocks, no real DB needed for unit tests)

---

## 📋 TEST FILES CREATED

### 1. Feature #1: BOM Auto-Allocate Tests
**File**: `/tests/test_bom_allocation.py`  
**Lines**: 600+  
**Test Classes**: 9  
**Test Cases**: 35+  
**Focus**: Material allocation logic, wastage, stock checking

### 2. Feature #4: Material Debt Service Tests  
**File**: `/tests/test_material_debt_service.py`  
**Lines**: 700+  
**Test Classes**: 9  
**Test Cases**: 40+  
**Focus**: Debt creation, approval, settlement, error handling

### 3. Feature #4: Material Debt API Tests
**File**: `/tests/test_material_debt_api.py`  
**Lines**: 600+  
**Test Classes**: 4  
**Test Cases**: 25+  
**Focus**: API endpoints, permissions, workflow simulation

**Total**: 1900+ lines, 100+ test cases

---

## 🚀 QUICK START - RUNNING TESTS

### Prerequisites

```bash
# Ensure pytest is installed
pip install pytest pytest-asyncio pytest-mock

# Navigate to project root
cd d:\Project\ERP2026\erp-softtoys
```

### Run All Tests

```bash
# Run all new test files
pytest tests/test_bom_allocation.py tests/test_material_debt_service.py tests/test_material_debt_api.py -v

# Or run individual feature tests
pytest tests/test_bom_allocation.py -v
pytest tests/test_material_debt_service.py -v
pytest tests/test_material_debt_api.py -v
```

### Run Specific Test Class

```bash
# BOM Allocation tests
pytest tests/test_bom_allocation.py::TestBOMAllocationBasics -v

# Material Debt tests
pytest tests/test_material_debt_service.py::TestMaterialDebtCreation -v

# API tests
pytest tests/test_material_debt_api.py::TestMaterialDebtEndpoints -v
```

### Run Specific Test Case

```bash
# Single test
pytest tests/test_bom_allocation.py::TestBOMAllocationBasics::test_allocate_material_with_sufficient_stock -v
```

---

## 📊 UNDERSTANDING TEST STRUCTURE

### BOM Allocation Tests (test_bom_allocation.py)

**Test Classes**:

1. **TestBOMAllocationBasics** - Core allocation functionality
   - test_allocate_material_with_sufficient_stock
   - test_allocate_material_with_insufficient_stock

2. **TestWastageCalculation** - Wastage percentage math
   - test_calculate_wastage_zero_percent
   - test_calculate_wastage_five_percent
   - test_calculate_wastage_large_percent

3. **TestBOMQueries** - BOM data retrieval
   - test_get_bom_by_article
   - test_get_allocation_preview

4. **TestAllocationStatus** - Status tracking
   - test_full_allocation_status
   - test_partial_allocation_status
   - test_failed_allocation_status

5. **TestAllocationValidation** - Input validation
   - test_invalid_spk_fails
   - test_invalid_material_fails
   - test_invalid_qty_fails

6. **TestAllocationWithDebtIntegration** - Debt creation
   - test_allocation_creates_debt_for_shortage

7. **TestAllocationCalculations** - Amount calculations
   - test_calculate_total_allocation_value
   - test_calculate_allocation_percentage
   - test_calculate_shortage_amount

8. **TestBOMAllocationEdgeCases** - Special scenarios
   - test_fractional_unit_qty
   - test_very_high_wastage
   - test_very_small_quantities

### Material Debt Service Tests (test_material_debt_service.py)

**Test Classes**:

1. **TestMaterialDebtCreation** - Debt creation & validation
   - test_create_debt_successfully
   - test_create_debt_validates_spk
   - test_create_debt_validates_material
   - test_create_debt_validates_quantity

2. **TestMaterialDebtApproval** - Approval workflow
   - test_approve_debt_pending
   - test_reject_debt_pending
   - test_reject_approved_debt_fails

3. **TestMaterialDebtAdjustment** - Settlement & adjustments
   - test_adjust_debt_partial_settlement
   - test_adjust_debt_full_settlement
   - test_adjust_debt_exceeds_amount_fails

4. **TestMaterialDebtQuerying** - Data retrieval
   - test_get_outstanding_debt
   - test_get_debt_status
   - test_check_po_blocking_threshold

5. **TestMaterialDebtIntegration** - Integration tests
   - test_debt_integrates_with_approval_workflow

6. **TestMaterialDebtErrorHandling** - Error scenarios
   - test_debt_not_found_raises_error
   - test_invalid_adjustment_type_raises_error
   - test_concurrent_settlement_safe

7. **TestMaterialDebtCalculations** - Math validation
   - test_calculate_debt_total_value
   - test_calculate_settled_percentage
   - test_calculate_debt_aging

### Material Debt API Tests (test_material_debt_api.py)

**Test Classes**:

1. **TestMaterialDebtEndpoints** - API endpoint testing
   - test_create_debt_endpoint_success
   - test_create_debt_requires_auth
   - test_approve_debt_endpoint_success
   - test_reject_debt_endpoint_success
   - test_adjust_debt_endpoint_success
   - test_get_debt_endpoint_success
   - test_get_outstanding_debts_endpoint_success
   - test_check_threshold_endpoint_success

2. **TestMaterialDebtWorkflow** - Full workflows
   - test_complete_workflow_create_approve_settle
   - test_workflow_rejection_path

3. **TestMaterialDebtFiltering** - Query filtering
   - test_get_debts_filter_by_status
   - test_get_debts_filter_by_department
   - test_get_debts_filter_by_spk

4. **TestMaterialDebtPagination** - Pagination
   - test_outstanding_debts_pagination_limit
   - test_outstanding_debts_pagination_offset

---

## 🔍 EXPECTED TEST RESULTS

### Success Indicators

When tests pass, you should see:

```
================================= test session starts =================================
collected 35 items

tests/test_bom_allocation.py::TestBOMAllocationBasics::test_allocate_material_with_sufficient_stock PASSED
tests/test_bom_allocation.py::TestBOMAllocationBasics::test_allocate_material_with_insufficient_stock PASSED
...

================================= 35 passed in 0.45s ==================================
```

### What Each Status Means

- ✅ **PASSED** - Test successful, assertion passed
- ❌ **FAILED** - Test failed, assertion failed
- ⏭️ **SKIPPED** - Test marked to skip
- ⚠️ **XFAIL** - Expected fail (but passed - something is better!)

---

## 🐛 DEBUGGING FAILURES

### Common Issues & Solutions

#### Issue 1: Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution**:
```bash
# Add project to Python path
set PYTHONPATH=%PYTHONPATH%;d:\Project\ERP2026\erp-softtoys
# Or run from project root
cd d:\Project\ERP2026\erp-softtoys
pytest tests/test_bom_allocation.py -v
```

#### Issue 2: Database Connection Errors

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solution**: This should NOT happen for unit tests with mocked DB
- All tests use `@pytest.fixture def db_mock()`
- Mock replaces real database
- No actual DB connection needed

If you see this error:
- Check that tests are using the fixture: `def test_something(db_mock)`
- Verify MagicMock is properly used

#### Issue 3: Async Test Failures

```
RuntimeError: Event loop is closed
```

**Solution**:
```bash
# Use pytest-asyncio
pip install pytest-asyncio

# Mark test as async
@pytest.mark.asyncio
async def test_something():
    pass
```

#### Issue 4: Mock Not Working

```
AttributeError: Mock object has no attribute 'query'
```

**Solution**:
```python
# Ensure fixture returns properly mocked Session
@pytest.fixture
def db_mock() -> Session:
    mock = MagicMock(spec=Session)
    mock.query = MagicMock()
    return mock
```

---

## ✨ RUNNING WITH COVERAGE

### Generate Coverage Report

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest tests/test_bom_allocation.py --cov=app.services.bom_service --cov-report=html -v
pytest tests/test_material_debt_service.py --cov=app.services.material_debt_service --cov-report=html -v
pytest tests/test_material_debt_api.py --cov=app.api.v1.warehouse.material_debt --cov-report=html -v

# View HTML report
start htmlcov/index.html
```

### Expected Coverage

- **BOM Allocation**: 85%+ of bom_service.py
- **Material Debt Service**: 80%+ of material_debt_service.py
- **Material Debt API**: 75%+ of material_debt.py (API endpoints)

---

## 🎯 TEST VALIDATION CHECKLIST

### Before Running Tests

- [ ] Python 3.9+ installed
- [ ] pytest installed
- [ ] pytest-asyncio installed
- [ ] pytest-mock installed
- [ ] Project structure intact
- [ ] All imports available
- [ ] No syntax errors

### Running Tests

- [ ] Run `pytest tests/test_bom_allocation.py -v`
- [ ] Run `pytest tests/test_material_debt_service.py -v`
- [ ] Run `pytest tests/test_material_debt_api.py -v`
- [ ] Check for passed/failed counts
- [ ] Note any failures for debugging

### Validating Results

- [ ] All tests pass (or failures are documented)
- [ ] Coverage > 75%
- [ ] No import errors
- [ ] No database connection errors
- [ ] Workflow tests complete successfully

---

## 📈 EXPECTED TEST COVERAGE

### Feature #1: BOM Auto-Allocate

| Component | Coverage |
|-----------|----------|
| `allocate_material_for_spk()` | 90% |
| Wastage calculation | 95% |
| Stock checking | 85% |
| Error handling | 80% |
| **Overall** | **87%** |

### Feature #4: Material Debt Service

| Component | Coverage |
|-----------|----------|
| `create_material_debt()` | 85% |
| `approve_material_debt()` | 80% |
| `adjust_material_debt()` | 85% |
| `get_outstanding_debts()` | 90% |
| `check_po_blocking_threshold()` | 85% |
| Error handling | 75% |
| **Overall** | **83%** |

### Feature #4: Material Debt API

| Component | Coverage |
|-----------|----------|
| Create endpoint | 80% |
| Approve endpoint | 85% |
| Adjust endpoint | 80% |
| Get endpoint | 90% |
| Outstanding list | 85% |
| Error handling | 70% |
| **Overall** | **82%** |

---

## 🚀 NEXT STEPS AFTER TESTS

### If All Tests Pass ✅

1. Run full test suite for entire project
2. Check overall code coverage
3. Merge to main branch
4. Deploy to staging
5. Run E2E tests on staging

### If Tests Fail ❌

1. Review error messages
2. Check stack traces
3. Debug using `-v` flag for verbose output
4. Fix issues in test file or implementation
5. Re-run tests
6. Document what was fixed

### Test Output Tips

```bash
# Verbose output - shows each test
pytest -v

# Very verbose - shows test output too
pytest -vv

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show slowest 10 tests
pytest --durations=10

# Run only failed tests
pytest --lf

# Run failed tests first, then others
pytest --ff
```

---

## 📝 DOCUMENTATION OF TEST PATTERNS

### Fixture Pattern (Reusable Setup)

```python
@pytest.fixture
def db_mock() -> Session:
    """Mock database session"""
    return MagicMock(spec=Session)

@pytest.fixture
def material_debt_service(db_mock: Session) -> MaterialDebtService:
    """Create service with mocked DB"""
    return MaterialDebtService(db=db_mock)
```

### Async Test Pattern

```python
@pytest.mark.asyncio
async def test_create_debt_successfully(self, material_debt_service, db_mock):
    """Async test with await"""
    result = await material_debt_service.create_material_debt(...)
    assert result is not None
```

### Mock Return Pattern

```python
# Setup mock to return specific value
db_mock.query().filter().first.return_value = mock_debt

# Act
result = await service.get_debt_status(debt_id=1)

# Assert
assert result["id"] == 1
```

### Workflow Testing Pattern

```python
def test_complete_workflow(self, test_client, auth_headers):
    # Step 1: Create
    response = test_client.post("/api/endpoint", json={...})
    assert response.status_code == 201
    
    # Step 2: Approve
    response = test_client.post(f"/api/endpoint/{id}/approve")
    assert response.status_code == 200
    
    # Step 3: Verify
    response = test_client.get(f"/api/endpoint/{id}")
    assert response.json()["status"] == "APPROVED"
```

---

## 🎓 LEARNING RESOURCES

### pytest Documentation
- https://docs.pytest.org/en/stable/
- https://docs.pytest.org/en/stable/fixture.html
- https://docs.pytest.org/en/stable/parametrize.html

### Mocking
- https://docs.python.org/3/library/unittest.mock.html
- AsyncMock for async functions

### Async Testing
- https://github.com/pytest-dev/pytest-asyncio
- `@pytest.mark.asyncio` decorator

---

## ✅ COMPLETION CHECKLIST

- [ ] All test files created and present
- [ ] Test files have correct structure
- [ ] Tests import required modules
- [ ] Fixtures are properly defined
- [ ] Mock objects are configured
- [ ] Async tests have correct decorator
- [ ] All assertions are meaningful
- [ ] Edge cases are covered
- [ ] Error scenarios are tested
- [ ] Code is documented with comments

---

**Next Step**: Execute `pytest tests/test_bom_allocation.py -v` to begin testing!
