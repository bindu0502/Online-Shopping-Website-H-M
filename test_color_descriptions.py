"""
Test Color Descriptions

Test script to verify color descriptions are working in the API and database.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.db import SessionLocal, Product

def test_color_descriptions():
    """Test color descriptions in the database."""
    
    db = SessionLocal()
    
    try:
        # Get products with color descriptions
        products = db.query(Product).filter(
            Product.color_description.isnot(None),
            Product.color_description != ''
        ).limit(20).all()
        
        print("=" * 80)
        print("COLOR DESCRIPTIONS TEST")
        print("=" * 80)
        
        if not products:
            print("No products with color descriptions found")
            return
        
        print(f"Found {len(products)} products with color descriptions:")
        print()
        
        for i, product in enumerate(products, 1):
            colors = product.colors.split(',') if product.colors else []
            print(f"{i}. Article: {product.article_id}")
            print(f"   Name: {product.name[:50]}...")
            print(f"   Colors: {colors}")
            print(f"   Primary: {product.primary_color}")
            print(f"   Description: {product.color_description}")
            print()
        
        # Statistics
        total_products = db.query(Product).count()
        products_with_colors = db.query(Product).filter(Product.colors.isnot(None)).count()
        products_with_descriptions = db.query(Product).filter(
            Product.color_description.isnot(None),
            Product.color_description != ''
        ).count()
        
        print("=" * 80)
        print("STATISTICS")
        print("=" * 80)
        print(f"Total products: {total_products:,}")
        print(f"Products with colors: {products_with_colors:,}")
        print(f"Products with descriptions: {products_with_descriptions:,}")
        print(f"Color coverage: {products_with_colors/total_products*100:.1f}%")
        print(f"Description coverage: {products_with_descriptions/total_products*100:.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_color_descriptions()