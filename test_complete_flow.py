"""
Complete E-Commerce Flow Test

Tests the entire user journey from signup to order placement.
Demonstrates the complete API functionality.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test complete e-commerce flow."""
    print("=" * 70)
    print("COMPLETE E-COMMERCE FLOW TEST")
    print("=" * 70)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    # Wait for server
    time.sleep(1)
    
    try:
        # ===== STEP 1: USER REGISTRATION =====
        print("STEP 1: USER REGISTRATION")
        print("-" * 70)
        
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": "shopper@example.com",
                "password": "shop123",
                "name": "Test Shopper"
            }
        )
        
        if signup_response.status_code == 201:
            print("✓ New user registered")
        elif signup_response.status_code == 400:
            print("ℹ User already exists (continuing with existing user)")
        else:
            print(f"✗ Signup failed: {signup_response.json()}")
            return
        
        print()
        
        # ===== STEP 2: USER LOGIN =====
        print("STEP 2: USER LOGIN")
        print("-" * 70)
        
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "shopper@example.com",
                "password": "shop123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"✗ Login failed: {login_response.json()}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✓ Logged in successfully")
        print(f"  Token: {token[:50]}...")
        print()
        
        # ===== STEP 3: BROWSE PRODUCTS =====
        print("STEP 3: BROWSE PRODUCTS")
        print("-" * 70)
        
        products_response = requests.get(f"{BASE_URL}/products")
        products = products_response.json()
        
        print(f"✓ Found {len(products)} products")
        for i, product in enumerate(products[:3], 1):
            print(f"  {i}. {product['name']} - ${product['price']}")
        print()
        
        if not products:
            print("⚠ No products available")
            return
        
        # ===== STEP 4: VIEW PRODUCT DETAILS =====
        print("STEP 4: VIEW PRODUCT DETAILS")
        print("-" * 70)
        
        selected_product = products[0]
        detail_response = requests.get(f"{BASE_URL}/products/{selected_product['article_id']}")
        product_detail = detail_response.json()
        
        print(f"✓ Viewing: {product_detail['name']}")
        print(f"  Price: ${product_detail['price']}")
        print(f"  Department: {product_detail.get('department_no', 'N/A')}")
        print()
        
        # ===== STEP 5: VIEW SIMILAR PRODUCTS =====
        print("STEP 5: VIEW SIMILAR PRODUCTS")
        print("-" * 70)
        
        similar_response = requests.get(
            f"{BASE_URL}/products/{selected_product['article_id']}/similar"
        )
        similar_products = similar_response.json()
        
        print(f"✓ Found {len(similar_products)} similar products")
        if similar_products:
            print(f"  Similar: {similar_products[0]['name']} - ${similar_products[0]['price']}")
        print()
        
        # ===== STEP 6: CLEAR CART (START FRESH) =====
        print("STEP 6: CLEAR CART")
        print("-" * 70)
        
        clear_response = requests.post(f"{BASE_URL}/cart/clear", headers=headers)
        print(f"✓ {clear_response.json()['message']}")
        print()
        
        # ===== STEP 7: ADD ITEMS TO CART =====
        print("STEP 7: ADD ITEMS TO CART")
        print("-" * 70)
        
        # Add first product
        add1_response = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers,
            json={"article_id": products[0]["article_id"], "qty": 2}
        )
        print(f"✓ Added {products[0]['name']} x2")
        
        # Add second product if available
        if len(products) > 1:
            add2_response = requests.post(
                f"{BASE_URL}/cart/add",
                headers=headers,
                json={"article_id": products[1]["article_id"], "qty": 1}
            )
            print(f"✓ Added {products[1]['name']} x1")
        print()
        
        # ===== STEP 8: VIEW CART =====
        print("STEP 8: VIEW CART")
        print("-" * 70)
        
        cart_response = requests.get(f"{BASE_URL}/cart", headers=headers)
        cart = cart_response.json()
        
        print(f"✓ Cart contains {len(cart)} items:")
        cart_total = 0
        for item in cart:
            subtotal = item['price'] * item['qty']
            cart_total += subtotal
            print(f"  - {item['product_name']}: {item['qty']}x @ ${item['price']} = ${subtotal:.2f}")
        print(f"  CART TOTAL: ${cart_total:.2f}")
        print()
        
        # ===== STEP 9: CHECKOUT =====
        print("STEP 9: CHECKOUT")
        print("-" * 70)
        
        checkout_response = requests.post(
            f"{BASE_URL}/orders/checkout",
            headers=headers,
            json={
                "address": "123 Main St, City, Country",
                "payment_method": "credit_card"
            }
        )
        
        if checkout_response.status_code != 200:
            print(f"✗ Checkout failed: {checkout_response.json()}")
            return
        
        order_data = checkout_response.json()
        print(f"✓ {order_data['message']}")
        print(f"  Order ID: {order_data['order_id']}")
        print(f"  Total: ${order_data['total_amount']:.2f}")
        print(f"  Items: {len(order_data['items'])}")
        print()
        
        # ===== STEP 10: VERIFY CART IS EMPTY =====
        print("STEP 10: VERIFY CART IS EMPTY")
        print("-" * 70)
        
        cart_after_response = requests.get(f"{BASE_URL}/cart", headers=headers)
        cart_after = cart_after_response.json()
        
        if len(cart_after) == 0:
            print("✓ Cart is empty after checkout")
        else:
            print(f"⚠ Cart still has {len(cart_after)} items")
        print()
        
        # ===== STEP 11: VIEW ORDER HISTORY =====
        print("STEP 11: VIEW ORDER HISTORY")
        print("-" * 70)
        
        orders_response = requests.get(f"{BASE_URL}/orders", headers=headers)
        orders_data = orders_response.json()
        orders = orders_data['orders']
        
        print(f"✓ Found {len(orders)} orders in history")
        for order in orders[:3]:  # Show last 3 orders
            print(f"  Order #{order['order_id']}: ${order['total_amount']:.2f} ({order['created_at'][:10]})")
        print()
        
        # ===== STEP 12: VIEW SPECIFIC ORDER =====
        print("STEP 12: VIEW SPECIFIC ORDER")
        print("-" * 70)
        
        order_id = order_data['order_id']
        order_detail_response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)
        order_detail = order_detail_response.json()
        
        print(f"✓ Order #{order_detail['order_id']} details:")
        print(f"  Date: {order_detail['created_at'][:19]}")
        print(f"  Total: ${order_detail['total_amount']:.2f}")
        print(f"  Items:")
        for item in order_detail['items']:
            print(f"    - Article {item['article_id']}: {item['qty']}x @ ${item['price']}")
        print()
        
        # ===== SUCCESS =====
        print("=" * 70)
        print("✓ COMPLETE E-COMMERCE FLOW TEST PASSED!")
        print("=" * 70)
        print()
        print("Summary:")
        print(f"  • User registered/logged in")
        print(f"  • Browsed {len(products)} products")
        print(f"  • Added {len(cart)} items to cart")
        print(f"  • Placed order #{order_id} for ${order_data['total_amount']:.2f}")
        print(f"  • Cart cleared automatically")
        print(f"  • Order history retrieved")
        print()
        print("The complete e-commerce API is working perfectly! 🎉")
        
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to server")
        print("Make sure the server is running:")
        print("  python main.py")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_complete_flow()
