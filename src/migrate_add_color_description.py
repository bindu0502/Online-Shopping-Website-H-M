"""
Database Migration: Add Color Description Field

Adds a color_description field to the products table to store detailed color descriptions.

Usage:
    python src/migrate_add_color_description.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.db import SessionLocal, engine, init_db

def migrate_add_color_description():
    """Add color_description column to products table."""
    
    # Initialize database first
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(products)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'color_description' in columns:
            print("✓ color_description column already exists")
            return
        
        # Add the new column
        print("Adding color_description column to products table...")
        db.execute(text("ALTER TABLE products ADD COLUMN color_description TEXT"))
        db.commit()
        
        print("✓ Successfully added color_description column")
        
        # Verify the column was added
        result = db.execute(text("PRAGMA table_info(products)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'color_description' in columns:
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
    print("DATABASE MIGRATION: ADD COLOR DESCRIPTION")
    print("=" * 60)
    
    migrate_add_color_description()
    
    print("=" * 60)
    print("✓ MIGRATION COMPLETE")
    print("=" * 60)