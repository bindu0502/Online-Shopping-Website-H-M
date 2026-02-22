"""
Update Image Paths Script

Updates product records in the database with image paths.
Maps article_id to image files in the images_128_128 directory.

Usage:
    python src/update_image_paths.py
"""

import sys
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import SessionLocal, Product


def update_image_paths():
    """
    Update product image paths in the database.
    
    For each product, constructs the image path based on article_id:
    - First 3 digits of article_id determine the folder
    - Image filename is article_id.jpg
    - Path format: /images/XXX/XXXXXXXXXX.jpg
    """
    print("Updating product image paths...")
    
    # Create database session
    db = SessionLocal()
    
    # Base path for images
    images_base = "Project149/datasets/images_128_128"
    
    try:
        # Get all products
        products = db.query(Product).all()
        total = len(products)
        print(f"Found {total} products to update")
        
        updated_count = 0
        missing_count = 0
        
        for idx, product in enumerate(products):
            # Get first 3 digits of article_id for folder
            folder = product.article_id[:3]
            
            # Construct image filename
            image_filename = f"{product.article_id}.jpg"
            
            # Full path on disk
            disk_path = os.path.join(images_base, folder, image_filename)
            
            # Check if image exists
            if os.path.exists(disk_path):
                # URL path for API (served via /images endpoint)
                product.image_path = f"/images/{folder}/{image_filename}"
                updated_count += 1
            else:
                # Image doesn't exist
                product.image_path = None
                missing_count += 1
            
            # Progress update every 10,000 products
            if (idx + 1) % 10000 == 0:
                print(f"Progress: {idx + 1}/{total} products processed "
                      f"(Updated: {updated_count}, Missing: {missing_count})")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*60)
        print(f"Image paths updated!")
        print(f"Updated: {updated_count} products with images")
        print(f"Missing: {missing_count} products without images")
        print("="*60)
        
    except Exception as e:
        print(f"Error updating image paths: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    update_image_paths()
