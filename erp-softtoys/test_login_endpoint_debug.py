"""Test login endpoint with detailed debugging"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

print("=" * 80)
print("🧪 TESTING LOGIN ENDPOINT")
print("=" * 80)

# Test 1: Simple admin login
print("\n1. Testing admin login:")
print(f"   URL: {LOGIN_URL}")

payload = {
    "username": "admin",
    "password": "admin123"
}

print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        LOGIN_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print(f"\n   Response Body:")
    
    try:
        response_json = response.json()
        print(f"   {json.dumps(response_json, indent=2)}")
    except:
        print(f"   {response.text}")
        
    if response.status_code == 200:
        print("\n   ✅ LOGIN SUCCESS!")
        data = response.json()
        print(f"   Token: {data.get('access_token', '')[:50]}...")
        print(f"   User: {data.get('user', {}).get('username')}")
        print(f"   Role: {data.get('user', {}).get('role')}")
    else:
        print(f"\n   ❌ LOGIN FAILED: HTTP {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ Connection Error - Backend not running?")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Try with different username formats
print("\n\n2. Testing different payload formats:")

test_payloads = [
    {"username": "admin", "password": "admin123"},
    {"username": "developer", "password": "admin123"},
]

for i, test_payload in enumerate(test_payloads, 1):
    print(f"\n   Test {i}: {test_payload['username']}")
    try:
        response = requests.post(LOGIN_URL, json=test_payload, timeout=5)
        if response.status_code == 200:
            print(f"      ✅ Success")
        else:
            print(f"      ❌ Failed: HTTP {response.status_code}")
            error_detail = response.json().get("detail", "No detail")
            print(f"      Detail: {error_detail[:100]}")
    except Exception as e:
        print(f"      ❌ Error: {str(e)[:100]}")

print("\n" + "=" * 80)
