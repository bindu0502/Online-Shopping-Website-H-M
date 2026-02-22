"""
Update Product Prices Script

Assigns realistic random prices to products based on their product group.
Different categories get different price ranges.

Usage:
    python src/update_prices.py
"""

import sys
from pathlib import Path
import random

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import SessionLocal, Product


# Price ranges by product group (min, max)
PRICE_RANGES = {
    # Accessories
    'Accessories': (9.99, 49.99),
    'Bags': (19.99, 89.99),
    'Shoes': (29.99, 149.99),
    'Socks & Tights': (4.99, 19.99),
    'Cosmetic': (5.99, 39.99),
    
    # Upper body
    'Garment Upper body': (14.99, 79.99),
    'Underwear/nightwear': (9.99, 39.99),
    'Swimwear': (19.99, 69.99),
    
    # Lower body
    'Garment Lower body': (19.99, 89.99),
    'Garment Full body': (29.99, 129.99),
    
    # Outerwear
    'Outdoor': (49.99, 199.99),
    
    # Kids
    'Items': (9.99, 49.99),
    
    # Default for unknown categories
    'default': (14.99, 59.99)
}


def get_price_for_product(product_group):
    """
    Get a random price based on product group.
    
    Args:
        product_group: Product group name
        
    Returns:
        Random price within the appropriate range
    """
    # Get price range for this group, or use default
    min_price, max_price = PRICE_RANGES.get(product_group, PRICE_RANGES['default'])
    
    # Generate random price
    price = random.uniform(min_price, max_price)
    
    # Round to .99 or .49 for realistic pricing
    if random.random() < 0.7:  # 70% chance of .99
        price = int(price) + 0.99
    else:  # 30% chance of .49
        price = int(price) + 0.49
    
    return round(price, 2)


def update_prices():
    """
    Update all product prices in the database with realistic random prices.
    """
    print("Updating product prices...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all products
        products = db.query(Product).all()
        total = len(products)
        print(f"Found {total} products to update")
        
        updated_count = 0
        
        for idx, product in enumerate(products):
            # Generate price based on product group
            new_price = get_price_for_product(product.product_group_name)
            product.price = new_price
            updated_count += 1
            
            # Progress update every 10,000 products
            if (idx + 1) % 10000 == 0:
                print(f"Progress: {idx + 1}/{total} products updated")
                db.commit()  # Commit in batches
        
        # Final commit
        db.commit()
        
        print("\n" + "="*60)
        print(f"Price update complete!")
        print(f"Updated {updated_count} products with new prices")
        print("="*60)
        
        # Show some examples
        print("\nSample prices by category:")
        for group_name in ['Accessories', 'Shoes', 'Garment Upper body', 'Outdoor']:
            sample = db.query(Product).filter(
                Product.product_group_name == group_name
            ).first()
            if sample:
                print(f"  {group_name}: ${sample.price:.2f} ({sample.name})")
        
    except Exception as e:
        print(f"Error updating prices: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    update_prices()
