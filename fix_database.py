"""
Fix Database - Add Missing Columns to Orders Table
"""

import sqlite3

def fix_database():
    print("Connecting to database...")
    conn = sqlite3.connect('project149.db')
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add payment_method if not exists
        if 'payment_method' not in columns:
            print("Adding payment_method column...")
            cursor.execute("ALTER TABLE orders ADD COLUMN payment_method VARCHAR(100) DEFAULT 'standard'")
            print("✓ payment_method added")
        else:
            print("✓ payment_method already exists")
        
        # Add payment_status if not exists
        if 'payment_status' not in columns:
            print("Adding payment_status column...")
            cursor.execute("ALTER TABLE orders ADD COLUMN payment_status VARCHAR(50) DEFAULT 'paid'")
            print("✓ payment_status added")
        else:
            print("✓ payment_status already exists")
        
        # Add client_order_id if not exists
        if 'client_order_id' not in columns:
            print("Adding client_order_id column...")
            cursor.execute("ALTER TABLE orders ADD COLUMN client_order_id VARCHAR(255)")
            print("✓ client_order_id added")
        else:
            print("✓ client_order_id already exists")
        
        conn.commit()
        print("\n✅ Database updated successfully!")
        print("\nNow restart your backend:")
        print("  python main.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
