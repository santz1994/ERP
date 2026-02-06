"""Test login for all users in database"""
import requests
import json
from app.core.database import SessionLocal
from app.core.models.users import User

db = SessionLocal()

# Get all users
users = db.query(User).all()

print(f"🔍 Found {len(users)} users in database\n")
print("="*80)

url = "http://localhost:8000/api/v1/auth/login"

# Test each user with common passwords
test_passwords = ["admin123", "password", "123456", "operator123"]

for user in users:
    print(f"\n👤 Testing user: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role.value}")
    print(f"   Active: {user.is_active}")
    
    login_success = False
    
    for password in test_passwords:
        payload = {
            "username": user.username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ LOGIN SUCCESS with password: '{password}'")
                data = response.json()
                print(f"   🎫 Access Token: {data['access_token'][:50]}...")
                login_success = True
                break
            elif response.status_code == 401:
                continue  # Wrong password, try next
            elif response.status_code == 500:
                print(f"   ❌ SERVER ERROR 500")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=6)}")
                except:
                    print(f"   Response: {response.text}")
                login_success = False
                break
            else:
                print(f"   ⚠️ Status {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error - Backend not running?")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
            break
    
    if not login_success and user.is_active:
        print(f"   ❌ FAILED - Could not login with any test password")
    
    print("-"*80)

db.close()

print("\n" + "="*80)
print("🏁 Testing complete!")
