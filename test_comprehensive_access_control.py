#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COMPREHENSIVE RBAC/PBAC/UAC TEST - ALL PAGES & ALL 22 USERS
Tests access to all 18 pages with all 22 user roles
Generates complete access matrix
"""

import os
import sys
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# All 22 users
ALL_USERS = {
    "developer": {"pwd": "password123"},
    "superadmin": {"pwd": "password123"},
    "admin": {"pwd": "password123"},
    "manager": {"pwd": "password123"},
    "finance_mgr": {"pwd": "password123"},
    "ppic_mgr": {"pwd": "password123"},
    "ppic_admin": {"pwd": "password123"},
    "spv_cutting": {"pwd": "password123"},
    "spv_sewing": {"pwd": "password123"},
    "spv_finishing": {"pwd": "password123"},
    "wh_admin": {"pwd": "password123"},
    "qc_lab": {"pwd": "password123"},
    "purchasing_head": {"pwd": "password123"},
    "purchasing": {"pwd": "password123"},
    "operator_cut": {"pwd": "password123"},
    "operator_embro": {"pwd": "password123"},
    "operator_sew": {"pwd": "password123"},
    "operator_finish": {"pwd": "password123"},
    "operator_pack": {"pwd": "password123"},
    "qc_inspector": {"pwd": "password123"},
    "wh_operator": {"pwd": "password123"},
    "security": {"pwd": "password123"},
}

# All 18 pages with their API endpoints
ALL_PAGES = {
    # Dashboard
    "Dashboard": ["/dashboard/stats"],
    
    # Purchasing
    "Purchasing": ["/purchasing/purchase-orders"],
    
    # PPIC
    "PPIC": ["/ppic/manufacturing-orders"],
    
    # Production Modules
    "Cutting": ["/production/cutting/pending", "/cutting/line-status"],
    "Embroidery": ["/embroidery/work-orders", "/embroidery/line-status"],
    "Sewing": ["/production/sewing/pending"],
    "Finishing": ["/production/finishing/pending"],
    "Packing": ["/production/packing/pending"],
    
    # Warehouse
    "Warehouse": ["/warehouse/stock-overview", "/warehouse/material-requests"],
    
    # Finish Goods
    "Finish Goods": ["/finishgoods/inventory", "/finishgoods/ready-for-shipment"],
    
    # QC
    "QC": ["/quality/stats"],
    
    # Reports
    "Reports": ["/reports/production-stats", "/reports/qc-stats"],
    
    # Admin
    "User Management": ["/admin/users"],
    "Permissions": ["/admin/permissions"],
    "Audit Trail": ["/audit/logs"],
    "Import/Export": ["/import-export/status"],
    
    # Settings (no API, just frontend routes)
    "Settings": [],
}


class ComprehensiveACLTester:
    def __init__(self):
        self.tokens = {}
        self.results = {}
        self.access_matrix = {}
    
    def login_user(self, username: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                self.tokens[username] = response.json().get("access_token")
                return True
        except:
            pass
        return False
    
    def test_endpoint(self, username: str, endpoint: str) -> int:
        try:
            token = self.tokens.get(username)
            if not token:
                return 401
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=5
            )
            return response.status_code
        except:
            return 0
    
    def run_tests(self):
        print("\n" + "="*120)
        print("COMPREHENSIVE RBAC/PBAC/UAC TEST - ALL 22 USERS & ALL 18 PAGES")
        print("="*120 + "\n")
        
        # Initialize access matrix
        for page in ALL_PAGES.keys():
            self.access_matrix[page] = {}
        
        # Login all users
        print("🔐 LOGGING IN ALL 22 USERS...")
        for username, creds in ALL_USERS.items():
            if self.login_user(username, creds["pwd"]):
                print(f"  ✅ {username:20}")
            else:
                print(f"  ❌ {username:20}")
        
        print("\n" + "="*120)
        print("📊 TESTING ALL PAGES WITH ALL USERS")
        print("="*120 + "\n")
        
        # Test each page with each user
        for page, endpoints in ALL_PAGES.items():
            print(f"\n📄 Page: {page}")
            print("-" * 120)
            
            if not endpoints:
                print("  ⚠️  Frontend-only page (no API to test)")
                continue
            
            # Test with each user
            for username in ALL_USERS.keys():
                statuses = []
                for endpoint in endpoints:
                    status = self.test_endpoint(username, endpoint)
                    statuses.append(status)
                
                # Determine result
                if 200 in statuses:
                    result = "✅ ALLOW"
                    self.access_matrix[page][username] = "ALLOWED"
                elif 403 in statuses or all(s == 403 for s in statuses):
                    result = "🚫 DENY"
                    self.access_matrix[page][username] = "DENIED"
                elif 404 in statuses or all(s == 404 for s in statuses):
                    result = "❓ NOT FOUND"
                    self.access_matrix[page][username] = "NOT_FOUND"
                else:
                    result = "❌ ERROR"
                    self.access_matrix[page][username] = "ERROR"
                
                # Print result
                print(f"  {result} {username:20} {statuses}")
        
        print("\n" + "="*120)
        print("📈 GENERATING ACCESS MATRIX")
        print("="*120 + "\n")
        self.print_access_matrix()
    
    def print_access_matrix(self):
        """Print access matrix table"""
        
        # Count access types
        summary = {}
        for page, users_access in self.access_matrix.items():
            allowed = len([u for u, s in users_access.items() if s == "ALLOWED"])
            denied = len([u for u, s in users_access.items() if s == "DENIED"])
            not_found = len([u for u, s in users_access.items() if s == "NOT_FOUND"])
            
            summary[page] = {
                "ALLOWED": allowed,
                "DENIED": denied,
                "NOT_FOUND": not_found,
            }
        
        # Print summary
        print("PAGE ACCESS SUMMARY")
        print(f"{'Page':<20} {'Allowed':<8} {'Denied':<8} {'Not Found':<10} {'Type'}")
        print("-" * 120)
        
        for page in sorted(summary.keys()):
            stats = summary[page]
            allowed = stats["ALLOWED"]
            denied = stats["DENIED"]
            not_found = stats["NOT_FOUND"]
            
            if denied > 15:
                page_type = "🔒 RESTRICTED"
            elif allowed > 15:
                page_type = "✅ PUBLIC"
            else:
                page_type = "⚠️  MIXED"
            
            print(f"{page:<20} {allowed:<8} {denied:<8} {not_found:<10} {page_type}")
        
        # Role-based summary
        print("\n" + "="*120)
        print("ROLE-BASED ACCESS SUMMARY")
        print("="*120 + "\n")
        
        role_summary = {}
        for username in ALL_USERS.keys():
            allowed = 0
            denied = 0
            for page, users_access in self.access_matrix.items():
                status = users_access.get(username, "UNKNOWN")
                if status == "ALLOWED":
                    allowed += 1
                elif status == "DENIED":
                    denied += 1
            
            role_summary[username] = {"allowed": allowed, "denied": denied}
        
        print(f"{'User':<20} {'Pages Allowed':<15} {'Pages Denied':<15} {'Access %'}")
        print("-" * 120)
        
        for username in sorted(role_summary.keys()):
            stats = role_summary[username]
            total = stats["allowed"] + stats["denied"]
            pct = (stats["allowed"] / total * 100) if total > 0 else 0
            print(f"{username:<20} {stats['allowed']:<15} {stats['denied']:<15} {pct:.0f}%")
        
        print("\n" + "="*120)
        print(f"✅ TEST COMPLETED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120 + "\n")


if __name__ == "__main__":
    tester = ComprehensiveACLTester()
    tester.run_tests()
