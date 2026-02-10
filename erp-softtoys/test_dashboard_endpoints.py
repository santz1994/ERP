"""
Test script to diagnose dashboard API endpoint issues
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test credentials
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

def test_endpoint(endpoint, token=None):
    """Test an endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    print(f"\n{'='*80}")
    print(f"Testing: GET {url}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Length: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
                print(f"Response Preview: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for undefined/None
                if data is None:
                    print("⚠️  WARNING: Response is None!")
                elif isinstance(data, list) and len(data) == 0:
                    print("⚠️  WARNING: Response is empty list!")
                    
                return True, data
            except json.JSONDecodeError as e:
                print(f"❌ ERROR: Cannot decode JSON: {e}")
                print(f"Raw response: {response.text[:200]}")
                return False, None
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Connection refused - Backend server is NOT running!")
        return False, None
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timeout!")
        return False, None
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False, None

def main():
    print("="*80)
    print("DASHBOARD API ENDPOINTS DIAGNOSTIC TEST")
    print("="*80)
    
    # Step 1: Check health
    print("\n📊 STEP 1: Check Backend Health")
    success, _ = test_endpoint("/health")
    
    if not success:
        print("\n❌ CRITICAL: Backend server is not accessible!")
        print("Please start the backend server with: python -m uvicorn app.main:app --reload")
        return
    
    # Step 2: Login
    print("\n📊 STEP 2: Login")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=LOGIN_DATA,
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Login successful! Token: {token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 3: Test API endpoints
    print("\n📊 STEP 3: Test API Endpoints")
    
    endpoints = [
        "/api/v1/ppic/manufacturing-orders",
        "/api/v1/ppic/manufacturing-orders?status=IN_PROGRESS",
        "/api/v1/material-allocation/shortages",
        "/api/v1/work-orders",
        "/api/v1/work-orders?department=ALL&state=ALL",
    ]
    
    results = {}
    for endpoint in endpoints:
        success, data = test_endpoint(endpoint, token)
        results[endpoint] = {"success": success, "data": data}
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for endpoint, result in results.items():
        status = "✅ OK" if result["success"] else "❌ FAIL"
        data_type = type(result["data"]).__name__ if result["data"] is not None else "None"
        length = len(result["data"]) if isinstance(result["data"], (list, dict)) else "N/A"
        print(f"{status} {endpoint}")
        print(f"    Type: {data_type}, Length: {length}")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    failed_endpoints = [ep for ep, res in results.items() if not res["success"]]
    
    if failed_endpoints:
        print("❌ Failed endpoints need attention:")
        for ep in failed_endpoints:
            print(f"  - {ep}")
        print("\nPossible fixes:")
        print("  1. Ensure backend server is running")
        print("  2. Check database connection")
        print("  3. Verify authentication token")
        print("  4. Check for missing data in database")
    else:
        print("✅ All endpoints working!")
        print("\nIf frontend still shows errors:")
        print("  1. Check CORS configuration")
        print("  2. Verify frontend API client configuration")
        print("  3. Check React Query error handling")
        print("  4. Review browser console for network errors")

if __name__ == "__main__":
    main()
