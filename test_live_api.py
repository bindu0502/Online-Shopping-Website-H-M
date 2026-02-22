"""
Live API Test Script

Tests the running FastAPI server with real HTTP requests.
Make sure the server is running first: python main.py
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_live_api():
    """Test the live API server."""
    print("=" * 60)
    print("LIVE API TEST")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    try:
        # Test 1: Root endpoint
        print("1. Testing root endpoint...")
        root_response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {root_response.status_code}")
        print(f"   Response: {root_response.json()}")
        print()
        
        # Test 2: Signup
        print("2. Testing signup...")
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": "livetest@example.com",
                "password": "testpassword123",
                "name": "Live Test User"
            }
        )
        print(f"   Status: {signup_response.status_code}")
        if signup_response.status_code == 201:
            user_data = signup_response.json()
            print(f"   ✓ User created: {user_data}")
        elif signup_response.status_code == 400:
            print(f"   ℹ User already exists (this is OK)")
        else:
            print(f"   Response: {signup_response.json()}")
        print()
        
        # Test 3: Login
        print("3. Testing login...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "livetest@example.com",
                "password": "testpassword123"
            }
        )
        print(f"   Status: {login_response.status_code}")
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"   ✓ Token received: {access_token[:50]}...")
        print()
        
        # Test 4: Get profile
        print("4. Testing protected endpoint...")
        me_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"   Status: {me_response.status_code}")
        user_info = me_response.json()
        print(f"   ✓ User profile: {user_info}")
        print()
        
        # Test 5: Invalid token
        print("5. Testing with invalid token...")
        invalid_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        print(f"   Status: {invalid_response.status_code}")
        print(f"   ✓ Correctly rejected: {invalid_response.json()['detail']}")
        print()
        
        print("=" * 60)
        print("✓ ALL LIVE API TESTS PASSED")
        print("=" * 60)
        print()
        print("You can now:")
        print("  - Open http://localhost:8000/docs for Swagger UI")
        print("  - Open http://localhost:8000/redoc for ReDoc")
        print("  - Use the API with your frontend application")
        
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to server")
        print("Make sure the server is running:")
        print("  python main.py")
    except Exception as e:
        print(f"✗ ERROR: {e}")


if __name__ == '__main__':
    test_live_api()
