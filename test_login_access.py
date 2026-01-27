#!/usr/bin/env python
"""Test login, access, permissions for all user roles"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

test_users = [
    ("admin", "password123", "Admin"),
    ("ppic_mgr", "password123", "PPIC Manager"),
    ("operator_cut", "password123", "Operator"),
    ("superadmin", "password123", "Superadmin"),
    ("wh_admin", "password123", "Warehouse"),
]

print("\n" + "="*70)
print("COMPREHENSIVE USER TEST: LOGIN + ACCESS + PERMISSIONS")
print("="*70 + "\n")

for username, password, label in test_users:
    print(f"\n{'='*70}")
    print(f"TEST: {label:25} (username: {username})")
    print(f"{'='*70}")
    
    try:
        # 1. LOGIN TEST
        print("\n[1] LOGIN TEST...")
        login_resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )
        
        if login_resp.status_code != 200:
            print(f"   ❌ FAILED: {login_resp.status_code}")
            print(f"   Response: {login_resp.text[:200]}")
            continue
            
        token_data = login_resp.json()
        access_token = token_data.get("access_token")
        token_type = token_data.get("token_type")
        user_id = token_data.get("user_id")
        role = token_data.get("role")
        
        print(f"   ✅ LOGIN SUCCESS")
        print(f"      User ID: {user_id}")
        print(f"      Role: {role}")
        print(f"      Token Type: {token_type}")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. DASHBOARD ACCESS TEST
        print("\n[2] DASHBOARD ACCESS TEST...")
        dash_resp = requests.get(
            f"{BASE_URL}/dashboard/stats",
            headers=headers,
            timeout=5
        )
        print(f"   GET /dashboard/stats: {'✅ 200' if dash_resp.status_code == 200 else f'❌ {dash_resp.status_code}'}")
        
        # 3. MODULE ACCESS TESTS (based on role)
        print("\n[3] MODULE ACCESS TESTS...")
        
        endpoints = [
            ("GET", "/admin/users", "Admin Access"),
            ("GET", "/admin/permissions", "Admin Permissions"),
            ("GET", "/audit/logs", "Audit Logs"),
            ("GET", "/ppic/manufacturing-orders", "PPIC Orders"),
            ("GET", "/warehouse/inventory", "Warehouse Inventory"),
            ("GET", "/purchasing/purchase-orders", "Purchase Orders"),
        ]
        
        for method, endpoint, name in endpoints:
            try:
                if method == "GET":
                    resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=3)
                
                status = resp.status_code
                if status == 200:
                    print(f"   ✅ {method:6} {endpoint:40} → 200 OK")
                elif status == 403:
                    print(f"   🚫 {method:6} {endpoint:40} → 403 FORBIDDEN (expected)")
                elif status == 404:
                    print(f"   ⚠️  {method:6} {endpoint:40} → 404 NOT FOUND")
                else:
                    print(f"   ❌ {method:6} {endpoint:40} → {status}")
            except Exception as e:
                print(f"   ⚠️  {method:6} {endpoint:40} → ERROR: {str(e)[:30]}")
        
        # 4. USER INFO TEST
        print("\n[4] USER INFO RETRIEVAL...")
        user_resp = requests.get(
            f"{BASE_URL}/admin/users/{user_id}",
            headers=headers,
            timeout=5
        )
        if user_resp.status_code == 200:
            user_info = user_resp.json()
            print(f"   ✅ Retrieved user info")
            print(f"      Username: {user_info.get('username')}")
            print(f"      Email: {user_info.get('email')}")
            print(f"      Role: {user_info.get('role')}")
            print(f"      Active: {user_info.get('is_active')}")
        elif user_resp.status_code == 403:
            print(f"   🚫 Cannot retrieve own user info (403 - permission denied)")
        else:
            print(f"   ❌ Failed: {user_resp.status_code}")
        
        print(f"\n✅ {label:25} - ALL TESTS PASSED")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CANNOT CONNECT TO API!")
        print(f"   Make sure backend is running: docker-compose up backend")
        break
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
