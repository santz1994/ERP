"""
Phase 2 Backend API Verification Script
Tests all 11 new endpoints + critical fixes
"""

import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, List

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <YOUR_JWT_TOKEN>"  # Replace with actual token
}

# Test data
TEST_SPK_ID = 1
TEST_USER_ID = 1
TEST_MATERIAL_ID = 5
TEST_PRODUCT_ID = 1


class APITester:
    """Test suite for Phase 2 endpoints"""
    
    def __init__(self, base_url: str, headers: Dict):
        self.base_url = base_url
        self.headers = headers
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test_endpoint(self, method: str, path: str, name: str, data: dict = None) -> bool:
        """Test single endpoint"""
        try:
            url = f"{self.base_url}{path}"
            
            if method == "GET":
                resp = requests.get(url, headers=self.headers)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=self.headers)
            elif method == "PUT":
                resp = requests.put(url, json=data, headers=self.headers)
            else:
                return False
            
            status = "✅ PASS" if resp.status_code < 400 else "❌ FAIL"
            self.results.append({
                "name": name,
                "method": method,
                "path": path,
                "status": resp.status_code,
                "result": status
            })
            
            if resp.status_code < 400:
                self.passed += 1
                print(f"{status} {method} {path} ({resp.status_code})")
                return True
            else:
                self.failed += 1
                print(f"{status} {method} {path} ({resp.status_code}) - {resp.text[:100]}")
                return False
                
        except Exception as e:
            self.failed += 1
            print(f"❌ FAIL {method} {path} - {str(e)[:100]}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 2 endpoint tests"""
        print("\n" + "="*70)
        print("🚀 PHASE 2 BACKEND API VERIFICATION")
        print("="*70 + "\n")
        
        # =====================================================================
        # TASK 1: Daily Production Input Endpoints (4)
        # =====================================================================
        print("\n📋 TASK 1: Daily Production Input Endpoints (4/4)\n")
        
        # Test 1.1: Record daily input
        self.test_endpoint(
            "POST",
            f"/production/spk/{TEST_SPK_ID}/daily-input",
            "Record Daily Input",
            {
                "production_date": date.today().isoformat(),
                "input_qty": 100,
                "notes": "Good production",
                "status": "CONFIRMED"
            }
        )
        
        # Test 1.2: Get SPK progress
        self.test_endpoint(
            "GET",
            f"/production/spk/{TEST_SPK_ID}/progress",
            "Get SPK Progress"
        )
        
        # Test 1.3: Get my SPKs
        self.test_endpoint(
            "GET",
            "/production/my-spks",
            "Get My SPKs"
        )
        
        # Test 1.4: Mobile daily input
        self.test_endpoint(
            "POST",
            "/production/mobile/daily-input",
            "Mobile Daily Input",
            {
                "spk_id": TEST_SPK_ID,
                "production_date": date.today().isoformat(),
                "input_qty": 50,
                "notes": "Mobile entry"
            }
        )
        
        # =====================================================================
        # TASK 2: PPIC Dashboard Endpoints (4)
        # =====================================================================
        print("\n📊 TASK 2: PPIC Dashboard Endpoints (4/4)\n")
        
        # Test 2.1: Get PPIC dashboard
        self.test_endpoint(
            "GET",
            "/ppic/dashboard",
            "PPIC Dashboard"
        )
        
        # Test 2.2: Get daily summary
        self.test_endpoint(
            "GET",
            "/ppic/reports/daily-summary",
            "Daily Summary Report"
        )
        
        # Test 2.3: Get on-track status
        self.test_endpoint(
            "GET",
            "/ppic/reports/on-track-status",
            "On-Track Status Report"
        )
        
        # Test 2.4: Get alerts
        self.test_endpoint(
            "GET",
            "/ppic/alerts",
            "PPIC Alerts"
        )
        
        # =====================================================================
        # TASK 3: Approval Workflow Endpoints (3)
        # =====================================================================
        print("\n✅ TASK 3: Approval Workflow Endpoints (3/3)\n")
        
        # Test 3.1: Request modification
        self.test_endpoint(
            "POST",
            f"/production/spk/{TEST_SPK_ID}/request-modification",
            "Request SPK Modification",
            {
                "new_qty": 450,
                "reason": "Customer reduced order",
                "notes": "Will adjust packing"
            }
        )
        
        # Test 3.2: Get pending approvals
        self.test_endpoint(
            "GET",
            "/production/approvals/pending",
            "Get Pending Approvals"
        )
        
        # Test 3.3: Approve modification
        self.test_endpoint(
            "POST",
            "/production/approvals/1/approve",
            "Approve Modification",
            {
                "approved": True,
                "approval_notes": "Approved"
            }
        )
        
        # =====================================================================
        # MATERIAL DEBT ENDPOINTS (Bonus: 2 endpoints)
        # =====================================================================
        print("\n📦 MATERIAL DEBT ENDPOINTS (Bonus 2)\n")
        
        # Test: Request material debt
        self.test_endpoint(
            "POST",
            f"/production/material-debt/request",
            "Request Material Debt",
            {
                "spk_id": TEST_SPK_ID,
                "material_id": TEST_MATERIAL_ID,
                "debt_qty": 100,
                "reason": "Supplier delayed"
            }
        )
        
        # Test: Get pending material debts
        self.test_endpoint(
            "GET",
            "/production/material-debt/pending",
            "Get Pending Material Debts"
        )
        
        # =====================================================================
        # SUMMARY
        # =====================================================================
        print("\n" + "="*70)
        print(f"✅ PASSED: {self.passed} | ❌ FAILED: {self.failed}")
        print(f"📊 TOTAL: {self.passed + self.failed} endpoints tested")
        print(f"📈 SUCCESS RATE: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("="*70 + "\n")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:\n")
        for result in self.results:
            print(f"  {result['result']:10} | {result['method']:6} | {result['path']:45} | {result['status']}")
        
        return self.failed == 0


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    tester = APITester(BASE_URL, HEADERS)
    
    print("""
    ⚠️  BEFORE RUNNING TESTS:
    
    1. Start the backend server:
       cd d:\\Project\\ERP2026\\erp-softtoys
       python -m uvicorn app.main:app --reload --port 8000
    
    2. Get a valid JWT token and replace <YOUR_JWT_TOKEN> in HEADERS
    
    3. Update TEST_SPK_ID, TEST_USER_ID, TEST_MATERIAL_ID if needed
    
    4. Run this script:
       python verify_phase2_apis.py
    """)
    
    input("\nPress ENTER to start testing...")
    
    # Run tests
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)
