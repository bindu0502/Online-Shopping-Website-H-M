"""Quick test for For You API endpoint."""
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.db import SessionLocal, User

# Get a real user token
db = SessionLocal()
user = db.query(User).first()

if not user:
    print("No users found. Please create a user first.")
    sys.exit(1)

print(f"Testing with user: {user.email}")

# Create a token (simplified - in production use proper JWT)
from src.api_auth import create_access_token
token = create_access_token(user.id)

print(f"Token: {token[:50]}...")

# Test the API
try:
    response = requests.get(
        'http://localhost:8000/foryou',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success!")
        print(f"  Recommendations: {data.get('count', 0)}")
        print(f"  Activity Products: {data.get('activity_products_count', 0)}")
        
        if data.get('recommendations'):
            print(f"\n  First recommendation:")
            rec = data['recommendations'][0]
            print(f"    - {rec['name']}")
            print(f"    - ${rec['price']}")
    else:
        print(f"✗ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n✗ Cannot connect to API. Is the server running?")
    print("  Start it with: python main.py")
except Exception as e:
    print(f"\n✗ Error: {e}")
finally:
    db.close()
