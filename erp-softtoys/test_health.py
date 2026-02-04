"""Test health endpoint"""
import requests

url = "http://localhost:8000/health"
print("🏥 Testing health endpoint...")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Health check: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
