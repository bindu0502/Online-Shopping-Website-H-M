"""
Test AI-Powered Search Feature

Quick test to verify Gemini AI search is working.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_search():
    """Test the AI search endpoint."""
    print("=" * 60)
    print("AI SEARCH TEST")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "red dress under $50",
        "affordable shoes",
        "luxury handbag",
        "casual t-shirt"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 60)
        
        try:
            # Make search request
            response = requests.get(
                f"{BASE_URL}/search/",
                params={"q": query, "limit": 5, "use_ai": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Search successful!")
                print(f"   Search Type: {data.get('search_type', 'unknown')}")
                print(f"   Results: {data.get('total', 0)} products")
                
                if data.get('interpreted_query'):
                    print(f"   AI Interpretation: {data['interpreted_query']}")
                
                # Show first result
                products = data.get('products', [])
                if products:
                    product = products[0]
                    print(f"\n   Sample Result:")
                    print(f"   - {product['name']}")
                    print(f"   - Price: ${product['price']:.2f}")
                    if product.get('product_group_name'):
                        print(f"   - Category: {product['product_group_name']}")
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


def test_suggestions():
    """Test search suggestions."""
    print("\n" + "=" * 60)
    print("SEARCH SUGGESTIONS TEST")
    print("=" * 60)
    
    test_queries = ["dre", "sho", "bag"]
    
    for query in test_queries:
        print(f"\n🔍 Testing suggestions for: '{query}'")
        
        try:
            response = requests.get(
                f"{BASE_URL}/search/suggestions",
                params={"q": query, "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                print(f"✅ Found {len(suggestions)} suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n🚀 Starting AI Search Tests...\n")
    
    # Test main search
    test_search()
    
    # Test suggestions
    test_suggestions()
    
    print("\n✨ All tests completed!\n")
