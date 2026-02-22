"""Test For You API with real login."""
import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("FOR YOU API TEST WITH LOGIN")
print("=" * 60)

# Step 1: Login
print("\n1. Logging in...")
try:
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        },
        timeout=5
    )
    
    if login_response.status_code != 200:
        print(f"✗ Login failed: {login_response.text}")
        print("\nTry creating a user first:")
        print("  python -c \"from src.db import *; db=SessionLocal(); u=User(email='test@example.com', password_hash=hash_password('password123'), name='Test'); db.add(u); db.commit(); print('User created')\"")
        exit(1)
    
    token = login_response.json()['access_token']
    print(f"✓ Login successful")
    print(f"  Token: {token[:50]}...")
    
except requests.exceptions.ConnectionError:
    print("\n✗ Cannot connect to API server")
    print("  Start the server with: python main.py")
    exit(1)

# Step 2: Test For You endpoint
print("\n2. Fetching For You recommendations...")
try:
    foryou_response = requests.get(
        f"{BASE_URL}/foryou",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    print(f"  Status: {foryou_response.status_code}")
    
    if foryou_response.status_code == 200:
        data = foryou_response.json()
        print(f"\n✓ SUCCESS!")
        print(f"  User ID: {data['user_id']}")
        print(f"  Activity Products: {data['activity_products_count']}")
        print(f"  Recommendations: {data['count']}")
        
        if data['recommendations']:
            print(f"\n  Sample recommendations:")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"    {i}. {rec['name']}")
                print(f"       ${rec['price']:.2f} - {rec['primary_color']}")
        else:
            print("\n  ℹ No recommendations (user has no activity)")
            print("  Add items to cart/wishlist to get recommendations")
    else:
        print(f"\n✗ Error: {foryou_response.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 60)
