"""Simple search test with actual product names"""

import requests

BASE_URL = "http://localhost:8000"

# Test with actual product names from database
queries = [
    "strap top",
    "t-shirt", 
    "jeans",
    "stockings"
]

for query in queries:
    print(f"\n🔍 Searching for: '{query}'")
    
    response = requests.get(
        f"{BASE_URL}/search/",
        params={"q": query, "limit": 5, "use_ai": True}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Type: {data['search_type']}")
        print(f"   Results: {data['total']}")
        
        if data.get('interpreted_query'):
            print(f"   AI: {data['interpreted_query']}")
        
        if data['products']:
            print(f"   First: {data['products'][0]['name']}")
    else:
        print(f"   Error: {response.status_code}")
