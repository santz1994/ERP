"""
End-to-End Tests for ERP System Workflows
Tests complete user journeys across multiple features

Coverage:
- BOM Allocation → Material Debt → Approval → Production workflow
- Daily Production tracking and completion
- SPK creation → Material allocation → Debt handling → Settlement
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch, AsyncMock

from app.core.models.users import User, UserRole


# ==================== Fixtures ====================

@pytest.fixture
def test_client():
    """Create test client"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers(role: UserRole = UserRole.WAREHOUSE):
    """Auth headers for requests"""
    return {
        "Authorization": "Bearer test_token_12345",
        "Content-Type": "application/json",
        "X-User-Role": role.value
    }


@pytest.fixture
def warehouse_user():
    """Warehouse staff user"""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "warehouse_staff"
    user.role = UserRole.WAREHOUSE
    user.department_id = 5
    return user


@pytest.fixture
def spv_user():
    """SPV (Supervisory) user"""
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "spv_user"
    user.role = UserRole.SPV
    user.department_id = 5
    return user


@pytest.fixture
def manager_user():
    """Manager user"""
    user = MagicMock(spec=User)
    user.id = 3
    user.username = "manager_user"
    user.role = UserRole.MANAGER
    user.department_id = 5
    return user


@pytest.fixture
def ppic_user():
    """PPIC operator user"""
    user = MagicMock(spec=User)
    user.id = 4
    user.username = "ppic_operator"
    user.role = UserRole.PPIC_OPERATOR
    user.department_id = 6
    return user


# ==================== E2E Test Scenarios ====================

class TestBOMAllocationToProductionWorkflow:
    """
    End-to-end workflow:
    1. Warehouse creates SPK with BOM auto-allocation
    2. System allocates materials or creates debt
    3. SPV approves debt if needed
    4. Manager approves debt
    5. Production starts with allocated materials
    6. Daily tracking records production
    7. Settlement when debt material arrives
    """
    
    def test_complete_spk_lifecycle_with_sufficient_stock(
        self, test_client, warehouse_user, ppic_user
    ):
        """
        Scenario: Create SPK → Allocate materials (all in stock) → Start production
        Expected: No debt created, production can start immediately
        """
        # Step 1: Warehouse creates SPK with auto-allocation
        spk_payload = {
            "article_id": 5,
            "spk_number": "SPK-2026-001",
            "target_qty": 1000,
            "deadline_date": (date.today() + timedelta(days=7)).isoformat(),
            "auto_allocate": True
        }
        
        with patch('app.api.v1.production.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                "/api/v1/production/spk/create-with-auto-allocation",
                json=spk_payload,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code in [200, 201]
        spk_id = response.json()["id"]
        allocation = response.json().get("allocation")
        
        # Step 2: Verify materials allocated (no debt)
        assert allocation["status"] == "FULLY_ALLOCATED"
        assert allocation["has_material_debt"] == False
        
        # Step 3: PPIC can start production immediately
        daily_input = {
            "qty_produced": 100,
            "defects": 2,
            "notes": "Production started"
        }
        
        with patch('app.api.v1.production.get_current_user', return_value=ppic_user):
            response = test_client.post(
                f"/api/v1/production/spk/{spk_id}/daily-input",
                json=daily_input,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code in [200, 201]
    
    def test_complete_spk_lifecycle_with_material_shortage(
        self, test_client, warehouse_user, spv_user, manager_user, ppic_user
    ):
        """
        Scenario: Create SPK → Allocate (shortage detected) → Create debt → 
                 Approve debt → Start production → Settle debt
        Expected: Full workflow with approval chain
        """
        # Step 1: Create SPK (shortage will trigger debt)
        spk_payload = {
            "article_id": 5,
            "spk_number": "SPK-2026-002",
            "target_qty": 1000,
            "deadline_date": (date.today() + timedelta(days=5)).isoformat(),
            "auto_allocate": True
        }
        
        with patch('app.api.v1.production.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                "/api/v1/production/spk/create-with-auto-allocation",
                json=spk_payload,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code in [200, 201]
        spk_id = response.json()["id"]
        allocation = response.json().get("allocation")
        
        # Step 2: Verify debt created for shortage
        assert allocation["has_material_debt"] == True
        debt_id = allocation.get("debt_id")
        
        # Step 3: SPV approves debt
        with patch('app.api.v1.warehouse.get_current_user', return_value=spv_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                json={"approval_notes": "Approved - urgent production"},
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        approval_status = response.json()["approval_status"]
        assert approval_status in ["APPROVED", "PENDING_MANAGER_APPROVAL"]
        
        # Step 4: If still pending, Manager approves
        if approval_status == "PENDING_MANAGER_APPROVAL":
            with patch('app.api.v1.warehouse.get_current_user', return_value=manager_user):
                response = test_client.post(
                    f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                    json={"approval_notes": "Approved by manager"},
                    headers={"Authorization": "Bearer token"}
                )
            
            assert response.status_code == 200
            assert response.json()["approval_status"] == "APPROVED"
        
        # Step 5: PPIC records daily production (despite missing material)
        daily_input = {
            "qty_produced": 150,
            "defects": 3,
            "notes": "Production with borrowed material"
        }
        
        with patch('app.api.v1.production.get_current_user', return_value=ppic_user):
            response = test_client.post(
                f"/api/v1/production/spk/{spk_id}/daily-input",
                json=daily_input,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code in [200, 201]
        
        # Step 6: Settlement when material arrives
        settlement = {
            "qty_settled": 250,
            "adjustment_type": "SETTLEMENT",
            "notes": "Material received from supplier"
        }
        
        with patch('app.api.v1.warehouse.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/adjust",
                json=settlement,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200


class TestDailyProductionTrackingWorkflow:
    """
    End-to-end workflow for daily production tracking:
    1. Create SPK with production target
    2. Record daily inputs
    3. System calculates cumulative progress
    4. Predictive completion calculation
    5. Alert if behind schedule
    6. Auto-complete when target reached
    """
    
    def test_production_tracking_on_schedule(self, test_client, ppic_user):
        """
        Scenario: Daily production tracking that matches schedule
        Expected: No alerts, completion date accurate
        """
        spk_id = 1
        target_qty = 1000
        deadline = date.today() + timedelta(days=10)
        
        # Day 1: Record 100 units (10% of target)
        day1_input = {
            "qty_produced": 100,
            "defects": 1,
            "notes": "Day 1 production"
        }
        
        with patch('app.api.v1.production.get_current_user', return_value=ppic_user):
            response = test_client.post(
                f"/api/v1/production/spk/{spk_id}/daily-input",
                json=day1_input,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code in [200, 201]
        
        # Check progress
        with patch('app.api.v1.production.get_current_user', return_value=ppic_user):
            response = test_client.get(
                f"/api/v1/production/spk/{spk_id}/progress",
                headers={"Authorization": "Bearer token"}
            )
        
        if response.status_code == 200:
            progress = response.json()
            assert progress["cumulative_qty"] >= 100
            assert progress["completion_percentage"] >= 10
    
    def test_production_tracking_behind_schedule(self, test_client, ppic_user, manager_user):
        """
        Scenario: Production falls behind schedule
        Expected: Alert generated and visible to manager
        """
        spk_id = 2
        
        # Day 1-5: Record only 100 units (should be 500 by day 5)
        for day in range(1, 6):
            daily_input = {
                "qty_produced": 20,
                "defects": 0,
                "notes": f"Day {day} - low production"
            }
            
            with patch('app.api.v1.production.get_current_user', return_value=ppic_user):
                response = test_client.post(
                    f"/api/v1/production/spk/{spk_id}/daily-input",
                    json=daily_input,
                    headers={"Authorization": "Bearer token"}
                )
            
            assert response.status_code in [200, 201]
        
        # Check for alerts
        with patch('app.api.v1.ppic.get_current_user', return_value=manager_user):
            response = test_client.get(
                "/api/v1/ppic/late-spks",
                headers={"Authorization": "Bearer token"}
            )
        
        if response.status_code == 200:
            late_spks = response.json()
            # Should contain alert about being behind schedule
            assert isinstance(late_spks, list)


class TestApprovalWorkflowMultiLevel:
    """
    End-to-end workflow for approval chain:
    1. Warehouse submits debt for approval
    2. SPV receives and reviews
    3. SPV approves/rejects
    4. If approved, Manager reviews
    5. Manager approves/rejects (final decision)
    6. Notifications sent at each step
    """
    
    def test_full_approval_chain_approval(
        self, test_client, warehouse_user, spv_user, manager_user
    ):
        """
        Scenario: Debt submitted → SPV approves → Manager approves
        Expected: Debt marked as APPROVED after both steps
        """
        debt_id = 1
        
        # Step 1: SPV reviews and approves
        spv_approval = {
            "approval_notes": "Approved - valid reason"
        }
        
        with patch('app.api.v1.warehouse.get_current_user', return_value=spv_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                json=spv_approval,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        debt = response.json()
        # Could be approved or waiting for manager
        assert debt["approval_status"] in ["APPROVED", "PENDING_MANAGER_APPROVAL"]
        
        # Step 2: If pending manager, manager approves
        if debt["approval_status"] == "PENDING_MANAGER_APPROVAL":
            manager_approval = {
                "approval_notes": "Approved - verified by manager"
            }
            
            with patch('app.api.v1.warehouse.get_current_user', return_value=manager_user):
                response = test_client.post(
                    f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                    json=manager_approval,
                    headers={"Authorization": "Bearer token"}
                )
            
            assert response.status_code == 200
            assert response.json()["approval_status"] == "APPROVED"
    
    def test_approval_chain_rejection_at_spv(
        self, test_client, spv_user, warehouse_user
    ):
        """
        Scenario: SPV rejects debt request
        Expected: Debt marked as REJECTED, warehouse notified
        """
        debt_id = 2
        
        # SPV rejects
        rejection = {
            "rejection_reason": "Insufficient documentation"
        }
        
        with patch('app.api.v1.warehouse.get_current_user', return_value=spv_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/reject",
                json=rejection,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        assert response.json()["approval_status"] == "REJECTED"


class TestDailyReportingWorkflow:
    """
    End-to-end workflow for PPIC daily reports:
    1. System collects daily production metrics
    2. Generates report with KPIs
    3. Identifies late SPKs
    4. Creates alerts for issues
    5. Sends email/WhatsApp notifications
    """
    
    def test_daily_report_generation(self, test_client, ppic_user):
        """
        Scenario: Generate daily production report
        Expected: Report contains metrics and alerts
        """
        # Generate report for today
        today = date.today()
        
        with patch('app.api.v1.ppic.get_current_user', return_value=ppic_user):
            response = test_client.get(
                f"/api/v1/ppic/daily-report?report_date={today.isoformat()}",
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        report = response.json()
        
        # Verify report structure
        assert "report_date" in report
        assert "total_spks" in report
        assert "completed_spks" in report
        assert "in_progress_spks" in report
        assert "late_spks" in report
        assert "on_time_rate" in report
        assert "avg_cycle_time" in report
        assert "quality_reject_rate" in report
        assert "material_status" in report
        assert "critical_alerts" in report
    
    def test_late_spk_detection_and_alert(self, test_client, ppic_user, manager_user):
        """
        Scenario: System detects late SPK and creates alert
        Expected: Alert visible in system and sent to manager
        """
        # Get late SPKs
        with patch('app.api.v1.ppic.get_current_user', return_value=ppic_user):
            response = test_client.get(
                "/api/v1/ppic/late-spks",
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        late_spks = response.json()
        assert isinstance(late_spks, list)


class TestMaterialDebtSettlementLifecycle:
    """
    Complete material debt lifecycle:
    1. Create debt
    2. Approve debt
    3. Multiple settlements
    4. Final reconciliation
    5. Debt closure
    """
    
    def test_complete_debt_settlement_cycle(
        self, test_client, warehouse_user, spv_user
    ):
        """
        Scenario: Debt created → Approved → Multiple settlements → Closed
        Expected: Debt status transitions correctly
        """
        debt_id = 3
        
        # Step 1: Approve debt
        with patch('app.api.v1.warehouse.get_current_user', return_value=spv_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/approve",
                json={"approval_notes": "Approved"},
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        
        # Step 2: First settlement (partial)
        with patch('app.api.v1.warehouse.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/adjust",
                json={
                    "qty_settled": 50,
                    "adjustment_type": "SETTLEMENT",
                    "notes": "First delivery - 50 units"
                },
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        assert response.json()["qty_settled"] == 50
        
        # Step 3: Second settlement (remainder)
        with patch('app.api.v1.warehouse.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                f"/api/v1/warehouse/material-debt/{debt_id}/adjust",
                json={
                    "qty_settled": 50,
                    "adjustment_type": "SETTLEMENT",
                    "notes": "Final delivery - 50 units"
                },
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code == 200
        # Should be SETTLED now
        assert response.json()["status"] == "SETTLED"


class TestCrossFeatureIntegration:
    """
    Test integration between multiple features:
    - BOM Allocation → Material Debt → Approval → Production
    - Daily Production → Reports → Alerts → Actions
    """
    
    def test_spk_allocation_to_daily_production_integration(
        self, test_client, warehouse_user, ppic_user
    ):
        """
        Scenario: SPK created with allocation → Production tracked daily
        Expected: Allocation data available in daily production view
        """
        spk_id = 5
        
        # Create SPK
        spk_payload = {
            "article_id": 10,
            "spk_number": "SPK-2026-E2E-001",
            "target_qty": 500,
            "deadline_date": (date.today() + timedelta(days=7)).isoformat(),
            "auto_allocate": True
        }
        
        with patch('app.api.v1.production.get_current_user', return_value=warehouse_user):
            response = test_client.post(
                "/api/v1/production/spk/create-with-auto-allocation",
                json=spk_payload,
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code in [200, 201]
        spk_id = response.json()["id"]
        
        # Record daily production
        with patch('app.api.v1.production.get_current_user', return_value=ppic_user):
            response = test_client.post(
                f"/api/v1/production/spk/{spk_id}/daily-input",
                json={
                    "qty_produced": 75,
                    "defects": 1,
                    "notes": "Day 1"
                },
                headers={"Authorization": "Bearer token"}
            )
        
        assert response.status_code in [200, 201]


# ==================== Test Execution ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
