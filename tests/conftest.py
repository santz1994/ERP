"""
Pytest Configuration & Fixtures
================================
Centralized configuration for all test environments

Author: IT QA Team
Date: 2026-01-22
"""

import os
import sys
from typing import Generator, Dict, Any
import pytest
from dotenv import load_dotenv
import requests
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Load environment variables
load_dotenv()

# ============================================================================
# TEST ENVIRONMENT SETUP
# ============================================================================

# Detect test environment
TEST_ENV = os.getenv("TEST_ENV", "docker")  # docker, local, ci
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

print(f"\n{'='*70}")
print(f"TEST ENVIRONMENT: {TEST_ENV}")
print(f"DEBUG MODE: {DEBUG_MODE}")
print(f"{'='*70}\n")

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

if TEST_ENV == "docker":
    # Using Docker PostgreSQL container
    DATABASE_URL = (
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER', 'postgres')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'erp_quty_karunia')}"
    )
elif TEST_ENV == "ci":
    # Using CI/CD PostgreSQL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://test_user:test_password@postgres:5432/erp_test"
    )
else:
    # Local development
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/erp_quty_karunia"
    )

print(f"Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'MISSING'}")

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_V1_URL = f"{API_BASE_URL}/api/v1"

TEST_USERS = {
    "developer": {
        "username": "developer",
        "password": os.getenv("DEV_PASSWORD", "password123"),
        "role": "DEVELOPER"
    },
    "admin": {
        "username": "admin",
        "password": os.getenv("ADMIN_PASSWORD", "admin123"),
        "role": "ADMIN"
    },
    "admin_cutting": {
        "username": "admin_cutting",
        "password": os.getenv("ADMIN_CUTTING_PASSWORD", "password123"),
        "role": "ADMIN_CUTTING"
    }
}

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: Mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow"
    )
    config.addinivalue_line(
        "markers", "critical: Mark test as critical path"
    )


# ============================================================================
# FIXTURES - API
# ============================================================================

@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Provide API base URL"""
    return API_V1_URL


@pytest.fixture(scope="session")
def test_users() -> Dict[str, Dict[str, str]]:
    """Provide test user credentials"""
    return TEST_USERS


@pytest.fixture
def developer_token(requests_session) -> str:
    """Get developer authentication token"""
    try:
        response = requests_session.post(
            f"{API_V1_URL}/auth/login",
            json=TEST_USERS["developer"],
            timeout=5
        )
        if response.status_code != 200:
            pytest.skip(f"API unavailable or developer user not found: {response.status_code}")
        return response.json().get("access_token")
    except Exception as e:
        pytest.skip(f"Could not connect to API: {str(e)}")


@pytest.fixture
def admin_token(requests_session) -> str:
    """Get admin authentication token"""
    try:
        response = requests_session.post(
            f"{API_V1_URL}/auth/login",
            json=TEST_USERS["admin"],
            timeout=5
        )
        if response.status_code != 200:
            pytest.skip("Admin user not available in test environment")
        return response.json().get("access_token")
    except Exception as e:
        pytest.skip(f"Could not connect to API: {str(e)}")


@pytest.fixture
def admin_cutting_token(requests_session) -> str:
    """Get admin_cutting authentication token"""
    try:
        response = requests_session.post(
            f"{API_V1_URL}/auth/login",
            json=TEST_USERS["admin_cutting"],
            timeout=5
        )
        if response.status_code != 200:
            pytest.skip("Admin Cutting user not available in test environment")
        return response.json().get("access_token")
    except Exception as e:
        pytest.skip(f"Could not connect to API: {str(e)}")


@pytest.fixture
def requests_session() -> requests.Session:
    """Create requests session with retry logic"""
    session = requests.Session()
    
    # Add retry logic
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    yield session
    session.close()


@pytest.fixture
def api_headers(developer_token) -> Dict[str, str]:
    """Provide API headers with authentication"""
    return {
        "Authorization": f"Bearer {developer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


# ============================================================================
# FIXTURES - DATABASE
# ============================================================================

@pytest.fixture(scope="session")
def db_engine():
    """Create database engine with connection pooling"""
    try:
        engine = create_engine(
            DATABASE_URL,
            echo=DEBUG_MODE,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 10}
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✅ Database connection successful")
        yield engine
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        pytest.skip(f"Database not available: {e}")
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine):
    """Create session factory"""
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    return SessionLocal


@pytest.fixture
def db_session(db_session_factory) -> Generator[Session, None, None]:
    """Provide database session with rollback"""
    session = db_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def clean_db(db_session):
    """Fixture to clean database before test"""
    yield db_session
    # Cleanup after test
    db_session.rollback()


# ============================================================================
# FIXTURES - UTILITIES
# ============================================================================

@pytest.fixture
def api_client(api_base_url, developer_token):
    """Provide configured API client"""
    class APIClient:
        def __init__(self, base_url: str, token: str):
            self.base_url = base_url
            self.token = token
            self.session = requests.Session()
        
        def get(self, endpoint: str, **kwargs):
            return self.session.get(
                f"{self.base_url}{endpoint}",
                headers={"Authorization": f"Bearer {self.token}"},
                **kwargs
            )
        
        def post(self, endpoint: str, **kwargs):
            return self.session.post(
                f"{self.base_url}{endpoint}",
                headers={"Authorization": f"Bearer {self.token}"},
                **kwargs
            )
        
        def put(self, endpoint: str, **kwargs):
            return self.session.put(
                f"{self.base_url}{endpoint}",
                headers={"Authorization": f"Bearer {self.token}"},
                **kwargs
            )
        
        def delete(self, endpoint: str, **kwargs):
            return self.session.delete(
                f"{self.base_url}{endpoint}",
                headers={"Authorization": f"Bearer {self.token}"},
                **kwargs
            )
        
        def close(self):
            self.session.close()
    
    client = APIClient(api_base_url, developer_token)
    yield client
    client.close()


@pytest.fixture
def sample_data():
    """Provide sample test data"""
    return {
        "product": {
            "name": "Test Product",
            "sku": "TEST-001",
            "quantity": 100
        },
        "work_order": {
            "order_number": "WO-2026-001",
            "product_id": 1,
            "quantity": 50
        },
        "qc_inspection": {
            "inspection_type": "INCOMING",
            "status": "PASSED",
            "pass_rate": 95.5
        }
    }


# ============================================================================
# HOOKS
# ============================================================================

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Add custom test reporting"""
    if call.when == "setup":
        print(f"\n{'─'*70}")
        print(f"🧪 Running: {item.name}")
        print(f"{'─'*70}")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)


# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

if __name__ == "__main__":
    print("\n✅ Conftest configuration loaded successfully")
    print(f"   API URL: {API_V1_URL}")
    print(f"   Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'MISSING'}")
    print(f"   Test Users: {', '.join(TEST_USERS.keys())}")
