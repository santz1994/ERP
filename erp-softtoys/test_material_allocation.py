"""
Test Material Allocation Endpoint
"""
import requests
import json

url = "http://localhost:8000/api/v1/material-allocation/shortages"
headers = {
    "Accept": "application/json",
    "Origin": "http://localhost:5173"
}

print("🔍 Testing Material Allocation Shortages Endpoint...")
print(f"URL: {url}\n")

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Success!")
        data = response.json()
        print(f"Response length: {len(str(data))} characters")
        print(f"Response preview: {str(data)[:300]}")
    else:
        print(f"❌ Error {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"💥 Exception: {type(e).__name__}: {str(e)}")
