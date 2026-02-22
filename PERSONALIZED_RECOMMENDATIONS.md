# Personalized Recommendations - How It Works

## Overview

Your e-commerce platform now has **intelligent, personalized recommendations** that adapt to your behavior in real-time!

## 🎯 How Recommendations Work

### What Influences Your Recommendations

The system tracks and learns from:

1. **🛒 Purchases** (Buy Now + Checkout)
   - Products you've bought
   - Purchase frequency
   - Purchase recency
   - Total spending

2. **👁️ Product Views**
   - Products you've clicked on
   - Time spent viewing
   - View frequency

3. **❤️ Wishlist Items**
   - Products you've saved
   - Wishlist additions/removals

4. **🛍️ Cart Activity**
   - Products added to cart
   - Cart abandonment patterns

5. **📊 Interaction Patterns**
   - Categories you browse
   - Price ranges you prefer
   - Departments you shop in

### The ML Pipeline

```
Your Actions → User Interactions DB → ML Model → Personalized Recommendations
```

**Step-by-Step:**

1. **You interact** (view, cart, wishlist, purchase)
2. **System records** interaction in database
3. **ML model analyzes** your behavior patterns
4. **Recommendations update** based on new data
5. **You see** personalized products in "Recommended For You"

## 🔄 Auto-Refresh Feature

### Automatic Updates
- Recommendations refresh **every 30 seconds**
- Picks up your latest interactions automatically
- No page reload needed!

### Manual Refresh
- Click **"🔄 Update"** button in recommendations section
- Instantly fetches new recommendations
- Based on your most recent activity

## 📈 How to See It in Action

### Test the Personalization:

1. **Browse Products**
   - Click on several products in a specific category (e.g., shoes)
   - Go back to Home page
   - Click "🔄 Update" on recommendations
   - You'll see more products from that category!

2. **Add to Wishlist**
   - Add 3-4 products to wishlist
   - Wait 30 seconds or click "🔄 Update"
   - Recommendations will include similar items

3. **Make Purchases**
   - Buy a product using "Buy Now"
   - Return to Home page
   - Recommendations will adapt to your purchase

4. **Add to Cart**
   - Add items to cart
   - Check recommendations
   - You'll see complementary products

## 🧠 ML Model Features

The recommendation system uses:

- **LightGBM Model** - Fast gradient boosting
- **Feature Engineering** - 50+ behavioral features
- **Retrieval System** - Candidate generation
- **Collaborative Filtering** - Learn from similar users
- **Content-Based Filtering** - Similar product attributes

### Recommendation Factors:

- **Popularity** - Trending products
- **Personalization** - Your unique preferences
- **Recency** - Recent interactions weighted higher
- **Diversity** - Mix of categories
- **Novelty** - New products you haven't seen

## 📊 Recommendation Quality

### Scoring System:
- Each recommendation has a **confidence score** (0-1)
- Higher score = Better match for you
- Scores update as you interact more

### Reasons for Recommendations:
- "Based on your purchases"
- "Similar to items you viewed"
- "Popular in your category"
- "Frequently bought together"
- "Trending now"

## 🎨 UI Features

### "Recommended For You" Section
- **Location**: Top of Home page
- **Count**: 12 personalized products
- **Layout**: Responsive grid (2-6 columns)
- **Refresh**: Auto (30s) + Manual button

### Visual Indicators:
- Section title: "Recommended For You"
- Update button: "🔄 Update"
- Hover tooltip: "Refresh recommendations based on your recent activity"

## 🔧 Technical Details

### API Endpoint
```
GET /recommend/me?k=12
```

**Parameters:**
- `k`: Number of recommendations (default: 12)
- `use_model`: Use ML model (default: true)
- `record_impression`: Track impressions (default: false)

**Response:**
```json
{
  "user_id": 5,
  "recommendations": [
    {
      "article_id": "0108775015",
      "score": 0.85,
      "product_name": "Strap top",
      "price": 29.99,
      "image_path": "/images/010/0108775015.jpg",
      "reason": "based_on_purchases"
    }
  ],
  "count": 12,
  "model_used": true,
  "generation_time_ms": 150.5
}
```

### Database Tracking

**UserInteraction Table:**
```sql
CREATE TABLE user_interactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    article_id VARCHAR(50),
    event_type VARCHAR(50),  -- 'view', 'purchase', 'add_to_cart', 'wishlist'
    value FLOAT,             -- Optional value (e.g., purchase amount)
    created_at DATETIME
);
```

### Interaction Types:
- `view` - Product page viewed
- `purchase` - Product purchased (Buy Now or Checkout)
- `add_to_cart` - Added to cart
- `wishlist` - Added to wishlist
- `impression` - Recommendation shown (optional)

## 🚀 Performance

- **Generation Time**: ~150-300ms
- **Refresh Interval**: 30 seconds
- **Cache**: Candidate generation cached
- **Scalability**: Handles 1000s of users

## 💡 Tips for Better Recommendations

1. **Interact More**: The more you browse/buy, the better recommendations get
2. **Use Wishlist**: Wishlist items strongly influence recommendations
3. **Complete Purchases**: Purchases have highest weight
4. **Explore Categories**: Browse different categories for diverse recommendations
5. **Wait for Updates**: Give the system 30 seconds to learn from new interactions

## 🔮 Future Enhancements

Planned improvements:

- [ ] Real-time recommendations (WebSocket)
- [ ] "Why this recommendation?" explanations
- [ ] Recommendation feedback (like/dislike)
- [ ] A/B testing different algorithms
- [ ] Seasonal/trending boosts
- [ ] Cross-sell recommendations
- [ ] "Complete the look" bundles
- [ ] Price-based personalization

## 📈 Monitoring

Track recommendation quality:

```bash
# Check recommendation health
curl http://localhost:8000/recommend/health

# Response:
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "Project149/models/lgbm_v1.pkl",
  "fallback_mode": "ml_powered"
}
```

## 🎯 Summary

Your recommendations are now:
- ✅ **Personalized** - Based on YOUR behavior
- ✅ **Dynamic** - Update every 30 seconds
- ✅ **Intelligent** - ML-powered predictions
- ✅ **Interactive** - Manual refresh available
- ✅ **Tracked** - All interactions recorded
- ✅ **Adaptive** - Learn from every action

**Start interacting and watch your recommendations evolve!** 🚀

---

**Updated**: Session 3
**Feature**: Auto-refreshing personalized recommendations
**Status**: ACTIVE ✅
