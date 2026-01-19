"""
Comprehensive Test Suite for Phase 1 - Authentication & Admin
Tests for user registration, login, token management, and role-based access
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.core.database import Base, get_db
from app.core.models.users import User, UserRole
from app.core.security import PasswordUtils, TokenUtils
from app.core.config import settings


# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepass123",
        "full_name": "Test User",
        "roles": ["operator_cutting"]
    }


@pytest.fixture
def admin_user(test_user_data):
    """Create admin user"""
    db = TestingSessionLocal()
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=PasswordUtils.hash_password("adminpass123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin


# ==================== REGISTRATION TESTS ====================

class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_register_success(self, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["is_active"] is True
    
    def test_register_duplicate_username(self, test_user_data):
        """Test duplicate username rejection"""
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_register_duplicate_email(self, test_user_data):
        """Test duplicate email rejection"""
        client.post("/api/v1/auth/register", json=test_user_data)
        test_user_data["username"] = "differentuser"
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self, test_user_data):
        """Test invalid email rejection"""
        test_user_data["email"] = "invalid-email"
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_short_password(self, test_user_data):
        """Test short password rejection"""
        test_user_data["password"] = "short"
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 422


# ==================== LOGIN TESTS ====================

class TestUserLogin:
    """Test user login endpoint"""
    
    @pytest.fixture
    def registered_user(self, test_user_data):
        """Create registered user"""
        client.post("/api/v1/auth/register", json=test_user_data)
        return test_user_data
    
    def test_login_success(self, registered_user):
        """Test successful login"""
        response = client.post("/api/v1/auth/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_with_email(self, registered_user):
        """Test login using email instead of username"""
        response = client.post("/api/v1/auth/login", json={
            "username": registered_user["email"],
            "password": registered_user["password"]
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self, registered_user):
        """Test login with invalid credentials"""
        response = client.post("/api/v1/auth/login", json={
            "username": registered_user["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        assert response.status_code == 401
    
    def test_login_account_locked_after_attempts(self, registered_user):
        """Test account lock after 5 failed attempts"""
        # Make 5 failed attempts
        for _ in range(5):
            client.post("/api/v1/auth/login", json={
                "username": registered_user["username"],
                "password": "wrongpassword"
            })
        
        # 6th attempt should be locked
        response = client.post("/api/v1/auth/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        assert response.status_code == 429
        assert "locked" in response.json()["detail"].lower()


# ==================== TOKEN TESTS ====================

class TestTokenManagement:
    """Test token refresh and validation"""
    
    @pytest.fixture
    def login_response(self, test_user_data):
        """Get login response"""
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        return response.json()
    
    def test_refresh_token_success(self, login_response):
        """Test successful token refresh"""
        response = client.post("/api/v1/auth/refresh", params={
            "refresh_token_str": login_response["refresh_token"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != login_response["access_token"]
    
    def test_refresh_invalid_token(self):
        """Test refresh with invalid token"""
        response = client.post("/api/v1/auth/refresh", params={
            "refresh_token_str": "invalid.token.here"
        })
        assert response.status_code == 401
    
    def test_access_protected_endpoint(self, login_response):
        """Test accessing protected endpoint with token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_response['access_token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"]
    
    def test_access_protected_endpoint_no_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403


# ==================== PROFILE TESTS ====================

class TestUserProfile:
    """Test user profile endpoints"""
    
    @pytest.fixture
    def auth_headers(self, test_user_data):
        """Get authorization headers"""
        client.post("/api/v1/auth/register", json=test_user_data)
        login = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }).json()
        return {"Authorization": f"Bearer {login['access_token']}"}
    
    def test_get_current_user(self, auth_headers, test_user_data):
        """Test getting current user profile"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
    
    def test_change_password_success(self, auth_headers, test_user_data):
        """Test successful password change"""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": test_user_data["password"],
                "new_password": "newpassword123"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]
    
    def test_change_password_wrong_old(self, auth_headers):
        """Test password change with wrong old password"""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123"
            },
            headers=auth_headers
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_logout(self, auth_headers):
        """Test logout endpoint"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]


# ==================== ADMIN TESTS ====================

class TestAdminEndpoints:
    """Test admin user management endpoints"""
    
    @pytest.fixture
    def admin_headers(self, admin_user):
        """Get admin authorization headers"""
        token = TokenUtils.create_access_token(
            user_id=admin_user.id,
            username=admin_user.username,
            email=admin_user.email,
            roles=["Admin"]
        )
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def regular_user(self, test_user_data):
        """Create regular user"""
        client.post("/api/v1/auth/register", json=test_user_data)
        return test_user_data
    
    def test_list_users_admin(self, admin_headers):
        """Test listing users as admin"""
        response = client.get("/api/v1/admin/users", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_users_non_admin(self, test_user_data):
        """Test non-admin cannot list users"""
        client.post("/api/v1/auth/register", json=test_user_data)
        login = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }).json()
        
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {login['access_token']}"}
        )
        assert response.status_code == 403
    
    def test_get_user_details_admin(self, admin_headers, admin_user):
        """Test getting user details as admin"""
        response = client.get(
            f"/api/v1/admin/users/{admin_user.id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == "admin"
    
    def test_deactivate_user(self, admin_headers, admin_user, test_user_data):
        """Test deactivating user"""
        # Create user to deactivate
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Get user ID
        users_response = client.get("/api/v1/admin/users", headers=admin_headers)
        user_id = next(u["id"] for u in users_response.json() if u["username"] == test_user_data["username"])
        
        # Deactivate
        response = client.post(
            f"/api/v1/admin/users/{user_id}/deactivate",
            headers=admin_headers
        )
        assert response.status_code == 200
    
    def test_cannot_deactivate_self(self, admin_headers, admin_user):
        """Test admin cannot deactivate themselves"""
        response = client.post(
            f"/api/v1/admin/users/{admin_user.id}/deactivate",
            headers=admin_headers
        )
        assert response.status_code == 400


# ==================== ROLE-BASED ACCESS TESTS ====================

class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_operator_role_access(self, test_user_data):
        """Test operator role permissions"""
        client.post("/api/v1/auth/register", json=test_user_data)
        login = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }).json()
        
        headers = {"Authorization": f"Bearer {login['access_token']}"}
        
        # Operator should not access admin endpoints
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
