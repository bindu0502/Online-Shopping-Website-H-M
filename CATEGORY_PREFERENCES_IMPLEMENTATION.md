# ✅ Category Preferences for New Users - Implementation Guide

## What's Been Done

### 1. Database Migration ✅
- Added `preferred_categories` column to User table
- Migration completed successfully
- Column stores comma-separated category names

### 2. Backend Updates ✅
- Updated `User` model in `src/db.py` with `preferred_categories` field
- Updated `SignupIn` schema to accept `preferred_categories: List[str]`
- Updated signup endpoint with validation:
  - Minimum 1 category required
  - Maximum 3 categories allowed
  - Validates against allowed categories
  - Stores as comma-separated string

### 3. Valid Categories
```
- Garment Upper body
- Garment Lower body
- Garment Full body
- Accessories
- Underwear
- Shoes
- Swimwear
- Socks & Tights
- Nightwear
```

## What Still Needs to Be Done

### 1. Update Signup.jsx Frontend
Add category selection UI with checkboxes. The form should include:
- Email field
- Password field
- Confirm Password field
- Name field
- **Category selection (checkboxes)** - NEW
- Validation for 1-3 categories

### 2. Update For You Recommendation Logic
Modify `src/personalized_recommend.py` to:
```python
def generate_personalized_recommendations(user_id, db, recommendations_per_product=5):
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    # Check if user has activity
    activity_products = get_user_activity_products(user_id, db)
    
    if not activity_products and user.preferred_categories:
        # NEW USER: Use category preferences
        categories = user.preferred_categories.split(',')
        return get_recommendations_by_categories(categories, db, limit=20)
    elif activity_products:
        # EXISTING USER: Use behavior-based recommendations
        return [existing logic...]
    else:
        # Fallback: random products
        return []
```

### 3. Create Category-Based Recommendation Function
```python
def get_recommendations_by_categories(categories: List[str], db: Session, limit: int = 20):
    """Get products from preferred categories for new users."""
    products = db.query(Product).filter(
        Product.product_group_name.in_(categories),
        Product.image_path.isnot(None)
    ).order_by(func.random()).limit(limit).all()
    
    return [format_product(p) for p in products]
```

## Testing

### Test Signup with Categories:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "password123",
    "name": "New User",
    "preferred_categories": ["Accessories", "Shoes"]
  }'
```

### Expected Behavior:
1. New user signs up with 2 categories
2. User logs in
3. Clicks "For You"
4. Sees products only from Accessories and Shoes
5. User adds items to cart
6. System switches to behavior-based recommendations

## Files Modified:
- ✅ `src/db.py` - Added preferred_categories field
- ✅ `src/api_auth.py` - Updated signup with validation
- ✅ `src/migrate_add_preferred_categories.py` - Migration script
- ⏳ `frontend/src/auth/Signup.jsx` - Needs category UI
- ⏳ `src/personalized_recommend.py` - Needs fallback logic

## Status: 70% Complete
Backend is ready. Frontend signup form and recommendation fallback logic need to be completed.
