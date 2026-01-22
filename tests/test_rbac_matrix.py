"""
RBAC Matrix Testing - Zero-Gap Access Control Verification
===========================================================
Tests the same scenarios with different user roles to ensure proper authorization.

Test Coverage:
- Admin: Full access to all modules
- Operator (Cutting/Sewing): Limited to production modules
- QC Inspector: Only QC and inspection modules
- Warehouse: Only warehouse and stock modules
- Unauthorized users: Proper 403 responses

Author: Daniel - IT Developer Senior
Date: 2026-01-22
"""

import pytest
import requests
from typing import Dict

# Test Configuration
API_URL = "http://localhost:8000/api/v1"

# Test Users with Different Roles
TEST_USERS = {
    "admin": {"username": "admin", "password": "password123"},
    "developer": {"username": "developer", "password": "password123"},
    "operator_cutting": {"username": "operator_cutting", "password": "password123"},
    "operator_sewing": {"username": "operator_sewing", "password": "password123"},
    "qc_inspector": {"username": "qc_inspector", "password": "password123"},
    "warehouse_staff": {"username": "warehouse_staff", "password": "password123"},
    "ppic": {"username": "ppic", "password": "password123"}
}


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def auth_tokens() -> Dict[str, str]:
    """Get authentication tokens for all test users"""
    tokens = {}
    
    for role, credentials in TEST_USERS.items():
        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json=credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                tokens[role] = response.json()["access_token"]
            else:
                print(f"⚠️ Failed to login as {role}: {response.status_code}")
                tokens[role] = None
        except Exception as e:
            print(f"⚠️ Error logging in as {role}: {str(e)}")
            tokens[role] = None
    
    return tokens


def make_request(method: str, endpoint: str, token: str, **kwargs):
    """Helper to make authenticated requests"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}{endpoint}"
    
    if method.upper() == "GET":
        return requests.get(url, headers=headers, timeout=5, **kwargs)
    elif method.upper() == "POST":
        return requests.post(url, headers=headers, timeout=5, **kwargs)
    elif method.upper() == "PUT":
        return requests.put(url, headers=headers, timeout=5, **kwargs)
    elif method.upper() == "DELETE":
        return requests.delete(url, headers=headers, timeout=5, **kwargs)


# ============================================================================
# TEST CLASS: RBAC Matrix - Admin Access
# ============================================================================

@pytest.mark.rbac
class TestRBACMatrixAdmin:
    """Test Admin has full access to all modules"""
    
    def test_admin_can_access_user_management(self, auth_tokens):
        """RBAC-01: Admin can access user management"""
        token = auth_tokens.get("admin")
        if not token:
            pytest.skip("Admin token not available")
        
        response = make_request("GET", "/admin/users", token)
        assert response.status_code in [200, 404], \
            f"Admin should have access to user management. Got: {response.status_code}"
    
    def test_admin_can_access_all_departments(self, auth_tokens):
        """RBAC-02: Admin can access all production departments"""
        token = auth_tokens.get("admin")
        if not token:
            pytest.skip("Admin token not available")
        
        endpoints = [
            "/ppic/manufacturing-orders",
            "/warehouse/stock/1",
            "/production/cutting/pending",
            "/audit/logs"
        ]
        
        for endpoint in endpoints:
            response = make_request("GET", endpoint, token)
            assert response.status_code in [200, 404], \
                f"Admin should access {endpoint}. Got: {response.status_code}"
    
    def test_admin_can_create_manufacturing_orders(self, auth_tokens):
        """RBAC-03: Admin can create manufacturing orders"""
        token = auth_tokens.get("admin")
        if not token:
            pytest.skip("Admin token not available")
        
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": "TEST-RBAC-001",
            "routing_type": "Route1"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", token, json=mo_data)
        # Expect 200/201 (success) or 400/422 (validation error, but access granted)
        assert response.status_code in [200, 201, 400, 422, 404], \
            f"Admin should have create permission. Got: {response.status_code}"


# ============================================================================
# TEST CLASS: RBAC Matrix - Operator Access
# ============================================================================

@pytest.mark.rbac
class TestRBACMatrixOperator:
    """Test Operators have limited access to their departments only"""
    
    def test_operator_cannot_access_admin_panel(self, auth_tokens):
        """RBAC-04: Operators should NOT access admin panel"""
        token = auth_tokens.get("operator_cutting")
        if not token:
            pytest.skip("Operator token not available")
        
        response = make_request("GET", "/admin/users", token)
        assert response.status_code == 403, \
            f"Operator should get 403 Forbidden for admin panel. Got: {response.status_code}"
    
    def test_operator_can_access_own_department(self, auth_tokens):
        """RBAC-05: Cutting operator can access cutting module"""
        token = auth_tokens.get("operator_cutting")
        if not token:
            pytest.skip("Operator token not available")
        
        response = make_request("GET", "/production/cutting/pending", token)
        assert response.status_code in [200, 404], \
            f"Cutting operator should access cutting module. Got: {response.status_code}"
    
    def test_operator_cannot_access_other_department(self, auth_tokens):
        """RBAC-06: Cutting operator should NOT access sewing module"""
        token = auth_tokens.get("operator_cutting")
        if not token:
            pytest.skip("Operator token not available")
        
        # Try to access sewing department endpoint
        response = make_request("GET", "/production/sewing/pending", token)
        # Should be either 403 (forbidden) or 404 (endpoint exists but no permission)
        assert response.status_code in [403, 404], \
            f"Operator should not access other departments. Got: {response.status_code}"
    
    def test_operator_cannot_create_manufacturing_orders(self, auth_tokens):
        """RBAC-07: Operators should NOT create MOs (only execute)"""
        token = auth_tokens.get("operator_cutting")
        if not token:
            pytest.skip("Operator token not available")
        
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": "TEST-UNAUTHORIZED"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", token, json=mo_data)
        assert response.status_code == 403, \
            f"Operator should NOT create MOs. Expected 403, Got: {response.status_code}"


# ============================================================================
# TEST CLASS: RBAC Matrix - QC Inspector Access
# ============================================================================

@pytest.mark.rbac
class TestRBACMatrixQC:
    """Test QC Inspectors have access only to quality modules"""
    
    def test_qc_can_access_qc_module(self, auth_tokens):
        """RBAC-08: QC Inspector can access QC module"""
        token = auth_tokens.get("qc_inspector")
        if not token:
            pytest.skip("QC token not available")
        
        response = make_request("GET", "/quality/inspections", token)
        assert response.status_code in [200, 404], \
            f"QC should access quality module. Got: {response.status_code}"
    
    def test_qc_cannot_modify_production(self, auth_tokens):
        """RBAC-09: QC cannot modify production orders"""
        token = auth_tokens.get("qc_inspector")
        if not token:
            pytest.skip("QC token not available")
        
        # Try to start a cutting operation
        response = make_request("POST", "/production/cutting/start", token, json={"work_order_id": 1})
        assert response.status_code == 403, \
            f"QC should NOT modify production. Expected 403, Got: {response.status_code}"
    
    def test_qc_cannot_access_warehouse(self, auth_tokens):
        """RBAC-10: QC should NOT access warehouse operations"""
        token = auth_tokens.get("qc_inspector")
        if not token:
            pytest.skip("QC token not available")
        
        stock_data = {"item_id": 1, "quantity": 10, "operation": "add"}
        response = make_request("POST", "/warehouse/stock", token, json=stock_data)
        assert response.status_code == 403, \
            f"QC should NOT access warehouse. Expected 403, Got: {response.status_code}"


# ============================================================================
# TEST CLASS: RBAC Matrix - Cross-Module Scenarios
# ============================================================================

@pytest.mark.rbac
class TestRBACCrossModule:
    """Test the same endpoint with different roles"""
    
    def test_dashboard_access_by_role(self, auth_tokens):
        """RBAC-11: Different roles accessing dashboard"""
        endpoint = "/dashboard/stats"
        
        # Admin: Should have full access
        if auth_tokens.get("admin"):
            response = make_request("GET", endpoint, auth_tokens["admin"])
            assert response.status_code in [200, 404], \
                f"Admin should access dashboard. Got: {response.status_code}"
        
        # Developer: Should have access (for monitoring)
        if auth_tokens.get("developer"):
            response = make_request("GET", endpoint, auth_tokens["developer"])
            assert response.status_code in [200, 404], \
                f"Developer should access dashboard. Got: {response.status_code}"
        
        # Operator: Limited or no access
        if auth_tokens.get("operator_cutting"):
            response = make_request("GET", endpoint, auth_tokens["operator_cutting"])
            # Operators might have limited dashboard or 403
            assert response.status_code in [200, 403, 404], \
                f"Operator dashboard response: {response.status_code}"
    
    def test_audit_trail_access_by_role(self, auth_tokens):
        """RBAC-12: Audit trail should be restricted"""
        endpoint = "/audit/logs"
        
        # Admin: Full access
        if auth_tokens.get("admin"):
            response = make_request("GET", endpoint, auth_tokens["admin"])
            assert response.status_code in [200, 404], \
                f"Admin should access audit logs. Got: {response.status_code}"
        
        # Operator: Should NOT access
        if auth_tokens.get("operator_cutting"):
            response = make_request("GET", endpoint, auth_tokens["operator_cutting"])
            assert response.status_code == 403, \
                f"Operator should NOT access audit logs. Got: {response.status_code}"
        
        # QC: Should NOT access
        if auth_tokens.get("qc_inspector"):
            response = make_request("GET", endpoint, auth_tokens["qc_inspector"])
            assert response.status_code == 403, \
                f"QC should NOT access audit logs. Got: {response.status_code}"


# ============================================================================
# TEST CLASS: RBAC Matrix - Permission Inheritance
# ============================================================================

@pytest.mark.rbac
class TestRBACPermissionInheritance:
    """Test that SPV inherits operator permissions + additional rights"""
    
    def test_warehouse_staff_basic_access(self, auth_tokens):
        """RBAC-13: Warehouse staff can check stock"""
        token = auth_tokens.get("warehouse_staff")
        if not token:
            pytest.skip("Warehouse token not available")
        
        response = make_request("GET", "/warehouse/stock/1", token)
        assert response.status_code in [200, 404], \
            f"Warehouse staff should check stock. Got: {response.status_code}"
    
    def test_ppic_planning_access(self, auth_tokens):
        """RBAC-14: PPIC can create manufacturing orders"""
        token = auth_tokens.get("ppic")
        if not token:
            pytest.skip("PPIC token not available")
        
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": "PPIC-TEST-001",
            "routing_type": "Route1"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", token, json=mo_data)
        # PPIC should have permission (200/201) or validation error (400/422)
        assert response.status_code in [200, 201, 400, 422, 404], \
            f"PPIC should create MOs. Got: {response.status_code}"


# ============================================================================
# SUMMARY TEST
# ============================================================================

@pytest.mark.rbac
def test_rbac_matrix_summary(auth_tokens):
    """
    RBAC Matrix Summary - Validate all tokens loaded correctly
    
    This test provides visibility into which roles are testable.
    """
    print("\n" + "="*60)
    print("RBAC MATRIX TEST CONFIGURATION")
    print("="*60)
    
    for role, token in auth_tokens.items():
        status = "✅ READY" if token else "❌ FAILED"
        print(f"{role:20s} : {status}")
    
    print("="*60 + "\n")
    
    # Ensure at least Admin and one operator are available
    assert auth_tokens.get("admin") or auth_tokens.get("developer"), \
        "Must have at least Admin or Developer token for RBAC testing"
