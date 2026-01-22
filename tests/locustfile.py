"""
LOCUST LOAD TESTING - ERP API
Stress test untuk menguji performa API saat high load
"""

from locust import HttpUser, task, between, events
import json
import time

# Test credentials
TEST_USER = {"username": "developer", "password": "password123"}

class ERPUser(HttpUser):
    """Simulate ERP user behavior"""
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token = None
    
    def on_start(self):
        """Login when test starts"""
        response = self.client.post("/api/v1/auth/login", json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Login failed: {response.status_code}")
            self.headers = {}
    
    @task(10)
    def view_dashboard(self):
        """Most common: View dashboard"""
        self.client.get("/api/v1/dashboard/stats", headers=self.headers, name="/dashboard")
    
    @task(8)
    def check_profile(self):
        """Frequent: Check user profile"""
        self.client.get("/api/v1/auth/me", headers=self.headers, name="/auth/me")
    
    @task(5)
    def view_manufacturing_orders(self):
        """Common: View manufacturing orders"""
        self.client.get("/api/v1/ppic/manufacturing-orders", headers=self.headers, name="/ppic/mo")
    
    @task(5)
    def view_warehouse_stock(self):
        """Common: View warehouse stock"""
        self.client.get("/api/v1/warehouse/stock", headers=self.headers, name="/warehouse/stock")
    
    @task(3)
    def view_kanban_board(self):
        """Regular: View kanban board"""
        self.client.get("/api/v1/kanban/board", headers=self.headers, name="/kanban")
    
    @task(3)
    def view_audit_trail(self):
        """Regular: View audit trail"""
        self.client.get("/api/v1/audit-trail?limit=50", headers=self.headers, name="/audit-trail")
    
    @task(2)
    def view_qc_tests(self):
        """Less frequent: View QC tests"""
        self.client.get("/api/v1/qc/tests", headers=self.headers, name="/qc/tests")
    
    @task(2)
    def view_reports(self):
        """Less frequent: View production reports"""
        self.client.get("/api/v1/reports/production", headers=self.headers, name="/reports")
    
    @task(1)
    def create_manufacturing_order(self):
        """Rare: Create new MO (will likely fail validation, but tests endpoint)"""
        data = {
            "product_id": 1,
            "quantity": 100,
            "priority": "normal"
        }
        self.client.post("/api/v1/ppic/manufacturing-orders", 
                        json=data, headers=self.headers, name="/ppic/mo [POST]")


class ConcurrentOperatorUser(HttpUser):
    """Simulate operator doing concurrent updates"""
    wait_time = between(0.5, 2)
    token = None
    
    def on_start(self):
        """Login"""
        response = self.client.post("/api/v1/auth/login", json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task
    def update_production_status(self):
        """Operator updates production status rapidly"""
        self.client.get("/api/v1/kanban/board", headers=self.headers, name="/kanban [concurrent]")


class StressTestUser(HttpUser):
    """Heavy load user for stress testing"""
    wait_time = between(0.1, 0.5)  # Very aggressive
    token = None
    
    def on_start(self):
        """Login"""
        response = self.client.post("/api/v1/auth/login", json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task
    def rapid_auth_check(self):
        """Rapid authentication checks"""
        self.client.get("/api/v1/auth/me", headers=self.headers, name="/auth/me [stress]")


# Custom event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "="*70)
    print("LOCUST LOAD TESTING - ERP API")
    print("="*70)
    print("Starting load test...")
    print("Target: http://localhost:8000")
    print("Users: Check Locust web UI for configuration")
    print("="*70 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "="*70)
    print("LOAD TEST COMPLETED")
    print("="*70)
    print("Check Locust web UI for detailed results")
    print("="*70 + "\n")
