# 📚 Complete Project Overview - Part 2: E-Commerce Features

## 🛒 PHASE 2: Shopping Features

### Step 2.1: Shopping Cart System

**Library Used: FastAPI + SQLAlchemy**

```python
# src/api_cart.py

Features Built:
1. View Cart (GET /cart)
   - Shows all items in user's cart
   - Calculates total price
   - Includes product details
   
2. Add to Cart (POST /cart/add)
   - Add products with quantity
   - Update quantity if already in cart
   - Validation for product existence
   
3. Update Quantity (POST /cart/update/{article_id})
   - Increase/decrease quantity
   - Remove if quantity = 0
   
4. Remove from Cart (POST /cart/remove/{article_id})
   - Delete specific item
   
5. Clear Cart (POST /cart/clear)
   - Empty entire cart
```

**Key Features:**
- Real-time cart updates
- Quantity management
- Price calculations
- User-specific carts (JWT protected)

---

### Step 2.2: Wishlist System

```python
# src/api_wishlist.py

Features Built:
1. View Wishlist (GET /wishlist)
   - All saved products
   
2. Add to Wishlist (POST /wishlist/add)
   - Save products for later
   
3. Remove from Wishlist (POST /wishlist/remove/{article_id})
   - Delete saved items
   
4. Move to Cart (POST /wishlist/move-to-cart/{article_id})
   - Transfer from wishlist to cart
```

---

### Step 2.3: Order Management System

```python
# src/api_orders.py

Features Built:
1. Checkout (POST /orders/checkout)
   - Create order from cart
   - Calculate total amount
   - Clear cart after order
   - Support for "Buy Now" (single product)
   
2. Order History (GET /orders)
   - List all user orders
   - Sorted by date (newest first)
   - Includes order items
   
3. Order Details (GET /orders/{order_id})
   - View specific order
   - All items and prices
   - Order status
```

**Key Features:**
- Transaction handling
- Order item tracking
- Price snapshot (price at time of purchase)
- Payment method tracking
- Idempotency support (prevent duplicate orders)

---

### Step 2.4: User Behavior Tracking

**Library Used: FastAPI + SQLAlchemy**

```python
# src/api_interactions.py

Features Built:
1. Record Interaction (POST /interactions/record)
   - Track: view, click, add_to_cart, purchase
   - Timestamp tracking
   - Value tracking (e.g., purchase amount)
   
2. Bulk Recording (POST /interactions/bulk)
   - Record multiple interactions at once
   
3. User History (GET /interactions/user)
   - View user's interaction history
   
4. Popular Items (GET /interactions/popular)
   - Most viewed/purchased products
   
5. Item Analytics (GET /interactions/item/{article_id}/top)
   - Top users for a product
```

**Purpose:**
- Data collection for ML training
- User behavior analytics
- Recommendation system input
- A/B testing support

---

