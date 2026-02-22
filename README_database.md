# Database Module

## Overview

The `src/db.py` module provides SQLAlchemy ORM models and database utilities for the recommendation system. It includes user management, product catalog, interaction tracking, shopping cart, and order management.

## Database Configuration

### Connection String

The database connection is configured via the `DATABASE_URL` environment variable:

```bash
# SQLite (default)
export DATABASE_URL="sqlite:///project149.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost/project149"

# MySQL
export DATABASE_URL="mysql+pymysql://user:password@localhost/project149"
```

If `DATABASE_URL` is not set, defaults to SQLite: `sqlite:///project149.db`

## Models

### User

User authentication and profile management.

**Attributes:**
- `id` (int, PK) - User ID
- `email` (str, unique) - Email address
- `password_hash` (str) - Bcrypt hashed password
- `name` (str) - Display name
- `created_at` (datetime) - Account creation timestamp

**Relationships:**
- `interactions` - User's interaction history
- `cart_items` - Items in shopping cart
- `orders` - Order history

### Product

Product catalog with article information.

**Attributes:**
- `article_id` (str, PK) - Article identifier
- `name` (str) - Product name
- `price` (float) - Product price
- `department_no` (int) - Department number
- `product_group_name` (str) - Product category
- `image_path` (str, nullable) - Path to product image

**Relationships:**
- `interactions` - Interactions with this product
- `cart_items` - Cart items containing this product
- `order_items` - Order items containing this product

### UserInteraction

Tracks user behavior for recommendation training.

**Attributes:**
- `id` (int, PK) - Interaction ID
- `user_id` (int, FK) - User ID
- `article_id` (str, FK) - Article ID
- `event_type` (str) - Event type: `view`, `click`, `add_to_cart`, `purchase`
- `value` (float, nullable) - Optional value (e.g., purchase amount)
- `created_at` (datetime) - Interaction timestamp

**Relationships:**
- `user` - User who performed the interaction
- `product` - Product that was interacted with

### CartItem

Shopping cart items.

**Attributes:**
- `id` (int, PK) - Cart item ID
- `user_id` (int, FK) - User ID
- `article_id` (str, FK) - Article ID
- `qty` (int) - Quantity

**Relationships:**
- `user` - Cart owner
- `product` - Product in cart

### Order

Completed purchase orders.

**Attributes:**
- `id` (int, PK) - Order ID
- `user_id` (int, FK) - User ID
- `total_amount` (float) - Total order amount
- `created_at` (datetime) - Order timestamp

**Relationships:**
- `user` - User who placed the order
- `items` - Items in the order

### OrderItem

Individual items in an order.

**Attributes:**
- `id` (int, PK) - Order item ID
- `order_id` (int, FK) - Order ID
- `article_id` (str, FK) - Article ID
- `qty` (int) - Quantity ordered
- `price` (float) - Price at time of purchase

**Relationships:**
- `order` - Order containing this item
- `product` - Product that was ordered

## Functions

### Database Initialization

**`init_db()`**

Creates all database tables. Safe to call multiple times.

```python
from src.db import init_db

init_db()
# Output: Database initialized
```

### Session Management

**`SessionLocal`**

Session factory for creating database sessions.

```python
from src.db import SessionLocal

db = SessionLocal()
try:
    users = db.query(User).all()
finally:
    db.close()
```

**`get_db()`**

Generator function for dependency injection (useful with FastAPI).

```python
from src.db import get_db

db = next(get_db())
users = db.query(User).all()
db.close()
```

### Password Utilities

**`hash_password(password: str) -> str`**

Hash a password using bcrypt.

```python
from src.db import hash_password

hashed = hash_password("mypassword123")
print(hashed)
# Output: $2b$12$...
```

**`verify_password(password: str, password_hash: str) -> bool`**

Verify a password against a hash.

```python
from src.db import verify_password, hash_password

hashed = hash_password("mypassword123")
verify_password("mypassword123", hashed)  # True
verify_password("wrongpassword", hashed)  # False
```

## Usage Examples

### Create User

```python
from src.db import SessionLocal, User, hash_password

db = SessionLocal()

user = User(
    email="user@example.com",
    password_hash=hash_password("secure_password"),
    name="John Doe"
)
db.add(user)
db.commit()
db.refresh(user)

print(f"Created user: {user.id}")
db.close()
```

### Add Products

```python
from src.db import SessionLocal, Product

db = SessionLocal()

product = Product(
    article_id="123456789",
    name="Cotton T-Shirt",
    price=29.99,
    department_no=1234,
    product_group_name="Garment Upper body",
    image_path="/images/123456789.jpg"
)
db.add(product)
db.commit()

db.close()
```

### Track User Interactions

```python
from src.db import SessionLocal, UserInteraction

db = SessionLocal()

# User viewed a product
interaction = UserInteraction(
    user_id=1,
    article_id="123456789",
    event_type="view"
)
db.add(interaction)

# User added to cart
interaction2 = UserInteraction(
    user_id=1,
    article_id="123456789",
    event_type="add_to_cart"
)
db.add(interaction2)

db.commit()
db.close()
```

### Manage Shopping Cart

```python
from src.db import SessionLocal, CartItem

db = SessionLocal()

# Add item to cart
cart_item = CartItem(
    user_id=1,
    article_id="123456789",
    qty=2
)
db.add(cart_item)
db.commit()

# Get user's cart
cart = db.query(CartItem).filter(CartItem.user_id == 1).all()
for item in cart:
    print(f"Article: {item.article_id}, Qty: {item.qty}")

db.close()
```

### Create Order

```python
from src.db import SessionLocal, Order, OrderItem

db = SessionLocal()

# Create order
order = Order(
    user_id=1,
    total_amount=59.98
)
db.add(order)
db.commit()

# Add order items
order_item = OrderItem(
    order_id=order.id,
    article_id="123456789",
    qty=2,
    price=29.99
)
db.add(order_item)
db.commit()

db.close()
```

### Query with Relationships

```python
from src.db import SessionLocal, User

db = SessionLocal()

user = db.query(User).filter(User.id == 1).first()

# Access relationships
print(f"User: {user.name}")
print(f"Interactions: {len(user.interactions)}")
print(f"Cart items: {len(user.cart_items)}")
print(f"Orders: {len(user.orders)}")

# Get user's purchase history
for order in user.orders:
    print(f"Order {order.id}: ${order.total_amount}")
    for item in order.items:
        print(f"  - {item.article_id} x{item.qty} @ ${item.price}")

db.close()
```

### Query Interactions by Type

```python
from src.db import SessionLocal, UserInteraction

db = SessionLocal()

# Get all views
views = db.query(UserInteraction).filter(
    UserInteraction.event_type == 'view'
).all()

# Get user's recent interactions
recent = db.query(UserInteraction).filter(
    UserInteraction.user_id == 1
).order_by(UserInteraction.created_at.desc()).limit(10).all()

# Get product's interaction count
from sqlalchemy import func

interaction_counts = db.query(
    UserInteraction.article_id,
    func.count(UserInteraction.id).label('count')
).group_by(UserInteraction.article_id).all()

db.close()
```

## Database Schema

```
users
├── id (PK)
├── email (unique)
├── password_hash
├── name
└── created_at

products
├── article_id (PK)
├── name
├── price
├── department_no
├── product_group_name
└── image_path

user_interactions
├── id (PK)
├── user_id (FK → users.id)
├── article_id (FK → products.article_id)
├── event_type
├── value
└── created_at

cart_items
├── id (PK)
├── user_id (FK → users.id)
├── article_id (FK → products.article_id)
└── qty

orders
├── id (PK)
├── user_id (FK → users.id)
├── total_amount
└── created_at

order_items
├── id (PK)
├── order_id (FK → orders.id)
├── article_id (FK → products.article_id)
├── qty
└── price
```

## Testing

Run the test script to verify all functionality:

```bash
python test_db.py
```

Expected output:
```
============================================================
DATABASE MODULE TEST
============================================================

1. Initializing database...
Database initialized

2. Testing password hashing...
   Original: test_password_123
   Hashed: $2b$12$...
   Verify correct: True
   Verify wrong: False

3. Creating test user...
   Created: <User(id=1, email='test@example.com', name='Test User')>

...

============================================================
✓ ALL TESTS PASSED
============================================================
```

## Integration with Recommendation System

### Tracking User Behavior

```python
# When user views a product
interaction = UserInteraction(
    user_id=current_user.id,
    article_id=product_id,
    event_type="view"
)
db.add(interaction)
db.commit()
```

### Building User Profiles

```python
# Get user's recent interactions for recommendations
recent_interactions = db.query(UserInteraction).filter(
    UserInteraction.user_id == user_id,
    UserInteraction.created_at >= datetime.now() - timedelta(days=30)
).all()

# Get user's purchase history
purchases = db.query(UserInteraction).filter(
    UserInteraction.user_id == user_id,
    UserInteraction.event_type == 'purchase'
).all()
```

### Generating Recommendations

```python
# Load trained model
import joblib
model = joblib.load('models/lgbm_v1.pkl')

# Get candidates for user
# ... (use retrieval.py to generate candidates)

# Predict scores
predictions = model.predict(candidate_features)

# Get top recommendations
top_products = candidates.nlargest(10, 'score')['article_id'].tolist()

# Fetch product details
recommended_products = db.query(Product).filter(
    Product.article_id.in_(top_products)
).all()
```

## Dependencies

```bash
pip install sqlalchemy bcrypt
```

## Environment Variables

- `DATABASE_URL` - Database connection string (optional, defaults to SQLite)

## Notes

- All timestamps use UTC
- Passwords are hashed with bcrypt (salt rounds: 12)
- Foreign key constraints are enforced
- Cascade deletes are configured for relationships
- Indexes are created on frequently queried columns
