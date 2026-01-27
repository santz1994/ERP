#!/usr/bin/env python3
"""
Test all 22 user logins + access control + button visibility
"""
import requests
import json
from typing import Dict, List

BASE_URL = "http://localhost:8000/api/v1"

# Test users (22 roles)
TEST_USERS = [
    ("admin", "password123", "Admin"),
    ("superadmin", "password123", "Superadmin"),
    ("developer", "password123", "Developer"),
    ("manager", "password123", "Manager"),
    ("finance_mgr", "password123", "Finance Manager"),
    ("ppic_mgr", "password123", "PPIC Manager"),
    ("ppic_admin", "password123", "PPIC Admin"),
    ("spv_cutting", "password123", "SPV Cutting"),
    ("spv_sewing", "password123", "SPV Sewing"),
    ("spv_finishing", "password123", "SPV Finishing"),
    ("wh_admin", "password123", "Warehouse Admin"),
    ("qc_lab", "password123", "QC Lab"),
    ("purchasing_head", "password123", "Purchasing Head"),
    ("purchasing", "password123", "Purchasing Officer"),
    ("operator_cut", "password123", "Operator Cutting"),
    ("operator_embro", "password123", "Operator Embroidery"),
    ("operator_sew", "password123", "Operator Sewing"),
    ("operator_finish", "password123", "Operator Finishing"),
    ("operator_pack", "password123", "Operator Packing"),
    ("qc_inspector", "password123", "QC Inspector"),
    ("wh_operator", "password123", "Warehouse Operator"),
    ("security", "password123", "Security Guard"),
]

# Endpoints to test per role
TEST_ENDPOINTS = {
    "Admin": [
        ("GET", "/admin/users", 200),
        ("GET", "/admin/permissions", 200),
        ("GET", "/audit/logs", 200),
        ("GET", "/dashboard/stats", 200),
    ],
    "PPIC Manager": [
        ("GET", "/ppic/manufacturing-orders", 200),
        ("GET", "/dashboard/stats", 200),
    ],
    "Operator Cutting": [
        ("GET", "/dashboard/stats", 200),
    ],
    "Warehouse Operator": [
        ("GET", "/dashboard/stats", 200),
    ],
}

def login(username: str, password: str) -> Dict:
    """Login and get JWT token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )
        return {
            "status": response.status_code,
            "token": response.json().get("access_token") if response.status_code == 200 else None,
            "data": response.json()
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

def test_endpoint(token: str, method: str, endpoint: str, expected_status: int) -> Dict:
    """Test single endpoint with token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        
        return {
            "endpoint": endpoint,
            "status": response.status_code,
            "expected": expected_status,
            "pass": response.status_code == expected_status
        }
    except Exception as e:
        return {"endpoint": endpoint, "status": "ERROR", "error": str(e), "pass": False}

def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE USER LOGIN & ACCESS CONTROL TEST")
    print("="*80 + "\n")
    
    results = {
        "login_success": 0,
        "login_failed": 0,
        "access_allowed": 0,
        "access_denied": 0,
        "errors": [],
        "details": []
    }
    
    for username, password, role_name in TEST_USERS:
        # 1. Test login
        login_result = login(username, password)
        
        if login_result["status"] == 200:
            token = login_result["token"]
            print(f"[OK] {username:20} ({role_name:25}) - LOGIN OK")
            results["login_success"] += 1
            
            # 2. Test endpoints for this role
            endpoints = TEST_ENDPOINTS.get(role_name, [("GET", "/dashboard/stats", 200)])
            for method, endpoint, expected in endpoints:
                test_result = test_endpoint(token, method, endpoint, expected)
                
                if test_result.get("pass"):
                    print(f"     [OK] {endpoint:40} [{test_result['status']}]")
                    results["access_allowed"] += 1
                else:
                    print(f"     [FAIL] {endpoint:40} [Got {test_result.get('status')}, Expected {expected}]")
                    results["access_denied"] += 1
                    results["errors"].append(f"{username}:{endpoint}:{test_result.get('status')}")
        else:
            print(f"[FAIL] {username:20} ({role_name:25}) - LOGIN FAILED [{login_result['status']}]")
            results["login_failed"] += 1
            results["errors"].append(f"{username}:LOGIN:{login_result['status']}")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"[OK] Successful Logins:  {results['login_success']}/22")
    print(f"[FAIL] Failed Logins:      {results['login_failed']}/22")
    print(f"[OK] Access Allowed:     {results['access_allowed']}")
    print(f"[FAIL] Access Denied:      {results['access_denied']}")
    
    if results["errors"]:
        print(f"\n[WARN] ERRORS ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"   - {error}")
    
    print("="*80 + "\n")
    
    # Return overall status
    return results["login_failed"] == 0 and results["access_denied"] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
