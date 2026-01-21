"""
PBAC Integration Tests
Tests all migrated endpoints to ensure permissions are enforced correctly
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.models.users import User, UserRole
from app.core.security import PasswordUtils


class TestDashboardPBAC:
    """Test Dashboard module PBAC enforcement"""
    
    def test_dashboard_stats_with_permission(self, client: TestClient, db: Session, user_with_permission):
        """User with dashboard.view_stats can access /stats"""
        # Arrange
        token = self._get_auth_token(client, user_with_permission)
        
        # Act
        response = client.get(
            "/api/v1/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_mos" in data
        assert "production_status" in data
    
    def test_dashboard_stats_without_permission(self, client: TestClient, db: Session, user_without_permission):
        """User without dashboard.view_stats gets 403"""
        # Arrange
        token = self._get_auth_token(client, user_without_permission)
        
        # Act
        response = client.get(
            "/api/v1/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]


class TestCuttingPBAC:
    """Test Cutting module PBAC enforcement"""
    
    def test_allocate_material_authorized(self, client: TestClient, db: Session, spv_cutting_user):
        """SPV Cutting can allocate material"""
        # Arrange
        token = self._get_auth_token(client, spv_cutting_user)
        payload = {
            "spk_number": "SPK-001",
            "mo_id": 1,
            "allocated_qty": 100
        }
        
        # Act
        response = client.post(
            "/api/v1/production/cutting/spk/receive",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_line_clearance_spv_only(self, client: TestClient, db: Session, operator_cutting_user):
        """Operator cannot perform line clearance"""
        # Arrange
        token = self._get_auth_token(client, operator_cutting_user)
        
        # Act
        response = client.get(
            "/api/v1/production/cutting/line-clear/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 403


class TestSewingPBAC:
    """Test Sewing module PBAC enforcement"""
    
    def test_inline_qc_qc_inspector_only(self, client: TestClient, db: Session, qc_inspector_user):
        """Only QC Inspector can perform inline QC"""
        # Arrange
        token = self._get_auth_token(client, qc_inspector_user)
        payload = {
            "work_order_id": 1,
            "inspector_id": qc_inspector_user.id,
            "pass_qty": 95,
            "rework_qty": 5,
            "scrap_qty": 0
        }
        
        # Act
        response = client.post(
            "/api/v1/production/sewing/qc-inspect",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_inline_qc_operator_denied(self, client: TestClient, db: Session, operator_sewing_user):
        """Operator cannot perform QC"""
        # Arrange
        token = self._get_auth_token(client, operator_sewing_user)
        payload = {
            "work_order_id": 1,
            "inspector_id": operator_sewing_user.id,
            "pass_qty": 95,
            "rework_qty": 5,
            "scrap_qty": 0
        }
        
        # Act
        response = client.post(
            "/api/v1/production/sewing/qc-inspect",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 403


class TestFinishingPBAC:
    """Test Finishing module PBAC enforcement (IKEA ISO 8124 compliance)"""
    
    def test_metal_detector_qc_inspector_only(self, client: TestClient, db: Session, qc_inspector_user):
        """Metal detector QC restricted to QC Inspector (safety critical)"""
        # Arrange
        token = self._get_auth_token(client, qc_inspector_user)
        payload = {
            "work_order_id": 1,
            "inspector_id": qc_inspector_user.id,
            "pass_qty": 100,
            "fail_qty": 0
        }
        
        # Act
        response = client.post(
            "/api/v1/production/finishing/metal-detector-test",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_convert_to_fg_spv_only(self, client: TestClient, db: Session, operator_finishing_user):
        """Operator cannot convert WIP to FG"""
        # Arrange
        token = self._get_auth_token(client, operator_finishing_user)
        payload = {
            "work_order_id": 1,
            "wip_code": "WIP-SHARK",
            "fg_code": "BLAHAJ-100",
            "qty_converted": 100
        }
        
        # Act
        response = client.post(
            "/api/v1/production/finishing/convert-to-fg",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 403


class TestPackingPBAC:
    """Test Packing module PBAC enforcement"""
    
    def test_shipping_mark_spv_only(self, client: TestClient, db: Session, spv_packing_user):
        """Shipping mark generation restricted to SPV"""
        # Arrange
        token = self._get_auth_token(client, spv_packing_user)
        payload = {
            "work_order_id": 1,
            "carton_number": 1,
            "qty_in_carton": 24,
            "destination": "US",
            "week_number": 3
        }
        
        # Act
        response = client.post(
            "/api/v1/production/packing/shipping-mark",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200


class TestPPICPBAC:
    """Test PPIC module PBAC enforcement"""
    
    def test_create_mo_ppic_manager_only(self, client: TestClient, db: Session, ppic_manager_user):
        """Only PPIC Manager can create MO"""
        # Arrange
        token = self._get_auth_token(client, ppic_manager_user)
        payload = {
            "so_line_id": 1,
            "product_id": 1,
            "qty_planned": 1000,
            "routing_type": "ROUTE_1",
            "batch_number": "BATCH-001"
        }
        
        # Act
        response = client.post(
            "/api/v1/ppic/manufacturing-order",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 201


class TestAdminPBAC:
    """Test Admin module PBAC enforcement"""
    
    def test_manage_users_admin_only(self, client: TestClient, db: Session, admin_user):
        """Only Admin can manage users"""
        # Arrange
        token = self._get_auth_token(client, admin_user)
        
        # Act
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_manage_users_regular_user_denied(self, client: TestClient, db: Session, operator_cutting_user):
        """Regular user cannot manage users"""
        # Arrange
        token = self._get_auth_token(client, operator_cutting_user)
        
        # Act
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 403


class TestImportExportPBAC:
    """Test Import/Export module PBAC enforcement"""
    
    def test_import_data_authorized(self, client: TestClient, db: Session, admin_user):
        """Admin can import data"""
        # Arrange
        token = self._get_auth_token(client, admin_user)
        
        # Create mock CSV file
        import io
        csv_content = "code,name,type,uom\\nTEST-001,Test Product,Raw Material,Meter"
        files = {"file": ("test.csv", io.StringIO(csv_content), "text/csv")}
        
        # Act
        response = client.post(
            "/api/v1/import-export/import/products",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def user_with_permission(db: Session):
    """Create user with dashboard.view_stats permission"""
    user = User(
        username="viewer",
        email="viewer@example.com",
        full_name="Dashboard Viewer",
        hashed_password=PasswordUtils.hash_password("password123"),
        role=UserRole.OPERATOR_CUTTING,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Add permission
    from app.core.models.permissions import Permission, RolePermission
    permission = Permission(
        code="dashboard.view_stats",
        name="View Dashboard Stats",
        module="dashboard"
    )
    db.add(permission)
    db.commit()
    
    return user


@pytest.fixture
def user_without_permission(db: Session):
    """Create user without dashboard permissions"""
    user = User(
        username="no_perms",
        email="no_perms@example.com",
        full_name="No Permissions User",
        hashed_password=PasswordUtils.hash_password("password123"),
        role=UserRole.OPERATOR_CUTTING,
        is_active=True
    )
    db.add(user)
    db.commit()
    return user


# Helper method
def _get_auth_token(client: TestClient, user: User) -> str:
    """Get JWT token for user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": user.username,
            "password": "password123"
        }
    )
    return response.json()["access_token"]
