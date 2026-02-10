"""
Final comprehensive endpoint testing
"""
import requests

endpoints = [
    "/api/v1/work-orders/",
    "/api/v1/material-allocation/shortages",
    "/health",
    "/",
]

base_url = "http://localhost:8000"

print("🔍 Final Endpoint Testing")
print("=" * 60)

all_passed = True

for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, headers={"Origin": "http://localhost:5173"})
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {endpoint}: {response.status_code}")
        if response.status_code != 200:
            all_passed = False
            print(f"      Error: {response.text[:100]}")
    except Exception as e:
        print(f"❌ {endpoint}: Exception - {str(e)[:100]}")
        all_passed = False

print("=" * 60)
if all_passed:
    print("✅ All endpoints passed!")
else:
    print("⚠️  Some endpoints failed")
