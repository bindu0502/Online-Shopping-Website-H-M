# 📚 Complete Project Overview - Part 5: Personalization & Frontend

## 💝 PHASE 6: Personalized Recommendation Systems

### Step 6.1: "For You" Page (Similarity-Based)

**Libraries Used: Pandas, NumPy, SQLAlchemy**

```python
# src/personalized_recommend.py

Algorithm:
1. Get User Activity
   - Cart items
   - Wishlist items
   - Order history
   
2. For Each Activity Product, Find Similar Products
   Similarity Scoring:
   - Name similarity (Jaccard): +5.0 points
   - Same primary color: +4.0 points
   - Same category: +3.0 points
   - Color overlap: +2.0 per color
   - Similar price (±20%): +1.5 points
   
3. Ranking Priority
   - Same category + color + similar name: 12+ points
   - Same category + color: 7+ points
   - Same category + similar name: 8+ points
   - Same category only: 3 points
   
4. Randomization
   - Shuffle for variety
   - Different products each visit
   - 3-5 recommendations per activity product
```

**Key Features:**
- No ML model needed (fast)
- Works immediately after user activity
- Name similarity using keyword extraction
- Optimized database queries

---

### Step 6.2: Cold-Start Recommendations

**Problem:** New users have no activity (empty cart/wishlist/orders)

**Solution: Category-Based Recommendations**

```python
# src/personalized_recommend.py - get_category_based_recommendations()

Logic:
1. Check User Activity
   IF cart.empty AND wishlist.empty AND orders.empty:
      → Cold-start user
   
2. Fetch Preferred Categories
   - Selected during signup
   - Example: ["Shoes", "Accessories"]
   
3. Query Products
   - WHERE category IN (preferred_categories)
   - AND image_path IS NOT NULL
   - LIMIT 20
   
4. Randomize & Return
   - Shuffle for variety
   - Return 20 products
```

**Database Addition:**
- `preferred_categories` field in User table
- Comma-separated category list
- Set during signup

**Result:**
- New users see 20 relevant products immediately
- No "No Recommendations Yet" message
- Solves cold-start problem

---

### Step 6.3: Category Pages & Navigation

```python
# src/api_categories.py
# frontend/src/pages/Category.jsx

Features Built:
1. Category List API
   - GET /categories
   - Returns all categories with product counts
   
2. Category Products API
   - GET /categories/{name}/products
   - Paginated product list
   - Filtering support
   
3. Category Dropdown (Navbar)
   - Shows all categories
   - Product counts
   - Click to navigate
   
4. Category Page
   - Infinite scrolling
   - Filter by price, color
   - Sort options
```

---

## 🎨 PHASE 7: Frontend Development

### Step 7.1: React Application Setup

**Libraries Used:**
- **React 19.2.0** - UI library
- **Vite 7.2.4** - Build tool
- **React Router DOM 7.9.6** - Routing
- **TailwindCSS 4.1.17** - Styling
- **Axios 1.13.2** - HTTP client

```javascript
// Frontend Structure
frontend/
├── src/
│   ├── pages/          # Page components
│   ├── components/     # Reusable components
│   ├── auth/          # Auth components
│   └── api/           # API client
```

---

### Step 7.2: Pages Built

**1. Authentication Pages**
```javascript
// src/auth/Login.jsx
- Email/password form
- JWT token storage
- Error handling
- Redirect after login

// src/auth/Signup.jsx
- Registration form
- Category preference selection (1-3 categories)
- Password validation
- Auto-login after signup
```

**2. Product Pages**
```javascript
// src/pages/Home.jsx
- Product grid (infinite scroll)
- Filter panel (price, category, color)
- Sort options
- Search integration

// src/pages/Product.jsx
- Product details
- Image display
- Add to cart/wishlist
- Similar products section

// src/pages/Category.jsx
- Category-specific products
- Infinite scrolling
- Filters and sorting
```

**3. Shopping Pages**
```javascript
// src/pages/Cart.jsx
- Cart items list
- Quantity controls
- Total calculation
- Checkout button

// src/pages/Wishlist.jsx
- Saved products
- Move to cart
- Remove items

// src/pages/Checkout.jsx
- Order summary
- Payment method selection
- Place order
```

**4. Recommendation Pages**
```javascript
// src/pages/ForYou.jsx
- Personalized recommendations
- Based on user activity
- Cold-start handling
- Product cards

// src/pages/Recommendations.jsx
- ML-powered recommendations
- Uses LightGBM model
- Score display
```

**5. Other Pages**
```javascript
// src/pages/Orders.jsx
- Order history
- Order details
- Order status

// src/pages/Search.jsx
- AI-powered search
- Search results
- Filters
```

---

