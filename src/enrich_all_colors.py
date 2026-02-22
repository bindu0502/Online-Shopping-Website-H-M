"""
Comprehensive Color Enrichment System

Ensures every product in the database has complete color and color description information.
Uses intelligent fallback generation for missing data.

Usage:
    python src/enrich_all_colors.py
    python src/enrich_all_colors.py --limit 1000
    python src/enrich_all_colors.py --force  # Re-process products that already have colors
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import SessionLocal, Product, init_db
from src.color_generator import color_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def enrich_product_colors(limit: int = None, force: bool = False, batch_size: int = 1000):
    """
    Enrich all products with color and color description information.
    
    Args:
        limit: Maximum number of products to process
        force: Re-process products that already have color information
        batch_size: Number of products to process in each batch
    """
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(Product)
        
        if not force:
            # Only process products without complete color information AND not manually edited
            query = query.filter(
                (Product.colors.is_(None)) | 
                (Product.colors == '') |
                (Product.color_description.is_(None)) |
                (Product.color_description == ''),
                Product.color_manually_edited == False  # Don't touch manually edited products
            )
        else:
            # Even with force, respect manual edits
            query = query.filter(Product.color_manually_edited == False)
        
        if limit:
            query = query.limit(limit)
        
        products = query.all()
        
        logger.info(f"Processing {len(products)} products (force: {force}, limit: {limit})")
        
        if not products:
            logger.info("No products found to process")
            return
        
        total_processed = 0
        total_updated = 0
        
        # Process in batches
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} products")
            
            for product in batch:
                try:
                    # Generate color information
                    color_info = color_generator.generate_color_info(
                        product_name=product.name,
                        product_group=product.product_group_name,
                        department_name=str(product.department_no) if product.department_no else None,
                        existing_colors=product.colors
                    )
                    
                    # Update product if we don't have complete information
                    needs_update = False
                    
                    if not product.colors or product.colors.strip() == '':
                        product.colors = color_info.color
                        needs_update = True
                    
                    if not product.primary_color or product.primary_color.strip() == '':
                        product.primary_color = color_info.color
                        needs_update = True
                    
                    if not product.color_description or product.color_description.strip() == '':
                        product.color_description = color_info.color_description
                        needs_update = True
                    
                    if needs_update or force:
                        # If forcing, update everything
                        if force:
                            product.colors = color_info.color
                            product.primary_color = color_info.color
                            product.color_description = color_info.color_description
                        
                        db.commit()
                        total_updated += 1
                        
                        logger.debug(f"Updated {product.article_id}: {color_info.color} - {color_info.color_description}")
                    
                    total_processed += 1
                    
                except Exception as e:
                    logger.error(f"Error processing product {product.article_id}: {e}")
                    db.rollback()
            
            # Progress update
            if total_processed % 1000 == 0:
                logger.info(f"Progress: {total_processed}/{len(products)} processed, {total_updated} updated")
        
        logger.info(f"✓ Complete: {total_processed} processed, {total_updated} updated with color information")
        
        # Show final statistics
        show_statistics(db)
        
    except Exception as e:
        logger.error(f"Error during color enrichment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def show_statistics(db):
    """Show database statistics after processing."""
    try:
        total_products = db.query(Product).count()
        
        products_with_colors = db.query(Product).filter(
            Product.colors.isnot(None),
            Product.colors != ''
        ).count()
        
        products_with_color_descriptions = db.query(Product).filter(
            Product.color_description.isnot(None),
            Product.color_description != ''
        ).count()
        
        products_complete = db.query(Product).filter(
            Product.colors.isnot(None),
            Product.colors != '',
            Product.color_description.isnot(None),
            Product.color_description != ''
        ).count()
        
        logger.info(f"Final Statistics:")
        logger.info(f"  Total products: {total_products:,}")
        logger.info(f"  Products with colors: {products_with_colors:,}")
        logger.info(f"  Products with color descriptions: {products_with_color_descriptions:,}")
        logger.info(f"  Products with complete color info: {products_complete:,}")
        logger.info(f"  Complete color coverage: {products_complete/total_products*100:.1f}%")
        
    except Exception as e:
        logger.error(f"Error showing statistics: {e}")


def show_examples(limit: int = 10):
    """Show examples of enriched products."""
    db = SessionLocal()
    
    try:
        products = db.query(Product).filter(
            Product.colors.isnot(None),
            Product.colors != '',
            Product.color_description.isnot(None),
            Product.color_description != ''
        ).limit(limit).all()
        
        if not products:
            logger.info("No products with complete color information found")
            return
        
        logger.info(f"\nColor enrichment examples ({len(products)} products):")
        logger.info("-" * 80)
        
        for product in products:
            logger.info(f"Article: {product.article_id}")
            logger.info(f"Name: {product.name}")
            logger.info(f"Group: {product.product_group_name}")
            logger.info(f"Color: {product.colors}")
            logger.info(f"Primary: {product.primary_color}")
            logger.info(f"Description: {product.color_description}")
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"Error showing examples: {e}")
    finally:
        db.close()


def test_color_generation():
    """Test the color generation system with sample data."""
    logger.info("Testing color generation system...")
    
    test_cases = [
        ("Red Dress", "Dress", None),
        ("Navy Blue Jeans", "Garment Lower body", None),
        ("White Cotton T-shirt", "Jersey Basic", None),
        ("Black Leather Jacket", "Jacket", None),
        ("Floral Summer Dress", "Dress", None),
        ("Basic Top", "Garment Upper body", None),
        ("Striped Shirt", "Shirt", None),
        ("Pink Blouse", "Blouse", None),
    ]
    
    logger.info("\nColor Generation Test Results:")
    logger.info("-" * 60)
    
    for name, group, dept in test_cases:
        color_info = color_generator.generate_color_info(name, group, dept)
        logger.info(f"Product: {name}")
        logger.info(f"  Color: {color_info.color}")
        logger.info(f"  Description: {color_info.color_description}")
        logger.info(f"  Confidence: {color_info.confidence:.2f}")
        logger.info("-" * 60)


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Enrich all products with color information")
    parser.add_argument('--limit', type=int, help='Maximum number of products to process')
    parser.add_argument('--force', action='store_true', help='Re-process products that already have colors')
    parser.add_argument('--batch_size', type=int, default=1000, help='Batch size for processing')
    parser.add_argument('--examples', action='store_true', help='Show color enrichment examples')
    parser.add_argument('--test', action='store_true', help='Test color generation system')
    parser.add_argument('--stats', action='store_true', help='Show current statistics only')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("COMPREHENSIVE COLOR ENRICHMENT SYSTEM")
    print("=" * 80)
    
    if args.test:
        test_color_generation()
        return
    
    if args.examples:
        show_examples()
        return
    
    if args.stats:
        db = SessionLocal()
        try:
            show_statistics(db)
        finally:
            db.close()
        return
    
    # Main processing
    enrich_product_colors(
        limit=args.limit,
        force=args.force,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()