"""
Test script for authentication API.

Tests signup, login, and protected endpoint functionality.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api_auth import router as auth_router
from src.db import init_db, SessionLocal, User


# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(title="Test API")
app.include_router(auth_router)

# Create test client
client = TestClient(app)


def cleanup_test_user(email: str):
    """Remove test user from database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_auth_flow():
    """Test complete authentication flow."""
    print("=" * 60)
    print("AUTHENTICATION API TEST")
    print("=" * 60)
    
    test_email = "test_auth@example.com"
    test_password = "secure_password_123"
    test_name = "Test Auth User"
    
    # Cleanup any existing test user
    cleanup_test_user(test_email)
    
    # Test 1: Signup
    print("\n1. Testing signup...")
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": test_email,
            "password": test_password,
            "name": test_name
        }
    )
    
    assert signup_response.status_code == 201, f"Signup failed: {signup_response.json()}"
    signup_data = signup_response.json()
    assert signup_data["email"] == test_email
    assert signup_data["name"] == test_name
    assert "id" in signup_data
    print(f"   ✓ User created: {signup_data}")
    
    # Test 2: Duplicate signup (should fail)
    print("\n2. Testing duplicate signup...")
    duplicate_response = client.post(
        "/auth/signup",
        json={
            "email": test_email,
            "password": "another_password",
            "name": "Another Name"
        }
    )
    
    assert duplicate_response.status_code == 400, "Duplicate signup should fail"
    print(f"   ✓ Duplicate signup rejected: {duplicate_response.json()['detail']}")
    
    # Test 3: Login with correct credentials
    print("\n3. Testing login with correct credentials...")
    login_response = client.post(
        "/auth/login",
        json={
            "email": test_email,
            "password": test_password
        }
    )
    
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    access_token = login_data["access_token"]
    print(f"   ✓ Login successful")
    print(f"   Token: {access_token[:50]}...")
    
    # Test 4: Login with wrong password
    print("\n4. Testing login with wrong password...")
    wrong_password_response = client.post(
        "/auth/login",
        json={
            "email": test_email,
            "password": "wrong_password"
        }
    )
    
    assert wrong_password_response.status_code == 401, "Wrong password should fail"
    print(f"   ✓ Wrong password rejected: {wrong_password_response.json()['detail']}")
    
    # Test 5: Login with non-existent email
    print("\n5. Testing login with non-existent email...")
    nonexistent_response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "any_password"
        }
    )
    
    assert nonexistent_response.status_code == 401, "Non-existent email should fail"
    print(f"   ✓ Non-existent email rejected: {nonexistent_response.json()['detail']}")
    
    # Test 6: Access protected endpoint with valid token
    print("\n6. Testing protected endpoint with valid token...")
    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert me_response.status_code == 200, f"Protected endpoint failed: {me_response.json()}"
    me_data = me_response.json()
    assert me_data["email"] == test_email
    assert me_data["name"] == test_name
    print(f"   ✓ User info retrieved: {me_data}")
    
    # Test 7: Access protected endpoint without token
    print("\n7. Testing protected endpoint without token...")
    no_token_response = client.get("/auth/me")
    
    assert no_token_response.status_code == 401, "Should require authentication"
    print(f"   ✓ Access denied without token")
    
    # Test 8: Access protected endpoint with invalid token
    print("\n8. Testing protected endpoint with invalid token...")
    invalid_token_response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token_12345"}
    )
    
    assert invalid_token_response.status_code == 401, "Invalid token should fail"
    print(f"   ✓ Invalid token rejected: {invalid_token_response.json()['detail']}")
    
    # Cleanup
    print("\n9. Cleaning up test user...")
    cleanup_test_user(test_email)
    print("   ✓ Test user removed")
    
    print("\n" + "=" * 60)
    print("✓ ALL AUTHENTICATION TESTS PASSED")
    print("=" * 60)


if __name__ == '__main__':
    test_auth_flow()
