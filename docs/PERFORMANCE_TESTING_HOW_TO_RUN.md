# Performance & Load Testing - How to Run

## Current Performance Tests (In test_production_ready.py)

### What Exists Today

#### 1. **Performance Benchmarks** (TestPerformance class)
- `test_perf01_login_response_time` - Login < 1 second
- `test_perf02_dashboard_load_time` - Dashboard load < 2 seconds

#### 2. **Stress Tests** (TestStressAndEdgeCases class)
- `test_stress01_race_condition_stock_collision` - Concurrent stock updates (2 threads)
- `test_stress02_websocket_concurrent_updates` - WebSocket load test (50 concurrent users)

---

## Why Performance Tests Skip

They're marked with `@pytest.mark.skip` because they need:
1. **API server running** at localhost:8000
2. **Valid test data** (admin user, manufacturing orders, warehouse stock)
3. **Auth headers** fixture from conftest.py

---

## How to Run Performance Tests

### Option 1: View What's Available (No API Needed)
```bash
cd D:\Project\ERP2026
pytest tests/test_production_ready.py::TestPerformance --collect-only -q

# Output:
# tests/test_production_ready.py::TestPerformance::test_perf01_login_response_time
# tests/test_production_ready.py::TestPerformance::test_perf02_dashboard_load_time
```

### Option 2: Run Performance Tests WITH API Server

**Step 1: Start the API** (Terminal 1)
```bash
cd D:\Project\ERP2026\erp-softtoys
python -m uvicorn app.main:app --reload
# Waits for: "Uvicorn running on http://127.0.0.1:8000"
```

**Step 2: Seed test data** (Terminal 2)
```bash
cd D:\Project\ERP2026\erp-softtoys

# Create admin user for testing
python seed_admin.py

# Optional: Load sample data
python seed_data.py
```

**Step 3: Run performance tests** (Terminal 3)
```bash
cd D:\Project\ERP2026

# Run all performance tests
pytest tests/test_production_ready.py::TestPerformance -v

# Run specific test
pytest tests/test_production_ready.py::TestPerformance::test_perf01_login_response_time -v

# Run stress tests
pytest tests/test_production_ready.py::TestStressAndEdgeCases -v

# Run both
pytest tests/test_production_ready.py::TestPerformance tests/test_production_ready.py::TestStressAndEdgeCases -v
```

---

## Expected Results

### Without API Server
```
SKIPPED - Requires API_URL and TEST_USER configuration
SKIPPED - Requires auth_headers fixture
```

### With API Server Running
```
test_perf01_login_response_time PASSED
├─ Login completes in 0.234s ✅ (< 1.0s target)

test_perf02_dashboard_load_time PASSED
├─ Dashboard loads in 0.456s ✅ (< 2.0s target)

test_stress01_race_condition_stock_collision PASSED
├─ 2 concurrent stock updates: all succeeded ✅

test_stress02_websocket_concurrent_updates PASSED
├─ 50 concurrent requests: 98% success ✅ (>70% target)
```

---

## Performance Test Details

### Test 1: Login Response Time
**What it tests:** How fast users can authenticate
```python
start = time.time()
response = requests.post(f"{API_URL}/auth/login", json=TEST_USER, timeout=5)
elapsed = time.time() - start

assert elapsed < 1.0  # Target: < 1 second
```

**Target:** < 1000ms ⚡  
**Why it matters:** Users expect instant login response

### Test 2: Dashboard Load Time
**What it tests:** How fast dashboard data loads
```python
start = time.time()
response = requests.get(f"{API_URL}/dashboard/stats", headers=auth_headers, timeout=5)
elapsed = time.time() - start

assert elapsed < 2.0  # Target: < 2 seconds
```

**Target:** < 2000ms ⚡  
**Why it matters:** Dashboard is most-accessed page

### Test 3: Race Condition (Stock Collision)
**What it tests:** Concurrent stock updates don't corrupt data
```python
# 2 threads simultaneously add to warehouse stock
# Both should either succeed or get validation error
# No corrupted state
```

**Target:** No data corruption ✅  
**Why it matters:** Multiple users can work simultaneously

### Test 4: WebSocket Concurrency (50 Users)
**What it tests:** Real-time updates with many concurrent users
```python
# 50 concurrent requests to kanban board
# Need >= 70% success rate
```

**Target:** >= 70% success rate ✅  
**Why it matters:** Production has many concurrent users

---

## Complete Performance Test Workflow

```bash
# 1. Start API (Terminal 1)
cd D:\Project\ERP2026\erp-softtoys
python -m uvicorn app.main:app --reload

# 2. Seed test data (Terminal 2)
cd D:\Project\ERP2026\erp-softtoys
python seed_admin.py

# 3. Run all performance tests (Terminal 3)
cd D:\Project\ERP2026
pytest tests/test_production_ready.py::TestPerformance tests/test_production_ready.py::TestStressAndEdgeCases -v --tb=short

# Output should show:
# ✅ test_perf01_login_response_time PASSED
# ✅ test_perf02_dashboard_load_time PASSED
# ✅ test_stress01_race_condition_stock_collision PASSED
# ✅ test_stress02_websocket_concurrent_updates PASSED
#
# 4 passed in 3.45s
```

---

## Performance Targets (SLAs)

| Operation | Target | Status |
|-----------|--------|--------|
| Login | < 1.0s | ✅ Tested |
| Dashboard | < 2.0s | ✅ Tested |
| Stock Update | < 0.5s | 🔄 Needs test |
| Order Search | < 0.3s | 🔄 Needs test |
| Report Gen | < 5.0s | 🔄 Needs test |
| Concurrent Users | >= 70% @ 50 users | ✅ Tested |

---

## Advanced Performance Testing

### Run with Timing Output
```bash
pytest tests/test_production_ready.py::TestPerformance -v --durations=0
```
Shows slowest tests first

### Run with Coverage
```bash
pytest tests/test_production_ready.py::TestPerformance --cov=app --cov-report=html
```
See which code paths are hit during tests

### Run Multiple Times (Stability Check)
```bash
pytest tests/test_production_ready.py::TestPerformance -v --count=5
```
Runs each test 5 times to check consistency

---

## Performance Profiling (Future Enhancements)

### Install profiling tools
```bash
pip install py-spy memory-profiler pytest-benchmark
```

### Profile with py-spy
```bash
py-spy record -o profile.svg -- pytest tests/test_production_ready.py::TestPerformance
```

### Memory profiling
```bash
pip install memory-profiler
pytest tests/test_production_ready.py::TestPerformance --memray
```

### Benchmark regression tracking
```bash
pytest tests/ --benchmark-json=benchmark.json
```

---

## Load Testing (Future - Not Yet Implemented)

### Will use Locust for load testing
```bash
# Install Locust
pip install locust

# Create load test file (future)
# tests/load/locustfile.py

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Headless load test
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless
```

---

## Troubleshooting Performance Tests

### "Connection refused" Error
```
AssertionError: HTTPConnection(host='localhost', port=8000): Failed
```
**Solution:** Start API server first
```bash
python -m uvicorn app.main:app --reload
```

### "Timeout after 5s"
```
requests.exceptions.Timeout: HTTPConnection timeout
```
**Solution:** API is slow or tests running at same time
- Check if API is responding: `curl http://localhost:8000/docs`
- Close other resource-heavy apps
- Run tests one at a time: `pytest tests/test_production_ready.py::TestPerformance::test_perf01_login_response_time -v`

### "Test failed: X exceeded SLA"
```
AssertionError: Login too slow: 2.345s (target: 1.0s)
```
**Causes:**
- API server is overloaded
- Database queries are slow
- Network is slow
- Run test multiple times to check if consistent

**Solution:** Profile the API to find bottleneck
```bash
# In API code, add timing
import time
start = time.time()
# ... your code ...
elapsed = time.time() - start
print(f"Query took: {elapsed:.3f}s")
```

---

## Quick Commands Reference

```bash
# View all performance tests
pytest tests/test_production_ready.py -k "perf or stress" --collect-only

# Run only performance tests
pytest tests/test_production_ready.py -k "perf" -v

# Run only stress tests
pytest tests/test_production_ready.py -k "stress" -v

# Run with detailed output
pytest tests/test_production_ready.py::TestPerformance -vv --tb=long

# Run and show durations
pytest tests/test_production_ready.py::TestPerformance -v --durations=10

# Run without skips (need API running!)
pytest tests/test_production_ready.py::TestPerformance -v --runxfail
```

---

## Next Steps

1. ✅ **Today:** Run with API server to verify performance baseline
2. 🔄 **Next:** Add more performance tests for critical paths
3. 🔄 **Then:** Set up load testing infrastructure (Locust)
4. 🔄 **Finally:** Continuous performance monitoring in production

See `PERFORMANCE_LOAD_TESTING_ROADMAP.md` for complete strategy.

---

**To Run Performance Tests NOW:**

```bash
# Terminal 1
cd D:\Project\ERP2026\erp-softtoys
python -m uvicorn app.main:app --reload

# Terminal 2
cd D:\Project\ERP2026
pytest tests/test_production_ready.py::TestPerformance -v
```

That's it! 🚀
