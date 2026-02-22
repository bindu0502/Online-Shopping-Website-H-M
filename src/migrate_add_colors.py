"""
Database Migration: Add Color Columns

Adds color and primary_color columns to the products table.

Usage:
    python src/migrate_add_colors.py
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import DATABASE_URL


def migrate_database():
    """Add color columns to products table."""
    
    # Extract database path from URL
    if DATABASE_URL.startswith('sqlite:///'):
        db_path = DATABASE_URL.replace('sqlite:///', '')
    else:
        print(f"Unsupported database URL: {DATABASE_URL}")
        return False
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Current columns in products table: {columns}")
        
        # Add colors column if it doesn't exist
        if 'colors' not in columns:
            print("Adding 'colors' column...")
            cursor.execute("ALTER TABLE products ADD COLUMN colors VARCHAR(255)")
            print("✓ Added 'colors' column")
        else:
            print("✓ 'colors' column already exists")
        
        # Add primary_color column if it doesn't exist
        if 'primary_color' not in columns:
            print("Adding 'primary_color' column...")
            cursor.execute("ALTER TABLE products ADD COLUMN primary_color VARCHAR(50)")
            print("✓ Added 'primary_color' column")
        else:
            print("✓ 'primary_color' column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(products)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"Updated columns in products table: {new_columns}")
        
        # Close connection
        conn.close()
        
        print("\n✓ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: ADD COLOR COLUMNS")
    print("=" * 60)
    
    print(f"Database URL: {DATABASE_URL}")
    
    success = migrate_database()
    
    if success:
        print("\nNext steps:")
        print("1. Run: python src/update_product_colors.py --test")
        print("2. Run: python src/update_product_colors.py --limit 100")
        print("3. Restart the backend server")
    else:
        print("\nMigration failed. Please check the error messages above.")
    
    print("\n" + "=" * 60)