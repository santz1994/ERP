import requests

# Login first
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "admin123"}
)

token = login_response.json()["access_token"]

# Test the failing endpoint
print("Testing: /api/v1/ppic/manufacturing-orders?status=IN_PROGRESS")
response = requests.get(
    "http://localhost:8000/api/v1/ppic/manufacturing-orders?status=IN_PROGRESS",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Test the second failing endpoint
print("\n\nTesting: /api/v1/work-orders?department=ALL&state=ALL")
response2 = requests.get(
    "http://localhost:8000/api/v1/work-orders?department=ALL&state=ALL",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status: {response2.status_code}")
print(f"Response: {response2.text}")
