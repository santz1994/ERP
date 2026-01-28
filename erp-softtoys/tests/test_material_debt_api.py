"""
Integration Tests for Material Debt API Endpoints
Tests the full request/response cycle for Material Debt Feature #4

Coverage:
- Endpoint routing and request handling
- Request validation
- Response schemas
- Permission checks
- Full workflow: create → approve → adjust → settle
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch, AsyncMock

from app.core.models.users import User
from app.core.models.daily_production import MaterialDebt


# ==================== Fixtures ====================

@pytest.fixture
def test_client():
    """Create test client"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Auth headers for requests"""
    return {
        "Authorization": "Bearer test_token_12345",
        "Content-Type": "application/json"
    }


@pytest.fixture
def warehouse_user():
    """Warehouse role user"""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "warehouse_user"
    user.role = UserRole.WAREHOUSE
    user.department_id = 5
    return user


@pytest.fixture
def spv_user():
    """SPV role user"""
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "spv_user"
    user.role = UserRole.SPV
    user.department_id = 5
    return user


@pytest.fixture
def manager_user():
    """Manager role user"""
    user = MagicMock(spec=User)
    user.id = 3
    user.username = "manager_user"
    user.role = UserRole.MANAGER
    user.department_id = 5
    return user


# ==================== Test Cases ====================

class TestMaterialDebtEndpoints:
    """Test Material Debt API endpoints"""
    
    def test_create_debt_endpoint_success(self, test_client, auth_headers, warehouse_user):
        """POST /material-debt/create should create debt"""
        # Arrange
        payload = {
            "spk_id": 1,
            "material_id": 101,
            "qty_debt": 50,
            "unit_price": 10000,
            "notes": "Insufficient stock for production"
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            # Act
            response = test_client.post(
                "/api/v1/warehouse/material-debt/create",
                json=payload,
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 201
        assert response.json()["status"] == "PENDING_APPROVAL"
    
    def test_create_debt_requires_auth(self, test_client):
        """POST /material-debt/create should require authentication"""
        # Arrange
        payload = {
            "spk_id": 1,
            "material_id": 101,
            "qty_debt": 50,
            "unit_price": 10000,
            "notes": "Test"
        }
        
        # Act
        response = test_client.post(
            "/api/v1/warehouse/material-debt/create",
            json=payload
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_create_debt_validation_missing_field(self, test_client, auth_headers, warehouse_user):
        """POST /material-debt/create should validate required fields"""
        # Arrange
        payload = {
            "spk_id": 1,
            # missing material_id
            "qty_debt": 50,
            "unit_price": 10000
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            # Act
            response = test_client.post(
                "/api/v1/warehouse/material-debt/create",
                json=payload,
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 422
    
    def test_create_debt_validation_invalid_qty(self, test_client, auth_headers, warehouse_user):
        """POST /material-debt/create should reject zero/negative qty"""
        # Arrange
        payload = {
            "spk_id": 1,
            "material_id": 101,
            "qty_debt": 0,  # Invalid
            "unit_price": 10000,
            "notes": "Test"
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            # Act
            response = test_client.post(
                "/api/v1/warehouse/material-debt/create",
                json=payload,
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code in [400, 422]
    
    def test_approve_debt_endpoint_success(self, test_client, auth_headers, spv_user):
        """POST /material-debt/{id}/approve should approve debt"""
        # Arrange
        debt_id = 1
        payload = {
            "approval_notes": "Approved for SPK-001"
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=spv_user):
            # Act
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                json=payload,
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["approval_status"] == "APPROVED"
    
    def test_approve_debt_requires_spv_role(self, test_client, auth_headers, warehouse_user):
        """POST /material-debt/{id}/approve should require SPV/Manager role"""
        # Arrange
        debt_id = 1
        payload = {"approval_notes": "Test"}
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            # Act
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                json=payload,
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 403
    
    def test_reject_debt_endpoint_success(self, test_client, auth_headers, spv_user):
        """POST /material-debt/{id}/reject should reject debt"""
        # Arrange
        debt_id = 1
        payload = {
            "rejection_reason": "Insufficient justification"
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=spv_user):
            # Act
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/reject",
                json=payload,
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["approval_status"] == "REJECTED"
    
    def test_adjust_debt_endpoint_success(self, test_client, auth_headers, warehouse_user):
        """POST /material-debt/{id}/adjust should record settlement"""
        # Arrange
        debt_id = 1
        payload = {
            "qty_settled": 30,
            "adjustment_type": "SETTLEMENT",
            "notes": "Received 30 units on delivery"
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            # Act
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/adjust",
                json=payload,
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["status"] in ["APPROVED", "SETTLED"]
    
    def test_get_debt_endpoint_success(self, test_client, auth_headers, warehouse_user):
        """GET /material-debt/{id} should return debt details"""
        # Arrange
        debt_id = 1
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            # Act
            response = test_client.get(
                f"/api/v1/warehouse/material-debt/{debt_id}",
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "spk_id" in data
        assert "status" in data
        assert "approval_status" in data
    
    def test_get_outstanding_debts_endpoint_success(self, test_client, auth_headers, warehouse_user):
        """GET /material-debt/outstanding should list outstanding debts"""
        # Arrange
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            # Act
            response = test_client.get(
                "/api/v1/warehouse/material-debt/outstanding",
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert all("status" in item for item in data)
    
    def test_check_threshold_endpoint_success(self, test_client, auth_headers, manager_user):
        """GET /material-debt/check-threshold should check PO blocking"""
        # Arrange
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=manager_user):
            # Act
            response = test_client.get(
                "/api/v1/warehouse/material-debt/check-threshold",
                headers=auth_headers
            )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "is_blocked" in data
        assert "total_outstanding" in data


class TestMaterialDebtWorkflow:
    """Test complete Material Debt workflow"""
    
    def test_complete_workflow_create_approve_settle(self, test_client, auth_headers, warehouse_user, spv_user):
        """Test complete workflow: Create → Approve → Adjust → Settle"""
        
        # Step 1: Create debt (Warehouse creates)
        payload = {
            "spk_id": 1,
            "material_id": 101,
            "qty_debt": 100,
            "unit_price": 10000,
            "notes": "Production start before material arrival"
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                "/api/v1/warehouse/material-debt/create",
                json=payload,
                headers=auth_headers
            )
        
        assert response.status_code == 201
        debt_id = response.json()["id"]
        assert response.json()["status"] == "PENDING_APPROVAL"
        
        # Step 2: Approve debt (SPV approves)
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=spv_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                json={"approval_notes": "Approved - urgent production"},
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert response.json()["approval_status"] == "APPROVED"
        
        # Step 3: Record first settlement (30/100 units received)
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/adjust",
                json={
                    "qty_settled": 30,
                    "adjustment_type": "SETTLEMENT",
                    "notes": "First delivery - 30 units"
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert response.json()["qty_settled"] == 30
        
        # Step 4: Record second settlement (remaining 70 units)
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/adjust",
                json={
                    "qty_settled": 70,
                    "adjustment_type": "SETTLEMENT",
                    "notes": "Final delivery - 70 units"
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert response.json()["status"] == "SETTLED"
    
    def test_workflow_rejection_path(self, test_client, auth_headers, warehouse_user, spv_user):
        """Test workflow rejection path"""
        
        # Create debt
        payload = {
            "spk_id": 2,
            "material_id": 102,
            "qty_debt": 50,
            "unit_price": 5000,
            "notes": "Test rejection"
        }
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                "/api/v1/warehouse/material-debt/create",
                json=payload,
                headers=auth_headers
            )
        
        debt_id = response.json()["id"]
        
        # Reject debt
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=spv_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/reject",
                json={"rejection_reason": "Invalid SPK reference"},
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert response.json()["approval_status"] == "REJECTED"


class TestMaterialDebtFiltering:
    """Test debt filtering and search"""
    
    def test_get_debts_filter_by_status(self, test_client, auth_headers, warehouse_user):
        """GET /material-debt/outstanding should filter by status"""
        # This test verifies query parameter handling
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.get(
                "/api/v1/warehouse/material-debt/outstanding?status=PENDING_APPROVAL",
                headers=auth_headers
            )
        
        assert response.status_code == 200
    
    def test_get_debts_filter_by_department(self, test_client, auth_headers, warehouse_user):
        """GET /material-debt/outstanding should filter by department"""
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.get(
                "/api/v1/warehouse/material-debt/outstanding?department_id=5",
                headers=auth_headers
            )
        
        assert response.status_code == 200
    
    def test_get_debts_filter_by_spk(self, test_client, auth_headers, warehouse_user):
        """GET /material-debt/outstanding should filter by SPK"""
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.get(
                "/api/v1/warehouse/material-debt/outstanding?spk_id=1",
                headers=auth_headers
            )
        
        assert response.status_code == 200


class TestMaterialDebtPagination:
    """Test debt list pagination"""
    
    def test_outstanding_debts_pagination_limit(self, test_client, auth_headers, warehouse_user):
        """GET /material-debt/outstanding should support limit parameter"""
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.get(
                "/api/v1/warehouse/material-debt/outstanding?limit=10",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert len(response.json()) <= 10
    
    def test_outstanding_debts_pagination_offset(self, test_client, auth_headers, warehouse_user):
        """GET /material-debt/outstanding should support offset parameter"""
        
        with patch('app.api.v1.warehouse.material_debt.get_current_user', return_value=warehouse_user):
            response = test_client.get(
                "/api/v1/warehouse/material-debt/outstanding?offset=0&limit=5",
                headers=auth_headers
            )
        
        assert response.status_code == 200


# ==================== Test Execution ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
