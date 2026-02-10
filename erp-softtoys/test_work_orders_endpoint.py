"""
Test Work Orders Endpoint - Debug 500 Error
"""
import requests
import json

# Test the endpoint
url = "http://localhost:8000/api/v1/work-orders/"
headers = {
    "Accept": "application/json",
    "Origin": "http://localhost:5173"
}

print("🔍 Testing Work Orders Endpoint...")
print(f"URL: {url}\n")

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ Success!")
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
    else:
        print(f"\n❌ Error {response.status_code}")
        print(f"Response Text: {response.text}")
        
except Exception as e:
    print(f"\n💥 Exception: {type(e).__name__}: {str(e)}")
