"""Test login functionality"""
import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
payload = {
    "username": "admin",
    "password": "admin123"
}

print("🔐 Testing login...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\n📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login SUCCESS!")
        print(f"Token: {data['access_token'][:50]}...")
        print(f"User: {data['user']['username']}")
        print(f"Role: {data['user']['role']}")
    else:
        print(f"❌ Login FAILED!")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
