"""
Test Product Filtering and Sorting

Tests the /products endpoint with various filter combinations:
- Price range filtering (min_price, max_price)
- Department filtering
- Sorting (price_asc, price_desc, popular)
- Pagination with filters
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_filters():
    """Test product filtering and sorting."""
    
    print("=" * 60)
    print("TESTING PRODUCT FILTERS")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Basic product listing
    print("\n1️⃣  Test: Basic product listing")
    try:
        response = requests.get(f"{BASE_URL}/products/?page=1&limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "products" in data, "Missing 'products' key"
        assert "total" in data, "Missing 'total' key"
        assert len(data["products"]) > 0, "No products returned"
        print(f"   ✅ Got {len(data['products'])} products, total: {data['total']}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 2: Min price filter
    print("\n2️⃣  Test: Min price filter (min_price=50)")
    try:
        response = requests.get(f"{BASE_URL}/products/?min_price=50&limit=10")
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        assert len(products) > 0, "No products returned"
        
        # Verify all products have price >= 50
        for product in products:
            assert product["price"] >= 50, f"Product {product['article_id']} has price {product['price']} < 50"
        
        print(f"   ✅ All {len(products)} products have price >= $50")
        print("   Sample prices:", [f"${p['price']:.2f}" for p in products[:3]])
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 3: Max price filter
    print("\n3️⃣  Test: Max price filter (max_price=30)")
    try:
        response = requests.get(f"{BASE_URL}/products/?max_price=30&limit=10")
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        assert len(products) > 0, "No products returned"
        
        # Verify all products have price <= 30
        for product in products:
            assert product["price"] <= 30, f"Product {product['article_id']} has price {product['price']} > 30"
        
        print(f"   ✅ All {len(products)} products have price <= $30")
        print(f"   Sample prices: {[f'${p['price']:.2f}' for p in products[:3]]}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 4: Price range filter
    print("\n4️⃣  Test: Price range filter (min_price=25, max_price=50)")
    try:
        response = requests.get(f"{BASE_URL}/products/?min_price=25&max_price=50&limit=10")
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        assert len(products) > 0, "No products returned"
        
        # Verify all products are in range
        for product in products:
            assert 25 <= product["price"] <= 50, f"Product {product['article_id']} price {product['price']} not in range"
        
        print(f"   ✅ All {len(products)} products have price between $25-$50")
        print(f"   Sample prices: {[f'${p['price']:.2f}' for p in products[:3]]}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 5: Department filter
    print("\n5️⃣  Test: Department filter (department=1676)")
    try:
        response = requests.get(f"{BASE_URL}/products/?department=1676&limit=10")
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        assert len(products) > 0, "No products returned"
        
        # Verify all products are from department 1676
        for product in products:
            assert product["department_no"] == 1676, f"Product {product['article_id']} not in dept 1676"
        
        print(f"   ✅ All {len(products)} products are from department 1676")
        print(f"   Sample products: {[p['name'][:30] for p in products[:3]]}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 6: Sort by price ascending
    print("\n6️⃣  Test: Sort by price ascending (sort=price_asc)")
    try:
        response = requests.get(f"{BASE_URL}/products/?sort=price_asc&limit=10")
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        assert len(products) > 0, "No products returned"
        
        # Verify prices are in ascending order
        prices = [p["price"] for p in products]
        assert prices == sorted(prices), "Prices not in ascending order"
        
        print(f"   ✅ Products sorted by price (ascending)")
        print(f"   Prices: {[f'${p:.2f}' for p in prices[:5]]}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 7: Sort by price descending
    print("\n7️⃣  Test: Sort by price descending (sort=price_desc)")
    try:
        response = requests.get(f"{BASE_URL}/products/?sort=price_desc&limit=10")
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        assert len(products) > 0, "No products returned"
        
        # Verify prices are in descending order
        prices = [p["price"] for p in products]
        assert prices == sorted(prices, reverse=True), "Prices not in descending order"
        
        print(f"   ✅ Products sorted by price (descending)")
        print(f"   Prices: {[f'${p:.2f}' for p in prices[:5]]}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 8: Combined filters (price range + department + sort)
    print("\n8️⃣  Test: Combined filters (price 20-40, dept 1339, sort price_asc)")
    try:
        response = requests.get(
            f"{BASE_URL}/products/?min_price=20&max_price=40&department=1339&sort=price_asc&limit=10"
        )
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        
        if len(products) > 0:
            # Verify all conditions
            for product in products:
                assert 20 <= product["price"] <= 40, f"Price {product['price']} not in range"
                assert product["department_no"] == 1339, f"Not in dept 1339"
            
            # Verify sorting
            prices = [p["price"] for p in products]
            assert prices == sorted(prices), "Not sorted by price"
            
            print(f"   ✅ All {len(products)} products match all filters")
            print(f"   Prices: {[f'${p:.2f}' for p in prices[:5]]}")
        else:
            print(f"   ⚠️  No products match these filters (this is OK)")
        
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 9: Pagination with filters
    print("\n9️⃣  Test: Pagination with filters (page 1 vs page 2)")
    try:
        response1 = requests.get(f"{BASE_URL}/products/?min_price=20&page=1&limit=5")
        response2 = requests.get(f"{BASE_URL}/products/?min_price=20&page=2&limit=5")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        products1 = data1["products"]
        products2 = data2["products"]
        
        # Verify different products on different pages
        ids1 = {p["article_id"] for p in products1}
        ids2 = {p["article_id"] for p in products2}
        
        assert len(ids1 & ids2) == 0, "Pages have overlapping products"
        
        print(f"   ✅ Page 1 and Page 2 have different products")
        print(f"   Page 1: {len(products1)} products, Page 2: {len(products2)} products")
        print(f"   Total pages: {data1['total_pages']}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 10: Popular sort (random)
    print("\n🔟 Test: Popular sort (sort=popular)")
    try:
        response = requests.get(f"{BASE_URL}/products/?sort=popular&limit=10")
        assert response.status_code == 200
        data = response.json()
        products = data["products"]
        assert len(products) > 0, "No products returned"
        
        print(f"   ✅ Got {len(products)} popular products")
        print(f"   Sample: {products[0]['name'][:40]}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 All filter tests passed!")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = test_filters()
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
