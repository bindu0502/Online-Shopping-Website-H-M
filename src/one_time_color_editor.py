"""
One-Time Color Editor

Allows manual editing of product colors ONLY ONCE per product.
After editing, the product is permanently locked from further color changes.

Usage:
    python src/one_time_color_editor.py --article_id 0108775015
    python src/one_time_color_editor.py --search "red dress" --limit 5
    python src/one_time_color_editor.py --list-editable --limit 10
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


def check_edit_permission(product: Product) -> bool:
    """
    Check if a product can be edited.
    
    Args:
        product: Product object
        
    Returns:
        True if product can be edited, False if locked
    """
    return not product.color_manually_edited


def edit_product_color_once(article_id: str):
    """
    Edit color information for a specific product (ONE TIME ONLY).
    
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
        
        # Check if product is already locked
        if not check_edit_permission(product):
            print("🔒 PRODUCT LOCKED")
            print("=" * 80)
            print(f"Product {article_id} has already been manually edited.")
            print("Color information is permanently locked and cannot be changed.")
            print()
            print("Current Color Information:")
            print(f"  Colors: {product.colors}")
            print(f"  Primary Color: {product.primary_color}")
            print(f"  Color Description: {product.color_description}")
            print("=" * 80)
            return
        
        print("⚠️  ONE-TIME EDIT WARNING")
        print("=" * 80)
        print("This is a ONE-TIME EDIT opportunity!")
        print("After saving changes, this product's colors will be PERMANENTLY LOCKED.")
        print("No further edits will be possible.")
        print("=" * 80)
        
        # Display current information
        print(f"Product: {article_id}")
        print(f"Name: {product.name}")
        print(f"Group: {product.product_group_name}")
        print(f"Department: {product.department_no}")
        print()
        print("Current Color Information:")
        print(f"  Colors: {product.colors or 'None'}")
        print(f"  Primary Color: {product.primary_color or 'None'}")
        print(f"  Color Description: {product.color_description or 'None'}")
        print()
        
        # Ask for confirmation to proceed
        proceed = input("Do you want to proceed with editing? This is your ONLY chance! (y/N): ").strip().lower()
        
        if proceed not in ['y', 'yes']:
            print("❌ Edit cancelled. Product remains unlocked for future editing.")
            return
        
        # Get new color information
        print()
        print("Enter new color information:")
        print("(Press Enter to keep current value)")
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
        
        # Final confirmation
        print()
        print("🔒 FINAL CONFIRMATION - PERMANENT LOCK")
        print("=" * 80)
        print("PROPOSED CHANGES:")
        print(f"Colors: {product.colors} → {new_colors}")
        print(f"Primary Color: {product.primary_color} → {new_primary}")
        print(f"Color Description: {product.color_description} → {new_description}")
        print()
        print("⚠️  WARNING: After saving, this product will be PERMANENTLY LOCKED!")
        print("No further color edits will ever be possible.")
        print("=" * 80)
        
        final_confirm = input("SAVE AND PERMANENTLY LOCK this product? (type 'LOCK' to confirm): ").strip()
        
        if final_confirm == 'LOCK':
            # Update the product and lock it
            product.colors = new_colors if new_colors else None
            product.primary_color = new_primary if new_primary else None
            product.color_description = new_description if new_description else None
            product.color_manually_edited = True  # PERMANENT LOCK
            
            db.commit()
            
            print()
            print("🔒 PRODUCT PERMANENTLY LOCKED")
            print("=" * 80)
            print("✅ Changes saved successfully!")
            print("🔒 Product is now permanently locked from further edits.")
            print()
            print("Final Color Information:")
            print(f"  Colors: {product.colors}")
            print(f"  Primary Color: {product.primary_color}")
            print(f"  Color Description: {product.color_description}")
            print("  Status: LOCKED ✅")
            print("=" * 80)
            
        else:
            print("❌ Changes cancelled. Product remains unlocked for future editing.")
            
    except Exception as e:
        logger.error(f"Error editing product {article_id}: {e}")
        db.rollback()
    finally:
        db.close()


def search_editable_products(search_term: str, limit: int = 10):
    """
    Search for products that can still be edited (not locked).
    
    Args:
        search_term: Search term to find products
        limit: Maximum number of products to show
    """
    db = SessionLocal()
    
    try:
        # Search for products that are not locked
        products = db.query(Product).filter(
            Product.name.ilike(f'%{search_term}%'),
            Product.color_manually_edited == False
        ).limit(limit).all()
        
        if not products:
            print(f"❌ No editable products found matching: {search_term}")
            return
        
        print("=" * 80)
        print(f"EDITABLE PRODUCTS FOR: {search_term}")
        print("=" * 80)
        
        # Display products
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.article_id} - {product.name}")
            print(f"   Colors: {product.colors or 'None'}")
            print(f"   Primary: {product.primary_color or 'None'}")
            print(f"   Status: ✅ EDITABLE (One-time edit available)")
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
                    edit_product_color_once(selected_product.article_id)
                    break
                else:
                    print(f"Please enter a number between 1 and {len(products)}")
                    
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
                
    except Exception as e:
        logger.error(f"Error searching products: {e}")
    finally:
        db.close()


def list_editable_products(limit: int = 20):
    """
    List products that can still be edited (not locked).
    
    Args:
        limit: Maximum number of products to show
    """
    db = SessionLocal()
    
    try:
        editable_products = db.query(Product).filter(
            Product.color_manually_edited == False
        ).limit(limit).all()
        
        locked_count = db.query(Product).filter(
            Product.color_manually_edited == True
        ).count()
        
        print("=" * 80)
        print(f"EDITABLE PRODUCTS (showing {len(editable_products)})")
        print("=" * 80)
        print(f"🔒 Locked products: {locked_count}")
        print(f"✅ Editable products: {len(editable_products)} (showing first {limit})")
        print("=" * 80)
        
        for i, product in enumerate(editable_products, 1):
            print(f"{i}. {product.article_id} - {product.name[:50]}...")
            print(f"   Colors: {product.colors or 'None'}")
            print(f"   Primary: {product.primary_color or 'None'}")
            print(f"   Status: ✅ EDITABLE")
            print()
            
    except Exception as e:
        logger.error(f"Error listing products: {e}")
    finally:
        db.close()


def list_locked_products(limit: int = 20):
    """
    List products that have been locked (manually edited).
    
    Args:
        limit: Maximum number of products to show
    """
    db = SessionLocal()
    
    try:
        locked_products = db.query(Product).filter(
            Product.color_manually_edited == True
        ).limit(limit).all()
        
        print("=" * 80)
        print(f"LOCKED PRODUCTS (showing {len(locked_products)})")
        print("=" * 80)
        print("These products have been manually edited and are permanently locked.")
        print("=" * 80)
        
        for i, product in enumerate(locked_products, 1):
            print(f"{i}. {product.article_id} - {product.name[:50]}...")
            print(f"   Colors: {product.colors}")
            print(f"   Primary: {product.primary_color}")
            print(f"   Description: {product.color_description[:60]}...")
            print(f"   Status: 🔒 LOCKED")
            print()
            
    except Exception as e:
        logger.error(f"Error listing locked products: {e}")
    finally:
        db.close()


def show_statistics():
    """Show statistics about editable vs locked products."""
    db = SessionLocal()
    
    try:
        total_products = db.query(Product).count()
        locked_products = db.query(Product).filter(Product.color_manually_edited == True).count()
        editable_products = total_products - locked_products
        
        print("=" * 80)
        print("COLOR EDIT STATISTICS")
        print("=" * 80)
        print(f"Total products: {total_products:,}")
        print(f"🔒 Locked products: {locked_products:,}")
        print(f"✅ Editable products: {editable_products:,}")
        print(f"Lock percentage: {locked_products/total_products*100:.1f}%")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Error showing statistics: {e}")
    finally:
        db.close()


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="One-Time Color Editor (Permanent Lock)")
    parser.add_argument('--article_id', type=str, help='Edit specific product by article ID (ONE TIME ONLY)')
    parser.add_argument('--search', type=str, help='Search for editable products')
    parser.add_argument('--list-editable', action='store_true', help='List products that can be edited')
    parser.add_argument('--list-locked', action='store_true', help='List products that are locked')
    parser.add_argument('--stats', action='store_true', help='Show edit statistics')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of results')
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    print("🔒 ONE-TIME COLOR EDITOR")
    print("=" * 80)
    print("⚠️  WARNING: Each product can only be edited ONCE!")
    print("After editing, products are permanently locked.")
    print("=" * 80)
    
    if args.article_id:
        edit_product_color_once(args.article_id)
    elif args.search:
        search_editable_products(args.search, args.limit)
    elif args.list_editable:
        list_editable_products(args.limit)
    elif args.list_locked:
        list_locked_products(args.limit)
    elif args.stats:
        show_statistics()
    else:
        print("Please specify an action:")
        print("  --article_id <id>     Edit specific product (ONE TIME ONLY)")
        print("  --search <term>       Search for editable products")
        print("  --list-editable       List products that can be edited")
        print("  --list-locked         List products that are locked")
        print("  --stats               Show edit statistics")
        print()
        print("Examples:")
        print("  python src/one_time_color_editor.py --article_id 0108775015")
        print("  python src/one_time_color_editor.py --search 'red dress'")
        print("  python src/one_time_color_editor.py --list-editable --limit 20")
        print("  python src/one_time_color_editor.py --stats")


if __name__ == "__main__":
    main()