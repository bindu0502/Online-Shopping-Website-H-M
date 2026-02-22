"""
Test script for Cart API.

Tests cart viewing, adding items, removing items, and clearing cart.
Requires authentication.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_cart_api():
    """Test the cart API endpoints."""
    print("=" * 60)
    print("CART API TEST")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    # Wait for server to be ready
    time.sleep(1)
    
    try:
        # Setup: Create user and login
        print("Setup: Creating test user and logging in...")
        
        # Try to signup (may already exist)
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": "carttest@example.com",
                "password": "testpass123",
                "name": "Cart Test User"
            }
        )
        
        if signup_response.status_code == 201:
            print("   ✓ User created")
        elif signup_response.status_code == 400:
            print("   ℹ User already exists (OK)")
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "carttest@example.com",
                "password": "testpass123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"   ✗ Login failed: {login_response.json()}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   ✓ Logged in successfully")
        print()
        
        # Get products to add to cart
        products_response = requests.get(f"{BASE_URL}/products")
        products = products_response.json()
        
        if not products:
            print("   ⚠ No products available for testing")
            return
        
        test_article_id = products[0]["article_id"]
        print(f"   Using test product: {products[0]['name']} ({test_article_id})")
        print()
        
        # Test 1: Clear cart first (to start fresh)
        print("1. Testing POST /cart/clear...")
        clear_response = requests.post(f"{BASE_URL}/cart/clear", headers=headers)
        print(f"   Status: {clear_response.status_code}")
        if clear_response.status_code == 200:
            result = clear_response.json()
            print(f"   ✓ {result['message']}: {result['items_removed']} items")
        print()
        
        # Test 2: View empty cart
        print("2. Testing GET /cart (empty)...")
        cart_response = requests.get(f"{BASE_URL}/cart", headers=headers)
        print(f"   Status: {cart_response.status_code}")
        if cart_response.status_code == 200:
            cart = cart_response.json()
            print(f"   ✓ Cart has {len(cart)} items")
        print()
        
        # Test 3: Add item to cart
        print("3. Testing POST /cart/add...")
        add_response = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers,
            json={"article_id": test_article_id, "qty": 2}
        )
        print(f"   Status: {add_response.status_code}")
        if add_response.status_code == 200:
            result = add_response.json()
            print(f"   ✓ {result['message']}")
            print(f"     Cart item ID: {result['cart_item_id']}")
            print(f"     Quantity: {result['qty']}")
        print()
        
        # Test 4: View cart with items
        print("4. Testing GET /cart (with items)...")
        cart_response = requests.get(f"{BASE_URL}/cart", headers=headers)
        print(f"   Status: {cart_response.status_code}")
        if cart_response.status_code == 200:
            cart = cart_response.json()
            print(f"   ✓ Cart has {len(cart)} items")
            if cart:
                item = cart[0]
                print(f"     Product: {item['product_name']}")
                print(f"     Price: ${item['price']}")
                print(f"     Quantity: {item['qty']}")
                print(f"     Subtotal: ${item['price'] * item['qty']:.2f}")
        print()
        
        # Test 5: Add same item again (should increase quantity)
        print("5. Testing POST /cart/add (same item)...")
        add_again_response = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers,
            json={"article_id": test_article_id, "qty": 1}
        )
        print(f"   Status: {add_again_response.status_code}")
        if add_again_response.status_code == 200:
            result = add_again_response.json()
            print(f"   ✓ {result['message']}")
            print(f"     New quantity: {result['qty']}")
        print()
        
        # Test 6: Add non-existent product (should fail)
        print("6. Testing POST /cart/add (non-existent product)...")
        invalid_add_response = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers,
            json={"article_id": "nonexistent123", "qty": 1}
        )
        print(f"   Status: {invalid_add_response.status_code}")
        if invalid_add_response.status_code == 404:
            print(f"   ✓ Correctly rejected: {invalid_add_response.json()['detail']}")
        print()
        
        # Test 7: Remove item from cart
        print(f"7. Testing POST /cart/remove/{test_article_id}...")
        remove_response = requests.post(
            f"{BASE_URL}/cart/remove/{test_article_id}",
            headers=headers
        )
        print(f"   Status: {remove_response.status_code}")
        if remove_response.status_code == 200:
            result = remove_response.json()
            print(f"   ✓ {result['message']}")
        print()
        
        # Test 8: Try to remove item not in cart (should fail)
        print("8. Testing POST /cart/remove (item not in cart)...")
        invalid_remove_response = requests.post(
            f"{BASE_URL}/cart/remove/notincart123",
            headers=headers
        )
        print(f"   Status: {invalid_remove_response.status_code}")
        if invalid_remove_response.status_code == 404:
            print(f"   ✓ Correctly rejected: {invalid_remove_response.json()['detail']}")
        print()
        
        # Test 9: Test without authentication (should fail)
        print("9. Testing GET /cart without authentication...")
        no_auth_response = requests.get(f"{BASE_URL}/cart")
        print(f"   Status: {no_auth_response.status_code}")
        if no_auth_response.status_code == 401:
            print(f"   ✓ Correctly requires authentication")
        print()
        
        print("=" * 60)
        print("✓ ALL CART API TESTS COMPLETED")
        print("=" * 60)
        print()
        print("You can now:")
        print("  - Open http://localhost:8000/docs to test cart endpoints")
        print("  - Use the cart API in your frontend application")
        
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to server")
        print("Make sure the server is running:")
        print("  python main.py")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_cart_api()
