"""
PermissionService Unit Tests
Tests the core PBAC service with Redis caching
"""
import pytest
import redis
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.permission_service import PermissionService
from app.core.models.users import User, UserRole
from app.core.models.permissions import Permission, RolePermission, UserCustomPermission


class TestPermissionServiceBasics:
    """Test basic permission checking"""
    
    def test_has_permission_direct_grant(self, db: Session, redis_client: redis.Redis):
        """User with direct permission grant should have access"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "test_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.allocate_material", "Cutting")
        self._grant_permission_to_user(db, user, permission)
        
        # Act
        has_perm = service.has_permission(db, user, "cutting.allocate_material")
        
        # Assert
        assert has_perm is True
    
    def test_has_permission_via_role(self, db: Session, redis_client: redis.Redis):
        """User should have permissions assigned to their role"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "operator", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.complete_operation", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, permission)
        
        # Act
        has_perm = service.has_permission(db, user, "cutting.complete_operation")
        
        # Assert
        assert has_perm is True
    
    def test_has_permission_denied(self, db: Session, redis_client: redis.Redis):
        """User without permission should be denied"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "no_perms", UserRole.OPERATOR_CUTTING)
        
        # Act
        has_perm = service.has_permission(db, user, "admin.manage_users")
        
        # Assert
        assert has_perm is False


class TestRoleHierarchy:
    """Test SPV inherits operator permissions"""
    
    def test_spv_inherits_operator_permissions(self, db: Session, redis_client: redis.Redis):
        """SPV Cutting should have all Operator Cutting permissions"""
        # Arrange
        service = PermissionService(redis_client)
        spv_user = self._create_user(db, "spv", UserRole.SPV_CUTTING)
        operator_permission = self._create_permission(db, "cutting.complete_operation", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, operator_permission)
        
        # Act
        has_perm = service.has_permission(db, spv_user, "cutting.complete_operation")
        
        # Assert
        assert has_perm is True
        
    def test_spv_has_additional_permissions(self, db: Session, redis_client: redis.Redis):
        """SPV should have permissions operators don't have"""
        # Arrange
        service = PermissionService(redis_client)
        spv_user = self._create_user(db, "spv", UserRole.SPV_CUTTING)
        operator_user = self._create_user(db, "operator", UserRole.OPERATOR_CUTTING)
        spv_permission = self._create_permission(db, "cutting.line_clearance", "Cutting")
        self._grant_permission_to_role(db, UserRole.SPV_CUTTING, spv_permission)
        
        # Act
        spv_has_perm = service.has_permission(db, spv_user, "cutting.line_clearance")
        operator_has_perm = service.has_permission(db, operator_user, "cutting.line_clearance")
        
        # Assert
        assert spv_has_perm is True
        assert operator_has_perm is False


class TestCustomPermissions:
    """Test custom permissions with expiration"""
    
    def test_custom_permission_active(self, db: Session, redis_client: redis.Redis):
        """User with active custom permission should have access"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "temp_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.handle_variance", "Cutting")
        
        # Grant custom permission (expires tomorrow)
        expires_at = datetime.utcnow() + timedelta(days=1)
        custom_perm = UserCustomPermission(
            user_id=user.id,
            permission_id=permission.id,
            granted_by=1,
            expires_at=expires_at,
            reason="Temporary coverage for absent SPV"
        )
        db.add(custom_perm)
        db.commit()
        
        # Act
        has_perm = service.has_permission(db, user, "cutting.handle_variance")
        
        # Assert
        assert has_perm is True
    
    def test_custom_permission_expired(self, db: Session, redis_client: redis.Redis):
        """User with expired custom permission should be denied"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "expired_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.handle_variance", "Cutting")
        
        # Grant expired custom permission
        expires_at = datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        custom_perm = UserCustomPermission(
            user_id=user.id,
            permission_id=permission.id,
            granted_by=1,
            expires_at=expires_at,
            reason="Expired temporary access"
        )
        db.add(custom_perm)
        db.commit()
        
        # Act
        has_perm = service.has_permission(db, user, "cutting.handle_variance")
        
        # Assert
        assert has_perm is False


class TestRedisCaching:
    """Test Redis caching performance and behavior"""
    
    def test_cache_cold_performance(self, db: Session, redis_client: redis.Redis):
        """Cold cache permission check should be <10ms"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "perf_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.view_status", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, permission)
        
        # Clear cache
        redis_client.flushdb()
        
        # Act
        start = time.time()
        has_perm = service.has_permission(db, user, "cutting.view_status", use_cache=True)
        elapsed_ms = (time.time() - start) * 1000
        
        # Assert
        assert has_perm is True
        assert elapsed_ms < 10  # <10ms for cold cache
    
    def test_cache_hot_performance(self, db: Session, redis_client: redis.Redis):
        """Hot cache permission check should be <1ms"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "cached_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.view_status", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, permission)
        
        # Warm cache
        service.has_permission(db, user, "cutting.view_status", use_cache=True)
        
        # Act
        start = time.time()
        has_perm = service.has_permission(db, user, "cutting.view_status", use_cache=True)
        elapsed_ms = (time.time() - start) * 1000
        
        # Assert
        assert has_perm is True
        assert elapsed_ms < 1  # <1ms for hot cache
    
    def test_cache_invalidation(self, db: Session, redis_client: redis.Redis):
        """Cache should invalidate when permissions change"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "invalidate_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.view_status", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, permission)
        
        # Warm cache
        has_perm_before = service.has_permission(db, user, "cutting.view_status")
        assert has_perm_before is True
        
        # Act: Revoke permission
        self._revoke_permission_from_role(db, UserRole.OPERATOR_CUTTING, permission)
        service.invalidate_user_cache(user.id)
        
        # Assert: Cache should reflect revocation
        has_perm_after = service.has_permission(db, user, "cutting.view_status")
        assert has_perm_after is False
    
    def test_cache_ttl(self, db: Session, redis_client: redis.Redis):
        """Cache should respect TTL (5 minutes default)"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "ttl_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.view_status", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, permission)
        
        # Act: Check permission (creates cache entry)
        service.has_permission(db, user, "cutting.view_status")
        
        # Check Redis TTL
        cache_key = f"perm:{user.id}:cutting.view_status"
        ttl = redis_client.ttl(cache_key)
        
        # Assert: TTL should be ~300 seconds (5 minutes)
        assert 290 < ttl <= 300


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_redis_unavailable_fallback(self, db: Session):
        """Should fallback to database if Redis unavailable"""
        # Arrange
        service = PermissionService(None)  # No Redis client
        user = self._create_user(db, "fallback_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.view_status", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, permission)
        
        # Act
        has_perm = service.has_permission(db, user, "cutting.view_status", use_cache=False)
        
        # Assert
        assert has_perm is True
    
    def test_permission_code_case_sensitive(self, db: Session, redis_client: redis.Redis):
        """Permission codes should be case-sensitive"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "case_user", UserRole.OPERATOR_CUTTING)
        permission = self._create_permission(db, "cutting.view_status", "Cutting")
        self._grant_permission_to_role(db, UserRole.OPERATOR_CUTTING, permission)
        
        # Act
        has_perm_correct = service.has_permission(db, user, "cutting.view_status")
        has_perm_wrong_case = service.has_permission(db, user, "Cutting.View_Status")
        
        # Assert
        assert has_perm_correct is True
        assert has_perm_wrong_case is False
    
    def test_nonexistent_permission(self, db: Session, redis_client: redis.Redis):
        """Checking non-existent permission should return False"""
        # Arrange
        service = PermissionService(redis_client)
        user = self._create_user(db, "any_user", UserRole.OPERATOR_CUTTING)
        
        # Act
        has_perm = service.has_permission(db, user, "nonexistent.permission")
        
        # Assert
        assert has_perm is False


# ============================================================================
# HELPER METHODS
# ============================================================================

def _create_user(db: Session, username: str, role: UserRole) -> User:
    """Create test user"""
    from app.core.security import PasswordUtils
    user = User(
        username=username,
        email=f"{username}@example.com",
        full_name=f"Test User {username}",
        hashed_password=PasswordUtils.hash_password("password123"),
        role=role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_permission(db: Session, code: str, module: str) -> Permission:
    """Create test permission"""
    permission = Permission(
        code=code,
        name=code.replace(".", " ").title(),
        module=module,
        description=f"Test permission: {code}"
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def _grant_permission_to_user(db: Session, user: User, permission: Permission):
    """Grant permission directly to user"""
    custom_perm = UserCustomPermission(
        user_id=user.id,
        permission_id=permission.id,
        granted_by=1,
        expires_at=None,  # No expiration
        reason="Test permission grant"
    )
    db.add(custom_perm)
    db.commit()


def _grant_permission_to_role(db: Session, role: UserRole, permission: Permission):
    """Grant permission to role"""
    role_perm = RolePermission(
        role=role.value,
        permission_id=permission.id
    )
    db.add(role_perm)
    db.commit()


def _revoke_permission_from_role(db: Session, role: UserRole, permission: Permission):
    """Revoke permission from role"""
    role_perm = db.query(RolePermission).filter(
        RolePermission.role == role.value,
        RolePermission.permission_id == permission.id
    ).first()
    if role_perm:
        db.delete(role_perm)
        db.commit()


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def redis_client():
    """Redis client for testing"""
    client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
    yield client
    # Clean up after each test
    client.flushdb()


@pytest.fixture
def db(session):
    """Database session"""
    return session
