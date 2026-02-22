"""
Test script for Products API.

Tests product listing, detail view, and similar products functionality.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_products_api():
    """Test the products API endpoints."""
    print("=" * 60)
    print("PRODUCTS API TEST")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    # Wait for server to be ready
    time.sleep(1)
    
    try:
        # Test 1: Get products list
        print("1. Testing GET /products...")
        products_response = requests.get(f"{BASE_URL}/products")
        print(f"   Status: {products_response.status_code}")
        
        if products_response.status_code == 200:
            products = products_response.json()
            print(f"   ✓ Retrieved {len(products)} products")
            
            if products:
                print(f"   First product: {products[0]['name']} (${products[0]['price']})")
                first_article_id = products[0]['article_id']
            else:
                print("   ⚠ No products in database")
                first_article_id = None
        else:
            print(f"   Response: {products_response.json()}")
            first_article_id = None
        print()
        
        # Test 2: Get products with pagination
        print("2. Testing GET /products with pagination...")
        paginated_response = requests.get(f"{BASE_URL}/products?skip=0&limit=5")
        print(f"   Status: {paginated_response.status_code}")
        
        if paginated_response.status_code == 200:
            paginated_products = paginated_response.json()
            print(f"   ✓ Retrieved {len(paginated_products)} products (limit=5)")
        print()
        
        if first_article_id:
            # Test 3: Get product detail
            print(f"3. Testing GET /products/{first_article_id}...")
            detail_response = requests.get(f"{BASE_URL}/products/{first_article_id}")
            print(f"   Status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                product = detail_response.json()
                print(f"   ✓ Product details:")
                print(f"     Name: {product['name']}")
                print(f"     Price: ${product['price']}")
                print(f"     Department: {product.get('department_no', 'N/A')}")
                print(f"     Group: {product.get('product_group_name', 'N/A')}")
            print()
            
            # Test 4: Get similar products
            print(f"4. Testing GET /products/{first_article_id}/similar...")
            similar_response = requests.get(f"{BASE_URL}/products/{first_article_id}/similar")
            print(f"   Status: {similar_response.status_code}")
            
            if similar_response.status_code == 200:
                similar_products = similar_response.json()
                print(f"   ✓ Retrieved {len(similar_products)} similar products")
                
                if similar_products:
                    print(f"   First similar: {similar_products[0]['name']} (${similar_products[0]['price']})")
            print()
        
        # Test 5: Get non-existent product (should return 404)
        print("5. Testing GET /products/nonexistent...")
        not_found_response = requests.get(f"{BASE_URL}/products/nonexistent123")
        print(f"   Status: {not_found_response.status_code}")
        
        if not_found_response.status_code == 404:
            print(f"   ✓ Correctly returned 404: {not_found_response.json()['detail']}")
        print()
        
        print("=" * 60)
        print("✓ ALL PRODUCTS API TESTS COMPLETED")
        print("=" * 60)
        print()
        print("You can now:")
        print("  - Open http://localhost:8000/docs to see all endpoints")
        print("  - Test products endpoints interactively")
        
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to server")
        print("Make sure the server is running:")
        print("  python main.py")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_products_api()
