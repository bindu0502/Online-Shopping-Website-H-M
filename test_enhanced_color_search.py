"""
Test Enhanced Color Search Functionality

Tests the new color matching and description features.
"""

import requests
import json


def test_color_search():
    """Test enhanced color search functionality."""
    
    print("=" * 80)
    print("🎨 ENHANCED COLOR SEARCH TEST")
    print("=" * 80)
    
    # Test different color searches
    test_queries = [
        "white dress",
        "black jeans", 
        "red",
        "blue shoes",
        "green jacket"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 50)
        
        try:
            response = requests.get(f'http://localhost:8000/search/?q={query}&limit=3')
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Query: {data['query']}")
                print(f"🎯 Matched Color: {data.get('matched_color', 'None')}")
                print(f"📊 Results: {len(data['products'])} products")
                print(f"🤖 Search Type: {data.get('search_type', 'unknown')}")
                
                if data.get('interpreted_query'):
                    print(f"🧠 AI Interpretation: {data['interpreted_query']}")
                
                # Show first result details
                if data['products']:
                    product = data['products'][0]
                    print(f"\n📦 First Result:")
                    print(f"   Name: {product['name']}")
                    print(f"   Available Colors: {product.get('colors', 'None')}")
                    print(f"   Matched Color: {product.get('matched_color', 'None')}")
                    
                    if product.get('color_description'):
                        print(f"   Color Description: {product['color_description']}")
                    
                    print(f"   Price: ${product['price']:.2f}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 80)
    print("✅ ENHANCED COLOR SEARCH TEST COMPLETE")
    print("=" * 80)
    
    print("\n🎯 Expected Behavior:")
    print("- 'white dress' → Shows white dresses with white color description")
    print("- 'black jeans' → Shows black jeans with black color description") 
    print("- 'red' → Shows red products with red color description")
    print("- Products display matched color and description in UI")
    print("- Non-color searches show regular color badges")


if __name__ == "__main__":
    test_color_search()