"""
Update Product Colors Script

Analyzes product images to detect colors and updates the database with color information.
This script processes all products and adds color descriptions to enable color-based search.

Usage:
    python src/update_product_colors.py
    python src/update_product_colors.py --limit 100  # Process only first 100 products
    python src/update_product_colors.py --article_id 0108775015  # Process specific product
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import SessionLocal, Product, init_db
from src.color_detection import analyze_product_colors, batch_analyze_colors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_image_directory():
    """
    Find the product images directory.
    
    Returns:
        Path to images directory or None if not found
    """
    possible_paths = [
        "Project149/datasets/images_128_128",
        "datasets/images_128_128",
        "images_128_128",
        "Project149/datasets/images",
        "datasets/images"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found images directory: {path}")
            return path
    
    logger.error("Images directory not found. Please check the following paths:")
    for path in possible_paths:
        logger.error(f"  - {path}")
    return None


def update_product_colors(article_id: str, color_data: dict, db_session):
    """
    Update a single product's color information in the database.
    
    Args:
        article_id: Product article ID
        color_data: Dictionary with colors, primary_color, and description
        db_session: Database session
    """
    try:
        product = db_session.query(Product).filter(Product.article_id == article_id).first()
        
        if not product:
            logger.warning(f"Product not found: {article_id}")
            return False
        
        # Handle both old format (list) and new format (dict)
        if isinstance(color_data, list):
            # Old format - just colors list
            colors = color_data
            primary_color = colors[0] if colors else None
            description = ""
        else:
            # New format - dict with colors, primary_color, description
            colors = color_data.get('colors', [])
            primary_color = color_data.get('primary_color')
            description = color_data.get('description', '')
        
        # Update color fields
        if colors:
            product.colors = ','.join(colors)
            product.primary_color = primary_color
            if hasattr(product, 'color_description'):
                product.color_description = description
        else:
            product.colors = None
            product.primary_color = None
            if hasattr(product, 'color_description'):
                product.color_description = None
        
        db_session.commit()
        logger.debug(f"Updated {article_id}: colors={colors}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating product {article_id}: {e}")
        db_session.rollback()
        return False


def process_products(limit: int = None, article_id: str = None, batch_size: int = 100):
    """
    Process products to detect and update color information.
    
    Args:
        limit: Maximum number of products to process
        article_id: Specific article ID to process (if provided)
        batch_size: Number of products to process in each batch
    """
    # Initialize database
    init_db()
    
    # Find images directory
    image_dir = find_image_directory()
    if not image_dir:
        return
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get products to process
        if article_id:
            products = db.query(Product).filter(Product.article_id == article_id).all()
            logger.info(f"Processing specific product: {article_id}")
        else:
            query = db.query(Product)
            if limit:
                query = query.limit(limit)
            products = query.all()
            logger.info(f"Processing {len(products)} products (limit: {limit})")
        
        if not products:
            logger.warning("No products found to process")
            return
        
        # Process in batches
        total_processed = 0
        total_updated = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            batch_article_ids = [p.article_id for p in batch]
            
            logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} products")
            
            # Analyze colors for this batch
            color_results = batch_analyze_colors(image_dir, batch_article_ids, max_workers=4)
            
            # Update database
            for article_id, color_data in color_results.items():
                if update_product_colors(article_id, color_data, db):
                    total_updated += 1
                total_processed += 1
                
                if total_processed % 50 == 0:
                    logger.info(f"Progress: {total_processed}/{len(products)} processed, {total_updated} updated")
        
        logger.info(f"✓ Complete: {total_processed} processed, {total_updated} updated with colors")
        
        # Show some statistics
        products_with_colors = db.query(Product).filter(Product.colors.isnot(None)).count()
        total_products = db.query(Product).count()
        
        logger.info(f"Database statistics:")
        logger.info(f"  Total products: {total_products}")
        logger.info(f"  Products with colors: {products_with_colors}")
        logger.info(f"  Coverage: {products_with_colors/total_products*100:.1f}%")
        
    except Exception as e:
        logger.error(f"Error processing products: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def show_color_examples(limit: int = 10):
    """
    Show examples of products with detected colors.
    
    Args:
        limit: Number of examples to show
    """
    db = SessionLocal()
    
    try:
        products = db.query(Product).filter(
            Product.colors.isnot(None)
        ).limit(limit).all()
        
        if not products:
            logger.info("No products with colors found")
            return
        
        logger.info(f"\nColor detection examples ({len(products)} products):")
        logger.info("-" * 80)
        
        for product in products:
            colors = product.colors.split(',') if product.colors else []
            logger.info(f"Article: {product.article_id}")
            logger.info(f"Name: {product.name[:60]}...")
            logger.info(f"Primary Color: {product.primary_color}")
            logger.info(f"All Colors: {colors}")
            logger.info(f"Image: {product.image_path}")
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"Error showing examples: {e}")
    finally:
        db.close()


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Update product colors from images")
    parser.add_argument('--limit', type=int, help='Maximum number of products to process')
    parser.add_argument('--article_id', type=str, help='Specific article ID to process')
    parser.add_argument('--batch_size', type=int, default=100, help='Batch size for processing')
    parser.add_argument('--examples', action='store_true', help='Show color detection examples')
    parser.add_argument('--test', action='store_true', help='Test color detection on sample products')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("PRODUCT COLOR DETECTION AND UPDATE")
    print("=" * 80)
    
    if args.examples:
        show_color_examples()
        return
    
    if args.test:
        # Test with a few sample products
        logger.info("Testing color detection on sample products...")
        process_products(limit=5)
        show_color_examples(limit=5)
        return
    
    # Main processing
    process_products(
        limit=args.limit,
        article_id=args.article_id,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()