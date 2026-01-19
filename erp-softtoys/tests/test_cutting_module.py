"""
Cutting Module Test Suite
Tests for Steps 200-293 of cutting process workflow
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, WorkOrderStatus
from app.core.models.products import Product, ProductType
from app.core.models.transfer import TransferLog, LineOccupancy, LineStatus
from app.core.models.warehouse import StockMove


class TestCuttingReceiveSPK:
    """Test receive SPK and allocate material (Step 200)"""

    def test_receive_spk_success(self, client, db: Session, admin_token, sample_product):
        """Test successful SPK receipt and material allocation"""
        response = client.post(
            "/api/v1/production/cutting/spk/receive",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "mo_id": 1,
                "material_requests": [
                    {"product_id": sample_product.id, "qty_needed": 100}
                ]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "work_order_id" in data
        assert data["status"] == "Material Allocated"

    def test_receive_spk_insufficient_stock(self, client, admin_token):
        """Test SPK receipt with insufficient stock"""
        response = client.post(
            "/api/v1/production/cutting/spk/receive",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "mo_id": 999,
                "material_requests": [{"product_id": 999, "qty_needed": 10000}]
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "insufficient stock" in response.json()["detail"].lower()

    def test_receive_spk_unauthorized(self, client):
        """Test SPK receipt without authorization"""
        response = client.post(
            "/api/v1/production/cutting/spk/receive",
            json={"mo_id": 1, "material_requests": []}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCuttingCompletion:
    """Test cutting operation completion (Step 220)"""

    def test_complete_cutting_success(self, client, db: Session, operator_token):
        """Test successful cutting completion"""
        response = client.post(
            "/api/v1/production/cutting/complete",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "output_qty": 100,
                "reject_qty": 2
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["output_qty"] == 100
        assert data["reject_qty"] == 2
        assert data["status"] in ["Complete", "Shortage", "Surplus"]

    def test_complete_cutting_shortage(self, client, operator_token):
        """Test cutting with shortage output"""
        response = client.post(
            "/api/v1/production/cutting/complete",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "output_qty": 75,  # Less than planned
                "reject_qty": 5
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "shortage_qty" in data or data["status"] == "Shortage"

    def test_complete_cutting_surplus(self, client, operator_token):
        """Test cutting with surplus output"""
        response = client.post(
            "/api/v1/production/cutting/complete",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "output_qty": 120,  # More than planned
                "reject_qty": 0
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] in ["Surplus", "Complete"]


class TestShortageHandling:
    """Test shortage handling logic (Steps 230-250)"""

    def test_shortage_escalation_request(self, client, supervisor_token):
        """Test shortage escalation request"""
        response = client.post(
            "/api/v1/production/cutting/shortage/handle",
            headers={"Authorization": f"Bearer {supervisor_token}"},
            json={
                "work_order_id": 1,
                "shortage_qty": 25,
                "reason": "Material defect in roll",
                "request_type": "additional_material"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Approval Pending"
        assert "request_id" in data

    def test_shortage_escalation_approval(self, client, admin_token):
        """Test shortage escalation approval"""
        response = client.post(
            "/api/v1/production/cutting/shortage/handle",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "request_id": 1,
                "action": "approve",
                "additional_material_qty": 30
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Approved"

    def test_shortage_escalation_rejection(self, client, admin_token):
        """Test shortage escalation rejection"""
        response = client.post(
            "/api/v1/production/cutting/shortage/handle",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "request_id": 1,
                "action": "reject",
                "reason": "Not justified"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Rejected"


class TestLineCleananceCheck:
    """Test line clearance check (Step 290) - QT-09 Protocol"""

    def test_line_clearance_allowed(self, client, db: Session, operator_token):
        """Test line clearance when sewing line is empty"""
        # Set sewing line to CLEAR
        response = client.get(
            "/api/v1/production/cutting/line-clear/1",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["line_status"] == "CLEAR"
        assert data["can_transfer"] is True

    def test_line_clearance_blocked(self, client, db: Session, operator_token):
        """Test line clearance when sewing line is occupied"""
        # Mock sewing line as OCCUPIED
        response = client.get(
            "/api/v1/production/cutting/line-clear/999",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        # Should return error or blocked status
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["can_transfer"] is False


class TestTransferHandshake:
    """Test digital handshake for transfer (Steps 291-293) - QT-09 Protocol"""

    def test_transfer_with_handshake_lock(self, client, operator_token):
        """Test transfer creation with handshake lock"""
        response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "TSLD-001"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["handshake_status"] == "LOCKED"
        assert data["transfer_slip"] is not None

    def test_transfer_acceptance_unlocks(self, client, db: Session, admin_token):
        """Test that transfer acceptance unlocks the handshake"""
        # First create transfer
        transfer_response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "TSLD-002"
            }
        )
        transfer_id = transfer_response.json()["transfer_id"]

        # Accept transfer from sewing side
        response = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"transfer_id": transfer_id, "received_qty": 100}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["handshake_status"] == "UNLOCKED"


class TestCuttingEndtoEnd:
    """End-to-end cutting process workflow"""

    def test_cutting_workflow_success(self, client, operator_token, admin_token):
        """Test complete cutting workflow from SPK to transfer"""
        # Step 1: Receive SPK
        response1 = client.post(
            "/api/v1/production/cutting/spk/receive",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "mo_id": 1,
                "material_requests": [{"product_id": 1, "qty_needed": 100}]
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        wo_id = response1.json()["work_order_id"]

        # Step 2: Complete cutting
        response2 = client.post(
            "/api/v1/production/cutting/complete",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={"work_order_id": wo_id, "output_qty": 100, "reject_qty": 2}
        )
        assert response2.status_code == status.HTTP_200_OK

        # Step 3: Check line clearance
        response3 = client.get(
            f"/api/v1/production/cutting/line-clear/{wo_id}",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response3.status_code == status.HTTP_200_OK
        assert response3.json()["can_transfer"] is True

        # Step 4: Transfer to sewing
        response4 = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": wo_id,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "TSLD-E2E"
            }
        )
        assert response4.status_code == status.HTTP_201_CREATED
        assert response4.json()["handshake_status"] == "LOCKED"

    def test_cutting_with_shortage_workflow(self, client, operator_token, supervisor_token, admin_token):
        """Test cutting workflow including shortage handling"""
        # Receive SPK
        response1 = client.post(
            "/api/v1/production/cutting/spk/receive",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"mo_id": 2, "material_requests": [{"product_id": 1, "qty_needed": 100}]}
        )
        wo_id = response1.json()["work_order_id"]

        # Complete with shortage
        response2 = client.post(
            "/api/v1/production/cutting/complete",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={"work_order_id": wo_id, "output_qty": 75, "reject_qty": 5}
        )
        assert response2.status_code == status.HTTP_200_OK

        # Request shortage handling
        response3 = client.post(
            "/api/v1/production/cutting/shortage/handle",
            headers={"Authorization": f"Bearer {supervisor_token}"},
            json={
                "work_order_id": wo_id,
                "shortage_qty": 25,
                "reason": "Material quality issue"
            }
        )
        assert response3.status_code == status.HTTP_200_OK
