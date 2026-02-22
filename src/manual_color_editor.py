"""
Manual Color Editor

Allows manual editing and saving of color information for specific products.
Useful for correcting automatically generated colors or adding custom color descriptions.

Usage:
    python src/manual_color_editor.py --article_id 0108775015
    python src/manual_color_editor.py --search "red dress" --limit 5
    python src/manual_color_editor.py --list --limit 10
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


def edit_product_color(article_id: str):
    """
    Edit color information for a specific product.
    
    Args:
        article_id: Product article ID to edit
    """
    db = SessionLocal()
    
    try:
        # Find the product
        product = db.query(Product).filter(Product.article_id == article_id).first()
        
        if not product:
            print(f"❌ Product not found: {article_id}")
            return
        
        print("=" * 80)
        print(f"EDITING PRODUCT: {article_id}")
        print("=" * 80)
        
        # Display current information
        print(f"Name: {product.name}")
        print(f"Group: {product.product_group_name}")
        print(f"Department: {product.department_no}")
        print()
        print("Current Color Information:")
        print(f"  Colors: {product.colors or 'None'}")
        print(f"  Primary Color: {product.primary_color or 'None'}")
        print(f"  Color Description: {product.color_description or 'None'}")
        print()
        
        # Get new color information
        print("Enter new color information (press Enter to keep current value):")
        print()
        
        # Colors input
        current_colors = product.colors or ''
        new_colors = input(f"Colors (comma-separated) [{current_colors}]: ").strip()
        if not new_colors:
            new_colors = current_colors
        
        # Primary color input
        current_primary = product.primary_color or ''
        new_primary = input(f"Primary Color [{current_primary}]: ").strip()
        if not new_primary:
            new_primary = current_primary
        
        # Color description input
        current_description = product.color_description or ''
        print(f"Current description: {current_description}")
        new_description = input(f"Color Description [{current_description}]: ").strip()
        if not new_description:
            new_description = current_description
        
        # Confirm changes
        print()
        print("=" * 80)
        print("PROPOSED CHANGES:")
        print("=" * 80)
        print(f"Colors: {product.colors} → {new_colors}")
        print(f"Primary Color: {product.primary_color} → {new_primary}")
        print(f"Color Description: {product.color_description} → {new_description}")
        print()
        
        confirm = input("Save these changes? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            # Update the product
            product.colors = new_colors if new_colors else None
            product.primary_color = new_primary if new_primary else None
            product.color_description = new_description if new_description else None
            
            db.commit()
            
            print("✅ Changes saved successfully!")
            
            # Show updated information
            print()
            print("Updated Color Information:")
            print(f"  Colors: {product.colors}")
            print(f"  Primary Color: {product.primary_color}")
            print(f"  Color Description: {product.color_description}")
            
        else:
            print("❌ Changes cancelled.")
            
    except Exception as e:
        logger.error(f"Error editing product {article_id}: {e}")
        db.rollback()
    finally:
        db.close()


def search_and_edit_products(search_term: str, limit: int = 10):
    """
    Search for products and allow editing their colors.
    
    Args:
        search_term: Search term to find products
        limit: Maximum number of products to show
    """
    db = SessionLocal()
    
    try:
        # Search for products
        products = db.query(Product).filter(
            Product.name.ilike(f'%{search_term}%')
        ).limit(limit).all()
        
        if not products:
            print(f"❌ No products found matching: {search_term}")
            return
        
        print("=" * 80)
        print(f"SEARCH RESULTS FOR: {search_term}")
        print("=" * 80)
        
        # Display products
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.article_id} - {product.name}")
            print(f"   Colors: {product.colors or 'None'}")
            print(f"   Primary: {product.primary_color or 'None'}")
            print(f"   Description: {product.color_description or 'None'}")
            print()
        
        # Let user select a product to edit
        while True:
            try:
                choice = input(f"Select product to edit (1-{len(products)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    break
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(products):
                    selected_product = products[choice_num - 1]
                    print()
                    edit_product_color(selected_product.article_id)
                    break
                else:
                    print(f"Please enter a number between 1 and {len(products)}")
                    
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
                
    except Exception as e:
        logger.error(f"Error searching products: {e}")
    finally:
        db.close()


def list_products_with_colors(limit: int = 20):
    """
    List products that have color information.
    
    Args:
        limit: Maximum number of products to show
    """
    db = SessionLocal()
    
    try:
        products = db.query(Product).filter(
            Product.colors.isnot(None),
            Product.colors != ''
        ).limit(limit).all()
        
        print("=" * 80)
        print(f"PRODUCTS WITH COLOR INFORMATION (showing {len(products)})")
        print("=" * 80)
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.article_id} - {product.name[:50]}...")
            print(f"   Colors: {product.colors}")
            print(f"   Primary: {product.primary_color}")
            print(f"   Description: {product.color_description[:60]}...")
            print()
            
    except Exception as e:
        logger.error(f"Error listing products: {e}")
    finally:
        db.close()


def bulk_update_colors(csv_file: str):
    """
    Bulk update colors from a CSV file.
    
    CSV format: article_id,colors,primary_color,color_description
    
    Args:
        csv_file: Path to CSV file with color updates
    """
    import csv
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    db = SessionLocal()
    
    try:
        updated_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                article_id = row.get('article_id', '').strip()
                colors = row.get('colors', '').strip()
                primary_color = row.get('primary_color', '').strip()
                color_description = row.get('color_description', '').strip()
                
                if not article_id:
                    continue
                
                # Find and update product
                product = db.query(Product).filter(Product.article_id == article_id).first()
                
                if product:
                    if colors:
                        product.colors = colors
                    if primary_color:
                        product.primary_color = primary_color
                    if color_description:
                        product.color_description = color_description
                    
                    updated_count += 1
                    
                    if updated_count % 100 == 0:
                        print(f"Updated {updated_count} products...")
                        db.commit()
        
        db.commit()
        print(f"✅ Bulk update complete: {updated_count} products updated")
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        db.rollback()
    finally:
        db.close()


def generate_color_suggestions(article_id: str):
    """
    Generate color suggestions for a product using the intelligent system.
    
    Args:
        article_id: Product article ID
    """
    db = SessionLocal()
    
    try:
        product = db.query(Product).filter(Product.article_id == article_id).first()
        
        if not product:
            print(f"❌ Product not found: {article_id}")
            return
        
        print("=" * 80)
        print(f"COLOR SUGGESTIONS FOR: {article_id}")
        print("=" * 80)
        print(f"Name: {product.name}")
        print(f"Group: {product.product_group_name}")
        print()
        
        # Generate suggestions
        color_info = color_generator.generate_color_info(
            product_name=product.name,
            product_group=product.product_group_name,
            department_name=str(product.department_no) if product.department_no else None,
            existing_colors=product.colors
        )
        
        print("Suggested Color Information:")
        print(f"  Color: {color_info.color}")
        print(f"  Description: {color_info.color_description}")
        print(f"  Confidence: {color_info.confidence:.2f}")
        print()
        
        apply = input("Apply these suggestions? (y/N): ").strip().lower()
        
        if apply in ['y', 'yes']:
            product.colors = color_info.color
            product.primary_color = color_info.color
            product.color_description = color_info.color_description
            
            db.commit()
            print("✅ Suggestions applied successfully!")
        else:
            print("❌ Suggestions not applied.")
            
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
    finally:
        db.close()


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Manual Color Editor for Products")
    parser.add_argument('--article_id', type=str, help='Edit specific product by article ID')
    parser.add_argument('--search', type=str, help='Search for products to edit')
    parser.add_argument('--list', action='store_true', help='List products with colors')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of results')
    parser.add_argument('--bulk', type=str, help='Bulk update from CSV file')
    parser.add_argument('--suggest', type=str, help='Generate color suggestions for article ID')
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    print("=" * 80)
    print("MANUAL COLOR EDITOR")
    print("=" * 80)
    
    if args.article_id:
        edit_product_color(args.article_id)
    elif args.search:
        search_and_edit_products(args.search, args.limit)
    elif args.list:
        list_products_with_colors(args.limit)
    elif args.bulk:
        bulk_update_colors(args.bulk)
    elif args.suggest:
        generate_color_suggestions(args.suggest)
    else:
        print("Please specify an action:")
        print("  --article_id <id>     Edit specific product")
        print("  --search <term>       Search and edit products")
        print("  --list                List products with colors")
        print("  --bulk <csv_file>     Bulk update from CSV")
        print("  --suggest <id>        Generate color suggestions")
        print()
        print("Examples:")
        print("  python src/manual_color_editor.py --article_id 0108775015")
        print("  python src/manual_color_editor.py --search 'red dress'")
        print("  python src/manual_color_editor.py --list --limit 20")


if __name__ == "__main__":
    main()