"""
Database Migration: Add Color Lock Field

Adds a color_manually_edited field to track products that have been manually edited.
Once edited, colors cannot be changed again.

Usage:
    python src/migrate_add_color_lock.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.db import SessionLocal, engine, init_db

def migrate_add_color_lock():
    """Add color_manually_edited column to products table."""
    
    # Initialize database first
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(products)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'color_manually_edited' in columns:
            print("✓ color_manually_edited column already exists")
            return
        
        # Add the new column
        print("Adding color_manually_edited column to products table...")
        db.execute(text("ALTER TABLE products ADD COLUMN color_manually_edited BOOLEAN DEFAULT FALSE"))
        db.commit()
        
        print("✓ Successfully added color_manually_edited column")
        
        # Verify the column was added
        result = db.execute(text("PRAGMA table_info(products)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'color_manually_edited' in columns:
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
    print("DATABASE MIGRATION: ADD COLOR LOCK")
    print("=" * 60)
    
    migrate_add_color_lock()
    
    print("=" * 60)
    print("✓ MIGRATION COMPLETE")
    print("=" * 60)