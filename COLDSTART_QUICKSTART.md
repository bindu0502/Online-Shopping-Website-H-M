# Cold-Start Recommendations - Quick Start

## 🚀 What Is This?

New users with no activity (empty cart/wishlist/orders) now get personalized recommendations based on their category preferences selected during signup.

## ⚡ Quick Test

```bash
# 1. Verify implementation
python verify_coldstart.py

# 2. Restart backend (REQUIRED!)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Test in browser
# Login: coldstart@example.com / password123
# Go to: "For You" page
# Expect: 20 products from preferred categories
```

## 🔧 How It Works

```
New user signs up
    ↓
Selects categories (e.g., "Shoes, Accessories")
    ↓
Logs in (no activity yet)
    ↓
Visits "For You" page
    ↓
Sees 20 products from selected categories
```

## ✅ What Changed

**Backend**: `src/personalized_recommend.py`
- Added `get_category_based_recommendations()`
- Updated `generate_personalized_recommendations()` with cold-start check

**Frontend**: No changes needed!

## 🧪 Test User

- Email: `coldstart@example.com`
- Password: `password123`
- Categories: "Shoes,Accessories,Garment Upper body"

## ⚠️ Important

**MUST restart backend server** after code changes!

```bash
# Stop server (Ctrl+C)
# Start again
uvicorn main:app --reload
```

## 📊 Expected Results

| Scenario | Result |
|----------|--------|
| New user, no activity | 20 category-based products |
| User with activity | Behavior-based recommendations |
| No categories set | Empty array (graceful) |

## 🐛 Troubleshooting

**No recommendations showing?**

1. Restart backend server ⚠️
2. Check user has `preferred_categories` set
3. Run `python verify_coldstart.py`
4. Check backend logs for "[COLD-START v2]"

## 📚 Full Documentation

- `COLD_START_COMPLETE.md` - Complete documentation
- `COLD_START_IMPLEMENTATION.md` - Technical details
- `test_complete_coldstart_flow.py` - Full test suite

---

**Status**: ✅ Ready for production (after server restart)
