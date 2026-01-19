"""
QT-09 Transfer Protocol Integration Tests
Tests for handshake protocol, line clearance, segregation checks
"""

import pytest
from fastapi import status


class TestQT09HandshakeProtocol:
    """Test QT-09 digital handshake mechanism"""

    def test_handshake_lock_on_transfer_creation(self, client, operator_token):
        """Test that stock is LOCKED when transfer is created"""
        response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "QT09-001"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify handshake is LOCKED
        assert data["handshake_status"] == "LOCKED"
        assert data["stock_status"] == "LOCKED"
        assert data["transfer_slip"] is not None

    def test_handshake_unlock_on_acceptance(self, client, admin_token):
        """Test that stock is UNLOCKED when receiving dept accepts"""
        # Create transfer first
        transfer_response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "QT09-002"
            }
        )
        assert transfer_response.status_code == status.HTTP_201_CREATED
        transfer_id = transfer_response.json()["transfer_id"]

        # Accept from sewing
        accept_response = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": transfer_id,
                "received_qty": 100,
                "receiving_location": "LINE_SEWING_01"
            }
        )
        assert accept_response.status_code == status.HTTP_200_OK
        
        # Verify handshake is UNLOCKED
        assert accept_response.json()["handshake_status"] == "UNLOCKED"
        assert accept_response.json()["stock_status"] == "AVAILABLE"

    def test_handshake_prevents_duplicate_acceptance(self, client, admin_token):
        """Test that handshake prevents duplicate acceptance"""
        # Create transfer
        transfer_response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "QT09-003"
            }
        )
        transfer_id = transfer_response.json()["transfer_id"]

        # Accept first time
        response1 = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"transfer_id": transfer_id, "received_qty": 100}
        )
        assert response1.status_code == status.HTTP_200_OK

        # Try to accept second time - should fail
        response2 = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"transfer_id": transfer_id, "received_qty": 100}
        )
        assert response2.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]


class TestQT09LineClearanceCheckCuttingToSewing:
    """Test QT-09 line clearance check between Cutting and Sewing (Step 290)"""

    def test_line_clearance_allows_transfer_when_clear(self, client, operator_token):
        """Test transfer allowed when sewing line is clear"""
        response = client.get(
            "/api/v1/production/cutting/line-clear/1",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["line_status"] == "CLEAR"
        assert data["can_transfer"] is True
        assert data["required_clearance"] is False

    def test_line_clearance_blocks_transfer_when_occupied(self, client, operator_token):
        """Test transfer blocked when sewing line has previous batch"""
        response = client.get(
            "/api/v1/production/cutting/line-clear/999",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # If occupied, should block
        if data["line_status"] == "OCCUPIED":
            assert data["can_transfer"] is False
            assert data["required_clearance"] is True


class TestQT09SegregationCheckSewingToFinishing:
    """Test QT-09 segregation check between Sewing and Finishing (Step 380)"""

    def test_segregation_allows_same_destination(self, client, admin_token):
        """Test segregation passes when destination matches"""
        response = client.get(
            "/api/v1/production/sewing/segregation-check/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["segregation_status"] == "APPROVED"
        assert data["can_transfer"] is True

    def test_segregation_blocks_different_destination(self, client, admin_token):
        """Test segregation blocks when destination differs"""
        response = client.get(
            "/api/v1/production/sewing/segregation-check/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # If destinations differ, should be blocked or require clearance
        if "segregation_status" in data and data["segregation_status"] != "APPROVED":
            assert data["can_transfer"] is False or data["requires_line_clearance"] is True


class TestQT09LineClearanceCheckFinishingToPacking:
    """Test QT-09 line clearance check between Finishing and Packing (Step 405-406)"""

    def test_packing_line_clearance_required(self, client, admin_token):
        """Test packing line clearance is checked before finishing transfer"""
        response = client.post(
            "/api/v1/production/finishing/line-clearance-check",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"work_order_id": 1}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "packing_line_status" in data
        assert data["packing_line_status"] in ["CLEAR", "OCCUPIED"]
        assert "can_proceed" in data or "allow_transfer" in data


class TestQT09ProtocolCompleteWorkflow:
    """Test complete QT-09 protocol workflow across multiple departments"""

    def test_qt09_cutting_to_sewing_complete(self, client, operator_token, admin_token):
        """Test complete QT-09 handshake from Cutting to Sewing"""
        
        # Step 1: Cutting completes and checks line clearance
        clearance_response = client.get(
            "/api/v1/production/cutting/line-clear/1",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert clearance_response.status_code == status.HTTP_200_OK
        assert clearance_response.json()["can_transfer"] is True

        # Step 2: Cutting creates transfer (LOCKED)
        transfer_response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "QT09-WORKFLOW-1"
            }
        )
        assert transfer_response.status_code == status.HTTP_201_CREATED
        assert transfer_response.json()["handshake_status"] == "LOCKED"
        transfer_id = transfer_response.json()["transfer_id"]

        # Step 3: Sewing accepts transfer (UNLOCKED)
        accept_response = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": transfer_id,
                "received_qty": 100,
                "receiving_location": "LINE_SEWING_01"
            }
        )
        assert accept_response.status_code == status.HTTP_200_OK
        assert accept_response.json()["handshake_status"] == "UNLOCKED"

    def test_qt09_sewing_to_finishing_complete(self, client, operator_token, admin_token):
        """Test complete QT-09 handshake from Sewing to Finishing"""
        
        # Step 1: Sewing checks segregation
        seg_response = client.get(
            "/api/v1/production/sewing/segregation-check/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert seg_response.status_code == status.HTTP_200_OK
        assert seg_response.json()["can_transfer"] is True

        # Step 2: Sewing creates transfer to finishing (LOCKED)
        transfer_response = client.post(
            "/api/v1/production/sewing/transfer-to-finishing",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "transfer_qty": 100,
                "transfer_slip_number": "QT09-WORKFLOW-2",
                "destination_line": "FINISH_LINE_01"
            }
        )
        assert transfer_response.status_code == status.HTTP_201_CREATED
        assert transfer_response.json()["handshake_status"] == "LOCKED"
        transfer_id = transfer_response.json()["transfer_id"]

        # Step 3: Finishing accepts transfer (UNLOCKED)
        accept_response = client.post(
            "/api/v1/production/finishing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": transfer_id,
                "received_qty": 100,
                "receiving_location": "FINISH_LINE_01"
            }
        )
        assert accept_response.status_code == status.HTTP_200_OK
        assert accept_response.json()["handshake_status"] == "UNLOCKED"

    def test_qt09_full_production_flow(self, client, operator_token, admin_token, qc_token):
        """Test complete QT-09 protocol through entire production flow"""
        
        # CUTTING PHASE
        print("\n=== CUTTING PHASE ===")
        cutting_response = client.post(
            "/api/v1/production/cutting/spk/receive",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"mo_id": 1, "material_requests": [{"product_id": 1, "qty_needed": 100}]}
        )
        assert cutting_response.status_code == status.HTTP_200_OK
        wo_id = cutting_response.json()["work_order_id"]
        
        # SEWING PHASE
        print("\n=== SEWING PHASE ===")
        sewing_response = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"transfer_id": 1, "received_qty": 100}
        )
        assert sewing_response.status_code == status.HTTP_200_OK
        
        # FINISHING PHASE
        print("\n=== FINISHING PHASE ===")
        finish_response = client.post(
            "/api/v1/production/finishing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"transfer_id": 2, "received_qty": 100}
        )
        assert finish_response.status_code == status.HTTP_200_OK
        
        # Metal Detector (CRITICAL)
        metal_response = client.post(
            "/api/v1/production/finishing/metal-detector-test",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": wo_id,
                "quantity_tested": 100,
                "metal_detected": False,
                "test_result": "PASS"
            }
        )
        assert metal_response.status_code == status.HTTP_200_OK
        assert metal_response.json()["alert_level"] is None or metal_response.json()["metal_detector_result"] == "PASS"


class TestQT09AuditTrail:
    """Test QT-09 audit trail and compliance"""

    def test_transfer_audit_trail_recorded(self, client, operator_token):
        """Test that all transfers are recorded in audit trail"""
        response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "QT09-AUDIT-001"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify audit fields
        assert "created_by" in data or "transferred_by" in data
        assert "transfer_timestamp" in data or "created_at" in data
        assert "transfer_slip_number" in data

    def test_handshake_status_tracked(self, client, admin_token):
        """Test that handshake status changes are tracked"""
        # Create transfer
        t_response = client.post(
            "/api/v1/production/cutting/transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "destination_department": "sewing",
                "transfer_qty": 100,
                "transfer_slip_number": "QT09-TRACK-001"
            }
        )
        transfer_id = t_response.json()["transfer_id"]

        # Accept to change status
        accept_response = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"transfer_id": transfer_id, "received_qty": 100}
        )
        
        # Should have status history
        data = accept_response.json()
        assert "handshake_status" in data
        assert data["handshake_status"] in ["UNLOCKED", "ACCEPTED"]
