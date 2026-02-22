"""Create a test order with a product that has an image."""
from src.db import SessionLocal, User, Product, Order, OrderItem
from datetime import datetime

db = SessionLocal()

# Get first user
user = db.query(User).first()
if not user:
    print("No users found")
    exit(1)

print(f"User: {user.email} (ID: {user.id})")

# Get a product WITH image
product = db.query(Product).filter(
    Product.image_path.isnot(None),
    Product.image_path != ''
).first()

if not product:
    print("No products with images found")
    exit(1)

print(f"\nProduct: {product.name}")
print(f"Article ID: {product.article_id}")
print(f"Image: {product.image_path}")
print(f"Price: ${product.price:.2f}")

# Create order
order = Order(
    user_id=user.id,
    total_amount=product.price * 2,
    payment_method='test',
    payment_status='paid',
    created_at=datetime.utcnow()
)
db.add(order)
db.flush()

# Create order item
order_item = OrderItem(
    order_id=order.id,
    article_id=product.article_id,
    qty=2,
    price=product.price
)
db.add(order_item)

db.commit()

print(f"\n✓ Created Order #{order.id}")
print(f"  Total: ${order.total_amount:.2f}")
print(f"  Item: {product.article_id} x 2")
print(f"  Image should be: {product.image_path}")

db.close()

print("\nNow check the Orders page in your browser!")
