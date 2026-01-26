#!/usr/bin/env python
"""
Comprehensive Page Access Testing for All 22 User Roles
Tests access to all pages/routes with each user account
Generates RBAC/PBAC/UAC access matrix
"""

import requests
import json
from typing import Dict, List, Tuple
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3001"

# All 22 test users
ALL_USERS = {
    # System Roles
    "developer": {"pwd": "password123", "level": "SYSTEM"},
    "superadmin": {"pwd": "password123", "level": "SYSTEM"},
    "admin": {"pwd": "password123", "level": "SYSTEM"},
    
    # Management
    "manager": {"pwd": "password123", "level": "MANAGEMENT"},
    "finance_mgr": {"pwd": "password123", "level": "MANAGEMENT"},
    
    # Department Managers
    "ppic_mgr": {"pwd": "password123", "level": "MANAGER"},
    "ppic_admin": {"pwd": "password123", "level": "MANAGER"},
    "spv_cutting": {"pwd": "password123", "level": "MANAGER"},
    "spv_sewing": {"pwd": "password123", "level": "MANAGER"},
    "spv_finishing": {"pwd": "password123", "level": "MANAGER"},
    "wh_admin": {"pwd": "password123", "level": "MANAGER"},
    "qc_lab": {"pwd": "password123", "level": "MANAGER"},
    "purchasing_head": {"pwd": "password123", "level": "MANAGER"},
    "purchasing": {"pwd": "password123", "level": "OPERATOR"},
    
    # Operators
    "operator_cut": {"pwd": "password123", "level": "OPERATOR"},
    "operator_embro": {"pwd": "password123", "level": "OPERATOR"},
    "operator_sew": {"pwd": "password123", "level": "OPERATOR"},
    "operator_finish": {"pwd": "password123", "level": "OPERATOR"},
    "operator_pack": {"pwd": "password123", "level": "OPERATOR"},
    "qc_inspector": {"pwd": "password123", "level": "OPERATOR"},
    "wh_operator": {"pwd": "password123", "level": "OPERATOR"},
    "security": {"pwd": "password123", "level": "OPERATOR"},
}

# All pages to test
PAGES_TO_TEST = {
    # Dashboard
    "Dashboard": {
        "route": "/",
        "api_endpoints": ["/dashboard/stats"],
    },
    
    # Purchasing
    "Purchasing": {
        "route": "/purchasing",
        "api_endpoints": ["/purchasing/purchase-orders"],
    },
    
    # PPIC
    "PPIC": {
        "route": "/ppic",
        "api_endpoints": ["/ppic/manufacturing-orders"],
    },
    
    # Production
    "Cutting": {
        "route": "/production/cutting",
        "api_endpoints": ["/production/cutting/pending"],
    },
    "Embroidery": {
        "route": "/production/embroidery",
        "api_endpoints": ["/embroidery/work-orders"],
    },
    "Sewing": {
        "route": "/production/sewing",
        "api_endpoints": ["/production/sewing/pending"],
    },
    "Finishing": {
        "route": "/production/finishing",
        "api_endpoints": ["/production/finishing/pending"],
    },
    "Packing": {
        "route": "/production/packing",
        "api_endpoints": ["/production/packing/pending"],
    },
    
    # Warehouse
    "Warehouse": {
        "route": "/warehouse",
        "api_endpoints": ["/warehouse/stock-overview"],
    },
    
    # Finished Goods
    "Finish Goods": {
        "route": "/finishgoods",
        "api_endpoints": ["/finishgoods/inventory"],
    },
    
    # QC
    "QC": {
        "route": "/qc",
        "api_endpoints": ["/quality/stats"],
    },
    
    # Reports
    "Reports": {
        "route": "/reports",
        "api_endpoints": ["/reports/production-stats"],
    },
    
    # Admin Pages
    "User Management": {
        "route": "/admin/users",
        "api_endpoints": ["/admin/users"],
    },
    "Permissions": {
        "route": "/admin/permissions",
        "api_endpoints": ["/admin/permissions"],
    },
    "Audit Trail": {
        "route": "/admin/audit-trail",
        "api_endpoints": ["/audit/logs"],
    },
    "Import/Export": {
        "route": "/admin/import-export",
        "api_endpoints": ["/import_export/status"],
    },
    
    # Settings Pages
    "Change Password": {
        "route": "/settings/password",
        "api_endpoints": [],
    },
    "Display Preferences": {
        "route": "/settings/display",
        "api_endpoints": [],
    },
    "User Access Control": {
        "route": "/settings/uac",
        "api_endpoints": [],
    },
}


class PageAccessTester:
    def __init__(self):
        self.results = {}
        self.tokens = {}
        self.access_matrix = {}
    
    def login_user(self, username: str, password: str) -> bool:
        """Login user and store token"""
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
        except Exception as e:
            pass
        return False
    
    def test_api_endpoint(self, username: str, endpoint: str) -> Tuple[int, str]:
        """Test API endpoint access"""
        try:
            token = self.tokens.get(username)
            if not token:
                return 401, "NO_TOKEN"
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=5
            )
            return response.status_code, "OK"
        except Exception as e:
            return 0, str(e)
    
    def run_all_tests(self):
        """Run tests for all users and pages"""
        print("\n" + "="*100)
        print("PAGE ACCESS TESTING - ALL 22 USER ROLES")
        print("="*100 + "\n")
        
        # Initialize access matrix
        for page in PAGES_TO_TEST.keys():
            self.access_matrix[page] = {}
        
        tested_users = 0
        for username, creds in ALL_USERS.items():
            # Login
            if not self.login_user(username, creds["pwd"]):
                print(f"❌ Failed to login: {username}")
                continue
            
            tested_users += 1
            print(f"\n[{tested_users}/22] Testing {username:20} ({creds['level']:12})")
            print("-" * 100)
            
            # Test each page
            for page, page_config in PAGES_TO_TEST.items():
                endpoints = page_config.get("api_endpoints", [])
                
                # Test all endpoints for this page
                all_ok = True
                status_codes = []
                
                for endpoint in endpoints:
                    status, msg = self.test_api_endpoint(username, endpoint)
                    status_codes.append(status)
                    
                    if status != 200:
                        all_ok = False
                
                # Determine result
                if not endpoints:
                    result = "⚠️  NO_ENDPOINTS"
                    status = "UNKNOWN"
                elif all_ok:
                    result = "✅ OK"
                    status = "ALLOWED"
                elif 403 in status_codes:
                    result = "🚫 FORBIDDEN"
                    status = "DENIED"
                elif 404 in status_codes:
                    result = "❓ NOT_FOUND"
                    status = "NOT_FOUND"
                else:
                    result = "❌ ERROR"
                    status = "ERROR"
                
                self.access_matrix[page][username] = status
                print(f"  {result} {page:25} {status_codes}")
        
        print("\n" + "="*100)
        print("GENERATING ACCESS MATRIX REPORT")
        print("="*100 + "\n")
        self.generate_report()
    
    def generate_report(self):
        """Generate access matrix report"""
        # Count access levels
        allowed = {}
        denied = {}
        
        for page, users_access in self.access_matrix.items():
            allowed[page] = len([u for u, s in users_access.items() if s == "ALLOWED"])
            denied[page] = len([u for u, s in users_access.items() if s == "DENIED"])
        
        # Print summary
        print("PAGE ACCESS SUMMARY")
        print("-" * 100)
        print(f"{'Page':<25} {'Allowed':<8} {'Denied':<8} {'Status'}")
        print("-" * 100)
        
        for page in PAGES_TO_TEST.keys():
            allow_count = allowed.get(page, 0)
            deny_count = denied.get(page, 0)
            status = "✅ PUBLIC" if allow_count > 15 else "🔒 RESTRICTED" if deny_count > 10 else "⚠️  MIXED"
            print(f"{page:<25} {allow_count:<8} {deny_count:<8} {status}")
        
        # Print role-based access
        print("\n" + "="*100)
        print("ROLE-BASED ACCESS SUMMARY")
        print("="*100 + "\n")
        
        role_access = {}
        for username, creds in ALL_USERS.items():
            level = creds["level"]
            if level not in role_access:
                role_access[level] = {"allowed": 0, "denied": 0, "total": 0}
            
            for page, users_access in self.access_matrix.items():
                role_access[level]["total"] += 1
                status = users_access.get(username, "UNKNOWN")
                if status == "ALLOWED":
                    role_access[level]["allowed"] += 1
                elif status == "DENIED":
                    role_access[level]["denied"] += 1
        
        print(f"{'Role Level':<20} {'Allowed':<12} {'Denied':<12} {'Access %'}")
        print("-" * 100)
        
        for level, stats in sorted(role_access.items()):
            if stats["total"] > 0:
                pct = (stats["allowed"] / stats["total"]) * 100
                print(f"{level:<20} {stats['allowed']:<12} {stats['denied']:<12} {pct:.0f}%")
        
        print("\n" + "="*100)
        print("✅ PAGE ACCESS TESTING COMPLETE")
        print("="*100 + "\n")


if __name__ == "__main__":
    tester = PageAccessTester()
    tester.run_all_tests()
