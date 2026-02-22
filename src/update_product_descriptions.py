"""
Update Product Descriptions Script

Updates product descriptions from the articles.csv file.
Reads the detail_desc column and updates the database.

Usage:
    python src/update_product_descriptions.py
    python src/update_product_descriptions.py --limit 1000
"""

import os
import sys
import argparse
import logging
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import SessionLocal, Product, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_articles_csv():
    """
    Find the articles.csv file.
    
    Returns:
        Path to articles.csv or None if not found
    """
    possible_paths = [
        "Project149/datasets/articles.csv/articles.csv",
        "datasets/articles.csv/articles.csv",
        "articles.csv/articles.csv",
        "Project149/datasets/articles.csv",
        "datasets/articles.csv",
        "articles.csv"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found articles.csv: {path}")
            return path
    
    logger.error("articles.csv not found. Please check the following paths:")
    for path in possible_paths:
        logger.error(f"  - {path}")
    return None


def load_articles_data(csv_path: str) -> pd.DataFrame:
    """
    Load articles data from CSV file.
    
    Args:
        csv_path: Path to articles.csv file
        
    Returns:
        DataFrame with articles data
    """
    try:
        logger.info(f"Loading articles data from {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Check required columns
        required_columns = ['article_id', 'detail_desc']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            logger.info(f"Available columns: {list(df.columns)}")
            return None
        
        logger.info(f"Loaded {len(df)} articles from CSV")
        return df
        
    except Exception as e:
        logger.error(f"Error loading articles data: {e}")
        return None


def update_product_descriptions(articles_df: pd.DataFrame, limit: int = None):
    """
    Update product descriptions in the database.
    
    Args:
        articles_df: DataFrame with articles data
        limit: Maximum number of products to update
    """
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Filter articles data if limit is specified
        if limit:
            articles_df = articles_df.head(limit)
            logger.info(f"Processing first {limit} articles")
        
        total_processed = 0
        total_updated = 0
        
        # Process each article
        for _, row in articles_df.iterrows():
            article_id_raw = row['article_id']
            # Convert to string with leading zero to match database format
            article_id = f"{article_id_raw:010d}"  # Pad to 10 digits with leading zeros
            description = row['detail_desc']
            
            # Skip if description is NaN or empty
            if pd.isna(description) or description == '':
                total_processed += 1
                continue
            
            try:
                # Find product in database
                product = db.query(Product).filter(Product.article_id == article_id).first()
                
                if product:
                    # Update description
                    product.description = description
                    db.commit()
                    total_updated += 1
                    logger.debug(f"Updated {article_id}: {description[:50]}...")
                else:
                    logger.debug(f"Product not found in database: {article_id}")
                
                total_processed += 1
                
                if total_processed % 1000 == 0:
                    logger.info(f"Progress: {total_processed}/{len(articles_df)} processed, {total_updated} updated")
                    
            except Exception as e:
                logger.error(f"Error updating product {article_id}: {e}")
                db.rollback()
        
        logger.info(f"✓ Complete: {total_processed} processed, {total_updated} updated with descriptions")
        
        # Show statistics
        products_with_descriptions = db.query(Product).filter(
            Product.description.isnot(None),
            Product.description != ''
        ).count()
        total_products = db.query(Product).count()
        
        logger.info(f"Database statistics:")
        logger.info(f"  Total products: {total_products:,}")
        logger.info(f"  Products with descriptions: {products_with_descriptions:,}")
        logger.info(f"  Description coverage: {products_with_descriptions/total_products*100:.1f}%")
        
    except Exception as e:
        logger.error(f"Error processing descriptions: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def show_description_examples(limit: int = 10):
    """
    Show examples of products with descriptions.
    
    Args:
        limit: Number of examples to show
    """
    db = SessionLocal()
    
    try:
        products = db.query(Product).filter(
            Product.description.isnot(None),
            Product.description != ''
        ).limit(limit).all()
        
        if not products:
            logger.info("No products with descriptions found")
            return
        
        logger.info(f"\nProduct description examples ({len(products)} products):")
        logger.info("-" * 80)
        
        for product in products:
            logger.info(f"Article: {product.article_id}")
            logger.info(f"Name: {product.name}")
            logger.info(f"Description: {product.description}")
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"Error showing examples: {e}")
    finally:
        db.close()


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Update product descriptions from articles.csv")
    parser.add_argument('--limit', type=int, help='Maximum number of products to process')
    parser.add_argument('--examples', action='store_true', help='Show description examples')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("PRODUCT DESCRIPTION UPDATE")
    print("=" * 80)
    
    if args.examples:
        show_description_examples()
        return
    
    # Find articles.csv file
    csv_path = find_articles_csv()
    if not csv_path:
        return
    
    # Load articles data
    articles_df = load_articles_data(csv_path)
    if articles_df is None:
        return
    
    # Update product descriptions
    update_product_descriptions(articles_df, limit=args.limit)


if __name__ == "__main__":
    main()