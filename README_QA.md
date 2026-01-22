# 🧪 ERP 2026 - Complete QA Testing Infrastructure

**Status**: ✅ READY FOR PRODUCTION
**Version**: 7.0.0  
**Last Updated**: January 22, 2026

---

## 📋 Overview

This project includes a comprehensive QA testing infrastructure with:

- ✅ **Unit & Integration Testing** - Pytest with 80% coverage minimum
- ✅ **Type Checking** - MyPy static analysis
- ✅ **Code Quality** - Ruff, Black, isort
- ✅ **Security Scanning** - Bandit, Safety
- ✅ **Load Testing** - Locust performance simulation
- ✅ **CI/CD Automation** - GitHub Actions pipeline
- ✅ **Multi-Environment Support** - Docker, Local, CI/CD

---

## 🚀 Quick Start

### Windows
```bash
# Navigate to project root
cd d:\Project\ERP2026

# Run setup script
.\qa-setup.bat

# Start backend
cd erp-softtoys
uvicorn app.main:app --reload --port 8000
```

### macOS / Linux
```bash
# Navigate to project root
cd /path/to/ERP2026

# Run setup script
chmod +x qa-setup.sh
./qa-setup.sh

# Start backend
cd erp-softtoys
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
# Rebuild containers
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Run tests inside container
docker-compose exec backend pytest tests/ -v
```

---

## 📁 Key Files & Locations

### Configuration Files
| File | Purpose | Location |
|------|---------|----------|
| `pyproject.toml` | Python project configuration | Project root |
| `requirements-dev.txt` | QA dependencies | `erp-softtoys/` |
| `tests/conftest.py` | Test fixtures & configuration | `tests/` |
| `.github/workflows/qa-testing-pipeline.yml` | CI/CD pipeline | `.github/workflows/` |

### Source Files
| File | Purpose | Location |
|------|---------|----------|
| `app/api/v1/qa_convenience_endpoints.py` | Missing convenience endpoints | `erp-softtoys/app/api/v1/` |
| Test suites | Unit & integration tests | `tests/` |

### Documentation
| File | Content |
|------|---------|
| `QA_TEST_REPORT_2026-01-22.md` | Initial test report |
| `QA_INFRASTRUCTURE_IMPLEMENTATION_2026.md` | Setup documentation |
| `FINAL_QA_SETUP_SUMMARY_2026.md` | Complete implementation summary |
| `README_QA.md` | This file |

---

## 🧪 Running Tests

### All Tests
```bash
cd erp-softtoys

# Run all tests
pytest ../tests/ -v

# Run with coverage report
pytest ../tests/ -v --cov=app --cov-report=html

# Run and generate HTML report
pytest ../tests/ -v --html=report.html --self-contained-html
```

### By Category
```bash
# Unit tests only
pytest ../tests/ -m "unit" -v

# Integration tests
pytest ../tests/ -m "integration" -v

# Critical path tests
pytest ../tests/ -m "critical" -v

# Security tests
pytest ../tests/ -m "security" -v
```

### Specific Test Suites
```bash
# Boundary value analysis (23 tests)
pytest ../tests/test_boundary_value_analysis.py -v

# Database integrity (9 tests)
pytest ../tests/test_database_integrity.py -v

# Production readiness (29 tests)
pytest ../tests/test_production_ready.py -v

# RBAC matrix (15 tests)
pytest ../tests/test_rbac_matrix.py -v
```

### With Markers
```bash
# Run with specific marker
pytest ../tests/ -m critical -v

# Exclude markers
pytest ../tests/ -m "not slow" -v

# Show available markers
pytest ../tests/ --markers
```

### Test Configuration
```bash
# Run with timeout
pytest ../tests/ --timeout=300 -v

# Verbose output
pytest ../tests/ -vv

# Stop on first failure
pytest ../tests/ -x -v

# Run last failed
pytest ../tests/ --lf -v

# Show print statements
pytest ../tests/ -s -v
```

---

## 📊 Code Quality & Analysis

### Type Checking
```bash
cd erp-softtoys

# Check type hints
mypy app --ignore-missing-imports

# Show all errors
mypy app --show-error-codes

# Generate report
mypy app --html=mypy_report
```

### Linting
```bash
# Run Ruff (fast linting)
ruff check app

# Fix issues automatically
ruff check app --fix

# Show specific issues
ruff check app --select E,F,W
```

### Code Formatting
```bash
# Format with Black
black app

# Check without formatting
black --check app

# Format specific file
black app/main.py
```

### Import Sorting
```bash
# Sort imports
isort app

# Check without sorting
isort --check-only app
```

### Security Scanning
```bash
# Bandit vulnerability scan
bandit -r app -f txt

# Detailed report
bandit -r app -f json -o bandit-report.json

# Safety dependency check
safety check --json > safety-report.json
```

---

## 📈 Performance & Load Testing

### Load Testing with Locust
```bash
cd erp-softtoys

# Simple load test
locust -f ../tests/locustfile.py --headless \
  -u 10 -r 2 -t 60s --host http://localhost:8000

# More users (heavy load)
locust -f ../tests/locustfile.py --headless \
  -u 100 -r 10 -t 300s --host http://localhost:8000

# Web UI (interactive)
locust -f ../tests/locustfile.py \
  --host http://localhost:8000
# Then open http://localhost:8089
```

### Locust Output Interpretation
```
Type                               # reqs     # failures
─────────────────────────────────────────────────────────
GET  /api/v1/auth/me            │   1000   │  0 (0%)    │
POST /api/v1/auth/login         │    500   │  5 (1%)    │
GET  /api/v1/quality/stats      │   2000   │  0 (0%)    │

Response Time Percentiles:
50th percentile:   50ms  ✅ Good
95th percentile:  200ms  ✅ Acceptable  
99th percentile:  500ms  ⚠️  Monitor
```

---

## 🔍 Debugging & Troubleshooting

### Database Connection Issues
```python
# Check in conftest.py
import os
print(os.getenv("DATABASE_URL"))  # Verify URL
print(os.getenv("TEST_ENV"))      # Check environment

# Manually test connection
from sqlalchemy import create_engine, text
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())
```

### Test Failures
```bash
# Run with detailed traceback
pytest ../tests/test_file.py -v --tb=long

# Run with print output
pytest ../tests/test_file.py -s -v

# Run specific test
pytest ../tests/test_file.py::TestClass::test_method -v

# Run with debugging
pytest ../tests/test_file.py -v --pdb
```

### Performance Issues
```bash
# Show slowest tests
pytest ../tests/ -v --durations=10

# Run with profiling
pytest ../tests/ -v --profile

# Memory profiling
pytest ../tests/ -v --memray
```

---

## 🔐 Security Best Practices

### Test Data
```python
# DON'T: Hardcode credentials
password = "admin123"  # ❌ WRONG

# DO: Use environment variables
from os import getenv
password = getenv("TEST_PASSWORD", "default")  # ✅ RIGHT
```

### Secret Management
```bash
# Environment variables
export DB_PASSWORD="secret"
export API_TOKEN="token123"

# Or in .env file (NOT committed)
DB_PASSWORD=secret
API_TOKEN=token123
```

### Credentials in Tests
```python
# From conftest.py - centralized, environment-aware
TEST_USERS = {
    "developer": {
        "username": "developer",
        "password": os.getenv("DEV_PASSWORD", "password123"),
        "role": "DEVELOPER"
    }
}
```

---

## 📊 Coverage Reports

### Generate Coverage
```bash
cd erp-softtoys

# Generate HTML report (80% minimum enforced)
pytest ../tests/ --cov=app --cov-report=html

# View report
open htmlcov/index.html          # macOS
start htmlcov/index.html         # Windows
xdg-open htmlcov/index.html      # Linux
```

### Coverage Requirements
```ini
# From pyproject.toml
[tool.coverage.report]
fail_under = 80  # Fail if below 80%
precision = 2    # Two decimal places
skip_covered = false  # Show covered lines
```

### Coverage Tips
- Focus on critical business logic
- Test error paths and edge cases
- Use `pytest --cov-report=term-missing` to see uncovered lines
- Aim for >90% on production code

---

## 🤖 CI/CD Pipeline

### Automatic Triggers
```yaml
# Runs automatically on:
- Push to main/develop branches
- Pull requests
- Daily schedule (2 AM UTC)
- Manual trigger via GitHub UI
```

### Pipeline Stages
1. **Python Tests** - Unit & integration tests
2. **API Testing** - Production readiness  
3. **Performance** - Load testing (scheduled only)
4. **Security** - Bandit, Safety, Semgrep
5. **Code Quality** - Linting, formatting
6. **Summary** - Results aggregation

### GitHub Actions Status
```bash
# View in GitHub Actions tab
# Or use GitHub CLI:
gh run list
gh run view <run-id>
gh run view <run-id> --log
```

---

## 📚 Test Data Management

### Using Fixtures
```python
# In conftest.py or your test file
@pytest.fixture
def sample_product():
    """Create sample product for testing"""
    return {
        "name": "Test Product",
        "sku": "TEST-001",
        "quantity": 100
    }

# Use in test
def test_something(sample_product):
    assert sample_product["quantity"] == 100
```

### Database Cleanup
```python
def test_with_cleanup(db_session):
    """Test with automatic cleanup"""
    # Create data
    item = create_test_item(db_session)
    
    # Test something
    assert item.id is not None
    
    # Cleanup happens automatically (conftest fixture)
    # db_session.rollback() called after test
```

---

## 🎯 Common Workflows

### Pre-Commit Checks
```bash
# Before committing code
black app/                    # Format
isort app/                    # Sort imports
ruff check app --fix          # Lint and fix
pytest ../tests/ -v --cov     # Run tests
bandit -r app                 # Security
```

### Code Review Checklist
```markdown
- [ ] All tests passing (pytest)
- [ ] Coverage >= 80% (coverage.py)
- [ ] Type hints valid (mypy)
- [ ] Code formatted (black)
- [ ] No lint issues (ruff)
- [ ] No security issues (bandit)
- [ ] Imports sorted (isort)
```

### Release Checklist
```bash
# Full QA before release
pytest ../tests/ -v --cov=app --cov-report=html
bandit -r app -f json -o security-report.json
safety check --json > dependency-report.json
mypy app --html=type-report

# Review reports
open htmlcov/index.html
open security-report.json
```

---

## 📖 Additional Resources

### Test Markers
```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.critical       # Critical path
@pytest.mark.security       # Security test
@pytest.mark.slow           # Slow test
@pytest.mark.skip           # Skip test
@pytest.mark.parametrize    # Parameterized test
```

### Pytest Fixtures
```python
@pytest.fixture(scope="session")   # Runs once per session
@pytest.fixture(scope="module")    # Runs once per module
@pytest.fixture(scope="function")  # Runs before each test (default)
@pytest.fixture(scope="class")     # Runs once per class
```

### Environment Variables
```bash
# Testing
TEST_ENV=docker|local|ci
API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@host:5432/db

# Development
DEBUG=true
LOG_LEVEL=DEBUG

# Security
DEV_PASSWORD=password123
ADMIN_PASSWORD=admin123
```

---

## 🆘 Support & Issues

### Getting Help
1. Check the documentation files listed above
2. Review test output and logs
3. Run with verbose flag: `-vv`
4. Check GitHub Issues for known problems
5. Create new issue with details

### Common Issues & Solutions

**Issue**: Database connection failed
```bash
# Solution: Ensure PostgreSQL is running
docker ps | grep postgres
# or check connection: psql -U postgres -h localhost
```

**Issue**: Import errors in tests
```bash
# Solution: Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/erp-softtoys"
```

**Issue**: Tests hanging
```bash
# Solution: Add timeout
pytest ../tests/ --timeout=300 -v
```

---

## 📝 Configuration Reference

### pytest.ini Options
```ini
addopts = -v --tb=short --cov=app --cov-report=html
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### pyproject.toml
```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
```

### conftest.py
```python
# Centralized configuration
DATABASE_URL = "postgresql://..."
API_URL = "http://localhost:8000"
TEST_ENV = "docker|local|ci"
```

---

## ✅ Final Checklist

Before considering tests complete:

- [ ] All tests passing (> 80% success rate)
- [ ] Coverage above 80%
- [ ] Type checking passes
- [ ] No lint issues
- [ ] No security vulnerabilities
- [ ] Load test passed (< 5% failure rate)
- [ ] Documentation up-to-date
- [ ] CI/CD pipeline green
- [ ] Can run in Docker
- [ ] Can run locally
- [ ] Can run in CI/CD

---

## 🎓 Further Reading

- [Pytest Documentation](https://docs.pytest.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Locust Documentation](https://docs.locust.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## 📄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-01-22 | Complete QA infrastructure setup |
| 1.0 | 2026-01-22 | Initial test suite |

---

**Last Updated**: January 22, 2026  
**Maintained By**: IT QA Team  
**License**: Internal Use Only

---

## 🚀 Ready to Start?

1. Run: `cd erp-softtoys && python ../tests/conftest.py`
2. Execute: `pytest ../tests/ -v`
3. Monitor: Check GitHub Actions after pushing
4. Deploy: Rebuild docker with `docker-compose up -d`

**Happy Testing! 🎉**
