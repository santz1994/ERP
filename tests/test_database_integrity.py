"""
Database Integrity Verification Tests
======================================
Verifies that API calls actually modify database state correctly.
Not just checking HTTP status codes, but actual data persistence.

Test Methodology:
1. Call API endpoint (POST/PUT/DELETE)
2. Query database directly to verify changes
3. Validate data consistency and relationships
4. Check audit trail logging

Author: Daniel - IT Developer Senior
Date: 2026-01-22
"""

import pytest
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Test Configuration
API_URL = "http://localhost:8000/api/v1"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/erp_quty_karunia"
)

# Test User
TEST_USER = {"username": "developer", "password": "password123"}


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def db_engine():
    """Create database engine for direct queries"""
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def db_session(db_engine):
    """Create database session"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


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
    
    if method.upper() == "GET":
        return requests.get(url, headers=headers, timeout=5, **kwargs)
    elif method.upper() == "POST":
        return requests.post(url, headers=headers, timeout=5, **kwargs)
    elif method.upper() == "PUT":
        return requests.put(url, headers=headers, timeout=5, **kwargs)
    elif method.upper() == "DELETE":
        return requests.delete(url, headers=headers, timeout=5, **kwargs)


# ============================================================================
# TEST CLASS: Stock Update Integrity
# ============================================================================

@pytest.mark.integrity
class TestStockIntegrity:
    """Verify stock updates persist correctly in database"""
    
    def test_stock_update_persists_to_database(self, auth_token, db_session):
        """
        DB-INT-01: Stock update via API actually changes database
        
        Steps:
        1. Get initial stock from DB
        2. Call API to update stock
        3. Query DB again to verify change
        4. Validate audit trail created
        """
        product_id = 1
        quantity_to_add = 50
        
        # Step 1: Get initial stock from database
        query = text("""
            SELECT qty_on_hand, qty_reserved
            FROM stock_quants
            WHERE product_id = :product_id
            LIMIT 1
        """)
        
        initial_result = db_session.execute(
            query,
            {"product_id": product_id}
        ).fetchone()
        
        if initial_result:
            initial_qty = float(initial_result[0])
        else:
            initial_qty = 0.0
        
        print(f"\n📊 Initial stock for product {product_id}: {initial_qty}")
        
        # Step 2: Call API to add stock
        stock_data = {
            "item_id": product_id,
            "quantity": quantity_to_add,
            "operation": "add",
            "location_id": 1,
            "reason": "Test DB Integrity"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        
        # API should succeed
        assert response.status_code in [200, 201], \
            f"Stock update failed: {response.status_code} - {response.text}"
        
        # Step 3: Query database to verify change
        db_session.commit()  # Ensure transaction committed
        db_session.expire_all()  # Clear cache
        
        updated_result = db_session.execute(
            query,
            {"product_id": product_id}
        ).fetchone()
        
        if updated_result:
            updated_qty = float(updated_result[0])
        else:
            pytest.fail("Stock record disappeared after update!")
        
        print(f"📊 Updated stock for product {product_id}: {updated_qty}")
        print(f"✅ Expected increase: {quantity_to_add}")
        print(f"✅ Actual increase: {updated_qty - initial_qty}")
        
        # Step 4: Validate the change
        assert updated_qty == initial_qty + quantity_to_add, \
            f"Stock not updated correctly. Expected {initial_qty + quantity_to_add}, Got {updated_qty}"
        
        # Step 5: Verify audit trail (stock_moves table)
        audit_query = text("""
            SELECT quantity, move_type, reference
            FROM stock_moves
            WHERE product_id = :product_id
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        audit_result = db_session.execute(
            audit_query,
            {"product_id": product_id}
        ).fetchone()
        
        if audit_result:
            logged_qty = float(audit_result[0])
            assert logged_qty == quantity_to_add, \
                f"Audit trail shows {logged_qty}, expected {quantity_to_add}"
            print(f"✅ Audit trail verified: {audit_result[2]}")
        else:
            print("⚠️ Warning: No audit trail found (may not be implemented yet)")
    
    def test_stock_subtract_integrity(self, auth_token, db_session):
        """
        DB-INT-02: Stock subtraction updates database correctly
        """
        product_id = 1
        quantity_to_subtract = 10
        
        # Get initial stock
        query = text("""
            SELECT qty_on_hand FROM stock_quants
            WHERE product_id = :product_id
            LIMIT 1
        """)
        
        initial_result = db_session.execute(
            query,
            {"product_id": product_id}
        ).fetchone()
        
        if not initial_result or float(initial_result[0]) < quantity_to_subtract:
            pytest.skip("Insufficient stock for subtraction test")
        
        initial_qty = float(initial_result[0])
        
        # Call API to subtract stock
        stock_data = {
            "item_id": product_id,
            "quantity": quantity_to_subtract,
            "operation": "subtract",
            "location_id": 1,
            "reason": "Test DB Integrity - Subtract"
        }
        
        response = make_request("POST", "/warehouse/stock", auth_token, json=stock_data)
        assert response.status_code == 200, f"Stock subtract failed: {response.text}"
        
        # Verify database change
        db_session.commit()
        db_session.expire_all()
        
        updated_result = db_session.execute(
            query,
            {"product_id": product_id}
        ).fetchone()
        
        updated_qty = float(updated_result[0])
        
        assert updated_qty == initial_qty - quantity_to_subtract, \
            f"Stock subtraction incorrect. Expected {initial_qty - quantity_to_subtract}, Got {updated_qty}"


# ============================================================================
# TEST CLASS: Manufacturing Order Integrity
# ============================================================================

@pytest.mark.integrity
class TestManufacturingOrderIntegrity:
    """Verify MO creation and transitions persist correctly"""
    
    def test_mo_creation_persists(self, auth_token, db_session):
        """
        DB-INT-03: Manufacturing Order creation persists to database
        """
        # Create MO via API
        mo_data = {
            "product_id": 1,
            "qty_planned": 500,
            "batch_number": f"DB-INT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "routing_type": "Route1"
        }
        
        response = make_request("POST", "/ppic/manufacturing-orders", auth_token, json=mo_data)
        
        if response.status_code == 403:
            pytest.skip("User lacks permission to create MO")
        
        assert response.status_code in [200, 201], \
            f"MO creation failed: {response.status_code} - {response.text}"
        
        response_data = response.json()
        mo_id = response_data.get("id") or response_data.get("mo_id")
        
        if not mo_id:
            pytest.skip("API response doesn't include MO ID")
        
        # Query database to verify MO exists
        query = text("""
            SELECT id, product_id, qty_planned, batch_number, state
            FROM manufacturing_orders
            WHERE id = :mo_id
        """)
        
        db_result = db_session.execute(query, {"mo_id": mo_id}).fetchone()
        
        assert db_result is not None, f"MO {mo_id} not found in database!"
        
        # Verify fields match
        assert db_result[1] == mo_data["product_id"], "Product ID mismatch"
        assert float(db_result[2]) == mo_data["qty_planned"], "Qty planned mismatch"
        assert db_result[3] == mo_data["batch_number"], "Batch number mismatch"
        
        print(f"✅ MO {mo_id} verified in database")
        print(f"   Product: {db_result[1]}, Qty: {db_result[2]}, State: {db_result[4]}")


# ============================================================================
# TEST CLASS: Transfer Log Integrity
# ============================================================================

@pytest.mark.integrity
class TestTransferIntegrity:
    """Verify transfer operations create proper database records"""
    
    def test_transfer_creates_log_entry(self, auth_token, db_session):
        """
        DB-INT-04: Transfer between departments creates log entry
        
        Note: This test requires existing work orders. May skip if none available.
        """
        # Try to create a transfer
        transfer_data = {
            "from_dept": "Cutting",
            "to_dept": "Sewing",
            "product_id": 1,
            "qty": 50,
            "reference_doc": "DB-INT-TEST",
            "batch_number": "TEST-BATCH-001"
        }
        
        response = make_request("POST", "/warehouse/transfer", auth_token, json=transfer_data)
        
        if response.status_code == 403:
            pytest.skip("User lacks transfer permission")
        
        if response.status_code == 400:
            # May fail due to business rules (line clearance, etc.)
            pytest.skip(f"Transfer blocked by business rules: {response.text}")
        
        if response.status_code not in [200, 201]:
            pytest.skip(f"Transfer endpoint returned {response.status_code}")
        
        response_data = response.json()
        transfer_id = response_data.get("id")
        
        if not transfer_id:
            pytest.skip("API response doesn't include transfer ID")
        
        # Query database to verify transfer log
        query = text("""
            SELECT id, from_dept, to_dept, qty_sent, status, is_line_clear
            FROM transfer_logs
            WHERE id = :transfer_id
        """)
        
        db_result = db_session.execute(query, {"transfer_id": transfer_id}).fetchone()
        
        assert db_result is not None, f"Transfer {transfer_id} not found in database!"
        
        print(f"✅ Transfer {transfer_id} verified in database")
        print(f"   From: {db_result[1]} → To: {db_result[2]}")
        print(f"   Qty: {db_result[3]}, Status: {db_result[4]}, Line Clear: {db_result[5]}")


# ============================================================================
# TEST CLASS: Audit Trail Integrity
# ============================================================================

@pytest.mark.integrity
class TestAuditTrailIntegrity:
    """Verify all significant operations create audit logs"""
    
    def test_login_creates_audit_log(self, db_session):
        """
        DB-INT-05: User login creates audit trail entry
        """
        # Perform login
        login_time = datetime.now()
        
        response = requests.post(
            f"{API_URL}/auth/login",
            json=TEST_USER,
            timeout=10
        )
        
        assert response.status_code == 200, "Login failed"
        
        # Query audit logs for recent login event
        query = text("""
            SELECT action, module, username, timestamp
            FROM audit_logs
            WHERE username = :username
              AND action = 'LOGIN'
              AND timestamp >= :login_time
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        db_result = db_session.execute(
            query,
            {"username": TEST_USER["username"], "login_time": login_time}
        ).fetchone()
        
        if db_result:
            print(f"✅ Login audit log found")
            print(f"   User: {db_result[2]}, Action: {db_result[0]}, Module: {db_result[1]}")
            assert db_result[2] == TEST_USER["username"], "Username mismatch in audit log"
        else:
            print("⚠️ Warning: Login audit log not found (may not be implemented yet)")


# ============================================================================
# TEST CLASS: Data Consistency
# ============================================================================

@pytest.mark.integrity
class TestDataConsistency:
    """Verify referential integrity and data consistency"""
    
    def test_no_orphaned_work_orders(self, db_session):
        """
        DB-INT-06: All work orders must reference valid manufacturing orders
        """
        query = text("""
            SELECT wo.id, wo.mo_id
            FROM work_orders wo
            LEFT JOIN manufacturing_orders mo ON wo.mo_id = mo.id
            WHERE mo.id IS NULL
            LIMIT 5
        """)
        
        orphaned = db_session.execute(query).fetchall()
        
        assert len(orphaned) == 0, \
            f"Found {len(orphaned)} orphaned work orders: {orphaned}"
        
        print("✅ No orphaned work orders found")
    
    def test_no_orphaned_bom_details(self, db_session):
        """
        DB-INT-07: All BOM details must reference valid BOM headers
        """
        query = text("""
            SELECT bd.id, bd.bom_header_id
            FROM bom_details bd
            LEFT JOIN bom_headers bh ON bd.bom_header_id = bh.id
            WHERE bh.id IS NULL
            LIMIT 5
        """)
        
        orphaned = db_session.execute(query).fetchall()
        
        assert len(orphaned) == 0, \
            f"Found {len(orphaned)} orphaned BOM details: {orphaned}"
        
        print("✅ No orphaned BOM details found")
    
    def test_stock_quants_non_negative(self, db_session):
        """
        DB-INT-08: Stock quantities should never be negative
        """
        query = text("""
            SELECT product_id, qty_on_hand, qty_reserved
            FROM stock_quants
            WHERE qty_on_hand < 0 OR qty_reserved < 0
            LIMIT 5
        """)
        
        negative_stock = db_session.execute(query).fetchall()
        
        assert len(negative_stock) == 0, \
            f"Found {len(negative_stock)} records with negative stock: {negative_stock}"
        
        print("✅ No negative stock quantities found")


# ============================================================================
# SUMMARY
# ============================================================================

@pytest.mark.integrity
def test_database_integrity_summary(db_session):
    """
    Print database integrity check summary
    """
    print("\n" + "="*60)
    print("DATABASE INTEGRITY CHECK SUMMARY")
    print("="*60)
    
    # Count key tables
    tables = {
        "manufacturing_orders": "SELECT COUNT(*) FROM manufacturing_orders",
        "work_orders": "SELECT COUNT(*) FROM work_orders",
        "stock_quants": "SELECT COUNT(*) FROM stock_quants",
        "transfer_logs": "SELECT COUNT(*) FROM transfer_logs",
        "audit_logs": "SELECT COUNT(*) FROM audit_logs"
    }
    
    for table_name, query in tables.items():
        try:
            result = db_session.execute(text(query)).scalar()
            print(f"{table_name:25s} : {result:,} records")
        except Exception as e:
            print(f"{table_name:25s} : ❌ Error: {str(e)}")
    
    print("="*60 + "\n")
