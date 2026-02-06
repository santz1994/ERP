"""Test login endpoint directly"""
import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
payload = {
    "username": "admin",
    "password": "admin123"
}

print(f"🔄 Testing login endpoint: {url}")
print(f"📦 Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*60)

try:
    response = requests.post(url, json=payload)
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📝 Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"\n✅ SUCCESS!")
        print(f"📦 Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"\n❌ FAILED!")
        print(f"📦 Response: {response.text}")
        
        # Try to parse as JSON
        try:
            error_data = response.json()
            print(f"\n🔍 Error Detail: {json.dumps(error_data, indent=2)}")
        except:
            pass
            
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection Error: {e}")
    print("   Is the backend running on port 8000?")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
