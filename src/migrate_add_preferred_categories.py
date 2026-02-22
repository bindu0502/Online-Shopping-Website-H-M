"""
Database Migration: Add preferred_categories to User table

Adds a preferred_categories column to store user's category preferences
during signup for cold-start recommendations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import Column, String, text
from src.db import engine, SessionLocal, User

def migrate():
    """Add preferred_categories column to users table."""
    print("=" * 70)
    print("MIGRATION: Add preferred_categories to User table")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'preferred_categories' in columns:
            print("\n✓ Column 'preferred_categories' already exists")
            return
        
        print("\nAdding 'preferred_categories' column...")
        
        # Add column (SQLite syntax)
        db.execute(text(
            "ALTER TABLE users ADD COLUMN preferred_categories TEXT"
        ))
        db.commit()
        
        print("✓ Column added successfully")
        
        # Verify
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'preferred_categories' in columns:
            print("✓ Migration verified")
        else:
            print("✗ Migration failed - column not found")
        
        print("\n" + "=" * 70)
        print("✓ MIGRATION COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Migration error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
