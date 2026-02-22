"""Add real shorts and cap products to cart."""
from src.db import SessionLocal, User, Product, CartItem

db = SessionLocal()

user = db.query(User).first()
print(f"User: {user.email}")

# Find shorts
shorts = db.query(Product).filter(
    Product.product_group_name.like('%Short%'),
    Product.image_path.isnot(None)
).first()

# Find cap/accessories
cap = db.query(Product).filter(
    Product.product_group_name.like('%Accessories%'),
    Product.image_path.isnot(None)
).first()

if not cap:
    cap = db.query(Product).filter(
        Product.name.like('%cap%'),
        Product.image_path.isnot(None)
    ).first()

if shorts:
    print(f"\nAdding shorts: {shorts.name}")
    print(f"  Category: {shorts.product_group_name}")
    print(f"  Color: {shorts.primary_color}")
    
    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.article_id == shorts.article_id
    ).first()
    
    if not existing:
        cart_item = CartItem(
            user_id=user.id,
            article_id=shorts.article_id,
            qty=1
        )
        db.add(cart_item)
        print("  ✓ Added to cart")
    else:
        print("  Already in cart")

if cap:
    print(f"\nAdding cap/accessory: {cap.name}")
    print(f"  Category: {cap.product_group_name}")
    print(f"  Color: {cap.primary_color}")
    
    existing = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.article_id == cap.article_id
    ).first()
    
    if not existing:
        cart_item = CartItem(
            user_id=user.id,
            article_id=cap.article_id,
            qty=1
        )
        db.add(cart_item)
        print("  ✓ Added to cart")
    else:
        print("  Already in cart")

db.commit()
db.close()

print("\n✓ Cart updated! Refresh the For You page.")
