#!/usr/bin/env python
"""Test RBAC, PBAC, UAC with all user accounts"""

import json
import requests
from typing import Dict, List

BASE_URL = "http://localhost:8000/api/v1"

# All test users with their credentials
TEST_USERS = {
    "admin": {"password": "password123", "role": "admin", "expected_access": "FULL"},
    "developer": {"password": "password123", "role": "developer", "expected_access": "FULL"},
    "superadmin": {"password": "password123", "role": "superadmin", "expected_access": "FULL"},
    "manager": {"password": "password123", "role": "manager", "expected_access": "HIGH"},
    "ppic_mgr": {"password": "password123", "role": "ppic_manager", "expected_access": "HIGH"},
    "wh_admin": {"password": "password123", "role": "warehouse_admin", "expected_access": "MEDIUM"},
    "spv_cutting": {"password": "password123", "role": "supervisor", "expected_access": "MEDIUM"},
    "operator_cut": {"password": "password123", "role": "operator", "expected_access": "LOW"},
    "qc_inspector": {"password": "password123", "role": "qc_inspector", "expected_access": "MEDIUM"},
}

# Test endpoints for each role
TEST_ENDPOINTS = {
    "FULL": [
        "/admin/users",
        "/admin/permissions",
        "/audit/logs",
        "/dashboard/stats",
    ],
    "HIGH": [
        "/dashboard/stats",
        "/audit/logs",
    ],
    "MEDIUM": [
        "/dashboard/stats",
    ],
    "LOW": [
        "/dashboard/stats",
    ]
}

class TestRunner:
    def __init__(self):
        self.results = []
        self.tokens = {}
    
    def login(self, username: str, password: str) -> bool:
        """Attempt to login user"""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.tokens[username] = data.get("access_token")
                return True
            return False
        except Exception as e:
            print(f"❌ Login failed for {username}: {e}")
            return False
    
    def test_endpoint(self, username: str, endpoint: str) -> bool:
        """Test if user can access endpoint"""
        try:
            token = self.tokens.get(username)
            if not token:
                return False
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("RBAC/PBAC/UAC TEST SUITE - All User Accounts")
        print("="*80 + "\n")
        
        for username, creds in TEST_USERS.items():
            print(f"Testing {username.upper():20} (Role: {creds['role']})...")
            
            # Test login
            if not self.login(username, creds["password"]):
                print(f"  ❌ LOGIN FAILED\n")
                continue
            
            print(f"  ✅ LOGIN SUCCESSFUL")
            
            # Test endpoints
            expected_access = creds["expected_access"]
            endpoints = TEST_ENDPOINTS.get(expected_access, [])
            
            for endpoint in endpoints:
                success = self.test_endpoint(username, endpoint)
                status = "✅" if success else "❌"
                print(f"    {status} {endpoint}")
            
            print()

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_tests()
