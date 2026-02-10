#!/usr/bin/env python
# Test manufacturing orders endpoint with detailed error capture
import requests
import json

# Get token
print("🔐 Getting auth token...")
login_resp = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_resp.json()["access_token"]
print(f"✅ Token obtained\n")

# Test the endpoint
url = "http://localhost:8000/api/v1/ppic/manufacturing-orders?status=IN_PROGRESS"
headers = {"Authorization": f"Bearer {token}"}

print(f"📡 Testing: {url}\n")
try:
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Headers: {dict(resp.headers)}\n")
    
    # Try to parse response
    try:
        data = resp.json()
        print(f"JSON Response:\n{json.dumps(data, indent=2)}")
    except:
        print(f"Raw Response:\n{resp.text}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
