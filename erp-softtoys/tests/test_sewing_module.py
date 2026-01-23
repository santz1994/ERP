"""
Sewing Module Test Suite
Tests for Steps 300-383 of sewing process workflow
"""

from fastapi import status


class TestSewingAcceptTransfer:
    """Test accept transfer and handshake (Step 300)"""

    def test_accept_transfer_success(self, client, admin_token):
        """Test successful transfer acceptance"""
        response = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": 1,
                "received_qty": 100,
                "receiving_location": "LINE_SEWING_01"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["handshake_status"] == "UNLOCKED"
        assert data["work_order_status"] == "Accepted"

    def test_accept_transfer_qty_mismatch(self, client, admin_token):
        """Test transfer acceptance with quantity mismatch"""
        response = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": 1,
                "received_qty": 95,  # Less than sent
                "receiving_location": "LINE_SEWING_01",
                "discrepancy_reason": "Counting error during receipt"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "discrepancy" in data or "qty_variance" in data


class TestSewingValidateInput:
    """Test input validation against BOM (Step 310)"""

    def test_validate_input_success(self, client, admin_token):
        """Test successful input validation"""
        response = client.post(
            "/api/v1/production/sewing/validate-input",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "input_qty": 100,
                "article_code": "SEW-SHARK-01"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["validation_status"] == "PASS"
        assert data["qty_ok"] is True

    def test_validate_input_insufficient_qty(self, client, admin_token):
        """Test validation with insufficient quantity"""
        response = client.post(
            "/api/v1/production/sewing/validate-input",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "input_qty": 50,  # Less than target
                "article_code": "SEW-SHARK-01"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["validation_status"] in ["INSUFFICIENT", "SHORTAGE"]

    def test_validate_input_auto_request_materials(self, client, admin_token):
        """Test automatic material request on insufficient input"""
        response = client.post(
            "/api/v1/production/sewing/validate-input",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "input_qty": 80,
                "article_code": "SEW-SHARK-01",
                "auto_request_materials": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "material_request_id" in data or "auto_request_pending" in data


class TestSewingProcessStages:
    """Test 3-stage sewing process (Steps 330-350)"""

    def test_stage_1_assembly(self, client, operator_token):
        """Test Stage 1: Assembly"""
        response = client.post(
            "/api/v1/production/sewing/process-stage/1",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_processed": 50,
                "stage_notes": "Assembly started at line 3"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["current_stage"] == 1
        assert data["stage_name"] == "Assembly"

    def test_stage_2_labeling(self, client, operator_token):
        """Test Stage 2: Attach Label"""
        response = client.post(
            "/api/v1/production/sewing/process-stage/2",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_processed": 50,
                "label_destination": "USA",
                "label_week": 22
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["current_stage"] == 2
        assert data["stage_name"] == "Labeling"
        assert data["label_destination"] == "USA"

    def test_stage_3_loop_stitch(self, client, operator_token):
        """Test Stage 3: Back Loop Stitch"""
        response = client.post(
            "/api/v1/production/sewing/process-stage/3",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_processed": 50,
                "stage_notes": "Loop stitching complete"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["current_stage"] == 3
        assert data["stage_name"] == "Loop Stitch"

    def test_stage_progression_validation(self, client, operator_token):
        """Test that stages must progress sequentially"""
        # Try to jump from stage 1 to stage 3
        response = client.post(
            "/api/v1/production/sewing/process-stage/3",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 99,  # New WO that hasn't completed stage 1 & 2
                "quantity_processed": 50
            }
        )
        # Should fail or require previous stages
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestInlineQC:
    """Test inline quality control (Steps 360-375)"""

    def test_qc_pass_inspection(self, client, qc_token):
        """Test QC pass inspection"""
        response = client.post(
            "/api/v1/production/sewing/qc-inspect",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": 1,
                "inspection_qty": 50,
                "stitching_quality": "excellent",
                "label_placement": "correct",
                "defects_found": 0,
                "result": "PASS"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["inspection_status"] == "PASS"
        assert data["pass_qty"] == 50
        assert data["rework_qty"] == 0

    def test_qc_rework_inspection(self, client, qc_token):
        """Test QC rework required"""
        response = client.post(
            "/api/v1/production/sewing/qc-inspect",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": 1,
                "inspection_qty": 50,
                "stitching_quality": "poor",
                "label_placement": "misaligned",
                "defects_found": 3,
                "result": "REWORK",
                "rework_instruction": "Re-stitch from middle"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["inspection_status"] == "REWORK"
        assert data["rework_qty"] == 50

    def test_qc_scrap_inspection(self, client, qc_token):
        """Test QC scrap decision"""
        response = client.post(
            "/api/v1/production/sewing/qc-inspect",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": 1,
                "inspection_qty": 5,
                "stitching_quality": "failed",
                "defects_found": 5,
                "result": "SCRAP",
                "scrap_reason": "Multiple needle breaks detected"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["inspection_status"] == "SCRAP"
        assert data["scrap_qty"] == 5


class TestSegregationCheck:
    """Test segregation check (Step 380) - QT-09 Protocol"""

    def test_segregation_same_destination_allowed(self, client, admin_token):
        """Test segregation check when destination matches"""
        response = client.get(
            "/api/v1/production/sewing/segregation-check/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["segregation_status"] == "APPROVED"
        assert data["can_transfer"] is True

    def test_segregation_different_destination_blocked(self, client, admin_token):
        """Test segregation check when destination differs"""
        response = client.get(
            "/api/v1/production/sewing/segregation-check/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should return blocked or require clearance
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # If destinations differ, should be blocked
        if "segregation_status" in data:
            assert data["segregation_status"] in ["BLOCKED", "REQUIRES_CLEARANCE"]


class TestTransferToFinishing:
    """Test transfer to finishing with handshake (Steps 381-383)"""

    def test_transfer_to_finishing_success(self, client, operator_token):
        """Test successful transfer to finishing"""
        response = client.post(
            "/api/v1/production/sewing/transfer-to-finishing",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "transfer_qty": 50,
                "transfer_slip_number": "TSLS-001",
                "destination_line": "FINISH_LINE_01"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["handshake_status"] == "LOCKED"
        assert data["transfer_slip"] is not None


class TestSewingStatusEndpoints:
    """Test status and pending work order endpoints"""

    def test_get_work_order_status(self, client, operator_token):
        """Test get work order status"""
        response = client.get(
            "/api/v1/production/sewing/status/1",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "work_order_id" in data
        assert "current_stage" in data
        assert "status" in data

    def test_get_pending_work_orders(self, client, operator_token):
        """Test get pending work orders"""
        response = client.get(
            "/api/v1/production/sewing/pending",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list) or "work_orders" in data


class TestSewingEndtoEnd:
    """End-to-end sewing process workflow"""

    def test_sewing_workflow_complete(self, client, admin_token, operator_token, qc_token):
        """Test complete sewing workflow"""
        # Accept transfer from cutting
        response1 = client.post(
            "/api/v1/production/sewing/accept-transfer",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "transfer_id": 1,
                "received_qty": 100,
                "receiving_location": "LINE_SEWING_01"
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        wo_id = response1.json()["work_order_id"]

        # Validate input
        response2 = client.post(
            "/api/v1/production/sewing/validate-input",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": wo_id,
                "input_qty": 100,
                "article_code": "SEW-SHARK-01"
            }
        )
        assert response2.status_code == status.HTTP_200_OK

        # Process all stages
        for stage in [1, 2, 3]:
            response = client.post(
                f"/api/v1/production/sewing/process-stage/{stage}",
                headers={"Authorization": f"Bearer {operator_token}"},
                json={"work_order_id": wo_id, "quantity_processed": 100}
            )
            assert response.status_code == status.HTTP_200_OK

        # Inline QC
        response3 = client.post(
            "/api/v1/production/sewing/qc-inspect",
            headers={"Authorization": f"Bearer {qc_token}"},
            json={
                "work_order_id": wo_id,
                "inspection_qty": 100,
                "stitching_quality": "excellent",
                "result": "PASS"
            }
        )
        assert response3.status_code == status.HTTP_200_OK

        # Segregation check
        response4 = client.get(
            f"/api/v1/production/sewing/segregation-check/{wo_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response4.status_code == status.HTTP_200_OK

        # Transfer to finishing
        response5 = client.post(
            "/api/v1/production/sewing/transfer-to-finishing",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": wo_id,
                "transfer_qty": 100,
                "transfer_slip_number": "TSLS-E2E"
            }
        )
        assert response5.status_code == status.HTTP_201_CREATED
        assert response5.json()["handshake_status"] == "LOCKED"
