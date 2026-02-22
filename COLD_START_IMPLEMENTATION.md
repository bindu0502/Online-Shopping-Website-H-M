# Cold-Start Recommendation Implementation

## Overview
Implemented cold-start recommendation logic for new users who have no activity (empty cart, wishlist, and orders).

## Implementation Details

### Backend Changes

#### 1. `src/personalized_recommend.py`
Added new function `get_category_based_recommendations()`:
- Fetches user's `preferred_categories` from database
- Queries products matching those categories
- Returns randomized product recommendations
- Includes proper reason text: "Based on your interest in {category}"

#### 2. Updated `generate_personalized_recommendations()`
- Added cold-start check at the beginning
- IF user has NO activity (cart/wishlist/orders empty):
  - Calls `get_category_based_recommendations()`
  - Returns 20 category-based recommendations
- ELSE:
  - Uses existing behavior-based recommendation logic

### Logic Flow

```
IF user.cart.length === 0 AND user.wishlist.length === 0 AND user.orders.length === 0
  THEN:
    categories = user.preferred_categories
    recommendedProducts = getProductsByCategories(categories)
    return recommendedProducts (20 items, randomized)
  ELSE:
    return behaviorBasedRecommendations(user)
```

### Database Requirements

The `users` table must have the `preferred_categories` field:
- Type: String (comma-separated categories)
- Example: "Shoes,Accessories,Garment Upper body"
- Set during user signup

### Available Categories

```
- Garment Upper body (40,371 products)
- Garment Lower body (18,702 products)
- Accessories (10,198 products)
- Underwear (5,291 products)
- Shoes (4,890 products)
- Garment Full body (12,105 products)
- Swimwear (3,080 products)
- Socks & Tights (2,373 products)
- Nightwear (1,833 products)
- And more...
```

## Testing

### Test User Created
- Email: `coldstart@example.com`
- Password: `password123`
- Preferred Categories: "Shoes,Accessories,Garment Upper body"
- Activity: None (empty cart, wishlist, orders)

### Test Scripts

1. **Direct Function Test**:
   ```bash
   python debug_coldstart.py
   ```
   Expected: 20 recommendations from preferred categories

2. **API Test** (requires server restart):
   ```bash
   python test_api_detailed.py
   ```
   Expected: 20 recommendations via `/foryou` endpoint

### Manual Testing Steps

1. **Restart the backend server** (important for code reload):
   ```bash
   # Stop existing server (Ctrl+C or kill process)
   # Start fresh server
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test via API**:
   ```bash
   # Login as cold-start user
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"coldstart@example.com","password":"password123"}'
   
   # Get token from response, then:
   curl -X GET http://localhost:8000/foryou \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

3. **Test via Frontend**:
   - Login as `coldstart@example.com` / `password123`
   - Navigate to "For You" page
   - Should see 20 products from Shoes, Accessories, and Garment Upper body categories
   - Should NOT see "No Recommendations Yet" message

## Expected Behavior

### New User (No Activity)
- User selects categories during signup (e.g., "Shoes")
- User logs in
- Navigates to "For You" page
- **Sees**: 20 products from selected categories
- **Does NOT see**: "No Recommendations Yet" message

### User with Activity
- User has items in cart/wishlist/orders
- Navigates to "For You" page
- **Sees**: Behavior-based recommendations (similar products)
- Existing logic unchanged

## Frontend Compatibility

The frontend (`frontend/src/pages/ForYou.jsx`) already handles this correctly:
- If `recommendations.length > 0`: Renders product cards
- If `recommendations.length === 0`: Shows empty state message

No frontend changes needed!

## Verification Checklist

✅ `preferred_categories` field exists in User table
✅ Categories are saved during signup (comma-separated format)
✅ Category names match product table exactly (case-sensitive)
✅ Products have `category` field populated
✅ For You API calls category-based logic when no activity
✅ Frontend renders returned products correctly
✅ Empty state only shows when truly no recommendations available

## Notes

- Recommendations are randomized on each request for variety
- Limit set to 20 products for cold-start users
- Products must have `image_path` to be included
- If user has no preferred categories, returns empty array (graceful fallback)
- If no products exist in selected categories, returns empty array

## Server Restart Required

⚠️ **IMPORTANT**: After code changes, you must restart the uvicorn server for changes to take effect, even with `--reload` flag.

The auto-reload may not detect changes in imported modules. Always restart manually after updating `src/personalized_recommend.py`.
