# Quick Start: Product Filters

## 🚀 Get Started in 3 Steps

### Step 1: Restart Backend
```bash
# Stop current backend (Ctrl+C in terminal)
python main.py
```

### Step 2: Start Frontend (if not running)
```bash
cd frontend
npm run dev
```

### Step 3: Test Filters
Open: http://localhost:5173

## ✨ What You Can Do

### Filter by Price
- Type min/max price in input fields
- Or click quick filters: "Under $25", "$25-$50", etc.

### Filter by Department
- Select from dropdown (15 departments available)
- Examples: Shoes, Bags, Accessories, Denim

### Sort Products
- Price: Low to High
- Price: High to Low
- Popular Items

### Share Filtered Views
- Filters appear in URL
- Copy and share: `?min_price=25&max_price=50&department=1339`

## 🧪 Verify It Works

Run automated tests:
```bash
python test_filters.py
```

Expected: ✅ All 10 tests pass

## 📊 Example Filters

Try these in the browser:

**Budget Shopping:**
```
http://localhost:5173/?max_price=25&sort=price_asc
```

**Premium Shoes:**
```
http://localhost:5173/?department=1339&min_price=100&sort=price_desc
```

**Mid-Range Bags:**
```
http://localhost:5173/?department=1494&min_price=30&max_price=80
```

## 🎯 Features

- ✅ Real-time filtering (300ms debounce)
- ✅ URL synchronization (shareable links)
- ✅ Pagination (works with filters)
- ✅ Active filter indicator
- ✅ Reset all button
- ✅ Responsive design

## 📚 Documentation

- **Technical Details**: `FILTER_FEATURE_COMPLETE.md`
- **User Guide**: `FILTER_USAGE_GUIDE.md`
- **Progress Tracker**: `PROGRESS_TRACKER.md`

## ❓ Troubleshooting

**Filters not working?**
→ Restart backend: `python main.py`

**No products found?**
→ Click "Reset All" to clear filters

**Tests failing?**
→ Ensure backend is running on port 8000

---

**Ready to filter!** 🎉
