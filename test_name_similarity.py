"""Test name similarity function."""
from src.personalized_recommend import calculate_name_similarity, extract_keywords

print("Testing keyword extraction:")
print(f"  'Slim Fit Jeans' → {extract_keywords('Slim Fit Jeans')}")
print(f"  'White Cotton T-Shirt' → {extract_keywords('White Cotton T-Shirt')}")

print("\nTesting name similarity:")
tests = [
    ("Slim Fit Jeans", "Straight Fit Jeans"),
    ("White T-Shirt", "White Shirt"),
    ("Black Cap", "Black Hat"),
    ("Running Shoes", "Walking Shoes"),
    ("Dress", "Jeans"),
]

for name1, name2 in tests:
    score = calculate_name_similarity(name1, name2)
    print(f"  '{name1}' vs '{name2}': {score:.2f}")
