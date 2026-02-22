"""Test order images - check if image_path is being returned."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.db import SessionLocal, Order, OrderItem, Product

print("=" * 70)
print("ORDER IMAGES DEBUG")
print("=" * 70)

db = SessionLocal()

try:
    # Get first order
    order = db.query(Order).first()
    
    if not order:
        print("\n✗ No orders found")
        print("Create an order first by checking out")
        exit(1)
    
    print(f"\n✓ Found Order #{order.id}")
    print(f"  User ID: {order.user_id}")
    print(f"  Total: ${order.total_amount:.2f}")
    
    # Get order items
    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()
    
    print(f"\n  Order Items: {len(order_items)}")
    
    for i, item in enumerate(order_items, 1):
        print(f"\n  Item {i}:")
        print(f"    Article ID: {item.article_id}")
        print(f"    Quantity: {item.qty}")
        print(f"    Price: ${item.price:.2f}")
        
        # Get product details
        product = db.query(Product).filter(
            Product.article_id == item.article_id
        ).first()
        
        if product:
            print(f"    Product Name: {product.name}")
            print(f"    Image Path: {product.image_path}")
            print(f"    Has Image: {'✓ YES' if product.image_path else '✗ NO'}")
        else:
            print(f"    ✗ Product not found in database!")
    
    print("\n" + "=" * 70)
    print("✓ DEBUG COMPLETE")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
