"""
Database Migration: Add Product Description Field

Adds a description field to the products table to store detailed product descriptions from articles.csv.

Usage:
    python src/migrate_add_description.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.db import SessionLocal, engine, init_db

def migrate_add_description():
    """Add description column to products table."""
    
    # Initialize database first
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(products)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'description' in columns:
            print("✓ description column already exists")
            return
        
        # Add the new column
        print("Adding description column to products table...")
        db.execute(text("ALTER TABLE products ADD COLUMN description TEXT"))
        db.commit()
        
        print("✓ Successfully added description column")
        
        # Verify the column was added
        result = db.execute(text("PRAGMA table_info(products)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'description' in columns:
            print("✓ Migration verified successfully")
        else:
            print("✗ Migration verification failed")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: ADD PRODUCT DESCRIPTION")
    print("=" * 60)
    
    migrate_add_description()
    
    print("=" * 60)
    print("✓ MIGRATION COMPLETE")
    print("=" * 60)