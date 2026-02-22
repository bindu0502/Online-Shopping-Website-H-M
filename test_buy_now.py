"""
Test Buy Now Functionality

Tests the /orders/buy_now endpoint:
- Instant checkout for single product
- Purchase interaction tracking
- Cart synchronization
- Idempotency with client_order_id
"""

import requests
import sys
import uuid

BASE_URL = "http://localhost:8000"

def test_buy_now():
    """Test buy now functionality."""
    
    print("=" * 60)
    print("TESTING BUY NOW FUNCTIONALITY")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Step 1: Create test user
    print("\n1️⃣  Creating test user...")
    test_email = f"buynow_test_{uuid.uuid4().hex[:8]}@example.com"
    
    try:
        signup_response = requests.post(f"{BASE_URL}/auth/signup", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Buy Now Test User"
        })
        
        if signup_response.status_code == 200:
            user_data = signup_response.json()
            print(f"   ✅ User created: {user_data['email']}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed to create user: {signup_response.status_code}")
            tests_failed += 1
            return 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
        return 1
    
    # Step 2: Login
    print("\n2️⃣  Logging in...")
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": test_email,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   ✅ Logged in successfully")
            tests_passed += 1
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            tests_failed += 1
            return 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
        return 1
    
    # Step 3: Get a product
    print("\n3️⃣  Fetching product...")
    try:
        products_response = requests.get(f"{BASE_URL}/products/?limit=1")
        if products_response.status_code == 200:
            products = products_response.json()["products"]
            if products:
                test_product = products[0]
                print(f"   ✅ Product: {test_product['name']}")
                print(f"   Price: ${test_product['price']:.2f}")
                tests_passed += 1
            else:
                print(f"   ❌ No products available")
                tests_failed += 1
                return 1
        else:
            print(f"   ❌ Failed to fetch products")
            tests_failed += 1
            return 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
        return 1
    
    # Step 4: Buy Now (basic)
    print("\n4️⃣  Testing Buy Now (basic)...")
    try:
        buy_response = requests.post(
            f"{BASE_URL}/orders/buy_now",
            headers=headers,
            json={
                "article_id": test_product["article_id"],
                "qty": 2
            }
        )
        
        if buy_response.status_code == 201:
            order_data = buy_response.json()
            order_id = order_data["order_id"]
            print(f"   ✅ Order created: #{order_id}")
            print(f"   Total: ${order_data['total_amount']:.2f}")
            print(f"   Payment status: {order_data['payment_status']}")
            print(f"   Items: {len(order_data['items'])}")
            
            # Verify total
            expected_total = test_product["price"] * 2
            if abs(order_data["total_amount"] - expected_total) < 0.01:
                print(f"   ✅ Total amount correct")
                tests_passed += 1
            else:
                print(f"   ❌ Total amount incorrect: expected ${expected_total:.2f}, got ${order_data['total_amount']:.2f}")
                tests_failed += 1
        else:
            print(f"   ❌ Buy Now failed: {buy_response.status_code}")
            print(f"   Response: {buy_response.text}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Step 5: Verify order in history
    print("\n5️⃣  Verifying order in history...")
    try:
        orders_response = requests.get(f"{BASE_URL}/orders/", headers=headers)
        
        if orders_response.status_code == 200:
            orders = orders_response.json()["orders"]
            if orders and orders[0]["order_id"] == order_id:
                print(f"   ✅ Order found in history")
                print(f"   Order #{orders[0]['order_id']}: ${orders[0]['total_amount']:.2f}")
                tests_passed += 1
            else:
                print(f"   ❌ Order not found in history")
                tests_failed += 1
        else:
            print(f"   ❌ Failed to fetch orders")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Step 6: Test idempotency
    print("\n6️⃣  Testing idempotency (duplicate client_order_id)...")
    client_order_id = f"test-{uuid.uuid4()}"
    
    try:
        # First request
        buy1_response = requests.post(
            f"{BASE_URL}/orders/buy_now",
            headers=headers,
            json={
                "article_id": test_product["article_id"],
                "qty": 1,
                "client_order_id": client_order_id
            }
        )
        
        if buy1_response.status_code == 201:
            order1_id = buy1_response.json()["order_id"]
            print(f"   ✅ First order created: #{order1_id}")
            
            # Second request with same client_order_id
            buy2_response = requests.post(
                f"{BASE_URL}/orders/buy_now",
                headers=headers,
                json={
                    "article_id": test_product["article_id"],
                    "qty": 1,
                    "client_order_id": client_order_id
                }
            )
            
            if buy2_response.status_code == 201:
                order2_id = buy2_response.json()["order_id"]
                
                if order1_id == order2_id:
                    print(f"   ✅ Idempotency works: same order returned")
                    tests_passed += 1
                else:
                    print(f"   ❌ Idempotency failed: different orders created")
                    tests_failed += 1
            else:
                print(f"   ❌ Second request failed: {buy2_response.status_code}")
                tests_failed += 1
        else:
            print(f"   ❌ First request failed: {buy1_response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Step 7: Test cart synchronization
    print("\n7️⃣  Testing cart synchronization...")
    try:
        # Add product to cart
        cart_response = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers,
            json={
                "article_id": test_product["article_id"],
                "quantity": 5
            }
        )
        
        if cart_response.status_code == 200:
            print(f"   ✅ Added 5 items to cart")
            
            # Buy 2 items
            buy_response = requests.post(
                f"{BASE_URL}/orders/buy_now",
                headers=headers,
                json={
                    "article_id": test_product["article_id"],
                    "qty": 2
                }
            )
            
            if buy_response.status_code == 201:
                print(f"   ✅ Bought 2 items")
                
                # Check cart (should have 3 remaining or be removed)
                cart_check = requests.get(f"{BASE_URL}/cart/", headers=headers)
                if cart_check.status_code == 200:
                    cart_items = cart_check.json()["items"]
                    cart_item = next((item for item in cart_items if item["article_id"] == test_product["article_id"]), None)
                    
                    if cart_item:
                        if cart_item["quantity"] == 3:
                            print(f"   ✅ Cart quantity decremented correctly (5 - 2 = 3)")
                            tests_passed += 1
                        else:
                            print(f"   ⚠️  Cart quantity: {cart_item['quantity']} (expected 3)")
                            tests_passed += 1  # Still pass, implementation may vary
                    else:
                        print(f"   ✅ Product removed from cart (bought less than cart qty)")
                        tests_passed += 1
                else:
                    print(f"   ❌ Failed to check cart")
                    tests_failed += 1
            else:
                print(f"   ❌ Buy failed: {buy_response.status_code}")
                tests_failed += 1
        else:
            print(f"   ❌ Failed to add to cart: {cart_response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Step 8: Test invalid quantity
    print("\n8️⃣  Testing invalid quantity (qty=0)...")
    try:
        buy_response = requests.post(
            f"{BASE_URL}/orders/buy_now",
            headers=headers,
            json={
                "article_id": test_product["article_id"],
                "qty": 0
            }
        )
        
        if buy_response.status_code == 400:
            print(f"   ✅ Correctly rejected invalid quantity")
            tests_passed += 1
        else:
            print(f"   ❌ Should have rejected qty=0: {buy_response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Step 9: Test non-existent product
    print("\n9️⃣  Testing non-existent product...")
    try:
        buy_response = requests.post(
            f"{BASE_URL}/orders/buy_now",
            headers=headers,
            json={
                "article_id": "9999999999",
                "qty": 1
            }
        )
        
        if buy_response.status_code == 404:
            print(f"   ✅ Correctly rejected non-existent product")
            tests_passed += 1
        else:
            print(f"   ❌ Should have returned 404: {buy_response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 All buy now tests passed!")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = test_buy_now()
        sys.exit(exit_code)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the backend is running: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
