import requests
import traceback

# Login first
login_url = "http://localhost:8000/api/v1/auth/login"
login_data = {"username": "admin", "password": "admin123"}
headers = {"Content-Type": "application/json"}

print("🔐 Logging in...")
login_response = requests.post(login_url, json=login_data, headers=headers)
token = login_response.json()["access_token"]
print(f"✅ Token: {token[:30]}...")

# Test endpoint
auth_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

test_url = "http://localhost:8000/api/v1/ppic/manufacturing-orders?status=IN_PROGRESS"
print(f"\n📡 Testing: {test_url}")

try:
    response = requests.get(test_url, headers=auth_headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("\n❌ ERROR!")
        try:
            print("JSON Error:", response.json())
        except:
            print("Raw Error:", response.text)
except Exception as e:
    print(f"❌ Exception: {e}")
    traceback.print_exc()
