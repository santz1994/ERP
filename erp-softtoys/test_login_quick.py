"""Quick login test for 15 management users after password fix"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from typing import Dict, List

BASE_URL = "http://127.0.0.1:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

# 15 Management-Level Users (after operator cleanup)
USERS = [
    # Tier 1 - System Access
    "developer", "superadmin", "admin",
    # Tier 2 - Management
    "manager", "finance_mgr", "ppic_mgr", "purchasing_head",
    # Tier 3 - Department Admin
    "ppic_admin", "wh_admin",
    # Tier 4 - Supervisors
    "spv_cutting", "spv_sewing", "spv_finishing",
    # Tier 5 - Specialists
    "qc_lab", "purchasing"
]

# Default password after fix
DEFAULT_PASSWORD = "admin123"

def test_login(username: str, password: str) -> Dict:
    """Test login for a user"""
    try:
        response = requests.post(
            LOGIN_URL,
            json={"username": username, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "username": username,
                "token": data.get("access_token", "")[:50] + "...",
                "role": data.get("user", {}).get("role", "Unknown")
            }
        else:
            return {
                "success": False,
                "username": username,
                "error": f"HTTP {response.status_code}",
                "detail": response.text[:200]
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "username": username,
            "error": "Connection Error",
            "detail": "Backend not running on port 8000"
        }
    except Exception as e:
        return {
            "success": False,
            "username": username,
            "error": str(e)[:100]
        }

def main():
    """Test all 15 management users"""
    print("=" * 80)
    print("🧪 TESTING LOGIN - 15 MANAGEMENT USERS")
    print("=" * 80)
    print(f"Backend: {BASE_URL}")
    print(f"Password: {DEFAULT_PASSWORD}")
    print()
    
    results: List[Dict] = []
    success_count = 0
    
    for username in USERS:
        result = test_login(username, DEFAULT_PASSWORD)
        results.append(result)
        
        if result["success"]:
            success_count += 1
            print(f"✅ {username:20s} | Role: {result['role']}")
        else:
            print(f"❌ {username:20s} | Error: {result['error']}")
            if "detail" in result and result["detail"]:
                print(f"   └─ Detail: {result['detail'][:100]}")
    
    print()
    print("=" * 80)
    print(f"📊 RESULTS: {success_count}/{len(USERS)} users can login")
    print("=" * 80)
    
    if success_count == len(USERS):
        print("✅ ALL USERS LOGIN SUCCESSFUL - Password fix verified!")
        print()
        print("Next Steps:")
        print("1. ✅ Login blocker RESOLVED")
        print("2. ⏭️  Proceed to PO Reference System implementation")
        print("3. ⏭️  Backend API enhancement (database migration)")
        return 0
    else:
        print(f"⚠️  {len(USERS) - success_count} users failed to login")
        print()
        print("Action Required:")
        print("1. Check backend logs for errors")
        print("2. Verify password hashes in database")
        print("3. Re-run fix_password_hashes.py if needed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
