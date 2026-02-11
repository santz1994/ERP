"""
Quick API endpoint tester for Session 51
Tests new PO Reference System endpoints
"""

import sys
sys.path.insert(0, 'erp-softtoys')

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"

def login(username="admin", password="admin123"):
    """Login and get JWT token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful: {username}")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_available_po_kain(token):
    """Test GET /purchasing/available-po-kain"""
    print("\n" + "="*60)
    print("TEST 1: GET /purchasing/available-po-kain")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/purchasing/available-po-kain", headers=headers)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        print(f"✅ Found {len(data)} available PO KAIN")
        return True
    else:
        print(f"❌ Error: {data}")
        return False

def test_articles(token):
    """Test GET /purchasing/articles"""
    print("\n" + "="*60)
    print("TEST 2: GET /purchasing/articles")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/purchasing/articles", headers=headers)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"✅ Found {len(data)} articles")
        if len(data) > 0:
            print(f"Sample: {data[0]}")
        return True
    else:
        print(f"❌ Error: {data}")
        return False

def test_bom_explosion(token, article_code="40551542", quantity=1000):
    """Test POST /purchasing/bom/explosion"""
    print("\n" + "="*60)
    print("TEST 3: POST /purchasing/bom/explosion")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "article_code": article_code,
        "quantity": quantity
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    response = requests.post(
        f"{BASE_URL}/purchasing/bom/explosion",
        headers=headers,
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        materials_count = len(data.get("materials", []))
        print(f"✅ BOM Explosion successful: {materials_count} materials")
        if materials_count > 0:
            print(f"Sample material: {data['materials'][0]}")
        else:
            print(f"⚠️ No materials (expected if BOM not imported)")
            print(f"Message: {data.get('message', 'N/A')}")
        return True
    else:
        print(f"❌ Error: {data}")
        return False

def main():
    print("🚀 SESSION 51 - API ENDPOINT TESTING")
    print("="*60)
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without token")
        return
    
    # Step 2: Test endpoints
    results = {
        "available-po-kain": test_available_po_kain(token),
        "articles": test_articles(token),
        "bom-explosion": test_bom_explosion(token)
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    for endpoint, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {endpoint}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend ready for frontend integration.")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
