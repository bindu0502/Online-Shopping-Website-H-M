"""
Test Product Filtering and Sorting
"""

import requests
import sys

BASE_URL = "http://localhost:8000"


def test_filters():
    print("=" * 60)
    print("TESTING PRODUCT FILTERS")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1
    print("\n1️⃣  Test: Basic product listing")
    try:
        response = requests.get(f"{BASE_URL}/products/?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert len(data["products"]) > 0

        print(f"   ✅ Got {len(data['products'])} products")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1

    # Test 2
    print("\n2️⃣  Test: Min price filter (min_price=50)")
    try:
        response = requests.get(f"{BASE_URL}/products/?min_price=50&limit=10")
        data = response.json()
        products = data["products"]

        for product in products:
            assert product["price"] >= 50

        print("   Sample prices:", [f"${p['price']:.2f}" for p in products[:3]])
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1

    # Test 3
    print("\n3️⃣  Test: Max price filter (max_price=30)")
    try:
        response = requests.get(f"{BASE_URL}/products/?max_price=30&limit=10")
        data = response.json()
        products = data["products"]

        for product in products:
            assert product["price"] <= 30

        print("   Sample prices:", [f"${p['price']:.2f}" for p in products[:3]])
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")

    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = test_filters()
        sys.exit(exit_code)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        sys.exit(1)