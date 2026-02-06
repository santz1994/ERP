"""Quick single login test to see debug output"""

import requests
import json

url = "http://127.0.0.1:8000/api/v1/auth/login"
payload = {"username": "admin", "password": "admin123"}

print("Testing admin login...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload)}\n")

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ LOGIN SUCCESS!")
    else:
        print(f"\n❌ LOGIN FAILED: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
