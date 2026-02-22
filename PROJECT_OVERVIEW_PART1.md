# 📚 Complete Project Overview - Part 1: Foundation & Backend

## 🎯 Project Goal

Built a **full-stack E-Commerce platform with ML-powered recommendations** - similar to H&M, Amazon, or any modern online shopping platform with personalized product suggestions.

---

## 📊 Project Scale

- **105,542 products** in catalog
- **7 database tables** with relationships
- **15+ API endpoints** for different features
- **10+ frontend pages** with routing
- **3 recommendation systems** (ML-based, similarity-based, cold-start)
- **AI-powered search** using Google Gemini

---

## 🏗️ PHASE 1: Database & Backend Foundation

### Step 1.1: Database Design (SQLAlchemy + SQLite)

**Library Used: SQLAlchemy 2.0.23**

Created 7 interconnected database tables:

```python
# src/db.py

1. User Table
   - id, email, password_hash, name
   - preferred_categories (for cold-start)
   - Relationships: cart, wishlist, orders, interactions

2. Product Table  
   - article_id, name, price, category
   - image_path, colors, primary_color
   - color_description, description
   - Relationships: cart_items, wishlist_items, order_items

3. CartItem Table
   - Links users to products in their cart
   - Tracks quantity

4. WishlistItem Table
   - Saves products users want to buy later

5. Order Table
   - Stores completed purchases
   - payment_method, payment_status, total_amount

6. OrderItem Table
   - Individual items in each order
   - Tracks price at time of purchase

7. UserInteraction Table
   - Tracks user behavior (views, clicks, purchases)
   - Used for ML training and analytics
```

**Key Libraries:**
- **SQLAlchemy**: ORM for database operations
- **Bcrypt**: Password hashing for security
- **SQLite**: Development database (can switch to PostgreSQL)

**What We Built:**
- Complete database schema with relationships
- Password hashing utilities
- Database initialization scripts
- Migration scripts for schema updates

---

### Step 1.2: Authentication System (JWT)

**Libraries Used: python-jose, PyJWT, bcrypt**

```python
# src/api_auth.py

Features Built:
1. User Registration (Signup)
   - Email validation
   - Password hashing with bcrypt
   - Category preference selection
   
2. User Login
   - JWT token generation
   - Token expiration (24 hours)
   - Secure password verification
   
3. Protected Routes
   - Token validation middleware
   - get_current_user() dependency
   - Authorization headers
```

**Security Features:**
- Passwords hashed with bcrypt (never stored plain text)
- JWT tokens for stateless authentication
- Token-based API protection
- CORS middleware for frontend access

---

### Step 1.3: Product Management API

**Library Used: FastAPI 0.104.1**

```python
# src/api_products.py

Endpoints Built:
1. GET /products
   - List all products with pagination
   - Filter by category, price range, colors
   - Search by name
   - Sort by price, name, popularity
   
2. GET /products/{article_id}
   - Get single product details
   - Includes all metadata
   
3. GET /products/{article_id}/similar
   - Find similar products
   - Based on category, color, price
```

**Key Features:**
- Query parameter validation with Pydantic
- Efficient database queries
- Image path handling
- Error handling and status codes

---

