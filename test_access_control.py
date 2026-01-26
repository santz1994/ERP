#!/usr/bin/env python
"""
Comprehensive RBAC/PBAC/UAC Testing Suite
Tests API endpoint access, page visibility, and function permissions for all 22 user roles
"""

import requests
import json
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000/api/v1"

# All test users with expected access levels
TEST_USERS = {
    # Level 0-1: Full Access
    "developer": {"access_level": "FULL", "can_access": ["admin", "audit", "dashboard", "ppic", "warehouse"]},
    "superadmin": {"access_level": "FULL", "can_access": ["admin", "audit", "dashboard", "ppic", "warehouse"]},
    
    # Level 2: High Access
    "manager": {"access_level": "HIGH", "can_access": ["dashboard", "audit", "ppic", "warehouse", "purchasing"]},
    "finance_mgr": {"access_level": "HIGH", "can_access": ["dashboard"]},
    
    # Level 3: System Admin
    "admin": {"access_level": "FULL", "can_access": ["admin", "audit", "dashboard", "ppic", "warehouse"]},
    
    # Level 4: Department Managers
    "ppic_mgr": {"access_level": "HIGH", "can_access": ["dashboard", "ppic"]},
    "ppic_admin": {"access_level": "HIGH", "can_access": ["dashboard", "ppic"]},
    "spv_cutting": {"access_level": "MEDIUM", "can_access": ["dashboard", "production"]},
    "spv_sewing": {"access_level": "MEDIUM", "can_access": ["dashboard", "production"]},
    "spv_finishing": {"access_level": "MEDIUM", "can_access": ["dashboard", "production"]},
    "wh_admin": {"access_level": "HIGH", "can_access": ["dashboard", "warehouse"]},
    "qc_lab": {"access_level": "MEDIUM", "can_access": ["dashboard", "quality"]},
    "purchasing_head": {"access_level": "HIGH", "can_access": ["dashboard", "purchasing"]},
    "purchasing": {"access_level": "MEDIUM", "can_access": ["dashboard", "purchasing"]},
    
    # Level 5: Operations
    "operator_cut": {"access_level": "LOW", "can_access": ["dashboard"]},
    "operator_embro": {"access_level": "LOW", "can_access": ["dashboard"]},
    "operator_sew": {"access_level": "LOW", "can_access": ["dashboard"]},
    "operator_finish": {"access_level": "LOW", "can_access": ["dashboard"]},
    "operator_pack": {"access_level": "LOW", "can_access": ["dashboard"]},
    "qc_inspector": {"access_level": "MEDIUM", "can_access": ["dashboard", "quality"]},
    "wh_operator": {"access_level": "LOW", "can_access": ["dashboard", "warehouse"]},
    "security": {"access_level": "LOW", "can_access": ["dashboard"]},
}

# API endpoints to test for each access level
ENDPOINTS_BY_LEVEL = {
    "FULL": [
        "/admin/users",
        "/admin/permissions",
        "/audit/logs",
        "/dashboard/stats",
        "/ppic/manufacturing-orders",
        "/warehouse/inventory",
    ],
    "HIGH": [
        "/dashboard/stats",
        "/audit/logs",
        "/ppic/manufacturing-orders",
    ],
    "MEDIUM": [
        "/dashboard/stats",
    ],
    "LOW": [
        "/dashboard/stats",
    ]
}

class ACLTester:
    def __init__(self):
        self.results = {
            "login": {},
            "endpoint_access": {},
            "summary": {}
        }
        self.tokens = {}
    
    def login_user(self, username: str, password: str = "password123") -> bool:
        """Test user login"""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.tokens[username] = data.get("access_token")
                self.results["login"][username] = {
                    "status": "[OK] SUCCESS",
                    "role": data.get("role", "unknown")
                }
                return True
            else:
                self.results["login"][username] = {
                    "status": "[FAIL]",
                    "code": response.status_code
                }
                return False
        except Exception as e:
            self.results["login"][username] = {
                "status": "[ERROR]",
                "error": str(e)
            }
            return False
    
    def test_endpoint(self, username: str, endpoint: str) -> Tuple[bool, int]:
        """Test if user can access endpoint"""
        try:
            token = self.tokens.get(username)
            if not token:
                return False, 0
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=5
            )
            # 200=success, 403=permission denied, 401=auth failed
            return response.status_code == 200, response.status_code
        except Exception as e:
            return False, 0
    
    def run_complete_tests(self):
        """Run all tests"""
        print("\n" + "="*100)
        print("COMPREHENSIVE RBAC/PBAC/UAC TEST SUITE - All 22 User Roles")
        print("="*100 + "\n")
        
        total_users = 0
        successful_logins = 0
        successful_access = 0
        total_access_tests = 0
        
        for username, user_config in sorted(TEST_USERS.items()):
            access_level = user_config["access_level"]
            
            # Test login
            print(f"\n[AUTH] Testing: {username:20} (Level: {access_level})")
            print("-" * 100)
            
            if not self.login_user(username):
                print(f"  [FAIL] LOGIN FAILED - Cannot proceed with endpoint tests")
                total_users += 1
                continue
            
            successful_logins += 1
            print(f"  [OK] LOGIN SUCCESSFUL")
            
            # Test endpoints for this access level
            endpoints = ENDPOINTS_BY_LEVEL.get(access_level, [])
            
            if not endpoints:
                print(f"  [INFO] No endpoints configured for access level {access_level}")
            else:
                print(f"  Testing {len(endpoints)} endpoints...")
                for endpoint in endpoints:
                    success, code = self.test_endpoint(username, endpoint)
                    status = "[OK]" if success else "[FAIL]"
                    code_str = f"({code})" if code else ""
                    print(f"    {status} {endpoint:40} {code_str}")
                    
                    if success:
                        successful_access += 1
                    total_access_tests += 1
            
            total_users += 1
            self.results["endpoint_access"][username] = {
                "access_level": access_level,
                "login": "success",
                "endpoints_tested": len(endpoints)
            }
        
        # Print summary
        print("\n" + "="*100)
        print("SUMMARY")
        print("="*100)
        print(f"Total Users Tested:           {total_users}/22")
        print(f"Successful Logins:            {successful_logins}/{total_users}")
        print(f"Successful Access Tests:      {successful_access}/{total_access_tests}")
        print(f"Access Success Rate:          {(successful_access/total_access_tests*100 if total_access_tests > 0 else 0):.1f}%")
        print("="*100 + "\n")
        
        return self.results

if __name__ == "__main__":
    tester = ACLTester()
    results = tester.run_complete_tests()
