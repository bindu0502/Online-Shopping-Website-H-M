"""
Product Import Script

Imports H&M product catalog from articles.csv into the SQLAlchemy database.
Handles duplicates safely and provides progress updates.

Usage:
    python src/import_products.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy.exc import IntegrityError
from src.db import SessionLocal, Product, init_db


def import_products():
    """
    Import products from articles.csv into the database.
    
    Reads the H&M articles dataset and inserts products into the Product table.
    Skips duplicates and provides progress updates every 10,000 rows.
    """
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Load articles CSV
    csv_path = "Project149/datasets/articles.csv/articles.csv"
    print(f"Loading products from {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} products from CSV")
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    # Create database session
    db = SessionLocal()
    
    # Track statistics
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        print("Starting import...")
        
        # Batch size for commits
        BATCH_SIZE = 1000
        batch = []
        
        for idx, row in df.iterrows():
            try:
                # Extract fields
                article_id = str(row['article_id']).zfill(10)  # Pad with zeros
                product_type_name = row.get('product_type_name', 'Unknown Product')
                product_group_name = row.get('product_group_name', None)
                department_no = row.get('department_no', None)
                
                # Convert department_no to int if not null
                if pd.notna(department_no):
                    department_no = int(department_no)
                else:
                    department_no = None
                
                # Use prod_name if available, otherwise use product_type_name
                name = row.get('prod_name', product_type_name)
                if pd.isna(name) or name == '':
                    name = product_type_name
                
                # Create product object
                product = Product(
                    article_id=article_id,
                    name=str(name)[:500],  # Limit to 500 chars
                    price=29.99,  # Default price
                    department_no=department_no,
                    product_group_name=str(product_group_name)[:255] if pd.notna(product_group_name) else None,
                    image_path=None
                )
                
                # Add to batch
                batch.append(product)
                
                # Commit batch when it reaches BATCH_SIZE
                if len(batch) >= BATCH_SIZE:
                    try:
                        db.bulk_save_objects(batch)
                        db.commit()
                        imported_count += len(batch)
                        batch = []
                    except IntegrityError as e:
                        # If batch fails, try one by one
                        db.rollback()
                        for p in batch:
                            try:
                                db.add(p)
                                db.commit()
                                imported_count += 1
                            except IntegrityError:
                                db.rollback()
                                skipped_count += 1
                        batch = []
                
                # Progress update every 10,000 rows
                if (idx + 1) % 10000 == 0:
                    print(f"Progress: {idx + 1}/{len(df)} rows processed "
                          f"(Imported: {imported_count}, Skipped: {skipped_count}, Errors: {error_count})")
                
            except Exception as e:
                # Other errors
                error_count += 1
                if error_count <= 5:  # Only print first 5 errors
                    print(f"Error on row {idx}: {e}")
        
        # Commit remaining batch
        if batch:
            try:
                db.bulk_save_objects(batch)
                db.commit()
                imported_count += len(batch)
            except IntegrityError:
                # If batch fails, try one by one
                db.rollback()
                for p in batch:
                    try:
                        db.add(p)
                        db.commit()
                        imported_count += 1
                    except IntegrityError:
                        db.rollback()
                        skipped_count += 1
        
        print("\n" + "="*60)
        print(f"Import complete!")
        print(f"Imported {imported_count} products into the database.")
        print(f"Skipped {skipped_count} duplicates.")
        if error_count > 0:
            print(f"Encountered {error_count} errors.")
        print("="*60)
        
    except Exception as e:
        print(f"Fatal error during import: {e}")
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    import_products()
