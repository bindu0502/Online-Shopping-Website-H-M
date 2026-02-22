"""
Update Product Color Descriptions Script

Analyzes product images to detect colors and generates natural language descriptions.
Updates the database with detailed color information including descriptions.

Usage:
    python src/update_color_descriptions.py
    python src/update_color_descriptions.py --limit 100  # Process only first 100 products
    python src/update_color_descriptions.py --article_id 0108775015  # Process specific product
    python src/update_color_descriptions.py --force  # Update products that already have colors
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import SessionLocal, Product, init_db
from src.color_detection import analyze_product_colors, batch_analyze_colors, generate_color_description

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


def update_product_color_info(article_id: str, color_data: dict, db_session):
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
        
        # Update color fields
        colors = color_data.get('colors', [])
        primary_color = color_data.get('primary_color')
        description = color_data.get('description', '')
        
        if colors:
            product.colors = ','.join(colors)
            product.primary_color = primary_color
            product.color_description = description
        else:
            product.colors = None
            product.primary_color = None
            product.color_description = None
        
        db_session.commit()
        logger.debug(f"Updated {article_id}: colors={colors}, description='{description}'")
        return True
        
    except Exception as e:
        logger.error(f"Error updating product {article_id}: {e}")
        db_session.rollback()
        return False


def generate_description_from_existing_colors(colors_str: str, primary_color: str = None) -> str:
    """
    Generate color description from existing color data in database.
    
    Args:
        colors_str: Comma-separated color names
        primary_color: Primary color name
        
    Returns:
        Generated color description
    """
    if not colors_str:
        return ""
    
    colors = [c.strip() for c in colors_str.split(',') if c.strip()]
    return generate_color_description(colors, primary_color)


def process_products(limit: int = None, article_id: str = None, batch_size: int = 100, force: bool = False):
    """
    Process products to detect and update color information with descriptions.
    
    Args:
        limit: Maximum number of products to process
        article_id: Specific article ID to process (if provided)
        batch_size: Number of products to process in each batch
        force: Update products that already have color information
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
            if not force:
                # Only process products without color descriptions
                query = query.filter(
                    (Product.color_description.is_(None)) | 
                    (Product.color_description == '')
                )
            if limit:
                query = query.limit(limit)
            products = query.all()
            logger.info(f"Processing {len(products)} products (limit: {limit}, force: {force})")
        
        if not products:
            logger.warning("No products found to process")
            return
        
        # Separate products that need image analysis vs description generation only
        needs_analysis = []
        needs_description_only = []
        
        for product in products:
            if not product.colors or force:
                needs_analysis.append(product)
            elif product.colors and not product.color_description:
                needs_description_only.append(product)
        
        logger.info(f"Products needing full analysis: {len(needs_analysis)}")
        logger.info(f"Products needing description only: {len(needs_description_only)}")
        
        total_processed = 0
        total_updated = 0
        
        # Process products that only need descriptions (already have colors)
        for product in needs_description_only:
            try:
                description = generate_description_from_existing_colors(
                    product.colors, 
                    product.primary_color
                )
                if description:
                    product.color_description = description
                    db.commit()
                    total_updated += 1
                    logger.debug(f"Added description to {product.article_id}: '{description}'")
                total_processed += 1
            except Exception as e:
                logger.error(f"Error updating description for {product.article_id}: {e}")
                db.rollback()
        
        # Process products that need full color analysis
        if needs_analysis:
            for i in range(0, len(needs_analysis), batch_size):
                batch = needs_analysis[i:i + batch_size]
                batch_article_ids = [p.article_id for p in batch]
                
                logger.info(f"Processing analysis batch {i//batch_size + 1}: {len(batch)} products")
                
                # Analyze colors for this batch
                color_results = batch_analyze_colors(image_dir, batch_article_ids, max_workers=4)
                
                # Update database
                for article_id, color_data in color_results.items():
                    if update_product_color_info(article_id, color_data, db):
                        total_updated += 1
                    total_processed += 1
                    
                    if total_processed % 50 == 0:
                        logger.info(f"Progress: {total_processed}/{len(products)} processed, {total_updated} updated")
        
        logger.info(f"✓ Complete: {total_processed} processed, {total_updated} updated with color descriptions")
        
        # Show some statistics
        products_with_colors = db.query(Product).filter(Product.colors.isnot(None)).count()
        products_with_descriptions = db.query(Product).filter(
            Product.color_description.isnot(None),
            Product.color_description != ''
        ).count()
        total_products = db.query(Product).count()
        
        logger.info(f"Database statistics:")
        logger.info(f"  Total products: {total_products}")
        logger.info(f"  Products with colors: {products_with_colors}")
        logger.info(f"  Products with descriptions: {products_with_descriptions}")
        logger.info(f"  Color coverage: {products_with_colors/total_products*100:.1f}%")
        logger.info(f"  Description coverage: {products_with_descriptions/total_products*100:.1f}%")
        
    except Exception as e:
        logger.error(f"Error processing products: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def show_description_examples(limit: int = 10):
    """
    Show examples of products with color descriptions.
    
    Args:
        limit: Number of examples to show
    """
    db = SessionLocal()
    
    try:
        products = db.query(Product).filter(
            Product.color_description.isnot(None),
            Product.color_description != ''
        ).limit(limit).all()
        
        if not products:
            logger.info("No products with color descriptions found")
            return
        
        logger.info(f"\nColor description examples ({len(products)} products):")
        logger.info("-" * 80)
        
        for product in products:
            colors = product.colors.split(',') if product.colors else []
            logger.info(f"Article: {product.article_id}")
            logger.info(f"Name: {product.name[:60]}...")
            logger.info(f"Colors: {colors}")
            logger.info(f"Primary: {product.primary_color}")
            logger.info(f"Description: {product.color_description}")
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"Error showing examples: {e}")
    finally:
        db.close()


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Update product color descriptions")
    parser.add_argument('--limit', type=int, help='Maximum number of products to process')
    parser.add_argument('--article_id', type=str, help='Specific article ID to process')
    parser.add_argument('--batch_size', type=int, default=100, help='Batch size for processing')
    parser.add_argument('--force', action='store_true', help='Update products that already have colors')
    parser.add_argument('--examples', action='store_true', help='Show color description examples')
    parser.add_argument('--test', action='store_true', help='Test color description on sample products')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("PRODUCT COLOR DESCRIPTION UPDATE")
    print("=" * 80)
    
    if args.examples:
        show_description_examples()
        return
    
    if args.test:
        # Test with a few sample products
        logger.info("Testing color description on sample products...")
        process_products(limit=5, force=True)
        show_description_examples(limit=5)
        return
    
    # Main processing
    process_products(
        limit=args.limit,
        article_id=args.article_id,
        batch_size=args.batch_size,
        force=args.force
    )


if __name__ == "__main__":
    main()