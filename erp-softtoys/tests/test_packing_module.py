"""
Packing Module Test Suite
Tests for Steps 470-490 of packing process workflow
"""

from fastapi import status


class TestPackingSortByDestination:
    """Test sort by destination and week (Step 470)"""

    def test_sort_by_destination_success(self, client, operator_token):
        """Test successful sorting by destination"""
        response = client.post(
            "/api/v1/production/packing/sort-by-destination",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_sort": 100,
                "destination_country": "USA",
                "delivery_week": 22
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Sorted"
        assert data["destination_country"] == "USA"
        assert data["delivery_week"] == 22

    def test_sort_multiple_destinations(self, client, operator_token):
        """Test sorting same batch to multiple destinations"""
        response = client.post(
            "/api/v1/production/packing/sort-by-destination",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantities_by_destination": [
                    {"country": "USA", "qty": 50, "week": 22},
                    {"country": "EUROPE", "qty": 30, "week": 22},
                    {"country": "ASIA", "qty": 20, "week": 23}
                ]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_sorted"] == 100
        assert len(data["destination_splits"]) == 3

    def test_sort_qty_validation(self, client, operator_token):
        """Test quantity validation during sorting"""
        response = client.post(
            "/api/v1/production/packing/sort-by-destination",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_sort": 150,  # More than available
                "destination_country": "USA",
                "delivery_week": 22
            }
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestPackagingIntoCartons:
    """Test packaging into cartons (Step 480)"""

    def test_package_cartons_success(self, client, operator_token):
        """Test successful carton packaging"""
        response = client.post(
            "/api/v1/production/packing/package-cartons",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_pack": 100,
                "items_per_carton": 10,
                "carton_type": "Polybag + Carton",
                "destination": "USA"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Packaged"
        assert data["total_cartons"] == 10
        assert data["items_packed"] == 100

    def test_package_cartons_partial_fill(self, client, operator_token):
        """Test carton packaging with partial last carton"""
        response = client.post(
            "/api/v1/production/packing/package-cartons",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_pack": 95,  # Will have 1 partial carton
                "items_per_carton": 10,
                "carton_type": "Polybag + Carton"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_cartons"] == 10  # 9 full + 1 partial
        assert data["items_packed"] == 95

    def test_package_cartons_manifest_creation(self, client, operator_token):
        """Test carton manifest creation during packaging"""
        response = client.post(
            "/api/v1/production/packing/package-cartons",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_pack": 100,
                "items_per_carton": 10,
                "carton_type": "Polybag + Carton",
                "create_manifest": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "carton_manifest_id" in data
        assert data["manifest_status"] == "Created"


class TestGenerateShippingMark:
    """Test shipping mark generation (Step 490)"""

    def test_generate_shipping_mark_success(self, client, admin_token):
        """Test successful shipping mark generation"""
        response = client.post(
            "/api/v1/production/packing/shipping-mark",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "carton_number": 1,
                "destination": "USA",
                "delivery_week": 22,
                "article_code": "BLAHAJ-100",
                "quantity": 10
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["shipping_mark_status"] == "Generated"
        assert "barcode" in data
        assert "shipping_mark_id" in data

    def test_generate_shipping_mark_batch(self, client, admin_token):
        """Test batch shipping mark generation"""
        response = client.post(
            "/api/v1/production/packing/shipping-mark",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "total_cartons": 10,
                "destination": "USA",
                "delivery_week": 22,
                "article_code": "BLAHAJ-100",
                "batch_generate": True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["marks_generated"] == 10
        assert "barcode_list" in data or "marks" in data

    def test_generate_shipping_mark_validation(self, client, admin_token):
        """Test shipping mark validation"""
        response = client.post(
            "/api/v1/production/packing/shipping-mark",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "carton_number": 999,  # Non-existent
                "destination": "USA",
                "delivery_week": 22,
                "article_code": "BLAHAJ-100",
                "quantity": 10
            }
        )
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


class TestPackingCompletion:
    """Test packing completion"""

    def test_packing_complete_success(self, client, admin_token):
        """Test successful packing completion"""
        response = client.post(
            "/api/v1/production/packing/complete",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "total_cartons": 10,
                "total_qty": 100,
                "final_inspection_pass": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Complete"
        assert data["total_cartons"] == 10

    def test_packing_final_inspection_fail(self, client, admin_token):
        """Test packing with final inspection failure"""
        response = client.post(
            "/api/v1/production/packing/complete",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "total_cartons": 10,
                "total_qty": 100,
                "final_inspection_pass": False,
                "inspection_issues": "Damaged cartons detected"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] in ["Failed", "Inspection Failed", "On Hold"]


class TestPackingStatusEndpoints:
    """Test status and pending work order endpoints"""

    def test_get_packing_status(self, client, operator_token):
        """Test get packing work order status"""
        response = client.get(
            "/api/v1/production/packing/status/1",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "work_order_id" in data
        assert "status" in data
        assert "total_cartons" in data or "quantity" in data

    def test_get_pending_packing(self, client, operator_token):
        """Test get pending packing work orders"""
        response = client.get(
            "/api/v1/production/packing/pending",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list) or "work_orders" in data


class TestPackingEndtoEnd:
    """End-to-end packing process workflow"""

    def test_packing_workflow_complete(self, client, operator_token, admin_token):
        """Test complete packing workflow from finishing"""
        # Sort by destination
        response1 = client.post(
            "/api/v1/production/packing/sort-by-destination",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_sort": 100,
                "destination_country": "USA",
                "delivery_week": 22
            }
        )
        assert response1.status_code == status.HTTP_200_OK

        # Package into cartons
        response2 = client.post(
            "/api/v1/production/packing/package-cartons",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_pack": 100,
                "items_per_carton": 10,
                "carton_type": "Polybag + Carton",
                "destination": "USA"
            }
        )
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        total_cartons = data2["total_cartons"]

        # Generate shipping marks
        response3 = client.post(
            "/api/v1/production/packing/shipping-mark",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "total_cartons": total_cartons,
                "destination": "USA",
                "delivery_week": 22,
                "article_code": "BLAHAJ-100",
                "batch_generate": True
            }
        )
        assert response3.status_code == status.HTTP_201_CREATED
        assert response3.json()["marks_generated"] == total_cartons

        # Complete packing
        response4 = client.post(
            "/api/v1/production/packing/complete",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "work_order_id": 1,
                "total_cartons": total_cartons,
                "total_qty": 100,
                "final_inspection_pass": True
            }
        )
        assert response4.status_code == status.HTTP_200_OK
        assert response4.json()["status"] == "Complete"

    def test_packing_split_destination_workflow(self, client, operator_token, admin_token):
        """Test packing workflow with split destinations"""
        # Sort to multiple destinations
        response1 = client.post(
            "/api/v1/production/packing/sort-by-destination",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantities_by_destination": [
                    {"country": "USA", "qty": 50, "week": 22},
                    {"country": "EUROPE", "qty": 50, "week": 22}
                ]
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["total_sorted"] == 100

        # Package USA batch
        response2a = client.post(
            "/api/v1/production/packing/package-cartons",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_pack": 50,
                "items_per_carton": 10,
                "destination": "USA"
            }
        )
        assert response2a.status_code == status.HTTP_200_OK

        # Package EUROPE batch
        response2b = client.post(
            "/api/v1/production/packing/package-cartons",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "work_order_id": 1,
                "quantity_to_pack": 50,
                "items_per_carton": 10,
                "destination": "EUROPE"
            }
        )
        assert response2b.status_code == status.HTTP_200_OK
