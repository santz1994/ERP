"""Test via Swagger UI API docs"""
import requests

# Test if Swagger UI accessible
swagger_url = "http://localhost:8000/docs"
print(f"🔍 Checking Swagger UI: {swagger_url}")

try:
    response = requests.get(swagger_url, timeout=5)
    if response.status_code == 200:
        print("✅ Swagger UI accessible!")
        print("   Please open http://localhost:8000/docs in browser")
        print("   Try login there to see detailed error message")
    else:
        print(f"❌ Swagger UI not accessible: {response.status_code}")
except Exception as e:
    print(f"❌ Error accessing Swagger: {str(e)}")

# Test OpenAPI spec
print("\n🔍 Checking OpenAPI spec...")
openapi_url = "http://localhost:8000/openapi.json"
try:
    response = requests.get(openapi_url, timeout=5)
    if response.status_code == 200:
        print("✅ OpenAPI spec accessible!")
        spec = response.json()
        if '/api/v1/auth/login' in spec.get('paths', {}):
            print("✅ /api/v1/auth/login endpoint defined")
            login_spec = spec['paths']['/api/v1/auth/login']
            print(f"   Methods: {list(login_spec.keys())}")
        else:
            print("❌ /api/v1/auth/login not found in OpenAPI spec")
    else:
        print(f"❌ OpenAPI spec error: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
