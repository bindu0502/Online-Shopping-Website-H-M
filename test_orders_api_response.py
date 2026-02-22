"""Test what the orders API actually returns."""
import requests
import json

# Login first
print("Logging in...")
login_response = requests.post(
    'http://localhost:8000/auth/login',
    json={'email': 'test@example.com', 'password': 'password123'}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    # Try another user
    login_response = requests.post(
        'http://localhost:8000/auth/login',
        json={'email': 'livetest@example.com', 'password': 'password123'}
    )

if login_response.status_code != 200:
    print("Could not login with any test user")
    exit(1)

token = login_response.json()['access_token']
print(f"✓ Logged in, token: {token[:30]}...")

# Get orders
print("\nFetching orders...")
orders_response = requests.get(
    'http://localhost:8000/orders/',
    headers={'Authorization': f'Bearer {token}'}
)

print(f"Status: {orders_response.status_code}")

if orders_response.status_code == 200:
    data = orders_response.json()
    print(f"\nOrders count: {len(data['orders'])}")
    
    if data['orders']:
        first_order = data['orders'][0]
        print(f"\nFirst Order:")
        print(f"  Order ID: {first_order['order_id']}")
        print(f"  Total: ${first_order['total_amount']}")
        print(f"  Items: {len(first_order['items'])}")
        
        if first_order['items']:
            print(f"\n  First Item:")
            item = first_order['items'][0]
            print(f"    Article ID: {item['article_id']}")
            print(f"    Name: {item.get('name', 'N/A')}")
            print(f"    Image Path: {item.get('image_path', 'N/A')}")
            print(f"    Has image_path key: {'image_path' in item}")
            print(f"    Image path value: {repr(item.get('image_path'))}")
            
            print(f"\n  Full item data:")
            print(json.dumps(item, indent=2))
else:
    print(f"Error: {orders_response.text}")
