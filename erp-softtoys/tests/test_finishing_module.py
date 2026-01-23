"""
Finishing Module Test Suite
Tests for Steps 400-450 of finishing process workflow
"""

from fastapi import status


class TestFinishingAcceptWIP:
    """Test accept WIP transfer (Step 400)"""

    def test_accept_wip_success(self, client, admin_token):
        """Test successful WIP acceptance"""
        response = client.post(
            "/api/v1/production/finishing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": 1,
                "received_qty": 100,
                "receiving_location": "FINISH_LINE_01"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["handshake_status"] == "UNLOCKED"
        assert data["status"] == "Accepted"

    def test_accept_wip_qty_discrepancy(self, client, admin_token):
        """Test WIP acceptance with quantity discrepancy"""
        response = client.post(
            "/api/v1/production/finishing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": 1,
                "received_qty": 98,  # 2 pcs missing
                "discrepancy_reason": "Lost during transfer",
                "receiving_location": "FINISH_LINE_01"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "discrepancy" in data or "qty_variance" in data


class TestLineCleananceCheckPacking:
    """Test line clearance check for packing (Steps 405-406)"""

    def test_packing_line_clear_allowed(self, client, admin_token):
        """Test transfer allowed when packing line is clear"""
        response = client.post(
            "/api/v1/production/finishing/line-clearance-check",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"work_order_id": 1}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["packing_line_status"] == "CLEAR"
        assert data["can_proceed"] is True

    def test_packing_line_blocked(self, client, admin_token):
        """Test transfer blocked when packing line is occupied"""
        response = client.post(
            "/api/v1/production/finishing/line-clearance-check",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"work_order_id": 999}  # Line with previous batch still running
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["can_proceed"] is False or data["packing_line_status"] == "OCCUPIED"


class TestStuffingProcess:
    """Test stuffing operation (Step 410)"""

    def test_stuffing_success(self, client, operator_token):
        """Test successful stuffing operation"""
        response = client.post(
            "/api/v1/production/finishing/stuffing",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_stuffed": 100,
                "dacron_weight_kg": 5.2,
                "operator_notes": "Stuffing distributed evenly"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Stuffed"
        assert data["quantity_stuffed"] == 100

    def test_stuffing_qty_mismatch(self, client, operator_token):
        """Test stuffing with quantity mismatch"""
        response = client.post(
            "/api/v1/production/finishing/stuffing",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_stuffed": 98,  # Less than received
                "dacron_weight_kg": 5.1,
                "discrepancy_reason": "2 units lost during process"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        if "discrepancy" in data:
            assert data["quantity_stuffed"] == 98


class TestClosingGrooming:
    """Test closing and grooming (Step 420)"""

    def test_closing_grooming_success(self, client, operator_token):
        """Test successful closing and grooming"""
        response = client.post(
            "/api/v1/production/finishing/closing-grooming",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_closed": 100,
                "seam_quality": "excellent",
                "grooming_notes": "All seams closed and groomed"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Closed and Groomed"
        assert data["quantity_closed"] == 100


class TestMetalDetectorQC:
    """Test CRITICAL metal detector quality check (Step 430-435)"""

    def test_metal_detector_pass(self, client, qc_token):
        """Test metal detector pass"""
        response = client.post(
            "/api/v1/production/finishing/metal-detector-test",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": 1,
                "quantity_tested": 100,
                "test_standard": "ISO_8124_4B",
                "metal_detected": False,
                "test_result": "PASS"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["metal_detector_result"] == "PASS"
        assert data["quantity_passed"] == 100
        assert data["alert_level"] is None

    def test_metal_detector_fail_alert(self, client, qc_token):
        """Test metal detector fail triggers CRITICAL alert"""
        response = client.post(
            "/api/v1/production/finishing/metal-detector-test",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": 1,
                "quantity_tested": 100,
                "test_standard": "ISO_8124_4B",
                "metal_detected": True,
                "metal_location": "Head area",
                "metal_type": "Steel needle fragment",
                "test_result": "FAIL"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["metal_detector_result"] == "FAIL"
        assert data["alert_level"] == "CRITICAL"
        assert data["status"] == "ALERT_TRIGGERED"
        assert "stop_production" in data or data["production_status"] == "STOPPED"

    def test_metal_detector_partial_fail(self, client, qc_token):
        """Test metal detector with partial failure"""
        response = client.post(
            "/api/v1/production/finishing/metal-detector-test",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": 1,
                "quantity_tested": 100,
                "units_with_metal": 3,
                "metal_detected": True,
                "test_result": "PARTIAL"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity_passed"] == 97
        assert data["units_with_metal"] == 3


class TestPhysicalQCCheck:
    """Test physical QC inspection"""

    def test_physical_qc_pass(self, client, qc_token):
        """Test physical QC pass"""
        response = client.post(
            "/api/v1/production/finishing/physical-qc-check",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": 1,
                "quantity_inspected": 100,
                "visual_inspection": "excellent",
                "symmetry_check": "approved",
                "dimension_check": "within_spec",
                "result": "PASS"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["physical_qc_status"] == "PASS"


class TestConversionToFG:
    """Test WIP to FG conversion (Step 450)"""

    def test_conversion_success(self, client, admin_token):
        """Test successful WIP to FG conversion"""
        response = client.post(
            "/api/v1/production/finishing/convert-to-fg",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "quantity_converted": 100,
                "wip_code": "WIP-FIN-SHARK-01",
                "fg_code": "BLAHAJ-100"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversion_status"] == "SUCCESS"
        assert data["fg_code"] == "BLAHAJ-100"
        assert data["quantity_fg"] == 100

    def test_conversion_invalid_destination(self, client, admin_token):
        """Test conversion with invalid destination code"""
        response = client.post(
            "/api/v1/production/finishing/convert-to-fg",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "quantity_converted": 100,
                "wip_code": "WIP-FIN-SHARK-01",
                "fg_code": "INVALID-CODE"
            }
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestFinishingStatusEndpoints:
    """Test status and pending work order endpoints"""

    def test_get_finishing_status(self, client, operator_token):
        """Test get finishing work order status"""
        response = client.get(
            "/api/v1/production/finishing/status/1",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "work_order_id" in data
        assert "status" in data

    def test_get_pending_finishing(self, client, operator_token):
        """Test get pending finishing work orders"""
        response = client.get(
            "/api/v1/production/finishing/pending",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list) or "work_orders" in data


class TestFinishingEndtoEnd:
    """End-to-end finishing process workflow"""

    def test_finishing_workflow_critical_qc(self, client, admin_token, operator_token, qc_token):
        """Test complete finishing workflow with metal detector"""
        # Accept WIP
        response1 = client.post(
            "/api/v1/production/finishing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": 1,
                "received_qty": 100,
                "receiving_location": "FINISH_LINE_01"
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        wo_id = response1.json()["work_order_id"]

        # Line clearance check
        response2 = client.post(
            "/api/v1/production/finishing/line-clearance-check",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"work_order_id": wo_id}
        )
        assert response2.status_code == status.HTTP_200_OK

        # Stuffing
        response3 = client.post(
            "/api/v1/production/finishing/stuffing",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": wo_id,
                "quantity_stuffed": 100,
                "dacron_weight_kg": 5.2
            }
        )
        assert response3.status_code == status.HTTP_200_OK

        # Closing & Grooming
        response4 = client.post(
            "/api/v1/production/finishing/closing-grooming",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": wo_id,
                "quantity_closed": 100,
                "seam_quality": "excellent"
            }
        )
        assert response4.status_code == status.HTTP_200_OK

        # CRITICAL: Metal Detector
        response5 = client.post(
            "/api/v1/production/finishing/metal-detector-test",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": wo_id,
                "quantity_tested": 100,
                "test_standard": "ISO_8124_4B",
                "metal_detected": False,
                "test_result": "PASS"
            }
        )
        assert response5.status_code == status.HTTP_200_OK
        assert response5.json()["metal_detector_result"] == "PASS"

        # Physical QC
        response6 = client.post(
            "/api/v1/production/finishing/physical-qc-check",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": wo_id,
                "quantity_inspected": 100,
                "visual_inspection": "excellent",
                "result": "PASS"
            }
        )
        assert response6.status_code == status.HTTP_200_OK

        # Convert to FG
        response7 = client.post(
            "/api/v1/production/finishing/convert-to-fg",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": wo_id,
                "quantity_converted": 100,
                "wip_code": "WIP-FIN-SHARK-01",
                "fg_code": "BLAHAJ-100"
            }
        )
        assert response7.status_code == status.HTTP_200_OK
        assert response7.json()["fg_code"] == "BLAHAJ-100"
