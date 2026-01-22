#!/usr/bin/env python3
"""
Real Integration Test - Tests ERP System End-to-End
Does ACTUAL testing, not guessing!
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:5173"
TEST_USER = "developer"
TEST_PASSWORD = "password123"

# Colors for output
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name, result, details=""):
    status = f"{Color.GREEN}✅ PASS{Color.RESET}" if result else f"{Color.RED}❌ FAIL{Color.RESET}"
    print(f"{status} {name}")
    if details:
        print(f"     {details}")

def test_backend_connection():
    """Test 1: Backend API is running"""
    print(f"\n{Color.YELLOW}TEST SUITE 1: Backend Connectivity{Color.RESET}")
    print("─" * 50)
    
    try:
        response = requests.options(f"{API_URL}/auth/login", timeout=5)
        print_test("Backend API Connection", response.status_code in [200, 405], 
                  f"Status: {response.status_code}")
        return True
    except Exception as e:
        print_test("Backend API Connection", False, f"Error: {str(e)}")
        return False

def test_login():
    """Test 2: Login endpoint works"""
    print(f"\n{Color.YELLOW}TEST SUITE 2: Authentication{Color.RESET}")
    print("─" * 50)
    
    try:
        payload = {
            "username": TEST_USER,
            "password": TEST_PASSWORD
        }
        response = requests.post(
            f"{API_URL}/auth/login",
            json=payload,
            timeout=5
        )
        
        if response.status_code != 200:
            print_test("Login Request", False, f"Status: {response.status_code}, Response: {response.text}")
            return None, None
        
        data = response.json()
        
        # Verify response has required fields
        has_token = "access_token" in data
        has_user = "user" in data
        
        print_test("Login Request", response.status_code == 200, 
                  f"User: {data.get('user', {}).get('username')} ({data.get('user', {}).get('role')})")
        print_test("Access Token", has_token, 
                  f"Length: {len(data.get('access_token', ''))}")
        print_test("User Data", has_user, 
                  f"Fields: {', '.join(data.get('user', {}).keys())}")
        
        if has_token and has_user:
            return data["access_token"], data["user"]
        return None, None
        
    except Exception as e:
        print_test("Login Request", False, f"Exception: {str(e)}")
        return None, None

def test_auth_me(token):
    """Test 3: /auth/me endpoint with token"""
    print(f"\n{Color.YELLOW}TEST SUITE 3: Token Validation{Color.RESET}")
    print("─" * 50)
    
    if not token:
        print_test("/auth/me", False, "No token from login")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/auth/me",
            headers=headers,
            timeout=5
        )
        
        success = response.status_code == 200
        print_test("/auth/me Endpoint", success, 
                  f"Status: {response.status_code}")
        
        if success:
            user = response.json()
            print_test("User Verification", True, 
                      f"Username: {user.get('username')}")
        
        return success
        
    except Exception as e:
        print_test("/auth/me Endpoint", False, f"Exception: {str(e)}")
        return False

def test_without_token():
    """Test 4: /auth/me without token should fail with 401"""
    print(f"\n{Color.YELLOW}TEST SUITE 4: Security Tests{Color.RESET}")
    print("─" * 50)
    
    try:
        response = requests.get(
            f"{API_URL}/auth/me",
            timeout=5
        )
        
        # Should return 401
        success = response.status_code == 401
        print_test("No Auth Protection", success, 
                  f"Status: {response.status_code} (expected 401)")
        return success
        
    except Exception as e:
        print_test("No Auth Protection", False, f"Exception: {str(e)}")
        return False

def test_invalid_token():
    """Test 5: Invalid token should fail"""
    print(f"\n{Color.YELLOW}TEST SUITE 5: Invalid Token Handling{Color.RESET}")
    print("─" * 50)
    
    try:
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = requests.get(
            f"{API_URL}/auth/me",
            headers=headers,
            timeout=5
        )
        
        success = response.status_code == 401
        print_test("Invalid Token Rejection", success, 
                  f"Status: {response.status_code} (expected 401)")
        return success
        
    except Exception as e:
        print_test("Invalid Token Rejection", False, f"Exception: {str(e)}")
        return False

def test_frontend_server():
    """Test 6: Frontend server is running"""
    print(f"\n{Color.YELLOW}TEST SUITE 6: Frontend Server{Color.RESET}")
    print("─" * 50)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        success = response.status_code == 200
        print_test("Frontend Server", success, 
                  f"URL: {FRONTEND_URL}")
        return success
    except Exception as e:
        print_test("Frontend Server", False, f"Error: {str(e)}")
        return False

def main():
    print(f"\n{'='*60}")
    print(f"{Color.BLUE}ERP SYSTEM - REAL INTEGRATION TEST{Color.RESET}")
    print(f"{'='*60}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Test User: {TEST_USER} / {TEST_PASSWORD}")
    
    results = []
    
    # Run all tests
    results.append(("Backend Connection", test_backend_connection()))
    
    token, user = test_login()
    results.append(("Login Success", token is not None))
    
    if token:
        results.append(("Token Validation", test_auth_me(token)))
    
    results.append(("No Auth Protection", test_without_token()))
    results.append(("Invalid Token Handling", test_invalid_token()))
    results.append(("Frontend Server", test_frontend_server()))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{Color.BLUE}TEST SUMMARY{Color.RESET}")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Color.GREEN}✅{Color.RESET}" if result else f"{Color.RED}❌{Color.RESET}"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {Color.GREEN}{passed}/{total}{Color.RESET}")
    
    if passed == total:
        print(f"\n{Color.GREEN}✅ ALL TESTS PASSED!{Color.RESET}")
        print(f"\n{Color.YELLOW}Next Steps:{Color.RESET}")
        print(f"1. Open {FRONTEND_URL} in browser")
        print(f"2. Login with: {TEST_USER} / {TEST_PASSWORD}")
        print(f"3. Check if navbar is visible")
        print(f"4. Press F5 to refresh")
        print(f"5. Verify you stay logged in (no redirect to login)")
        return 0
    else:
        print(f"\n{Color.RED}❌ SOME TESTS FAILED{Color.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
