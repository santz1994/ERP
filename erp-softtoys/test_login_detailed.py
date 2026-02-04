"""Test auth endpoint dengan detail error"""
import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
payload = {
    "username": "admin",
    "password": "admin123"
}

print("🔐 Testing login with detailed error...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login SUCCESS!")
        print(f"Token (first 50 chars): {data['access_token'][:50]}...")
        print(f"User: {data['user']}")
    else:
        print(f"❌ Login FAILED!")
        print(f"Response Text: {response.text}")
        print(f"Response Content: {response.content}")
        
        # Try to parse as JSON error
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
        except:
            pass
            
except requests.exceptions.Timeout:
    print("❌ Request timeout - backend might be slow")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {str(e)}")
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    import traceback
    traceback.print_exc()
