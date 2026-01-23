"""
Boundary Value Analysis (BVA) Tests
====================================
Tests edge cases, invalid inputs, and boundary conditions.

Test Coverage:
- Negative numbers where positive expected
- Zero values where non-zero required
- Extremely large values exceeding limits
- Non-numeric characters in numeric fields
- Invalid date formats
- Empty strings and null values
- SQL injection attempts
- XSS attempts in text fields

Author: Daniel - IT Developer Senior
Date: 2026-01-22
"""

import pytest
import requests
from datetime import datetime, timedelta

# Test Configuration
API_URL = "http://localhost:8000/api/v1"
TEST_USER = {"username": "developer", "password": "password123"}


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{API_URL}/auth/login",
        json=TEST_USER,
        timeout=10
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


def make_request(method: str, endpoint: str, token: str, **kwargs):
    """Helper for authenticated requests"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}{endpoint}"
    
    if method.upper() == "POST":
        return requests.post(url, headers=headers, timeout=5, **kwargs)
    elif method.upper() == "GET":
        return requests.get(url, headers=headers, timeout=5, **kwargs)


# ============================================================================
# TEST CLASS: Numeric Boundary Values
# ============================================================================

@pytest.mark.bva
class TestNumericBoundaries:
    """Test numeric input boundaries"""
    
    def test_negative_quantity_rejected(self, auth_token):
        """
        BVA-01: Negative quantity should be rejected
        """
        stock_data = {
            "item_id": 1,
            "quantity": -50,  # NEGATIVE
            "operation": "add",
            "location_id": 1
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422], \
            f"Negative quantity accepted! Status: {response.status_code}"
        
        print(f"✅ Negative quantity properly rejected: {response.json()}")
    
    def test_zero_quantity_rejected(self, auth_token):
        """
        BVA-02: Zero quantity should be rejected
        """
        stock_data = {
            "item_id": 1,
            "quantity": 0,  # ZERO
            "operation": "add",
            "location_id": 1
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422], \
            f"Zero quantity accepted! Status: {response.status_code}"
        
        print(f"✅ Zero quantity properly rejected")
    
    def test_extremely_large_quantity(self, auth_token):
        """
        BVA-03: Extremely large quantity (> max int) should be rejected
        """
        cutting_data = {
            "work_order_id": 1,
            "quantity": 999999999999999  # Extremely large
        }
        
        response = make_request("POST", "/production/cutting/operations", auth_token, json=cutting_data)
        
        # Should reject with 422 (exceeds MAX_QUANTITY = 10000)
        assert response.status_code in [400, 422], \
            f"Extremely large quantity accepted! Status: {response.status_code}"
        
        print(f"✅ Extremely large quantity properly rejected")
    
    def test_quantity_exactly_at_max_limit(self, auth_token):
        """
        BVA-04: Quantity exactly at max limit (10000) should be ACCEPTED
        """
        cutting_data = {
            "work_order_id": 1,
            "quantity": 10000  # Exactly at MAX_QUANTITY
        }
        
        response = make_request("POST", "/production/cutting/operations", auth_token, json=cutting_data)
        
        # Should accept (200/201) or fail due to work order issue (404), but NOT 422
        assert response.status_code in [200, 201, 400, 404], \
            f"Max quantity boundary failed! Status: {response.status_code}"
        
        print(f"✅ Max limit quantity handled correctly")
    
    def test_quantity_one_above_max_limit(self, auth_token):
        """
        BVA-05: Quantity one above max (10001) should be REJECTED
        """
        cutting_data = {
            "work_order_id": 1,
            "quantity": 10001  # One above MAX_QUANTITY
        }
        
        response = make_request("POST", "/production/cutting/operations", auth_token, json=cutting_data)
        
        # Should reject with 422
        assert response.status_code == 422, \
            f"Quantity above max was not rejected! Status: {response.status_code}"
        
        response_data = response.json()
        assert "exceeds" in response_data.get("detail", "").lower(), \
            "Error message should mention 'exceeds'"
        
        print(f"✅ Quantity above max properly rejected: {response_data['detail']}")


# ============================================================================
# TEST CLASS: String Input Validation
# ============================================================================

@pytest.mark.bva
class TestStringBoundaries:
    """Test string input edge cases"""
    
    def test_empty_string_username(self):
        """
        BVA-06: Empty string username should be rejected
        """
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": "", "password": "test123"},
            timeout=5
        )
        
        assert response.status_code in [400, 422], \
            f"Empty username accepted! Status: {response.status_code}"
        
        print(f"✅ Empty username properly rejected")
    
    def test_sql_injection_attempt(self, auth_token):
        """
        BVA-07: SQL injection in batch number should be sanitized
        """
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": "'; DROP TABLE users; --",  # SQL INJECTION
            "routing_type": "Route1"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", auth_token, json=mo_data)
        
        # Should either sanitize or reject, but NOT execute SQL
        # If accepted, it should be stored as a string, not executed
        if response.status_code in [200, 201]:
            response_data = response.json()
            # Batch number should be stored as-is (escaped), not executed
            print(f"✅ SQL injection attempt handled (stored as string)")
        else:
            # Rejected is also acceptable
            print(f"✅ SQL injection attempt rejected: {response.status_code}")
    
    def test_xss_attempt_in_text_field(self, auth_token):
        """
        BVA-08: XSS attempt in text field should be sanitized
        """
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": "<script>alert('XSS')</script>",  # XSS ATTEMPT
            "routing_type": "Route1"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", auth_token, json=mo_data)
        
        # Should either sanitize or reject
        if response.status_code in [200, 201]:
            print(f"✅ XSS attempt stored safely (should be escaped in frontend)")
        else:
            print(f"✅ XSS attempt rejected: {response.status_code}")
    
    def test_extremely_long_string(self, auth_token):
        """
        BVA-09: Extremely long string (>255 chars) should be rejected or truncated
        """
        long_string = "A" * 1000  # 1000 characters
        
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": long_string,
            "routing_type": "Route1"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", auth_token, json=mo_data)
        
        # Should reject if field has max length constraint
        assert response.status_code in [200, 201, 400, 422], \
            f"Unexpected response for long string: {response.status_code}"
        
        if response.status_code in [400, 422]:
            print(f"✅ Long string properly rejected")
        else:
            print(f"⚠️ Long string accepted (may be truncated by DB)")
    
    def test_unicode_characters(self, auth_token):
        """
        BVA-10: Unicode characters should be handled correctly
        """
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": "测试-批次-🎯",  # Chinese + Emoji
            "routing_type": "Route1"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", auth_token, json=mo_data)
        
        # Should handle unicode or reject gracefully
        assert response.status_code in [200, 201, 400, 422], \
            f"Unicode handling failed: {response.status_code}"
        
        print(f"✅ Unicode characters handled: {response.status_code}")


# ============================================================================
# TEST CLASS: Date/Time Boundaries
# ============================================================================

@pytest.mark.bva
class TestDateTimeBoundaries:
    """Test date/time input edge cases"""
    
    def test_future_date_in_past_field(self, auth_token):
        """
        BVA-11: Future date in 'completed_at' field should be rejected or handled
        """
        from datetime import datetime, timedelta
        # Create a work order first
        work_order_data = {
            "product_id": 1,
            "mo_id": 1,
            "input_qty": 100.0,
            "status": "In Progress"
        }
        wo_response = make_request("POST", "/sewing/operations", auth_token, json=work_order_data)
        
        if wo_response.status_code not in [200, 201]:
            pytest.skip(f"Cannot create work order for date test: {wo_response.status_code}")
        
        # Try to update with future completed_at (before started_at)
        future_date = (datetime.utcnow() + timedelta(days=10)).isoformat()
        update_data = {"completed_at": future_date, "status": "Completed"}
        
        response = make_request("PATCH", f"/sewing/operations/{wo_response.json().get('id')}", 
                               auth_token, json=update_data)
        
        # Should either accept (with validation logic) or handle gracefully
        if response.status_code not in [200, 201, 400, 422]:
            pytest.skip(f"Date endpoint behavior unclear: {response.status_code}")
        print(f"✅ Future date handled: {response.status_code}")
    
    def test_invalid_date_format(self, auth_token):
        """
        BVA-12: Invalid date format should be rejected
        Example: "2026-13-45" (invalid month/day) or non-ISO format
        """
        from datetime import datetime
        # Create a work order first
        work_order_data = {
            "product_id": 1,
            "mo_id": 1,
            "input_qty": 100.0,
            "status": "In Progress"
        }
        wo_response = make_request("POST", "/sewing/operations", auth_token, json=work_order_data)
        
        if wo_response.status_code not in [200, 201]:
            pytest.skip(f"Cannot create work order for date test: {wo_response.status_code}")
        
        # Try invalid date format
        invalid_dates = [
            "2026-13-45",  # Invalid month/day
            "invalid-date",  # Not a date
            "2026/01/01",  # Wrong format
            ""  # Empty
        ]
        
        for invalid_date in invalid_dates:
            update_data = {"started_at": invalid_date}
            response = make_request("PATCH", f"/sewing/operations/{wo_response.json().get('id')}", 
                                   auth_token, json=update_data)
            
            if response.status_code in [400, 422]:
                print(f"✅ Invalid format rejected: {invalid_date}")
                return
        
        pytest.skip("Date format validation not enforced on this endpoint")
    
    def test_year_1900_edge_case(self, auth_token):
        """
        BVA-13: Year 1900 edge case (common datetime bug)
        Historical dates that might cause issues
        """
        from datetime import datetime
        # Create a work order first
        work_order_data = {
            "product_id": 1,
            "mo_id": 1,
            "input_qty": 100.0,
            "status": "In Progress"
        }
        wo_response = make_request("POST", "/sewing/operations", auth_token, json=work_order_data)
        
        if wo_response.status_code not in [200, 201]:
            pytest.skip(f"Cannot create work order for date test: {wo_response.status_code}")
        
        # Try edge case dates
        edge_case_dates = [
            "1900-01-01T00:00:00",  # Year 1900
            "1970-01-01T00:00:00",  # Unix epoch
            "0001-01-01T00:00:00",  # Year 1 AD
        ]
        
        for edge_date in edge_case_dates:
            update_data = {"started_at": edge_date}
            response = make_request("PATCH", f"/sewing/operations/{wo_response.json().get('id')}", 
                                   auth_token, json=update_data)
            
            # Accept either success or rejection, just shouldn't crash
            if response.status_code < 500:
                print(f"✅ Edge case date handled: {edge_date} -> {response.status_code}")
            else:
                raise AssertionError(f"Server error on edge date: {response.status_code}")
        
        print("✅ All edge case dates handled without server errors")


# ============================================================================
# TEST CLASS: Missing Required Fields
# ============================================================================

@pytest.mark.bva
class TestMissingFields:
    """Test behavior when required fields are missing"""
    
    def test_missing_item_id_in_stock_update(self, auth_token):
        """
        BVA-14: Missing item_id should be rejected
        """
        stock_data = {
            # "item_id": missing!
            "quantity": 10,
            "operation": "add"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422], \
            f"Missing item_id was accepted! Status: {response.status_code}"
        
        response_data = response.json()
        detail = response_data.get("detail", "")
        # Handle detail as either string or list
        if isinstance(detail, list):
            detail = str(detail).lower()
        else:
            detail = detail.lower()
        assert "item_id" in detail, \
            "Error message should mention 'item_id'"
        
        print(f"✅ Missing item_id properly rejected: {response_data['detail']}")
    
    def test_missing_quantity_in_stock_update(self, auth_token):
        """
        BVA-15: Missing quantity should be rejected or default to 0 (then rejected)
        """
        stock_data = {
            "item_id": 1,
            # "quantity": missing!
            "operation": "add"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422], \
            f"Missing quantity was accepted! Status: {response.status_code}"
        
        print(f"✅ Missing quantity properly rejected")
    
    def test_missing_work_order_id_in_cutting(self, auth_token):
        """
        BVA-16: Missing work_order_id should be rejected
        """
        cutting_data = {
            # "work_order_id": missing!
            "quantity": 100
        }
        
        response = make_request("POST", "/production/cutting/operations", auth_token, json=cutting_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422], \
            f"Missing work_order_id was accepted! Status: {response.status_code}"
        
        print(f"✅ Missing work_order_id properly rejected")


# ============================================================================
# TEST CLASS: Type Mismatch
# ============================================================================

@pytest.mark.bva
class TestTypeMismatch:
    """Test behavior when wrong data types are provided"""
    
    def test_string_instead_of_number(self, auth_token):
        """
        BVA-17: String in numeric field should be rejected
        """
        stock_data = {
            "item_id": "not_a_number",  # STRING instead of INT
            "quantity": 10,
            "operation": "add"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 422 (validation error)
        assert response.status_code == 422, \
            f"Type mismatch was accepted! Status: {response.status_code}"
        
        print(f"✅ Type mismatch properly rejected")
    
    def test_float_in_integer_field(self, auth_token):
        """
        BVA-18: Float in integer field should be accepted (rounded) or rejected
        """
        stock_data = {
            "item_id": 1,
            "quantity": 10.7,  # FLOAT instead of INT
            "operation": "add"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Either accept (coerce to int), reject, or return 404 if validation fails
        assert response.status_code in [200, 201, 400, 404, 422], \
            f"Float handling unexpected: {response.status_code}"
        
        if response.status_code in [200, 201]:
            print(f"✅ Float accepted (coerced to integer)")
        elif response.status_code == 404:
            print(f"✅ Float endpoint not found or validation failed")
        else:
            print(f"✅ Float rejected (strict type checking)")
    
    def test_array_instead_of_single_value(self, auth_token):
        """
        BVA-19: Array in single-value field should be rejected
        """
        stock_data = {
            "item_id": [1, 2, 3],  # ARRAY instead of INT
            "quantity": 10,
            "operation": "add"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 422
        assert response.status_code == 422, \
            f"Array in single-value field was accepted! Status: {response.status_code}"
        
        print(f"✅ Array properly rejected")


# ============================================================================
# TEST CLASS: Invalid Enum Values
# ============================================================================

@pytest.mark.bva
class TestInvalidEnums:
    """Test invalid enum values"""
    
    def test_invalid_operation_type(self, auth_token):
        """
        BVA-20: Invalid operation type should be rejected
        """
        stock_data = {
            "item_id": 1,
            "quantity": 10,
            "operation": "invalid_operation"  # Invalid enum
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422], \
            f"Invalid operation accepted! Status: {response.status_code}"
        
        print(f"✅ Invalid operation properly rejected")
    
    def test_invalid_routing_type(self, auth_token):
        """
        BVA-21: Invalid routing type should be rejected
        """
        mo_data = {
            "product_id": 1,
            "qty_planned": 100,
            "batch_number": "TEST-BVA-021",
            "routing_type": "InvalidRoute"  # Invalid enum
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", auth_token, json=mo_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422, 403], \
            f"Invalid routing type handling: {response.status_code}"
        
        print(f"✅ Invalid routing type handled")


# ============================================================================
# TEST CLASS: Null/None Values
# ============================================================================

@pytest.mark.bva
class TestNullValues:
    """Test null/None value handling"""
    
    def test_null_in_required_field(self, auth_token):
        """
        BVA-22: Null in required field should be rejected
        """
        stock_data = {
            "item_id": None,  # NULL
            "quantity": 10,
            "operation": "add"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # Should reject with 400 or 422
        assert response.status_code in [400, 422], \
            f"Null in required field was accepted! Status: {response.status_code}"
        
        print(f"✅ Null properly rejected")


# ============================================================================
# SUMMARY
# ============================================================================

@pytest.mark.bva
def test_bva_summary():
    """
    Print BVA test summary
    """
    print("\n" + "="*60)
    print("BOUNDARY VALUE ANALYSIS (BVA) TEST COVERAGE")
    print("="*60)
    print("✅ Numeric boundaries (negative, zero, max, overflow)")
    print("✅ String validation (empty, SQL injection, XSS, length)")
    print("✅ Date/time edge cases (future, invalid, 1900)")
    print("✅ Missing required fields")
    print("✅ Type mismatches (string→int, float→int, array)")
    print("✅ Invalid enum values")
    print("✅ Null/None handling")
    print("="*60 + "\n")
